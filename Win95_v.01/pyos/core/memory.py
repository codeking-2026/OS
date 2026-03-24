"""
Virtual memory tracking.

This module simulates a simple block allocator. It does not implement paging
or address translation in a hardware-accurate way, but it teaches the central
idea that processes request memory, hold blocks, and release them later.

Example usage:
    from pyos.core.memory import MemoryManager

    mm = MemoryManager(total_kb=128)
    block = mm.allocate("shell", 16)
    print(mm.report())
    mm.free(block.block_id)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List


def _ts() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class MemoryBlock:
    """Representation of one allocated range in simulated RAM."""

    block_id: int
    owner: str
    start_kb: int
    size_kb: int
    allocated_at: str = field(default_factory=_ts)

    @property
    def end_kb(self) -> int:
        return self.start_kb + self.size_kb - 1

    def summary(self) -> str:
        return (
            f"{self.block_id:>3}  {self.owner:<14}  "
            f"{self.start_kb:>4}-{self.end_kb:<4} KB  {self.size_kb:>4} KB"
        )


class MemoryManager:
    """Track virtual RAM reservations."""

    def __init__(self, total_kb: int = 1024) -> None:
        self.total_kb = total_kb
        self._next_block_id = 1
        self._blocks: Dict[int, MemoryBlock] = {}
        self._history: List[str] = [f"[{_ts()}] Memory manager initialized with {total_kb} KB"]

    def allocated_blocks(self) -> List[MemoryBlock]:
        return sorted(self._blocks.values(), key=lambda block: block.start_kb)

    def free_kb(self) -> int:
        return self.total_kb - sum(block.size_kb for block in self._blocks.values())

    def used_kb(self) -> int:
        return self.total_kb - self.free_kb()

    def _gaps(self) -> List[tuple[int, int]]:
        gaps: List[tuple[int, int]] = []
        current = 0
        for block in self.allocated_blocks():
            if block.start_kb > current:
                gaps.append((current, block.start_kb - current))
            current = block.end_kb + 1
        if current < self.total_kb:
            gaps.append((current, self.total_kb - current))
        return gaps

    def allocate(self, owner: str, size_kb: int) -> MemoryBlock:
        size_kb = max(1, size_kb)
        for gap_start, gap_size in self._gaps():
            if gap_size >= size_kb:
                block = MemoryBlock(
                    block_id=self._next_block_id,
                    owner=owner,
                    start_kb=gap_start,
                    size_kb=size_kb,
                )
                self._next_block_id += 1
                self._blocks[block.block_id] = block
                self._history.append(
                    f"[{_ts()}] Allocated block {block.block_id} to {owner} ({size_kb} KB)"
                )
                return block
        raise MemoryError(f"Not enough memory to allocate {size_kb} KB for {owner}")

    def free(self, block_id: int) -> MemoryBlock:
        if block_id not in self._blocks:
            raise KeyError(f"No such memory block: {block_id}")
        block = self._blocks.pop(block_id)
        self._history.append(f"[{_ts()}] Freed block {block_id} from {block.owner}")
        return block

    def free_owner(self, owner: str) -> List[MemoryBlock]:
        released = [block for block in self.allocated_blocks() if block.owner == owner]
        for block in released:
            self._blocks.pop(block.block_id, None)
            self._history.append(f"[{_ts()}] Freed block {block.block_id} from {block.owner}")
        return released

    def owner_usage(self, owner: str) -> int:
        return sum(block.size_kb for block in self._blocks.values() if block.owner == owner)

    def report(self) -> str:
        lines = [
            f"RAM total: {self.total_kb} KB",
            f"RAM used : {self.used_kb()} KB",
            f"RAM free : {self.free_kb()} KB",
            "",
            "ID  OWNER           RANGE         SIZE",
        ]
        blocks = self.allocated_blocks()
        if not blocks:
            lines.append("<no allocated blocks>")
        else:
            lines.extend(block.summary() for block in blocks)
        return "\n".join(lines)

    def fragmentation_report(self) -> str:
        gaps = self._gaps()
        lines = ["Free gaps:"]
        if not gaps:
            lines.append("<no free gaps>")
        else:
            for start, size in gaps:
                end = start + size - 1
                lines.append(f"{start:>4}-{end:<4} KB  {size:>4} KB free")
        return "\n".join(lines)

    def history(self, limit: int = 10) -> str:
        return "\n".join(self._history[-limit:])
