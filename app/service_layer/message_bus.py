"""Message bus."""

from abc import ABC, abstractmethod
import logging
from dataclasses import dataclass, field
from typing import Callable, List, Any

from pika import exceptions as pika_exc
from sqlalchemy import exc as sa_exc
from sqlalchemy.orm import exc as sa_orm_exc
from tenacity import RetryCallState, Retrying, wait, stop
from tenacity.before_sleep import before_sleep_log
from tenacity.retry import retry_any, retry_base, retry_if_exception, retry_if_exception_type

from app.domain import events, commands, Message

from .unit_of_work import AbstractUnitOfWork


logger = logging.getLogger(__name__)


@dataclass
class HandlerResult:
    """Results of message handling."""

    results: List[Any] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)

    def add(self, other_result: 'HandlerResult') -> None:
        """Appends results and messages from the other result to this object."""
        self.results.extend(other_result.results)
        self.messages.extend(other_result.messages)


class AbstractMessageBus(ABC):
    """Abstract MessageBus interface."""

    @abstractmethod
    def handle(self, message: Message) -> List[Any]:
        """Handles a single message."""


class retry_minimum_attempts(retry_base):
    """Retry strategy that retries at least a given number of times."""

    def __init__(self, attempts: int) -> None:
        self.attempts = attempts

    def __call__(self, retry_state: 'RetryCallState') -> bool:
        if not retry_state.outcome or not retry_state.outcome.failed:
            return False

        return retry_state.attempt_number <= self.attempts


@dataclass
class MessageBus(AbstractMessageBus):
    """Message bus"""

    uow: AbstractUnitOfWork

    event_handlers: dict[type[Any], list[Callable]] = field(default_factory=dict)
    command_handlers: dict[type[Any], Callable] = field(default_factory=dict)

    event_retry_stop: stop.stop_base = stop.stop_never
    event_retry_wait: wait.wait_base = wait.wait_exponential(multiplier=1, min=1, max=60)
    command_retry_stop: stop.stop_base = stop.stop_never
    command_retry_wait: wait.wait_base = wait.wait_none()

    def __post_init__(self):
        self.event_handling_retrier = Retrying(
            stop=self.event_retry_stop,
            wait=self.event_retry_wait,
            before_sleep=before_sleep_log(logger, logging.ERROR),
            reraise=True,
            retry=retry_any(
                # There are exceptions (like disconnections) that are recoverable
                # and should be retried until completion. But we still want to retry
                # at least several times in case of other failures just to be sure.
                retry_if_exception(self._is_recoverable_error),
                retry_minimum_attempts(5),
            ),
        )

        self.command_handling_retrier = Retrying(
            stop=self.command_retry_stop,
            wait=self.command_retry_wait,
            reraise=True,
            retry=retry_if_exception_type(sa_orm_exc.StaleDataError),
        )

    def _is_recoverable_error(self, ex: BaseException) -> bool:
        if isinstance(ex, sa_orm_exc.StaleDataError):
            # Optimistic version error - someone changed data before us
            return True

        if isinstance(ex, sa_exc.DBAPIError):
            # Disconnected from database
            return ex.connection_invalidated

        if isinstance(ex, pika_exc.StreamLostError):
            # Disconnected from RabbitMQ
            return True

        return False

    def handle(self, message: Message) -> List[Any]:
        """Handles a single message."""

        results = []

        handler_result = self._handle_message(message)

        # record the results of this handler first
        results.extend(handler_result.results)

        # ... then the results of derived message handlers
        for derived_message in handler_result.messages:
            results.extend(self.handle(derived_message))

        return results

    def _handle_message(self, message: Message) -> HandlerResult:
        if isinstance(message, events.Event):
            return self._handle_event(message)
        elif isinstance(message, commands.Command):
            return self._handle_command(message)
        else:
            raise Exception(f'{message} was not an Event or Command')

    def _handle_event(self, event: events.Event) -> HandlerResult:
        composite_result = HandlerResult()

        for handler in self.event_handlers[type(event)]:
            handler_result = self._handle_event_with_handler(event, handler)
            composite_result.add(handler_result)

        return composite_result

    def _handle_event_with_handler(self, event: events.Event, handler: Callable) -> HandlerResult:
        logger.info('Handling event %s with %s', repr(event), handler.__name__)

        # By default, the retrier is infinite, so we might need to add
        # error types that break this infinite loop (unprocessable events, for ex).
        self.event_handling_retrier(handler, event, self.uow)

        return HandlerResult(messages=list(self.uow.collect_new_events()))

    def _handle_command(self, command: commands.Command) -> HandlerResult:
        handler = self.command_handlers[type(command)]

        logger.info('Handling command %s with %s', repr(command), handler.__name__)

        # Has no retrier wrapping as generally commands are issued by API endpoints.
        # These commands tend to raise various application-level errors that need to
        # propagate upstream.
        result = self.command_handling_retrier(handler, command, self.uow)

        return HandlerResult([result], list(self.uow.collect_new_events()))

    def _handle_unknown(self, message):
        message_cls_name = message.__class__.__name__
        raise Exception(f'{message} was not an Event or Command')

    def _trace_span_info(self, message: Message) -> dict:
        message_cls_name = message.__class__.__name__

        if isinstance(message, events.Event):
            return {'name': f'EVENT {message_cls_name}', 'attributes': {'event': repr(message)}}
        elif isinstance(message, commands.Command):
            return {'name': f'COMMAND {message_cls_name}', 'attributes': {'command': repr(message)}}
        else:
            return {'name': f'UNKNOWN {message_cls_name}', 'attributes': {'message': repr(message)}}
