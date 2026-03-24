"""
Bundled demo programs for the OS simulator.

Programs here are intentionally lightweight. Each one returns a dictionary
describing the amount of CPU work, memory footprint, and optional shell output.
The kernel turns that description into a simulated process.

Example usage:
    from pyos.apps.demo_programs import build_demo_programs

    programs = build_demo_programs()
    print(programs["clock"]())
"""

from __future__ import annotations

from typing import Callable, Dict

ProgramFactory = Callable[[], dict]


def _clock_program() -> dict:
    return {
        "name": "clock",
        "instructions": 4,
        "memory_kb": 24,
        "output": "Clock process scheduled. It will tick a few times and exit.",
    }


def _editor_program() -> dict:
    return {
        "name": "editor",
        "instructions": 8,
        "memory_kb": 64,
        "output": "Editor started with an empty document buffer.",
    }


def _calc_program() -> dict:
    return {
        "name": "calc",
        "instructions": 5,
        "memory_kb": 20,
        "output": "Calculator warmed up and is ready for arithmetic.",
    }


def _backup_program() -> dict:
    return {
        "name": "backup",
        "instructions": 10,
        "memory_kb": 48,
        "output": "Backup job scanning files and packing archives.",
    }


def _type_program() -> dict:
    return {
        "name": "typewriter",
        "instructions": 6,
        "memory_kb": 18,
        "output": "Typewriter is polling the keyboard device for input.",
        "io_wait": 1,
    }


def build_demo_programs() -> Dict[str, ProgramFactory]:
    """Return the built-in simulated user programs."""

    return {
        "backup": _backup_program,
        "calc": _calc_program,
        "clock": _clock_program,
        "editor": _editor_program,
        "typewriter": _type_program,
    }
