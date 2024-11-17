"""Events and commands mapping to handlers."""

from app.domain import events, commands
from app.service_layer.handlers import command_handlers


EVENT_HANDLERS = {}

COMMAND_HANDLERS = {}
