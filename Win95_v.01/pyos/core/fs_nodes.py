"""
Filesystem node definitions.

This module contains small, focused classes that represent directories and
files inside the in-memory virtual filesystem. The structures are kept
simple on purpose so learners can trace how a path turns into an object.

Example usage:
    from pyos.core.fs_nodes import DirectoryNode, FileNode

    root = DirectoryNode(name="", parent=None)
    notes = FileNode(name="notes.txt", parent=root, content="Hello")
    root.add_child(notes)
    print(root.get_child("notes.txt").read())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, Optional


def _timestamp() -> datetime:
    return datetime.now()


@dataclass
class BaseNode:
    """Common information shared by all filesystem nodes."""

    name: str
    parent: Optional["DirectoryNode"]
    created_at: datetime = field(default_factory=_timestamp)
    modified_at: datetime = field(default_factory=_timestamp)

    def is_dir(self) -> bool:
        return False

    def is_file(self) -> bool:
        return False

    @property
    def path(self) -> str:
        if self.parent is None:
            return "/"
        parts = []
        current: Optional[BaseNode] = self
        while current is not None and current.parent is not None:
            parts.append(current.name)
            current = current.parent
        ordered = list(reversed(parts))
        if ordered and len(ordered[0]) == 1 and ordered[0].isalpha():
            drive = ordered[0].upper()
            tail = "/".join(ordered[1:])
            return f"{drive}:/{tail}" if tail else f"{drive}:/"
        return "/" + "/".join(ordered)

    def touch(self) -> None:
        self.modified_at = _timestamp()

    def describe(self) -> str:
        kind = "dir" if self.is_dir() else "file"
        return f"{kind:<4} {self.path}"


@dataclass
class FileNode(BaseNode):
    """A text file living in the in-memory filesystem."""

    content: str = ""

    def is_file(self) -> bool:
        return True

    @property
    def size(self) -> int:
        return len(self.content.encode("utf-8"))

    def read(self) -> str:
        return self.content

    def write(self, content: str) -> None:
        self.content = content
        self.touch()

    def append(self, text: str) -> None:
        self.content += text
        self.touch()

    def describe(self) -> str:
        return f"file {self.path} ({self.size} bytes)"


@dataclass
class DirectoryNode(BaseNode):
    """A directory containing named child nodes."""

    children: Dict[str, BaseNode] = field(default_factory=dict)

    def is_dir(self) -> bool:
        return True

    def add_child(self, node: BaseNode) -> None:
        if node.name in self.children:
            raise ValueError(f"'{node.name}' already exists in {self.path}")
        self.children[node.name] = node
        node.parent = self
        self.touch()

    def remove_child(self, name: str) -> BaseNode:
        if name not in self.children:
            raise KeyError(name)
        removed = self.children.pop(name)
        self.touch()
        return removed

    def get_child(self, name: str) -> BaseNode:
        if name not in self.children:
            raise KeyError(name)
        return self.children[name]

    def has_child(self, name: str) -> bool:
        return name in self.children

    def list_children(self) -> Iterable[BaseNode]:
        for name in sorted(self.children):
            yield self.children[name]

    def describe(self) -> str:
        count = len(self.children)
        suffix = "item" if count == 1 else "items"
        return f"dir  {self.path} ({count} {suffix})"
