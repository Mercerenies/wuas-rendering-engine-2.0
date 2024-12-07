
"""Message logger API."""

from __future__ import annotations

from typing import Sequence


class MessageLogger:
    _messages: list[str]

    def log(self, message: str) -> None:
        """Log a message."""
        self._messages.append(message)

    def messages(self) -> Sequence[str]:
        """Get all logged messages. This reference is ONLY valid up
        until the next call to log().

        """
        return self._messages
