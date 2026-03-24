"""
Command-line shell for the OS simulator.

The shell parses user input and maps each command to kernel operations. The
implementation is intentionally explicit instead of meta-programmed so students
can trace how tokens become function calls.

Example usage:
    from pyos.services.kernel import Kernel
    from pyos.ui.shell import Shell

    shell = Shell(Kernel())
    print(shell.onecmd("pwd"))
    print(shell.onecmd("run clock"))
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from pyos.services.kernel import CommandResult, Kernel


@dataclass
class ParsedCommand:
    """Tokenized shell command."""

    name: str
    args: List[str]


class Shell:
    """Tiny educational shell running against the simulated kernel."""

    def __init__(self, kernel: Optional[Kernel] = None) -> None:
        self.kernel = kernel or Kernel()
        self.running = True
        self._dispatch: Dict[str, Callable[[List[str]], str]] = {
            "append": self._cmd_append,
            "cat": self._cmd_cat,
            "cd": self._cmd_cd,
            "clear": self._cmd_clear,
            "du": self._cmd_du,
            "exit": self._cmd_exit,
            "help": self._cmd_help,
            "keyfeed": self._cmd_keyfeed,
            "keyread": self._cmd_keyread,
            "kill": self._cmd_kill,
            "ls": self._cmd_ls,
            "mem": self._cmd_mem,
            "memhist": self._cmd_memhist,
            "memmap": self._cmd_memmap,
            "mkdir": self._cmd_mkdir,
            "mv": self._cmd_mv,
            "proc": self._cmd_proc,
            "programs": self._cmd_programs,
            "ps": self._cmd_ps,
            "pwd": self._cmd_pwd,
            "rm": self._cmd_rm,
            "run": self._cmd_run,
            "screen": self._cmd_screen,
            "stat": self._cmd_stat,
            "tick": self._cmd_tick,
            "touch": self._cmd_touch,
            "tree": self._cmd_tree,
            "write": self._cmd_write,
        }

    def prompt(self) -> str:
        return f"{self.kernel.pwd()}> "

    def parse(self, line: str) -> Optional[ParsedCommand]:
        line = line.strip()
        if not line:
            return None
        tokens = shlex.split(line)
        return ParsedCommand(name=tokens[0], args=tokens[1:])

    def _format(self, result: CommandResult) -> str:
        return result.message if result.ok else f"error: {result.message}"

    def onecmd(self, line: str) -> str:
        parsed = self.parse(line)
        if parsed is None:
            return ""
        handler = self._dispatch.get(parsed.name)
        if handler is None:
            return f"error: unknown command '{parsed.name}'"
        try:
            output = handler(parsed.args)
        except ValueError as exc:
            return f"error: {exc}"
        if output:
            self.kernel.screen.write(output)
        return output

    def repl(self) -> None:
        print(self.kernel.boot_report())
        while self.running:
            try:
                line = input(self.prompt())
            except EOFError:
                print()
                break
            output = self.onecmd(line)
            if output:
                print(output)

    def _require_args(self, args: List[str], count: int, usage: str) -> None:
        if len(args) < count:
            raise ValueError(f"usage: {usage}")

    def _cmd_help(self, args: List[str]) -> str:
        return self.kernel.help_text()

    def _cmd_exit(self, args: List[str]) -> str:
        self.running = False
        return "Exiting pyOS shell"

    def _cmd_pwd(self, args: List[str]) -> str:
        return self.kernel.pwd()

    def _cmd_ls(self, args: List[str]) -> str:
        return self._format(self.kernel.ls(args[0] if args else "."))

    def _cmd_tree(self, args: List[str]) -> str:
        return self._format(self.kernel.tree(args[0] if args else "."))

    def _cmd_cat(self, args: List[str]) -> str:
        self._require_args(args, 1, "cat <path>")
        return self._format(self.kernel.cat(args[0]))

    def _cmd_cd(self, args: List[str]) -> str:
        self._require_args(args, 1, "cd <path>")
        result = self.kernel.cd(args[0])
        return self._format(result) if not result.ok else ""

    def _cmd_mkdir(self, args: List[str]) -> str:
        self._require_args(args, 1, "mkdir <path>")
        return self._format(self.kernel.mkdir(args[0]))

    def _cmd_touch(self, args: List[str]) -> str:
        self._require_args(args, 1, "touch <path>")
        return self._format(self.kernel.touch(args[0]))

    def _cmd_write(self, args: List[str]) -> str:
        self._require_args(args, 2, "write <path> <text>")
        path = args[0]
        text = " ".join(args[1:])
        return self._format(self.kernel.write(path, text))

    def _cmd_append(self, args: List[str]) -> str:
        self._require_args(args, 2, "append <path> <text>")
        path = args[0]
        text = " ".join(args[1:])
        return self._format(self.kernel.append(path, text))

    def _cmd_rm(self, args: List[str]) -> str:
        self._require_args(args, 1, "rm [-r] <path>")
        recursive = False
        filtered = []
        for arg in args:
            if arg in {"-r", "-R", "--recursive"}:
                recursive = True
            else:
                filtered.append(arg)
        self._require_args(filtered, 1, "rm [-r] <path>")
        return self._format(self.kernel.rm(filtered[0], recursive=recursive))

    def _cmd_mv(self, args: List[str]) -> str:
        self._require_args(args, 2, "mv <src> <dest>")
        return self._format(self.kernel.mv(args[0], args[1]))

    def _cmd_stat(self, args: List[str]) -> str:
        self._require_args(args, 1, "stat <path>")
        return self._format(self.kernel.stat(args[0]))

    def _cmd_du(self, args: List[str]) -> str:
        return self._format(self.kernel.du(args[0] if args else "."))

    def _cmd_programs(self, args: List[str]) -> str:
        return self._format(self.kernel.list_programs())

    def _cmd_run(self, args: List[str]) -> str:
        self._require_args(args, 1, "run <program>")
        return self._format(self.kernel.launch_program(args[0]))

    def _cmd_tick(self, args: List[str]) -> str:
        count = 1
        if args:
            try:
                count = int(args[0])
            except ValueError as exc:
                raise ValueError("usage: tick [count]") from exc
        return self._format(self.kernel.tick(count))

    def _cmd_ps(self, args: List[str]) -> str:
        return self._format(self.kernel.ps())

    def _cmd_kill(self, args: List[str]) -> str:
        self._require_args(args, 1, "kill <pid>")
        try:
            pid = int(args[0])
        except ValueError as exc:
            raise ValueError("PID must be an integer") from exc
        return self._format(self.kernel.kill(pid))

    def _cmd_proc(self, args: List[str]) -> str:
        self._require_args(args, 1, "proc <pid>")
        try:
            pid = int(args[0])
        except ValueError as exc:
            raise ValueError("PID must be an integer") from exc
        return self._format(self.kernel.procinfo(pid))

    def _cmd_mem(self, args: List[str]) -> str:
        return self._format(self.kernel.mem())

    def _cmd_memmap(self, args: List[str]) -> str:
        return self._format(self.kernel.memmap())

    def _cmd_memhist(self, args: List[str]) -> str:
        return self._format(self.kernel.memhistory())

    def _cmd_keyfeed(self, args: List[str]) -> str:
        self._require_args(args, 1, "keyfeed <text>")
        return self._format(self.kernel.keyboard_feed(" ".join(args)))

    def _cmd_keyread(self, args: List[str]) -> str:
        return self._format(self.kernel.keyboard_read())

    def _cmd_screen(self, args: List[str]) -> str:
        limit = None
        if args:
            try:
                limit = int(args[0])
            except ValueError as exc:
                raise ValueError("screen limit must be an integer") from exc
        return self._format(self.kernel.screen_dump(limit))

    def _cmd_clear(self, args: List[str]) -> str:
        return self._format(self.kernel.screen_clear())
