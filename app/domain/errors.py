"""Errors"""


class NotFound(Exception):
    """Record not found."""

    message: str

    def __init__(self, message: str = None):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message
