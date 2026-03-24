"""
Core data structures for the OS simulator.

Example usage:
    from pyos.core.memory import MemoryManager

    memory = MemoryManager(total_kb=256)
    block = memory.allocate("editor", 32)
    memory.free(block.block_id)
"""
