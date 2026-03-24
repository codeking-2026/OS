"""
In-memory virtual filesystem.

The filesystem module exposes a small API similar to what a kernel might offer
to shell commands and user programs. It intentionally favors clarity over raw
performance so the logic is easy to follow.

Example usage:
    from pyos.core.filesystem import VirtualFileSystem

    fs = VirtualFileSystem()
    fs.mkdir("/docs")
    fs.write_file("/docs/readme.txt", "Welcome to pyOS")
    print(fs.read_file("/docs/readme.txt"))
    print(fs.listdir("/"))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List, Tuple

from .fs_nodes import BaseNode, DirectoryNode, FileNode


class FileSystemError(RuntimeError):
    """Base class for filesystem-related problems."""


class NodeNotFoundError(FileSystemError):
    pass


class NodeExistsError(FileSystemError):
    pass


class NotADirectoryErrorFS(FileSystemError):
    pass


class IsADirectoryErrorFS(FileSystemError):
    pass


class DirectoryNotEmptyErrorFS(FileSystemError):
    pass


def _normalize_parts(path: str) -> List[str]:
    if not path:
        return []
    normalized = path.replace("\\", "/").strip()
    if len(normalized) >= 2 and normalized[1] == ":" and normalized[0].isalpha():
        drive = normalized[0].upper()
        tail = normalized[2:]
        normalized = f"/{drive}/{tail.lstrip('/')}"
    return [part for part in normalized.split("/") if part and part != "."]


@dataclass
class WalkEntry:
    node: BaseNode
    depth: int


class VirtualFileSystem:
    """Educational in-memory filesystem for a single user."""

    def __init__(self) -> None:
        self.root = DirectoryNode(name="", parent=None)
        self.cwd = self.root
        self._seed_initial_files()

    def _seed_initial_files(self) -> None:
        self.mkdir("/C")
        self.mkdir("C:/WINDOWS")
        self.mkdir("C:/WINDOWS/DESKTOP")
        self.mkdir("C:/PROGRAM FILES")
        self.mkdir("C:/TEMP")
        self.mkdir("C:/USER")
        self.mkdir("C:/USER/DESKTOP")
        self.mkdir("C:/USER/DOCUMENTS")
        self.mkdir("C:/USER/GAMES")
        self.write_file(
            "C:/USER/README.txt",
            "Welcome to pyOS 95.\nType 'help' to see available shell commands.\n",
        )
        self.write_file(
            "C:/USER/TODO.txt",
            "1. Explore My Computer\n2. Launch a demo program\n3. Inspect memory\n",
        )
        self.write_file(
            "C:/USER/DESKTOP/NOTEPAD.txt",
            "This desktop is powered by pure Python.\n",
        )
        self.write_file(
            "C:/WINDOWS/DESKTOP.INI",
            "[Shell]\nIconFile=pyos95.dll\n",
        )

    def _starting_directory(self, path: str) -> DirectoryNode:
        normalized = path.replace("\\", "/").strip()
        if normalized.startswith("/") or (len(normalized) >= 2 and normalized[1] == ":" and normalized[0].isalpha()):
            return self.root
        return self.cwd

    def _resolve(
        self,
        path: str,
        *,
        create_missing_dirs: bool = False,
        stop_before_leaf: bool = False,
    ) -> BaseNode:
        if path == "/":
            return self.root
        parts = _normalize_parts(path)
        if stop_before_leaf and parts:
            parts = parts[:-1]
        current: BaseNode = self._starting_directory(path)
        for part in parts:
            if part == "..":
                if current.parent is not None:
                    current = current.parent
                continue
            if not isinstance(current, DirectoryNode):
                raise NotADirectoryErrorFS(f"{current.path} is not a directory")
            if current.has_child(part):
                current = current.get_child(part)
                continue
            if create_missing_dirs:
                new_dir = DirectoryNode(name=part, parent=current)
                current.add_child(new_dir)
                current = new_dir
                continue
            raise NodeNotFoundError(path)
        return current

    def _split_parent(self, path: str) -> Tuple[DirectoryNode, str]:
        parts = _normalize_parts(path)
        name = parts[-1] if parts else ""
        if not name:
            raise FileSystemError("Path has no leaf name")
        parent = self._resolve(path, stop_before_leaf=True)
        if not isinstance(parent, DirectoryNode):
            raise NotADirectoryErrorFS(f"{parent.path} is not a directory")
        return parent, name

    def exists(self, path: str) -> bool:
        try:
            self._resolve(path)
            return True
        except FileSystemError:
            return False

    def chdir(self, path: str) -> str:
        node = self._resolve(path)
        if not isinstance(node, DirectoryNode):
            raise NotADirectoryErrorFS(path)
        self.cwd = node
        return node.path

    def pwd(self) -> str:
        return self.cwd.path

    def mkdir(self, path: str, *, parents: bool = False) -> str:
        if parents:
            node = self._resolve(path, create_missing_dirs=True)
            if not isinstance(node, DirectoryNode):
                raise NotADirectoryErrorFS(path)
            return node.path
        parent, name = self._split_parent(path)
        if parent.has_child(name):
            raise NodeExistsError(path)
        directory = DirectoryNode(name=name, parent=parent)
        parent.add_child(directory)
        return directory.path

    def listdir(self, path: str = ".") -> List[str]:
        node = self._resolve(path)
        if not isinstance(node, DirectoryNode):
            raise NotADirectoryErrorFS(path)
        return [child.name for child in node.list_children()]

    def scandir(self, path: str = ".") -> List[BaseNode]:
        node = self._resolve(path)
        if not isinstance(node, DirectoryNode):
            raise NotADirectoryErrorFS(path)
        return list(node.list_children())

    def create_file(self, path: str, content: str = "") -> str:
        parent, name = self._split_parent(path)
        if parent.has_child(name):
            raise NodeExistsError(path)
        file_node = FileNode(name=name, parent=parent, content=content)
        parent.add_child(file_node)
        return file_node.path

    def write_file(self, path: str, content: str) -> str:
        if self.exists(path):
            node = self._resolve(path)
            if isinstance(node, DirectoryNode):
                raise IsADirectoryErrorFS(path)
            node.write(content)
            return node.path
        return self.create_file(path, content)

    def append_file(self, path: str, text: str) -> str:
        if self.exists(path):
            node = self._resolve(path)
            if isinstance(node, DirectoryNode):
                raise IsADirectoryErrorFS(path)
            node.append(text)
            return node.path
        return self.create_file(path, text)

    def read_file(self, path: str) -> str:
        node = self._resolve(path)
        if isinstance(node, DirectoryNode):
            raise IsADirectoryErrorFS(path)
        return node.read()

    def remove(self, path: str, *, recursive: bool = False) -> str:
        node = self._resolve(path)
        if node is self.root:
            raise FileSystemError("Cannot remove the root directory")
        parent = node.parent
        if parent is None:
            raise FileSystemError("Node has no parent")
        if isinstance(node, DirectoryNode) and node.children and not recursive:
            raise DirectoryNotEmptyErrorFS(path)
        parent.remove_child(node.name)
        return path

    def rename(self, src: str, dest: str) -> str:
        node = self._resolve(src)
        if node is self.root:
            raise FileSystemError("Cannot rename the root directory")
        old_parent = node.parent
        if old_parent is None:
            raise FileSystemError("Node has no parent")
        new_parent, new_name = self._split_parent(dest)
        if new_parent.has_child(new_name):
            raise NodeExistsError(dest)
        old_parent.remove_child(node.name)
        node.name = new_name
        new_parent.add_child(node)
        return node.path

    def walk(self, path: str = ".") -> Iterator[WalkEntry]:
        start = self._resolve(path)
        stack = [(start, 0)]
        while stack:
            node, depth = stack.pop()
            yield WalkEntry(node=node, depth=depth)
            if isinstance(node, DirectoryNode):
                children = list(node.list_children())
                for child in reversed(children):
                    stack.append((child, depth + 1))

    def tree(self, path: str = ".") -> str:
        lines = []
        for entry in self.walk(path):
            name = "/" if entry.node is self.root else entry.node.name
            prefix = "  " * entry.depth
            marker = "[D]" if entry.node.is_dir() else "[F]"
            lines.append(f"{prefix}{marker} {name}")
        return "\n".join(lines)

    def disk_usage(self, path: str = ".") -> int:
        total = 0
        for entry in self.walk(path):
            if isinstance(entry.node, FileNode):
                total += entry.node.size
        return total

    def stat(self, path: str) -> dict:
        node = self._resolve(path)
        return {
            "path": node.path,
            "type": "directory" if node.is_dir() else "file",
            "size": 0 if node.is_dir() else node.size,
            "created_at": node.created_at.isoformat(timespec="seconds"),
            "modified_at": node.modified_at.isoformat(timespec="seconds"),
        }
