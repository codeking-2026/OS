"""
Process management simulation.

This module models a very small process table, basic lifecycle states, and a
cooperative scheduler. It is intentionally simplified: there is one user, no
real CPU execution, and each process advances one synthetic "tick" at a time.

Example usage:
    from pyos.core.process import ProcessManager

    pm = ProcessManager()
    pid = pm.create_process("clock", instructions=5)
    pm.tick()
    print(pm.ps())
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


class ProcessState(str, Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"


@dataclass
class ProcessControlBlock:
    """Minimal process metadata."""

    pid: int
    name: str
    owner: str = "student"
    state: ProcessState = ProcessState.NEW
    instructions_total: int = 1
    instructions_remaining: int = 1
    memory_kb: int = 0
    created_at: str = field(default_factory=now_iso)
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    exit_code: Optional[int] = None
    log: List[str] = field(default_factory=list)
    waiting_ticks: int = 0

    def add_log(self, message: str) -> None:
        self.log.append(f"[{now_iso()}] {message}")

    @property
    def progress(self) -> float:
        if self.instructions_total == 0:
            return 100.0
        done = self.instructions_total - self.instructions_remaining
        return max(0.0, min(100.0, (done / self.instructions_total) * 100))

    def summary(self) -> str:
        return (
            f"{self.pid:>3}  {self.name:<14}  {self.state.value:<10}  "
            f"{self.memory_kb:>4} KB  {self.progress:>5.1f}%"
        )


class ProcessManager:
    """Cooperative process scheduler for the simulator."""

    def __init__(self) -> None:
        self._next_pid = 100
        self._processes: Dict[int, ProcessControlBlock] = {}
        self._ready_queue: List[int] = []
        self._running_pid: Optional[int] = None
        self._tick_count = 0
        self._listeners: List[Callable[[ProcessControlBlock, str], None]] = []

    def add_listener(self, callback: Callable[[ProcessControlBlock, str], None]) -> None:
        self._listeners.append(callback)

    def _emit(self, pcb: ProcessControlBlock, event: str) -> None:
        for listener in self._listeners:
            listener(pcb, event)

    def create_process(self, name: str, *, instructions: int = 5, memory_kb: int = 32) -> int:
        pid = self._next_pid
        self._next_pid += 1
        pcb = ProcessControlBlock(
            pid=pid,
            name=name,
            state=ProcessState.READY,
            instructions_total=max(1, instructions),
            instructions_remaining=max(1, instructions),
            memory_kb=max(1, memory_kb),
        )
        pcb.add_log("Process created")
        self._processes[pid] = pcb
        self._ready_queue.append(pid)
        self._emit(pcb, "created")
        return pid

    def get(self, pid: int) -> ProcessControlBlock:
        if pid not in self._processes:
            raise KeyError(f"No such PID: {pid}")
        return self._processes[pid]

    def list_processes(self, *, include_terminated: bool = True) -> List[ProcessControlBlock]:
        processes = [self._processes[pid] for pid in sorted(self._processes)]
        if include_terminated:
            return processes
        return [pcb for pcb in processes if pcb.state != ProcessState.TERMINATED]

    def _select_next_ready(self) -> Optional[ProcessControlBlock]:
        while self._ready_queue:
            pid = self._ready_queue.pop(0)
            pcb = self._processes.get(pid)
            if pcb is None:
                continue
            if pcb.state == ProcessState.READY:
                self._running_pid = pid
                pcb.state = ProcessState.RUNNING
                if pcb.started_at is None:
                    pcb.started_at = now_iso()
                pcb.add_log("Scheduled onto CPU")
                self._emit(pcb, "scheduled")
                return pcb
        self._running_pid = None
        return None

    def kill(self, pid: int, *, exit_code: int = -9) -> ProcessControlBlock:
        pcb = self.get(pid)
        if pcb.state == ProcessState.TERMINATED:
            return pcb
        pcb.state = ProcessState.TERMINATED
        pcb.instructions_remaining = 0
        pcb.exit_code = exit_code
        pcb.ended_at = now_iso()
        pcb.add_log(f"Terminated with exit code {exit_code}")
        if pid == self._running_pid:
            self._running_pid = None
        self._emit(pcb, "killed")
        return pcb

    def block(self, pid: int, ticks: int = 1) -> ProcessControlBlock:
        pcb = self.get(pid)
        if pcb.state == ProcessState.TERMINATED:
            return pcb
        pcb.state = ProcessState.WAITING
        pcb.waiting_ticks = max(1, ticks)
        pcb.add_log(f"Blocked for {pcb.waiting_ticks} tick(s)")
        if pid == self._running_pid:
            self._running_pid = None
        self._emit(pcb, "blocked")
        return pcb

    def _advance_waiting(self) -> None:
        for pcb in self._processes.values():
            if pcb.state != ProcessState.WAITING:
                continue
            pcb.waiting_ticks -= 1
            if pcb.waiting_ticks <= 0:
                pcb.state = ProcessState.READY
                pcb.add_log("I/O complete; moved to READY")
                self._ready_queue.append(pcb.pid)
                self._emit(pcb, "ready")

    def tick(self) -> Optional[ProcessControlBlock]:
        self._tick_count += 1
        self._advance_waiting()

        pcb = self._processes.get(self._running_pid) if self._running_pid else None
        if pcb is None or pcb.state != ProcessState.RUNNING:
            pcb = self._select_next_ready()
            if pcb is None:
                return None

        pcb.instructions_remaining -= 1
        pcb.add_log("Executed 1 instruction")
        self._emit(pcb, "tick")

        if pcb.instructions_remaining <= 0:
            pcb.state = ProcessState.TERMINATED
            pcb.exit_code = 0
            pcb.ended_at = now_iso()
            pcb.add_log("Completed successfully")
            self._running_pid = None
            self._emit(pcb, "terminated")
        else:
            pcb.state = ProcessState.READY
            pcb.add_log("Yielded CPU")
            self._ready_queue.append(pcb.pid)
            self._running_pid = None
            self._emit(pcb, "yielded")

        return pcb

    def run_until_idle(self, max_ticks: int = 100) -> int:
        ticks = 0
        while ticks < max_ticks:
            active = [
                pcb
                for pcb in self._processes.values()
                if pcb.state != ProcessState.TERMINATED
            ]
            if not active:
                break
            self.tick()
            ticks += 1
        return ticks

    def ps(self) -> str:
        lines = ["PID  NAME            STATE       MEM      PROGRESS"]
        for pcb in self.list_processes():
            lines.append(pcb.summary())
        return "\n".join(lines)

    def describe(self, pid: int) -> str:
        pcb = self.get(pid)
        lines = [
            f"PID: {pcb.pid}",
            f"Name: {pcb.name}",
            f"Owner: {pcb.owner}",
            f"State: {pcb.state.value}",
            f"Created: {pcb.created_at}",
            f"Started: {pcb.started_at or 'not started'}",
            f"Ended: {pcb.ended_at or 'still running'}",
            f"Memory: {pcb.memory_kb} KB",
            f"Instructions: {pcb.instructions_total - pcb.instructions_remaining}/{pcb.instructions_total}",
            f"Exit code: {pcb.exit_code if pcb.exit_code is not None else 'pending'}",
            "Recent log:",
        ]
        lines.extend(pcb.log[-8:] or ["<no log entries>"])
        return "\n".join(lines)

    def scheduler_state(self) -> dict:
        return {
            "tick_count": self._tick_count,
            "running_pid": self._running_pid,
            "ready_queue": list(self._ready_queue),
            "process_count": len(self._processes),
        }
