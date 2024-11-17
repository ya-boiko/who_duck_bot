"""Unit of work."""

import abc

from sqlalchemy import orm


class AbstractUnitOfWork(abc.ABC):
    """Abstract UoW."""

    _repos: list

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.rollback()

    def collect_new_events(self):
        """Returns events from newly seen entities."""
        for entity in self._seen():
            while entity.events:
                yield entity.events.pop(0)

    @abc.abstractmethod
    def commit(self):
        """Commit transaction."""

    @abc.abstractmethod
    def rollback(self):
        """Rollback transaction."""

    def _seen(self):
        if not hasattr(self, '_repos'):
            return

        for repo in self._repos:
            for entity in repo.seen:
                yield entity


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """UoW implementation for SqlAlchemy."""

    session: orm.Session

    def __init__(self, session_factory) -> None:
        self._session_factory = session_factory

    def __enter__(self):
        self.session = self._session_factory()
        self._repos = self._init_repositories(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def _init_repositories(self, session) -> list[object]:  # pylint: disable=unused-argument
        """Override this method to initialize repositories on entering the context.

        Return the repositories that need to be analyzed for `seen` entities after the event
        is handled.
        """
        return []


class UnitOfWork(AbstractUnitOfWork):
    """UoW."""

    ...
