"""
Keyboard and screen I/O simulation.

The simulator uses this module to model simple devices. A keyboard holds input
events, and a screen stores rendered lines. This separation mirrors how a real
OS talks to hardware through device abstractions.

Example usage:
    from pyos.services.device_io import KeyboardDevice, ScreenDevice

    keyboard = KeyboardDevice()
    screen = ScreenDevice()
    keyboard.feed("hello")
    screen.write_line("Boot complete")
    print(keyboard.read_line())
    print(screen.dump())
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, List, Optional


def _stamp() -> str:
    return datetime.now().strftime("%H:%M:%S")


@dataclass
class KeyboardEvent:
    """Single keyboard input event."""

    text: str
    created_at: str = field(default_factory=_stamp)

    def summary(self) -> str:
        return f"[{self.created_at}] {self.text}"


class KeyboardDevice:
    """Simple FIFO keyboard buffer."""

    def __init__(self) -> None:
        self._queue: Deque[KeyboardEvent] = deque()
        self._history: List[str] = []

    def feed(self, text: str) -> None:
        event = KeyboardEvent(text=text)
        self._queue.append(event)
        self._history.append(f"queued: {event.summary()}")

    def read_line(self) -> Optional[str]:
        if not self._queue:
            self._history.append("read attempted on empty queue")
            return None
        event = self._queue.popleft()
        self._history.append(f"read: {event.summary()}")
        return event.text

    def pending(self) -> int:
        return len(self._queue)

    def history(self, limit: int = 10) -> str:
        return "\n".join(self._history[-limit:] or ["<no keyboard activity>"])


class ScreenDevice:
    """Text-mode screen buffer."""

    def __init__(self, *, max_lines: int = 200) -> None:
        self.max_lines = max_lines
        self._lines: List[str] = []

    def write(self, text: str) -> None:
        for line in text.splitlines() or [""]:
            self.write_line(line)

    def write_line(self, text: str) -> None:
        stamped = f"[{_stamp()}] {text}"
        self._lines.append(stamped)
        overflow = len(self._lines) - self.max_lines
        if overflow > 0:
            del self._lines[:overflow]

    def clear(self) -> None:
        self._lines.clear()

    def snapshot(self, limit: Optional[int] = None) -> List[str]:
        if limit is None:
            return list(self._lines)
        return self._lines[-limit:]

    def dump(self, limit: Optional[int] = None) -> str:
        lines = self.snapshot(limit)
        return "\n".join(lines if lines else ["<screen is empty>"])
