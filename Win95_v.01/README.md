# pyOS

`pyOS` is a small educational operating system simulator for a single user.
It runs entirely in Python and keeps its virtual filesystem in memory.

## Features

- Command-line shell with commands such as `ls`, `cat`, `mkdir`, `rm`, `ps`, and `mem`
- In-memory virtual filesystem with directories, files, tree walking, and metadata
- Simulated process creation, scheduling, blocking, and termination
- Virtual memory tracking with first-fit allocation and fragmentation reporting
- Simple keyboard and screen device simulation
- Modular project structure with comments and example usage in every module

## Run

```bash
python main.py
```

This now opens a desktop window with sign-up and sign-in, then the simulator UI.

## CLI shell

```bash
python main.py --cli
```

## Demo

```bash
python main.py --demo
```

## Scripted example

```bash
python main.py --script "ls; run clock; tick 4; ps; mem"
```

## Project layout

- `main.py`: entry point
- `pyos/core`: filesystem, process, and memory primitives
- `pyos/services`: kernel and device abstractions
- `pyos/ui`: interactive shell
- `pyos/apps`: bundled demo programs
