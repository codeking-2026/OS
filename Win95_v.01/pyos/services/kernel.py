"""
Kernel facade tying the simulator together.

The kernel coordinates the virtual filesystem, process manager, memory manager,
and I/O devices. Shell commands call into this layer instead of manipulating
subsystems directly, which mirrors how real operating systems centralize policy
in the kernel.

Example usage:
    from pyos.services.kernel import Kernel

    kernel = Kernel()
    print(kernel.boot_report())
    kernel.launch_program("clock")
    kernel.tick()
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Dict, List, Optional

from pyos.apps.demo_programs import build_demo_programs
from pyos.core.filesystem import (
    DirectoryNotEmptyErrorFS,
    FileSystemError,
    IsADirectoryErrorFS,
    NodeExistsError,
    NodeNotFoundError,
    NotADirectoryErrorFS,
    VirtualFileSystem,
)
from pyos.core.memory import MemoryManager
from pyos.core.process import ProcessControlBlock, ProcessManager
from pyos.services.device_io import KeyboardDevice, ScreenDevice


@dataclass
class CommandResult:
    ok: bool
    message: str = ""


class Kernel:
    """Single-user operating system simulator."""

    def __init__(self) -> None:
        self.fs = VirtualFileSystem()
        self.memory = MemoryManager(total_kb=1024)
        self.processes = ProcessManager()
        self.keyboard = KeyboardDevice()
        self.screen = ScreenDevice()
        self.programs = build_demo_programs()
        self._pid_memory_map: Dict[int, List[int]] = {}
        self.processes.add_listener(self._handle_process_event)
        self._boot_sequence()

    def _boot_sequence(self) -> None:
        self.screen.write_line("Pyos_v0.1 booting...")
        self.screen.write_line("Drive C mounted")
        self.screen.write_line("Single-user mode enabled")
        self.screen.write_line("Ready")
        self.fs.chdir("C:/USER")

    def boot_report(self) -> str:
        return (
            "Pyos_v0.1 educational simulator\n"
            "Subsystems: filesystem, processes, memory, keyboard, screen\n"
            f"Working directory: {self.fs.pwd()}"
        )

    def _handle_process_event(self, pcb: ProcessControlBlock, event: str) -> None:
        if event == "created":
            try:
                block = self.memory.allocate(f"pid:{pcb.pid}:{pcb.name}", pcb.memory_kb)
                self._pid_memory_map.setdefault(pcb.pid, []).append(block.block_id)
                self.screen.write_line(
                    f"Process {pcb.pid} ({pcb.name}) created and allocated {block.size_kb} KB"
                )
            except MemoryError as exc:
                pcb.add_log(str(exc))
                self.processes.kill(pcb.pid, exit_code=-1)
                self.screen.write_line(f"Process {pcb.pid} failed to start: {exc}")
        elif event == "scheduled":
            self.screen.write_line(f"Running PID {pcb.pid}: {pcb.name}")
        elif event == "blocked":
            self.screen.write_line(f"PID {pcb.pid} is waiting for I/O")
        elif event in {"terminated", "killed"}:
            for block_id in self._pid_memory_map.pop(pcb.pid, []):
                try:
                    self.memory.free(block_id)
                except KeyError:
                    pass
            self.screen.write_line(f"Process {pcb.pid} ended with code {pcb.exit_code}")

    def _wrap_fs_errors(self, func, *args, **kwargs) -> CommandResult:
        try:
            message = func(*args, **kwargs)
            if message is None:
                message = ""
            return CommandResult(True, str(message))
        except NodeNotFoundError:
            return CommandResult(False, "Path not found")
        except NodeExistsError:
            return CommandResult(False, "Path already exists")
        except NotADirectoryErrorFS:
            return CommandResult(False, "Not a directory")
        except IsADirectoryErrorFS:
            return CommandResult(False, "Is a directory")
        except DirectoryNotEmptyErrorFS:
            return CommandResult(False, "Directory not empty; use recursive delete")
        except FileSystemError as exc:
            return CommandResult(False, str(exc))

    def pwd(self) -> str:
        return self.fs.pwd()

    def ls(self, path: str = ".") -> CommandResult:
        def action(target: str) -> str:
            rows = []
            for node in self.fs.scandir(target):
                marker = "<DIR>" if node.is_dir() else f"{getattr(node, 'size', 0):>5}"
                rows.append(f"{marker:>8}  {node.name}")
            return "\n".join(rows) if rows else "<empty directory>"

        return self._wrap_fs_errors(action, path)

    def tree(self, path: str = ".") -> CommandResult:
        return self._wrap_fs_errors(self.fs.tree, path)

    def cat(self, path: str) -> CommandResult:
        return self._wrap_fs_errors(self.fs.read_file, path)

    def mkdir(self, path: str) -> CommandResult:
        return self._wrap_fs_errors(self.fs.mkdir, path)

    def touch(self, path: str) -> CommandResult:
        return self._wrap_fs_errors(self.fs.create_file, path, "")

    def write(self, path: str, text: str) -> CommandResult:
        return self._wrap_fs_errors(self.fs.write_file, path, text)

    def append(self, path: str, text: str) -> CommandResult:
        return self._wrap_fs_errors(self.fs.append_file, path, text)

    def rm(self, path: str, *, recursive: bool = False) -> CommandResult:
        return self._wrap_fs_errors(self.fs.remove, path, recursive=recursive)

    def cd(self, path: str) -> CommandResult:
        return self._wrap_fs_errors(self.fs.chdir, path)

    def mv(self, src: str, dest: str) -> CommandResult:
        return self._wrap_fs_errors(self.fs.rename, src, dest)

    def stat(self, path: str) -> CommandResult:
        result = self._wrap_fs_errors(self.fs.stat, path)
        if not result.ok:
            return result
        metadata = ast.literal_eval(result.message)
        lines = [f"{key}: {value}" for key, value in metadata.items()]
        return CommandResult(True, "\n".join(lines))

    def du(self, path: str = ".") -> CommandResult:
        return self._wrap_fs_errors(lambda target: f"{self.fs.disk_usage(target)} bytes", path)

    def launch_program(self, name: str) -> CommandResult:
        factory = self.programs.get(name)
        if factory is None:
            return CommandResult(False, f"Unknown program: {name}")
        spec = factory()
        pid = self.processes.create_process(
            spec["name"],
            instructions=spec.get("instructions", 5),
            memory_kb=spec.get("memory_kb", 32),
        )
        message = [f"Launched {spec['name']} as PID {pid}"]
        if "output" in spec:
            message.append(spec["output"])
        if spec.get("io_wait"):
            self.processes.block(pid, spec["io_wait"])
            message.append(f"PID {pid} entered waiting state for I/O")
        return CommandResult(True, "\n".join(message))

    def list_programs(self) -> CommandResult:
        lines = ["Built-in programs:"]
        lines.extend(f"- {name}" for name in sorted(self.programs))
        return CommandResult(True, "\n".join(lines))

    def tick(self, count: int = 1) -> CommandResult:
        events = []
        for _ in range(max(1, count)):
            pcb = self.processes.tick()
            if pcb is None:
                events.append("Scheduler idle")
            else:
                events.append(
                    f"Tick ran PID {pcb.pid} ({pcb.name}); state is now {pcb.state.value}"
                )
        return CommandResult(True, "\n".join(events))

    def ps(self) -> CommandResult:
        return CommandResult(True, self.processes.ps())

    def kill(self, pid: int) -> CommandResult:
        try:
            pcb = self.processes.kill(pid)
        except KeyError:
            return CommandResult(False, f"No such PID: {pid}")
        return CommandResult(True, f"Killed PID {pcb.pid}")

    def procinfo(self, pid: int) -> CommandResult:
        try:
            return CommandResult(True, self.processes.describe(pid))
        except KeyError:
            return CommandResult(False, f"No such PID: {pid}")

    def mem(self) -> CommandResult:
        return CommandResult(True, self.memory.report())

    def memmap(self) -> CommandResult:
        return CommandResult(True, self.memory.fragmentation_report())

    def memhistory(self) -> CommandResult:
        return CommandResult(True, self.memory.history())

    def keyboard_feed(self, text: str) -> CommandResult:
        self.keyboard.feed(text)
        return CommandResult(True, f"Queued keyboard input: {text}")

    def keyboard_read(self) -> CommandResult:
        text = self.keyboard.read_line()
        if text is None:
            return CommandResult(False, "Keyboard buffer is empty")
        return CommandResult(True, text)

    def screen_dump(self, limit: Optional[int] = None) -> CommandResult:
        return CommandResult(True, self.screen.dump(limit))

    def screen_clear(self) -> CommandResult:
        self.screen.clear()
        return CommandResult(True, "Screen cleared")

    def help_text(self) -> str:
        return (
            "Filesystem commands:\n"
            "  ls [path]        List directory contents\n"
            "  tree [path]      Print a directory tree\n"
            "  pwd              Show current directory\n"
            "  cd <path>        Change directory\n"
            "  mkdir <path>     Create a directory\n"
            "  touch <path>     Create an empty file\n"
            "  cat <path>       Display file contents\n"
            "  write <path> <text>   Replace file contents\n"
            "  append <path> <text>  Append to a file\n"
            "  mv <src> <dest>  Rename or move a file\n"
            "  rm [-r] <path>   Remove a file or directory\n"
            "  stat <path>      Show metadata\n"
            "  du [path]        Show disk usage in bytes\n"
            "\n"
            "Process commands:\n"
            "  programs         List built-in programs\n"
            "  run <name>       Launch a demo program\n"
            "  tick [n]         Advance the scheduler\n"
            "  ps               Show process table\n"
            "  kill <pid>       Terminate a process\n"
            "  proc <pid>       Show detailed process info\n"
            "\n"
            "Memory and device commands:\n"
            "  mem              Show memory allocations\n"
            "  memmap           Show free gaps\n"
            "  memhist          Show recent memory events\n"
            "  keyfeed <text>   Queue keyboard input\n"
            "  keyread          Read one keyboard event\n"
            "  screen [n]       Show recent screen lines\n"
            "  clear            Clear the screen buffer\n"
            "\n"
            "Other:\n"
            "  help             Show this help message\n"
            "  exit             Leave the shell"
        )
