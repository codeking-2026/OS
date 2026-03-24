"""Entry point for the pure-Python Pyos_v0.1 desktop simulator."""

from __future__ import annotations

import argparse

from pyos.services.kernel import Kernel
from pyos.ui.shell import Shell
from pyos.ui.window import run_gui


def run_cli() -> None:
    """Run the text shell."""

    Shell(Kernel()).repl()


def run_demo(script: str) -> None:
    """Run a semicolon-separated shell script."""

    shell = Shell(Kernel())
    print(shell.kernel.boot_report())
    for raw_command in script.split(";"):
        command = raw_command.strip()
        if not command:
            continue
        print(f"\n> {command}")
        output = shell.onecmd(command)
        if output:
            print(output)


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""

    parser = argparse.ArgumentParser(description="Pyos_v0.1 pure-Python desktop simulator")
    parser.add_argument("--cli", action="store_true", help="run the text shell instead of the desktop")
    parser.add_argument("--demo", action="store_true", help="run a built-in scripted demonstration")
    parser.add_argument("--script", type=str, help="run a semicolon-separated command script")
    return parser


def main() -> None:
    """Dispatch to GUI, CLI, or scripted demo mode."""

    args = build_parser().parse_args()
    if args.cli:
        run_cli()
        return
    if args.script:
        run_demo(args.script)
        return
    if args.demo:
        run_demo("help; programs; run clock; run editor; tick 4; ps; mem; tree C:/")
        return
    run_gui()


if __name__ == "__main__":
    main()
