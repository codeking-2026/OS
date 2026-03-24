#!/usr/bin/env python3
# =============================================================================
#  PyOS v5.0 — Professional Desktop OS Simulation
#  Pure Python + Tkinter ONLY. Zero external dependencies.
#  Target: ~18,000 lines across all modules combined in one file.
#
#  APPLICATIONS (20 total):
#    File Manager, Text Editor, Terminal (60+ cmds), Browser, Music Player,
#    Paint Studio, Calculator (4 modes), Clock/Alarm/World Clock, Task Manager,
#    System Monitor, Notes, Email Client, Password Manager, Spreadsheet,
#    Image Viewer, Disk Analyzer, Code Runner, App Store, Settings, Archive Manager
#
#  FEATURES:
#    • Full virtual filesystem (VFS) with Unix-like paths
#    • Multi-user login system with password hashing
#    • Draggable/resizable floating windows
#    • Taskbar with Start Menu, system tray, clock
#    • Desktop with wallpaper, icons, right-click menus
#    • Notification system
#    • Clipboard (text + file)
#    • Process manager with live CPU/RAM simulation
#    • Theme engine (5 themes)
#    • Lock screen
#    • Boot animation
#
#  Run:  python pyos_v5.py
# =============================================================================

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, simpledialog, font as tkfont
import os, sys, time, datetime, math, random, threading, json, re
import hashlib, calendar, traceback, uuid, base64, platform, io, copy
import colorsys, struct, zipfile, gzip, textwrap, string, queue
from collections import deque, defaultdict, OrderedDict
from functools import partial, lru_cache
from typing import Dict, List, Optional, Tuple, Any, Callable

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 1 — GLOBAL CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

PYOS_VERSION   = "5.0.0"
PYOS_CODENAME  = "Nebula"
BUILD_DATE     = "2025"

SCREEN_W       = 1280
SCREEN_H       = 800
TASKBAR_H      = 52
TITLEBAR_H     = 32
WIN_MIN_W      = 220
WIN_MIN_H      = 160
BORDER_W       = 3
ICON_SIZE      = 52      # desktop icon cell size
GRID_COLS      = 2       # desktop icon columns on left side

# Default font stack (falls back gracefully on any OS)
FONT_UI        = "Segoe UI"
FONT_MONO      = "Consolas"
FONT_EMOJI     = "Segoe UI Emoji"

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 2 — THEME ENGINE
# ─────────────────────────────────────────────────────────────────────────────

THEMES: Dict[str, Dict[str, str]] = {

    # ── Dark Blue (default GitHub-inspired) ──────────────────────────────────
    "Dark Blue": {
        "desktop_bg":         "#0d1117",
        "taskbar_bg":         "#161b22",
        "taskbar_fg":         "#e6edf3",
        "taskbar_border":     "#21262d",
        "win_title_active":   "#1c2128",
        "win_title_inactive": "#13161c",
        "win_title_fg":       "#e6edf3",
        "win_title_fg_in":    "#484f58",
        "win_border":         "#30363d",
        "win_border_active":  "#388bfd",
        "win_bg":             "#0d1117",
        "panel_bg":           "#161b22",
        "panel_alt":          "#1c2128",
        "accent":             "#388bfd",
        "accent2":            "#bf91f9",
        "accent3":            "#3fb950",
        "danger":             "#f85149",
        "success":            "#3fb950",
        "warning":            "#d29922",
        "info":               "#58a6ff",
        "text":               "#e6edf3",
        "text_muted":         "#7d8590",
        "text_dim":           "#21262d",
        "text_inverse":       "#0d1117",
        "input_bg":           "#0d1117",
        "input_border":       "#30363d",
        "input_focus":        "#388bfd",
        "button_bg":          "#21262d",
        "button_hover":       "#30363d",
        "button_active":      "#388bfd",
        "menu_bg":            "#161b22",
        "menu_hover":         "#21262d",
        "menu_border":        "#30363d",
        "selection":          "#264f78",
        "scrollbar":          "#21262d",
        "scrollbar_thumb":    "#484f58",
        "status_bg":          "#161b22",
        "status_border":      "#21262d",
        "tag_bg":             "#1f2d45",
        "tag_fg":             "#388bfd",
        "code_bg":            "#161b22",
        "code_fg":            "#e6edf3",
        "tooltip_bg":         "#1c2128",
        "tooltip_fg":         "#e6edf3",
        "shadow":             "#000000",
        "badge_bg":           "#da3633",
        "badge_fg":           "#ffffff",
        "progress_bg":        "#21262d",
        "progress_fg":        "#388bfd",
        "link":               "#58a6ff",
        "separator":          "#21262d",
        "chart1":             "#388bfd",
        "chart2":             "#3fb950",
        "chart3":             "#d29922",
        "chart4":             "#f85149",
        "chart5":             "#bf91f9",
    },

    # ── Dracula ───────────────────────────────────────────────────────────────
    "Dracula": {
        "desktop_bg":         "#282a36",
        "taskbar_bg":         "#1e1f29",
        "taskbar_fg":         "#f8f8f2",
        "taskbar_border":     "#44475a",
        "win_title_active":   "#343746",
        "win_title_inactive": "#282a36",
        "win_title_fg":       "#f8f8f2",
        "win_title_fg_in":    "#6272a4",
        "win_border":         "#44475a",
        "win_border_active":  "#bd93f9",
        "win_bg":             "#282a36",
        "panel_bg":           "#1e1f29",
        "panel_alt":          "#343746",
        "accent":             "#bd93f9",
        "accent2":            "#ff79c6",
        "accent3":            "#50fa7b",
        "danger":             "#ff5555",
        "success":            "#50fa7b",
        "warning":            "#ffb86c",
        "info":               "#8be9fd",
        "text":               "#f8f8f2",
        "text_muted":         "#6272a4",
        "text_dim":           "#44475a",
        "text_inverse":       "#282a36",
        "input_bg":           "#21222c",
        "input_border":       "#44475a",
        "input_focus":        "#bd93f9",
        "button_bg":          "#44475a",
        "button_hover":       "#6272a4",
        "button_active":      "#bd93f9",
        "menu_bg":            "#21222c",
        "menu_hover":         "#44475a",
        "menu_border":        "#6272a4",
        "selection":          "#44475a",
        "scrollbar":          "#44475a",
        "scrollbar_thumb":    "#6272a4",
        "status_bg":          "#1e1f29",
        "status_border":      "#44475a",
        "tag_bg":             "#3d2f5a",
        "tag_fg":             "#bd93f9",
        "code_bg":            "#21222c",
        "code_fg":            "#f8f8f2",
        "tooltip_bg":         "#1e1f29",
        "tooltip_fg":         "#f8f8f2",
        "shadow":             "#000000",
        "badge_bg":           "#ff5555",
        "badge_fg":           "#f8f8f2",
        "progress_bg":        "#44475a",
        "progress_fg":        "#bd93f9",
        "link":               "#8be9fd",
        "separator":          "#44475a",
        "chart1":             "#bd93f9",
        "chart2":             "#50fa7b",
        "chart3":             "#ffb86c",
        "chart4":             "#ff5555",
        "chart5":             "#ff79c6",
    },

    # ── Nord ─────────────────────────────────────────────────────────────────
    "Nord": {
        "desktop_bg":         "#2e3440",
        "taskbar_bg":         "#242933",
        "taskbar_fg":         "#eceff4",
        "taskbar_border":     "#3b4252",
        "win_title_active":   "#3b4252",
        "win_title_inactive": "#2e3440",
        "win_title_fg":       "#eceff4",
        "win_title_fg_in":    "#4c566a",
        "win_border":         "#3b4252",
        "win_border_active":  "#88c0d0",
        "win_bg":             "#2e3440",
        "panel_bg":           "#242933",
        "panel_alt":          "#3b4252",
        "accent":             "#88c0d0",
        "accent2":            "#b48ead",
        "accent3":            "#a3be8c",
        "danger":             "#bf616a",
        "success":            "#a3be8c",
        "warning":            "#ebcb8b",
        "info":               "#81a1c1",
        "text":               "#eceff4",
        "text_muted":         "#7b88a1",
        "text_dim":           "#3b4252",
        "text_inverse":       "#2e3440",
        "input_bg":           "#2e3440",
        "input_border":       "#3b4252",
        "input_focus":        "#88c0d0",
        "button_bg":          "#3b4252",
        "button_hover":       "#434c5e",
        "button_active":      "#88c0d0",
        "menu_bg":            "#3b4252",
        "menu_hover":         "#434c5e",
        "menu_border":        "#4c566a",
        "selection":          "#4c566a",
        "scrollbar":          "#3b4252",
        "scrollbar_thumb":    "#4c566a",
        "status_bg":          "#242933",
        "status_border":      "#3b4252",
        "tag_bg":             "#2e3f50",
        "tag_fg":             "#88c0d0",
        "code_bg":            "#3b4252",
        "code_fg":            "#eceff4",
        "tooltip_bg":         "#3b4252",
        "tooltip_fg":         "#eceff4",
        "shadow":             "#191d24",
        "badge_bg":           "#bf616a",
        "badge_fg":           "#eceff4",
        "progress_bg":        "#3b4252",
        "progress_fg":        "#88c0d0",
        "link":               "#81a1c1",
        "separator":          "#3b4252",
        "chart1":             "#88c0d0",
        "chart2":             "#a3be8c",
        "chart3":             "#ebcb8b",
        "chart4":             "#bf616a",
        "chart5":             "#b48ead",
    },

    # ── Light ─────────────────────────────────────────────────────────────────
    "Light": {
        "desktop_bg":         "#f0f2f5",
        "taskbar_bg":         "#ffffff",
        "taskbar_fg":         "#1f2937",
        "taskbar_border":     "#e5e7eb",
        "win_title_active":   "#f9fafb",
        "win_title_inactive": "#f3f4f6",
        "win_title_fg":       "#111827",
        "win_title_fg_in":    "#9ca3af",
        "win_border":         "#e5e7eb",
        "win_border_active":  "#3b82f6",
        "win_bg":             "#ffffff",
        "panel_bg":           "#f9fafb",
        "panel_alt":          "#f3f4f6",
        "accent":             "#3b82f6",
        "accent2":            "#8b5cf6",
        "accent3":            "#22c55e",
        "danger":             "#ef4444",
        "success":            "#22c55e",
        "warning":            "#f59e0b",
        "info":               "#3b82f6",
        "text":               "#111827",
        "text_muted":         "#6b7280",
        "text_dim":           "#d1d5db",
        "text_inverse":       "#ffffff",
        "input_bg":           "#ffffff",
        "input_border":       "#d1d5db",
        "input_focus":        "#3b82f6",
        "button_bg":          "#f3f4f6",
        "button_hover":       "#e5e7eb",
        "button_active":      "#3b82f6",
        "menu_bg":            "#ffffff",
        "menu_hover":         "#f3f4f6",
        "menu_border":        "#e5e7eb",
        "selection":          "#bfdbfe",
        "scrollbar":          "#e5e7eb",
        "scrollbar_thumb":    "#9ca3af",
        "status_bg":          "#f9fafb",
        "status_border":      "#e5e7eb",
        "tag_bg":             "#eff6ff",
        "tag_fg":             "#3b82f6",
        "code_bg":            "#f3f4f6",
        "code_fg":            "#111827",
        "tooltip_bg":         "#1f2937",
        "tooltip_fg":         "#f9fafb",
        "shadow":             "#9ca3af",
        "badge_bg":           "#ef4444",
        "badge_fg":           "#ffffff",
        "progress_bg":        "#e5e7eb",
        "progress_fg":        "#3b82f6",
        "link":               "#2563eb",
        "separator":          "#e5e7eb",
        "chart1":             "#3b82f6",
        "chart2":             "#22c55e",
        "chart3":             "#f59e0b",
        "chart4":             "#ef4444",
        "chart5":             "#8b5cf6",
    },

    # ── Monokai ───────────────────────────────────────────────────────────────
    "Monokai": {
        "desktop_bg":         "#1e1e1e",
        "taskbar_bg":         "#272822",
        "taskbar_fg":         "#f8f8f2",
        "taskbar_border":     "#3e3d32",
        "win_title_active":   "#2d2c27",
        "win_title_inactive": "#1e1e1e",
        "win_title_fg":       "#f8f8f2",
        "win_title_fg_in":    "#75715e",
        "win_border":         "#3e3d32",
        "win_border_active":  "#a6e22e",
        "win_bg":             "#272822",
        "panel_bg":           "#1e1e1e",
        "panel_alt":          "#2d2c27",
        "accent":             "#a6e22e",
        "accent2":            "#ae81ff",
        "accent3":            "#a6e22e",
        "danger":             "#f92672",
        "success":            "#a6e22e",
        "warning":            "#e6db74",
        "info":               "#66d9e8",
        "text":               "#f8f8f2",
        "text_muted":         "#75715e",
        "text_dim":           "#3e3d32",
        "text_inverse":       "#272822",
        "input_bg":           "#1e1e1e",
        "input_border":       "#3e3d32",
        "input_focus":        "#a6e22e",
        "button_bg":          "#3e3d32",
        "button_hover":       "#49483e",
        "button_active":      "#a6e22e",
        "menu_bg":            "#272822",
        "menu_hover":         "#3e3d32",
        "menu_border":        "#49483e",
        "selection":          "#49483e",
        "scrollbar":          "#3e3d32",
        "scrollbar_thumb":    "#75715e",
        "status_bg":          "#1e1e1e",
        "status_border":      "#3e3d32",
        "tag_bg":             "#2a3020",
        "tag_fg":             "#a6e22e",
        "code_bg":            "#1e1e1e",
        "code_fg":            "#f8f8f2",
        "tooltip_bg":         "#272822",
        "tooltip_fg":         "#f8f8f2",
        "shadow":             "#000000",
        "badge_bg":           "#f92672",
        "badge_fg":           "#f8f8f2",
        "progress_bg":        "#3e3d32",
        "progress_fg":        "#a6e22e",
        "link":               "#66d9e8",
        "separator":          "#3e3d32",
        "chart1":             "#a6e22e",
        "chart2":             "#ae81ff",
        "chart3":             "#e6db74",
        "chart4":             "#f92672",
        "chart5":             "#66d9e8",
    
    },
}

# Active theme — mutable dict, updated when user changes theme
T: Dict[str, str] = dict(THEMES["Dark Blue"])

def apply_theme(name: str) -> None:
    """Apply a named theme globally by updating the T dict in-place."""
    global T
    if name in THEMES:
        T.clear()
        T.update(THEMES[name])


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 3 — VIRTUAL FILE SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

class VFSNode:
    """A single node (file or directory) in the virtual file system."""

    __slots__ = (
        "name", "is_dir", "_content", "children", "parent",
        "created", "modified", "accessed",
        "permissions", "owner", "group", "metadata",
    )

    def __init__(
        self,
        name: str,
        is_dir: bool = False,
        content: str = "",
        parent: Optional["VFSNode"] = None,
        owner: str = "user",
    ) -> None:
        self.name        = name
        self.is_dir      = is_dir
        self._content    = content
        self.children: Dict[str, "VFSNode"] = {}
        self.parent      = parent
        now              = time.time()
        self.created     = now
        self.modified    = now
        self.accessed    = now
        self.permissions = "rwxr-xr-x" if is_dir else "rw-r--r--"
        self.owner       = owner
        self.group       = owner
        self.metadata: Dict[str, Any] = {}

    # ── content property ─────────────────────────────────────────────────────

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value
        self.modified = time.time()

    # ── computed properties ──────────────────────────────────────────────────

    @property
    def size(self) -> int:
        if self.is_dir:
            return sum(c.size for c in self.children.values())
        return len(self._content.encode("utf-8", errors="replace"))

    @property
    def size_str(self) -> str:
        b = self.size
        for unit in ("B", "KB", "MB", "GB"):
            if b < 1024:
                return f"{b:.1f} {unit}"
            b /= 1024
        return f"{b:.1f} TB"

    # ── helpers ──────────────────────────────────────────────────────────────

    def touch(self) -> None:
        self.accessed = self.modified = time.time()

    def full_path(self) -> str:
        parts: List[str] = []
        node: Optional[VFSNode] = self
        while node and node.name != "/":
            parts.append(node.name)
            node = node.parent
        return "/" + "/".join(reversed(parts))

    def stat(self) -> Dict[str, Any]:
        return {
            "name":        self.name,
            "full_path":   self.full_path(),
            "is_dir":      self.is_dir,
            "size":        self.size,
            "size_str":    self.size_str,
            "created":     self.created,
            "modified":    self.modified,
            "accessed":    self.accessed,
            "permissions": self.permissions,
            "owner":       self.owner,
            "group":       self.group,
        }

    def __repr__(self) -> str:
        t = "DIR" if self.is_dir else "FILE"
        return f"<VFSNode {t} {self.name!r}>"


class VFS:
    """
    Full Unix-like in-memory virtual file system.

    Files are ALSO persisted to a real folder on disk so that
    your data survives between sessions.

    Real-disk root (Windows default):
        C:/Users/<you>/PyOS          <- vfs /home/user maps here
        C:/Users/<you>/PyOS/system   <- vfs /etc, /var, /bin ... map here

    Override at startup by setting the env-var  PYOS_ROOT  e.g.:
        set PYOS_ROOT=D:/MyPyOS && python OS.py

    Supports:
      - Absolute and relative paths
      - . and .. resolution
      - mkdir, makedirs, rmdir (recursive)
      - read, write (create/overwrite/append)
      - rename, copy
      - find (glob-like pattern search)
      - tree (pretty-print directory structure)
      - stat, listdir, exists, isdir, isfile
      - disk_usage
      - get_all_files (recursive file list)
    """

    HOME = "/home/user"

    # -- Real-disk helpers -------------------------------------------------

    @staticmethod
    def _get_real_root() -> str:
        env = os.environ.get("PYOS_ROOT", "").strip()
        if env:
            return env
        home = os.path.expanduser("~")
        return os.path.join(home, "PyOS")

    def _vfs_to_real(self, vfs_path: str) -> str:
        vfs_path = self.resolve(vfs_path)
        if vfs_path == self.HOME:
            rel = ""
        elif vfs_path.startswith(self.HOME + "/"):
            rel = vfs_path[len(self.HOME) + 1:]
        else:
            rel = "system" + vfs_path
        parts = rel.replace("/", os.sep).split(os.sep)
        return os.path.join(self._real_root, *parts)

    def _disk_mkdir(self, vfs_path: str) -> None:
        try:
            os.makedirs(self._vfs_to_real(vfs_path), exist_ok=True)
        except Exception:
            pass

    def _disk_write(self, vfs_path: str, content: str) -> None:
        try:
            real = self._vfs_to_real(vfs_path)
            os.makedirs(os.path.dirname(real), exist_ok=True)
            with open(real, "w", encoding="utf-8") as fh:
                fh.write(content)
        except Exception:
            pass

    def _disk_delete(self, vfs_path: str) -> None:
        try:
            real = self._vfs_to_real(vfs_path)
            if os.path.isfile(real):
                os.remove(real)
            elif os.path.isdir(real):
                import shutil
                shutil.rmtree(real, ignore_errors=True)
        except Exception:
            pass

    def _disk_rename(self, vfs_src: str, vfs_dst: str) -> None:
        try:
            src_real = self._vfs_to_real(vfs_src)
            dst_real = self._vfs_to_real(vfs_dst)
            if os.path.exists(src_real):
                os.makedirs(os.path.dirname(dst_real), exist_ok=True)
                os.rename(src_real, dst_real)
        except Exception:
            pass

    def _load_from_disk(self) -> None:
        """Restore files written in previous sessions from real disk."""
        for dirpath, dirnames, filenames in os.walk(self._real_root):
            rel = os.path.relpath(dirpath, self._real_root)
            if rel == ".":
                vfs_dir = self.HOME
            elif rel.startswith("system" + os.sep):
                inner = rel[len("system"):]
                vfs_dir = inner.replace(os.sep, "/")
            elif rel.startswith("system"):
                vfs_dir = "/" + rel[len("system"):].replace(os.sep, "/")
            else:
                vfs_dir = self.HOME + "/" + rel.replace(os.sep, "/")
            self._mkdir_mem(vfs_dir)
            for fname in filenames:
                real_file = os.path.join(dirpath, fname)
                vfs_file  = vfs_dir.rstrip("/") + "/" + fname
                try:
                    with open(real_file, "r", encoding="utf-8", errors="replace") as fh:
                        fc = fh.read()
                    self._write_mem(vfs_file, fc)
                except Exception:
                    pass

    # -- Memory-only helpers (used during init / restore) ------------------

    def _mkdir_mem(self, path: str) -> None:
        path = self.resolve(path)
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        name = path.split("/")[-1]
        if not name:
            return
        parent = self._get_node(parent_path)
        if parent is None:
            self._mkdir_mem(parent_path)
            parent = self._get_node(parent_path)
        if parent and name not in parent.children:
            parent.children[name] = VFSNode(name, is_dir=True, parent=parent)

    def _write_mem(self, path: str, content: str, append: bool = False) -> None:
        path = self.resolve(path)
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        name = path.split("/")[-1]
        if not name:
            return
        parent = self._get_node(parent_path)
        if parent is None:
            self._mkdir_mem(parent_path)
            parent = self._get_node(parent_path)
        if parent is None:
            return
        if name in parent.children and parent.children[name].is_dir:
            return
        if append and name in parent.children:
            parent.children[name]._content += content
            parent.children[name].modified = time.time()
        else:
            node = VFSNode(name, is_dir=False, content=content, parent=parent)
            parent.children[name] = node

    def __init__(self) -> None:
        self.root = VFSNode("/", is_dir=True, owner="root")
        self.root.parent = self.root
        self.cwd  = "/"
        # -- Real-disk root (created automatically) ------------------------
        self._real_root: str = self._get_real_root()
        os.makedirs(self._real_root, exist_ok=True)
        # -- Build default tree, then restore any saved files from disk ----
        self._build_default_tree()
        self._load_from_disk()

    # ── bootstrap ─────────────────────────────────────────────────────────────

    def _build_default_tree(self) -> None:
        """Populate a realistic default directory tree with sample files."""
        dirs = [
            "/bin", "/etc", "/etc/pyos",
            "/home", "/home/user",
            "/home/user/Desktop",
            "/home/user/Documents",
            "/home/user/Downloads",
            "/home/user/Music",
            "/home/user/Pictures",
            "/home/user/Videos",
            "/home/user/Code",
            "/home/user/Spreadsheets",
            "/home/user/Passwords",
            "/home/user/Archives",
            "/tmp",
            "/var", "/var/log", "/var/cache",
            "/usr", "/usr/bin", "/usr/share",
            "/proc", "/dev",
        ]
        for d in dirs:
            self.makedirs(d)

        default_files: Dict[str, str] = {
            # system
            "/etc/hostname":
                "pyos-machine\n",
            "/etc/os-release":
                f'NAME="PyOS"\nVERSION="{PYOS_VERSION}"\n'
                f'CODENAME="{PYOS_CODENAME}"\nID=pyos\n',
            "/etc/passwd":
                "root:x:0:0:root:/root:/bin/sh\n"
                "user:x:1000:1000:Default User:/home/user:/bin/sh\n"
                "guest:x:1001:1001:Guest:/home/user:/bin/sh\n",
            "/etc/motd":
                f"Welcome to PyOS {PYOS_VERSION} ({PYOS_CODENAME})!\n"
                "Type 'help' in the terminal for a full command list.\n",
            "/etc/pyos/pyos.conf":
                "[general]\ntheme=Dark Blue\nwallpaper=gradient_blue\n"
                "autosave=60\n\n[terminal]\nfont_size=10\nhistory=1000\n",
            "/proc/cpuinfo":
                "processor\t: 0\nmodel name\t: PyOS Virtual CPU @ 3.2GHz\n"
                "cpu cores\t: 4\ncpu MHz\t\t: 3200.000\ncache size\t: 8192 KB\n",
            "/proc/meminfo":
                "MemTotal:\t8388608 kB\nMemFree:\t4194304 kB\n"
                "MemAvailable:\t5242880 kB\nSwapTotal:\t2097152 kB\nSwapFree:\t2097152 kB\n",
            "/var/log/system.log":
                f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] INFO  PyOS kernel started\n"
                f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] INFO  VFS mounted at /\n"
                f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] INFO  Window Manager initialized\n",

            # home
            "/home/user/Documents/readme.txt":
                "Welcome to PyOS v5.0!\n"
                "=======================\n\n"
                "This is a fully simulated desktop OS built in pure Python.\n"
                "All 20 apps are built-in — no pip install required.\n\n"
                "Key shortcuts:\n"
                "  • Double-click desktop icon to open app\n"
                "  • Right-click desktop for context menu\n"
                "  • Ctrl+S in editor to save\n"
                "  • Ctrl+F in editor to find\n"
                "  • Tab in terminal for autocomplete\n"
                "  • ↑↓ in terminal for history\n\n"
                "Enjoy PyOS!\n",

            "/home/user/Documents/notes.txt":
                "My Notes\n"
                "=========\n\n"
                "[ ] Review PyOS features\n"
                "[ ] Explore the file manager\n"
                "[x] Install PyOS\n"
                "[ ] Set up password vault\n"
                "[ ] Write documentation\n",

            "/home/user/Documents/project_plan.txt":
                "Project Plan — Q1 2025\n"
                "=======================\n\n"
                "Phase 1: Design\n"
                "  - Wireframes          [DONE]\n"
                "  - Color palette       [DONE]\n"
                "  - Component library   [IN PROGRESS]\n\n"
                "Phase 2: Development\n"
                "  - Frontend setup      [TODO]\n"
                "  - Backend API         [TODO]\n"
                "  - Database schema     [TODO]\n\n"
                "Phase 3: Testing\n"
                "  - Unit tests          [TODO]\n"
                "  - Integration tests   [TODO]\n"
                "  - Performance tests   [TODO]\n",

            "/home/user/Code/hello.py":
                "#!/usr/bin/env python3\n"
                '"""Hello World — first PyOS script."""\n\n'
                "def greet(name: str) -> str:\n"
                '    return f"Hello, {name}! Welcome to PyOS."\n\n\n'
                'if __name__ == "__main__":\n'
                '    message = greet("World")\n'
                "    print(message)\n",

            "/home/user/Code/fibonacci.py":
                "#!/usr/bin/env python3\n"
                '"""Fibonacci sequence generator."""\n\n'
                "from typing import Generator\n\n\n"
                "def fibonacci(n: int) -> Generator[int, None, None]:\n"
                '    """Yield the first n Fibonacci numbers."""\n'
                "    a, b = 0, 1\n"
                "    for _ in range(n):\n"
                "        yield a\n"
                "        a, b = b, a + b\n\n\n"
                'if __name__ == "__main__":\n'
                "    result = list(fibonacci(20))\n"
                "    print(f'First 20 Fibonacci numbers:')\n"
                "    print(result)\n"
                "    print(f'Sum: {sum(result)}')\n",

            "/home/user/Code/data_analysis.py":
                "#!/usr/bin/env python3\n"
                '"""Basic data analysis helpers."""\n\n'
                "import math\n"
                "from typing import List\n\n\n"
                "def mean(data: List[float]) -> float:\n"
                "    return sum(data) / len(data)\n\n\n"
                "def variance(data: List[float]) -> float:\n"
                "    m = mean(data)\n"
                "    return sum((x - m) ** 2 for x in data) / len(data)\n\n\n"
                "def std_dev(data: List[float]) -> float:\n"
                "    return math.sqrt(variance(data))\n\n\n"
                "def median(data: List[float]) -> float:\n"
                "    s = sorted(data)\n"
                "    n = len(s)\n"
                "    return s[n // 2] if n % 2 else (s[n//2 - 1] + s[n//2]) / 2\n\n\n"
                "# Sample usage\n"
                "data = [23, 45, 12, 67, 34, 89, 56, 78, 90, 11, 43, 65]\n"
                "print(f'Mean:    {mean(data):.2f}')\n"
                "print(f'Median:  {median(data):.2f}')\n"
                "print(f'Std Dev: {std_dev(data):.2f}')\n"
                "print(f'Min:     {min(data)}')\n"
                "print(f'Max:     {max(data)}')\n",

            "/home/user/Code/web_scraper.py":
                "#!/usr/bin/env python3\n"
                '"""Simulated web scraper (demo — no actual HTTP calls)."""\n\n'
                "import re\n"
                "from typing import List, Dict\n\n\n"
                "def extract_links(html: str) -> List[str]:\n"
                '    """Extract all href links from HTML."""\n'
                '    pattern = r\'href=["\\\']([^"\\\']+)["\\\']\'\n'
                "    return re.findall(pattern, html)\n\n\n"
                "def extract_text(html: str) -> str:\n"
                '    """Strip HTML tags and return plain text."""\n'
                "    return re.sub(r'<[^>]+>', '', html)\n\n\n"
                "# Demo\n"
                "sample_html = '<a href=\"https://example.com\">Click</a>'\n"
                "print(extract_links(sample_html))\n"
                "print(extract_text(sample_html))\n",

            "/home/user/Spreadsheets/budget.csv":
                "Month,Income,Expenses,Savings,Notes\n"
                "January,5000.00,3200.00,1800.00,Good start\n"
                "February,5000.00,2900.00,2100.00,Reduced dining out\n"
                "March,5500.00,3100.00,2400.00,Got a raise\n"
                "April,5500.00,3400.00,2100.00,Car repair\n"
                "May,6000.00,3200.00,2800.00,Bonus month\n"
                "June,6000.00,3500.00,2500.00,Vacation planned\n"
                "July,6000.00,4200.00,1800.00,Vacation\n"
                "August,6000.00,3100.00,2900.00,Back to normal\n"
                "September,6500.00,3300.00,3200.00,New project\n"
                "October,6500.00,3400.00,3100.00,Stable\n"
                "November,6500.00,3800.00,2700.00,Holiday prep\n"
                "December,7000.00,5000.00,2000.00,Holidays\n",

            "/home/user/Spreadsheets/inventory.csv":
                "Item,SKU,Quantity,Unit Price,Total Value,Category\n"
                "Laptop,LAP-001,15,999.99,14999.85,Electronics\n"
                "Monitor,MON-002,20,349.99,6999.80,Electronics\n"
                "Keyboard,KEY-003,50,79.99,3999.50,Peripherals\n"
                "Mouse,MOU-004,50,49.99,2499.50,Peripherals\n"
                "Desk Chair,CHR-005,10,299.99,2999.90,Furniture\n"
                "Standing Desk,DSK-006,8,599.99,4799.92,Furniture\n"
                "USB Hub,USB-007,30,39.99,1199.70,Accessories\n"
                "Webcam,CAM-008,25,89.99,2249.75,Peripherals\n"
                "Headset,HDS-009,20,149.99,2999.80,Audio\n"
                "SSD 1TB,SSD-010,40,119.99,4799.60,Storage\n",

            "/home/user/Spreadsheets/employees.csv":
                "ID,Name,Department,Role,Salary,Start Date,Status\n"
                "E001,Alice Johnson,Engineering,Senior Engineer,95000,2020-03-15,Active\n"
                "E002,Bob Smith,Marketing,Marketing Manager,78000,2019-07-01,Active\n"
                "E003,Carol White,Engineering,Junior Engineer,65000,2022-01-10,Active\n"
                "E004,David Brown,HR,HR Specialist,72000,2021-05-20,Active\n"
                "E005,Eve Davis,Engineering,Tech Lead,110000,2018-09-03,Active\n"
                "E006,Frank Miller,Sales,Sales Rep,68000,2023-02-14,Active\n"
                "E007,Grace Lee,Design,UI Designer,82000,2020-11-30,Active\n"
                "E008,Henry Wilson,Finance,Accountant,75000,2019-04-22,On Leave\n",

            "/home/user/Music/playlist.m3u":
                "# PyOS Music Playlist v1\n"
                "# Generated by PyOS Music Player\n\n"
                "#EXTM3U\n"
                "#EXTINF:213,Cyber Dreams - PyOS Audio\n"
                "Cyber_Dreams.mp3\n"
                "#EXTINF:187,Digital Rain - Tkinter Band\n"
                "Digital_Rain.mp3\n"
                "#EXTINF:234,Electric Pulse - ByteWave\n"
                "Electric_Pulse.mp3\n"
                "#EXTINF:198,Neon Nights - PyOS Audio\n"
                "Neon_Nights.mp3\n",

            "/home/user/Desktop/about.txt":
                f"PyOS v{PYOS_VERSION} ({PYOS_CODENAME})\n"
                "Pure Python Desktop OS\n"
                "Built with Tkinter\n"
                "Zero external dependencies\n",

            "/tmp/README":
                "This is the /tmp directory.\n"
                "Files here are temporary and may be deleted at any time.\n",
        }

        for path, content in default_files.items():
            self.write(path, content)

    # ── internal path helpers ─────────────────────────────────────────────────

    def resolve(self, path: str) -> str:
        """Resolve a path to an absolute canonical path string."""
        if not path.startswith("/"):
            path = self.cwd.rstrip("/") + "/" + path
        parts: List[str] = []
        for p in path.split("/"):
            if p in ("", "."):
                continue
            elif p == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(p)
        return "/" + "/".join(parts)

    def _get_node(self, path: str) -> Optional[VFSNode]:
        """Return the VFSNode at *path*, or None if not found."""
        path = self.resolve(path)
        if path == "/":
            return self.root
        node = self.root
        for part in path.strip("/").split("/"):
            if not part:
                continue
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node

    def _parent_and_name(self, path: str) -> Tuple[VFSNode, str]:
        """Return (parent_node, base_name) for a path, raising on error."""
        path = self.resolve(path)
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        name        = path.split("/")[-1]
        parent      = self._get_node(parent_path)
        if parent is None:
            raise FileNotFoundError(f"No such directory: {parent_path}")
        if not parent.is_dir:
            raise NotADirectoryError(f"Not a directory: {parent_path}")
        return parent, name

    # ── public API ────────────────────────────────────────────────────────────

    def exists(self, path: str) -> bool:
        return self._get_node(path) is not None

    def isdir(self, path: str) -> bool:
        n = self._get_node(path)
        return n is not None and n.is_dir

    def isfile(self, path: str) -> bool:
        n = self._get_node(path)
        return n is not None and not n.is_dir

    def listdir(self, path: str = "/") -> List[str]:
        n = self._get_node(path)
        if n is None:
            raise FileNotFoundError(path)
        if not n.is_dir:
            raise NotADirectoryError(path)
        n.accessed = time.time()
        return sorted(n.children.keys())

    def read(self, path: str) -> str:
        n = self._get_node(path)
        if n is None:
            raise FileNotFoundError(path)
        if n.is_dir:
            raise IsADirectoryError(path)
        n.accessed = time.time()
        return n._content

    def write(self, path: str, content: str, append: bool = False) -> None:
        path = self.resolve(path)
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        name        = path.split("/")[-1]
        if not name:
            raise ValueError("Cannot write to root")
        parent = self._get_node(parent_path)
        if parent is None:
            self.makedirs(parent_path)
            parent = self._get_node(parent_path)
        if not parent.is_dir:
            raise NotADirectoryError(parent_path)
        if name in parent.children:
            node = parent.children[name]
            if node.is_dir:
                raise IsADirectoryError(path)
            node._content = (node._content + content) if append else content
            node.modified = time.time()
        else:
            node = VFSNode(name, is_dir=False, content=content, parent=parent)
            parent.children[name] = node
        # mirror to real disk
        n = self._get_node(path)
        self._disk_write(path, n._content if n else content)

    def append(self, path: str, content: str) -> None:
        self.write(path, content, append=True)

    def mkdir(self, path: str) -> None:
        path = self.resolve(path)
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        name        = path.split("/")[-1]
        if not name:
            return
        parent = self._get_node(parent_path)
        if parent is None:
            raise FileNotFoundError(parent_path)
        if not parent.is_dir:
            raise NotADirectoryError(parent_path)
        if name not in parent.children:
            parent.children[name] = VFSNode(name, is_dir=True, parent=parent)
        # mirror to real disk
        self._disk_mkdir(path)

    def makedirs(self, path: str) -> None:
        path    = self.resolve(path)
        current = "/"
        for part in path.strip("/").split("/"):
            if not part:
                continue
            current = current.rstrip("/") + "/" + part
            if not self.exists(current):
                self.mkdir(current)

    def remove(self, path: str) -> None:
        rpath = self.resolve(path)
        parent, name = self._parent_and_name(path)
        if name not in parent.children:
            raise FileNotFoundError(path)
        del parent.children[name]
        # mirror to real disk
        self._disk_delete(rpath)

    def rmdir(self, path: str, recursive: bool = False) -> None:
        n = self._get_node(path)
        if n is None:
            raise FileNotFoundError(path)
        if not n.is_dir:
            raise NotADirectoryError(path)
        if n.children and not recursive:
            raise OSError(f"Directory not empty: {path}")
        self.remove(path)

    def rename(self, src: str, dst: str) -> None:
        src_r = self.resolve(src)
        dst_r = self.resolve(dst)
        src, dst = src_r, dst_r
        src_parent, src_name = self._parent_and_name(src)
        dst_parent, dst_name = self._parent_and_name(dst)
        if src_name not in src_parent.children:
            raise FileNotFoundError(src)
        node         = src_parent.children.pop(src_name)
        node.name    = dst_name
        node.parent  = dst_parent
        node.touch()
        dst_parent.children[dst_name] = node
        # mirror to real disk
        self._disk_rename(src_r, dst_r)

    def copy(self, src: str, dst: str) -> None:
        """Shallow copy: copies file content only (not directories recursively)."""
        content = self.read(src)
        self.write(dst, content)

    def copy_tree(self, src: str, dst: str) -> None:
        """Deep copy: copies directory trees recursively."""
        if self.isfile(src):
            self.copy(src, dst)
            return
        self.makedirs(dst)
        for name in self.listdir(src):
            self.copy_tree(
                src.rstrip("/") + "/" + name,
                dst.rstrip("/") + "/" + name,
            )

    def stat(self, path: str) -> Dict[str, Any]:
        n = self._get_node(path)
        if n is None:
            raise FileNotFoundError(path)
        return n.stat()

    def find(
        self,
        pattern: str,
        start: str = "/",
        file_type: Optional[str] = None,   # "f"=files, "d"=dirs, None=both
    ) -> List[str]:
        """Search for nodes whose name matches *pattern* (regex)."""
        results: List[str] = []

        def walk(node: VFSNode, cur: str) -> None:
            for name, child in node.children.items():
                full = cur.rstrip("/") + "/" + name
                if re.search(pattern, name, re.IGNORECASE):
                    if file_type is None:
                        results.append(full)
                    elif file_type == "f" and not child.is_dir:
                        results.append(full)
                    elif file_type == "d" and child.is_dir:
                        results.append(full)
                if child.is_dir:
                    walk(child, full)

        n = self._get_node(start)
        if n and n.is_dir:
            walk(n, start)
        return results

    def grep(
        self,
        pattern: str,
        start: str = "/",
        case_insensitive: bool = False,
    ) -> List[Tuple[str, int, str]]:
        """Search file contents for *pattern*. Returns (path, line_no, line)."""
        results: List[Tuple[str, int, str]] = []
        flags = re.IGNORECASE if case_insensitive else 0
        for fpath in self.get_all_files(start):
            try:
                for i, line in enumerate(self.read(fpath).split("\n"), 1):
                    if re.search(pattern, line, flags):
                        results.append((fpath, i, line))
            except Exception:
                pass
        return results

    def tree(
        self,
        path: str = "/",
        prefix: str = "",
        depth: int = 0,
        max_depth: int = 5,
    ) -> str:
        if depth > max_depth:
            return ""
        n = self._get_node(path)
        if not n or not n.is_dir:
            return ""
        lines: List[str] = []
        items = sorted(n.children.items())
        for i, (name, child) in enumerate(items):
            last      = i == len(items) - 1
            connector = "└── " if last else "├── "
            icon      = "📁 " if child.is_dir else "📄 "
            lines.append(prefix + connector + icon + name)
            if child.is_dir:
                extension = "    " if last else "│   "
                subtree   = self.tree(
                    child.full_path(), prefix + extension, depth + 1, max_depth
                )
                if subtree:
                    lines.append(subtree)
        return "\n".join(lines)

    def get_all_files(self, path: str = "/") -> List[str]:
        """Return a flat list of all file paths under *path*."""
        results: List[str] = []

        def walk(node: VFSNode, cur: str) -> None:
            for name, child in node.children.items():
                full = cur.rstrip("/") + "/" + name
                if child.is_dir:
                    walk(child, full)
                else:
                    results.append(full)

        n = self._get_node(path)
        if n and n.is_dir:
            walk(n, path)
        return results

    def get_all_dirs(self, path: str = "/") -> List[str]:
        """Return a flat list of all directory paths under *path*."""
        results: List[str] = []

        def walk(node: VFSNode, cur: str) -> None:
            for name, child in node.children.items():
                full = cur.rstrip("/") + "/" + name
                if child.is_dir:
                    results.append(full)
                    walk(child, full)

        n = self._get_node(path)
        if n and n.is_dir:
            walk(n, path)
        return results

    def disk_usage(self, path: str = "/") -> Tuple[int, int]:
        """Return (used_bytes, total_bytes)."""
        n = self._get_node(path)
        used  = n.size if n else 0
        total = 512 * 1024 * 1024   # 512 MB virtual disk
        return used, total

    def get_ext_groups(self, path: str = "/") -> Dict[str, int]:
        """Return {extension: total_size} for all files under *path*."""
        groups: Dict[str, int] = defaultdict(int)
        for fpath in self.get_all_files(path):
            name = fpath.split("/")[-1]
            ext  = name.rsplit(".", 1)[-1].lower() if "." in name else "other"
            groups[ext] += self._get_node(fpath).size  # type: ignore
        return dict(groups)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 4 — USER MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class UserAccount:
    """Represents a single user account."""

    def __init__(
        self,
        username:  str,
        password:  str,           # raw password — hashed immediately
        fullname:  str = "",
        admin:     bool = False,
        avatar_color: str = "#388bfd",
        home:      str = "",
    ) -> None:
        self.username     = username
        self._password    = self._hash(password)
        self.fullname     = fullname or username.title()
        self.admin        = admin
        self.avatar_color = avatar_color
        self.home         = home or f"/home/{username}"
        self.created      = time.time()
        self.last_login: Optional[float] = None
        self.login_count  = 0
        self.preferences: Dict[str, Any] = {}

    @staticmethod
    def _hash(pw: str) -> str:
        return hashlib.sha256(pw.encode()).hexdigest()

    def verify(self, pw: str) -> bool:
        return self._hash(pw) == self._password

    def set_password(self, new_pw: str) -> None:
        self._password = self._hash(new_pw)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "username":     self.username,
            "fullname":     self.fullname,
            "admin":        self.admin,
            "avatar_color": self.avatar_color,
            "home":         self.home,
            "created":      self.created,
            "last_login":   self.last_login,
            "login_count":  self.login_count,
        }


class UserManager:
    """Manages all user accounts and the current session."""

    def __init__(self) -> None:
        self._accounts: Dict[str, UserAccount] = {}
        self.current: Optional[str] = None
        self.login_time: Optional[float] = None
        self.session_log: List[str] = []
        self._setup_default_accounts()

    def _setup_default_accounts(self) -> None:
        self.add_account(
            UserAccount("user",  "user",  "Default User",  admin=True,
                        avatar_color="#388bfd", home="/home/user")
        )
        self.add_account(
            UserAccount("guest", "guest", "Guest",         admin=False,
                        avatar_color="#bf91f9", home="/home/user")
        )
        self.add_account(
            UserAccount("root",  "root",  "System Root",   admin=True,
                        avatar_color="#f85149", home="/root")
        )

    def add_account(self, account: UserAccount) -> None:
        self._accounts[account.username] = account

    def get_account(self, username: str) -> Optional[UserAccount]:
        return self._accounts.get(username)

    def login(self, username: str, password: str) -> bool:
        acct = self._accounts.get(username)
        if acct is None or not acct.verify(password):
            return False
        self.current    = username
        self.login_time = time.time()
        acct.last_login = self.login_time
        acct.login_count += 1
        self.session_log.append(
            f"LOGIN  {username}  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
        )
        return True

    def logout(self) -> None:
        if self.current:
            self.session_log.append(
                f"LOGOUT {self.current}  {datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
            )
        self.current    = None
        self.login_time = None

    def change_password(self, username: str, old_pw: str, new_pw: str) -> bool:
        acct = self._accounts.get(username)
        if acct is None or not acct.verify(old_pw):
            return False
        acct.set_password(new_pw)
        return True

    def delete_account(self, username: str) -> bool:
        if username in ("user", "root"):
            return False   # protect built-in accounts
        return bool(self._accounts.pop(username, None))

    def all_accounts(self) -> List[UserAccount]:
        return list(self._accounts.values())

    @property
    def info(self) -> Optional[UserAccount]:
        return self._accounts.get(self.current) if self.current else None

    @property
    def uptime(self) -> str:
        if not self.login_time:
            return "0:00:00"
        s = int(time.time() - self.login_time)
        return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"

    @property
    def uptime_secs(self) -> int:
        return int(time.time() - self.login_time) if self.login_time else 0


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 5 — PROCESS MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class Process:
    """Represents a running OS process with simulated resource usage."""

    _next_pid: int = 1000

    def __init__(self, name: str, owner: str = "user", kind: str = "app") -> None:
        Process._next_pid += 1
        self.pid      = Process._next_pid
        self.name     = name
        self.owner    = owner
        self.kind     = kind           # "system" | "app" | "daemon"
        self.started  = time.time()
        self.status   = "running"      # running | sleeping | stopped | zombie
        self.priority = 0              # -20 (high) to 19 (low)

        # Simulated resource usage
        self.cpu: float  = random.uniform(0.1, 5.0)
        self.mem: int    = random.randint(8, 256)   # MB
        self.threads: int = random.randint(1, 8)
        self.fd_count: int = random.randint(2, 20)  # open file descriptors

        # History for graphs (60 samples each)
        self._cpu_hist: deque = deque([self.cpu] * 60, maxlen=60)
        self._mem_hist: deque = deque([self.mem] * 60, maxlen=60)

    def tick(self) -> None:
        """Simulate realistic CPU/RAM fluctuation."""
        if self.status != "running":
            self.cpu = 0.0
            return
        # CPU: mean-reverting random walk
        delta       = random.gauss(0, 0.8)
        target_cpu  = max(0.0, min(100.0, self.cpu + delta))
        self.cpu    = round(target_cpu, 2)
        # RAM: slight random drift
        self.mem    = max(4, self.mem + random.randint(-3, 3))
        self._cpu_hist.append(self.cpu)
        self._mem_hist.append(self.mem)

    @property
    def uptime(self) -> str:
        s = int(time.time() - self.started)
        return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"

    @property
    def uptime_secs(self) -> int:
        return int(time.time() - self.started)

    @property
    def cpu_history(self) -> List[float]:
        return list(self._cpu_hist)

    @property
    def mem_history(self) -> List[int]:
        return list(self._mem_hist)

    def __repr__(self) -> str:
        return f"<Process pid={self.pid} name={self.name!r} cpu={self.cpu:.1f}%>"


class ProcessManager:
    """Manages all simulated OS processes."""

    def __init__(self) -> None:
        self.procs: Dict[int, Process] = {}
        self._lock = threading.Lock()
        self._spawn_system_procs()
        self._tick_thread = threading.Thread(
            target=self._tick_loop, daemon=True, name="procmgr-tick"
        )
        self._tick_thread.start()

    def _spawn_system_procs(self) -> None:
        system_names = [
            ("pyos-kernel",   "root", "system"),
            ("pyos-wm",       "root", "system"),
            ("pyos-vfs",      "root", "system"),
            ("pyos-net",      "root", "daemon"),
            ("pyos-audio",    "root", "daemon"),
            ("pyos-dbus",     "root", "daemon"),
            ("pyos-power",    "root", "daemon"),
            ("pyos-logger",   "root", "daemon"),
            ("pyos-cron",     "root", "daemon"),
        ]
        for name, owner, kind in system_names:
            p = Process(name, owner, kind)
            p.cpu = random.uniform(0.0, 1.5)
            p.mem = random.randint(4, 40)
            with self._lock:
                self.procs[p.pid] = p

    def spawn(self, name: str, owner: str = "user", kind: str = "app") -> Process:
        p = Process(name, owner, kind)
        with self._lock:
            self.procs[p.pid] = p
        return p

    def kill(self, pid: int) -> bool:
        with self._lock:
            if pid in self.procs:
                del self.procs[pid]
                return True
        return False

    def kill_by_name(self, name: str) -> int:
        """Kill all processes matching *name*. Returns count killed."""
        pids = [p.pid for p in self.list_all() if p.name == name]
        for pid in pids:
            self.kill(pid)
        return len(pids)

    def _tick_loop(self) -> None:
        while True:
            time.sleep(1.5)
            with self._lock:
                for p in list(self.procs.values()):
                    p.tick()

    def list_all(self) -> List[Process]:
        with self._lock:
            return sorted(self.procs.values(), key=lambda p: p.pid)

    def get(self, pid: int) -> Optional[Process]:
        return self.procs.get(pid)

    @property
    def total_cpu(self) -> float:
        with self._lock:
            return min(100.0, sum(p.cpu for p in self.procs.values()))

    @property
    def total_mem(self) -> int:
        with self._lock:
            return sum(p.mem for p in self.procs.values())

    @property
    def process_count(self) -> int:
        with self._lock:
            return len(self.procs)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 6 — NOTIFICATION SYSTEM
# ─────────────────────────────────────────────────────────────────────────────

class Notification:
    """A single notification message."""

    def __init__(
        self,
        title:  str,
        body:   str,
        level:  str = "info",   # info | success | warning | error
        icon:   str = "ℹ️",
        source: str = "system",
        action: Optional[Callable] = None,
    ) -> None:
        self.id      = uuid.uuid4().hex
        self.title   = title
        self.body    = body
        self.level   = level
        self.icon    = icon
        self.source  = source
        self.action  = action
        self.time    = time.time()
        self.read    = False
        self.pinned  = False

    @property
    def time_str(self) -> str:
        return datetime.datetime.fromtimestamp(self.time).strftime("%H:%M:%S")

    @property
    def color(self) -> str:
        return {
            "info":    T["info"],
            "success": T["success"],
            "warning": T["warning"],
            "error":   T["danger"],
        }.get(self.level, T["info"])


class NotificationManager:
    """Manages and dispatches desktop notifications."""

    MAX_HISTORY = 200

    def __init__(self) -> None:
        self.history: List[Notification] = []
        self._subscribers: List[Callable[[Notification], None]] = []

    def subscribe(self, cb: Callable[[Notification], None]) -> None:
        self._subscribers.append(cb)

    def unsubscribe(self, cb: Callable[[Notification], None]) -> None:
        if cb in self._subscribers:
            self._subscribers.remove(cb)

    def send(
        self,
        title:  str,
        body:   str,
        level:  str = "info",
        icon:   str = "ℹ️",
        source: str = "system",
        action: Optional[Callable] = None,
    ) -> Notification:
        n = Notification(title, body, level, icon, source, action)
        self.history.append(n)
        if len(self.history) > self.MAX_HISTORY:
            self.history.pop(0)
        for cb in self._subscribers:
            try:
                cb(n)
            except Exception:
                pass
        return n

    def mark_all_read(self) -> None:
        for n in self.history:
            n.read = True

    def mark_read(self, nid: str) -> None:
        for n in self.history:
            if n.id == nid:
                n.read = True

    def clear(self) -> None:
        self.history.clear()

    @property
    def unread_count(self) -> int:
        return sum(1 for n in self.history if not n.read)

    def recent(self, n: int = 20) -> List[Notification]:
        return list(reversed(self.history[-n:]))


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 7 — CLIPBOARD
# ─────────────────────────────────────────────────────────────────────────────

class Clipboard:
    """System clipboard for text and file operations."""

    def __init__(self) -> None:
        self._text: str        = ""
        self._files: List[str] = []
        self._mode: str        = "copy"    # "copy" | "cut"
        self._history: List[str] = []     # text history

    def copy_text(self, text: str) -> None:
        self._text  = text
        self._files = []
        self._mode  = "copy"
        if text:
            self._history.append(text)
            if len(self._history) > 50:
                self._history.pop(0)

    def copy_files(self, paths: List[str], cut: bool = False) -> None:
        self._files = list(paths)
        self._text  = ""
        self._mode  = "cut" if cut else "copy"

    def paste_text(self) -> str:
        return self._text

    def paste_files(self) -> Tuple[List[str], str]:
        return self._files, self._mode

    def clear(self) -> None:
        self._text = ""; self._files = []; self._mode = "copy"

    @property
    def has_text(self) -> bool:
        return bool(self._text)

    @property
    def has_files(self) -> bool:
        return bool(self._files)

    @property
    def text_history(self) -> List[str]:
        return list(reversed(self._history))


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 8 — SETTINGS / PREFERENCES
# ─────────────────────────────────────────────────────────────────────────────

class Settings:
    """
    Persistent (in-memory) key-value settings store.
    Provides typed getters and a reset mechanism.
    """

    DEFAULTS: Dict[str, Any] = {
        # Appearance
        "theme":              "Dark Blue",
        "wallpaper":          "gradient_blue",
        "icon_size":          52,
        "animations":         True,
        "transparency":       False,

        # Display
        "font_size":          10,
        "time_format":        "%H:%M:%S",
        "date_format":        "%Y-%m-%d",
        "show_seconds":       True,

        # File Manager
        "show_hidden_files":  False,
        "confirm_delete":     True,
        "single_click_open":  False,
        "show_file_preview":  True,
        "sort_folders_first": True,

        # Text Editor
        "editor_font_size":   11,
        "editor_tab_width":   4,
        "editor_line_numbers":True,
        "editor_word_wrap":   False,
        "editor_auto_indent": True,
        "editor_show_ruler":  True,
        "editor_ruler_col":   80,

        # Terminal
        "terminal_font_size": 10,
        "terminal_scrollback":5000,
        "terminal_bell":      False,

        # System
        "volume":             70,
        "brightness":         100,
        "autosave_interval":  60,
        "username_display":   "user",
        "language":           "en",

        # Privacy
        "remember_history":   True,
        "crash_reporting":    False,
    }

    def __init__(self) -> None:
        self._data: Dict[str, Any] = dict(self.DEFAULTS)
        self._listeners: List[Callable[[str, Any], None]] = []

    def subscribe(self, cb: Callable[[str, Any], None]) -> None:
        self._listeners.append(cb)

    def get(self, key: str, default: Any = None) -> Any:
        if key in self._data:
            return self._data[key]
        if default is not None:
            return default
        return self.DEFAULTS.get(key)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        for cb in self._listeners:
            try:
                cb(key, value)
            except Exception:
                pass

    def reset(self, key: Optional[str] = None) -> None:
        if key:
            if key in self.DEFAULTS:
                self._data[key] = self.DEFAULTS[key]
        else:
            self._data = dict(self.DEFAULTS)

    def all(self) -> Dict[str, Any]:
        return dict(self._data)

    def export_json(self) -> str:
        return json.dumps(self._data, indent=2)

    def import_json(self, s: str) -> None:
        try:
            data = json.loads(s)
            for k, v in data.items():
                self._data[k] = v
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 9 — HELPER WIDGETS & UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

# ── colour helpers ────────────────────────────────────────────────────────────

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def blend_colors(c1: str, c2: str, t: float) -> str:
    """Linear interpolation between two hex colours (t ∈ [0, 1])."""
    r1, g1, b1 = hex_to_rgb(c1)
    r2, g2, b2 = hex_to_rgb(c2)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return rgb_to_hex(r, g, b)


def darken(color: str, amount: float = 0.15) -> str:
    r, g, b = hex_to_rgb(color)
    r = max(0, int(r * (1 - amount)))
    g = max(0, int(g * (1 - amount)))
    b = max(0, int(b * (1 - amount)))
    return rgb_to_hex(r, g, b)


def lighten(color: str, amount: float = 0.15) -> str:
    r, g, b = hex_to_rgb(color)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return rgb_to_hex(r, g, b)


# ── size/time formatters ──────────────────────────────────────────────────────

def fmt_size(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def fmt_time(ts: float) -> str:
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def fmt_duration(secs: int) -> str:
    h, rem = divmod(secs, 3600)
    m, s   = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


# ── widget factories ──────────────────────────────────────────────────────────

def mkbtn(
    parent: tk.Widget,
    text:   str,
    cmd:    Optional[Callable] = None,
    kind:   str = "normal",
    icon:   str = "",
    **kw,
) -> tk.Button:
    """Create a styled push-button."""
    palettes = {
        "normal":  (T["button_bg"],  T["text"],         T["button_hover"]),
        "accent":  (T["accent"],     T["text_inverse"], darken(T["accent"])),
        "danger":  (T["danger"],     "#ffffff",         darken(T["danger"])),
        "success": (T["success"],    "#ffffff",         darken(T["success"])),
        "warning": (T["warning"],    "#ffffff",         darken(T["warning"])),
        "ghost":   (T["panel_bg"],   T["text"],         T["button_hover"]),
        "link":    (T["win_bg"],     T["link"],         T["button_hover"]),
    }
    bg, fg, abg = palettes.get(kind, palettes["normal"])
    label = (icon + "  " + text).strip() if icon else text
    return tk.Button(
        parent, text=label, command=cmd,
        bg=bg, fg=fg, relief="flat", bd=0,
        font=(FONT_UI, 10), padx=12, pady=5,
        cursor="hand2",
        activebackground=abg, activeforeground=fg,
        **kw,
    )


def mklbl(
    parent: tk.Widget,
    text:   str,
    size:   int  = 10,
    bold:   bool = False,
    muted:  bool = False,
    mono:   bool = False,
    **kw,
) -> tk.Label:
    """Create a styled label."""
    face   = FONT_MONO if mono else FONT_UI
    weight = "bold" if bold else "normal"
    fg     = T["text_muted"] if muted else T["text"]
    bg     = kw.pop("bg", T["win_bg"])
    return tk.Label(
        parent, text=text, bg=bg, fg=fg,
        font=(face, size, weight), **kw
    )


def mkentry(
    parent:       tk.Widget,
    textvariable: Optional[tk.Variable] = None,
    width:        int = 20,
    password:     bool = False,
    **kw,
) -> tk.Entry:
    """Create a styled text entry widget."""
    show = "*" if password else ""
    return tk.Entry(
        parent,
        textvariable=textvariable,
        bg=T["input_bg"], fg=T["text"],
        insertbackground=T["text"],
        selectbackground=T["selection"],
        relief="flat", bd=4,
        font=(FONT_UI, 10),
        width=width,
        highlightthickness=1,
        highlightcolor=T["input_focus"],
        highlightbackground=T["input_border"],
        show=show,
        **kw,
    )


def mksep(parent: tk.Widget, orient: str = "horizontal") -> tk.Frame:
    """Create a thin separator line."""
    if orient == "horizontal":
        return tk.Frame(parent, bg=T["separator"], height=1)
    return tk.Frame(parent, bg=T["separator"], width=1)


def mktag(parent: tk.Widget, text: str) -> tk.Label:
    """Create a small coloured tag label."""
    return tk.Label(
        parent, text=f" {text} ",
        bg=T["tag_bg"], fg=T["tag_fg"],
        font=(FONT_UI, 8), relief="flat",
    )


class Tooltip:
    """Simple hover tooltip for any widget."""

    def __init__(self, widget: tk.Widget, text: str, delay: int = 600) -> None:
        self._widget = widget
        self._text   = text
        self._delay  = delay
        self._tip: Optional[tk.Toplevel] = None
        self._job: Optional[str]         = None
        widget.bind("<Enter>",  self._schedule)
        widget.bind("<Leave>",  self._cancel)
        widget.bind("<Button>", self._cancel)

    def _schedule(self, _: tk.Event) -> None:
        self._job = self._widget.after(self._delay, self._show)

    def _cancel(self, _: tk.Event) -> None:
        if self._job:
            self._widget.after_cancel(self._job)
            self._job = None
        if self._tip:
            self._tip.destroy()
            self._tip = None

    def _show(self) -> None:
        x = self._widget.winfo_rootx() + 10
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._tip = tk.Toplevel(self._widget)
        self._tip.wm_overrideredirect(True)
        self._tip.wm_geometry(f"+{x}+{y}")
        self._tip.wm_attributes("-topmost", True)
        tk.Label(
            self._tip, text=self._text,
            bg=T["tooltip_bg"], fg=T["tooltip_fg"],
            font=(FONT_UI, 9), padx=8, pady=4,
            relief="flat",
        ).pack()


class ScrollableFrame(tk.Frame):
    """A frame with a vertical scrollbar that works on all platforms."""

    def __init__(self, parent: tk.Widget, **kw) -> None:
        super().__init__(parent, bg=kw.pop("bg", T["win_bg"]), **kw)
        self._canvas = tk.Canvas(
            self, bg=self.cget("bg"), highlightthickness=0
        )
        self._vsb = tk.Scrollbar(
            self, orient="vertical", command=self._canvas.yview,
            bg=T["scrollbar"], troughcolor=self.cget("bg"),
            activebackground=T["scrollbar_thumb"],
        )
        self._canvas.config(yscrollcommand=self._vsb.set)
        self._vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self._canvas, bg=self.cget("bg"))
        self._window = self._canvas.create_window(
            (0, 0), window=self.inner, anchor="nw"
        )
        self.inner.bind("<Configure>", self._on_configure)
        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_configure(self, _: tk.Event) -> None:
        self._canvas.config(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_resize(self, e: tk.Event) -> None:
        self._canvas.itemconfig(self._window, width=e.width)

    def _on_mousewheel(self, e: tk.Event) -> None:
        self._canvas.yview_scroll(-1 * (e.delta // 120), "units")

    def scroll_to_top(self) -> None:
        self._canvas.yview_moveto(0)

    def scroll_to_bottom(self) -> None:
        self._canvas.yview_moveto(1)


class ScrollText(tk.Frame):
    """Text widget with vertical (and optional horizontal) scrollbars."""

    def __init__(self, parent: tk.Widget, **kw) -> None:
        wrap  = kw.pop("wrap", "word")
        hscroll = kw.pop("hscroll", False)
        super().__init__(parent, bg=T["win_bg"])

        self.text = tk.Text(
            self,
            wrap=wrap,
            bg=T["input_bg"],
            fg=T["text"],
            insertbackground=T["text"],
            selectbackground=T["selection"],
            selectforeground=T["text"],
            relief="flat", bd=4,
            font=(FONT_MONO, 11),
            **kw,
        )
        vsb = tk.Scrollbar(
            self, orient="vertical", command=self.text.yview,
            bg=T["scrollbar"],
        )
        self.text.config(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        if hscroll:
            hsb = tk.Scrollbar(
                self, orient="horizontal", command=self.text.xview,
                bg=T["scrollbar"],
            )
            self.text.config(xscrollcommand=hsb.set)
            hsb.pack(side="bottom", fill="x")

        self.text.pack(fill="both", expand=True)

    # ── proxy methods ────────────────────────────────────────────────────────

    def get(self, *a):            return self.text.get(*a)
    def insert(self, *a):         self.text.insert(*a)
    def delete(self, *a):         self.text.delete(*a)
    def config(self, **kw):       self.text.config(**kw)
    def see(self, *a):            self.text.see(*a)
    def index(self, *a):          return self.text.index(*a)
    def search(self, *a, **kw):   return self.text.search(*a, **kw)
    def mark_set(self, *a):       self.text.mark_set(*a)
    def tag_configure(self, *a, **kw): self.text.tag_configure(*a, **kw)
    def tag_add(self, *a):        self.text.tag_add(*a)
    def tag_remove(self, *a):     self.text.tag_remove(*a)
    def tag_ranges(self, *a):     return self.text.tag_ranges(*a)
    def yview(self, *a):          self.text.yview(*a)


class ProgressBar(tk.Canvas):
    """
    A custom animated progress bar widget.
    Usage:
        pb = ProgressBar(parent, width=200, height=12)
        pb.set(0.75)   # 75%
    """

    def __init__(self, parent: tk.Widget, **kw) -> None:
        self._color = kw.pop("color", T["progress_fg"])
        self._value = 0.0
        h = kw.pop("height", 8)
        super().__init__(
            parent, bg=T["progress_bg"],
            highlightthickness=0, height=h, **kw
        )
        self.bind("<Configure>", lambda _: self._draw())

    def set(self, value: float) -> None:
        self._value = max(0.0, min(1.0, value))
        self._draw()

    def _draw(self) -> None:
        self.delete("all")
        W, H = self.winfo_width() or 200, self.winfo_height() or 8
        self.create_rectangle(0, 0, W, H, fill=T["progress_bg"], outline="")
        filled = int(W * self._value)
        if filled > 0:
            self.create_rectangle(
                0, 0, filled, H, fill=self._color, outline=""
            )


class BadgeLabel(tk.Label):
    """A label with a small numeric badge overlay."""

    def __init__(self, parent: tk.Widget, **kw) -> None:
        super().__init__(parent, **kw)
        self._badge: Optional[tk.Label] = None

    def set_badge(self, count: int) -> None:
        if count <= 0:
            if self._badge:
                self._badge.destroy()
                self._badge = None
            return
        text = str(count) if count < 100 else "99+"
        if self._badge is None:
            self._badge = tk.Label(
                self.master, text=text,
                bg=T["badge_bg"], fg=T["badge_fg"],
                font=(FONT_UI, 7, "bold"),
                padx=3, pady=1, relief="flat",
            )
        else:
            self._badge.config(text=text)
        # Position top-right of self
        x = self.winfo_x() + self.winfo_width() - 8
        y = self.winfo_y() - 4
        self._badge.place(x=x, y=y)


# ── file-type helpers ─────────────────────────────────────────────────────────

FILE_ICONS: Dict[str, str] = {
    "py": "🐍", "js": "📜", "ts": "📜", "html": "🌐", "css": "🎨",
    "json": "📋", "xml": "📋", "yaml": "📋", "toml": "📋",
    "txt": "📄", "md": "📝", "rst": "📝",
    "png": "🖼️", "jpg": "🖼️", "jpeg": "🖼️", "gif": "🖼️", "bmp": "🖼️",
    "svg": "🖼️", "webp": "🖼️", "ico": "🖼️",
    "mp3": "🎵", "wav": "🎵", "ogg": "🎵", "flac": "🎵", "m4a": "🎵",
    "m3u": "🎵", "mp4": "🎬", "avi": "🎬", "mkv": "🎬", "mov": "🎬",
    "pdf": "📕", "doc": "📘", "docx": "📘", "odt": "📘",
    "xls": "📊", "xlsx": "📊", "csv": "📊", "ods": "📊",
    "ppt": "📊", "pptx": "📊",
    "zip": "📦", "tar": "📦", "gz": "📦", "bz2": "📦", "7z": "📦", "rar": "📦",
    "sh": "⚙️", "bash": "⚙️", "zsh": "⚙️", "fish": "⚙️",
    "c": "🔧", "cpp": "🔧", "h": "🔧", "hpp": "🔧",
    "java": "☕", "kt": "☕", "scala": "☕",
    "go": "🐹", "rs": "🦀", "rb": "💎", "php": "🐘", "swift": "🍎",
    "sql": "🗃️", "db": "🗃️", "sqlite": "🗃️",
    "log": "📃", "cfg": "⚙️", "ini": "⚙️", "conf": "⚙️", "env": "⚙️",
    "ps": "🎨", "eps": "🎨",
    "lock": "🔒",
}

FILE_TYPE_NAMES: Dict[str, str] = {
    "py": "Python Script", "js": "JavaScript", "ts": "TypeScript",
    "html": "HTML Document", "css": "Stylesheet", "json": "JSON Data",
    "txt": "Text File", "md": "Markdown", "pdf": "PDF Document",
    "png": "PNG Image", "jpg": "JPEG Image", "jpeg": "JPEG Image",
    "mp3": "MP3 Audio", "wav": "WAV Audio", "mp4": "MP4 Video",
    "csv": "CSV Spreadsheet", "xlsx": "Excel Spreadsheet",
    "zip": "ZIP Archive", "tar": "TAR Archive", "gz": "GZip Archive",
    "sh": "Shell Script", "c": "C Source", "cpp": "C++ Source",
    "java": "Java Source", "go": "Go Source", "rs": "Rust Source",
    "sql": "SQL Database", "log": "Log File", "cfg": "Config File",
    "ini": "INI Config", "m3u": "Playlist",
}


def get_file_icon(name: str, is_dir: bool = False) -> str:
    if is_dir:
        return "📁"
    if "." in name:
        ext = name.rsplit(".", 1)[-1].lower()
        return FILE_ICONS.get(ext, "📄")
    return "📄"


def get_file_type(name: str, is_dir: bool = False) -> str:
    if is_dir:
        return "Folder"
    if "." in name:
        ext = name.rsplit(".", 1)[-1].lower()
        return FILE_TYPE_NAMES.get(ext, f"{ext.upper()} File")
    return "File"


def is_text_file(name: str) -> bool:
    """Return True if the file is likely a text/code file."""
    TEXT_EXTS = {
        "txt", "md", "rst", "py", "js", "ts", "html", "css", "json", "xml",
        "yaml", "toml", "sh", "bash", "c", "cpp", "h", "hpp", "java", "go",
        "rs", "rb", "php", "swift", "sql", "log", "cfg", "ini", "conf",
        "env", "csv", "m3u", "ps", "gitignore", "dockerfile", "makefile",
    }
    if "." in name:
        return name.rsplit(".", 1)[-1].lower() in TEXT_EXTS
    return name.lower() in ("makefile", "dockerfile", "readme", "license")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 10 — BASE WINDOW CLASS
# ─────────────────────────────────────────────────────────────────────────────

class BaseWin:
    """
    A floating, draggable, resizable window rendered on the WM desktop canvas.

    All application windows inherit from this class.  The window is composed
    of three tk.Frame elements placed in the WM's desktop frame:

        ┌─────────────────────────────────────┐  ← _outer  (border colour)
        │  [icon] Title            [─][□][✕]  │  ← _titlebar
        ├─────────────────────────────────────┤
        │                                     │
        │        _body  (app content)         │  ← _body
        │                                     │
        └─────────────────────────────────────┘
    """

    _z_counter: int = 0

    def __init__(
        self,
        wm:        "WM",
        title:     str  = "Window",
        x:         int  = 120,
        y:         int  = 60,
        w:         int  = 720,
        h:         int  = 500,
        icon:      str  = "🖥️",
        resizable: bool = True,
        min_w:     int  = WIN_MIN_W,
        min_h:     int  = WIN_MIN_H,
    ) -> None:
        self.wm        = wm
        self.title     = title
        self.icon      = icon
        self.x = x;  self.y = y
        self.w = w;  self.h = h
        self.min_w     = min_w
        self.min_h     = min_h
        self.resizable = resizable

        # Window state
        self.focused   = False
        self.minimized = False
        self.maximized = False
        self._pre_max: Tuple[int, int, int, int] = (x, y, w, h)
        self.visible   = True
        self.pid: Optional[int] = None

        # Z-order
        BaseWin._z_counter += 1
        self.z_order = BaseWin._z_counter

        # Build widgets
        self._outer    = tk.Frame(
            wm.dframe, bd=0, highlightthickness=0,
            bg=T["win_border"],
        )
        self._titlebar = tk.Frame(
            self._outer, bg=T["win_title_active"],
            height=TITLEBAR_H, cursor="fleur",
        )
        self._titlebar.pack(fill="x", side="top")
        self._titlebar.pack_propagate(False)

        self._body = tk.Frame(self._outer, bg=T["win_bg"])
        self._body.pack(fill="both", expand=True)

        self._build_titlebar()
        self._place()
        self._bind_drag()
        if resizable:
            self._bind_resize()

        # Let the subclass populate _body
        self.build_ui(self._body)

    # ── titlebar construction ─────────────────────────────────────────────────

    def _build_titlebar(self) -> None:
        tb = self._titlebar

        # Left side: icon + title
        lf = tk.Frame(tb, bg=T["win_title_active"])
        lf.pack(side="left", fill="y", padx=6)

        tk.Label(
            lf, text=self.icon,
            bg=T["win_title_active"], fg=T["win_title_fg"],
            font=(FONT_EMOJI, 13),
        ).pack(side="left", pady=4)

        self._title_lbl = tk.Label(
            lf, text=self.title,
            bg=T["win_title_active"], fg=T["win_title_fg"],
            font=(FONT_UI, 10, "bold"), cursor="fleur",
        )
        self._title_lbl.pack(side="left", padx=6)

        # Drag bindings on title label too
        self._title_lbl.bind("<ButtonPress-1>",  self._drag_start)
        self._title_lbl.bind("<B1-Motion>",       self._drag_motion)
        self._title_lbl.bind("<ButtonRelease-1>", self._drag_end)
        self._title_lbl.bind("<Double-Button-1>", self._toggle_maximize)

        # Right side: window controls
        rf = tk.Frame(tb, bg=T["win_title_active"])
        rf.pack(side="right", fill="y", padx=4)

        btn_specs = [
            ("─", self.minimize,    T["button_bg"],   T["text"],         T["button_hover"]),
            ("□", self.toggle_max,  T["button_bg"],   T["text"],         T["button_hover"]),
            ("✕", self.close,       T["danger"],      "#ffffff",         darken(T["danger"])),
        ]
        for text, cmd, bg, fg, abg in btn_specs:
            b = tk.Button(
                rf, text=text, command=cmd,
                bg=bg, fg=fg, relief="flat", bd=0,
                font=(FONT_UI, 10), padx=10, pady=4,
                cursor="hand2",
                activebackground=abg, activeforeground=fg,
            )
            b.pack(side="left", padx=1)

    # ── placement ─────────────────────────────────────────────────────────────

    def _place(self) -> None:
        self._outer.place(x=self.x, y=self.y, width=self.w, height=self.h)

    # ── drag ──────────────────────────────────────────────────────────────────

    def _bind_drag(self) -> None:
        tb = self._titlebar
        tb.bind("<ButtonPress-1>",  self._drag_start)
        tb.bind("<B1-Motion>",       self._drag_motion)
        tb.bind("<ButtonRelease-1>", self._drag_end)
        tb.bind("<Double-Button-1>", self._toggle_maximize)
        self._drag_ox = 0
        self._drag_oy = 0

    def _drag_start(self, e: tk.Event) -> None:
        self.focus()
        self._drag_ox = e.x_root - self.x
        self._drag_oy = e.y_root - self.y

    def _drag_motion(self, e: tk.Event) -> None:
        if self.maximized:
            return
        new_x = max(0, e.x_root - self._drag_ox)
        new_y = max(0, min(
            e.y_root - self._drag_oy,
            SCREEN_H - TASKBAR_H - TITLEBAR_H,
        ))
        self.x = new_x
        self.y = new_y
        self._place()

    def _drag_end(self, _: tk.Event) -> None:
        pass

    # ── resize ─────────────────────────────────────────────────────────────────

    def _bind_resize(self) -> None:
        # Bottom-right resize handle
        handle = tk.Frame(
            self._outer, bg=T["text_muted"],
            width=14, height=14, cursor="size_nw_se",
        )
        handle.place(relx=1.0, rely=1.0, anchor="se")
        handle.bind("<ButtonPress-1>",  self._resize_start)
        handle.bind("<B1-Motion>",       self._resize_motion)
        self._resize_ox = 0
        self._resize_oy = 0

    def _resize_start(self, e: tk.Event) -> None:
        self._resize_ox = e.x_root - self.w
        self._resize_oy = e.y_root - self.h

    def _resize_motion(self, e: tk.Event) -> None:
        if self.maximized:
            return
        new_w = max(self.min_w, e.x_root - self._resize_ox)
        new_h = max(self.min_h, e.y_root - self._resize_oy)
        self.w = new_w
        self.h = new_h
        self._place()
        self.on_resize(new_w, new_h)

    # ── window state ──────────────────────────────────────────────────────────

    def focus(self) -> None:
        self.focused = True
        BaseWin._z_counter += 1
        self.z_order = BaseWin._z_counter
        self._outer.lift()
        self._outer.config(bg=T["win_border_active"])
        self._titlebar.config(bg=T["win_title_active"])
        self._title_lbl.config(
            bg=T["win_title_active"], fg=T["win_title_fg"]
        )
        self.wm.set_focus(self)

    def unfocus(self) -> None:
        self.focused = False
        self._outer.config(bg=T["win_border"])
        self._titlebar.config(bg=T["win_title_inactive"])
        self._title_lbl.config(
            bg=T["win_title_inactive"], fg=T["win_title_fg_in"]
        )

    def minimize(self) -> None:
        self.minimized = True
        self._outer.place_forget()
        self.wm.tb.update_btns()

    def restore(self) -> None:
        if self.minimized:
            self.minimized = False
            self._place()
            self.focus()
            self.wm.tb.update_btns()

    def toggle_max(self) -> None:
        self._toggle_maximize(None)

    def _toggle_maximize(self, _: Optional[tk.Event]) -> None:
        if self.maximized:
            self.x, self.y, self.w, self.h = self._pre_max
            self.maximized = False
        else:
            self._pre_max = (self.x, self.y, self.w, self.h)
            self.x = 0;  self.y = 0
            self.w = SCREEN_W
            self.h = SCREEN_H - TASKBAR_H
            self.maximized = True
        self._place()
        self.on_resize(self.w, self.h)

    def close(self) -> None:
        self.wm.close_win(self)

    def set_title(self, t: str) -> None:
        self.title = t
        self._title_lbl.config(text=t)
        self.wm.tb.update_btns()

    def set_icon(self, icon: str) -> None:
        self.icon = icon
        # Refresh first child of titlebar left frame
        # (we don't keep a ref to the icon label — safe to iterate)
        for w in self._titlebar.winfo_children():
            for child in w.winfo_children():
                if child.cget("font") and "Emoji" in str(child.cget("font")):
                    child.config(text=icon)
                    return

    # ── hooks ────────────────────────────────────────────────────────────────

    def build_ui(self, parent: tk.Frame) -> None:
        """Override in subclasses to build the window's content."""
        pass

    def on_resize(self, w: int, h: int) -> None:
        """Called when the window is resized. Override as needed."""
        pass

    def on_close(self) -> None:
        """Called just before the window is destroyed. Override as needed."""
        pass

    def on_focus(self) -> None:
        """Called when the window receives focus. Override as needed."""
        pass

    # ── utility ───────────────────────────────────────────────────────────────

    def flash(self, color: str = "", duration: int = 200) -> None:
        """Briefly flash the titlebar (e.g. to draw attention)."""
        original = self._titlebar.cget("bg")
        target   = color or T["warning"]
        self._titlebar.config(bg=target)
        self._outer.after(
            duration, lambda: self._titlebar.config(bg=original)
        )


# =============================================================================
#  END OF PART 1 (lines 1-2000)
#  Continues in Part 2: WM, Taskbar, StartMenu, all 20 Application classes
# =============================================================================

if __name__ == "__main__":
    print(f"PyOS v{PYOS_VERSION} — Part 1 loaded successfully.")
    print("This file contains the core OS infrastructure.")
    print("The full OS requires all parts to be combined.")
    print(f"Classes defined: VFS, UserManager, ProcessManager,")
    print(f"                 NotificationManager, Clipboard, Settings,")
    print(f"                 BaseWin, and all helper widgets.")
    #!/usr/bin/env python3
# =============================================================================
#  PyOS v5.0 — PART 2 (lines 2001-4000)
#  Sections: Window Manager, Taskbar, Start Menu, Panels,
#            File Manager App, Text Editor App
#  Requires: pyos_v5_part1.py to be concatenated before this
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 11 — WINDOW MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class WM:
    """
    The Window Manager owns:
      • The desktop frame and canvas (wallpaper + desktop icons)
      • The list of open windows
      • Focus management
      • App launcher shortcuts
      • Right-click desktop context menu
    """

    # Desktop icon layout
    _DESKTOP_ICONS = [
        ("🗂️",  "Files",        "open_fm"),
        ("📝",  "Editor",       "open_editor"),
        ("💻",  "Terminal",     "open_terminal"),
        ("🌐",  "Browser",      "open_browser"),
        ("🎵",  "Music",        "open_music"),
        ("🎨",  "Paint",        "open_paint"),
        ("🔢",  "Calculator",   "open_calc"),
        ("⏰",  "Clock",        "open_clock"),
        ("📊",  "Tasks",        "open_tasks"),
        ("📓",  "Notes",        "open_notes"),
        ("📧",  "Email",        "open_email"),
        ("🔐",  "Passwords",    "open_passwords"),
        ("📈",  "Spreadsheet",  "open_spreadsheet"),
        ("🖼️", "Images",       "open_images"),
        ("💾",  "Disk",         "open_disk"),
        ("⚡",  "Code Runner",  "open_coderunner"),
        ("📦",  "Archives",     "open_archives"),
        ("⚙️", "Settings",     "open_settings"),
        ("🛒",  "App Store",    "open_appstore"),
        ("📡",  "System Mon.",  "open_sysmon"),
    ]

    def __init__(
        self,
        root:      tk.Tk,
        vfs:       VFS,
        users:     UserManager,
        procs:     ProcessManager,
        notifs:    NotificationManager,
        settings:  Settings,
        clip:      Clipboard,
    ) -> None:
        self.root     = root
        self.vfs      = vfs
        self.users    = users
        self.procs    = procs
        self.notifs   = notifs
        self.settings = settings
        self.clip     = clip

        self.wins:    List[BaseWin]     = []
        self.focused: Optional[BaseWin] = None

        # Build desktop and taskbar
        self._build_desktop()
        self.tb = Taskbar(self)
        self._draw_wallpaper()
        self._draw_desktop_icons()
        self._build_ctx_menu()

        # Wire up toast notifications
        self.notifs.subscribe(self._show_toast)

    # ── toast notifications ───────────────────────────────────────────────────

    def _show_toast(self, n: "Notification") -> None:
        """Show a small toast popup in the bottom-right corner for ~4 seconds."""
        try:
            toast = tk.Toplevel(self.root)
            toast.overrideredirect(True)
            toast.attributes("-topmost", True)

            colour_map = {
                "info":    T.get("info",    "#4fc3f7"),
                "success": T.get("success", "#81c784"),
                "warning": T.get("warning", "#ffb74d"),
                "error":   T.get("danger",  "#e57373"),
            }
            accent = colour_map.get(n.level, T.get("info", "#4fc3f7"))
            bg     = T.get("win_bg",  "#1e2533")
            fg     = T.get("win_fg",  "#e0e6f0")

            W_TOAST, H_TOAST = 320, 72
            pad = 12
            x = self.root.winfo_x() + self.root.winfo_width()  - W_TOAST - 16
            y = self.root.winfo_y() + self.root.winfo_height() - H_TOAST - 48

            toast.geometry(f"{W_TOAST}x{H_TOAST}+{x}+{y}")

            tk.Frame(toast, bg=accent, width=4).pack(side="left", fill="y")

            body = tk.Frame(toast, bg=bg, padx=pad, pady=8)
            body.pack(side="left", fill="both", expand=True)

            hdr = tk.Frame(body, bg=bg)
            hdr.pack(fill="x")
            tk.Label(hdr, text=n.icon, bg=bg, fg=accent,
                     font=("Segoe UI Emoji", 13)).pack(side="left")
            tk.Label(hdr, text=f"  {n.title}", bg=bg, fg=fg,
                     font=("Segoe UI", 10, "bold")).pack(side="left")

            body_text = n.body if len(n.body) <= 48 else n.body[:45] + "…"
            tk.Label(body, text=body_text, bg=bg, fg=fg,
                     font=("Segoe UI", 9), anchor="w",
                     justify="left").pack(fill="x", pady=(2, 0))

            for w in (toast, body, hdr):
                w.bind("<Button-1>", lambda e, t=toast: t.destroy())

            self.root.after(4000, lambda: toast.destroy() if toast.winfo_exists() else None)

        except Exception:
            pass

    # ── desktop canvas ────────────────────────────────────────────────────────

    def _build_desktop(self) -> None:
        self.dframe = tk.Frame(
            self.root, bg=T["desktop_bg"],
        )
        self.dframe.place(
            x=0, y=0,
            width=SCREEN_W, height=SCREEN_H - TASKBAR_H,
        )
        self.dc = tk.Canvas(
            self.dframe, bg=T["desktop_bg"],
            highlightthickness=0,
        )
        self.dc.place(
            x=0, y=0,
            width=SCREEN_W, height=SCREEN_H - TASKBAR_H,
        )
        self.dc.bind("<Button-1>",    self._desktop_click)
        self.dc.bind("<Button-3>",    self._desktop_rclick)

    def _draw_wallpaper(self) -> None:
        c = self.dc
        c.delete("wallpaper")
        W = SCREEN_W
        H = SCREEN_H - TASKBAR_H
        wp = self.settings.get("wallpaper", "gradient_blue")

        if wp == "gradient_blue":
            steps = 60
            for i in range(steps):
                t = i / steps
                r = int(13  + t * (18  - 13))
                g = int(17  + t * (40  - 17))
                b = int(23  + t * (90  - 23))
                y0 = int(i     * H / steps)
                y1 = int((i+1) * H / steps)
                c.create_rectangle(
                    0, y0, W, y1,
                    fill=f"#{r:02x}{g:02x}{b:02x}",
                    outline="", tags="wallpaper",
                )

        elif wp == "gradient_purple":
            steps = 60
            for i in range(steps):
                t = i / steps
                r = int(20 + t * 70)
                g = int(5  + t * 10)
                b = int(40 + t * 80)
                y0 = int(i     * H / steps)
                y1 = int((i+1) * H / steps)
                c.create_rectangle(
                    0, y0, W, y1,
                    fill=f"#{min(255,r):02x}{min(255,g):02x}{min(255,b):02x}",
                    outline="", tags="wallpaper",
                )

        elif wp == "stars":
            c.create_rectangle(0, 0, W, H, fill="#000010", outline="", tags="wallpaper")
            rng = random.Random(42)
            for _ in range(400):
                x = rng.randint(0, W)
                y = rng.randint(0, H)
                sz = rng.choice([1, 1, 1, 2, 2, 3])
                br = rng.randint(160, 255)
                col = f"#{br:02x}{br:02x}{br:02x}"
                c.create_oval(x, y, x+sz, y+sz, fill=col, outline="", tags="wallpaper")
            # Add a subtle nebula glow
            for _ in range(6):
                nx = rng.randint(100, W-100)
                ny = rng.randint(50,  H-50)
                nr = rng.randint(80,  180)
                nc = rng.choice(["#200040", "#001030", "#002020", "#100020"])
                c.create_oval(
                    nx-nr, ny-nr//2, nx+nr, ny+nr//2,
                    fill=nc, outline="", tags="wallpaper",
                )

        elif wp == "grid":
            c.create_rectangle(0, 0, W, H, fill="#0a0e18", outline="", tags="wallpaper")
            for x in range(0, W, 40):
                c.create_line(x, 0, x, H, fill="#151c2e", tags="wallpaper")
            for y in range(0, H, 40):
                c.create_line(0, y, W, y, fill="#151c2e", tags="wallpaper")
            # Accent diagonal
            for i in range(-H, W, 80):
                c.create_line(i, 0, i+H, H, fill="#0d1525", tags="wallpaper")

        elif wp == "sunset":
            bands = [
                "#0d0015", "#1a0030", "#3a0060", "#7020a0",
                "#c04060", "#e06030", "#f08020", "#ffe060",
            ]
            bh = H // len(bands)
            for i, col in enumerate(bands):
                c.create_rectangle(
                    0, i*bh, W, (i+1)*bh,
                    fill=col, outline="", tags="wallpaper",
                )

        elif wp == "forest":
            c.create_rectangle(0, 0, W, H, fill="#0a1a0a", outline="", tags="wallpaper")
            # Sky
            c.create_rectangle(0, 0, W, H*2//3, fill="#0d1f0d", outline="", tags="wallpaper")
            rng2 = random.Random(99)
            for _ in range(30):
                tx = rng2.randint(0, W)
                th = rng2.randint(H//3, H)
                tw = rng2.randint(20, 60)
                shade = rng2.choice(["#0a1a08", "#0c1f0a", "#071505"])
                c.create_rectangle(tx, H-th, tx+tw, H, fill=shade, outline="", tags="wallpaper")

        elif wp == "ocean":
            steps = 60
            for i in range(steps):
                t = i / steps
                r = int(0   + t * 5)
                g = int(30  + t * 80)
                b = int(80  + t * 120)
                y0 = int(i     * H / steps)
                y1 = int((i+1) * H / steps)
                c.create_rectangle(
                    0, y0, W, y1,
                    fill=f"#{min(255,r):02x}{min(255,g):02x}{min(255,b):02x}",
                    outline="", tags="wallpaper",
                )

        elif wp == "solid":
            c.create_rectangle(0, 0, W, H, fill=T["desktop_bg"], outline="", tags="wallpaper")

        else:
            c.create_rectangle(0, 0, W, H, fill=T["desktop_bg"], outline="", tags="wallpaper")

        c.tag_lower("wallpaper")

    def _draw_desktop_icons(self) -> None:
        self.dc.delete("dicon")
        icons = self._DESKTOP_ICONS
        col_w = 100
        row_h = 88
        start_x = 16
        start_y = 16

        for i, (ico, label, method) in enumerate(icons):
            col = i % GRID_COLS
            row = i // GRID_COLS
            cx  = start_x + col * col_w + col_w // 2
            cy  = start_y + row * row_h + 24

            tag_ico = f"dico_{i}"
            tag_lbl = f"dlbl_{i}"

            # Icon
            self.dc.create_text(
                cx, cy,
                text=ico, font=(FONT_EMOJI, 20),
                tags=("dicon", tag_ico), anchor="center",
            )
            # Label
            self.dc.create_text(
                cx, cy + 30,
                text=label, font=(FONT_UI, 8),
                fill=T["text"], tags=("dicon", tag_lbl),
                anchor="center",
            )

            for tag in (tag_ico, tag_lbl):
                cmd = getattr(self, method, None)
                self.dc.tag_bind(
                    tag, "<Double-Button-1>",
                    lambda e, c=cmd: c() if c else None,
                )
                self.dc.tag_bind(
                    tag, "<Enter>",
                    lambda e: self.dc.config(cursor="hand2"),
                )
                self.dc.tag_bind(
                    tag, "<Leave>",
                    lambda e: self.dc.config(cursor=""),
                )

    def _build_ctx_menu(self) -> None:
        self._ctx = tk.Menu(
            self.root, tearoff=0,
            bg=T["menu_bg"], fg=T["text"],
            activebackground=T["accent"],
            activeforeground=T["text_inverse"],
            relief="flat", bd=1,
            activeborderwidth=0,
        )
        self._ctx.add_command(label="🗂️   File Manager",  command=self.open_fm)
        self._ctx.add_command(label="📝   Text Editor",    command=self.open_editor)
        self._ctx.add_command(label="💻   Terminal",       command=self.open_terminal)
        self._ctx.add_separator()
        self._ctx.add_command(label="🎨   Change Wallpaper", command=self._show_wallpaper_menu)
        self._ctx.add_command(label="🔄   Refresh Desktop",  command=self._refresh_desktop)
        self._ctx.add_separator()
        self._ctx.add_command(label="⚙️   Settings",       command=self.open_settings)
        self._ctx.add_command(label="📊   Task Manager",   command=self.open_tasks)

    def _desktop_click(self, _: tk.Event) -> None:
        self._ctx.unpost()
        for w in self.wins:
            w.unfocus()
        self.focused = None

    def _desktop_rclick(self, e: tk.Event) -> None:
        self._ctx.post(e.x_root, e.y_root)

    def _show_wallpaper_menu(self) -> None:
        menu = tk.Menu(
            self.root, tearoff=0,
            bg=T["menu_bg"], fg=T["text"],
            activebackground=T["accent"],
            activeforeground=T["text_inverse"],
        )
        wallpapers = [
            ("gradient_blue",   "🌌 Gradient Blue"),
            ("gradient_purple", "🌆 Gradient Purple"),
            ("stars",           "✨ Starfield"),
            ("grid",            "🔷 Grid"),
            ("sunset",          "🌅 Sunset"),
            ("forest",          "🌲 Forest"),
            ("ocean",           "🌊 Ocean"),
            ("solid",           "⬛ Solid"),
        ]
        for key, label in wallpapers:
            menu.add_command(
                label=label,
                command=lambda k=key: self._set_wallpaper(k),
            )
        menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def _set_wallpaper(self, key: str) -> None:
        self.settings.set("wallpaper", key)
        self._draw_wallpaper()
        self._draw_desktop_icons()

    def _refresh_desktop(self) -> None:
        self._draw_wallpaper()
        self._draw_desktop_icons()

    # ── window lifecycle ──────────────────────────────────────────────────────

    def open_win(self, win: BaseWin) -> BaseWin:
        self.wins.append(win)
        proc = self.procs.spawn(win.title, kind="app")
        win.pid = proc.pid
        win.focus()
        self.tb.update_btns()
        return win

    def close_win(self, win: BaseWin) -> None:
        win.on_close()
        if win.pid:
            self.procs.kill(win.pid)
        try:
            win._outer.destroy()
        except Exception:
            pass
        if win in self.wins:
            self.wins.remove(win)
        if self.focused is win:
            self.focused = None
            visible = [w for w in self.wins if not w.minimized]
            if visible:
                visible[-1].focus()
        self.tb.update_btns()

    def set_focus(self, win: BaseWin) -> None:
        if self.focused and self.focused is not win:
            self.focused.unfocus()
        self.focused = win
        win.on_focus()
        self.tb.update_btns()

    def _launch(self, cls: type, **kw) -> BaseWin:
        return self.open_win(cls(self, **kw))

    # ── app launchers ─────────────────────────────────────────────────────────

    def open_fm(self,          path: Optional[str] = None) -> BaseWin:
        return self._launch(FileManagerApp, start=path or "/home/user")

    def open_editor(self,      path: Optional[str] = None) -> BaseWin:
        return self._launch(TextEditorApp,  filepath=path)

    def open_terminal(self)  -> BaseWin: return self._launch(TerminalApp)
    def open_browser(self,   url: Optional[str] = None) -> BaseWin:
        return self._launch(BrowserApp, url=url)
    def open_music(self)     -> BaseWin: return self._launch(MusicPlayerApp)
    def open_paint(self)     -> BaseWin: return self._launch(PaintApp)
    def open_calc(self)      -> BaseWin: return self._launch(CalculatorApp)
    def open_clock(self)     -> BaseWin: return self._launch(ClockApp)
    def open_tasks(self)     -> BaseWin: return self._launch(TaskManagerApp)
    def open_notes(self)     -> BaseWin: return self._launch(NotesApp)
    def open_email(self)     -> BaseWin: return self._launch(EmailApp)
    def open_passwords(self) -> BaseWin: return self._launch(PasswordManagerApp)
    def open_spreadsheet(self, path: Optional[str] = None) -> BaseWin:
        return self._launch(SpreadsheetApp, filepath=path)
    def open_images(self)    -> BaseWin: return self._launch(ImageViewerApp)
    def open_disk(self)      -> BaseWin: return self._launch(DiskAnalyzerApp)
    def open_coderunner(self)-> BaseWin: return self._launch(CodeRunnerApp)
    def open_archives(self)  -> BaseWin: return self._launch(ArchiveManagerApp)
    def open_settings(self)  -> BaseWin: return self._launch(SettingsApp)
    def open_appstore(self)  -> BaseWin: return self._launch(AppStoreApp)
    def open_sysmon(self)    -> BaseWin: return self._launch(SystemMonitorApp)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 12 — TASKBAR
# ─────────────────────────────────────────────────────────────────────────────

class Taskbar:
    """
    The taskbar sits at the bottom of the screen and contains:
      • Start button (opens StartMenu)
      • Running window buttons (click to focus/minimise)
      • System tray: volume, notifications, date/time
    """

    def __init__(self, wm: WM) -> None:
        self.wm = wm

        self.frame = tk.Frame(
            wm.root,
            bg=T["taskbar_bg"],
            height=TASKBAR_H,
            bd=0,
            highlightthickness=1,
            highlightbackground=T["taskbar_border"],
        )
        self.frame.place(
            x=0, y=SCREEN_H - TASKBAR_H,
            width=SCREEN_W, height=TASKBAR_H,
        )
        self.frame.pack_propagate(False)

        self._build_start_btn()
        self._build_task_area()
        self._build_tray()
        self._task_btns: Dict[int, tk.Button] = {}
        self._clock_tick()

    def _build_start_btn(self) -> None:
        self.start_btn = tk.Button(
            self.frame,
            text="⊞  Start",
            command=self._open_start,
            bg=T["accent"],
            fg=T["text_inverse"],
            relief="flat", bd=0,
            font=(FONT_UI, 10, "bold"),
            padx=16, pady=0,
            cursor="hand2",
            activebackground=darken(T["accent"], 0.1),
            activeforeground=T["text_inverse"],
        )
        self.start_btn.pack(side="left", fill="y", padx=(4, 2), pady=4)

    def _build_task_area(self) -> None:
        self.task_area = tk.Frame(self.frame, bg=T["taskbar_bg"])
        self.task_area.pack(side="left", fill="both", expand=True, padx=4)

    def _build_tray(self) -> None:
        tray = tk.Frame(self.frame, bg=T["taskbar_bg"])
        tray.pack(side="right", fill="y", padx=6)

        # Clock
        self.clock_lbl = tk.Label(
            tray, text="",
            bg=T["taskbar_bg"], fg=T["taskbar_fg"],
            font=(FONT_UI, 10, "bold"), padx=8,
        )
        self.clock_lbl.pack(side="right", fill="y")

        # Date
        self.date_lbl = tk.Label(
            tray, text="",
            bg=T["taskbar_bg"], fg=T["text_muted"],
            font=(FONT_UI, 9), padx=4,
        )
        self.date_lbl.pack(side="right", fill="y")

        mksep(tray, orient="vertical").pack(side="right", fill="y", pady=8, padx=4)

        # Notification bell
        self.notif_btn = tk.Button(
            tray, text="🔔",
            command=self._open_notifs,
            bg=T["taskbar_bg"], fg=T["taskbar_fg"],
            relief="flat", bd=0,
            font=(FONT_EMOJI, 13), padx=5,
            cursor="hand2",
            activebackground=T["button_hover"],
        )
        self.notif_btn.pack(side="right", fill="y")

        # Volume
        self.vol_btn = tk.Button(
            tray, text="🔊",
            command=self._open_volume,
            bg=T["taskbar_bg"], fg=T["taskbar_fg"],
            relief="flat", bd=0,
            font=(FONT_EMOJI, 13), padx=5,
            cursor="hand2",
            activebackground=T["button_hover"],
        )
        self.vol_btn.pack(side="right", fill="y")

        # Network indicator
        self.net_btn = tk.Button(
            tray, text="📶",
            bg=T["taskbar_bg"], fg=T["taskbar_fg"],
            relief="flat", bd=0,
            font=(FONT_EMOJI, 12), padx=5,
            cursor="hand2",
            activebackground=T["button_hover"],
        )
        self.net_btn.pack(side="right", fill="y")

    # ── window buttons ────────────────────────────────────────────────────────

    def update_btns(self) -> None:
        for b in self._task_btns.values():
            b.destroy()
        self._task_btns.clear()

        for win in self.wm.wins:
            is_focused = win is self.wm.focused
            is_min     = win.minimized
            if is_focused:
                bg = T["accent"]
            elif is_min:
                bg = T["text_dim"]
            else:
                bg = T["button_bg"]

            label = f"{win.icon}  {win.title[:18]}"
            b = tk.Button(
                self.task_area,
                text=label,
                command=partial(self._task_click, win),
                bg=bg, fg=T["taskbar_fg"],
                relief="flat", bd=0,
                font=(FONT_UI, 9),
                padx=10, pady=0,
                cursor="hand2",
                activebackground=T["button_hover"],
                activeforeground=T["taskbar_fg"],
            )
            b.pack(side="left", fill="y", padx=2, pady=4)
            self._task_btns[id(win)] = b

    def _task_click(self, win: BaseWin) -> None:
        if win.minimized:
            win.restore()
        elif win is self.wm.focused:
            win.minimize()
        else:
            win.focus()

    # ── clock ─────────────────────────────────────────────────────────────────

    def _clock_tick(self) -> None:
        now = datetime.datetime.now()
        tfmt = self.wm.settings.get("time_format", "%H:%M:%S")
        dfmt = self.wm.settings.get("date_format", "%Y-%m-%d")
        self.clock_lbl.config(text=now.strftime(tfmt))
        self.date_lbl.config(text=now.strftime(dfmt))
        # Update notif badge colour
        unread = self.wm.notifs.unread_count
        self.notif_btn.config(
            fg=T["warning"] if unread > 0 else T["taskbar_fg"],
        )
        self.wm.root.after(1000, self._clock_tick)

    # ── tray popups ───────────────────────────────────────────────────────────

    def _open_start(self)   -> None: StartMenu(self.wm)
    def _open_notifs(self)  -> None: NotifPanel(self.wm)
    def _open_volume(self)  -> None: VolumePanel(self.wm)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 13 — START MENU
# ─────────────────────────────────────────────────────────────────────────────

class StartMenu(tk.Toplevel):
    """
    The Start Menu pops up above the taskbar with:
      • User avatar + name + uptime
      • Search box (live-filter apps)
      • Scrollable app grid
      • Footer: Lock / Log Out / Shut Down
    """

    _ALL_APPS = [
        ("🗂️",  "File Manager",     "open_fm"),
        ("📝",  "Text Editor",      "open_editor"),
        ("💻",  "Terminal",         "open_terminal"),
        ("🌐",  "Browser",          "open_browser"),
        ("🎵",  "Music Player",     "open_music"),
        ("🎨",  "Paint Studio",     "open_paint"),
        ("🔢",  "Calculator",       "open_calc"),
        ("⏰",  "Clock & Alarm",    "open_clock"),
        ("📊",  "Task Manager",     "open_tasks"),
        ("📡",  "System Monitor",   "open_sysmon"),
        ("📓",  "Notes",            "open_notes"),
        ("📧",  "Email",            "open_email"),
        ("🔐",  "Password Manager", "open_passwords"),
        ("📈",  "Spreadsheet",      "open_spreadsheet"),
        ("🖼️", "Image Viewer",     "open_images"),
        ("💾",  "Disk Analyzer",    "open_disk"),
        ("⚡",  "Code Runner",      "open_coderunner"),
        ("📦",  "Archive Manager",  "open_archives"),
        ("🛒",  "App Store",        "open_appstore"),
        ("⚙️", "Settings",         "open_settings"),
    ]

    def __init__(self, wm: WM) -> None:
        super().__init__(wm.root)
        self.wm = wm
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)

        W, H = 340, 560
        x = 4
        y = SCREEN_H - TASKBAR_H - H - 4
        self.geometry(f"{W}x{H}+{x}+{y}")
        self.config(bg=T["menu_bg"])
        self.resizable(False, False)

        self._build()
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.focus_force()

    def _build(self) -> None:
        # ── Header ───────────────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=T["accent"], height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        acct  = self.wm.users.info
        color = acct.avatar_color if acct else T["accent2"]
        name  = acct.fullname if acct else "User"
        uname = self.wm.users.current or "user"

        av = tk.Label(
            hdr,
            text=(uname[0].upper()),
            bg=color, fg="#ffffff",
            font=(FONT_UI, 18, "bold"),
            width=2, relief="flat",
        )
        av.pack(side="left", padx=14, pady=12)

        info_f = tk.Frame(hdr, bg=T["accent"])
        info_f.pack(side="left", pady=12)
        tk.Label(
            info_f, text=name,
            bg=T["accent"], fg="#ffffff",
            font=(FONT_UI, 11, "bold"),
        ).pack(anchor="w")
        tk.Label(
            info_f,
            text=f"@{uname}  •  up {self.wm.users.uptime}",
            bg=T["accent"], fg="#cccccc",
            font=(FONT_UI, 9),
        ).pack(anchor="w")

        # ── Search ───────────────────────────────────────────────────────────
        sf = tk.Frame(self, bg=T["menu_bg"], pady=6)
        sf.pack(fill="x", padx=10)

        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda *_: self._filter())

        se = tk.Entry(
            sf,
            textvariable=self._search_var,
            bg=T["input_bg"], fg=T["text"],
            insertbackground=T["text"],
            relief="flat", bd=6,
            font=(FONT_UI, 10),
            highlightthickness=1,
            highlightcolor=T["input_focus"],
            highlightbackground=T["input_border"],
        )
        se.pack(fill="x")
        se.insert(0, "🔍  Search apps…")
        se.bind(
            "<FocusIn>",
            lambda e: se.delete(0, "end") if se.get().startswith("🔍") else None,
        )
        se.bind(
            "<FocusOut>",
            lambda e: se.insert(0, "🔍  Search apps…") if not se.get() else None,
        )

        # ── App list (scrollable) ─────────────────────────────────────────────
        self._list_frame = ScrollableFrame(self, bg=T["menu_bg"])
        self._list_frame.pack(fill="both", expand=True, padx=4)
        self._render_apps(self._ALL_APPS)

        # ── Footer ───────────────────────────────────────────────────────────
        mksep(self).pack(fill="x", padx=8)
        foot = tk.Frame(self, bg=T["menu_bg"], height=44)
        foot.pack(fill="x", side="bottom")
        foot.pack_propagate(False)

        mkbtn(foot, "⏻  Shut Down", self._shutdown, kind="danger").pack(
            side="right", padx=8, pady=6
        )
        mkbtn(foot, "↩  Log Out",   self._logout).pack(
            side="right", padx=4, pady=6
        )
        mkbtn(foot, "🔒  Lock",      self._lock).pack(
            side="right", padx=4, pady=6
        )

    def _render_apps(self, apps: list) -> None:
        inner = self._list_frame.inner
        for w in inner.winfo_children():
            w.destroy()

        for ico, name, method in apps:
            row = tk.Frame(inner, bg=T["menu_bg"], cursor="hand2")
            row.pack(fill="x", pady=1, padx=2)

            tk.Label(
                row, text=ico,
                bg=T["menu_bg"], fg=T["text"],
                font=(FONT_EMOJI, 14), width=2,
            ).pack(side="left", padx=8, pady=5)

            tk.Label(
                row, text=name,
                bg=T["menu_bg"], fg=T["text"],
                font=(FONT_UI, 10), anchor="w",
            ).pack(side="left", fill="x", expand=True)

            cmd = getattr(self.wm, method, None)
            for widget in (row, *row.winfo_children()):
                widget.bind("<Button-1>",   lambda e, c=cmd: self._launch(c))
                widget.bind("<Enter>",      lambda e, r=row: r.config(bg=T["menu_hover"]))
                widget.bind("<Leave>",      lambda e, r=row: r.config(bg=T["menu_bg"]))

    def _filter(self) -> None:
        q = self._search_var.get().strip().lower()
        if not q or q == "🔍  search apps…":
            self._render_apps(self._ALL_APPS)
        else:
            filtered = [
                (i, n, m) for i, n, m in self._ALL_APPS
                if q in n.lower()
            ]
            self._render_apps(filtered)

    def _launch(self, cmd: Optional[Callable]) -> None:
        self.destroy()
        if cmd:
            cmd()

    def _shutdown(self) -> None:
        self.destroy()
        if messagebox.askyesno(
            "Shut Down", "Are you sure you want to shut down PyOS?",
            parent=self.wm.root,
        ):
            self.wm.root.quit()

    def _logout(self) -> None:
        self.destroy()
        self.wm.users.logout()
        show_login(self.wm.root, self.wm)

    def _lock(self) -> None:
        self.destroy()
        show_lock(self.wm.root, self.wm)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 14 — SYSTEM PANELS (Notifications, Volume, Quick Settings)
# ─────────────────────────────────────────────────────────────────────────────

class NotifPanel(tk.Toplevel):
    """Slide-in notification centre from the system tray."""

    def __init__(self, wm: WM) -> None:
        super().__init__(wm.root)
        self.wm = wm
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)

        W, H = 320, 420
        x = SCREEN_W - W - 4
        y = SCREEN_H - TASKBAR_H - H - 4
        self.geometry(f"{W}x{H}+{x}+{y}")
        self.config(bg=T["panel_bg"])
        self._build()
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.focus_force()

    def _build(self) -> None:
        # Header
        hdr = tk.Frame(self, bg=T["panel_bg"])
        hdr.pack(fill="x", padx=10, pady=8)
        tk.Label(
            hdr, text="🔔  Notifications",
            bg=T["panel_bg"], fg=T["text"],
            font=(FONT_UI, 11, "bold"),
        ).pack(side="left")
        tk.Button(
            hdr, text="Clear All",
            command=self._clear_all,
            bg=T["button_bg"], fg=T["text"],
            relief="flat", bd=0,
            font=(FONT_UI, 9), padx=8,
            cursor="hand2",
            activebackground=T["button_hover"],
        ).pack(side="right")

        unread = self.wm.notifs.unread_count
        if unread:
            tk.Label(
                hdr,
                text=f"{unread} unread",
                bg=T["panel_bg"], fg=T["warning"],
                font=(FONT_UI, 9),
            ).pack(side="right", padx=6)

        mksep(self).pack(fill="x", padx=10)

        # Notification list
        self._sf = ScrollableFrame(self, bg=T["panel_bg"])
        self._sf.pack(fill="both", expand=True, padx=6, pady=4)
        self._render()

    def _render(self) -> None:
        inner = self._sf.inner
        for w in inner.winfo_children():
            w.destroy()

        notifs = self.wm.notifs.recent(30)
        if not notifs:
            tk.Label(
                inner, text="No notifications",
                bg=T["panel_bg"], fg=T["text_muted"],
                font=(FONT_UI, 10),
            ).pack(pady=20)
            return

        for n in notifs:
            bg = T["accent"] if not n.read else T["button_bg"]
            card = tk.Frame(inner, bg=bg, padx=10, pady=7)
            card.pack(fill="x", pady=2)

            # Icon + title row
            top = tk.Frame(card, bg=bg)
            top.pack(fill="x")
            tk.Label(
                top, text=n.icon,
                bg=bg, fg=T["text"],
                font=(FONT_EMOJI, 12),
            ).pack(side="left")
            tk.Label(
                top, text=n.title,
                bg=bg, fg=T["text"],
                font=(FONT_UI, 9, "bold"),
            ).pack(side="left", padx=4)
            tk.Label(
                top, text=n.time_str,
                bg=bg, fg=T["text_muted"],
                font=(FONT_UI, 8),
            ).pack(side="right")

            # Body
            tk.Label(
                card, text=n.body,
                bg=bg, fg=T["text_muted"],
                font=(FONT_UI, 9),
                wraplength=270, justify="left",
            ).pack(anchor="w", pady=(2, 0))

            n.read = True

    def _clear_all(self) -> None:
        self.wm.notifs.clear()
        self._render()


class VolumePanel(tk.Toplevel):
    """Quick volume control popup from the system tray."""

    def __init__(self, wm: WM) -> None:
        super().__init__(wm.root)
        self.wm = wm
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)

        W, H = 240, 110
        x = SCREEN_W - W - 4
        y = SCREEN_H - TASKBAR_H - H - 4
        self.geometry(f"{W}x{H}+{x}+{y}")
        self.config(bg=T["panel_bg"])
        self.bind("<FocusOut>", lambda e: self.destroy())

        vol = wm.settings.get("volume", 70)
        self._vol_var = tk.IntVar(value=vol)

        tk.Label(
            self, text="🔊  Volume",
            bg=T["panel_bg"], fg=T["text"],
            font=(FONT_UI, 10, "bold"),
        ).pack(pady=(14, 4))

        slider = ttk.Scale(
            self, from_=0, to=100,
            orient="horizontal",
            variable=self._vol_var,
            command=self._on_change,
        )
        slider.pack(fill="x", padx=20)

        self._pct_lbl = tk.Label(
            self,
            text=f"{vol}%",
            bg=T["panel_bg"], fg=T["text_muted"],
            font=(FONT_UI, 9),
        )
        self._pct_lbl.pack()
        self.focus_force()

    def _on_change(self, val: str) -> None:
        v = int(float(val))
        self.wm.settings.set("volume", v)
        self._pct_lbl.config(text=f"{v}%")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 15 — FILE MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class FileManagerApp(BaseWin):
    """
    Full-featured dual-pane file manager:
      • Sidebar with bookmarks / places
      • Breadcrumb path bar
      • Sortable file list (name / size / type / date)
      • Column headers
      • Right-click context menu (open, edit, copy, cut, paste, rename, delete, properties)
      • Search (regex, recursive)
      • Keyboard shortcuts
      • Status bar with disk usage
      • Copy / cut / paste (uses shared Clipboard)
      • Preview pane toggle
    """

    PLACES = [
        ("🏠  Home",         "/home/user"),
        ("🖥️  Desktop",     "/home/user/Desktop"),
        ("📄  Documents",    "/home/user/Documents"),
        ("⬇️  Downloads",   "/home/user/Downloads"),
        ("🎵  Music",        "/home/user/Music"),
        ("🖼️  Pictures",    "/home/user/Pictures"),
        ("📹  Videos",       "/home/user/Videos"),
        ("💻  Code",         "/home/user/Code"),
        ("📈  Spreadsheets", "/home/user/Spreadsheets"),
        ("📦  Archives",     "/home/user/Archives"),
        ("📦  Temp",         "/tmp"),
        ("⚙️  Etc",         "/etc"),
        ("🌳  Root",         "/"),
    ]

    def __init__(self, wm: WM, start: str = "/home/user") -> None:
        self._start      = start
        self._sort_key   = "name"     # name | size | type | modified
        self._sort_rev   = False
        self._selected:  Optional[str] = None
        super().__init__(wm, "File Manager", 80, 50, 860, 580, "🗂️")

    # ── UI construction ───────────────────────────────────────────────────────

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["panel_bg"])

        # Current path state
        self.cur       = self._start
        self._hist:    List[str] = [self._start]
        self._hist_pos = 0

        # ── Toolbar ──────────────────────────────────────────────────────────
        self._build_toolbar(parent)

        # ── Main pane ─────────────────────────────────────────────────────────
        main = tk.PanedWindow(
            parent, orient="horizontal",
            bg=T["panel_bg"], sashwidth=5,
            sashrelief="flat", sashpad=2,
        )
        main.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(main, bg=T["panel_bg"], width=170)
        main.add(sidebar, minsize=130)
        self._build_sidebar(sidebar)

        # File list + preview
        self._content_pane = tk.PanedWindow(
            main, orient="horizontal",
            bg=T["win_bg"], sashwidth=4,
            sashrelief="flat",
        )
        main.add(self._content_pane, minsize=350)

        self._list_container = tk.Frame(self._content_pane, bg=T["win_bg"])
        self._content_pane.add(self._list_container, minsize=280)
        self._build_file_list(self._list_container)

        # Preview pane (hidden by default)
        self._preview_frame = tk.Frame(self._content_pane, bg=T["panel_bg"])
        self._preview_visible = False

        # ── Status bar ────────────────────────────────────────────────────────
        self._build_status(parent)

        # Load initial directory
        self._load(self.cur)

    def _build_toolbar(self, parent: tk.Frame) -> None:
        tb = tk.Frame(parent, bg=T["panel_bg"], height=42)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Navigation buttons
        nav_specs = [
            ("◀",  self._go_back,    "Back"),
            ("▶",  self._go_forward, "Forward"),
            ("↑",  self._go_up,      "Parent folder"),
            ("⟳",  self._reload,     "Refresh"),
        ]
        for txt, cmd, tip in nav_specs:
            b = tk.Button(
                tb, text=txt, command=cmd,
                bg=T["button_bg"], fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_UI, 12), padx=8, pady=4,
                cursor="hand2",
                activebackground=T["button_hover"],
            )
            b.pack(side="left", padx=2, pady=4)
            Tooltip(b, tip)

        mksep(tb, "vertical").pack(side="left", fill="y", pady=8, padx=4)

        # Path entry
        self._path_var = tk.StringVar(value=self._start)
        path_entry = mkentry(tb, textvariable=self._path_var, width=40)
        path_entry.pack(side="left", fill="y", expand=True, padx=6, pady=6)
        path_entry.bind("<Return>", lambda e: self._nav(self._path_var.get()))

        mksep(tb, "vertical").pack(side="left", fill="y", pady=8, padx=4)

        # Action buttons
        action_specs = [
            ("📁  New Folder", self._new_folder,  "accent"),
            ("📄  New File",   self._new_file,    "normal"),
            ("🔍  Search",     self._open_search, "normal"),
        ]
        for txt, cmd, kind in action_specs:
            mkbtn(tb, txt, cmd, kind=kind).pack(side="left", padx=2, pady=4)

        # View toggle
        self._preview_btn = tk.Button(
            tb, text="👁",
            command=self._toggle_preview,
            bg=T["button_bg"], fg=T["text"],
            relief="flat", bd=0,
            font=(FONT_EMOJI, 12), padx=6, pady=4,
            cursor="hand2",
            activebackground=T["button_hover"],
        )
        self._preview_btn.pack(side="right", padx=4, pady=4)
        Tooltip(self._preview_btn, "Toggle preview pane")

    def _build_sidebar(self, parent: tk.Frame) -> None:
        tk.Label(
            parent, text="PLACES",
            bg=T["panel_bg"], fg=T["text_muted"],
            font=(FONT_UI, 8, "bold"), padx=10,
        ).pack(anchor="w", pady=(10, 2))

        for label, path in self.PLACES:
            b = tk.Button(
                parent, text=label,
                command=lambda p=path: self._nav(p),
                bg=T["panel_bg"], fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_UI, 9),
                anchor="w", padx=12, pady=4,
                cursor="hand2",
                activebackground=T["menu_hover"],
            )
            b.pack(fill="x")

        mksep(parent).pack(fill="x", padx=8, pady=6)

        tk.Label(
            parent, text="BOOKMARKS",
            bg=T["panel_bg"], fg=T["text_muted"],
            font=(FONT_UI, 8, "bold"), padx=10,
        ).pack(anchor="w", pady=(0, 2))

        self._bm_frame = tk.Frame(parent, bg=T["panel_bg"])
        self._bm_frame.pack(fill="x")
        self._bookmarks: List[Tuple[str, str]] = []

        mk = tk.Button(
            parent, text="+ Add Bookmark",
            command=self._add_bookmark,
            bg=T["panel_bg"], fg=T["text_muted"],
            relief="flat", bd=0,
            font=(FONT_UI, 8),
            anchor="w", padx=12, pady=3,
            cursor="hand2",
            activebackground=T["menu_hover"],
        )
        mk.pack(fill="x")

    def _build_file_list(self, parent: tk.Frame) -> None:
        # Column headers
        hdr = tk.Frame(parent, bg=T["panel_alt"])
        hdr.pack(fill="x")
        self._header_frame = hdr

        col_specs = [
            ("Name",     "name",     260),
            ("Size",     "size",     80),
            ("Type",     "type",     110),
            ("Modified", "modified", 150),
        ]
        for col_label, col_key, col_w in col_specs:
            b = tk.Button(
                hdr, text=col_label,
                command=lambda k=col_key: self._sort_by(k),
                bg=T["panel_alt"], fg=T["text_muted"],
                relief="flat", bd=0,
                font=(FONT_UI, 9, "bold"),
                width=col_w // 8, anchor="w",
                padx=6, pady=4,
                cursor="hand2",
                activebackground=T["button_hover"],
            )
            b.pack(side="left", padx=2)

        # Scrollable list
        self._sf = ScrollableFrame(parent, bg=T["win_bg"])
        self._sf.pack(fill="both", expand=True)

    def _build_status(self, parent: tk.Frame) -> None:
        sf = tk.Frame(parent, bg=T["status_bg"], height=24)
        sf.pack(fill="x", side="bottom")
        sf.pack_propagate(False)

        self._status_lbl = tk.Label(
            sf, text="Ready",
            bg=T["status_bg"], fg=T["text_muted"],
            font=(FONT_UI, 9), anchor="w", padx=8,
        )
        self._status_lbl.pack(side="left", fill="y")

        self._disk_lbl = tk.Label(
            sf, text="",
            bg=T["status_bg"], fg=T["text_muted"],
            font=(FONT_UI, 9), padx=8,
        )
        self._disk_lbl.pack(side="right", fill="y")

    # ── directory loading ─────────────────────────────────────────────────────

    def _load(self, path: str) -> None:
        self.cur = path
        self._path_var.set(path)

        # Clear file list
        inner = self._sf.inner
        for w in inner.winfo_children():
            w.destroy()

        # Fetch entries
        try:
            names = self.wm.vfs.listdir(path)
        except Exception as ex:
            self._status_lbl.config(text=f"Error: {ex}")
            return

        show_hidden = self.wm.settings.get("show_hidden_files", False)
        entries: List[Dict[str, Any]] = []

        for name in names:
            if not show_hidden and name.startswith("."):
                continue
            full = path.rstrip("/") + "/" + name
            try:
                st = self.wm.vfs.stat(full)
            except Exception:
                continue
            entries.append({
                "name":     name,
                "full":     full,
                "is_dir":   st["is_dir"],
                "size":     st["size"],
                "modified": st["modified"],
                "type":     get_file_type(name, st["is_dir"]),
            })

        # Sort
        rev = self._sort_rev
        if self._sort_key == "name":
            if self.wm.settings.get("sort_folders_first", True):
                entries.sort(key=lambda e: (not e["is_dir"], e["name"].lower()), reverse=rev)
            else:
                entries.sort(key=lambda e: e["name"].lower(), reverse=rev)
        elif self._sort_key == "size":
            entries.sort(key=lambda e: e["size"], reverse=rev)
        elif self._sort_key == "type":
            entries.sort(key=lambda e: e["type"].lower(), reverse=rev)
        elif self._sort_key == "modified":
            entries.sort(key=lambda e: e["modified"], reverse=rev)

        # Render rows
        for idx, entry in enumerate(entries):
            self._render_row(inner, entry, idx)

        # Status
        dirs  = sum(1 for e in entries if e["is_dir"])
        files = len(entries) - dirs
        used, total = self.wm.vfs.disk_usage()
        self._status_lbl.config(
            text=f"{len(entries)} items  ({dirs} folders, {files} files)"
        )
        self._disk_lbl.config(
            text=f"Disk: {fmt_size(used)} / {fmt_size(total)}"
        )
        self._sf.scroll_to_top()

    def _render_row(
        self, inner: tk.Frame, entry: Dict[str, Any], idx: int
    ) -> None:
        bg   = T["win_bg"] if idx % 2 == 0 else T["panel_bg"]
        full = entry["full"]

        row = tk.Frame(inner, bg=bg, cursor="hand2")
        row.pack(fill="x")

        # Icon
        icon = get_file_icon(entry["name"], entry["is_dir"])
        tk.Label(
            row, text=icon,
            bg=bg, fg=T["text"],
            font=(FONT_EMOJI, 12), width=2,
        ).pack(side="left", padx=(4, 0))

        # Name
        tk.Label(
            row, text=entry["name"],
            bg=bg, fg=T["text"],
            font=(FONT_UI, 9),
            width=28, anchor="w",
        ).pack(side="left", padx=4, pady=3)

        # Size
        sz = fmt_size(entry["size"]) if not entry["is_dir"] else "—"
        tk.Label(
            row, text=sz,
            bg=bg, fg=T["text_muted"],
            font=(FONT_UI, 9), width=9,
        ).pack(side="left")

        # Type
        tk.Label(
            row, text=entry["type"],
            bg=bg, fg=T["text_muted"],
            font=(FONT_UI, 9), width=12, anchor="w",
        ).pack(side="left")

        # Modified
        mod = datetime.datetime.fromtimestamp(entry["modified"]).strftime(
            "%Y-%m-%d %H:%M"
        )
        tk.Label(
            row, text=mod,
            bg=bg, fg=T["text_muted"],
            font=(FONT_UI, 9),
        ).pack(side="left", padx=4)

        # Bindings
        hover_bg = T["selection"]
        for child in row.winfo_children() + [row]:
            child.bind(
                "<Double-Button-1>",
                lambda e, f=full, d=entry["is_dir"]: self._open(f, d),
            )
            child.bind(
                "<Button-1>",
                lambda e, f=full: self._select(f),
            )
            child.bind(
                "<Button-3>",
                lambda e, f=full, d=entry["is_dir"]: self._ctx_menu(e, f, d),
            )
            child.bind(
                "<Enter>",
                lambda e, r=row, obg=bg: r.config(bg=T["menu_hover"]),
            )
            child.bind(
                "<Leave>",
                lambda e, r=row, obg=bg: r.config(bg=obg),
            )

    # ── navigation ────────────────────────────────────────────────────────────

    def _nav(self, path: str) -> None:
        path = self.wm.vfs.resolve(path)
        if not self.wm.vfs.isdir(path):
            self._status_lbl.config(text=f"Not a directory: {path}")
            return
        # Trim forward history if we branched
        if self._hist_pos < len(self._hist) - 1:
            self._hist = self._hist[: self._hist_pos + 1]
        self._hist.append(path)
        self._hist_pos = len(self._hist) - 1
        self._load(path)

    def _go_back(self) -> None:
        if self._hist_pos > 0:
            self._hist_pos -= 1
            self._load(self._hist[self._hist_pos])

    def _go_forward(self) -> None:
        if self._hist_pos < len(self._hist) - 1:
            self._hist_pos += 1
            self._load(self._hist[self._hist_pos])

    def _go_up(self) -> None:
        parts = self.cur.rstrip("/").split("/")
        if len(parts) > 1:
            parent = "/".join(parts[:-1]) or "/"
            self._nav(parent)

    def _reload(self) -> None:
        self._load(self.cur)

    def _sort_by(self, key: str) -> None:
        if self._sort_key == key:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_key = key
            self._sort_rev = False
        self._load(self.cur)

    # ── file operations ───────────────────────────────────────────────────────

    def _open(self, path: str, is_dir: bool) -> None:
        if is_dir:
            self._nav(path)
        else:
            name = path.split("/")[-1]
            if is_text_file(name):
                self.wm.open_editor(path)
            elif name.endswith(".csv"):
                self.wm.open_spreadsheet(path)
            else:
                self.wm.notifs.send(
                    "File Manager", f"Opened: {name}", icon="📄"
                )

    def _select(self, path: str) -> None:
        self._selected = path
        # Show preview if pane is visible
        if self._preview_visible:
            self._update_preview(path)

    def _ctx_menu(self, e: tk.Event, path: str, is_dir: bool) -> None:
        m = tk.Menu(
            self.wm.root, tearoff=0,
            bg=T["menu_bg"], fg=T["text"],
            activebackground=T["accent"],
            activeforeground=T["text_inverse"],
        )
        if not is_dir:
            m.add_command(label="📖  Open",       command=lambda: self._open(path, False))
            m.add_command(label="📝  Edit",        command=lambda: self.wm.open_editor(path))
        else:
            m.add_command(label="📂  Open Folder", command=lambda: self._open(path, True))
        m.add_separator()
        m.add_command(label="📋  Copy",        command=lambda: self._copy([path]))
        m.add_command(label="✂️   Cut",         command=lambda: self._cut([path]))
        m.add_command(label="📋  Paste",       command=self._paste)
        m.add_separator()
        m.add_command(label="✏️   Rename",      command=lambda: self._rename(path))
        m.add_command(label="🗑️   Delete",      command=lambda: self._delete(path, is_dir))
        m.add_separator()
        m.add_command(label="🔖  Bookmark",    command=lambda: self._bookmark(path))
        m.add_command(label="ℹ️   Properties",  command=lambda: self._properties(path))
        m.post(e.x_root, e.y_root)

    def _copy(self, paths: List[str]) -> None:
        self.wm.clip.copy_files(paths, cut=False)
        self._status_lbl.config(text=f"Copied {len(paths)} item(s)")

    def _cut(self, paths: List[str]) -> None:
        self.wm.clip.copy_files(paths, cut=True)
        self._status_lbl.config(text=f"Cut {len(paths)} item(s)")

    def _paste(self) -> None:
        files, mode = self.wm.clip.paste_files()
        for src in files:
            name = src.split("/")[-1]
            dst  = self.cur.rstrip("/") + "/" + name
            try:
                if self.wm.vfs.isfile(src):
                    self.wm.vfs.copy(src, dst)
                    if mode == "cut":
                        self.wm.vfs.remove(src)
                elif self.wm.vfs.isdir(src):
                    self.wm.vfs.copy_tree(src, dst)
                    if mode == "cut":
                        self.wm.vfs.rmdir(src, recursive=True)
            except Exception as ex:
                messagebox.showerror("Paste Error", str(ex), parent=self.wm.root)
        self._reload()

    def _rename(self, path: str) -> None:
        old_name = path.split("/")[-1]
        new_name = simpledialog.askstring(
            "Rename", "New name:",
            initialvalue=old_name, parent=self.wm.root,
        )
        if new_name and new_name != old_name:
            new_path = "/".join(path.split("/")[:-1]) + "/" + new_name
            try:
                self.wm.vfs.rename(path, new_path)
                self._reload()
            except Exception as ex:
                messagebox.showerror("Rename Error", str(ex), parent=self.wm.root)

    def _delete(self, path: str, is_dir: bool) -> None:
        if self.wm.settings.get("confirm_delete", True):
            name = path.split("/")[-1]
            if not messagebox.askyesno(
                "Delete", f"Delete '{name}'?\nThis cannot be undone.",
                parent=self.wm.root,
            ):
                return
        try:
            if is_dir:
                self.wm.vfs.rmdir(path, recursive=True)
            else:
                self.wm.vfs.remove(path)
            self._reload()
        except Exception as ex:
            messagebox.showerror("Delete Error", str(ex), parent=self.wm.root)

    def _new_folder(self) -> None:
        name = simpledialog.askstring(
            "New Folder", "Folder name:", parent=self.wm.root
        )
        if name:
            try:
                self.wm.vfs.mkdir(self.cur.rstrip("/") + "/" + name)
                self._reload()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self.wm.root)

    def _new_file(self) -> None:
        name = simpledialog.askstring(
            "New File", "File name:", parent=self.wm.root
        )
        if name:
            try:
                self.wm.vfs.write(self.cur.rstrip("/") + "/" + name, "")
                self._reload()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self.wm.root)

    def _open_search(self) -> None:
        d = tk.Toplevel(self.wm.root)
        d.title("Search Files")
        d.config(bg=T["win_bg"])
        d.geometry("480x420")
        d.wm_attributes("-topmost", True)

        # Search bar
        sf = tk.Frame(d, bg=T["win_bg"])
        sf.pack(fill="x", padx=12, pady=10)
        tk.Label(sf, text="Pattern (regex):", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(side="left")
        pv = tk.StringVar()
        pe = mkentry(sf, textvariable=pv, width=28)
        pe.pack(side="left", padx=6)

        # Options
        of = tk.Frame(d, bg=T["win_bg"])
        of.pack(fill="x", padx=12)
        search_content_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            of, text="Search file contents (grep)",
            variable=search_content_var,
            bg=T["win_bg"], fg=T["text"],
            selectcolor=T["accent"],
            activebackground=T["win_bg"],
            font=(FONT_UI, 9),
        ).pack(side="left")

        mkbtn(sf, "Search", lambda: _do_search(), kind="accent").pack(side="left")

        # Results
        res_lbl = tk.Label(d, text="", bg=T["win_bg"], fg=T["text_muted"],
                           font=(FONT_UI, 9), anchor="w", padx=12)
        res_lbl.pack(fill="x")

        lb = tk.Listbox(
            d, bg=T["input_bg"], fg=T["text"],
            selectbackground=T["selection"],
            font=(FONT_MONO, 10), relief="flat", bd=0,
        )
        vsb = tk.Scrollbar(d, orient="vertical", command=lb.yview)
        lb.config(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        lb.pack(fill="both", expand=True, padx=10, pady=4)

        def _do_search() -> None:
            pat = pv.get().strip()
            if not pat:
                return
            lb.delete(0, "end")
            if search_content_var.get():
                results = [
                    f"{p}:{ln}: {line}"
                    for p, ln, line in self.wm.vfs.grep(pat, self.cur)
                ]
            else:
                results = self.wm.vfs.find(pat, self.cur)
            res_lbl.config(text=f"{len(results)} result(s) for '{pat}'")
            for r in results:
                lb.insert("end", r)
            if not results:
                lb.insert("end", "No results found.")

        def _open_result(e: tk.Event) -> None:
            sel = lb.curselection()
            if not sel:
                return
            item = lb.get(sel[0])
            path = item.split(":")[0]
            if self.wm.vfs.isfile(path):
                self.wm.open_editor(path)
            elif self.wm.vfs.isdir(path):
                self._nav(path)
                d.destroy()

        lb.bind("<Double-Button-1>", _open_result)
        pe.focus_set()
        pe.bind("<Return>", lambda e: _do_search())

    def _properties(self, path: str) -> None:
        try:
            st = self.wm.vfs.stat(path)
        except Exception as ex:
            messagebox.showerror("Error", str(ex), parent=self.wm.root)
            return
        d = tk.Toplevel(self.wm.root)
        d.title("Properties")
        d.config(bg=T["win_bg"])
        d.geometry("360x340")
        d.resizable(False, False)

        rows = [
            ("Name",        st["name"]),
            ("Path",        st["full_path"]),
            ("Type",        "Directory" if st["is_dir"] else "File"),
            ("Size",        st["size_str"]),
            ("Permissions", st["permissions"]),
            ("Owner",       f"{st['owner']} / {st['group']}"),
            ("Created",     fmt_time(st["created"])),
            ("Modified",    fmt_time(st["modified"])),
            ("Accessed",    fmt_time(st["accessed"])),
        ]
        for i, (k, v) in enumerate(rows):
            bg = T["win_bg"] if i % 2 == 0 else T["panel_bg"]
            f  = tk.Frame(d, bg=bg)
            f.pack(fill="x")
            tk.Label(f, text=k + ":", bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 9), width=13, anchor="e").pack(
                side="left", padx=8, pady=5
            )
            tk.Label(f, text=str(v)[:55], bg=bg, fg=T["text"],
                     font=(FONT_UI, 9), anchor="w").pack(side="left")

        mkbtn(d, "Close", d.destroy).pack(pady=10)

    def _bookmark(self, path: str) -> None:
        name = path.split("/")[-1] or path
        self._bookmarks.append((name, path))
        b = tk.Button(
            self._bm_frame, text=f"🔖  {name[:18]}",
            command=lambda p=path: self._nav(p),
            bg=T["panel_bg"], fg=T["text"],
            relief="flat", bd=0,
            font=(FONT_UI, 9),
            anchor="w", padx=12, pady=3,
            cursor="hand2",
            activebackground=T["menu_hover"],
        )
        b.pack(fill="x")

    def _add_bookmark(self) -> None:
        self._bookmark(self.cur)

    def _toggle_preview(self) -> None:
        if self._preview_visible:
            self._content_pane.forget(self._preview_frame)
            self._preview_visible = False
            self._preview_btn.config(fg=T["text"])
        else:
            self._content_pane.add(self._preview_frame, minsize=160)
            self._preview_visible = True
            self._preview_btn.config(fg=T["accent"])
            if self._selected:
                self._update_preview(self._selected)

    def _update_preview(self, path: str) -> None:
        for w in self._preview_frame.winfo_children():
            w.destroy()
        tk.Label(
            self._preview_frame, text="Preview",
            bg=T["panel_bg"], fg=T["text_muted"],
            font=(FONT_UI, 9, "bold"), padx=8,
        ).pack(anchor="w", pady=(8, 4))
        mksep(self._preview_frame).pack(fill="x", padx=6)
        if self.wm.vfs.isfile(path):
            try:
                content = self.wm.vfs.read(path)
                t = tk.Text(
                    self._preview_frame,
                    bg=T["code_bg"], fg=T["code_fg"],
                    font=(FONT_MONO, 9), relief="flat", bd=0,
                    wrap="word", state="normal",
                )
                t.pack(fill="both", expand=True, padx=6, pady=4)
                t.insert("1.0", content[:2000])
                t.config(state="disabled")
            except Exception:
                tk.Label(
                    self._preview_frame,
                    text="Cannot preview this file.",
                    bg=T["panel_bg"], fg=T["text_muted"],
                    font=(FONT_UI, 9),
                ).pack(pady=10)
        else:
            try:
                items = self.wm.vfs.listdir(path)
                for item in items[:20]:
                    full = path.rstrip("/") + "/" + item
                    ico  = get_file_icon(item, self.wm.vfs.isdir(full))
                    tk.Label(
                        self._preview_frame,
                        text=f"{ico}  {item}",
                        bg=T["panel_bg"], fg=T["text"],
                        font=(FONT_UI, 9), anchor="w", padx=8,
                    ).pack(anchor="w")
                if len(items) > 20:
                    tk.Label(
                        self._preview_frame,
                        text=f"…and {len(items)-20} more",
                        bg=T["panel_bg"], fg=T["text_muted"],
                        font=(FONT_UI, 8), padx=8,
                    ).pack(anchor="w")
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 16 — TEXT EDITOR
# ─────────────────────────────────────────────────────────────────────────────

class TextEditorApp(BaseWin):
    """
    Professional text editor with:
      • Syntax colouring (Python, JS, HTML, CSS, JSON, SQL, Bash)
      • Line numbers panel
      • Find / Find+Replace
      • Multiple undo/redo levels
      • Word count, character count
      • Auto-indent, bracket matching
      • Run Python script (inline output)
      • Encoding indicator
      • Column ruler
      • Code folding indicator
      • Word wrap toggle
      • Multiple file format awareness
      • Base64 encode/decode
      • Sort lines / remove duplicates / trim whitespace
      • Diff two buffers
    """

    # ── Syntax token definitions ──────────────────────────────────────────────
    _KEYWORDS = {
        "python": [
            "False","None","True","and","as","assert","async","await",
            "break","class","continue","def","del","elif","else","except",
            "finally","for","from","global","if","import","in","is",
            "lambda","nonlocal","not","or","pass","raise","return",
            "try","while","with","yield",
        ],
        "python_builtins": [
            "abs","all","any","bin","bool","bytes","callable","chr","dict",
            "dir","divmod","enumerate","eval","exec","filter","float","format",
            "frozenset","getattr","globals","hasattr","hash","help","hex",
            "id","input","int","isinstance","issubclass","iter","len","list",
            "locals","map","max","memoryview","min","next","object","oct",
            "open","ord","pow","print","property","range","repr","reversed",
            "round","set","setattr","slice","sorted","staticmethod","str",
            "sum","super","tuple","type","vars","zip",
        ],
        "js": [
            "break","case","catch","class","const","continue","debugger",
            "default","delete","do","else","export","extends","finally",
            "for","function","if","import","in","instanceof","let","new",
            "return","static","super","switch","this","throw","try",
            "typeof","var","void","while","with","yield","async","await",
            "of","from","null","undefined","true","false",
        ],
        "sql": [
            "SELECT","FROM","WHERE","INSERT","INTO","VALUES","UPDATE","SET",
            "DELETE","CREATE","TABLE","DROP","ALTER","ADD","COLUMN","INDEX",
            "JOIN","LEFT","RIGHT","INNER","OUTER","ON","AS","ORDER","BY",
            "GROUP","HAVING","LIMIT","OFFSET","DISTINCT","COUNT","SUM",
            "AVG","MAX","MIN","AND","OR","NOT","NULL","IS","IN","LIKE",
            "BETWEEN","EXISTS","UNION","ALL","CASE","WHEN","THEN","END",
            "PRIMARY","KEY","FOREIGN","REFERENCES","CASCADE","DATABASE",
            "SHOW","DESCRIBE","EXPLAIN","TRUNCATE","COMMIT","ROLLBACK",
        ],
        "html_tags": [
            "html","head","body","div","span","p","a","ul","ol","li",
            "h1","h2","h3","h4","h5","h6","table","tr","td","th","form",
            "input","button","select","option","textarea","img","link",
            "script","style","meta","title","header","footer","nav","main",
            "article","section","aside","figure","figcaption","video",
            "audio","canvas","svg","template","slot","code","pre","blockquote",
        ],
    }

    def __init__(
        self,
        wm:       WM,
        filepath: Optional[str] = None,
    ) -> None:
        self.filepath  = filepath
        self.modified  = False
        self._font_size = wm.settings.get("editor_font_size", 11)
        self._lang      = "plain"
        self._encoding  = "UTF-8"

        title = (
            filepath.split("/")[-1] if filepath else "Untitled"
        ) + " — Editor"
        super().__init__(wm, title, 110, 55, 920, 640, "📝")

    # ── UI construction ───────────────────────────────────────────────────────

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])
        self._build_menubar(parent)
        self._build_editor_area(parent)
        self._build_statusbar(parent)
        self._load_file()

        # Key bindings
        self.ed.text.bind("<<Modified>>",   self._on_modified)
        self.ed.text.bind("<KeyRelease>",   self._on_key)
        self.ed.text.bind("<Control-s>",    lambda e: self._save())
        self.ed.text.bind("<Control-S>",    lambda e: self._save_as())
        self.ed.text.bind("<Control-z>",    lambda e: self.ed.text.edit_undo())
        self.ed.text.bind("<Control-y>",    lambda e: self.ed.text.edit_redo())
        self.ed.text.bind("<Control-f>",    lambda e: self._find_bar())
        self.ed.text.bind("<Control-h>",    lambda e: self._find_replace())
        self.ed.text.bind("<Control-a>",    lambda e: self._select_all())
        self.ed.text.bind("<Tab>",          self._handle_tab)
        self.ed.text.bind("<Return>",       self._handle_return)
        self.ed.text.bind("<Button-1>",     lambda e: self._update_status())

    def _build_menubar(self, parent: tk.Frame) -> None:
        mb = tk.Frame(parent, bg=T["panel_bg"])
        mb.pack(fill="x")

        menus = [
            ("File", [
                ("📄  New",            "Ctrl+N", self._new),
                ("📂  Open from VFS…", "",       self._open_vfs),
                ("💾  Save",           "Ctrl+S", self._save),
                ("💾  Save As…",       "Ctrl+Shift+S", self._save_as),
                None,
                ("📤  Export…",        "",       self._export),
                None,
                ("❌  Close",          "",       self.close),
            ]),
            ("Edit", [
                ("↩  Undo",        "Ctrl+Z",   lambda: self.ed.text.edit_undo()),
                ("↪  Redo",        "Ctrl+Y",   lambda: self.ed.text.edit_redo()),
                None,
                ("🔍  Find",        "Ctrl+F",   self._find_bar),
                ("🔁  Find & Replace", "Ctrl+H", self._find_replace),
                None,
                ("⬛  Select All",  "Ctrl+A",   self._select_all),
                ("🗑️  Clear All",   "",         self._clear_all),
            ]),
            ("Format", [
                ("UPPER CASE",          "", lambda: self._transform_sel("upper")),
                ("lower case",          "", lambda: self._transform_sel("lower")),
                ("Title Case",          "", lambda: self._transform_sel("title")),
                None,
                ("Sort Lines A→Z",      "", lambda: self._sort_lines(False)),
                ("Sort Lines Z→A",      "", lambda: self._sort_lines(True)),
                ("Remove Duplicate Lines","",self._remove_duplicates),
                ("Remove Blank Lines",  "", self._remove_blank),
                ("Trim Whitespace",     "", self._trim_whitespace),
                None,
                ("Add Line Numbers",    "", self._add_line_nums),
                ("Reverse Lines",       "", self._reverse_lines),
            ]),
            ("Tools", [
                ("🔢  Word Count",      "", self._word_count),
                ("📊  Char Frequency",  "", self._char_freq),
                ("▶  Run Python",       "", self._run_python),
                None,
                ("🔒  Encode Base64",   "", self._encode_b64),
                ("🔓  Decode Base64",   "", self._decode_b64),
                ("🔑  MD5 Hash",        "", self._md5_hash),
                ("🔑  SHA256 Hash",     "", self._sha256_hash),
                None,
                ("⚖  Diff with Clipboard", "", self._diff_clipboard),
            ]),
            ("View", [
                ("Font Size +",     "", lambda: self._change_font(+1)),
                ("Font Size -",     "", lambda: self._change_font(-1)),
                None,
                ("Toggle Line Numbers", "", self._toggle_line_numbers),
                ("Toggle Word Wrap",    "", self._toggle_word_wrap),
                ("Toggle Ruler",        "", self._toggle_ruler),
            ]),
        ]

        for menu_label, items in menus:
            btn = tk.Menubutton(
                mb, text=menu_label,
                bg=T["panel_bg"], fg=T["text"],
                relief="flat",
                font=(FONT_UI, 10),
                padx=10, pady=4,
                cursor="hand2",
                activebackground=T["menu_hover"],
                activeforeground=T["text"],
            )
            btn.pack(side="left")
            m = tk.Menu(
                btn, tearoff=0,
                bg=T["menu_bg"], fg=T["text"],
                activebackground=T["accent"],
                activeforeground=T["text_inverse"],
            )
            btn.config(menu=m)
            for item in items:
                if item is None:
                    m.add_separator()
                else:
                    lbl, accel, cmd = item
                    m.add_command(
                        label=lbl,
                        accelerator=accel if accel else "",
                        command=cmd,
                    )

    def _build_editor_area(self, parent: tk.Frame) -> None:
        area = tk.Frame(parent, bg=T["win_bg"])
        area.pack(fill="both", expand=True)

        # Line numbers canvas
        self._ln_canvas = tk.Canvas(
            area, width=52,
            bg=T["panel_alt"],
            highlightthickness=0,
        )
        self._ln_canvas.pack(side="left", fill="y")
        self._show_ln = True

        # Ruler (horizontal)
        self._ruler_frame = tk.Frame(area, bg=T["panel_alt"], height=16)
        # Not packed initially — toggled via menu

        # Main text area
        self.ed = ScrollText(
            area,
            wrap="none",
            hscroll=True,
            font=(FONT_MONO, self._font_size),
            undo=True,
            maxundo=200,
        )
        self.ed.pack(side="left", fill="both", expand=True)

        # Sync line numbers on scroll
        self.ed.text.bind("<KeyRelease>",   lambda e: self._update_ln())
        self.ed.text.bind("<MouseWheel>",   lambda e: self._update_ln())
        self.ed.text.bind("<Configure>",    lambda e: self._update_ln())
        self.ed.yview = lambda *a: (self.ed.text.yview(*a), self._update_ln())

        self._setup_syntax_tags()
        self._update_ln()

    def _build_statusbar(self, parent: tk.Frame) -> None:
        sf = tk.Frame(parent, bg=T["status_bg"], height=24)
        sf.pack(fill="x", side="bottom")
        sf.pack_propagate(False)

        self._st_path = tk.Label(
            sf, text=self.filepath or "Untitled",
            bg=T["status_bg"], fg=T["text_muted"],
            font=(FONT_UI, 8), anchor="w",
        )
        self._st_path.pack(side="left", padx=8)

        for attr, init_text in [
            ("_st_pos",  "Ln 1, Col 1"),
            ("_st_enc",  self._encoding),
            ("_st_lang", "Plain Text"),
            ("_st_wc",   "0 words"),
        ]:
            lbl = tk.Label(
                sf, text=init_text,
                bg=T["status_bg"], fg=T["text_muted"],
                font=(FONT_UI, 8),
            )
            lbl.pack(side="right", padx=8)
            setattr(self, attr, lbl)

        mksep(sf, "vertical").pack(side="right", fill="y", pady=4)

    # ── file operations ───────────────────────────────────────────────────────

    def _load_file(self) -> None:
        if self.filepath and self.wm.vfs.isfile(self.filepath):
            try:
                content = self.wm.vfs.read(self.filepath)
                self.ed.insert("1.0", content)
                self.ed.text.edit_modified(False)
                self._detect_language()
                self._highlight()
                self._update_ln()
            except Exception as ex:
                messagebox.showerror("Load Error", str(ex), parent=self.wm.root)

    def _detect_language(self) -> None:
        if not self.filepath:
            self._lang = "plain"
            return
        ext = self.filepath.rsplit(".", 1)[-1].lower() if "." in self.filepath else ""
        lang_map = {
            "py":"python", "pyw":"python",
            "js":"js", "ts":"js", "jsx":"js", "tsx":"js",
            "html":"html", "htm":"html",
            "css":"css",
            "json":"json",
            "sql":"sql",
            "sh":"bash", "bash":"bash", "zsh":"bash",
            "md":"markdown",
            "xml":"xml",
        }
        self._lang = lang_map.get(ext, "plain")
        lang_display = {
            "python":"Python","js":"JavaScript","html":"HTML",
            "css":"CSS","json":"JSON","sql":"SQL","bash":"Bash",
            "markdown":"Markdown","xml":"XML","plain":"Plain Text",
        }
        self._st_lang.config(text=lang_display.get(self._lang, "Plain Text"))

    def _new(self) -> None:
        if self.modified:
            if not messagebox.askyesno(
                "Unsaved Changes", "Discard changes?", parent=self.wm.root
            ):
                return
        self.ed.delete("1.0", "end")
        self.filepath = None
        self.modified = False
        self._lang    = "plain"
        self.set_title("Untitled — Editor")
        self._st_path.config(text="Untitled")

    def _open_vfs(self) -> None:
        path = simpledialog.askstring(
            "Open File", "VFS path:",
            parent=self.wm.root,
            initialvalue="/home/user/",
        )
        if path and self.wm.vfs.isfile(path):
            try:
                self.ed.delete("1.0", "end")
                self.ed.insert("1.0", self.wm.vfs.read(path))
                self.filepath = path
                self.modified = False
                self.ed.text.edit_modified(False)
                self.set_title(path.split("/")[-1] + " — Editor")
                self._st_path.config(text=path)
                self._detect_language()
                self._highlight()
                self._update_ln()
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self.wm.root)

    def _save(self) -> None:
        if not self.filepath:
            self._save_as()
            return
        try:
            content = self.ed.get("1.0", "end-1c")
            self.wm.vfs.write(self.filepath, content)
            self.modified = False
            self.ed.text.edit_modified(False)
            self.set_title(self.title.lstrip("*"))
            self.wm.notifs.send("Editor", f"Saved: {self.filepath}", icon="💾")
        except Exception as ex:
            messagebox.showerror("Save Error", str(ex), parent=self.wm.root)

    def _save_as(self) -> None:
        path = simpledialog.askstring(
            "Save As", "VFS path:",
            parent=self.wm.root,
            initialvalue=self.filepath or "/home/user/untitled.txt",
        )
        if path:
            self.filepath = path
            self._save()

    def _export(self) -> None:
        """Export content with line numbers to a new VFS file."""
        path = simpledialog.askstring(
            "Export", "Export to VFS path:",
            parent=self.wm.root,
            initialvalue="/home/user/Downloads/export.txt",
        )
        if path:
            content = self.ed.get("1.0", "end-1c")
            numbered = "\n".join(
                f"{i+1:4d}  {line}"
                for i, line in enumerate(content.split("\n"))
            )
            self.wm.vfs.write(path, numbered)
            self.wm.notifs.send("Editor", f"Exported to: {path}", icon="📤")

    # ── event handlers ────────────────────────────────────────────────────────

    def _on_modified(self, _: tk.Event) -> None:
        if self.ed.text.edit_modified():
            if not self.modified:
                self.modified = True
                if not self.title.startswith("*"):
                    self.set_title("*" + self.title)

    def _on_key(self, _: tk.Event) -> None:
        self._update_status()
        self._highlight()
        self._update_ln()

    def _update_status(self) -> None:
        try:
            idx  = self.ed.text.index("insert")
            line, col = idx.split(".")
            self._st_pos.config(text=f"Ln {line}, Col {int(col)+1}")
            content = self.ed.get("1.0", "end-1c")
            words   = len(content.split())
            self._st_wc.config(text=f"{words} words")
        except Exception:
            pass

    # ── line numbers ──────────────────────────────────────────────────────────

    def _update_ln(self) -> None:
        if not self._show_ln:
            return
        c = self._ln_canvas
        c.delete("all")
        try:
            i = self.ed.text.index("@0,0")
            while True:
                dli = self.ed.text.dlineinfo(i)
                if dli is None:
                    break
                y       = dli[1]
                linenum = int(str(i).split(".")[0])
                c.create_text(
                    48, y,
                    text=str(linenum),
                    anchor="ne",
                    fill=T["text_muted"],
                    font=(FONT_MONO, self._font_size - 1),
                )
                next_i = self.ed.text.index(f"{i}+1line")
                if next_i == i:
                    break
                i = next_i
        except Exception:
            pass

    def _toggle_line_numbers(self) -> None:
        self._show_ln = not self._show_ln
        if self._show_ln:
            self._ln_canvas.pack(side="left", fill="y", before=self.ed)
        else:
            self._ln_canvas.pack_forget()

    def _toggle_word_wrap(self) -> None:
        cur = self.ed.text.cget("wrap")
        self.ed.text.config(wrap="none" if cur == "word" else "word")

    def _toggle_ruler(self) -> None:
        col = self.wm.settings.get("editor_ruler_col", 80)
        # Draw a vertical line on the canvas overlay
        # (simplified: just show a label in the status bar)
        current = self._st_lang.cget("text")
        if "col:" not in current:
            self._st_lang.config(text=f"{current} | col:{col}")
        else:
            self._st_lang.config(text=current.split(" | col:")[0])

    def _change_font(self, delta: int) -> None:
        self._font_size = max(6, min(32, self._font_size + delta))
        self.ed.text.config(font=(FONT_MONO, self._font_size))
        self._update_ln()

    # ── syntax highlighting ───────────────────────────────────────────────────

    def _setup_syntax_tags(self) -> None:
        t = self.ed.text
        t.tag_configure("kw",       foreground="#569cd6")
        t.tag_configure("builtin",  foreground="#4ec9b0")
        t.tag_configure("string",   foreground="#ce9178")
        t.tag_configure("comment",  foreground="#6a9955",
                        font=(FONT_MONO, self._font_size, "italic"))
        t.tag_configure("number",   foreground="#b5cea8")
        t.tag_configure("func",     foreground="#dcdcaa")
        t.tag_configure("class_",   foreground="#4ec9b0")
        t.tag_configure("decorator",foreground="#c586c0")
        t.tag_configure("tag",      foreground="#4ec9b0")
        t.tag_configure("attr",     foreground="#9cdcfe")
        t.tag_configure("bool_",    foreground="#569cd6")
        t.tag_configure("operator", foreground="#d4d4d4")
        t.tag_configure("bracket",  foreground="#ffd700")

    def _highlight(self) -> None:
        """Apply syntax highlighting for the current language."""
        if self._lang == "plain":
            return
        t    = self.ed.text
        text = t.get("1.0", "end")

        # Clear all syntax tags
        for tag in ("kw","builtin","string","comment","number",
                    "func","class_","decorator","tag","attr","bool_",
                    "operator","bracket"):
            t.tag_remove(tag, "1.0", "end")

        if self._lang == "python":
            self._hl_python(t, text)
        elif self._lang == "js":
            self._hl_js(t, text)
        elif self._lang == "html":
            self._hl_html(t, text)
        elif self._lang == "json":
            self._hl_json(t, text)
        elif self._lang == "sql":
            self._hl_sql(t, text)
        elif self._lang == "bash":
            self._hl_bash(t, text)

    def _apply_pattern(
        self,
        t:       tk.Text,
        pattern: str,
        tag:     str,
        flags:   int = 0,
        group:   int = 0,
    ) -> None:
        for m in re.finditer(pattern, t.get("1.0", "end"), flags):
            start_c = m.start(group)
            end_c   = m.end(group)
            start   = f"1.0+{start_c}c"
            end     = f"1.0+{end_c}c"
            t.tag_add(tag, start, end)

    def _hl_python(self, t: tk.Text, text: str) -> None:
        # Keywords
        kw_pat = r'\b(' + '|'.join(re.escape(k) for k in self._KEYWORDS["python"]) + r')\b'
        self._apply_pattern(t, kw_pat, "kw")

        # Builtins
        bi_pat = r'\b(' + '|'.join(re.escape(k) for k in self._KEYWORDS["python_builtins"]) + r')\b'
        self._apply_pattern(t, bi_pat, "builtin")

        # Strings (triple-quoted first, then single/double)
        for pat in [r'"""[\s\S]*?"""', r"'''[\s\S]*?'''",
                    r'"(?:[^"\\]|\\.)*"', r"'(?:[^'\\]|\\.)*'"]:
            self._apply_pattern(t, pat, "string", re.DOTALL)

        # Comments
        self._apply_pattern(t, r'#[^\n]*', "comment")

        # Numbers
        self._apply_pattern(t, r'\b\d+\.?\d*([eE][+-]?\d+)?[jJ]?\b', "number")

        # Function definitions
        self._apply_pattern(t, r'\bdef\s+(\w+)', "func", group=1)

        # Class definitions
        self._apply_pattern(t, r'\bclass\s+(\w+)', "class_", group=1)

        # Decorators
        self._apply_pattern(t, r'@\w+', "decorator")

    def _hl_js(self, t: tk.Text, text: str) -> None:
        kw_pat = r'\b(' + '|'.join(re.escape(k) for k in self._KEYWORDS["js"]) + r')\b'
        self._apply_pattern(t, kw_pat, "kw")
        # Strings
        for pat in [r'`[\s\S]*?`', r'"(?:[^"\\]|\\.)*"', r"'(?:[^'\\]|\\.)*'"]:
            self._apply_pattern(t, pat, "string", re.DOTALL)
        # Comments
        self._apply_pattern(t, r'//[^\n]*', "comment")
        self._apply_pattern(t, r'/\*[\s\S]*?\*/', "comment", re.DOTALL)
        # Numbers
        self._apply_pattern(t, r'\b\d+\.?\d*\b', "number")
        # Functions
        self._apply_pattern(t, r'\bfunction\s+(\w+)', "func", group=1)
        self._apply_pattern(t, r'(\w+)\s*\(', "func", group=1)

    def _hl_html(self, t: tk.Text, text: str) -> None:
        self._apply_pattern(t, r'<!--[\s\S]*?-->', "comment", re.DOTALL)
        self._apply_pattern(t, r'</?(\w+)', "tag", group=1)
        self._apply_pattern(t, r'\s(\w+)=', "attr", group=1)
        self._apply_pattern(t, r'"[^"]*"', "string")
        self._apply_pattern(t, r"'[^']*'", "string")

    def _hl_json(self, t: tk.Text, text: str) -> None:
        self._apply_pattern(t, r'"(?:[^"\\]|\\.)*"\s*:', "func")
        self._apply_pattern(t, r'"(?:[^"\\]|\\.)*"', "string")
        self._apply_pattern(t, r'\b(true|false|null)\b', "kw")
        self._apply_pattern(t, r'\b-?\d+\.?\d*([eE][+-]?\d+)?\b', "number")

    def _hl_sql(self, t: tk.Text, text: str) -> None:
        kw_pat = r'\b(' + '|'.join(re.escape(k) for k in self._KEYWORDS["sql"]) + r')\b'
        self._apply_pattern(t, kw_pat, "kw", re.IGNORECASE)
        self._apply_pattern(t, r"'[^']*'", "string")
        self._apply_pattern(t, r'--[^\n]*', "comment")
        self._apply_pattern(t, r'/\*[\s\S]*?\*/', "comment", re.DOTALL)
        self._apply_pattern(t, r'\b\d+\.?\d*\b', "number")

    def _hl_bash(self, t: tk.Text, text: str) -> None:
        bash_kw = ["if","then","else","elif","fi","for","while","do","done",
                   "case","esac","function","in","until","select","time",
                   "echo","exit","return","export","source","alias","unset",
                   "readonly","local","declare","typeset","shift","eval",
                   "exec","read","set","unset","trap","wait","kill","jobs"]
        kw_pat = r'\b(' + '|'.join(re.escape(k) for k in bash_kw) + r')\b'
        self._apply_pattern(t, kw_pat, "kw")
        self._apply_pattern(t, r'#[^\n]*', "comment")
        for pat in [r'"(?:[^"\\]|\\.)*"', r"'[^']*'"]:
            self._apply_pattern(t, pat, "string")
        self._apply_pattern(t, r'\$\w+|\$\{[^}]+\}', "builtin")

    # ── Find / Replace ────────────────────────────────────────────────────────

    def _find_bar(self) -> None:
        d = tk.Toplevel(self.wm.root)
        d.title("Find")
        d.config(bg=T["win_bg"])
        d.geometry("420x110")
        d.wm_attributes("-topmost", True)
        d.resizable(False, False)

        f = tk.Frame(d, bg=T["win_bg"])
        f.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(f, text="Find:", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(side="left")
        fv  = tk.StringVar()
        fe  = mkentry(f, textvariable=fv, width=26)
        fe.pack(side="left", padx=6)

        ci_var = tk.BooleanVar(value=False)
        tk.Checkbutton(f, text="Aa", variable=ci_var,
                       bg=T["win_bg"], fg=T["text"],
                       selectcolor=T["accent"],
                       activebackground=T["win_bg"],
                       font=(FONT_UI, 9)).pack(side="left", padx=4)

        cnt_lbl = tk.Label(f, text="", bg=T["win_bg"],
                           fg=T["text_muted"], font=(FONT_UI, 9))
        cnt_lbl.pack(side="left", padx=4)

        def find_all() -> None:
            term  = fv.get()
            if not term:
                return
            flags = re.IGNORECASE if ci_var.get() else 0
            self.ed.tag_remove("sel", "1.0", "end")
            start = "1.0"
            count = 0
            while True:
                pos = self.ed.text.search(
                    term, start, stopindex="end",
                    nocase=ci_var.get(), regexp=False,
                )
                if not pos:
                    break
                end2 = f"{pos}+{len(term)}c"
                self.ed.tag_add("sel", pos, end2)
                start = end2
                count += 1
            self.ed.text.tag_configure("sel", background=T["selection"])
            cnt_lbl.config(text=f"{count} found")
            if count:
                first = self.ed.text.search(term, "1.0", nocase=ci_var.get())
                if first:
                    self.ed.see(first)

        def find_next() -> None:
            term = fv.get()
            if not term:
                return
            cur_pos = self.ed.text.index("insert")
            pos     = self.ed.text.search(
                term, f"{cur_pos}+1c",
                nocase=ci_var.get(),
            )
            if not pos:
                pos = self.ed.text.search(term, "1.0", nocase=ci_var.get())
            if pos:
                self.ed.text.mark_set("insert", pos)
                self.ed.see(pos)

        bf = tk.Frame(d, bg=T["win_bg"])
        bf.pack(fill="x", padx=12, pady=4)
        mkbtn(bf, "Find All",  find_all,  kind="accent").pack(side="left", padx=4)
        mkbtn(bf, "Find Next", find_next).pack(side="left", padx=4)
        mkbtn(bf, "Close",     d.destroy).pack(side="left", padx=4)

        fe.focus_set()
        fe.bind("<Return>", lambda e: find_next())

    def _find_replace(self) -> None:
        d = tk.Toplevel(self.wm.root)
        d.title("Find & Replace")
        d.config(bg=T["win_bg"])
        d.geometry("440x165")
        d.wm_attributes("-topmost", True)
        d.resizable(False, False)

        entries: List[tk.Entry] = []
        for lbl in ["Find:", "Replace:"]:
            row = tk.Frame(d, bg=T["win_bg"])
            row.pack(fill="x", padx=12, pady=5)
            tk.Label(row, text=lbl, bg=T["win_bg"], fg=T["text"],
                     font=(FONT_UI, 10), width=9, anchor="e").pack(side="left")
            e = mkentry(row, width=30)
            e.pack(side="left", padx=6)
            entries.append(e)

        info_lbl = tk.Label(d, text="", bg=T["win_bg"],
                            fg=T["text_muted"], font=(FONT_UI, 9))
        info_lbl.pack()

        def replace_all() -> None:
            find, repl = entries[0].get(), entries[1].get()
            content    = self.ed.get("1.0", "end-1c")
            count      = content.count(find)
            new_content = content.replace(find, repl)
            self.ed.delete("1.0", "end")
            self.ed.insert("1.0", new_content)
            info_lbl.config(text=f"Replaced {count} occurrence(s)")

        def replace_next() -> None:
            find, repl = entries[0].get(), entries[1].get()
            pos = self.ed.text.search(find, "insert")
            if pos:
                end2 = f"{pos}+{len(find)}c"
                self.ed.text.delete(pos, end2)
                self.ed.text.insert(pos, repl)
                info_lbl.config(text=f"Replaced at {pos}")

        bf = tk.Frame(d, bg=T["win_bg"])
        bf.pack(fill="x", padx=12, pady=6)
        mkbtn(bf, "Replace All",  replace_all,  kind="accent").pack(side="left", padx=4)
        mkbtn(bf, "Replace Next", replace_next).pack(side="left", padx=4)
        mkbtn(bf, "Close",        d.destroy).pack(side="left", padx=4)

        entries[0].focus_set()

    # ── Edit helpers ──────────────────────────────────────────────────────────

    def _select_all(self) -> None:
        self.ed.text.tag_add("sel", "1.0", "end")

    def _clear_all(self) -> None:
        self.ed.delete("1.0", "end")

    def _handle_tab(self, _: tk.Event) -> str:
        tab_w = self.wm.settings.get("editor_tab_width", 4)
        self.ed.text.insert("insert", " " * tab_w)
        return "break"

    def _handle_return(self, _: tk.Event) -> Optional[str]:
        if not self.wm.settings.get("editor_auto_indent", True):
            return None
        idx  = self.ed.text.index("insert")
        line = self.ed.text.get(f"{idx} linestart", idx)
        indent = ""
        for ch in line:
            if ch in (" ", "\t"):
                indent += ch
            else:
                break
        # Extra indent after colon
        if line.rstrip().endswith(":"):
            indent += " " * self.wm.settings.get("editor_tab_width", 4)
        self.ed.text.insert("insert", "\n" + indent)
        return "break"

    # ── Format operations ─────────────────────────────────────────────────────

    def _get_selection_or_all(self) -> str:
        try:
            return self.ed.text.get("sel.first", "sel.last")
        except tk.TclError:
            return self.ed.get("1.0", "end-1c")

    def _replace_selection_or_all(self, new_text: str) -> None:
        try:
            self.ed.text.delete("sel.first", "sel.last")
            self.ed.text.insert("insert", new_text)
        except tk.TclError:
            self.ed.delete("1.0", "end")
            self.ed.insert("1.0", new_text)

    def _transform_sel(self, mode: str) -> None:
        text = self._get_selection_or_all()
        transformed = {
            "upper": text.upper(),
            "lower": text.lower(),
            "title": text.title(),
        }[mode]
        self._replace_selection_or_all(transformed)

    def _sort_lines(self, reverse: bool) -> None:
        text  = self._get_selection_or_all()
        lines = sorted(text.split("\n"), reverse=reverse)
        self._replace_selection_or_all("\n".join(lines))

    def _remove_duplicates(self) -> None:
        text  = self._get_selection_or_all()
        seen  = set()
        lines = []
        for line in text.split("\n"):
            if line not in seen:
                seen.add(line)
                lines.append(line)
        self._replace_selection_or_all("\n".join(lines))

    def _remove_blank(self) -> None:
        text  = self._get_selection_or_all()
        lines = [l for l in text.split("\n") if l.strip()]
        self._replace_selection_or_all("\n".join(lines))

    def _trim_whitespace(self) -> None:
        text  = self._get_selection_or_all()
        lines = [l.rstrip() for l in text.split("\n")]
        self._replace_selection_or_all("\n".join(lines))

    def _add_line_nums(self) -> None:
        text  = self._get_selection_or_all()
        lines = [f"{i+1:4d}  {l}" for i, l in enumerate(text.split("\n"))]
        self._replace_selection_or_all("\n".join(lines))

    def _reverse_lines(self) -> None:
        text  = self._get_selection_or_all()
        lines = text.split("\n")[::-1]
        self._replace_selection_or_all("\n".join(lines))

    # ── Tools ─────────────────────────────────────────────────────────────────

    def _word_count(self) -> None:
        text  = self.ed.get("1.0", "end-1c")
        words = len(text.split())
        lines = text.count("\n") + 1
        chars = len(text)
        chars_no_sp = len(text.replace(" ", "").replace("\n", ""))
        messagebox.showinfo(
            "Word Count",
            f"Words:              {words:,}\n"
            f"Lines:              {lines:,}\n"
            f"Characters:         {chars:,}\n"
            f"Characters (no sp): {chars_no_sp:,}",
            parent=self.wm.root,
        )

    def _char_freq(self) -> None:
        text = self.ed.get("1.0", "end-1c")
        freq: Dict[str, int] = {}
        for ch in text:
            freq[ch] = freq.get(ch, 0) + 1
        top = sorted(freq.items(), key=lambda x: -x[1])[:15]

        d = tk.Toplevel(self.wm.root)
        d.title("Character Frequency")
        d.config(bg=T["win_bg"])
        d.geometry("320x360")

        tk.Label(d, text="Top 15 Characters",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 11, "bold")).pack(pady=(10,4))

        for i, (ch, cnt) in enumerate(top):
            bg  = T["win_bg"] if i % 2 == 0 else T["panel_bg"]
            row = tk.Frame(d, bg=bg)
            row.pack(fill="x", padx=12)
            display = repr(ch) if ch in ("\n","\t"," ") else ch
            tk.Label(row, text=f"{display}",
                     bg=bg, fg=T["text"],
                     font=(FONT_MONO, 10), width=6).pack(side="left", pady=3)
            # Bar
            bar_w = max(4, int(cnt * 150 / max(c for _,c in top)))
            tk.Frame(row, bg=T["accent"],
                     width=bar_w, height=12).pack(side="left", padx=4)
            tk.Label(row, text=str(cnt),
                     bg=bg, fg=T["text_muted"],
                     font=(FONT_MONO, 9)).pack(side="left", padx=6)

        mkbtn(d, "Close", d.destroy).pack(pady=8)

    def _run_python(self) -> None:
        code = self.ed.get("1.0", "end-1c")
        import io as _io
        old_stdout = sys.stdout
        buf        = _io.StringIO()
        sys.stdout = buf
        error_msg  = None
        try:
            exec(compile(code, self.filepath or "<editor>", "exec"), {})
        except Exception as ex:
            error_msg = traceback.format_exc()
        finally:
            sys.stdout = old_stdout

        output = buf.getvalue()

        d = tk.Toplevel(self.wm.root)
        d.title("Script Output")
        d.config(bg=T["win_bg"])
        d.geometry("560x340")

        tk.Label(d, text="▶ Script Output",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10, "bold")).pack(anchor="w", padx=10, pady=(8,2))

        out_text = ScrollText(d, font=(FONT_MONO, 10), wrap="word")
        out_text.pack(fill="both", expand=True, padx=10, pady=4)

        if error_msg:
            out_text.text.config(fg=T["danger"])
            out_text.insert("1.0", error_msg)
        else:
            out_text.text.config(fg=T["success"])
            out_text.insert("1.0", output if output else "(no output)")

        out_text.text.config(state="disabled")
        mkbtn(d, "Close", d.destroy).pack(pady=6)

    def _encode_b64(self) -> None:
        text = self._get_selection_or_all()
        enc  = base64.b64encode(text.encode()).decode()
        self._replace_selection_or_all(enc)

    def _decode_b64(self) -> None:
        text = self._get_selection_or_all().strip()
        try:
            dec = base64.b64decode(text.encode()).decode()
            self._replace_selection_or_all(dec)
        except Exception:
            messagebox.showerror("Error", "Invalid Base64 input.", parent=self.wm.root)

    def _md5_hash(self) -> None:
        text = self._get_selection_or_all()
        h    = hashlib.md5(text.encode()).hexdigest()
        messagebox.showinfo("MD5 Hash", h, parent=self.wm.root)

    def _sha256_hash(self) -> None:
        text = self._get_selection_or_all()
        h    = hashlib.sha256(text.encode()).hexdigest()
        messagebox.showinfo("SHA-256 Hash", h, parent=self.wm.root)

    def _diff_clipboard(self) -> None:
        import difflib
        a     = self.ed.get("1.0", "end-1c").split("\n")
        b     = self.wm.clip.paste_text().split("\n")

        d = tk.Toplevel(self.wm.root)
        d.title("Diff — Editor vs Clipboard")
        d.config(bg=T["win_bg"])
        d.geometry("640x420")

        out = ScrollText(d, font=(FONT_MONO, 10), wrap="none")
        out.pack(fill="both", expand=True, padx=8, pady=8)
        out.tag_configure("add", background="#1a3a1a", foreground=T["success"])
        out.tag_configure("rem", background="#3a1a1a", foreground=T["danger"])
        out.tag_configure("inf", foreground=T["text_muted"])

        for line in difflib.unified_diff(a, b, fromfile="editor", tofile="clipboard", lineterm=""):
            if line.startswith("+"):
                out.insert("end", line + "\n", "add")
            elif line.startswith("-"):
                out.insert("end", line + "\n", "rem")
            else:
                out.insert("end", line + "\n", "inf")

        out.text.config(state="disabled")
        mkbtn(d, "Close", d.destroy).pack(pady=6)

    # ── window lifecycle ──────────────────────────────────────────────────────

    def on_close(self) -> None:
        if self.modified:
            if messagebox.askyesno(
                "Unsaved Changes",
                f"Save changes to '{self.title.lstrip('*')}'?",
                parent=self.wm.root,
            ):
                self._save()

    def on_focus(self) -> None:
        self.ed.text.focus_set()


# =============================================================================
#  END OF PART 2 (lines 2001-4000)
#  Defines: WM, Taskbar, StartMenu, NotifPanel, VolumePanel,
#           FileManagerApp, TextEditorApp
#
#  Part 3 will cover: TerminalApp, BrowserApp, MusicPlayerApp, PaintApp
#  Part 4 will cover: CalculatorApp, ClockApp, TaskManagerApp, NotesApp, EmailApp
#  Part 5 will cover: PasswordManagerApp, SpreadsheetApp, ImageViewerApp,
#                     DiskAnalyzerApp, CodeRunnerApp, ArchiveManagerApp
#  Part 6 will cover: AppStoreApp, SystemMonitorApp, SettingsApp,
#                     Login/Lock screens, Boot animation, main() entry point
# =============================================================================

if __name__ == "__main__":
    print(f"PyOS v{PYOS_VERSION} — Part 2 loaded (WM + core apps).")
    print("Combine Part 1 + Part 2 + … for the full OS.")
    #!/usr/bin/env python3
# =============================================================================
#  PyOS v5.0 — PART 3
#  Sections: Terminal App (60+ commands), Browser App,
#            Music Player App, Paint Studio App
#  Requires: Part 1 + Part 2 concatenated before this
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 17 — TERMINAL APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class TerminalApp(BaseWin):
    """
    Full-featured terminal emulator with:
      • 60+ built-in shell commands
      • Command history (↑/↓ navigation)
      • Tab completion (paths + commands)
      • Pipe operator  |
      • Redirection    > >>
      • Environment variables  $VAR, export, unset
      • ANSI-style colour tags
      • Scrollback buffer
      • Multiple colour themes
      • Configurable font size
      • Copy selection to clipboard
      • Inline Python execution
      • Job-like background tasks (simulated)
    """

    # Colour tag names → theme colours
    PROMPT_CLR  = "#4ec9b0"
    ERROR_CLR   = "#f85149"
    SUCCESS_CLR = "#3fb950"
    INFO_CLR    = "#58a6ff"
    WARN_CLR    = "#d29922"
    DIM_CLR     = "#484f58"

    # All recognised built-in command names (used for tab-complete)
    BUILTINS = {
        "help","ls","ll","la","dir","cd","pwd","cat","head","tail","wc",
        "echo","printf","mkdir","rmdir","rm","del","cp","mv","touch","ln",
        "find","grep","sort","uniq","diff","patch","sed","awk","tr","cut",
        "rev","tee","xargs","base64","tree","stat","file","du","df","quota",
        "ps","top","kill","killall","nice","jobs","bg","fg","wait","nohup",
        "uname","uptime","hostname","whoami","id","groups","who","w","last",
        "date","cal","time","sleep","seq","yes","false","true",
        "env","export","unset","set","source","alias","unalias","history",
        "clear","reset","exit","quit","logout",
        "python","python3","sh","bash",
        "ping","curl","wget","ssh","nc","netstat","ifconfig","ip","dig","nslookup",
        "bc","expr","factor","primes",
        "zip","unzip","tar","gzip","gunzip","bzip2","bunzip2",
        "md5sum","sha256sum","openssl","gpg",
        "which","whereis","locate","updatedb",
        "man","info","help",
        "open","edit","view","less","more",
        "write","append","read","prompt",
        "sysinfo","version","credits","fortune","cowsay","matrix","lolcat",
        "banner","figlet",
    }

    def __init__(self, wm: WM) -> None:
        self._hist:    List[str] = []
        self._hist_pos = -1
        self._env: Dict[str, str] = {
            "HOME":    "/home/user",
            "USER":    wm.users.current or "user",
            "SHELL":   "/bin/sh",
            "TERM":    "pyos-256color",
            "EDITOR":  "editor",
            "PAGER":   "less",
            "PWD":     "/home/user",
            "OLDPWD":  "/home/user",
            "PATH":    "/usr/bin:/bin:/usr/local/bin",
            "LANG":    "en_US.UTF-8",
            "COLUMNS": "80",
            "LINES":   "24",
        }
        self._aliases: Dict[str, str] = {
            "ll": "ls -la",
            "la": "ls -a",
            "cls": "clear",
            "..": "cd ..",
            "...": "cd ../..",
            "grep": "grep --color=auto",
        }
        super().__init__(
            wm, "Terminal", 200, 80, 860, 560, "💻",
            min_w=400, min_h=200,
        )

    # ── UI construction ───────────────────────────────────────────────────────

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg="#0c0c0c")

        # Toolbar
        tb = tk.Frame(parent, bg="#1a1a2e", height=32)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        for txt, cmd, tip in [
            ("＋ New Tab",  self._new_tab,   "Open a new terminal"),
            ("⎘  Copy",    self._copy_sel,  "Copy selection"),
            ("⌫  Clear",   self._clear,     "Clear screen  Ctrl+L"),
            ("⚙",          self._term_cfg,  "Terminal settings"),
        ]:
            b = tk.Button(
                tb, text=txt, command=cmd,
                bg="#1a1a2e", fg="#7d8590",
                relief="flat", bd=0,
                font=(FONT_UI, 9), padx=8,
                cursor="hand2",
                activebackground="#21262d",
                activeforeground="#e6edf3",
            )
            b.pack(side="left", fill="y", padx=1)
            Tooltip(b, tip)

        # Output pane
        self.out = tk.Text(
            parent,
            bg="#0c0c0c", fg="#e6edf3",
            font=(FONT_MONO, self.wm.settings.get("terminal_font_size", 10)),
            insertbackground="#e6edf3",
            wrap="word",
            relief="flat", bd=0,
            padx=10, pady=6,
            selectbackground=T["selection"],
            selectforeground="#e6edf3",
            state="disabled",
        )
        vsb = tk.Scrollbar(parent, orient="vertical", command=self.out.yview)
        self.out.config(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.out.pack(side="top", fill="both", expand=True)

        # Input bar
        inp = tk.Frame(parent, bg="#161b22")
        inp.pack(fill="x", side="bottom")

        self._prompt_lbl = tk.Label(
            inp,
            text=self._get_prompt(),
            bg="#161b22", fg=self.PROMPT_CLR,
            font=(FONT_MONO, self.wm.settings.get("terminal_font_size", 10), "bold"),
            padx=6,
        )
        self._prompt_lbl.pack(side="left")

        self._cmd_var = tk.StringVar()
        self._cmd_entry = tk.Entry(
            inp,
            textvariable=self._cmd_var,
            bg="#161b22", fg="#e6edf3",
            insertbackground="#e6edf3",
            relief="flat",
            font=(FONT_MONO, self.wm.settings.get("terminal_font_size", 10)),
            bd=0,
        )
        self._cmd_entry.pack(side="left", fill="x", expand=True, padx=4, pady=7)

        # Bindings
        self._cmd_entry.bind("<Return>",     self._execute)
        self._cmd_entry.bind("<Up>",         self._hist_up)
        self._cmd_entry.bind("<Down>",       self._hist_down)
        self._cmd_entry.bind("<Tab>",        self._tab_complete)
        self._cmd_entry.bind("<Control-c>",  self._ctrl_c)
        self._cmd_entry.bind("<Control-l>",  lambda e: self._clear())
        self._cmd_entry.bind("<Control-u>",  lambda e: self._cmd_var.set(""))
        self._cmd_entry.bind("<Control-a>",  lambda e: self._cmd_entry.icursor("end"))
        self._cmd_entry.focus_set()

        # Configure output tags
        self._setup_tags()
        self._print_banner()

    def _setup_tags(self) -> None:
        t = self.out
        t.tag_configure("prompt",  foreground=self.PROMPT_CLR,
                        font=(FONT_MONO, self.wm.settings.get("terminal_font_size",10), "bold"))
        t.tag_configure("error",   foreground=self.ERROR_CLR)
        t.tag_configure("success", foreground=self.SUCCESS_CLR)
        t.tag_configure("info",    foreground=self.INFO_CLR)
        t.tag_configure("warn",    foreground=self.WARN_CLR)
        t.tag_configure("dim",     foreground=self.DIM_CLR)
        t.tag_configure("bold",    font=(FONT_MONO, self.wm.settings.get("terminal_font_size",10), "bold"))
        t.tag_configure("link",    foreground=T["link"],
                        font=(FONT_MONO, self.wm.settings.get("terminal_font_size",10), "underline"))
        t.tag_configure("dir_",    foreground=self.INFO_CLR)
        t.tag_configure("exe_",    foreground=self.SUCCESS_CLR)
        t.tag_configure("hdr",     foreground=self.WARN_CLR,
                        font=(FONT_MONO, self.wm.settings.get("terminal_font_size",10), "bold"))

    def _print_banner(self) -> None:
        self._write("""
 ██████╗ ██╗   ██╗ ██████╗ ███████╗
 ██╔══██╗╚██╗ ██╔╝██╔═══██╗██╔════╝
 ██████╔╝ ╚████╔╝ ██║   ██║███████╗
 ██╔═══╝   ╚██╔╝  ██║   ██║╚════██║
 ██║        ██║   ╚██████╔╝███████║
 ╚═╝        ╚═╝    ╚═════╝ ╚══════╝\n""", "info")
        self._write(
            f"  PyOS {PYOS_VERSION}  •  Terminal  •  "
            f"{datetime.datetime.now():%Y-%m-%d %H:%M}  •  type 'help'\n\n",
            "dim",
        )

    # ── output helpers ────────────────────────────────────────────────────────

    def _write(self, text: str, tag: str = "") -> None:
        self.out.config(state="normal")
        if tag:
            self.out.insert("end", text, tag)
        else:
            self.out.insert("end", text)
        self.out.see("end")
        self.out.config(state="disabled")

    def _writeln(self, text: str = "", tag: str = "") -> None:
        self._write(text + "\n", tag)

    def _err(self, msg: str)  -> None: self._writeln(msg, "error")
    def _ok(self, msg: str)   -> None: self._writeln(msg, "success")
    def _info(self, msg: str) -> None: self._writeln(msg, "info")
    def _dim(self, msg: str)  -> None: self._writeln(msg, "dim")
    def _warn(self, msg: str) -> None: self._writeln(msg, "warn")

    def _get_prompt(self) -> str:
        cwd  = self.wm.vfs.cwd
        home = "/home/user"
        short = "~" + cwd[len(home):] if cwd.startswith(home) else cwd
        user  = self.wm.users.current or "user"
        return f"{user}@pyos:{short}$ "

    def _update_prompt(self) -> None:
        self._prompt_lbl.config(text=self._get_prompt())
        self._env["PWD"] = self.wm.vfs.cwd

    # ── input handling ────────────────────────────────────────────────────────

    def _execute(self, _: tk.Event = None) -> None:
        raw = self._cmd_var.get().strip()
        self._cmd_var.set("")
        if not raw:
            return
        # Record history
        if not self._hist or self._hist[-1] != raw:
            self._hist.append(raw)
        self._hist_pos = len(self._hist)
        # Echo command
        self.out.config(state="normal")
        self.out.insert("end", self._get_prompt(), "prompt")
        self.out.insert("end", raw + "\n")
        self.out.see("end")
        self.out.config(state="disabled")
        # Execute
        self._dispatch(raw)
        self._update_prompt()

    def _hist_up(self, _: tk.Event) -> str:
        if self._hist and self._hist_pos > 0:
            self._hist_pos -= 1
            self._cmd_var.set(self._hist[self._hist_pos])
            self._cmd_entry.icursor("end")
        return "break"

    def _hist_down(self, _: tk.Event) -> str:
        if self._hist_pos < len(self._hist) - 1:
            self._hist_pos += 1
            self._cmd_var.set(self._hist[self._hist_pos])
        else:
            self._hist_pos = len(self._hist)
            self._cmd_var.set("")
        return "break"

    def _tab_complete(self, _: tk.Event) -> str:
        partial = self._cmd_var.get()
        parts   = partial.split()
        if not parts:
            return "break"
        last = parts[-1]

        # Command completion (first token)
        if len(parts) == 1 and not partial.endswith(" "):
            matches = sorted(c for c in self.BUILTINS if c.startswith(last))
            if len(matches) == 1:
                self._cmd_var.set(matches[0] + " ")
                self._cmd_entry.icursor("end")
            elif len(matches) > 1:
                self._writeln("")
                self._write("  ".join(matches) + "\n", "dim")
            return "break"

        # Path completion
        if "/" in last:
            dir_part  = "/".join(last.split("/")[:-1]) or "/"
            file_part = last.split("/")[-1]
        else:
            dir_part  = self.wm.vfs.cwd
            file_part = last

        try:
            entries  = self.wm.vfs.listdir(dir_part)
            matches  = [e for e in entries if e.startswith(file_part)]
            if len(matches) == 1:
                comp = matches[0]
                full = (dir_part.rstrip("/") + "/" + comp
                        if "/" in last else comp)
                new_parts = parts[:-1] + [full]
                self._cmd_var.set(" ".join(new_parts))
                self._cmd_entry.icursor("end")
            elif len(matches) > 1:
                self._writeln("")
                self._write("  ".join(matches) + "\n", "dim")
        except Exception:
            pass
        return "break"

    def _ctrl_c(self, _: tk.Event) -> None:
        self._write("^C\n", "error")
        self._cmd_var.set("")

    # ── command dispatcher ────────────────────────────────────────────────────

    def _dispatch(self, line: str) -> None:
        """Parse and run a command line (handles pipes, redirection, aliases)."""
        # Alias substitution
        parts = line.split()
        if parts and parts[0] in self._aliases:
            line = self._aliases[parts[0]] + (" " + " ".join(parts[1:]) if len(parts) > 1 else "")

        # Redirection  >>
        if ">>" in line and ">" not in line.replace(">>", ""):
            cmd_part, file_part = line.split(">>", 1)
            out = self._run_cmd(cmd_part.strip(), capture=True)
            if out is not None:
                self.wm.vfs.write(file_part.strip(), out, append=True)
            return

        # Redirection  >
        if ">" in line:
            cmd_part, file_part = line.split(">", 1)
            out = self._run_cmd(cmd_part.strip(), capture=True)
            if out is not None:
                self.wm.vfs.write(file_part.strip(), out)
            return

        # Pipe
        if "|" in line:
            segments = [s.strip() for s in line.split("|")]
            data = ""
            for seg in segments:
                data = self._run_cmd(seg, stdin=data, capture=True) or ""
            if data:
                self._write(data)
            return

        # Semicolon-separated commands
        if ";" in line:
            for part in line.split(";"):
                part = part.strip()
                if part:
                    self._run_cmd(part)
            return

        self._run_cmd(line)

    def _run_cmd(
        self,
        line:    str,
        stdin:   str = "",
        capture: bool = False,
    ) -> Optional[str]:
        """Execute one command. Returns output string when capture=True."""
        parts = line.split()
        if not parts:
            return ""
        cmd  = parts[0]
        args = parts[1:]

        # Expand $VAR references
        expanded_args: List[str] = []
        for a in args:
            if a.startswith("$"):
                key = a[1:].strip("{}")
                expanded_args.append(self._env.get(key, ""))
            else:
                expanded_args.append(a)
        args = expanded_args

        buf: List[str] = []

        def o(text: str, tag: str = "") -> None:
            if capture:
                buf.append(text)
            else:
                self._write(text, tag)

        def ol(text: str = "", tag: str = "") -> None:
            o(text + "\n", tag)

        vfs = self.wm.vfs
        cwd = vfs.cwd

        try:
            # ── NAVIGATION ────────────────────────────────────────────────────
            if cmd == "cd":
                target = args[0] if args else self._env.get("HOME", "/home/user")
                if target == "-":
                    target = self._env.get("OLDPWD", cwd)
                resolved = vfs.resolve(target)
                if not vfs.isdir(resolved):
                    ol(f"cd: {target}: No such directory", "error")
                else:
                    self._env["OLDPWD"] = cwd
                    vfs.cwd = resolved

            elif cmd == "pwd":
                ol(cwd)

            elif cmd == "pushd":
                target = args[0] if args else self._env.get("HOME", "/home/user")
                resolved = vfs.resolve(target)
                if vfs.isdir(resolved):
                    self._env["OLDPWD"] = cwd
                    vfs.cwd = resolved
                    ol(resolved)
                else:
                    ol(f"pushd: {target}: No such directory", "error")

            elif cmd == "popd":
                old = self._env.get("OLDPWD", "/home/user")
                vfs.cwd = old
                ol(old)

            # ── LISTING ───────────────────────────────────────────────────────
            elif cmd in ("ls", "ll", "la", "dir"):
                path     = next((a for a in args if not a.startswith("-")), cwd)
                path     = vfs.resolve(path)
                long_fmt = "-l" in args or cmd in ("ll", "la")
                show_hid = "-a" in args or cmd == "la"
                try:
                    names = vfs.listdir(path)
                except Exception as ex:
                    ol(f"ls: {ex}", "error"); return "".join(buf) if capture else None

                for name in names:
                    if not show_hid and name.startswith("."):
                        continue
                    full = path.rstrip("/") + "/" + name
                    try:
                        st = vfs.stat(full)
                    except Exception:
                        continue
                    if long_fmt:
                        dt  = datetime.datetime.fromtimestamp(st["modified"]).strftime("%b %d %H:%M")
                        pfx = "d" if st["is_dir"] else "-"
                        tag = "dir_" if st["is_dir"] else ""
                        ol(f"{pfx}{st['permissions']}  {st['owner']:8s}  {st['size']:8d}  {dt}  {name}", tag)
                    else:
                        icon = "📁" if st["is_dir"] else get_file_icon(name)
                        tag  = "dir_" if st["is_dir"] else ""
                        o(f"{icon} {name}  ", tag)
                if not long_fmt:
                    ol()

            elif cmd == "tree":
                start = vfs.resolve(args[0]) if args and not args[0].startswith("-") else cwd
                depth = int(args[args.index("-L")+1]) if "-L" in args and args.index("-L")+1 < len(args) else 4
                ol(start, "dir_")
                ol(vfs.tree(start, max_depth=depth))

            # ── FILE CONTENT ──────────────────────────────────────────────────
            elif cmd == "cat":
                if not args:
                    if stdin:
                        ol(stdin)
                    else:
                        ol("cat: no file specified", "error")
                    return "".join(buf) if capture else None
                for fname in args:
                    if fname.startswith("-"):
                        continue
                    fp = vfs.resolve(fname)
                    try:
                        content = vfs.read(fp)
                        if "-n" in args:
                            for i, line in enumerate(content.split("\n"), 1):
                                ol(f"{i:6d}\t{line}")
                        else:
                            o(content if content.endswith("\n") else content + "\n")
                    except FileNotFoundError:
                        ol(f"cat: {fname}: No such file", "error")
                    except IsADirectoryError:
                        ol(f"cat: {fname}: Is a directory", "error")

            elif cmd == "head":
                n = 10
                files: List[str] = []
                i = 0
                while i < len(args):
                    if args[i] == "-n" and i + 1 < len(args):
                        n = int(args[i+1]); i += 2
                    elif args[i].startswith("-"):
                        i += 1
                    else:
                        files.append(args[i]); i += 1
                src = vfs.read(vfs.resolve(files[0])) if files else stdin
                ol("\n".join(src.split("\n")[:n]))

            elif cmd == "tail":
                n = 10
                files = []
                i = 0
                while i < len(args):
                    if args[i] == "-n" and i + 1 < len(args):
                        n = int(args[i+1]); i += 2
                    elif args[i].startswith("-"):
                        i += 1
                    else:
                        files.append(args[i]); i += 1
                src = vfs.read(vfs.resolve(files[0])) if files else stdin
                ol("\n".join(src.split("\n")[-n:]))

            elif cmd in ("less", "more", "view"):
                fname = args[0] if args else None
                if fname:
                    try:
                        content = vfs.read(vfs.resolve(fname))
                        lines   = content.split("\n")
                        page    = 24
                        for chunk_start in range(0, len(lines), page):
                            for line in lines[chunk_start:chunk_start+page]:
                                ol(line)
                    except Exception as ex:
                        ol(str(ex), "error")

            elif cmd == "wc":
                results = []
                for fname in (a for a in args if not a.startswith("-")):
                    fp = vfs.resolve(fname)
                    try:
                        content = vfs.read(fp)
                        lc = content.count("\n")
                        wc = len(content.split())
                        cc = len(content)
                        results.append((lc, wc, cc, fname))
                        ol(f"  {lc:6d} {wc:7d} {cc:7d} {fname}")
                    except Exception:
                        ol(f"wc: {fname}: not found", "error")
                if not results and stdin:
                    lc = stdin.count("\n"); wc = len(stdin.split()); cc = len(stdin)
                    ol(f"  {lc:6d} {wc:7d} {cc:7d}")

            elif cmd == "file":
                for fname in (a for a in args if not a.startswith("-")):
                    fp = vfs.resolve(fname)
                    try:
                        st = vfs.stat(fp)
                        tp = get_file_type(fname, st["is_dir"])
                        ol(f"{fname}: {tp}")
                    except Exception:
                        ol(f"file: {fname}: not found", "error")

            # ── TEXT PROCESSING ───────────────────────────────────────────────
            elif cmd in ("echo", "print"):
                joined = " ".join(a for a in args if a not in ("-n", "-e"))
                if "-e" in args:
                    joined = joined.replace("\\n", "\n").replace("\\t", "\t").replace("\\033", "\033")
                if "-n" not in args:
                    joined += "\n"
                o(joined)

            elif cmd == "printf":
                fmt_str = args[0].replace("\\n", "\n").replace("\\t", "\t") if args else ""
                try:
                    o(fmt_str % tuple(args[1:]) if len(args) > 1 else fmt_str)
                except Exception:
                    o(fmt_str)

            elif cmd == "sort":
                src   = ""
                files = [a for a in args if not a.startswith("-")]
                if files:
                    try:
                        src = vfs.read(vfs.resolve(files[0]))
                    except Exception:
                        ol(f"sort: {files[0]}: not found", "error"); return "".join(buf) if capture else None
                else:
                    src = stdin
                rev   = "-r" in args
                uniq_ = "-u" in args
                lines = src.strip().split("\n")
                if "-n" in args:
                    try:
                        lines = sorted(lines, key=lambda x: float(x.split()[0]) if x.split() else 0, reverse=rev)
                    except Exception:
                        lines = sorted(lines, reverse=rev)
                else:
                    lines = sorted(lines, key=str.lower, reverse=rev)
                if uniq_:
                    seen: set = set()
                    deduped   = []
                    for l in lines:
                        if l not in seen:
                            seen.add(l); deduped.append(l)
                    lines = deduped
                result = "\n".join(lines) + "\n"
                o(result)
                if capture:
                    return result

            elif cmd == "uniq":
                src   = ""
                files = [a for a in args if not a.startswith("-")]
                if files:
                    try:
                        src = vfs.read(vfs.resolve(files[0]))
                    except Exception:
                        ol(f"uniq: {files[0]}: not found", "error"); return "".join(buf) if capture else None
                else:
                    src = stdin
                prev   = object()
                result = []
                for ln in src.split("\n"):
                    if ln != prev:
                        result.append(ln)
                        prev = ln
                o("\n".join(result) + "\n")

            elif cmd == "grep":
                ci  = "-i" in args
                rec = "-r" in args
                vv  = "-v" in args
                ln_ = "-n" in args
                non_flag = [a for a in args if not a.startswith("-")]
                if not non_flag:
                    ol("grep: pattern required", "error"); return "".join(buf) if capture else None
                pat    = non_flag[0]
                target = non_flag[1:] if len(non_flag) > 1 else (
                    [cwd] if rec else []
                )
                flags  = re.IGNORECASE if ci else 0

                def grep_file(fp: str) -> None:
                    try:
                        for i, line in enumerate(vfs.read(fp).split("\n"), 1):
                            matched = bool(re.search(pat, line, flags))
                            if matched != vv:
                                prefix = f"{fp}:{i}: " if ln_ else ""
                                o(prefix + line + "\n", "success" if matched else "")
                    except Exception:
                        pass

                if not target:
                    # grep on stdin
                    for i, line in enumerate(stdin.split("\n"), 1):
                        if bool(re.search(pat, line, flags)) != vv:
                            o(line + "\n", "success")
                else:
                    for t in target:
                        fp = vfs.resolve(t)
                        if vfs.isdir(fp) and rec:
                            for f in vfs.get_all_files(fp):
                                grep_file(f)
                        elif vfs.isfile(fp):
                            grep_file(fp)
                        else:
                            ol(f"grep: {t}: not found", "error")

            elif cmd == "sed":
                if not args:
                    ol("sed: expression required", "error"); return "".join(buf) if capture else None
                expr  = args[0]
                files = [a for a in args[1:] if not a.startswith("-")]
                src   = vfs.read(vfs.resolve(files[0])) if files else stdin
                m     = re.match(r"s([/|,])(.+?)\1(.*?)\1([giGI]*)", expr)
                if m:
                    _, pat, repl, flags_str = m.groups()
                    rf    = re.IGNORECASE if "i" in flags_str.lower() else 0
                    count = 0 if "g" in flags_str.lower() else 1
                    result = re.sub(pat, repl, src, count=count, flags=rf)
                    o(result if result.endswith("\n") else result + "\n")
                    if capture:
                        return result
                else:
                    ol(f"sed: unsupported expression: {expr}", "error")

            elif cmd == "awk":
                # Basic awk: field splitting and print
                if not args:
                    ol("awk: usage: awk '{print $1}' file", "error"); return "".join(buf) if capture else None
                prog  = args[0].strip("'\"")
                files = [a for a in args[1:] if not a.startswith("-")]
                src   = vfs.read(vfs.resolve(files[0])) if files else stdin
                sep   = " "
                if "-F" in args:
                    idx = args.index("-F")
                    if idx + 1 < len(args):
                        sep = args[idx+1]
                for row in src.split("\n"):
                    fields = row.split(sep)
                    local  = {"NF": len(fields), "NR": 1, "FS": sep, "RS": "\n"}
                    for i, f in enumerate(fields, 1):
                        local[f"${i}"] = f
                    local["$0"] = row
                    # Very simple: handle print $N or print
                    pm = re.search(r'print\s+(\S+)', prog)
                    if pm:
                        ref = pm.group(1)
                        val = local.get(ref, ref)
                        ol(str(val))
                    elif "print" in prog:
                        ol(row)

            elif cmd == "tr":
                if len(args) < 2:
                    ol("tr: usage: tr from to", "error"); return "".join(buf) if capture else None
                src    = stdin
                table  = str.maketrans(args[0], args[1])
                result = src.translate(table)
                o(result)

            elif cmd == "cut":
                delim = "\t"; fields_list = [0]
                i = 0
                while i < len(args):
                    if args[i] == "-d" and i+1 < len(args):
                        delim = args[i+1]; i += 2
                    elif args[i] == "-f" and i+1 < len(args):
                        fields_list = [int(x)-1 for x in args[i+1].split(",")]; i += 2
                    else:
                        i += 1
                files = [a for a in args if not a.startswith("-") and a not in (delim, str(fields_list))]
                src   = vfs.read(vfs.resolve(files[0])) if files else stdin
                for row in src.split("\n"):
                    pts = row.split(delim)
                    ol(delim.join(pts[f] for f in fields_list if f < len(pts)))

            elif cmd == "rev":
                files = [a for a in args if not a.startswith("-")]
                src   = vfs.read(vfs.resolve(files[0])) if files else stdin
                for ln in src.split("\n"):
                    ol(ln[::-1])

            elif cmd == "tee":
                if args:
                    fp = vfs.resolve(args[0])
                    vfs.write(fp, stdin, append="-a" in args)
                o(stdin)

            elif cmd == "base64":
                files = [a for a in args if not a.startswith("-")]
                src   = vfs.read(vfs.resolve(files[0])) if files else stdin
                if "-d" in args:
                    try:
                        ol(base64.b64decode(src.strip().encode()).decode())
                    except Exception:
                        ol("base64: invalid input", "error")
                else:
                    ol(base64.b64encode(src.encode()).decode())

            elif cmd in ("md5sum", "md5"):
                files = [a for a in args if not a.startswith("-")]
                src   = vfs.read(vfs.resolve(files[0])) if files else stdin
                ol(hashlib.md5(src.encode()).hexdigest() + ("  " + files[0] if files else ""))

            elif cmd in ("sha256sum", "sha256"):
                files = [a for a in args if not a.startswith("-")]
                src   = vfs.read(vfs.resolve(files[0])) if files else stdin
                ol(hashlib.sha256(src.encode()).hexdigest() + ("  " + files[0] if files else ""))

            elif cmd == "diff":
                if len(args) < 2:
                    ol("diff: usage: diff file1 file2", "error"); return "".join(buf) if capture else None
                import difflib
                try:
                    a_lines = vfs.read(vfs.resolve(args[0])).split("\n")
                    b_lines = vfs.read(vfs.resolve(args[1])).split("\n")
                    for ln in difflib.unified_diff(
                        a_lines, b_lines,
                        fromfile=args[0], tofile=args[1], lineterm="",
                    ):
                        if ln.startswith("+"):
                            ol(ln, "success")
                        elif ln.startswith("-"):
                            ol(ln, "error")
                        else:
                            ol(ln, "dim")
                except Exception as ex:
                    ol(str(ex), "error")

            # ── FILE MANAGEMENT ───────────────────────────────────────────────
            elif cmd == "mkdir":
                for d in (a for a in args if not a.startswith("-")):
                    fp = vfs.resolve(d)
                    try:
                        if "-p" in args:
                            vfs.makedirs(fp)
                        else:
                            vfs.mkdir(fp)
                        self._ok(f"mkdir: created '{d}'") if not capture else ol(f"created '{d}'")
                    except Exception as ex:
                        ol(str(ex), "error")

            elif cmd in ("rm", "del"):
                rec = "-r" in args or "-rf" in args
                for f in (a for a in args if not a.startswith("-")):
                    fp = vfs.resolve(f)
                    try:
                        if vfs.isdir(fp):
                            if rec:
                                vfs.rmdir(fp, recursive=True)
                            else:
                                ol(f"rm: {f}: is a directory (use -r)", "error")
                        else:
                            vfs.remove(fp)
                    except FileNotFoundError:
                        ol(f"rm: {f}: No such file", "error")
                    except Exception as ex:
                        ol(str(ex), "error")

            elif cmd == "rmdir":
                for d in (a for a in args if not a.startswith("-")):
                    try:
                        vfs.rmdir(vfs.resolve(d))
                    except Exception as ex:
                        ol(str(ex), "error")

            elif cmd in ("cp", "copy"):
                if len(args) < 2:
                    ol("cp: usage: cp <src> <dst>", "error"); return "".join(buf) if capture else None
                try:
                    vfs.copy(vfs.resolve(args[0]), vfs.resolve(args[1]))
                    self._ok(f"Copied {args[0]} → {args[1]}") if not capture else None
                except Exception as ex:
                    ol(str(ex), "error")

            elif cmd in ("mv", "move"):
                if len(args) < 2:
                    ol("mv: usage: mv <src> <dst>", "error"); return "".join(buf) if capture else None
                try:
                    vfs.rename(vfs.resolve(args[0]), vfs.resolve(args[1]))
                    self._ok(f"Moved {args[0]} → {args[1]}") if not capture else None
                except Exception as ex:
                    ol(str(ex), "error")

            elif cmd == "touch":
                for f in (a for a in args if not a.startswith("-")):
                    fp = vfs.resolve(f)
                    if vfs.isfile(fp):
                        vfs._get_node(fp).touch()
                    elif not vfs.exists(fp):
                        vfs.write(fp, "")

            elif cmd == "ln":
                # Simulated: just copy
                if len(args) >= 2:
                    try:
                        vfs.copy(vfs.resolve(args[-2]), vfs.resolve(args[-1]))
                        ol(f"linked {args[-2]} → {args[-1]}")
                    except Exception as ex:
                        ol(str(ex), "error")

            elif cmd == "find":
                start   = cwd
                pattern = "."
                ftype   = None
                i = 0
                while i < len(args):
                    if args[i] == "-name" and i+1 < len(args):
                        pattern = args[i+1]; i += 2
                    elif args[i] == "-type" and i+1 < len(args):
                        ftype = args[i+1]; i += 2
                    elif not args[i].startswith("-"):
                        start = vfs.resolve(args[i]); i += 1
                    else:
                        i += 1
                for fp in vfs.find(pattern, start, file_type=ftype):
                    ol(fp)

            elif cmd == "stat":
                for f in (a for a in args if not a.startswith("-")):
                    fp = vfs.resolve(f)
                    try:
                        st = vfs.stat(fp)
                        ol(f"  File:    {st['full_path']}")
                        ol(f"  Size:    {st['size_str']}  ({st['size']} bytes)")
                        ol(f"  Type:    {'Directory' if st['is_dir'] else 'File'}")
                        ol(f"  Mode:    {st['permissions']}")
                        ol(f"  Owner:   {st['owner']} / {st['group']}")
                        ol(f"  Created: {fmt_time(st['created'])}")
                        ol(f"  Modify:  {fmt_time(st['modified'])}")
                        ol(f"  Access:  {fmt_time(st['accessed'])}")
                    except FileNotFoundError:
                        ol(f"stat: {f}: No such file", "error")

            elif cmd == "df":
                used, total = vfs.disk_usage()
                free = total - used
                ol("Filesystem        Size    Used    Avail   Use%", "hdr")
                ol("─" * 55, "dim")
                ol(f"pyos-vfs     {fmt_size(total):>8}  {fmt_size(used):>6}  {fmt_size(free):>7}  {used*100//total}%")

            elif cmd == "du":
                target = vfs.resolve(args[0] if args and not args[0].startswith("-") else cwd)
                if vfs.isdir(target):
                    for name in vfs.listdir(target):
                        fp = target.rstrip("/") + "/" + name
                        try:
                            st = vfs.stat(fp)
                            ol(f"{st['size_str']:>10}\t{fp}")
                        except Exception:
                            pass
                else:
                    try:
                        st = vfs.stat(target)
                        ol(f"{st['size_str']:>10}\t{target}")
                    except Exception as ex:
                        ol(str(ex), "error")

            elif cmd == "quota":
                used, total = vfs.disk_usage()
                pct  = used * 100 // total
                bar  = "█" * (pct // 5) + "░" * (20 - pct // 5)
                ol(f"Disk quota for {self.wm.users.current}:")
                ol(f"  [{bar}] {pct}%  ({fmt_size(used)} / {fmt_size(total)})")

            # ── PROCESS ───────────────────────────────────────────────────────
            elif cmd == "ps":
                wide = "-e" in args or "-ef" in args
                ol(f"{'PID':>6}  {'USER':8}  {'CPU%':6}  {'MEM':6}  {'STATUS':10}  COMMAND", "hdr")
                ol("─" * 60, "dim")
                for p in self.wm.procs.list_all():
                    if not wide and p.owner != (self.wm.users.current or "user"):
                        continue
                    ol(f"{p.pid:>6}  {p.owner:8}  {p.cpu:5.1f}%  {p.mem:4d}MB  {p.status:10}  {p.name}")

            elif cmd == "top":
                procs = self.wm.procs.list_all()
                ol(f"PyOS top — {datetime.datetime.now():%H:%M:%S}  "
                   f"Procs: {len(procs)}  CPU: {self.wm.procs.total_cpu:.1f}%  "
                   f"Mem: {self.wm.procs.total_mem}MB", "hdr")
                ol(f"{'PID':>6}  {'NAME':20}  {'CPU%':6}  {'MEM':5}  UPTIME", "bold")
                for p in sorted(procs, key=lambda x: x.cpu, reverse=True)[:20]:
                    bar = "█" * max(0, int(p.cpu / 10))
                    ol(f"{p.pid:>6}  {p.name:20}  {p.cpu:5.1f}%  {p.mem:4d}M  {p.uptime}  {bar}")

            elif cmd == "kill":
                if not args:
                    ol("kill: usage: kill [-9] <pid>", "error"); return "".join(buf) if capture else None
                pids = [a for a in args if a.lstrip("-").isdigit()]
                for pid_s in pids:
                    pid = int(pid_s)
                    if self.wm.procs.kill(pid):
                        self._ok(f"Killed PID {pid}") if not capture else ol(f"killed {pid}")
                    else:
                        ol(f"kill: ({pid}) — No such process", "error")

            elif cmd == "killall":
                if not args:
                    ol("killall: usage: killall <name>", "error"); return "".join(buf) if capture else None
                n = self.wm.procs.kill_by_name(args[0])
                ol(f"Killed {n} process(es) named '{args[0]}'",
                   "success" if n else "warn")

            elif cmd == "nice":
                if len(args) >= 2:
                    self._dispatch(" ".join(args[1:]))

            elif cmd == "jobs":
                ol("No background jobs running.", "dim")

            elif cmd in ("bg", "fg"):
                ol(f"{cmd}: no background jobs", "warn")

            # ── SYSTEM INFO ───────────────────────────────────────────────────
            elif cmd == "uname":
                if "-a" in args:
                    ol(f"PyOS {PYOS_VERSION} pyos-machine Python-kernel {PYOS_CODENAME} "
                       f"Python/{sys.version.split()[0]} GNU/Python")
                elif "-r" in args:
                    ol(f"Python-{sys.version.split()[0]}")
                elif "-m" in args:
                    ol(platform.machine())
                else:
                    ol("PyOS")

            elif cmd == "uptime":
                s   = self.wm.users.uptime_secs
                avg = self.wm.procs.total_cpu / max(1, len(self.wm.procs.procs))
                ol(f" {datetime.datetime.now():%H:%M:%S}  up {fmt_duration(s)},  "
                   f"{len(self.wm.users.all_accounts())} user(s),  "
                   f"load average: {avg:.2f}, {avg*0.9:.2f}, {avg*0.8:.2f}")

            elif cmd == "hostname":
                if "-i" in args:
                    ol("192.168.1.100")
                else:
                    ol("pyos-machine")

            elif cmd == "whoami":
                ol(self.wm.users.current or "user")

            elif cmd == "id":
                u = self.wm.users.current or "user"
                ol(f"uid=1000({u}) gid=1000({u}) groups=1000({u}),4(adm),27(sudo),100(users)")

            elif cmd == "who":
                u    = self.wm.users.current or "user"
                dt   = datetime.datetime.fromtimestamp(
                    self.wm.users.login_time or time.time()
                ).strftime("%Y-%m-%d %H:%M")
                ol(f"{u}   tty0   {dt}   (pyos)")

            elif cmd == "w":
                self._dispatch("who")
                self._dispatch("uptime")

            elif cmd == "last":
                for entry in reversed(self.wm.users.session_log[-10:]):
                    ol(entry)

            elif cmd == "groups":
                u = self.wm.users.current or "user"
                ol(f"{u} adm sudo users")

            elif cmd in ("sysinfo", "neofetch"):
                used, total = vfs.disk_usage()
                lines = [
                    ("OS",       f"PyOS {PYOS_VERSION} ({PYOS_CODENAME})"),
                    ("Kernel",   f"Python {sys.version.split()[0]}"),
                    ("Host",     "pyos-machine"),
                    ("Uptime",   self.wm.users.uptime),
                    ("Shell",    "/bin/pysh"),
                    ("Terminal", "PyOS Terminal"),
                    ("CPU",      "PyOS Virtual CPU @ 3.2GHz × 4"),
                    ("Memory",   f"{self.wm.procs.total_mem} MB / 8192 MB"),
                    ("Disk",     f"{fmt_size(used)} / {fmt_size(total)}"),
                    ("Processes",str(self.wm.procs.process_count)),
                    ("Windows",  str(len(self.wm.wins))),
                    ("Theme",    self.wm.settings.get("theme", "Dark Blue")),
                ]
                logo = [
                    "  ██████╗ ██╗   ██╗",
                    "  ██╔══██╗╚██╗ ██╔╝",
                    "  ██████╔╝ ╚████╔╝ ",
                    "  ██╔═══╝   ╚██╔╝  ",
                    "  ██║        ██║   ",
                    "  ╚═╝        ╚═╝   ",
                ]
                for i, (key, val) in enumerate(lines):
                    logo_line = logo[i] if i < len(logo) else " " * 20
                    o(logo_line, "info")
                    ol(f"  {key}: {val}")

            # ── DATE / TIME ───────────────────────────────────────────────────
            elif cmd == "date":
                fmt = " ".join(args).lstrip("+") if args else "%a %b %d %H:%M:%S %Z %Y"
                ol(datetime.datetime.now().strftime(fmt))

            elif cmd == "cal":
                today = datetime.date.today()
                y     = today.year
                m     = today.month
                if len(args) == 1:
                    y = int(args[0])
                elif len(args) >= 2:
                    m, y = int(args[0]), int(args[1])
                ol(calendar.month(y, m), "info")

            elif cmd in ("time",):
                # Just show current time
                ol(datetime.datetime.now().strftime("%H:%M:%S"))

            elif cmd == "sleep":
                secs = float(args[0]) if args else 1
                ol(f"(sleeping {secs}s…)", "dim")

            # ── MATH ──────────────────────────────────────────────────────────
            elif cmd == "bc":
                expr = " ".join(args) if args else stdin.strip()
                try:
                    import math as _m
                    safe_env = {k: getattr(_m, k) for k in dir(_m) if not k.startswith("_")}
                    safe_env["__builtins__"] = {}
                    result = eval(expr, safe_env)
                    ol(str(result))
                except Exception as ex:
                    ol(f"bc: {ex}", "error")

            elif cmd == "expr":
                try:
                    ol(str(eval(" ".join(args), {"__builtins__": {}})))
                except Exception as ex:
                    ol(str(ex), "error")

            elif cmd == "factor":
                def factorize(n: int) -> List[int]:
                    factors = []
                    d = 2
                    while d * d <= n:
                        while n % d == 0:
                            factors.append(d); n //= d
                        d += 1
                    if n > 1:
                        factors.append(n)
                    return factors
                for a in args:
                    try:
                        n = int(a)
                        ol(f"{n}: {' '.join(map(str, factorize(n)))}")
                    except Exception:
                        ol(f"factor: {a}: not a number", "error")

            elif cmd == "seq":
                try:
                    if len(args) == 1:
                        vals = range(1, int(args[0]) + 1)
                    elif len(args) == 2:
                        vals = range(int(args[0]), int(args[1]) + 1)
                    elif len(args) == 3:
                        vals = range(int(args[0]), int(args[2]) + 1, int(args[1]))
                    else:
                        vals = range(0)
                    for v in vals:
                        ol(str(v))
                except Exception as ex:
                    ol(str(ex), "error")

            elif cmd == "yes":
                msg = args[0] if args else "y"
                for _ in range(30):
                    ol(msg)
                ol("… (truncated)", "dim")

            # ── ENVIRONMENT ───────────────────────────────────────────────────
            elif cmd in ("env", "printenv"):
                var = args[0] if args else None
                if var:
                    ol(self._env.get(var, ""))
                else:
                    for k, v in sorted(self._env.items()):
                        ol(f"{k}={v}")

            elif cmd == "export":
                for a in args:
                    if "=" in a:
                        k, v = a.split("=", 1)
                        self._env[k] = v
                    else:
                        ol(f"export: {a}={self._env.get(a, '')}")

            elif cmd == "unset":
                for a in args:
                    self._env.pop(a, None)

            elif cmd == "set":
                for k, v in sorted(self._env.items()):
                    ol(f"{k}='{v}'")

            elif cmd == "alias":
                if not args:
                    for k, v in sorted(self._aliases.items()):
                        ol(f"alias {k}='{v}'")
                elif "=" in args[0]:
                    k, v = args[0].split("=", 1)
                    self._aliases[k] = v.strip("'\"")
                else:
                    v = self._aliases.get(args[0], "")
                    if v:
                        ol(f"alias {args[0]}='{v}'")

            elif cmd == "unalias":
                for a in args:
                    self._aliases.pop(a, None)

            elif cmd == "history":
                n = int(args[0]) if args else len(self._hist)
                for i, h in enumerate(self._hist[-n:], max(1, len(self._hist)-n+1)):
                    ol(f"  {i:4d}  {h}")

            elif cmd == "source":
                if args:
                    fp = vfs.resolve(args[0])
                    try:
                        for line in vfs.read(fp).split("\n"):
                            line = line.strip()
                            if line and not line.startswith("#"):
                                self._dispatch(line)
                    except Exception as ex:
                        ol(str(ex), "error")

            # ── NETWORK ───────────────────────────────────────────────────────
            elif cmd == "ping":
                host  = args[0] if args else "pyos.local"
                count = int(args[args.index("-c")+1]) if "-c" in args and args.index("-c")+1 < len(args) else 4
                for i in range(count):
                    ms = random.uniform(0.3, 45.0)
                    ol(f"64 bytes from {host}: icmp_seq={i+1} ttl=64 time={ms:.2f} ms", "success")
                ol(f"\n--- {host} ping statistics ---")
                ol(f"{count} packets transmitted, {count} received, 0% packet loss")

            elif cmd == "curl":
                url     = next((a for a in args if a.startswith(("http","pyos"))), "")
                verbose = "-v" in args
                if verbose:
                    ol(f"> GET {url} HTTP/1.1", "dim")
                    ol("> Host: " + (url.split("/")[2] if "//" in url else url), "dim")
                    ol("< HTTP/1.1 200 OK", "success")
                ol(f'{{"status":200,"url":"{url}","simulated":true,'
                   f'"server":"PyOS/1.0","timestamp":"{datetime.datetime.now().isoformat()}"}}', "success")

            elif cmd == "wget":
                url   = next((a for a in args if a.startswith("http")), "")
                fname = url.split("/")[-1] or "index.html"
                fp    = vfs.resolve(fname)
                content = f"<!-- Downloaded from {url} by PyOS wget -->\n<html><body><p>Simulated content</p></body></html>\n"
                vfs.write(fp, content)
                ol(f"Connecting to {url}…")
                ol(f"HTTP request sent, awaiting response… 200 OK")
                ol(f"Saving to: '{fname}'")
                ol(f"'{fname}' saved [{len(content)}/{len(content)}]", "success")

            elif cmd == "netstat":
                ol("Active Internet connections", "hdr")
                ol(f"{'Proto':6}  {'Local':22}  {'Remote':22}  {'State':12}")
                ol("─" * 70, "dim")
                entries_n = [
                    ("tcp", "0.0.0.0:80",     "0.0.0.0:*",      "LISTEN"),
                    ("tcp", "127.0.0.1:3306",  "0.0.0.0:*",      "LISTEN"),
                    ("tcp", "192.168.1.100:22","192.168.1.1:5544","ESTABLISHED"),
                    ("udp", "0.0.0.0:53",      "0.0.0.0:*",      ""),
                ]
                for proto, local, remote, state in entries_n:
                    ol(f"{proto:6}  {local:22}  {remote:22}  {state}")

            elif cmd in ("ifconfig", "ip"):
                ol("eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500", "hdr")
                ol("      inet 192.168.1.100  netmask 255.255.255.0  broadcast 192.168.1.255")
                ol("      inet6 fe80::1  prefixlen 64  scopeid 0x20<link>")
                ol("      ether 00:11:22:33:44:55  txqueuelen 1000  (Ethernet)")
                ol("lo:   flags=73<UP,LOOPBACK,RUNNING>  mtu 65536", "hdr")
                ol("      inet 127.0.0.1  netmask 255.0.0.0")

            elif cmd == "nslookup":
                host = args[0] if args else "pyos.local"
                ol(f"Server:         192.168.1.1")
                ol(f"Address:        192.168.1.1#53")
                ol(f"Non-authoritative answer:")
                ol(f"Name:   {host}")
                ol(f"Address: 192.168.{random.randint(0,255)}.{random.randint(1,254)}")

            elif cmd == "dig":
                host = args[0] if args else "pyos.local"
                ol(f"; <<>> DiG 9.x <<>> {host}")
                ol(f";; ANSWER SECTION:")
                ol(f"{host}.    300    IN    A    192.168.{random.randint(0,255)}.{random.randint(1,254)}")

            elif cmd == "ssh":
                host = args[0] if args else "pyos.local"
                ol(f"ssh: connect to host {host}: Connection simulated (PyOS)", "warn")

            # ── ARCHIVE ───────────────────────────────────────────────────────
            elif cmd == "zip":
                if len(args) < 2:
                    ol("zip: usage: zip archive.zip file...", "error"); return "".join(buf) if capture else None
                arc_name = args[0]
                files    = args[1:]
                content  = f"# PyOS Zip Archive: {arc_name}\n"
                for f in files:
                    fp = vfs.resolve(f)
                    try:
                        content += f"\n--- {f} ---\n"
                        content += vfs.read(fp)
                    except Exception:
                        content += f"(could not read {f})\n"
                vfs.write(vfs.resolve(arc_name), content)
                ol(f"  adding: {', '.join(files)}", "success")
                ol(f"Archive created: {arc_name}", "success")

            elif cmd in ("unzip", "tar"):
                fname = next((a for a in args if not a.startswith("-")), None)
                if fname:
                    fp = vfs.resolve(fname)
                    if vfs.isfile(fp):
                        ol(f"Archive: {fname}")
                        ol(f"  inflating: (simulated extraction)", "dim")
                        ol(f"Extracted successfully.", "success")
                    else:
                        ol(f"{cmd}: {fname}: not found", "error")

            # ── PYTHON EXEC ───────────────────────────────────────────────────
            elif cmd in ("python", "python3"):
                if not args or args[0].startswith("-"):
                    ol("Python 3 (PyOS embedded)", "info")
                    ol("Type 'exit()' or Ctrl+D to quit.", "dim")
                else:
                    fp = vfs.resolve(args[0])
                    try:
                        code       = vfs.read(fp)
                        import io as _io
                        old_stdout = sys.stdout
                        buf2       = _io.StringIO()
                        sys.stdout = buf2
                        try:
                            exec(compile(code, fp, "exec"), {"__file__": fp, "__name__": "__main__"})
                        except SystemExit:
                            pass
                        except Exception as ex:
                            sys.stdout = old_stdout
                            ol(traceback.format_exc(), "error")
                            return "".join(buf) if capture else None
                        finally:
                            sys.stdout = old_stdout
                        out2 = buf2.getvalue()
                        if out2:
                            o(out2)
                    except FileNotFoundError:
                        ol(f"python: {args[0]}: No such file", "error")

            elif cmd in ("sh", "bash"):
                if args:
                    fp = vfs.resolve(args[0])
                    try:
                        for line in vfs.read(fp).split("\n"):
                            line = line.strip()
                            if line and not line.startswith("#"):
                                self._dispatch(line)
                    except Exception as ex:
                        ol(str(ex), "error")

            # ── MISC ──────────────────────────────────────────────────────────
            elif cmd in ("open", "edit"):
                target = args[0] if args else None
                if target:
                    fp = vfs.resolve(target)
                    if vfs.isfile(fp):
                        self.wm.open_editor(fp)
                    elif vfs.isdir(fp):
                        self.wm.open_fm(fp)
                    else:
                        ol(f"open: {target}: not found", "error")

            elif cmd == "write":
                if len(args) < 2:
                    ol("write: usage: write <file> <content>", "error"); return "".join(buf) if capture else None
                fp      = vfs.resolve(args[0])
                content = " ".join(args[1:]) + "\n"
                vfs.write(fp, content)
                ol(f"Written to {fp}", "success")

            elif cmd == "append":
                if len(args) < 2:
                    ol("append: usage: append <file> <content>", "error"); return "".join(buf) if capture else None
                fp      = vfs.resolve(args[0])
                content = " ".join(args[1:]) + "\n"
                vfs.write(fp, content, append=True)
                ol(f"Appended to {fp}", "success")

            elif cmd == "which":
                for a in args:
                    if a in self.BUILTINS:
                        ol(f"/usr/bin/{a}")
                    else:
                        ol(f"which: {a}: not found", "warn")

            elif cmd == "clear":
                self._clear()

            elif cmd == "reset":
                self._clear()
                self._print_banner()

            elif cmd in ("exit", "quit", "logout"):
                self.wm.users.logout()
                show_login(self.wm.root, self.wm)

            elif cmd == "version":
                ol(f"PyOS {PYOS_VERSION} ({PYOS_CODENAME})", "info")
                ol(f"Python {sys.version}")
                ol(f"Platform: {platform.system()} {platform.release()}")

            elif cmd == "credits":
                ol("┌──────────────────────────────────┐", "info")
                ol("│      PyOS v5.0  Credits           │", "info")
                ol("├──────────────────────────────────┤", "info")
                ol("│  Built with: Python + Tkinter     │", "info")
                ol("│  VFS: Custom in-memory FS         │", "info")
                ol("│  WM:  Custom floating windows     │", "info")
                ol("│  Deps: ZERO (stdlib only)         │", "info")
                ol("│  Lines: ~18,000                   │", "info")
                ol("└──────────────────────────────────┘", "info")

            elif cmd == "fortune":
                fortunes = [
                    "Talk is cheap. Show me the code.  — Linus Torvalds",
                    "Any fool can write code that a computer can understand.\n"
                    "Good programmers write code that humans can understand.  — Martin Fowler",
                    "First, solve the problem. Then, write the code.  — John Johnson",
                    "Debugging is twice as hard as writing the code in the first place.",
                    "The best tool is the one you know.",
                    "Simplicity is the ultimate sophistication.",
                    "Make it work, make it right, make it fast.",
                    "Code is read more often than it is written.",
                    "Premature optimisation is the root of all evil.  — Knuth",
                    "Keep it simple, stupid.",
                ]
                ol(random.choice(fortunes), "success")

            elif cmd == "cowsay":
                msg    = " ".join(args) if args else "Moo!"
                border = "─" * (len(msg) + 2)
                ol(f"  ┌{border}┐")
                ol(f"  │ {msg} │")
                ol(f"  └{border}┘")
                ol(r"         \   ^__^")
                ol(r"          \  (oo)\_______")
                ol(r"             (__)\       )\/\ ")
                ol(r"                 ||----w |")
                ol(r"                 ||     ||")

            elif cmd == "matrix":
                chars = "ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂｵﾘｱﾎﾃﾆｼ01"
                for _ in range(24):
                    ol("".join(random.choice(chars) for _ in range(72)), "success")

            elif cmd == "banner":
                msg = " ".join(args) if args else "PyOS"
                ol(f"\n{'#' * (len(msg) + 4)}")
                ol(f"# {msg.upper()} #")
                ol(f"{'#' * (len(msg) + 4)}\n", "hdr")

            elif cmd == "lolcat":
                text = " ".join(args) if args else stdin
                cols = [T["chart1"], T["chart2"], T["chart3"], T["chart4"], T["chart5"]]
                for ch in text:
                    o(ch, random.choice(["success","info","warn","error","dim"]))
                ol()

            elif cmd == "help":
                ol("PyOS Shell — Built-in Commands", "hdr")
                ol("═" * 55, "dim")
                sections = [
                    ("Navigation",    "cd, pwd, pushd, popd"),
                    ("Listing",       "ls, ll, la, dir, tree"),
                    ("File Content",  "cat, head, tail, less, wc, file"),
                    ("Text Process",  "grep, sed, awk, sort, uniq, tr, cut, rev, tee, diff"),
                    ("File Ops",      "mkdir, rmdir, rm, cp, mv, touch, ln, find, stat"),
                    ("Disk",          "df, du, quota"),
                    ("Processes",     "ps, top, kill, killall, nice, jobs, bg, fg"),
                    ("System Info",   "uname, uptime, hostname, whoami, id, who, w, last, sysinfo"),
                    ("Date/Time",     "date, cal, time, sleep"),
                    ("Math",          "bc, expr, factor, seq, yes"),
                    ("Environment",   "env, export, unset, set, alias, unalias, history, source"),
                    ("Encoding",      "base64, md5sum, sha256sum"),
                    ("Network",       "ping, curl, wget, netstat, ifconfig, nslookup, dig, ssh"),
                    ("Archive",       "zip, unzip, tar"),
                    ("Scripting",     "python, python3, sh, bash"),
                    ("I/O",           "echo, printf, write, append, open, edit, which"),
                    ("Fun",           "fortune, cowsay, matrix, banner, lolcat"),
                    ("Shell",         "clear, reset, exit, quit, version, credits, help"),
                ]
                for section, cmds in sections:
                    o(f"  {section:<14}", "info")
                    ol(cmds)

            elif cmd in ("true",):
                pass

            elif cmd in ("false",):
                pass

            elif cmd == "":
                pass

            else:
                # Check if it's a path to an executable
                fp = vfs.resolve(cmd)
                if vfs.isfile(fp) and cmd.endswith(".py"):
                    self._dispatch(f"python {cmd} {' '.join(args)}")
                elif vfs.isfile(fp) and cmd.endswith(".sh"):
                    self._dispatch(f"sh {cmd} {' '.join(args)}")
                else:
                    ol(f"{cmd}: command not found", "error")
                    ol(f"  Type 'help' for a list of commands.", "dim")

        except Exception as ex:
            ol(f"Error: {ex}", "error")
            ol(traceback.format_exc(), "dim")

        if capture:
            return "".join(buf)
        return None

    # ── toolbar actions ───────────────────────────────────────────────────────

    def _clear(self) -> None:
        self.out.config(state="normal")
        self.out.delete("1.0", "end")
        self.out.config(state="disabled")

    def _copy_sel(self) -> None:
        try:
            text = self.out.get("sel.first", "sel.last")
            self.wm.clip.copy_text(text)
            self.wm.notifs.send("Terminal", "Selection copied to clipboard.", icon="📋")
        except tk.TclError:
            pass

    def _new_tab(self) -> None:
        self.wm.open_terminal()

    def _term_cfg(self) -> None:
        d = tk.Toplevel(self.wm.root)
        d.title("Terminal Settings")
        d.config(bg=T["win_bg"])
        d.geometry("300x180")
        d.wm_attributes("-topmost", True)

        tk.Label(d, text="Font Size:", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(pady=(16, 4))
        fv = tk.IntVar(value=self.wm.settings.get("terminal_font_size", 10))

        def apply_font():
            fs = fv.get()
            self.wm.settings.set("terminal_font_size", fs)
            self.out.config(font=(FONT_MONO, fs))
            self._cmd_entry.config(font=(FONT_MONO, fs))
            self._prompt_lbl.config(font=(FONT_MONO, fs, "bold"))

        ttk.Scale(d, from_=7, to=20, orient="horizontal",
                  variable=fv, command=lambda _: apply_font()).pack(
            fill="x", padx=24
        )
        tk.Label(d, textvariable=fv, bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 9)).pack()
        mkbtn(d, "Apply & Close",
              lambda: (apply_font(), d.destroy()),
              kind="accent").pack(pady=10)

    def on_focus(self) -> None:
        self._cmd_entry.focus_set()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 18 — BROWSER APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class BrowserApp(BaseWin):
    """
    Simulated web browser with:
      • Address bar + navigation buttons
      • Bookmarks bar
      • Internal page renderer (HTML-like markup)
      • Tabs (multiple pages)
      • History tracking
      • Page printing (save to VFS)
      • Find in page
      • Reader mode
      • Built-in pages: home, news, docs, about, help, gallery, settings
    """

    HOME_URL = "pyos://home"

    PAGES: Dict[str, str] = {
        "pyos://home": """
<h1>🏠 PyOS Home</h1>
<p>Welcome to <b>PyOS v5.0 Browser</b> — your gateway to the PyOS ecosystem.</p>
<h2>📌 Quick Links</h2>
<ul>
<li><a href="pyos://news">📰 News & Updates</a></li>
<li><a href="pyos://docs">📚 Documentation</a></li>
<li><a href="pyos://api">🔌 API Reference</a></li>
<li><a href="pyos://gallery">🖼️ Gallery</a></li>
<li><a href="pyos://about">ℹ️ About PyOS</a></li>
<li><a href="pyos://help">❓ Help Center</a></li>
<li><a href="pyos://settings_browser">⚙️ Browser Settings</a></li>
</ul>
<h2>🌐 Simulate External Sites</h2>
<ul>
<li><a href="http://python.org">python.org (simulated)</a></li>
<li><a href="http://github.com">github.com (simulated)</a></li>
<li><a href="http://stackoverflow.com">stackoverflow.com (simulated)</a></li>
</ul>
""",
        "pyos://news": """
<h1>📰 PyOS News</h1>
<h2>🎉 PyOS v5.0 "Nebula" Released!</h2>
<p>The biggest PyOS release ever. <b>20 built-in apps</b>, <b>60+ terminal commands</b>,
and a completely overhauled UI — all in pure Python with zero dependencies.</p>
<h2>✨ What's New in v5.0</h2>
<ul>
<li>Archive Manager — zip/unzip VFS files</li>
<li>System Monitor — live CPU/RAM/disk graphs</li>
<li>Password Manager — encrypted vault</li>
<li>Spreadsheet — CSV editor with formulas</li>
<li>Code Runner — run Python snippets instantly</li>
<li>Image Viewer — view and filter images</li>
<li>5 built-in themes: Dark Blue, Dracula, Nord, Light, Monokai</li>
<li>Browser now supports tabs and reader mode</li>
<li>Terminal gains 20 new commands including awk, netstat, dig</li>
</ul>
<h2>🛣️ Coming in v5.1</h2>
<ul>
<li>Calendar app with iCal support</li>
<li>Video player (simulated)</li>
<li>Plugin system for third-party apps</li>
<li>Remote filesystem (SFTP simulation)</li>
</ul>
""",
        "pyos://docs": """
<h1>📚 PyOS Documentation</h1>
<h2>Getting Started</h2>
<p>PyOS is a complete desktop OS simulation built entirely in Python using Tkinter.
Run it with <b>python pyos.py</b> — no pip install required.</p>
<h2>Applications</h2>
<ul>
<li><b>File Manager</b> — browse VFS, copy/paste, search, preview</li>
<li><b>Text Editor</b> — syntax highlighting, find/replace, run Python</li>
<li><b>Terminal</b> — 60+ shell commands, pipes, redirection, history</li>
<li><b>Browser</b> — you are here! Internal pages + simulated external</li>
<li><b>Music Player</b> — waveform visualiser, playlist management</li>
<li><b>Paint Studio</b> — 10 drawing tools, layers, colour picker</li>
<li><b>Calculator</b> — standard, scientific, programmer, unit conversion</li>
<li><b>Clock</b> — analog/digital, alarm, stopwatch, world clock</li>
<li><b>Task Manager</b> — processes, CPU/RAM graphs, network, disk</li>
<li><b>System Monitor</b> — live system health dashboard</li>
<li><b>Notes</b> — rich text note-taking with tags</li>
<li><b>Email</b> — simulated inbox, compose, reply, archive</li>
<li><b>Password Manager</b> — encrypted vault with generator</li>
<li><b>Spreadsheet</b> — CSV editor with formula support</li>
<li><b>Image Viewer</b> — canvas-based image rendering and filters</li>
<li><b>Disk Analyzer</b> — pie chart, extension breakdown</li>
<li><b>Code Runner</b> — REPL, snippets, output capture</li>
<li><b>Archive Manager</b> — create/extract zip archives</li>
<li><b>App Store</b> — browse and install simulated apps</li>
<li><b>Settings</b> — theme, display, privacy, accounts</li>
</ul>
<h2>Keyboard Shortcuts</h2>
<ul>
<li><b>Ctrl+S</b> — Save (editor)</li>
<li><b>Ctrl+F</b> — Find (editor/browser)</li>
<li><b>Ctrl+L</b> — Clear (terminal)</li>
<li><b>Tab</b> — Autocomplete (terminal)</li>
<li><b>↑↓</b> — History (terminal)</li>
<li><b>Double-click</b> — Open file/folder</li>
<li><b>Right-click desktop</b> — Context menu</li>
</ul>
""",
        "pyos://api": """
<h1>🔌 PyOS API Reference</h1>
<h2>VFS Module</h2>
<ul>
<li><b>vfs.read(path)</b> — Read file content</li>
<li><b>vfs.write(path, content)</b> — Write/overwrite file</li>
<li><b>vfs.append(path, content)</b> — Append to file</li>
<li><b>vfs.listdir(path)</b> — List directory contents</li>
<li><b>vfs.mkdir(path)</b> — Create directory</li>
<li><b>vfs.makedirs(path)</b> — Create directory tree</li>
<li><b>vfs.remove(path)</b> — Delete file</li>
<li><b>vfs.rmdir(path, recursive)</b> — Delete directory</li>
<li><b>vfs.rename(src, dst)</b> — Move/rename</li>
<li><b>vfs.copy(src, dst)</b> — Copy file</li>
<li><b>vfs.stat(path)</b> — File metadata</li>
<li><b>vfs.find(pattern, start)</b> — Search by name</li>
<li><b>vfs.grep(pattern, start)</b> — Search by content</li>
<li><b>vfs.tree(path)</b> — Pretty-print tree</li>
</ul>
<h2>WM Module</h2>
<ul>
<li><b>wm.open_fm(path)</b> — Launch File Manager</li>
<li><b>wm.open_editor(path)</b> — Launch Text Editor</li>
<li><b>wm.open_terminal()</b> — Launch Terminal</li>
<li><b>wm.notifs.send(title, body)</b> — Send notification</li>
<li><b>wm.settings.get(key)</b> — Read setting</li>
<li><b>wm.settings.set(key, val)</b> — Write setting</li>
</ul>
""",
        "pyos://gallery": """
<h1>🖼️ PyOS Gallery</h1>
<p>Screenshots of PyOS v5.0 in action.</p>
<h2>Themes</h2>
<ul>
<li>Dark Blue (default) — GitHub-inspired dark theme</li>
<li>Dracula — Classic purple vampire theme</li>
<li>Nord — Arctic, north-bluish color palette</li>
<li>Light — Clean, professional light theme</li>
<li>Monokai — Editor-inspired green accents</li>
</ul>
<h2>Wallpapers</h2>
<ul>
<li>Gradient Blue — Deep space blue gradient</li>
<li>Gradient Purple — Royal purple gradient</li>
<li>Starfield — 400 procedural stars with nebulae</li>
<li>Grid — Dark cyberpunk grid</li>
<li>Sunset — 8-band colour gradient</li>
<li>Forest — Procedural tree silhouettes</li>
<li>Ocean — Deep ocean gradient</li>
<li>Solid — Single colour</li>
</ul>
""",
        "pyos://about": f"""
<h1>ℹ️ About PyOS v{PYOS_VERSION}</h1>
<h2>Project Info</h2>
<ul>
<li><b>Name:</b> PyOS</li>
<li><b>Version:</b> {PYOS_VERSION} ({PYOS_CODENAME})</li>
<li><b>Language:</b> Python 3.x</li>
<li><b>GUI:</b> Tkinter (standard library only)</li>
<li><b>Dependencies:</b> Zero external packages</li>
<li><b>Lines of Code:</b> ~18,000</li>
<li><b>Built-in Apps:</b> 20</li>
<li><b>Terminal Commands:</b> 60+</li>
<li><b>Themes:</b> 5</li>
<li><b>Wallpapers:</b> 8</li>
</ul>
<h2>Philosophy</h2>
<p>PyOS demonstrates that a complete, feature-rich desktop OS can be built
using only Python's standard library. No pip install. No external frameworks.
Just pure Python and Tkinter.</p>
""",
        "pyos://help": """
<h1>❓ Help Center</h1>
<h2>Common Questions</h2>
<ul>
<li><b>How do I open an app?</b> Double-click its icon on the desktop, or use the Start Menu.</li>
<li><b>How do I save a file?</b> Ctrl+S in the Text Editor.</li>
<li><b>How do I change the theme?</b> Settings → Appearance → Theme.</li>
<li><b>How do I run Python code?</b> Use the Code Runner app, or the terminal: python script.py</li>
<li><b>How do I search files?</b> File Manager → Search button, or terminal: find / grep</li>
<li><b>How do I create a user?</b> Settings → Accounts → Add User.</li>
</ul>
<h2>Terminal Quick Reference</h2>
<ul>
<li><b>ls</b> — list files</li>
<li><b>cd path</b> — change directory</li>
<li><b>cat file</b> — show file contents</li>
<li><b>grep pattern file</b> — search in file</li>
<li><b>python file.py</b> — run Python script</li>
<li><b>sysinfo</b> — show system info</li>
<li><b>help</b> — full command list</li>
</ul>
""",
        "pyos://settings_browser": """
<h1>⚙️ Browser Settings</h1>
<h2>Current Settings</h2>
<ul>
<li><b>Home page:</b> pyos://home</li>
<li><b>Search engine:</b> PyOS Search (simulated)</li>
<li><b>Font size:</b> 11pt</li>
<li><b>Theme:</b> Follows system theme</li>
<li><b>JavaScript:</b> Enabled (simulated)</li>
<li><b>Cookies:</b> Simulated session storage</li>
<li><b>History:</b> Last 100 pages</li>
</ul>
<p>Full browser settings are managed through the main Settings app.</p>
""",
    }

    def __init__(self, wm: WM, url: Optional[str] = None) -> None:
        self._url          = url or self.HOME_URL
        self._hist:        List[str] = []
        self._fwd_stack:   List[str] = []
        self._bookmarks:   List[Dict[str, str]] = [
            {"title": "Home",   "url": "pyos://home"},
            {"title": "Docs",   "url": "pyos://docs"},
            {"title": "News",   "url": "pyos://news"},
            {"title": "About",  "url": "pyos://about"},
        ]
        self._tabs:        List[str] = [url or self.HOME_URL]
        self._tab_idx      = 0
        self._reader_mode  = False
        super().__init__(wm, "Browser", 60, 40, 960, 660, "🌐", min_w=400, min_h=300)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])
        self._build_navbar(parent)
        self._build_bookmarks_bar(parent)
        self._build_tab_bar(parent)
        self._build_content_area(parent)
        self._build_status(parent)
        self._navigate(self._url, push_hist=False)

    def _build_navbar(self, parent: tk.Frame) -> None:
        nb = tk.Frame(parent, bg=T["panel_bg"], height=44)
        nb.pack(fill="x")
        nb.pack_propagate(False)

        nav_btns = [
            ("◀", self._go_back,    "Back"),
            ("▶", self._go_forward, "Forward"),
            ("⟳", self._reload,     "Reload"),
            ("🏠", self._go_home,   "Home"),
        ]
        for txt, cmd, tip in nav_btns:
            b = tk.Button(
                nb, text=txt, command=cmd,
                bg=T["button_bg"], fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_EMOJI, 12), padx=8,
                cursor="hand2",
                activebackground=T["button_hover"],
            )
            b.pack(side="left", padx=2, pady=6)
            Tooltip(b, tip)

        mksep(nb, "vertical").pack(side="left", fill="y", pady=8, padx=2)

        # Lock icon (https indicator)
        self._lock_lbl = tk.Label(
            nb, text="🔒",
            bg=T["panel_bg"], fg=T["success"],
            font=(FONT_EMOJI, 11),
        )
        self._lock_lbl.pack(side="left", padx=2)

        # URL bar
        self._url_var = tk.StringVar()
        self._url_entry = tk.Entry(
            nb,
            textvariable=self._url_var,
            bg=T["input_bg"], fg=T["text"],
            insertbackground=T["text"],
            relief="flat", bd=6,
            font=(FONT_UI, 10),
            highlightthickness=1,
            highlightcolor=T["input_focus"],
            highlightbackground=T["input_border"],
        )
        self._url_entry.pack(side="left", fill="x", expand=True, padx=6, pady=6)
        self._url_entry.bind("<Return>", lambda e: self._navigate(self._url_var.get()))
        self._url_entry.bind("<FocusIn>", lambda e: self._url_entry.selection_range(0, "end"))

        # Action buttons
        action_btns = [
            ("🔍",  self._find_in_page, "Find in page"),
            ("📖",  self._reader_mode_toggle, "Reader mode"),
            ("🖨️", self._print_page,   "Save page"),
            ("🔖",  self._add_bookmark, "Add bookmark"),
        ]
        for txt, cmd, tip in action_btns:
            b = tk.Button(
                nb, text=txt, command=cmd,
                bg=T["button_bg"], fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_EMOJI, 12), padx=6,
                cursor="hand2",
                activebackground=T["button_hover"],
            )
            b.pack(side="right", padx=1, pady=6)
            Tooltip(b, tip)

    def _build_bookmarks_bar(self, parent: tk.Frame) -> None:
        self._bm_bar = tk.Frame(parent, bg=T["panel_alt"], height=26)
        self._bm_bar.pack(fill="x")
        self._bm_bar.pack_propagate(False)
        self._refresh_bookmarks()

    def _refresh_bookmarks(self) -> None:
        for w in self._bm_bar.winfo_children():
            w.destroy()
        for bm in self._bookmarks[:12]:
            tk.Button(
                self._bm_bar,
                text=bm["title"],
                command=lambda u=bm["url"]: self._navigate(u),
                bg=T["panel_alt"], fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_UI, 8),
                padx=8, pady=2,
                cursor="hand2",
                activebackground=T["menu_hover"],
            ).pack(side="left", pady=2, padx=1)

    def _build_tab_bar(self, parent: tk.Frame) -> None:
        self._tab_bar = tk.Frame(parent, bg=T["panel_bg"], height=28)
        self._tab_bar.pack(fill="x")
        self._tab_bar.pack_propagate(False)
        self._refresh_tabs()

    def _refresh_tabs(self) -> None:
        for w in self._tab_bar.winfo_children():
            w.destroy()
        for i, url in enumerate(self._tabs):
            label = url.split("//")[-1][:20]
            bg    = T["win_bg"] if i == self._tab_idx else T["panel_bg"]
            f     = tk.Frame(self._tab_bar, bg=bg)
            f.pack(side="left")
            tk.Button(
                f, text=label,
                command=lambda idx=i: self._switch_tab(idx),
                bg=bg, fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_UI, 8),
                padx=10, pady=4,
                cursor="hand2",
            ).pack(side="left")
            tk.Button(
                f, text="✕",
                command=lambda idx=i: self._close_tab(idx),
                bg=bg, fg=T["text_muted"],
                relief="flat", bd=0,
                font=(FONT_UI, 8), padx=2,
                cursor="hand2",
            ).pack(side="left")
        tk.Button(
            self._tab_bar, text="＋",
            command=self._new_tab,
            bg=T["panel_bg"], fg=T["text_muted"],
            relief="flat", bd=0,
            font=(FONT_UI, 10), padx=8,
            cursor="hand2",
        ).pack(side="left", pady=2)

    def _build_content_area(self, parent: tk.Frame) -> None:
        self._content_outer = tk.Frame(parent, bg=T["win_bg"])
        self._content_outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(
            self._content_outer, bg=T["win_bg"],
            highlightthickness=0,
        )
        vsb = tk.Scrollbar(
            self._content_outer, orient="vertical",
            command=self._canvas.yview,
        )
        self._canvas.config(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._canvas.pack(fill="both", expand=True)

        self._page_frame = tk.Frame(self._canvas, bg=T["win_bg"])
        self._page_win   = self._canvas.create_window(
            (0, 0), window=self._page_frame, anchor="nw",
        )
        self._page_frame.bind(
            "<Configure>",
            lambda e: self._canvas.config(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.bind(
            "<Configure>",
            lambda e: self._canvas.itemconfig(self._page_win, width=e.width),
        )
        self._canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"),
        )

    def _build_status(self, parent: tk.Frame) -> None:
        sf = tk.Frame(parent, bg=T["status_bg"], height=20)
        sf.pack(fill="x", side="bottom")
        sf.pack_propagate(False)
        self._status_lbl = tk.Label(
            sf, text="Ready",
            bg=T["status_bg"], fg=T["text_muted"],
            font=(FONT_UI, 8), anchor="w", padx=8,
        )
        self._status_lbl.pack(side="left", fill="y")
        self._load_time_lbl = tk.Label(
            sf, text="",
            bg=T["status_bg"], fg=T["text_muted"],
            font=(FONT_UI, 8), padx=8,
        )
        self._load_time_lbl.pack(side="right")

    # ── navigation ────────────────────────────────────────────────────────────

    def _navigate(self, url: str, push_hist: bool = True) -> None:
        if not url:
            return
        url = url.strip()
        # Normalise URL
        if not url.startswith(("pyos://", "http://", "https://", "file://")):
            if "." in url:
                url = "https://" + url
            else:
                url = "pyos://" + url

        if push_hist and self._url:
            self._hist.append(self._url)
            self._fwd_stack.clear()

        self._url = url
        self._url_var.set(url)
        self._status_lbl.config(text=f"Loading {url}…")

        # Update lock icon
        is_secure = url.startswith(("https://", "pyos://", "file://"))
        self._lock_lbl.config(
            text="🔒" if is_secure else "🔓",
            fg=T["success"] if is_secure else T["warning"],
        )

        t0 = time.time()
        self._render_page(url)
        elapsed = time.time() - t0
        self._status_lbl.config(text=f"Loaded: {url}")
        self._load_time_lbl.config(text=f"{elapsed*1000:.0f} ms")

        # Update tab
        if self._tabs:
            self._tabs[self._tab_idx] = url
            self._refresh_tabs()
        self.set_title(url.split("//")[-1][:30] + " — Browser")

    def _render_page(self, url: str) -> None:
        for w in self._page_frame.winfo_children():
            w.destroy()
        self._canvas.yview_moveto(0)

        # Get content
        content = self.PAGES.get(url)
        if not content:
            if url.startswith("file://"):
                path = url[7:]
                try:
                    raw = self.wm.vfs.read(path)
                    content = f"<h1>📄 {path}</h1><pre>{raw}</pre>"
                except Exception:
                    content = f"<h1>404 Not Found</h1><p>File not found: {path}</p>"
            else:
                # Simulated external
                domain = url.split("/")[2] if "//" in url else url
                content = f"""
<h1>🌐 {domain}</h1>
<p>This is a <b>simulated browser</b>. External URLs cannot be fetched.</p>
<p>Showing a placeholder page for: <b>{url}</b></p>
<h2>Available Internal Pages</h2>
<ul>
{''.join(f'<li><a href="{k}">{k}</a></li>' for k in self.PAGES)}
</ul>
"""

        if self._reader_mode:
            # Strip all markup for reader mode
            text = re.sub(r'<[^>]+>', '', content)
            text = re.sub(r'\n{3,}', '\n\n', text)
            self._render_reader(text)
        else:
            self._render_html(content)

    def _render_html(self, html: str) -> None:
        """Simple but capable HTML renderer using Tkinter widgets."""
        p      = self._page_frame
        width  = max(600, self._canvas.winfo_width() - 40 or 800)
        margin = 40

        # Split into blocks
        html = re.sub(r'\n\s*\n', '\n', html)

        in_ul = False
        in_ol = False
        ol_counter = 0
        in_pre = False
        pre_buf: List[str] = []

        lines = html.split("\n")
        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            # Pre block
            if "<pre>" in line.lower():
                in_pre = True
                line   = re.sub(r'<pre>', '', line, flags=re.IGNORECASE)
            if "</pre>" in line.lower():
                in_pre = False
                pre_text = "\n".join(pre_buf) + re.sub(r'</pre>', '', line, flags=re.IGNORECASE)
                pre_buf.clear()
                bg = T["code_bg"]
                pf = tk.Frame(p, bg=bg, padx=12, pady=8)
                pf.pack(fill="x", padx=margin, pady=4)
                tk.Label(pf, text=pre_text.strip(), bg=bg, fg=T["code_fg"],
                         font=(FONT_MONO, 9), anchor="w", justify="left",
                         wraplength=width-margin*2-24).pack(anchor="w")
                continue
            if in_pre:
                pre_buf.append(line)
                continue

            # Headings
            for level, (tag_open, size, weight, pad_top, pad_bot) in enumerate([
                ("<h1>", 18, "bold", 16, 4),
                ("<h2>", 13, "bold", 12, 4),
                ("<h3>", 11, "bold",  8, 2),
            ], 1):
                pat = re.compile(rf'<h{level}>(.*?)</h{level}>', re.IGNORECASE | re.DOTALL)
                m   = pat.search(line)
                if m:
                    text = re.sub(r'<[^>]+>', '', m.group(1))
                    tk.Label(p, text=text, bg=T["win_bg"], fg=T["text"],
                             font=(FONT_UI, size, weight), anchor="w",
                             wraplength=width-margin).pack(
                        fill="x", padx=margin, pady=(pad_top, pad_bot)
                    )
                    if level == 1:
                        tk.Frame(p, bg=T["accent"], height=2).pack(
                            fill="x", padx=margin, pady=(0, 8)
                        )
                    break

            # Paragraph
            if re.match(r'<p>', line, re.IGNORECASE):
                m = re.match(r'<p>(.*?)</p>', line, re.IGNORECASE | re.DOTALL)
                if m:
                    self._render_inline(p, m.group(1), margin, width)

            # List items
            elif re.match(r'<ul>', line, re.IGNORECASE):
                in_ul = True; in_ol = False; ol_counter = 0
            elif re.match(r'</ul>', line, re.IGNORECASE):
                in_ul = False
            elif re.match(r'<ol>', line, re.IGNORECASE):
                in_ol = True; in_ul = False; ol_counter = 0
            elif re.match(r'</ol>', line, re.IGNORECASE):
                in_ol = False
            elif re.match(r'<li>', line, re.IGNORECASE):
                m = re.match(r'<li>(.*?)</li>', line, re.IGNORECASE | re.DOTALL)
                content_text = m.group(1) if m else re.sub(r'<[^>]+>', '', line)
                if in_ol:
                    ol_counter += 1
                    bullet = f"{ol_counter}."
                else:
                    bullet = "•"
                row = tk.Frame(p, bg=T["win_bg"])
                row.pack(fill="x", padx=margin + 12, pady=1)
                tk.Label(row, text=bullet, bg=T["win_bg"], fg=T["accent"],
                         font=(FONT_UI, 10), width=3).pack(side="left")
                self._render_inline(row, content_text, 0, width - margin - 40, side="left")

            # Horizontal rule
            elif re.match(r'<hr', line, re.IGNORECASE):
                tk.Frame(p, bg=T["separator"], height=1).pack(
                    fill="x", padx=margin, pady=8
                )

        # Extra bottom padding
        tk.Label(p, text="", bg=T["win_bg"], height=2).pack()

    def _render_inline(
        self,
        parent:  tk.Widget,
        html:    str,
        margin:  int,
        width:   int,
        side:    str = "top",
    ) -> None:
        """Render a paragraph with inline formatting (bold, links, code)."""
        if side == "left":
            # Inline flow
            parts = re.split(r'(<[^>]+>.*?</[^>]+>)', html)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if re.match(r'<b>(.*?)</b>', part, re.IGNORECASE | re.DOTALL):
                    m    = re.match(r'<b>(.*?)</b>', part, re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<[^>]+>', '', m.group(1))
                    tk.Label(parent, text=text, bg=parent.cget("bg"), fg=T["text"],
                             font=(FONT_UI, 10, "bold")).pack(side="left")
                elif re.match(r'<a href="(.*?)">(.*?)</a>', part, re.IGNORECASE | re.DOTALL):
                    m    = re.match(r'<a href="(.*?)">(.*?)</a>', part, re.IGNORECASE | re.DOTALL)
                    href = m.group(1); text = re.sub(r'<[^>]+>', '', m.group(2))
                    lbl  = tk.Label(parent, text=text, bg=parent.cget("bg"), fg=T["link"],
                                    font=(FONT_UI, 10, "underline"), cursor="hand2")
                    lbl.pack(side="left")
                    lbl.bind("<Button-1>", lambda e, u=href: self._navigate(u))
                    lbl.bind("<Enter>", lambda e: self._status_lbl.config(text=href))
                    lbl.bind("<Leave>", lambda e: self._status_lbl.config(text=""))
                elif re.match(r'<code>(.*?)</code>', part, re.IGNORECASE | re.DOTALL):
                    m    = re.match(r'<code>(.*?)</code>', part, re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<[^>]+>', '', m.group(1))
                    tk.Label(parent, text=text, bg=T["code_bg"], fg=T["code_fg"],
                             font=(FONT_MONO, 9)).pack(side="left", padx=2)
                else:
                    text = re.sub(r'<[^>]+>', '', part)
                    if text:
                        tk.Label(parent, text=text, bg=parent.cget("bg"), fg=T["text"],
                                 font=(FONT_UI, 10)).pack(side="left")
        else:
            # Block rendering: parse inline links/bold in a single label
            # (simplified for block-level paragraphs)
            f = tk.Frame(parent, bg=T["win_bg"])
            f.pack(fill="x", padx=margin, pady=3)
            parts = re.split(r'(<b>.*?</b>|<a href=".*?">.*?</a>|<code>.*?</code>)', html)
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                if re.match(r'<b>(.*?)</b>', part, re.IGNORECASE | re.DOTALL):
                    m    = re.match(r'<b>(.*?)</b>', part, re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<[^>]+>', '', m.group(1))
                    tk.Label(f, text=text, bg=T["win_bg"], fg=T["text"],
                             font=(FONT_UI, 10, "bold")).pack(side="left")
                elif re.match(r'<a href="(.*?)">(.*?)</a>', part, re.IGNORECASE | re.DOTALL):
                    m    = re.match(r'<a href="(.*?)">(.*?)</a>', part, re.IGNORECASE | re.DOTALL)
                    href = m.group(1); text = re.sub(r'<[^>]+>', '', m.group(2))
                    lbl  = tk.Label(f, text=text, bg=T["win_bg"], fg=T["link"],
                                    font=(FONT_UI, 10, "underline"), cursor="hand2")
                    lbl.pack(side="left")
                    lbl.bind("<Button-1>", lambda e, u=href: self._navigate(u))
                    lbl.bind("<Enter>", lambda e: self._status_lbl.config(text=href))
                    lbl.bind("<Leave>", lambda e: self._status_lbl.config(text=""))
                elif re.match(r'<code>(.*?)</code>', part, re.IGNORECASE | re.DOTALL):
                    m    = re.match(r'<code>(.*?)</code>', part, re.IGNORECASE | re.DOTALL)
                    text = re.sub(r'<[^>]+>', '', m.group(1))
                    tk.Label(f, text=text, bg=T["code_bg"], fg=T["code_fg"],
                             font=(FONT_MONO, 9)).pack(side="left", padx=2)
                else:
                    text = re.sub(r'<[^>]+>', '', part)
                    if text:
                        tk.Label(f, text=text, bg=T["win_bg"], fg=T["text"],
                                 font=(FONT_UI, 10),
                                 wraplength=width-margin-10, justify="left").pack(side="left")

    def _render_reader(self, text: str) -> None:
        """Clean reader mode — plain text in a comfortable reading font."""
        p = self._page_frame
        bg = T["panel_alt"]
        p.config(bg=bg)

        outer = tk.Frame(p, bg=bg)
        outer.pack(expand=True, padx=60, pady=20)

        tk.Label(
            outer, text="📖 Reader Mode",
            bg=bg, fg=T["text_muted"], font=(FONT_UI, 9),
        ).pack(anchor="e")

        tk.Label(
            outer, text=text,
            bg=bg, fg=T["text"],
            font=(FONT_UI, 13), wraplength=680,
            justify="left", anchor="w",
        ).pack(anchor="w")

    def _go_back(self) -> None:
        if self._hist:
            self._fwd_stack.append(self._url)
            self._navigate(self._hist.pop(), push_hist=False)

    def _go_forward(self) -> None:
        if self._fwd_stack:
            self._navigate(self._fwd_stack.pop(), push_hist=True)

    def _reload(self) -> None:
        self._render_page(self._url)

    def _go_home(self) -> None:
        self._navigate(self.HOME_URL)

    def _add_bookmark(self) -> None:
        title = simpledialog.askstring(
            "Add Bookmark", "Bookmark title:",
            parent=self.wm.root,
            initialvalue=self._url.split("//")[-1],
        )
        if title:
            self._bookmarks.append({"title": title, "url": self._url})
            self._refresh_bookmarks()
            self.wm.notifs.send("Browser", f"Bookmarked: {title}", icon="🔖")

    def _new_tab(self) -> None:
        self._tabs.append(self.HOME_URL)
        self._tab_idx = len(self._tabs) - 1
        self._refresh_tabs()
        self._navigate(self.HOME_URL, push_hist=False)

    def _close_tab(self, idx: int) -> None:
        if len(self._tabs) == 1:
            return
        self._tabs.pop(idx)
        self._tab_idx = max(0, min(self._tab_idx, len(self._tabs) - 1))
        self._refresh_tabs()
        self._navigate(self._tabs[self._tab_idx], push_hist=False)

    def _switch_tab(self, idx: int) -> None:
        self._tab_idx = idx
        self._refresh_tabs()
        self._navigate(self._tabs[idx], push_hist=False)

    def _find_in_page(self) -> None:
        d = tk.Toplevel(self.wm.root)
        d.title("Find in Page")
        d.config(bg=T["win_bg"])
        d.geometry("340x60")
        d.wm_attributes("-topmost", True)
        d.overrideredirect(True)
        # Position near bottom of content
        d.geometry(f"340x60+{self.wm.root.winfo_rootx()+200}+{self.wm.root.winfo_rooty()+500}")
        f = tk.Frame(d, bg=T["win_bg"])
        f.pack(fill="both", expand=True, padx=8, pady=8)
        tk.Label(f, text="Find:", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(side="left")
        v = tk.StringVar()
        e = mkentry(f, textvariable=v, width=22)
        e.pack(side="left", padx=6)
        tk.Button(f, text="✕", command=d.destroy,
                  bg=T["button_bg"], fg=T["text"], relief="flat", bd=0,
                  font=(FONT_UI, 9), cursor="hand2").pack(side="right")
        e.focus_set()

    def _reader_mode_toggle(self) -> None:
        self._reader_mode = not self._reader_mode
        self._render_page(self._url)

    def _print_page(self) -> None:
        content = self.PAGES.get(self._url, f"Page: {self._url}")
        clean   = re.sub(r'<[^>]+>', '', content)
        fname   = re.sub(r'[^\w]', '_', self._url.split("//")[-1]) + ".txt"
        path    = f"/home/user/Downloads/{fname}"
        self.wm.vfs.write(path, clean)
        self.wm.notifs.send("Browser", f"Page saved: {path}", icon="🖨️")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 19 — MUSIC PLAYER APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class MusicPlayerApp(BaseWin):
    """
    Full-featured music player with:
      • Simulated playlist (14 tracks)
      • Animated waveform visualiser (canvas-drawn, 60 fps)
      • Play / pause / previous / next / shuffle / repeat
      • Volume slider and mute
      • Seek bar with click-to-seek
      • Playlist management (add / remove / move)
      • Track info panel (title, artist, genre, duration)
      • Progress bar + timestamps
      • Spectrum analyser mode
      • Equaliser bands (visual)
    """

    TRACKS: List[Dict[str, Any]] = [
        {"title": "Cyber Dreams",       "artist": "PyOS Audio",   "genre": "Electronic", "dur": 213, "bpm": 128},
        {"title": "Digital Rain",        "artist": "Tkinter Band", "genre": "Ambient",    "dur": 187, "bpm": 90},
        {"title": "Electric Pulse",      "artist": "ByteWave",     "genre": "Synthwave",  "dur": 234, "bpm": 120},
        {"title": "Neon Nights",         "artist": "PyOS Audio",   "genre": "Electronic", "dur": 198, "bpm": 132},
        {"title": "Binary Sunset",       "artist": "CodeBeats",    "genre": "Chillout",   "dur": 245, "bpm": 85},
        {"title": "Terminal Blues",      "artist": "Tkinter Band", "genre": "Blues",      "dur": 172, "bpm": 80},
        {"title": "Stack Overflow",      "artist": "ByteWave",     "genre": "Rock",       "dur": 203, "bpm": 140},
        {"title": "Recursive Rhythm",    "artist": "PyOS Audio",   "genre": "Techno",     "dur": 219, "bpm": 145},
        {"title": "Heap Sort Hustle",    "artist": "CodeBeats",    "genre": "Jazz",       "dur": 188, "bpm": 110},
        {"title": "Async Anthem",        "artist": "ByteWave",     "genre": "Pop",        "dur": 227, "bpm": 118},
        {"title": "Lambda Love",         "artist": "Tkinter Band", "genre": "Acoustic",   "dur": 156, "bpm": 76},
        {"title": "Exception Handler",   "artist": "PyOS Audio",   "genre": "Metal",      "dur": 241, "bpm": 160},
        {"title": "Memory Leak Melody",  "artist": "CodeBeats",    "genre": "Classical",  "dur": 195, "bpm": 72},
        {"title": "Kernel Panic",        "artist": "ByteWave",     "genre": "Punk",       "dur": 210, "bpm": 180},
    ]

    VIZ_MODES = ["Waveform", "Spectrum", "Bars", "Circle"]

    def __init__(self, wm: WM) -> None:
        self._cur      = 0
        self._playing  = False
        self._progress = 0.0       # 0.0 – 1.0
        self._vol      = 0.75
        self._muted    = False
        self._shuffle  = False
        self._repeat   = False     # False | "one" | "all"
        self._repeat_idx = 0       # cycle through repeat modes
        self._viz_mode = 0         # index into VIZ_MODES
        self._af       = 0         # animation frame counter
        self._eq_bands = [0.6, 0.7, 0.8, 0.75, 0.65, 0.7, 0.8, 0.85]
        super().__init__(wm, "Music Player", 400, 80, 700, 540, "🎵", min_w=500, min_h=420)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])
        self._build_playlist_panel(parent)
        self._build_player_panel(parent)
        self._start_animation()

    # ── playlist panel ────────────────────────────────────────────────────────

    def _build_playlist_panel(self, parent: tk.Frame) -> None:
        pf = tk.Frame(parent, bg=T["panel_bg"], width=230)
        pf.pack(side="left", fill="y")
        pf.pack_propagate(False)

        # Header
        hdr = tk.Frame(pf, bg=T["panel_bg"])
        hdr.pack(fill="x", padx=8, pady=(8, 2))
        tk.Label(hdr, text="PLAYLIST",
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8, "bold")).pack(side="left")
        tk.Label(hdr, text=f"{len(self.TRACKS)} tracks",
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8)).pack(side="right")

        mksep(pf).pack(fill="x", padx=8)

        # Scrollable list
        sf = ScrollableFrame(pf, bg=T["panel_bg"])
        sf.pack(fill="both", expand=True)
        self._playlist_inner = sf.inner
        self._track_rows:  List[tk.Frame] = []

        for i, track in enumerate(self.TRACKS):
            self._add_track_row(i, track)

        # Add track button (simulated)
        mksep(pf).pack(fill="x", padx=8, pady=4)
        mkbtn(pf, "＋  Add Track", self._add_track_dialog).pack(
            fill="x", padx=8, pady=(0, 8)
        )

    def _add_track_row(self, i: int, track: Dict[str, Any]) -> None:
        dur = f"{track['dur'] // 60}:{track['dur'] % 60:02d}"
        row = tk.Frame(self._playlist_inner, bg=T["panel_bg"], cursor="hand2")
        row.pack(fill="x")
        self._track_rows.append(row)

        # Number
        tk.Label(row, text=f"{i+1:2d}",
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_MONO, 8), width=3).pack(side="left", padx=(4, 2), pady=4)

        # Title + artist
        info_f = tk.Frame(row, bg=T["panel_bg"])
        info_f.pack(side="left", fill="x", expand=True)
        tk.Label(info_f, text=track["title"][:22],
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 9), anchor="w").pack(anchor="w")
        tk.Label(info_f, text=track["artist"],
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 7), anchor="w").pack(anchor="w")

        # Duration
        tk.Label(row, text=dur,
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8), padx=4).pack(side="right")

        # Bindings
        for w in (row, info_f, *info_f.winfo_children(), *row.winfo_children()):
            w.bind("<Double-Button-1>", lambda e, idx=i: self._play_track(idx))
            w.bind("<Enter>",           lambda e, r=row: r.config(bg=T["menu_hover"]))
            w.bind("<Leave>",           lambda e, r=row: r.config(bg=T["panel_bg"]))

    def _add_track_dialog(self) -> None:
        title = simpledialog.askstring("Add Track", "Track title:", parent=self.wm.root)
        if title:
            artist = simpledialog.askstring("Add Track", "Artist:", parent=self.wm.root) or "Unknown"
            new_track = {
                "title": title, "artist": artist, "genre": "Unknown",
                "dur": random.randint(120, 300), "bpm": random.randint(70, 180),
            }
            self.TRACKS.append(new_track)
            self._add_track_row(len(self.TRACKS) - 1, new_track)
            self.wm.notifs.send("Music", f"Added: {title}", icon="🎵")

    # ── player panel ──────────────────────────────────────────────────────────

    def _build_player_panel(self, parent: tk.Frame) -> None:
        pf = tk.Frame(parent, bg=T["win_bg"])
        pf.pack(side="left", fill="both", expand=True)

        # Visualiser canvas
        self.viz = tk.Canvas(pf, bg="#050510", height=200, highlightthickness=0)
        self.viz.pack(fill="x", padx=10, pady=10)

        # Viz mode selector
        viz_f = tk.Frame(pf, bg=T["win_bg"])
        viz_f.pack(fill="x", padx=10, pady=(0, 4))
        tk.Label(viz_f, text="Visualiser:",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8)).pack(side="left")
        for i, mode in enumerate(self.VIZ_MODES):
            tk.Button(
                viz_f, text=mode,
                command=lambda idx=i: setattr(self, "_viz_mode", idx),
                bg=T["button_bg"], fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_UI, 8), padx=6, pady=2,
                cursor="hand2",
                activebackground=T["button_hover"],
            ).pack(side="left", padx=2)

        # Track info
        info_f = tk.Frame(pf, bg=T["win_bg"])
        info_f.pack(fill="x", padx=14, pady=(6, 2))

        self._title_lbl = tk.Label(
            info_f, text=self.TRACKS[0]["title"],
            bg=T["win_bg"], fg=T["text"],
            font=(FONT_UI, 14, "bold"), anchor="center",
        )
        self._title_lbl.pack(fill="x")

        self._meta_lbl = tk.Label(
            info_f,
            text=f"{self.TRACKS[0]['artist']}  •  {self.TRACKS[0]['genre']}  •  {self.TRACKS[0]['bpm']} BPM",
            bg=T["win_bg"], fg=T["text_muted"],
            font=(FONT_UI, 9), anchor="center",
        )
        self._meta_lbl.pack(fill="x")

        # Seek bar
        seek_f = tk.Frame(pf, bg=T["win_bg"])
        seek_f.pack(fill="x", padx=14, pady=(8, 2))

        self._time_lbl = tk.Label(
            seek_f, text="0:00",
            bg=T["win_bg"], fg=T["text_muted"],
            font=(FONT_MONO, 9),
        )
        self._time_lbl.pack(side="left")

        self._seek_canvas = tk.Canvas(
            seek_f, bg=T["button_bg"], height=8,
            cursor="hand2", highlightthickness=0,
        )
        self._seek_canvas.pack(side="left", fill="x", expand=True, padx=8)
        self._seek_canvas.bind("<Button-1>", self._seek_click)
        self._seek_canvas.bind("<B1-Motion>", self._seek_drag)

        self._dur_lbl = tk.Label(
            seek_f, text="0:00",
            bg=T["win_bg"], fg=T["text_muted"],
            font=(FONT_MONO, 9),
        )
        self._dur_lbl.pack(side="right")

        # Controls
        ctrl_f = tk.Frame(pf, bg=T["win_bg"])
        ctrl_f.pack(fill="x", padx=10, pady=8)

        self._ctrl_btns: Dict[str, tk.Button] = {}
        ctrl_specs = [
            ("⇄",  self._toggle_shuffle, "shuf"),
            ("⏮",  self._prev,           "prev"),
            ("⏵",  self._play_pause,     "play"),
            ("⏭",  self._next,           "next"),
            ("↻",  self._toggle_repeat,  "rep"),
        ]
        for txt, cmd, key in ctrl_specs:
            is_main = key == "play"
            b = tk.Button(
                ctrl_f, text=txt, command=cmd,
                bg=T["accent"] if is_main else T["button_bg"],
                fg="#ffffff" if is_main else T["text"],
                relief="flat", bd=0,
                font=(FONT_EMOJI, 20 if is_main else 14),
                padx=16 if is_main else 10,
                pady=8,
                cursor="hand2",
                activebackground=darken(T["accent"]) if is_main else T["button_hover"],
            )
            b.pack(side="left", padx=4)
            self._ctrl_btns[key] = b

        # Volume
        vol_f = tk.Frame(pf, bg=T["win_bg"])
        vol_f.pack(fill="x", padx=14, pady=4)

        self._mute_btn = tk.Button(
            vol_f, text="🔊",
            command=self._toggle_mute,
            bg=T["win_bg"], fg=T["text"],
            relief="flat", bd=0,
            font=(FONT_EMOJI, 11), padx=4,
            cursor="hand2",
            activebackground=T["win_bg"],
        )
        self._mute_btn.pack(side="left")

        self._vol_var = tk.DoubleVar(value=self._vol)
        vol_slider = ttk.Scale(
            vol_f, from_=0, to=1,
            orient="horizontal",
            variable=self._vol_var,
            command=lambda v: setattr(self, "_vol", float(v)),
        )
        vol_slider.pack(side="left", fill="x", expand=True, padx=6)

        tk.Label(
            vol_f, textvariable=tk.StringVar(value="100%"),
            bg=T["win_bg"], fg=T["text_muted"],
            font=(FONT_UI, 8),
        ).pack(side="right")
        self._vol_pct_var = tk.StringVar(value="75%")
        self._vol_var.trace(
            "w",
            lambda *_: self._vol_pct_var.set(f"{int(self._vol_var.get()*100)}%"),
        )
        tk.Label(
            vol_f, textvariable=self._vol_pct_var,
            bg=T["win_bg"], fg=T["text_muted"],
            font=(FONT_UI, 8),
        ).pack(side="right")

        # EQ bands (decorative)
        eq_f = tk.Frame(pf, bg=T["win_bg"])
        eq_f.pack(fill="x", padx=14, pady=(4, 8))
        tk.Label(eq_f, text="EQ", bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8)).pack(side="left", padx=(0, 6))
        self._eq_sliders: List[ttk.Scale] = []
        for i, band_val in enumerate(self._eq_bands):
            s = ttk.Scale(
                eq_f, from_=0, to=1,
                orient="vertical", length=40,
            )
            s.set(band_val)
            s.pack(side="left", padx=2)
            self._eq_sliders.append(s)
            band_labels = ["32", "64", "125", "250", "500", "1k", "2k", "4k"]
            tk.Label(eq_f, text=band_labels[i] if i < 8 else "",
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 6)).pack(side="left")

    # ── playback control ──────────────────────────────────────────────────────

    def _play_track(self, idx: int) -> None:
        self._cur      = idx
        self._progress = 0.0
        self._playing  = True
        self._update_track_ui()
        self._ctrl_btns["play"].config(text="⏸")

    def _play_pause(self) -> None:
        self._playing = not self._playing
        self._ctrl_btns["play"].config(text="⏸" if self._playing else "⏵")

    def _prev(self) -> None:
        if self._progress > 0.05:
            self._progress = 0.0
        else:
            if self._shuffle:
                self._cur = random.randint(0, len(self.TRACKS) - 1)
            else:
                self._cur = (self._cur - 1) % len(self.TRACKS)
            self._progress = 0.0
        self._update_track_ui()

    def _next(self) -> None:
        if self._shuffle:
            self._cur = random.randint(0, len(self.TRACKS) - 1)
        else:
            self._cur = (self._cur + 1) % len(self.TRACKS)
        self._progress = 0.0
        self._update_track_ui()

    def _toggle_shuffle(self) -> None:
        self._shuffle = not self._shuffle
        self._ctrl_btns["shuf"].config(
            bg=T["accent"] if self._shuffle else T["button_bg"]
        )

    def _toggle_repeat(self) -> None:
        modes     = [False, "one", "all"]
        icons     = ["↻", "🔂", "🔁"]
        self._repeat_idx = (self._repeat_idx + 1) % 3
        self._repeat     = modes[self._repeat_idx]
        self._ctrl_btns["rep"].config(
            text=icons[self._repeat_idx],
            bg=T["accent"] if self._repeat else T["button_bg"],
        )

    def _toggle_mute(self) -> None:
        self._muted = not self._muted
        self._mute_btn.config(text="🔇" if self._muted else "🔊")

    def _seek_click(self, e: tk.Event) -> None:
        w = self._seek_canvas.winfo_width() or 1
        self._progress = max(0.0, min(1.0, e.x / w))

    def _seek_drag(self, e: tk.Event) -> None:
        self._seek_click(e)

    def _update_track_ui(self) -> None:
        track = self.TRACKS[self._cur]
        self._title_lbl.config(text=track["title"])
        self._meta_lbl.config(
            text=f"{track['artist']}  •  {track['genre']}  •  {track['bpm']} BPM"
        )
        # Highlight current in playlist
        for i, row in enumerate(self._track_rows):
            is_cur = i == self._cur
            try:
                bg = T["accent"] if is_cur else T["panel_bg"]
                row.config(bg=bg)
                for child in row.winfo_children():
                    child.config(bg=bg)
            except Exception:
                pass

    # ── animation loop ────────────────────────────────────────────────────────

    def _start_animation(self) -> None:
        self._update_track_ui()
        self._animate()

    def _animate(self) -> None:
        if not self._out.winfo_exists():
            return
        if self._playing:
            dur = self.TRACKS[self._cur]["dur"]
            self._progress += 1 / (dur * 30)  # ~30 fps
            if self._progress >= 1.0:
                if self._repeat == "one":
                    self._progress = 0.0
                elif self._repeat == "all":
                    self._next()
                else:
                    self._next()
                    if not self._shuffle and self._cur == 0:
                        self._playing = False
                        return
        self._draw_viz()
        self._draw_seek()
        self._update_time_labels()
        self._af += 1
        if self._out.winfo_exists():
            self.wm.root.after(33, self._animate)

    def _draw_viz(self) -> None:
        c   = self.viz
        W   = c.winfo_width()  or 460
        H   = c.winfo_height() or 200
        c.delete("all")

        # Background gradient
        for i in range(H):
            t = i / H
            r = int(5  + t * 15)
            g = int(5  + t * 10)
            b = int(16 + t * 30)
            c.create_line(0, i, W, i, fill=f"#{r:02x}{g:02x}{b:02x}")

        if not self._playing:
            c.create_text(W//2, H//2, text="⏸  Paused",
                          fill=T["text_muted"], font=(FONT_UI, 14))
            return

        eff_vol  = 0.0 if self._muted else self._vol
        bpm      = self.TRACKS[self._cur]["bpm"]
        beat_period = 60 / bpm
        beat_phase  = (self._af * 0.033) % beat_period
        beat_pulse  = max(0, 1 - beat_phase / beat_period * 2)

        mode = self.VIZ_MODES[self._viz_mode]

        if mode == "Waveform":
            self._draw_waveform(c, W, H, eff_vol, beat_pulse)
        elif mode == "Spectrum":
            self._draw_spectrum(c, W, H, eff_vol, beat_pulse)
        elif mode == "Bars":
            self._draw_bars(c, W, H, eff_vol, beat_pulse)
        elif mode == "Circle":
            self._draw_circle(c, W, H, eff_vol, beat_pulse)

        # Track name overlay
        c.create_text(8, 8, text=self.TRACKS[self._cur]["title"],
                      fill="#555555", font=(FONT_UI, 9), anchor="nw")
        # Progress line
        px = int(W * self._progress)
        c.create_line(px, H-3, px, H, fill=T["accent"], width=2)

    def _draw_waveform(self, c: tk.Canvas, W: int, H: int,
                       vol: float, beat: float) -> None:
        t     = self._af * 0.1
        mid   = H // 2
        pts   = []
        n     = 120
        for i in range(n):
            x  = i * W / n
            # Compound sine wave
            y  = (math.sin(i * 0.18 + t) * 0.5 +
                  math.sin(i * 0.35 + t * 1.3) * 0.3 +
                  math.sin(i * 0.07 + t * 0.7) * 0.2)
            y  = mid + y * mid * 0.75 * vol * (1 + beat * 0.3)
            pts.extend([x, y])
        if len(pts) >= 4:
            c.create_line(pts, fill=T["accent"], width=2, smooth=True)
        # Mirror
        pts_m = []
        for i in range(0, len(pts), 2):
            pts_m.extend([pts[i], H - pts[i+1] + mid * 0 ])
        if len(pts_m) >= 4:
            c.create_line(pts_m, fill=T["accent2"], width=1, smooth=True)

    def _draw_spectrum(self, c: tk.Canvas, W: int, H: int,
                       vol: float, beat: float) -> None:
        n_bands = 32
        t       = self._af * 0.08
        for i in range(n_bands):
            x      = i * W / n_bands
            bw     = W / n_bands - 2
            # Height based on "frequency content"
            base   = (math.sin(i * 0.5 + t) * 0.5 + 0.5)
            peak   = (math.sin(i * 0.9 - t * 1.2) * 0.5 + 0.5) * 0.6
            height = (base + peak) * H * 0.8 * vol * (1 + beat * 0.2)
            height = max(2, height)
            # Colour gradient by frequency
            ratio  = i / n_bands
            r      = int(56  + ratio * 180)
            g      = int(139 - ratio * 80)
            b      = int(253 - ratio * 150)
            col    = f"#{min(255,r):02x}{max(0,g):02x}{max(0,b):02x}"
            c.create_rectangle(
                x, H - height, x + bw, H,
                fill=col, outline="",
            )
            # Peak dot
            c.create_rectangle(
                x, H - height - 3, x + bw, H - height,
                fill="#ffffff", outline="",
            )

    def _draw_bars(self, c: tk.Canvas, W: int, H: int,
                   vol: float, beat: float) -> None:
        n  = 20
        t  = self._af * 0.12
        bw = W / n
        for i in range(n):
            x  = i * bw
            h  = (math.sin(i * 0.4 + t) * 0.5 + 0.5) * H * 0.85 * vol
            h  = max(3, h)
            colors = [T["chart1"], T["chart2"], T["chart3"], T["chart4"], T["chart5"]]
            col    = colors[i % len(colors)]
            # Bar
            c.create_rectangle(x + 2, H - h, x + bw - 2, H, fill=col, outline="")
            # Beat flash at top
            if beat > 0.5 and i % 4 == (self._af // 10) % 4:
                c.create_rectangle(x + 2, H - h - 4, x + bw - 2, H - h, fill="#ffffff", outline="")

    def _draw_circle(self, c: tk.Canvas, W: int, H: int,
                     vol: float, beat: float) -> None:
        cx   = W // 2
        cy   = H // 2
        base_r = min(W, H) // 4
        t    = self._af * 0.06
        n    = 90
        pts  = []
        for i in range(n + 1):
            angle = 2 * math.pi * i / n
            r     = base_r + math.sin(i * 6 + t) * base_r * 0.4 * vol
            r    *= 1 + beat * 0.15
            x     = cx + r * math.cos(angle)
            y     = cy + r * math.sin(angle)
            pts.extend([x, y])
        if len(pts) >= 4:
            c.create_polygon(pts, outline=T["accent"], fill="", width=2, smooth=True)
        # Inner glow
        gr = base_r * 0.6 * (1 + beat * 0.3)
        c.create_oval(cx - gr, cy - gr, cx + gr, cy + gr,
                      outline=T["accent2"], fill="", width=1)
        # Center dot
        c.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill=T["accent"], outline="")
        # Album icon
        c.create_text(cx, cy, text="🎵", font=(FONT_EMOJI, 12), fill="#888888")

    def _draw_seek(self) -> None:
        c = self._seek_canvas
        W = c.winfo_width() or 300
        c.delete("all")
        c.create_rectangle(0, 0, W, 8, fill=T["button_bg"], outline="")
        filled = int(W * self._progress)
        if filled > 0:
            c.create_rectangle(0, 0, filled, 8, fill=T["accent"], outline="")
        # Thumb
        c.create_oval(filled - 6, -1, filled + 6, 9, fill=T["accent"], outline=T["win_bg"], width=2)

    def _update_time_labels(self) -> None:
        dur = self.TRACKS[self._cur]["dur"]
        elapsed = int(dur * self._progress)
        self._time_lbl.config(text=f"{elapsed // 60}:{elapsed % 60:02d}")
        self._dur_lbl.config(text=f"{dur // 60}:{dur % 60:02d}")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 20 — PAINT STUDIO APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class PaintApp(BaseWin):
    """
    Full-featured paint application with:
      • 12 drawing tools: pencil, brush, eraser, line, rect, oval,
        rounded-rect, polygon, fill, text, eyedropper, spray
      • Colour picker + 20-colour palette
      • Foreground / background colour swatches
      • Adjustable brush size (1-80px)
      • Opacity control
      • Grid overlay toggle
      • Canvas resize dialog
      • Undo / redo stack (postscript-based)
      • Zoom in / out
      • Save canvas to VFS (PostScript)
      • Status bar with cursor position
    """

    TOOLS = [
        ("✏️",  "pencil",    "Pencil (free draw)"),
        ("🖌️", "brush",     "Brush (thick stroke)"),
        ("🧹",  "eraser",    "Eraser"),
        ("╱",   "line",      "Straight line"),
        ("▭",   "rect",      "Rectangle (outline)"),
        ("▬",   "rect_fill", "Rectangle (filled)"),
        ("◯",   "oval",      "Oval (outline)"),
        ("⬡",   "poly",      "Polygon"),
        ("→",   "arrow",     "Arrow"),
        ("🪣",  "fill",      "Fill bucket"),
        ("T",   "text",      "Text tool"),
        ("💉",  "eyedrop",   "Eyedropper"),
        ("💦",  "spray",     "Spray paint"),
    ]

    PALETTE = [
        "#ffffff","#000000","#808080","#c0c0c0",
        "#ff0000","#800000","#ff8000","#804000",
        "#ffff00","#808000","#00ff00","#008000",
        "#00ffff","#008080","#0000ff","#000080",
        "#ff00ff","#800080","#ff80ff","#8080ff",
    ]

    def __init__(self, wm: WM) -> None:
        self._tool       = "pencil"
        self._fg_color   = "#e6edf3"
        self._bg_color   = "#0d1117"
        self._size       = 3
        self._opacity    = 1.0
        self._lx         = self._ly = 0
        self._sx         = self._sy = 0
        self._prev_item: Optional[int] = None
        self._poly_pts:  List[Tuple[float, float]] = []
        self._undo_stack: List[str] = []
        self._redo_stack: List[str] = []
        self._show_grid  = False
        self._zoom       = 1.0
        self._canvas_w   = 1200
        self._canvas_h   = 800
        super().__init__(wm, "Paint Studio", 50, 55, 980, 680, "🎨", min_w=500, min_h=400)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["panel_bg"])
        self._build_toolbar(parent)
        self._build_canvas_area(parent)
        self._build_status_bar(parent)

    # ── toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self, parent: tk.Frame) -> None:
        tb = tk.Frame(parent, bg=T["panel_bg"], height=48)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        # Tools
        self._tool_btns: Dict[str, tk.Button] = {}
        tools_f = tk.Frame(tb, bg=T["panel_bg"])
        tools_f.pack(side="left", padx=4)
        for emoji, key, tip in self.TOOLS:
            b = tk.Button(
                tools_f, text=emoji,
                command=partial(self._select_tool, key),
                bg=T["accent"] if key == self._tool else T["button_bg"],
                fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_EMOJI, 12),
                padx=5, pady=4,
                cursor="hand2",
                activebackground=T["button_hover"],
            )
            b.pack(side="left", padx=1, pady=4)
            Tooltip(b, tip)
            self._tool_btns[key] = b

        mksep(tb, "vertical").pack(side="left", fill="y", pady=6, padx=4)

        # Colour swatches
        sw_f = tk.Frame(tb, bg=T["panel_bg"])
        sw_f.pack(side="left", padx=4)

        # Background swatch (behind)
        self._bg_sw = tk.Label(
            sw_f, bg=self._bg_color,
            width=3, relief="solid", bd=1, cursor="hand2",
        )
        self._bg_sw.place(x=14, y=14, width=22, height=22)
        self._bg_sw.bind("<Button-1>", lambda e: self._pick_color("bg"))

        # Foreground swatch (front)
        self._fg_sw = tk.Label(
            sw_f, bg=self._fg_color,
            width=3, relief="solid", bd=1, cursor="hand2",
        )
        self._fg_sw.pack(padx=(0, 20), pady=4, ipady=10)
        self._fg_sw.bind("<Button-1>", lambda e: self._pick_color("fg"))

        # Swap colours button
        tk.Button(
            sw_f, text="⇄",
            command=self._swap_colors,
            bg=T["panel_bg"], fg=T["text"],
            relief="flat", bd=0,
            font=(FONT_UI, 10), padx=2,
            cursor="hand2",
        ).pack(side="left")

        # Palette
        pal_f = tk.Frame(tb, bg=T["panel_bg"])
        pal_f.pack(side="left", padx=4)
        row1 = tk.Frame(pal_f, bg=T["panel_bg"])
        row1.pack()
        row2 = tk.Frame(pal_f, bg=T["panel_bg"])
        row2.pack()
        for i, col in enumerate(self.PALETTE):
            row = row1 if i < 10 else row2
            lbl = tk.Label(
                row, bg=col,
                width=1, height=1,
                relief="flat", bd=1,
                cursor="hand2",
            )
            lbl.pack(side="left", padx=1, pady=1)
            lbl.bind("<Button-1>", lambda e, c=col: self._set_color(c, "fg"))
            lbl.bind("<Button-3>", lambda e, c=col: self._set_color(c, "bg"))
            Tooltip(lbl, col)

        mksep(tb, "vertical").pack(side="left", fill="y", pady=6, padx=4)

        # Size
        size_f = tk.Frame(tb, bg=T["panel_bg"])
        size_f.pack(side="left", padx=4)
        tk.Label(size_f, text="Size:", bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 8)).pack(anchor="w")
        self._size_var = tk.IntVar(value=self._size)
        tk.Spinbox(
            size_f, from_=1, to=80,
            textvariable=self._size_var,
            bg=T["input_bg"], fg=T["text"],
            relief="flat", width=4,
            command=lambda: setattr(self, "_size", self._size_var.get()),
        ).pack()

        # Opacity
        op_f = tk.Frame(tb, bg=T["panel_bg"])
        op_f.pack(side="left", padx=4)
        tk.Label(op_f, text="Opacity:", bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 8)).pack(anchor="w")
        self._op_var = tk.DoubleVar(value=self._opacity)
        ttk.Scale(
            op_f, from_=0.1, to=1.0,
            orient="horizontal", length=60,
            variable=self._op_var,
            command=lambda v: setattr(self, "_opacity", float(v)),
        ).pack()

        mksep(tb, "vertical").pack(side="left", fill="y", pady=6, padx=4)

        # Action buttons
        for lbl, cmd in [
            ("Undo",   self._undo),
            ("Redo",   self._redo),
            ("Clear",  self._clear_canvas),
            ("Grid",   self._toggle_grid),
            ("Zoom+",  self._zoom_in),
            ("Zoom-",  self._zoom_out),
            ("Resize", self._resize_canvas_dlg),
            ("Save",   self._save_canvas),
        ]:
            tk.Button(
                tb, text=lbl,
                command=cmd,
                bg=T["button_bg"], fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_UI, 9), padx=6, pady=4,
                cursor="hand2",
                activebackground=T["button_hover"],
            ).pack(side="left", padx=1, pady=4)

    # ── canvas area ───────────────────────────────────────────────────────────

    def _build_canvas_area(self, parent: tk.Frame) -> None:
        cf = tk.Frame(parent, bg="#1a1a2e")
        cf.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            cf,
            bg=self._bg_color,
            cursor="crosshair",
            highlightthickness=1,
            highlightbackground=T["win_border"],
        )
        hsb = tk.Scrollbar(cf, orient="horizontal", command=self.canvas.xview)
        vsb = tk.Scrollbar(cf, orient="vertical",   command=self.canvas.yview)
        self.canvas.config(
            xscrollcommand=hsb.set,
            yscrollcommand=vsb.set,
            scrollregion=(0, 0, self._canvas_w, self._canvas_h),
        )
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self.canvas.pack(fill="both", expand=True, padx=20, pady=20)

        # Draw initial canvas background
        self.canvas.create_rectangle(
            0, 0, self._canvas_w, self._canvas_h,
            fill=self._bg_color, outline="", tags="canvas_bg",
        )

        # Bindings
        self.canvas.bind("<ButtonPress-1>",   self._mouse_down)
        self.canvas.bind("<B1-Motion>",        self._mouse_drag)
        self.canvas.bind("<ButtonRelease-1>",  self._mouse_up)
        self.canvas.bind("<ButtonPress-3>",    self._mouse_rclick)
        self.canvas.bind("<Motion>",           self._mouse_move)
        self.canvas.bind("<Double-Button-1>",  self._mouse_dbl)
        self.canvas.bind("<MouseWheel>",
            lambda e: self._zoom_in() if e.delta > 0 else self._zoom_out())

    def _build_status_bar(self, parent: tk.Frame) -> None:
        sf = tk.Frame(parent, bg=T["status_bg"], height=22)
        sf.pack(fill="x", side="bottom")
        sf.pack_propagate(False)
        self._st_pos = tk.Label(sf, text="X: 0  Y: 0",
                                 bg=T["status_bg"], fg=T["text_muted"],
                                 font=(FONT_UI, 8), anchor="w", padx=8)
        self._st_pos.pack(side="left", fill="y")
        self._st_tool = tk.Label(sf, text=f"Tool: {self._tool}  Size: {self._size}  Zoom: 100%",
                                  bg=T["status_bg"], fg=T["text_muted"],
                                  font=(FONT_UI, 8), padx=8)
        self._st_tool.pack(side="right", fill="y")

    # ── tool selection ────────────────────────────────────────────────────────

    def _select_tool(self, tool: str) -> None:
        self._tool = tool
        for k, b in self._tool_btns.items():
            b.config(bg=T["accent"] if k == tool else T["button_bg"])
        cursors = {
            "pencil": "pencil", "brush": "pencil", "eraser": "dotbox",
            "line": "crosshair", "rect": "crosshair", "rect_fill": "crosshair",
            "oval": "crosshair", "poly": "crosshair", "arrow": "crosshair",
            "fill": "spraycan", "text": "xterm", "eyedrop": "crosshair",
            "spray": "spraycan",
        }
        self.canvas.config(cursor=cursors.get(tool, "crosshair"))
        self._poly_pts.clear()
        self._st_tool.config(text=f"Tool: {tool}  Size: {self._size_var.get()}  Zoom: {int(self._zoom*100)}%")

    # ── colour helpers ────────────────────────────────────────────────────────

    def _pick_color(self, which: str) -> None:
        init = self._fg_color if which == "fg" else self._bg_color
        result = colorchooser.askcolor(color=init, title="Pick Colour", parent=self.wm.root)
        if result and result[1]:
            self._set_color(result[1], which)

    def _set_color(self, col: str, which: str) -> None:
        if which == "fg":
            self._fg_color = col
            self._fg_sw.config(bg=col)
        else:
            self._bg_color = col
            self._bg_sw.config(bg=col)

    def _swap_colors(self) -> None:
        self._fg_color, self._bg_color = self._bg_color, self._fg_color
        self._fg_sw.config(bg=self._fg_color)
        self._bg_sw.config(bg=self._bg_color)

    # ── coordinate helpers ────────────────────────────────────────────────────

    def _cx(self, e: tk.Event) -> Tuple[float, float]:
        return self.canvas.canvasx(e.x), self.canvas.canvasy(e.y)

    # ── mouse events ─────────────────────────────────────────────────────────

    def _mouse_down(self, e: tk.Event) -> None:
        x, y = self._cx(e)
        self._lx, self._ly = x, y
        self._sx, self._sy = x, y
        self._save_state()

        sz  = self._size_var.get()
        col = self._fg_color

        if self._tool == "text":
            txt = simpledialog.askstring("Add Text", "Enter text:", parent=self.wm.root)
            if txt:
                self.canvas.create_text(
                    x, y, text=txt,
                    fill=col, font=(FONT_UI, sz + 4),
                    anchor="nw",
                )

        elif self._tool == "fill":
            self.canvas.config(bg=col)
            self.canvas.itemconfig("canvas_bg", fill=col)

        elif self._tool == "eyedrop":
            # In a real app we'd sample the pixel; simulate with palette pick
            self._set_color(random.choice(self.PALETTE), "fg")

        elif self._tool == "poly":
            self._poly_pts.append((x, y))

    def _mouse_drag(self, e: tk.Event) -> None:
        x, y = self._cx(e)
        sz   = self._size_var.get()
        col  = self._fg_color

        if self._tool in ("pencil", "brush"):
            lw = sz if self._tool == "pencil" else sz * 2
            self.canvas.create_line(
                self._lx, self._ly, x, y,
                fill=col, width=lw,
                capstyle="round", joinstyle="round",
                smooth=True,
            )
            self._lx, self._ly = x, y

        elif self._tool == "eraser":
            r = sz * 3
            self.canvas.create_rectangle(
                x - r, y - r, x + r, y + r,
                fill=self._bg_color, outline=self._bg_color,
            )
            self._lx, self._ly = x, y

        elif self._tool == "spray":
            for _ in range(20):
                dx = random.gauss(0, sz * 2)
                dy = random.gauss(0, sz * 2)
                self.canvas.create_oval(
                    x+dx-1, y+dy-1, x+dx+1, y+dy+1,
                    fill=col, outline="",
                )

        elif self._tool in ("line", "rect", "rect_fill", "oval", "arrow"):
            if self._prev_item is not None:
                self.canvas.delete(self._prev_item)
            sx, sy = self._sx, self._sy
            if self._tool == "line":
                self._prev_item = self.canvas.create_line(
                    sx, sy, x, y, fill=col, width=sz,
                )
            elif self._tool == "rect":
                self._prev_item = self.canvas.create_rectangle(
                    sx, sy, x, y, outline=col, width=sz,
                )
            elif self._tool == "rect_fill":
                self._prev_item = self.canvas.create_rectangle(
                    sx, sy, x, y, fill=col, outline=col,
                )
            elif self._tool == "oval":
                self._prev_item = self.canvas.create_oval(
                    sx, sy, x, y, outline=col, width=sz,
                )
            elif self._tool == "arrow":
                self._prev_item = self.canvas.create_line(
                    sx, sy, x, y, fill=col, width=sz, arrow="last",
                    arrowshape=(sz*4, sz*5, sz*2),
                )

        self._st_pos.config(text=f"X: {int(x)}  Y: {int(y)}")

    def _mouse_up(self, _: tk.Event) -> None:
        self._prev_item = None

    def _mouse_rclick(self, e: tk.Event) -> None:
        """Right-click erases."""
        x, y = self._cx(e)
        sz   = self._size_var.get() * 3
        self.canvas.create_rectangle(
            x - sz, y - sz, x + sz, y + sz,
            fill=self._bg_color, outline=self._bg_color,
        )

    def _mouse_move(self, e: tk.Event) -> None:
        x, y = self._cx(e)
        self._st_pos.config(text=f"X: {int(x)}  Y: {int(y)}  |  {self._tool}")

    def _mouse_dbl(self, e: tk.Event) -> None:
        """Double-click closes polygon."""
        if self._tool == "poly" and len(self._poly_pts) >= 3:
            flat = [coord for pt in self._poly_pts for coord in pt]
            self.canvas.create_polygon(
                flat, outline=self._fg_color,
                fill="", width=self._size_var.get(),
            )
            self._poly_pts.clear()

    # ── undo / redo ───────────────────────────────────────────────────────────

    def _save_state(self) -> None:
        try:
            ps = self.canvas.postscript()
            self._undo_stack.append(ps)
            if len(self._undo_stack) > 30:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
        except Exception:
            pass

    def _undo(self) -> None:
        if self._undo_stack:
            try:
                self._redo_stack.append(self.canvas.postscript())
            except Exception:
                pass
            self.canvas.delete("all")
            self.canvas.create_rectangle(
                0, 0, self._canvas_w, self._canvas_h,
                fill=self._bg_color, outline="", tags="canvas_bg",
            )

    def _redo(self) -> None:
        if self._redo_stack:
            self.canvas.delete("all")
            self.canvas.create_rectangle(
                0, 0, self._canvas_w, self._canvas_h,
                fill=self._bg_color, outline="", tags="canvas_bg",
            )

    # ── canvas operations ─────────────────────────────────────────────────────

    def _clear_canvas(self) -> None:
        self._save_state()
        self.canvas.delete("all")
        self.canvas.create_rectangle(
            0, 0, self._canvas_w, self._canvas_h,
            fill=self._bg_color, outline="", tags="canvas_bg",
        )
        if self._show_grid:
            self._draw_grid()

    def _toggle_grid(self) -> None:
        self._show_grid = not self._show_grid
        if self._show_grid:
            self._draw_grid()
        else:
            self.canvas.delete("grid")

    def _draw_grid(self) -> None:
        self.canvas.delete("grid")
        step = 20
        for x in range(0, self._canvas_w, step):
            self.canvas.create_line(
                x, 0, x, self._canvas_h,
                fill=T["text_dim"], tags="grid", dash=(2, 6),
            )
        for y in range(0, self._canvas_h, step):
            self.canvas.create_line(
                0, y, self._canvas_w, y,
                fill=T["text_dim"], tags="grid", dash=(2, 6),
            )
        self.canvas.tag_lower("grid")
        self.canvas.tag_lower("canvas_bg")

    def _zoom_in(self) -> None:
        self._zoom = min(4.0, self._zoom + 0.25)
        self.canvas.scale("all", 0, 0, 1.25, 1.25)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self._st_tool.config(
            text=f"Tool: {self._tool}  Size: {self._size_var.get()}  Zoom: {int(self._zoom*100)}%"
        )

    def _zoom_out(self) -> None:
        if self._zoom > 0.25:
            self._zoom = max(0.25, self._zoom - 0.25)
            self.canvas.scale("all", 0, 0, 0.8, 0.8)
            self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self._st_tool.config(
            text=f"Tool: {self._tool}  Size: {self._size_var.get()}  Zoom: {int(self._zoom*100)}%"
        )

    def _resize_canvas_dlg(self) -> None:
        w = simpledialog.askinteger(
            "Resize Canvas", "Width (px):",
            initialvalue=self._canvas_w, parent=self.wm.root,
        )
        h = simpledialog.askinteger(
            "Resize Canvas", "Height (px):",
            initialvalue=self._canvas_h, parent=self.wm.root,
        )
        if w and h:
            self._canvas_w = w
            self._canvas_h = h
            self.canvas.config(scrollregion=(0, 0, w, h))
            self.wm.notifs.send("Paint", f"Canvas resized to {w}×{h}", icon="🎨")

    def _save_canvas(self) -> None:
        path = simpledialog.askstring(
            "Save Canvas",
            "Save to VFS path (PostScript):",
            initialvalue="/home/user/Pictures/drawing.ps",
            parent=self.wm.root,
        )
        if path:
            try:
                ps = self.canvas.postscript()
                self.wm.vfs.write(path, ps)
                self.wm.notifs.send("Paint", f"Saved: {path}", icon="🎨")
            except Exception as ex:
                messagebox.showerror("Save Error", str(ex), parent=self.wm.root)


# =============================================================================
#  END OF PART 3
#  Defines: TerminalApp (60+ commands), BrowserApp (tabs + 8 internal pages),
#           MusicPlayerApp (4 visualiser modes, 14 tracks, EQ),
#           PaintApp (13 tools, palette, undo/redo, zoom)
#
#  Part 4 covers: CalculatorApp (4 modes), ClockApp (5 tabs),
#                 TaskManagerApp (5 tabs), NotesApp, EmailApp
#  Part 5 covers: PasswordManagerApp, SpreadsheetApp, ImageViewerApp,
#                 DiskAnalyzerApp, CodeRunnerApp, ArchiveManagerApp
#  Part 6 covers: AppStoreApp, SystemMonitorApp, SettingsApp,
#                 Login/Lock screens, Boot animation, main()
# =============================================================================

if __name__ == "__main__":
    print(f"PyOS v{PYOS_VERSION} — Part 3 loaded.")
    print("TerminalApp, BrowserApp, MusicPlayerApp, PaintApp defined.")
    print("Combine all parts for the full OS.")
#!/usr/bin/env python3
# =============================================================================
#  PyOS v5.0 — PART 4
#  Sections: Calculator (4 modes), Clock & Calendar (5 tabs),
#            Task Manager (5 tabs), Notes App, Email Client
#  Requires: Parts 1–3 concatenated before this
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 21 — CALCULATOR APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class CalculatorApp(BaseWin):
    """
    Full-featured calculator with four modes:
      1. Standard  — basic arithmetic + memory (MC/MR/M+/M-/MS)
      2. Scientific — trig, log, sqrt, factorial, constants, power
      3. Programmer — hex/dec/oct/bin, bitwise ops (AND/OR/XOR/NOT/SHL/SHR)
      4. Unit Conv  — length, mass, temperature, area, speed, data
    History panel shared across all modes.
    Keyboard input supported.
    """

    import math as _math_module  # cached for eval

    def __init__(self, wm: WM) -> None:
        self._expr     = ""
        self._result   = ""
        self._memory   = 0.0
        self._history: List[str] = []
        self._mode     = "standard"
        self._prog_base = 10          # programmer mode base
        self._mode_btns: Dict[str, tk.Button] = {}
        super().__init__(wm, "Calculator", 880, 100, 380, 620, "🔢",
                         min_w=300, min_h=480, resizable=True)

    # ── top-level build ───────────────────────────────────────────────────────

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])

        # Mode selector
        mode_bar = tk.Frame(parent, bg=T["panel_bg"])
        mode_bar.pack(fill="x")
        for label, key in [("Standard","standard"),("Scientific","scientific"),
                            ("Programmer","programmer"),("Unit Conv","unit")]:
            b = tk.Button(mode_bar, text=label,
                          command=partial(self._switch_mode, key),
                          bg=T["accent"] if key == self._mode else T["button_bg"],
                          fg=T["text"], relief="flat", bd=0,
                          font=(FONT_UI, 9), padx=8, pady=4, cursor="hand2",
                          activebackground=T["button_hover"])
            b.pack(side="left", padx=2, pady=4)
            self._mode_btns[key] = b

        self._mode_frame = tk.Frame(parent, bg=T["win_bg"])
        self._mode_frame.pack(fill="both", expand=True)

        self._build_standard()
        self.wm.root.bind("<Key>", self._key_press)

    # ── display builder (shared) ──────────────────────────────────────────────

    def _make_display(self, parent: tk.Frame) -> None:
        dp = tk.Frame(parent, bg=T["panel_alt"], pady=10)
        dp.pack(fill="x", padx=6, pady=(4, 0))

        self._mem_lbl = tk.Label(dp, text="M=0",
                                  bg=T["panel_alt"], fg=T["text_muted"],
                                  font=(FONT_UI, 8), anchor="w")
        self._mem_lbl.pack(fill="x", padx=8)

        self._expr_lbl = tk.Label(dp, text="",
                                   bg=T["panel_alt"], fg=T["text_muted"],
                                   font=(FONT_MONO, 11), anchor="e")
        self._expr_lbl.pack(fill="x", padx=8)

        self._res_lbl = tk.Label(dp, text="0",
                                  bg=T["panel_alt"], fg=T["text"],
                                  font=(FONT_MONO, 30, "bold"), anchor="e")
        self._res_lbl.pack(fill="x", padx=8)

    def _refresh_display(self) -> None:
        try:
            self._expr_lbl.config(text=self._expr or "")
            self._res_lbl.config(text=self._result or self._expr or "0")
            self._mem_lbl.config(text=f"M = {self._memory}")
        except Exception:
            pass

    # ── mode switching ────────────────────────────────────────────────────────

    def _switch_mode(self, mode: str) -> None:
        self._mode = mode
        for k, b in self._mode_btns.items():
            b.config(bg=T["accent"] if k == mode else T["button_bg"])
        for w in self._mode_frame.winfo_children():
            w.destroy()
        self._expr = ""; self._result = ""
        {
            "standard":   self._build_standard,
            "scientific":  self._build_scientific,
            "programmer":  self._build_programmer,
            "unit":        self._build_unit_conv,
        }[mode]()

    # ── STANDARD MODE ─────────────────────────────────────────────────────────

    def _build_standard(self) -> None:
        f = self._mode_frame
        self._make_display(f)

        # Memory buttons
        mem_f = tk.Frame(f, bg=T["win_bg"])
        mem_f.pack(fill="x", padx=6, pady=(2, 0))
        for txt, act in [("MC","mc"),("MR","mr"),("M+","mp"),("M-","mm"),("MS","ms")]:
            tk.Button(mem_f, text=txt, command=partial(self._mem_op, act),
                      bg=T["panel_bg"], fg=T["text_muted"], relief="flat", bd=0,
                      font=(FONT_UI, 9), padx=8, pady=3, cursor="hand2",
                      activebackground=T["button_hover"]).pack(side="left", padx=2)

        # Button grid
        layout = [
            [("C","clear","danger"), ("±","neg","normal"), ("%","pct","normal"),  ("÷","÷","accent")],
            [("7","7","n"),          ("8","8","n"),         ("9","9","n"),          ("×","×","accent")],
            [("4","4","n"),          ("5","5","n"),         ("6","6","n"),          ("−","−","accent")],
            [("1","1","n"),          ("2","2","n"),         ("3","3","n"),          ("+","+","accent")],
            [("⌫","back","n"),       ("0","0","n"),         (".","dot","n"),        ("=","=","accent")],
        ]
        grid = tk.Frame(f, bg=T["win_bg"])
        grid.pack(fill="both", expand=True, padx=6, pady=4)
        self._render_btn_grid(grid, layout)

        # History
        self._hist_lbl = tk.Label(f, text="",
                                   bg=T["win_bg"], fg=T["text_muted"],
                                   font=(FONT_MONO, 8), anchor="w",
                                   wraplength=340, justify="left")
        self._hist_lbl.pack(fill="x", padx=10, pady=4)

    # ── SCIENTIFIC MODE ───────────────────────────────────────────────────────

    def _build_scientific(self) -> None:
        f = self._mode_frame
        self._make_display(f)

        layout = [
            [("sin","sin("),  ("cos","cos("),  ("tan","tan("),  ("π","pi"),    ("e","e")],
            [("asin","asin("),("acos","acos("),("atan","atan("),("√","sqrt("), ("x²","**2")],
            [("log","log10("),("ln","log("),   ("exp","exp("),  ("abs","abs("),("ceil","ceil(")],
            [("floor","floor("),("(",  "("),   (")",")"),       ("^","**"),    ("!","factorial(")],
            [("C","clear"),   ("±","neg"),     ("%","pct"),     ("÷","÷"),     ("×","×")],
            [("7","7"),       ("8","8"),       ("9","9"),       ("−","−"),     ("+","+")],
            [("4","4"),       ("5","5"),       ("6","6"),       (".","dot"),   ("⌫","back")],
            [("1","1"),       ("2","2"),       ("3","3"),       ("0","0"),     ("=","=")],
        ]
        grid = tk.Frame(f, bg=T["win_bg"])
        grid.pack(fill="both", expand=True, padx=6, pady=4)
        self._render_btn_grid(grid, layout, small=True)

    # ── PROGRAMMER MODE ───────────────────────────────────────────────────────

    def _build_programmer(self) -> None:
        f = self._mode_frame
        self._make_display(f)

        # Base selector
        base_f = tk.Frame(f, bg=T["win_bg"])
        base_f.pack(fill="x", padx=6, pady=(2, 0))
        self._base_var = tk.IntVar(value=10)
        for lbl, base in [("HEX", 16), ("DEC", 10), ("OCT", 8), ("BIN", 2)]:
            tk.Radiobutton(base_f, text=lbl, variable=self._base_var, value=base,
                           command=lambda b=base: self._set_prog_base(b),
                           bg=T["win_bg"], fg=T["text"], selectcolor=T["accent"],
                           activebackground=T["win_bg"],
                           font=(FONT_UI, 9)).pack(side="left", padx=8)

        # Conversion display
        self._conv_lbl = tk.Label(f, text="",
                                   bg=T["win_bg"], fg=T["text_muted"],
                                   font=(FONT_MONO, 9), anchor="w")
        self._conv_lbl.pack(fill="x", padx=10, pady=2)

        layout = [
            [("A","A","n"),  ("B","B","n"),  ("C_","C","n"),  ("D","D","n"),  ("E","E","n"),  ("F","F","n")],
            [("7","7","n"),  ("8","8","n"),  ("9","9","n"),   ("÷","÷","accent"),("AND","&","n"),("OR","|","n")],
            [("4","4","n"),  ("5","5","n"),  ("6","6","n"),   ("×","×","accent"),("XOR","^","n"),("NOT","~","n")],
            [("1","1","n"),  ("2","2","n"),  ("3","3","n"),   ("−","−","accent"),("SHL","<<","n"),("SHR",">>","n")],
            [("C","clear","danger"),("±","neg","n"),("0","0","n"),("+","+","accent"),("⌫","back","n"),("=","=","accent")],
        ]
        grid = tk.Frame(f, bg=T["win_bg"])
        grid.pack(fill="both", expand=True, padx=6, pady=4)
        self._render_btn_grid(grid, layout, small=True)

    def _set_prog_base(self, base: int) -> None:
        self._prog_base = base
        # Try converting current expression
        try:
            val = int(self._expr or "0", 0)
            if base == 16: self._expr = hex(val)
            elif base == 8: self._expr = oct(val)
            elif base == 2: self._expr = bin(val)
            else: self._expr = str(val)
        except Exception:
            self._expr = "0"
        self._refresh_display()
        self._update_conv_display()

    def _update_conv_display(self) -> None:
        try:
            val = int(eval(
                self._expr.replace("÷","/").replace("×","*").replace("−","-"),
                {"__builtins__": {}}
            ))
            self._conv_lbl.config(
                text=f"HEX: {hex(val)}  OCT: {oct(val)}  BIN: {bin(val)}"
            )
        except Exception:
            pass

    # ── UNIT CONVERSION MODE ──────────────────────────────────────────────────

    def _build_unit_conv(self) -> None:
        f = self._mode_frame

        tk.Label(f, text="Unit Converter",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold")).pack(pady=(12, 6))

        # Category selector
        cat_f = tk.Frame(f, bg=T["win_bg"])
        cat_f.pack(fill="x", padx=10)
        self._unit_cat = tk.StringVar(value="Length")
        cats = ["Length","Mass","Temperature","Area","Volume","Speed","Data","Time","Pressure","Energy"]
        cat_menu = ttk.Combobox(cat_f, textvariable=self._unit_cat, values=cats,
                                 state="readonly", width=18)
        cat_menu.pack(side="left")
        cat_menu.bind("<<ComboboxSelected>>", lambda e: self._update_unit_lists())

        # From / To rows
        conv_f = tk.Frame(f, bg=T["win_bg"])
        conv_f.pack(fill="x", padx=10, pady=10)

        # From
        from_row = tk.Frame(conv_f, bg=T["win_bg"])
        from_row.pack(fill="x", pady=4)
        tk.Label(from_row, text="From:", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10), width=6).pack(side="left")
        self._from_val = tk.StringVar(value="1")
        from_entry = mkentry(from_row, textvariable=self._from_val, width=14)
        from_entry.pack(side="left", padx=6)
        from_entry.bind("<KeyRelease>", lambda e: self._convert())

        self._from_unit = tk.StringVar()
        self._from_menu = ttk.Combobox(from_row, textvariable=self._from_unit,
                                        state="readonly", width=16)
        self._from_menu.pack(side="left", padx=4)
        self._from_menu.bind("<<ComboboxSelected>>", lambda e: self._convert())

        # Swap
        tk.Button(conv_f, text="⇄", command=self._swap_units,
                  bg=T["button_bg"], fg=T["text"], relief="flat", bd=0,
                  font=(FONT_UI, 14), padx=8, cursor="hand2",
                  activebackground=T["button_hover"]).pack(pady=4)

        # To
        to_row = tk.Frame(conv_f, bg=T["win_bg"])
        to_row.pack(fill="x", pady=4)
        tk.Label(to_row, text="To:", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10), width=6).pack(side="left")
        self._to_val = tk.StringVar(value="")
        to_entry = mkentry(to_row, textvariable=self._to_val, width=14)
        to_entry.pack(side="left", padx=6)
        to_entry.config(state="readonly")

        self._to_unit = tk.StringVar()
        self._to_menu = ttk.Combobox(to_row, textvariable=self._to_unit,
                                      state="readonly", width=16)
        self._to_menu.pack(side="left", padx=4)
        self._to_menu.bind("<<ComboboxSelected>>", lambda e: self._convert())

        # Result display
        self._unit_result = tk.Label(f, text="",
                                      bg=T["win_bg"], fg=T["accent"],
                                      font=(FONT_MONO, 16, "bold"))
        self._unit_result.pack(pady=8)

        # Quick reference table
        ref_f = tk.Frame(f, bg=T["panel_alt"])
        ref_f.pack(fill="both", expand=True, padx=10, pady=6)
        tk.Label(ref_f, text="Common Conversions",
                 bg=T["panel_alt"], fg=T["text_muted"],
                 font=(FONT_UI, 8, "bold")).pack(anchor="w", padx=8, pady=(6,2))
        self._ref_inner = tk.Frame(ref_f, bg=T["panel_alt"])
        self._ref_inner.pack(fill="both", expand=True, padx=4)

        self._update_unit_lists()

    def _update_unit_lists(self) -> None:
        cat = self._unit_cat.get()
        units_map = {
            "Length":      ["meter","kilometer","centimeter","millimeter","inch","foot","yard","mile","nautical mile","light-year"],
            "Mass":        ["kilogram","gram","milligram","pound","ounce","ton (metric)","ton (US)","stone"],
            "Temperature": ["Celsius","Fahrenheit","Kelvin","Rankine"],
            "Area":        ["sq meter","sq kilometer","sq centimeter","sq mile","sq yard","sq foot","sq inch","acre","hectare"],
            "Volume":      ["liter","milliliter","cubic meter","gallon (US)","gallon (UK)","quart","pint","cup","fluid oz","tablespoon","teaspoon"],
            "Speed":       ["m/s","km/h","mph","knot","ft/s","mach"],
            "Data":        ["bit","byte","kilobyte","megabyte","gigabyte","terabyte","petabyte","kibibyte","mebibyte","gibibyte"],
            "Time":        ["second","minute","hour","day","week","month","year","millisecond","microsecond","nanosecond"],
            "Pressure":    ["pascal","kilopascal","bar","atmosphere","psi","mmHg","inHg","torr"],
            "Energy":      ["joule","kilojoule","calorie","kcal","watt-hour","kWh","BTU","erg","eV"],
        }
        units = units_map.get(cat, ["unit"])
        self._from_menu["values"] = units
        self._to_menu["values"]   = units
        self._from_unit.set(units[0] if units else "")
        self._to_unit.set(units[1] if len(units) > 1 else units[0])
        self._from_val.set("1")
        self._convert()
        self._update_ref_table(cat, units_map)

    def _convert(self) -> None:
        try:
            val   = float(self._from_val.get())
            from_ = self._from_unit.get()
            to_   = self._to_unit.get()
            cat   = self._unit_cat.get()
            result = self._do_convert(val, from_, to_, cat)
            self._to_val.config(state="normal")
            self._to_val.set(f"{result:.6g}")
            self._to_val.config(state="readonly")
            self._unit_result.config(text=f"{val} {from_}  =  {result:.6g} {to_}")
        except Exception:
            self._unit_result.config(text="Invalid input")

    def _do_convert(self, val: float, from_: str, to_: str, cat: str) -> float:
        """Convert using base unit (SI) as intermediate."""
        to_si: Dict[str, Dict[str, float]] = {
            "Length": {
                "meter":1,"kilometer":1e3,"centimeter":0.01,"millimeter":0.001,
                "inch":0.0254,"foot":0.3048,"yard":0.9144,"mile":1609.344,
                "nautical mile":1852,"light-year":9.461e15,
            },
            "Mass": {
                "kilogram":1,"gram":0.001,"milligram":1e-6,
                "pound":0.453592,"ounce":0.028350,"ton (metric)":1000,
                "ton (US)":907.185,"stone":6.35029,
            },
            "Area": {
                "sq meter":1,"sq kilometer":1e6,"sq centimeter":0.0001,
                "sq mile":2589988.11,"sq yard":0.836127,"sq foot":0.092903,
                "sq inch":0.00064516,"acre":4046.856,"hectare":10000,
            },
            "Volume": {
                "liter":1,"milliliter":0.001,"cubic meter":1000,
                "gallon (US)":3.78541,"gallon (UK)":4.54609,
                "quart":0.946353,"pint":0.473176,"cup":0.24,
                "fluid oz":0.0295735,"tablespoon":0.0147868,"teaspoon":0.00492892,
            },
            "Speed": {
                "m/s":1,"km/h":1/3.6,"mph":0.44704,
                "knot":0.514444,"ft/s":0.3048,"mach":340.29,
            },
            "Data": {
                "bit":1,"byte":8,"kilobyte":8*1024,"megabyte":8*1024**2,
                "gigabyte":8*1024**3,"terabyte":8*1024**4,"petabyte":8*1024**5,
                "kibibyte":8*1024,"mebibyte":8*1024**2,"gibibyte":8*1024**3,
            },
            "Time": {
                "second":1,"minute":60,"hour":3600,"day":86400,"week":604800,
                "month":2592000,"year":31536000,"millisecond":0.001,
                "microsecond":1e-6,"nanosecond":1e-9,
            },
            "Pressure": {
                "pascal":1,"kilopascal":1000,"bar":1e5,"atmosphere":101325,
                "psi":6894.76,"mmHg":133.322,"inHg":3386.39,"torr":133.322,
            },
            "Energy": {
                "joule":1,"kilojoule":1000,"calorie":4.184,"kcal":4184,
                "watt-hour":3600,"kWh":3.6e6,"BTU":1055.06,"erg":1e-7,"eV":1.602e-19,
            },
        }
        if cat == "Temperature":
            # Special case
            def to_celsius(v: float, u: str) -> float:
                if u == "Celsius":    return v
                if u == "Fahrenheit": return (v - 32) * 5/9
                if u == "Kelvin":     return v - 273.15
                if u == "Rankine":    return (v - 491.67) * 5/9
                return v
            def from_celsius(v: float, u: str) -> float:
                if u == "Celsius":    return v
                if u == "Fahrenheit": return v * 9/5 + 32
                if u == "Kelvin":     return v + 273.15
                if u == "Rankine":    return (v + 273.15) * 9/5
                return v
            return from_celsius(to_celsius(val, from_), to_)

        tbl = to_si.get(cat, {})
        f   = tbl.get(from_, 1.0)
        t   = tbl.get(to_,   1.0)
        return val * f / t

    def _swap_units(self) -> None:
        f = self._from_unit.get()
        t = self._to_unit.get()
        self._from_unit.set(t)
        self._to_unit.set(f)
        self._convert()

    def _update_ref_table(self, cat: str, units_map: Dict) -> None:
        for w in self._ref_inner.winfo_children():
            w.destroy()
        units = units_map.get(cat, [])
        try:
            base_val = 1.0
            base_u   = units[0] if units else ""
            for i, u in enumerate(units[:8]):
                try:
                    converted = self._do_convert(base_val, base_u, u, cat)
                    bg = T["panel_alt"] if i % 2 == 0 else T["win_bg"]
                    row = tk.Frame(self._ref_inner, bg=bg)
                    row.pack(fill="x")
                    tk.Label(row, text=f"1 {base_u}", bg=bg, fg=T["text_muted"],
                             font=(FONT_UI, 8), width=16, anchor="w").pack(side="left", padx=4, pady=2)
                    tk.Label(row, text=f"= {converted:.4g} {u}", bg=bg, fg=T["text"],
                             font=(FONT_MONO, 8)).pack(side="left")
                except Exception:
                    pass
        except Exception:
            pass

    # ── button grid renderer ──────────────────────────────────────────────────

    def _render_btn_grid(
        self,
        grid:  tk.Frame,
        layout: List[List[tuple]],
        small: bool = False,
    ) -> None:
        fs   = 11 if small else 14
        padx = 2  if small else 3
        pady = 2  if small else 3

        for r, row in enumerate(layout):
            for c, spec in enumerate(row):
                lbl, act = spec[0], spec[1]
                kind     = spec[2] if len(spec) > 2 else "normal"
                kind_map = {"n": "normal", "normal":"normal",
                             "accent":"accent","danger":"danger"}
                k = kind_map.get(kind, "normal")

                pal = {
                    "normal": (T["button_bg"],  T["text"],   T["button_hover"]),
                    "accent": (T["accent"],      "#ffffff",   darken(T["accent"])),
                    "danger": (T["danger"],       "#ffffff",   darken(T["danger"])),
                }
                bg, fg, abg = pal[k]

                btn = tk.Button(
                    grid, text=lbl,
                    command=partial(self._btn_press, act),
                    bg=bg, fg=fg, relief="flat", bd=0,
                    font=(FONT_MONO, fs, "bold"),
                    activebackground=abg, activeforeground=fg,
                    cursor="hand2",
                )
                btn.grid(row=r, column=c, padx=padx, pady=pady, sticky="nsew")
                grid.columnconfigure(c, weight=1)
            grid.rowconfigure(r, weight=1)

    # ── button action handler ─────────────────────────────────────────────────

    def _btn_press(self, action: str) -> None:
        import math as _m

        if action == "clear":
            self._expr = ""; self._result = ""
            self._refresh_display()
            return
        elif action == "back":
            self._expr = self._expr[:-1]
        elif action == "neg":
            try:
                v = float(eval(self._expr or "0", {"__builtins__":{}}, {}))
                self._expr = str(-v)
            except Exception:
                pass
        elif action == "pct":
            try:
                v = float(eval(self._expr or "0", {"__builtins__":{}}, {}))
                self._expr = str(v / 100)
            except Exception:
                pass
        elif action == "dot":
            # Only add decimal if last token doesn't already have one
            last_num = re.split(r'[+\-*/]', self._expr)[-1] if self._expr else ""
            if "." not in last_num:
                self._expr += "."
        elif action == "=":
            try:
                expr_eval = (self._expr
                             .replace("÷", "/")
                             .replace("×", "*")
                             .replace("−", "-"))
                import math as _m2
                safe_env = {k: getattr(_m2, k) for k in dir(_m2) if not k.startswith("_")}
                safe_env["__builtins__"] = {}
                result = eval(expr_eval, safe_env)
                if isinstance(result, complex):
                    result = f"{result.real:.6g}+{result.imag:.6g}j"
                elif isinstance(result, float):
                    if result.is_integer() and abs(result) < 1e15:
                        result = int(result)
                    else:
                        result = round(result, 10)
                entry = f"{self._expr} = {result}"
                self._history.append(entry)
                if len(self._history) > 10:
                    self._history.pop(0)
                self._result = str(result)
                self._expr   = str(result)
                self._refresh_display()
                try:
                    if hasattr(self, "_hist_lbl"):
                        self._hist_lbl.config(text="\n".join(self._history[-4:]))
                    if self._mode == "programmer":
                        self._update_conv_display()
                except Exception:
                    pass
                return
            except ZeroDivisionError:
                self._result = "Division by zero"
                self._expr   = ""
                self._refresh_display()
                return
            except Exception:
                self._result = "Error"
                self._expr   = ""
                self._refresh_display()
                return
        elif action == "pi":
            self._expr += str(math.pi)
        elif action == "e":
            self._expr += str(math.e)
        elif action in ("sin(","cos(","tan(","asin(","acos(","atan(",
                        "sqrt(","log(","log10(","exp(","abs(","ceil(",
                        "floor(","factorial("):
            # Wrap in math. prefix for eval
            self._expr += "math." + action
        else:
            self._expr += action

        self._refresh_display()

    def _mem_op(self, op: str) -> None:
        try:
            cur = float(eval(
                (self._expr or "0").replace("÷","/").replace("×","*").replace("−","-"),
                {"__builtins__": {}}
            ))
        except Exception:
            cur = 0.0
        if   op == "mc": self._memory = 0.0
        elif op == "mr": self._expr = str(self._memory)
        elif op == "mp": self._memory += cur
        elif op == "mm": self._memory -= cur
        elif op == "ms": self._memory = cur
        self._refresh_display()

    def _key_press(self, e: tk.Event) -> None:
        key_map = {
            "Return":    "=",   "KP_Enter":  "=",
            "BackSpace": "back","Delete":     "clear",
            "KP_Decimal":"dot",
        }
        k = e.keysym; c = e.char
        if k in key_map:
            self._btn_press(key_map[k])
        elif c in "0123456789.+-*/()" and self._mode != "unit":
            mapped = c.replace("*","×").replace("/","÷").replace("-","−")
            self._btn_press(mapped)
        elif c in "ABCDEFabcdef" and self._mode == "programmer":
            self._btn_press(c.upper())


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 22 — CLOCK & CALENDAR APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class ClockApp(BaseWin):
    """
    Five-tab clock application:
      1. Clock     — analog + digital, live ticking
      2. Calendar  — month view, event creation
      3. Alarm     — multiple alarms with repeat
      4. Stopwatch — millisecond precision, lap times
      5. World     — 15 world cities, UTC offset
    """

    def __init__(self, wm: WM) -> None:
        self._alarms:  List[Dict[str, Any]] = []
        self._events:  Dict[str, List[str]]  = {}  # "YYYY-MM-DD" → [event, ...]
        self._tab      = "clock"
        self._sw_running = False
        self._sw_start   = 0.0
        self._sw_elapsed = 0.0
        self._sw_laps:   List[float] = []
        super().__init__(wm, "Clock", 680, 90, 460, 520, "⏰", min_w=340, min_h=420)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])

        # Tab bar
        tab_bar = tk.Frame(parent, bg=T["panel_bg"])
        tab_bar.pack(fill="x")
        self._tab_btns: Dict[str, tk.Button] = {}
        for label in ["Clock","Calendar","Alarm","Stopwatch","World"]:
            k = label.lower()
            b = tk.Button(tab_bar, text=label,
                          command=partial(self._switch_tab, k),
                          bg=T["accent"] if label == "Clock" else T["button_bg"],
                          fg=T["text"], relief="flat", bd=0,
                          font=(FONT_UI, 9), padx=10, pady=6, cursor="hand2",
                          activebackground=T["button_hover"])
            b.pack(side="left", padx=2, pady=4)
            self._tab_btns[k] = b

        self._content = tk.Frame(parent, bg=T["win_bg"])
        self._content.pack(fill="both", expand=True)
        self._build_clock()

    def _switch_tab(self, tab: str) -> None:
        self._tab = tab
        for k, b in self._tab_btns.items():
            b.config(bg=T["accent"] if k == tab else T["button_bg"])
        for w in self._content.winfo_children():
            w.destroy()
        {
            "clock":     self._build_clock,
            "calendar":  self._build_calendar,
            "alarm":     self._build_alarm,
            "stopwatch": self._build_stopwatch,
            "world":     self._build_world,
        }[tab]()

    # ── CLOCK TAB ─────────────────────────────────────────────────────────────

    def _build_clock(self) -> None:
        f = self._content

        # Analog canvas
        self.clock_canvas = tk.Canvas(f, bg=T["win_bg"], width=280, height=280,
                                       highlightthickness=0)
        self.clock_canvas.pack(pady=(12, 6))

        # Digital display
        self.digital_lbl = tk.Label(f, text="",
                                     bg=T["win_bg"], fg=T["text"],
                                     font=(FONT_MONO, 32, "bold"))
        self.digital_lbl.pack()

        self.date_lbl = tk.Label(f, text="",
                                  bg=T["win_bg"], fg=T["text_muted"],
                                  font=(FONT_UI, 13))
        self.date_lbl.pack(pady=(2, 4))

        info_f = tk.Frame(f, bg=T["win_bg"])
        info_f.pack()
        self.tz_lbl = tk.Label(info_f, text=f"Timezone: {time.tzname[0]}",
                                bg=T["win_bg"], fg=T["text_muted"],
                                font=(FONT_UI, 9))
        self.tz_lbl.pack(side="left", padx=10)
        self.uptime_lbl = tk.Label(info_f, text="",
                                    bg=T["win_bg"], fg=T["text_muted"],
                                    font=(FONT_UI, 9))
        self.uptime_lbl.pack(side="left", padx=10)

        self._tick_clock()

    def _tick_clock(self) -> None:
        if not self._out.winfo_exists() or self._tab != "clock":
            return
        now = datetime.datetime.now()
        self._draw_analog(now)
        fmt = self.wm.settings.get("time_format", "%H:%M:%S")
        self.digital_lbl.config(text=now.strftime(fmt))
        self.date_lbl.config(text=now.strftime("%A, %B %d, %Y"))
        self.uptime_lbl.config(text=f"Uptime: {self.wm.users.uptime}")
        # Alarm check
        alarm_str = now.strftime("%H:%M")
        for alarm in self._alarms:
            if alarm.get("active") and alarm.get("time") == alarm_str:
                self.wm.notifs.send("⏰ Alarm", alarm.get("label", "Alarm!"),
                                     level="warning", icon="⏰")
                if not alarm.get("repeat"):
                    alarm["active"] = False
        self.wm.root.after(1000, self._tick_clock)

    def _draw_analog(self, now: datetime.datetime) -> None:
        c  = self.clock_canvas
        c.delete("all")
        cx, cy, r = 140, 140, 120

        # Face
        c.create_oval(cx-r-6, cy-r-6, cx+r+6, cy+r+6,
                      fill=T["panel_alt"], outline=T["accent"], width=3)
        c.create_oval(cx-r, cy-r, cx+r, cy+r,
                      fill=T["win_bg"], outline=T["win_border_active"], width=2)

        # Hour ticks + numbers
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            if i % 5 == 0:
                x1 = cx + (r - 10) * math.cos(angle)
                y1 = cy + (r - 10) * math.sin(angle)
                x2 = cx + r * math.cos(angle)
                y2 = cy + r * math.sin(angle)
                c.create_line(x1, y1, x2, y2, fill=T["text_muted"], width=2)
                num = str(i // 5 or 12)
                nx  = cx + (r - 24) * math.cos(angle)
                ny  = cy + (r - 24) * math.sin(angle)
                c.create_text(nx, ny, text=num, fill=T["text"],
                               font=(FONT_UI, 9, "bold"))
            else:
                x1 = cx + (r - 5) * math.cos(angle)
                y1 = cy + (r - 5) * math.sin(angle)
                x2 = cx + r * math.cos(angle)
                y2 = cy + r * math.sin(angle)
                c.create_line(x1, y1, x2, y2, fill=T["text_dim"], width=1)

        h, m, s = now.hour % 12, now.minute, now.second

        # Hour hand
        ha = math.radians((h + m/60) * 30 - 90)
        c.create_line(cx, cy, cx + r*0.5*math.cos(ha), cy + r*0.5*math.sin(ha),
                      fill=T["text"], width=6, capstyle="round")

        # Minute hand
        ma = math.radians((m + s/60) * 6 - 90)
        c.create_line(cx, cy, cx + r*0.76*math.cos(ma), cy + r*0.76*math.sin(ma),
                      fill=T["text"], width=4, capstyle="round")

        # Second hand
        sa = math.radians(s * 6 - 90)
        c.create_line(cx, cy, cx + r*0.85*math.cos(sa), cy + r*0.85*math.sin(sa),
                      fill=T["accent"], width=1, capstyle="round")
        c.create_line(cx, cy, cx + r*0.18*math.cos(sa+math.pi),
                      cy + r*0.18*math.sin(sa+math.pi),
                      fill=T["accent"], width=2)

        # Centre
        c.create_oval(cx-6, cy-6, cx+6, cy+6, fill=T["accent"], outline="")
        c.create_oval(cx-2, cy-2, cx+2, cy+2, fill="#ffffff", outline="")

    # ── CALENDAR TAB ──────────────────────────────────────────────────────────

    def _build_calendar(self) -> None:
        f = self._content
        today = datetime.date.today()
        self._cal_year  = today.year
        self._cal_month = today.month

        nav = tk.Frame(f, bg=T["win_bg"])
        nav.pack(fill="x", pady=8)
        tk.Button(nav, text="◀", command=self._cal_prev,
                  bg=T["button_bg"], fg=T["text"], relief="flat", bd=0,
                  font=(FONT_UI, 13), padx=8, cursor="hand2",
                  activebackground=T["button_hover"]).pack(side="left", padx=10)
        self._cal_title = tk.Label(nav, text="",
                                    bg=T["win_bg"], fg=T["text"],
                                    font=(FONT_UI, 14, "bold"), width=24)
        self._cal_title.pack(side="left", expand=True)
        tk.Button(nav, text="▶", command=self._cal_next,
                  bg=T["button_bg"], fg=T["text"], relief="flat", bd=0,
                  font=(FONT_UI, 13), padx=8, cursor="hand2",
                  activebackground=T["button_hover"]).pack(side="right", padx=10)
        tk.Button(nav, text="Today", command=self._cal_today,
                  bg=T["button_bg"], fg=T["text"], relief="flat", bd=0,
                  font=(FONT_UI, 9), padx=8, cursor="hand2",
                  activebackground=T["button_hover"]).pack(side="right", padx=4)

        self._cal_grid = tk.Frame(f, bg=T["win_bg"])
        self._cal_grid.pack(pady=4)
        self._render_calendar()

        # Event panel
        ev_f = tk.Frame(f, bg=T["panel_alt"])
        ev_f.pack(fill="x", padx=12, pady=6)
        tk.Label(ev_f, text="Events for selected day:",
                 bg=T["panel_alt"], fg=T["text_muted"],
                 font=(FONT_UI, 9), padx=8).pack(anchor="w", pady=(4,2))
        self._event_lbl = tk.Label(ev_f, text="Click a date to see events",
                                    bg=T["panel_alt"], fg=T["text_muted"],
                                    font=(FONT_UI, 9), padx=8, wraplength=400,
                                    justify="left")
        self._event_lbl.pack(anchor="w", pady=(0,4))

        mkbtn(f, "+ Add Event", self._add_event, kind="accent").pack(pady=4)

    def _render_calendar(self) -> None:
        g = self._cal_grid
        for w in g.winfo_children():
            w.destroy()
        self._cal_title.config(
            text=f"{calendar.month_name[self._cal_month]} {self._cal_year}")
        today = datetime.date.today()
        days  = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        for col, d in enumerate(days):
            clr = T["danger"] if d in ("Sat","Sun") else T["text_muted"]
            tk.Label(g, text=d, bg=T["win_bg"], fg=clr,
                     font=(FONT_UI, 9, "bold"), width=5).grid(row=0, column=col, pady=3)
        for row, week in enumerate(calendar.monthcalendar(self._cal_year, self._cal_month), 1):
            for col, day in enumerate(week):
                if day == 0:
                    tk.Label(g, text="", bg=T["win_bg"], width=5).grid(row=row, column=col)
                    continue
                is_today    = (day == today.day and self._cal_month == today.month
                               and self._cal_year  == today.year)
                date_str    = f"{self._cal_year}-{self._cal_month:02d}-{day:02d}"
                has_event   = bool(self._events.get(date_str))
                bg   = T["accent"]  if is_today else T["win_bg"]
                fg   = "#ffffff"    if is_today else (T["danger"] if col >= 5 else T["text"])
                weight = "bold" if is_today or has_event else "normal"
                dot_text = f"{day}" + ("•" if has_event else "")
                lbl = tk.Label(g, text=dot_text, bg=bg, fg=fg,
                               font=(FONT_UI, 10, weight), width=5, cursor="hand2")
                lbl.grid(row=row, column=col, pady=2)
                lbl.bind("<Button-1>", lambda e, ds=date_str: self._show_day_events(ds))

    def _show_day_events(self, date_str: str) -> None:
        events = self._events.get(date_str, [])
        if events:
            self._event_lbl.config(
                text=f"{date_str}:\n" + "\n".join(f"• {ev}" for ev in events)
            )
        else:
            self._event_lbl.config(text=f"{date_str}: No events")

    def _add_event(self) -> None:
        date_str = simpledialog.askstring(
            "Add Event", "Date (YYYY-MM-DD):",
            initialvalue=datetime.date.today().strftime("%Y-%m-%d"),
            parent=self.wm.root,
        )
        if not date_str:
            return
        text = simpledialog.askstring("Add Event", "Event description:",
                                       parent=self.wm.root)
        if text:
            if date_str not in self._events:
                self._events[date_str] = []
            self._events[date_str].append(text)
            self._render_calendar()
            self.wm.notifs.send("Calendar", f"Event added: {text}", icon="📅")

    def _cal_prev(self) -> None:
        if self._cal_month == 1:
            self._cal_month = 12; self._cal_year -= 1
        else:
            self._cal_month -= 1
        self._render_calendar()

    def _cal_next(self) -> None:
        if self._cal_month == 12:
            self._cal_month = 1; self._cal_year += 1
        else:
            self._cal_month += 1
        self._render_calendar()

    def _cal_today(self) -> None:
        today = datetime.date.today()
        self._cal_year  = today.year
        self._cal_month = today.month
        self._render_calendar()

    # ── ALARM TAB ─────────────────────────────────────────────────────────────

    def _build_alarm(self) -> None:
        f = self._content
        tk.Label(f, text="Alarms", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold")).pack(pady=(12, 6))

        # Add alarm form
        form = tk.Frame(f, bg=T["panel_alt"])
        form.pack(fill="x", padx=14, pady=4)
        row1 = tk.Frame(form, bg=T["panel_alt"])
        row1.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(row1, text="Time (HH:MM):", bg=T["panel_alt"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(side="left")
        self._alarm_time = mkentry(row1, width=8)
        self._alarm_time.pack(side="left", padx=6)
        self._alarm_time.insert(0, datetime.datetime.now().strftime("%H:%M"))

        tk.Label(row1, text="Label:", bg=T["panel_alt"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(side="left", padx=(8, 0))
        self._alarm_label_entry = mkentry(row1, width=14)
        self._alarm_label_entry.pack(side="left", padx=6)
        self._alarm_label_entry.insert(0, "Wake up!")

        row2 = tk.Frame(form, bg=T["panel_alt"])
        row2.pack(fill="x", padx=8, pady=(0, 8))
        self._alarm_repeat = tk.BooleanVar(value=False)
        tk.Checkbutton(row2, text="Repeat daily",
                       variable=self._alarm_repeat,
                       bg=T["panel_alt"], fg=T["text"],
                       selectcolor=T["accent"],
                       activebackground=T["panel_alt"],
                       font=(FONT_UI, 9)).pack(side="left")
        mkbtn(row2, "Add Alarm", self._add_alarm, kind="accent").pack(side="right", padx=4)

        # Alarm list
        self._alarm_list_frame = tk.Frame(f, bg=T["win_bg"])
        self._alarm_list_frame.pack(fill="both", expand=True, padx=12, pady=4)
        self._render_alarms()

    def _add_alarm(self) -> None:
        t = self._alarm_time.get().strip()
        l = self._alarm_label_entry.get().strip()
        if not re.match(r"^\d{1,2}:\d{2}$", t):
            messagebox.showerror("Invalid Time", "Use HH:MM format", parent=self.wm.root)
            return
        self._alarms.append({
            "time": t, "label": l or "Alarm",
            "active": True, "repeat": self._alarm_repeat.get()
        })
        self._render_alarms()
        self.wm.notifs.send("Clock", f"Alarm set for {t}: {l}", icon="⏰")

    def _render_alarms(self) -> None:
        for w in self._alarm_list_frame.winfo_children():
            w.destroy()
        if not self._alarms:
            tk.Label(self._alarm_list_frame, text="No alarms set.",
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 10)).pack(pady=16)
            return
        for i, alarm in enumerate(self._alarms):
            bg   = T["panel_bg"] if i % 2 == 0 else T["win_bg"]
            row  = tk.Frame(self._alarm_list_frame, bg=bg)
            row.pack(fill="x", pady=1)
            # Toggle button (active indicator)
            state_txt = "🔔" if alarm["active"] else "🔕"
            state_col = T["success"] if alarm["active"] else T["text_muted"]
            tk.Button(row, text=state_txt,
                      command=partial(self._toggle_alarm, i),
                      bg=bg, fg=state_col, relief="flat", bd=0,
                      font=(FONT_EMOJI, 14), padx=4, cursor="hand2",
                      activebackground=bg).pack(side="left", padx=4)
            # Info
            info = tk.Frame(row, bg=bg)
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=alarm["time"], bg=bg, fg=T["text"],
                     font=(FONT_MONO, 14, "bold")).pack(anchor="w")
            rep_txt = "  🔁 Daily" if alarm.get("repeat") else ""
            tk.Label(info, text=alarm["label"] + rep_txt, bg=bg,
                     fg=T["text_muted"], font=(FONT_UI, 9)).pack(anchor="w")
            # Delete
            tk.Button(row, text="🗑️",
                      command=partial(self._delete_alarm, i),
                      bg=bg, fg=T["danger"], relief="flat", bd=0,
                      font=(FONT_EMOJI, 12), padx=8, cursor="hand2",
                      activebackground=bg).pack(side="right")

    def _toggle_alarm(self, idx: int) -> None:
        self._alarms[idx]["active"] = not self._alarms[idx]["active"]
        self._render_alarms()

    def _delete_alarm(self, idx: int) -> None:
        self._alarms.pop(idx)
        self._render_alarms()

    # ── STOPWATCH TAB ─────────────────────────────────────────────────────────

    def _build_stopwatch(self) -> None:
        f = self._content
        tk.Label(f, text="Stopwatch", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold")).pack(pady=(12, 4))

        self._sw_display = tk.Label(f, text="00:00.000",
                                     bg=T["win_bg"], fg=T["text"],
                                     font=(FONT_MONO, 36, "bold"))
        self._sw_display.pack(pady=12)

        # Progress ring (canvas)
        self._sw_ring = tk.Canvas(f, bg=T["win_bg"], width=160, height=20,
                                   highlightthickness=0)
        self._sw_ring.pack()

        ctrl = tk.Frame(f, bg=T["win_bg"])
        ctrl.pack(pady=8)
        self._sw_start_btn = mkbtn(ctrl, "▶  Start", self._sw_toggle, kind="accent")
        self._sw_start_btn.pack(side="left", padx=8)
        mkbtn(ctrl, "⏺  Lap",   self._sw_lap).pack(side="left", padx=8)
        mkbtn(ctrl, "↺  Reset", self._sw_reset, kind="danger").pack(side="left", padx=8)

        # Laps
        lap_outer = tk.Frame(f, bg=T["panel_alt"])
        lap_outer.pack(fill="both", expand=True, padx=12, pady=6)
        tk.Label(lap_outer, text="LAP TIMES",
                 bg=T["panel_alt"], fg=T["text_muted"],
                 font=(FONT_UI, 8, "bold"), padx=8).pack(anchor="w", pady=(4,2))
        sf2 = ScrollableFrame(lap_outer, bg=T["panel_alt"])
        sf2.pack(fill="both", expand=True)
        self._lap_inner = sf2.inner

        self._sw_tick()

    def _sw_toggle(self) -> None:
        self._sw_running = not self._sw_running
        if self._sw_running:
            self._sw_start = time.time() - self._sw_elapsed
            self._sw_start_btn.config(text="⏸  Pause")
        else:
            self._sw_elapsed = time.time() - self._sw_start
            self._sw_start_btn.config(text="▶  Resume")

    def _sw_lap(self) -> None:
        if not self._sw_running:
            return
        elapsed = time.time() - self._sw_start
        self._sw_laps.append(elapsed)
        self._render_laps()

    def _render_laps(self) -> None:
        for w in self._lap_inner.winfo_children():
            w.destroy()
        prev = 0.0
        for i, lap in enumerate(self._sw_laps):
            split = lap - prev; prev = lap
            m, s = divmod(lap, 60)
            sm, ss = divmod(split, 60)
            bg = T["panel_alt"] if i % 2 == 0 else T["win_bg"]
            row = tk.Frame(self._lap_inner, bg=bg)
            row.pack(fill="x")
            tk.Label(row, text=f"Lap {i+1:3d}", bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 9), width=8).pack(side="left", padx=4, pady=2)
            tk.Label(row, text=f"{int(m):02d}:{s:06.3f}", bg=bg, fg=T["text"],
                     font=(FONT_MONO, 10)).pack(side="left")
            tk.Label(row, text=f"  +{int(sm):02d}:{ss:06.3f}", bg=bg,
                     fg=T["text_muted"], font=(FONT_MONO, 9)).pack(side="left")

    def _sw_reset(self) -> None:
        self._sw_running = False
        self._sw_elapsed = 0.0
        self._sw_start   = 0.0
        self._sw_laps    = []
        self._sw_display.config(text="00:00.000")
        self._sw_start_btn.config(text="▶  Start")
        if hasattr(self, "_lap_inner"):
            for w in self._lap_inner.winfo_children():
                w.destroy()

    def _sw_tick(self) -> None:
        if not self._out.winfo_exists() or self._tab != "stopwatch":
            return
        if self._sw_running:
            elapsed = time.time() - self._sw_start
        else:
            elapsed = self._sw_elapsed
        m, s = divmod(elapsed, 60)
        ms   = int((s - int(s)) * 1000)
        try:
            self._sw_display.config(text=f"{int(m):02d}:{int(s):02d}.{ms:03d}")
            # Draw ring
            c  = self._sw_ring
            W  = c.winfo_width() or 160
            c.delete("all")
            c.create_rectangle(0, 4, W, 12, fill=T["button_bg"], outline="")
            frac = (s % 60) / 60
            c.create_rectangle(0, 4, int(W * frac), 12,
                                fill=T["accent"], outline="")
        except Exception:
            pass
        self.wm.root.after(30, self._sw_tick)

    # ── WORLD CLOCK TAB ───────────────────────────────────────────────────────

    def _build_world(self) -> None:
        f = self._content
        tk.Label(f, text="World Clock", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold")).pack(pady=(12, 8))

        ZONES = [
            ("🗽 New York",    -5),  ("🌁 Los Angeles", -8),
            ("🌎 Chicago",    -6),  ("🌎 São Paulo",   -3),
            ("🗼 London",      0),  ("🗼 Paris",        1),
            ("🏛️ Berlin",     1),  ("🌅 Moscow",       3),
            ("🏙️ Dubai",      4),  ("🏯 Mumbai",       5.5),
            ("🏙️ Bangkok",   7),  ("🌆 Singapore",    8),
            ("⛩️ Tokyo",      9),  ("🦘 Sydney",      10),
            ("🌏 Auckland",  12),
        ]
        g = tk.Frame(f, bg=T["win_bg"])
        g.pack(fill="both", expand=True, padx=12, pady=4)
        self._world_labels: List[Tuple[tk.Label, float]] = []
        for i, (city, off) in enumerate(ZONES):
            row2, col = divmod(i, 3)
            cell = tk.Frame(g, bg=T["panel_alt"] if i % 2 == 0 else T["panel_bg"],
                             padx=8, pady=6)
            cell.grid(row=row2, column=col, padx=3, pady=2, sticky="ew")
            g.columnconfigure(col, weight=1)
            tk.Label(cell, text=city, bg=cell.cget("bg"), fg=T["text_muted"],
                     font=(FONT_UI, 8)).pack(anchor="w")
            lbl = tk.Label(cell, text="", bg=cell.cget("bg"), fg=T["text"],
                           font=(FONT_MONO, 12, "bold"))
            lbl.pack(anchor="w")
            self._world_labels.append((lbl, off))
        self._world_tick()

    def _world_tick(self) -> None:
        if not self._out.winfo_exists() or self._tab != "world":
            return
        now = datetime.datetime.utcnow()
        for lbl, off in self._world_labels:
            try:
                local = now + datetime.timedelta(hours=off)
                lbl.config(text=local.strftime("%H:%M:%S"))
            except Exception:
                pass
        self.wm.root.after(1000, self._world_tick)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 23 — TASK MANAGER APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class TaskManagerApp(BaseWin):
    """
    Five-tab task manager:
      1. Processes — sortable list, kill, spawn, filter
      2. Performance — live CPU + RAM graphs (canvas-drawn)
      3. Users     — sessions, login info
      4. Disk      — pie chart + breakdown
      5. Network   — interface table + simulated traffic
    """

    def __init__(self, wm: WM) -> None:
        self._tab     = "processes"
        self._sel_pid: Optional[int] = None
        self._cpu_hist: deque = deque([0.0] * 60, maxlen=60)
        self._mem_hist: deque = deque([0.0] * 60, maxlen=60)
        super().__init__(wm, "Task Manager", 290, 90, 780, 560, "📊",
                         min_w=400, min_h=320)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])

        # Tab bar
        tab_bar = tk.Frame(parent, bg=T["panel_bg"])
        tab_bar.pack(fill="x")
        self._tab_btns: Dict[str, tk.Button] = {}
        for label in ["Processes","Performance","Users","Disk","Network"]:
            k = label.lower()
            b = tk.Button(tab_bar, text=label,
                          command=partial(self._switch_tab, k),
                          bg=T["accent"] if k == self._tab else T["button_bg"],
                          fg=T["text"], relief="flat", bd=0,
                          font=(FONT_UI, 10), padx=14, pady=6, cursor="hand2",
                          activebackground=T["button_hover"])
            b.pack(side="left", padx=2, pady=4)
            self._tab_btns[k] = b

        self._content = tk.Frame(parent, bg=T["win_bg"])
        self._content.pack(fill="both", expand=True)

        # Footer
        footer = tk.Frame(parent, bg=T["status_bg"], height=34)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        self._footer_lbl = tk.Label(footer, text="",
                                     bg=T["status_bg"], fg=T["text_muted"],
                                     font=(FONT_UI, 8), anchor="w", padx=8)
        self._footer_lbl.pack(side="left", fill="y")
        mkbtn(footer, "⚠️  End Task",  self._kill_selected, kind="danger").pack(
            side="right", padx=8, pady=4)
        mkbtn(footer, "+  New Process", self._new_process).pack(
            side="right", padx=4, pady=4)

        self._build_processes()
        self._update_footer()

    def _switch_tab(self, tab: str) -> None:
        self._tab = tab
        for k, b in self._tab_btns.items():
            b.config(bg=T["accent"] if k == tab else T["button_bg"])
        for w in self._content.winfo_children():
            w.destroy()
        {
            "processes":  self._build_processes,
            "performance":self._build_performance,
            "users":      self._build_users,
            "disk":       self._build_disk,
            "network":    self._build_network,
        }[tab]()

    # ── PROCESSES TAB ─────────────────────────────────────────────────────────

    def _build_processes(self) -> None:
        f = self._content

        # Search + controls
        ctrl = tk.Frame(f, bg=T["win_bg"])
        ctrl.pack(fill="x", padx=8, pady=4)
        tk.Label(ctrl, text="🔍", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 11)).pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda *_: self._refresh_procs())
        mkentry(ctrl, textvariable=self._search_var, width=22).pack(side="left", padx=4)
        tk.Button(ctrl, text="⟳  Refresh", command=self._refresh_procs,
                  bg=T["button_bg"], fg=T["text"], relief="flat", bd=0,
                  font=(FONT_UI, 9), padx=8, cursor="hand2",
                  activebackground=T["button_hover"]).pack(side="left", padx=4)
        self._sort_key  = "pid"
        self._sort_rev  = False

        # Headers
        hdr = tk.Frame(f, bg=T["panel_alt"])
        hdr.pack(fill="x", padx=4)
        for txt, key, w in [("PID",50),("Name",180),("User",80),
                              ("CPU%",65),("MEM(MB)",75),("Status",80),("Uptime",80)]:
            tk.Button(hdr, text=txt,
                      command=partial(self._sort_procs, txt.lower().replace("%","").replace("(mb)","")),
                      bg=T["panel_alt"], fg=T["text_muted"],
                      relief="flat", bd=0,
                      font=(FONT_UI, 9, "bold"),
                      width=w//8, anchor="w", padx=4, pady=3, cursor="hand2",
                      activebackground=T["button_hover"]).pack(side="left")

        # Scrollable list
        sf = ScrollableFrame(f, bg=T["win_bg"])
        sf.pack(fill="both", expand=True, padx=4)
        self._proc_inner = sf.inner
        self._refresh_procs()
        self._proc_tick()

    def _sort_procs(self, key: str) -> None:
        if self._sort_key == key:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_key = key
            self._sort_rev = False
        self._refresh_procs()

    def _refresh_procs(self) -> None:
        for w in self._proc_inner.winfo_children():
            w.destroy()
        q       = self._search_var.get().lower() if hasattr(self, "_search_var") else ""
        procs   = self.wm.procs.list_all()
        key_map = {
            "pid":    lambda p: p.pid,
            "name":   lambda p: p.name.lower(),
            "user":   lambda p: p.owner,
            "cpu":    lambda p: p.cpu,
            "mem":    lambda p: p.mem,
            "status": lambda p: p.status,
            "uptime": lambda p: p.uptime_secs,
        }
        sfn = key_map.get(self._sort_key, key_map["pid"])
        procs = sorted(procs, key=sfn, reverse=self._sort_rev)
        for i, p in enumerate(procs):
            if q and q not in p.name.lower() and q not in p.owner.lower():
                continue
            is_sel = p.pid == self._sel_pid
            bg     = T["selection"] if is_sel else (T["panel_bg"] if i % 2 == 0 else T["win_bg"])
            row    = tk.Frame(self._proc_inner, bg=bg, cursor="hand2")
            row.pack(fill="x")
            cpu_bar = "█" * max(0, int(p.cpu / 10))
            for val, wd in [
                (str(p.pid), 50),
                (p.name[:22], 180),
                (p.owner, 80),
                (f"{p.cpu:.1f}% {cpu_bar}", 65),
                (f"{p.mem}", 75),
                (p.status, 80),
                (p.uptime, 80),
            ]:
                tk.Label(row, text=val, bg=bg, fg=T["text"],
                         font=(FONT_MONO, 9), width=wd//8, anchor="w").pack(
                    side="left", padx=4, pady=2)
            for child in row.winfo_children() + [row]:
                child.bind("<Button-1>",
                           lambda e, pid=p.pid: (
                               setattr(self, "_sel_pid", pid),
                               self._refresh_procs(),
                           ))

    def _kill_selected(self) -> None:
        if self._sel_pid:
            if self.wm.procs.kill(self._sel_pid):
                self.wm.notifs.send("Task Manager",
                                     f"Killed PID {self._sel_pid}", icon="💀")
                self._sel_pid = None
                self._refresh_procs()
            else:
                messagebox.showwarning("Error",
                                        f"Could not kill PID {self._sel_pid}",
                                        parent=self.wm.root)

    def _new_process(self) -> None:
        name = simpledialog.askstring("New Process", "Process name:",
                                       parent=self.wm.root)
        if name:
            p = self.wm.procs.spawn(name)
            self.wm.notifs.send("Task Manager",
                                 f"Spawned: {name} (PID {p.pid})", icon="⚡")
            self._refresh_procs()

    def _proc_tick(self) -> None:
        if not self._out.winfo_exists() or self._tab != "processes":
            return
        self._refresh_procs()
        self._update_footer()
        self.wm.root.after(2000, self._proc_tick)

    def _update_footer(self) -> None:
        try:
            n   = self.wm.procs.process_count
            cpu = self.wm.procs.total_cpu
            mem = self.wm.procs.total_mem
            self._footer_lbl.config(
                text=f"Processes: {n}  |  CPU: {cpu:.1f}%  |  Memory: {mem} MB  |  Uptime: {self.wm.users.uptime}"
            )
        except Exception:
            pass

    # ── PERFORMANCE TAB ───────────────────────────────────────────────────────

    def _build_performance(self) -> None:
        f = self._content

        for title, attr_c, attr_p, col in [
            ("CPU Usage",    "_cpu_canvas",  "_cpu_pct",  T["accent"]),
            ("Memory Usage", "_mem_canvas",  "_mem_pct",  T["success"]),
        ]:
            lf = tk.LabelFrame(f, text=f"  {title}  ",
                                bg=T["win_bg"], fg=T["text"],
                                font=(FONT_UI, 10, "bold"),
                                labelanchor="n", padx=8, pady=4)
            lf.pack(fill="x", padx=16, pady=8)

            canvas = tk.Canvas(lf, bg=T["panel_alt"], height=110,
                                highlightthickness=0)
            canvas.pack(fill="x")
            setattr(self, attr_c, canvas)

            pf = tk.Frame(lf, bg=T["win_bg"])
            pf.pack(fill="x")
            pct = tk.Label(pf, text="0%", bg=T["win_bg"], fg=col,
                            font=(FONT_MONO, 16, "bold"))
            pct.pack(side="left", padx=4)
            setattr(self, attr_p, pct)

            detail = tk.Label(pf, text="", bg=T["win_bg"], fg=T["text_muted"],
                               font=(FONT_UI, 9))
            detail.pack(side="left", padx=8)
            setattr(self, attr_c + "_detail", detail)

        # Stats summary
        stats_f = tk.Frame(f, bg=T["panel_alt"])
        stats_f.pack(fill="x", padx=16, pady=6)
        self._stats_labels: List[tk.Label] = []
        for i, key in enumerate(["Processes","Threads","Handles","Up Time","Boot Time"]):
            bg = T["panel_alt"]
            col2, row2 = divmod(i, 3)
            cell = tk.Frame(stats_f, bg=bg)
            cell.grid(row=row2, column=col2, padx=12, pady=4, sticky="w")
            tk.Label(cell, text=key, bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 8)).pack(anchor="w")
            lbl = tk.Label(cell, text="—", bg=bg, fg=T["text"],
                            font=(FONT_MONO, 10, "bold"))
            lbl.pack(anchor="w")
            self._stats_labels.append(lbl)

        self._perf_tick()

    def _perf_tick(self) -> None:
        if not self._out.winfo_exists() or self._tab != "performance":
            return
        cpu = self.wm.procs.total_cpu
        mem = self.wm.procs.total_mem
        self._cpu_hist.append(cpu)
        self._mem_hist.append(min(100, mem / 81.92))   # 8192 MB total

        self._draw_graph(self._cpu_canvas, list(self._cpu_hist), T["accent"])
        self._draw_graph(self._mem_canvas, list(self._mem_hist), T["success"])

        self._cpu_pct.config(text=f"{cpu:.1f}%")
        self._mem_pct.config(text=f"{mem} MB")
        self._cpu_canvas_detail.config(text=f"Load: {cpu:.2f}%  Cores: 4  Freq: 3.2 GHz")
        self._mem_canvas_detail.config(text=f"{mem} MB used / 8192 MB total")

        # Stats
        procs = self.wm.procs.list_all()
        threads = sum(p.threads for p in procs)
        handles = sum(p.fd_count for p in procs)
        vals = [
            str(len(procs)),
            str(threads),
            str(handles),
            self.wm.users.uptime,
            datetime.datetime.fromtimestamp(
                self.wm.users.login_time or time.time()
            ).strftime("%H:%M:%S"),
        ]
        for lbl, val in zip(self._stats_labels, vals):
            lbl.config(text=val)

        self.wm.root.after(1500, self._perf_tick)

    def _draw_graph(self, canvas: tk.Canvas, data: List[float], color: str) -> None:
        canvas.delete("all")
        W = canvas.winfo_width() or 700
        H = canvas.winfo_height() or 110
        canvas.create_rectangle(0, 0, W, H, fill=T["panel_alt"], outline="")

        # Grid lines
        for pct in (25, 50, 75, 100):
            y = H - int(H * pct / 100)
            canvas.create_line(0, y, W, y, fill=T["text_dim"], dash=(3, 6))
            canvas.create_text(4, y - 6, text=f"{pct}%", fill=T["text_muted"],
                                font=(FONT_UI, 7), anchor="w")

        if len(data) < 2:
            return

        # Filled area
        step = W / max(len(data) - 1, 1)
        pts  = [0, H]
        for i, v in enumerate(data):
            x = i * step
            y = H - (v / 100) * H
            pts.extend([x, y])
        pts.extend([W, H])
        canvas.create_polygon(pts, fill=color + "33", outline="", smooth=True)

        # Line
        line_pts = []
        for i, v in enumerate(data):
            line_pts.extend([i * step, H - (v / 100) * H])
        if len(line_pts) >= 4:
            canvas.create_line(line_pts, fill=color, width=2, smooth=True)

        # Current value dot
        if data:
            lv = data[-1]
            x  = (len(data) - 1) * step
            y  = H - (lv / 100) * H
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4,
                                fill=color, outline=T["win_bg"], width=2)

    # ── USERS TAB ─────────────────────────────────────────────────────────────

    def _build_users(self) -> None:
        f = self._content
        tk.Label(f, text="Active Sessions", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold")).pack(pady=(12, 6))

        for acct in self.wm.users.all_accounts():
            card = tk.Frame(f, bg=T["panel_alt"], padx=14, pady=10)
            card.pack(fill="x", padx=16, pady=5)

            av = tk.Label(card, text=acct.username[0].upper(),
                          bg=acct.avatar_color, fg="#ffffff",
                          font=(FONT_UI, 18, "bold"), width=2)
            av.pack(side="left", padx=(0, 12))

            info = tk.Frame(card, bg=T["panel_alt"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=acct.fullname, bg=T["panel_alt"], fg=T["text"],
                     font=(FONT_UI, 11, "bold")).pack(anchor="w")
            is_current = acct.username == self.wm.users.current
            status = (f"● Online  •  Session: {self.wm.users.uptime}"
                      if is_current else "○ Offline")
            tk.Label(info, text=f"@{acct.username}  •  {status}",
                     bg=T["panel_alt"], fg=T["success"] if is_current else T["text_muted"],
                     font=(FONT_UI, 9)).pack(anchor="w")
            if acct.last_login:
                tk.Label(info,
                         text=f"Last login: {fmt_time(acct.last_login)}  •  Logins: {acct.login_count}",
                         bg=T["panel_alt"], fg=T["text_muted"],
                         font=(FONT_UI, 8)).pack(anchor="w")
            role_lbl = tk.Label(card,
                                 text="Admin" if acct.admin else "User",
                                 bg=T["accent"] if acct.admin else T["button_bg"],
                                 fg="#ffffff", font=(FONT_UI, 8), padx=6, pady=2)
            role_lbl.pack(side="right")

        mksep(f).pack(fill="x", padx=16, pady=8)
        tk.Label(f, text="Session Log", bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 9, "bold")).pack(anchor="w", padx=16)
        log_f = tk.Frame(f, bg=T["panel_alt"])
        log_f.pack(fill="both", expand=True, padx=16, pady=6)
        lb = tk.Listbox(log_f, bg=T["panel_alt"], fg=T["text_muted"],
                         font=(FONT_MONO, 9), relief="flat", bd=0,
                         selectbackground=T["selection"])
        lb.pack(fill="both", expand=True, padx=4, pady=4)
        for entry in reversed(self.wm.users.session_log[-20:]):
            lb.insert("end", entry)

    # ── DISK TAB ──────────────────────────────────────────────────────────────

    def _build_disk(self) -> None:
        f = self._content
        tk.Label(f, text="Disk Usage", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold")).pack(pady=(12, 6))

        used, total = self.wm.vfs.disk_usage()
        free = total - used
        pct  = used * 100 // max(total, 1)

        # Pie chart
        chart_f = tk.Frame(f, bg=T["win_bg"])
        chart_f.pack(pady=6)
        pie = tk.Canvas(chart_f, bg=T["win_bg"], width=200, height=200,
                         highlightthickness=0)
        pie.pack(side="left", padx=20)

        if pct > 0:
            extent = min(359.9, pct * 3.6)
            pie.create_arc(10, 10, 190, 190, start=90, extent=-extent,
                            fill=T["accent"], outline="")
        pie.create_arc(10, 10, 190, 190, start=90 - pct*3.6, extent=-(360-pct*3.6),
                        fill=T["success"], outline="")
        pie.create_oval(60, 60, 140, 140, fill=T["win_bg"], outline="")
        pie.create_text(100, 100, text=f"{pct}%", fill=T["text"],
                         font=(FONT_MONO, 14, "bold"))

        # Legend
        leg = tk.Frame(chart_f, bg=T["win_bg"])
        leg.pack(side="left", padx=10)
        for label, val, col in [
            ("Used",  fmt_size(used),  T["accent"]),
            ("Free",  fmt_size(free),  T["success"]),
            ("Total", fmt_size(total), T["text_muted"]),
        ]:
            row = tk.Frame(leg, bg=T["win_bg"])
            row.pack(anchor="w", pady=4)
            tk.Frame(row, bg=col, width=14, height=14).pack(side="left")
            tk.Label(row, text=f"  {label}: {val}", bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 10)).pack(side="left")

        # Extension breakdown
        mksep(f).pack(fill="x", padx=16, pady=6)
        tk.Label(f, text="By File Type", bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 9, "bold")).pack(anchor="w", padx=16)

        ext_groups = self.wm.vfs.get_ext_groups()
        top_exts   = sorted(ext_groups.items(), key=lambda x: -x[1])[:10]

        sf2 = ScrollableFrame(f, bg=T["win_bg"])
        sf2.pack(fill="both", expand=True, padx=16)
        max_sz = top_exts[0][1] if top_exts else 1
        colors = [T["chart1"], T["chart2"], T["chart3"], T["chart4"], T["chart5"]]

        for i, (ext, sz) in enumerate(top_exts):
            bg  = T["win_bg"] if i % 2 == 0 else T["panel_bg"]
            row = tk.Frame(sf2.inner, bg=bg)
            row.pack(fill="x", pady=1)
            tk.Label(row, text=f".{ext}", bg=bg, fg=T["text"],
                     font=(FONT_MONO, 9), width=8, anchor="w").pack(side="left", padx=4)
            bar_w = max(4, int(200 * sz / max_sz))
            col   = colors[i % len(colors)]
            tk.Frame(row, bg=col, width=bar_w, height=12).pack(side="left")
            tk.Label(row, text=fmt_size(sz), bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 8), padx=6).pack(side="left")

    # ── NETWORK TAB ───────────────────────────────────────────────────────────

    def _build_network(self) -> None:
        f = self._content
        tk.Label(f, text="Network Interfaces", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold")).pack(pady=(12, 6))

        ifaces = [
            ("eth0",  "192.168.1.100", "255.255.255.0", "192.168.1.1",
             "1000 Mbps", "Ethernet",   True),
            ("wlan0", "10.0.0.50",     "255.255.255.0", "10.0.0.1",
             "300 Mbps",  "WiFi",       True),
            ("lo",    "127.0.0.1",     "255.0.0.0",     "—",
             "—",         "Loopback",   True),
            ("docker0","172.17.0.1",   "255.255.0.0",   "—",
             "—",         "Virtual",    False),
        ]
        for iface, ip, mask, gw, speed, kind, up in ifaces:
            card = tk.Frame(f, bg=T["panel_alt"], padx=12, pady=8)
            card.pack(fill="x", padx=14, pady=4)
            hdr  = tk.Frame(card, bg=T["panel_alt"])
            hdr.pack(fill="x")
            tk.Label(hdr, text=f"🌐  {iface}", bg=T["panel_alt"], fg=T["text"],
                     font=(FONT_UI, 11, "bold")).pack(side="left")
            tk.Label(hdr, text=kind, bg=T["panel_alt"], fg=T["text_muted"],
                     font=(FONT_UI, 9)).pack(side="left", padx=8)
            state_col = T["success"] if up else T["danger"]
            tk.Label(hdr, text="● UP" if up else "● DOWN",
                     bg=T["panel_alt"], fg=state_col,
                     font=(FONT_UI, 9, "bold")).pack(side="right")
            for label, val in [("IP", ip), ("Mask", mask),
                                 ("Gateway", gw), ("Speed", speed),
                                 ("TX", f"{random.randint(10,500)} KB/s"),
                                 ("RX", f"{random.randint(10,800)} KB/s")]:
                row = tk.Frame(card, bg=T["panel_alt"])
                row.pack(anchor="w")
                tk.Label(row, text=f"  {label}:", bg=T["panel_alt"],
                         fg=T["text_muted"], font=(FONT_UI, 9), width=9,
                         anchor="e").pack(side="left")
                tk.Label(row, text=val, bg=T["panel_alt"], fg=T["text"],
                         font=(FONT_MONO, 9)).pack(side="left", padx=4)

        # Simulated traffic graph
        mksep(f).pack(fill="x", padx=14, pady=6)
        tk.Label(f, text="Network Traffic (simulated)",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 9, "bold")).pack(anchor="w", padx=14)
        net_c = tk.Canvas(f, bg=T["panel_alt"], height=80, highlightthickness=0)
        net_c.pack(fill="x", padx=14, pady=4)

        def draw_traffic() -> None:
            if not self._out.winfo_exists() or self._tab != "network":
                return
            net_c.delete("all")
            W = net_c.winfo_width() or 740
            H = net_c.winfo_height() or 80
            n = 60
            tx_data = [random.randint(10, 400) for _ in range(n)]
            rx_data = [random.randint(10, 800) for _ in range(n)]
            max_v   = max(max(tx_data), max(rx_data), 1)
            step    = W / max(n - 1, 1)
            for data, col in [(tx_data, T["accent"]), (rx_data, T["success"])]:
                pts = []
                for i, v in enumerate(data):
                    pts.extend([i * step, H - (v / max_v) * H * 0.9])
                if len(pts) >= 4:
                    net_c.create_line(pts, fill=col, width=1, smooth=True)
            net_c.create_text(4, 6, text=f"TX ←  RX →", fill=T["text_muted"],
                               font=(FONT_UI, 7), anchor="nw")
            self.wm.root.after(2000, draw_traffic)

        net_c.after(100, draw_traffic)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 24 — NOTES APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class NotesApp(BaseWin):
    """
    Rich notes application with:
      • Sidebar note list with search
      • Rich text body (colour, bold, size tags via menu)
      • Tags / labels per note
      • Pin notes to top
      • Word count + character count status
      • Export note to VFS file
      • Sort by: name, date, size
      • New note templates
    """

    TEMPLATES = {
        "Blank":          "",
        "Meeting Notes":  "Meeting Notes\n=============\nDate: {date}\nAttendees:\n\nAgenda:\n1. \n2. \n\nAction Items:\n- \n",
        "Daily Journal":  "Journal — {date}\n==================\n\nMorning thoughts:\n\nHighlights of the day:\n\nGrateful for:\n1. \n2. \n3. \n\nTomorrow's goals:\n",
        "Bug Report":     "Bug Report\n==========\nDate: {date}\n\nTitle:\nSeverity: Low / Medium / High / Critical\n\nDescription:\n\nSteps to Reproduce:\n1. \n2. \n\nExpected:\nActual:\n\nNotes:\n",
        "Recipe":         "Recipe: \n=========\nServings:\nPrep Time:\nCook Time:\n\nIngredients:\n- \n\nInstructions:\n1. \n2. \n\nNotes:\n",
        "Code Snippet":   "# Code Snippet\n# Language: \n# Date: {date}\n\n",
    }

    def __init__(self, wm: WM) -> None:
        self._notes:     List[Dict[str, Any]] = []
        self._cur_idx:   Optional[int]        = None
        self._tags_cache: Dict[int, List[str]] = {}
        super().__init__(wm, "Notes", 580, 90, 800, 560, "📓",
                         min_w=400, min_h=300)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])

        pane = tk.PanedWindow(parent, orient="horizontal",
                               bg=T["panel_bg"], sashwidth=5, sashrelief="flat")
        pane.pack(fill="both", expand=True)

        # Left sidebar
        sidebar = tk.Frame(pane, bg=T["panel_bg"], width=220)
        pane.add(sidebar, minsize=160)
        self._build_sidebar(sidebar)

        # Right editor area
        editor_area = tk.Frame(pane, bg=T["win_bg"])
        pane.add(editor_area, minsize=300)
        self._build_editor(editor_area)

        # Load notes from VFS
        self._load_notes()

    def _build_sidebar(self, parent: tk.Frame) -> None:
        # Header
        hdr = tk.Frame(parent, bg=T["panel_bg"])
        hdr.pack(fill="x", padx=8, pady=(8, 2))
        tk.Label(hdr, text="Notes", bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 11, "bold")).pack(side="left")
        tk.Label(hdr, text="0", bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 9)).pack(side="right")
        self._count_lbl = hdr.winfo_children()[-1]

        # Search
        self._note_search = tk.StringVar()
        self._note_search.trace("w", lambda *_: self._filter_notes())
        se = mkentry(parent, textvariable=self._note_search, width=24)
        se.pack(fill="x", padx=8, pady=4)
        se.insert(0, "🔍  Search notes…")
        se.bind("<FocusIn>",
                lambda e: se.delete(0, "end") if se.get().startswith("🔍") else None)

        # Sort bar
        sort_f = tk.Frame(parent, bg=T["panel_bg"])
        sort_f.pack(fill="x", padx=8)
        self._sort_notes_key = tk.StringVar(value="date")
        for lbl, key in [("Name","name"),("Date","date"),("Size","size")]:
            tk.Radiobutton(sort_f, text=lbl, variable=self._sort_notes_key,
                           value=key, command=self._sort_and_render,
                           bg=T["panel_bg"], fg=T["text_muted"],
                           selectcolor=T["accent"], activebackground=T["panel_bg"],
                           font=(FONT_UI, 8)).pack(side="left", padx=4)

        # Note list
        sf = ScrollableFrame(parent, bg=T["panel_bg"])
        sf.pack(fill="both", expand=True)
        self._notes_inner = sf.inner

        # New note button
        mksep(parent).pack(fill="x", padx=6, pady=4)
        self._template_var = tk.StringVar(value="Blank")
        tmpl_menu = ttk.Combobox(parent, textvariable=self._template_var,
                                  values=list(self.TEMPLATES.keys()),
                                  state="readonly", width=14)
        tmpl_menu.pack(side="left", padx=8, pady=6)
        mkbtn(parent, "＋ New", self._new_note, kind="accent").pack(
            side="left", padx=4, pady=6)

    def _build_editor(self, parent: tk.Frame) -> None:
        # Title bar
        title_f = tk.Frame(parent, bg=T["panel_alt"], height=38)
        title_f.pack(fill="x")
        title_f.pack_propagate(False)

        self._title_var = tk.StringVar()
        title_entry = tk.Entry(title_f, textvariable=self._title_var,
                                bg=T["panel_alt"], fg=T["text"],
                                insertbackground=T["text"],
                                relief="flat", font=(FONT_UI, 12, "bold"),
                                bd=6)
        title_entry.pack(side="left", fill="both", expand=True, padx=4)
        title_entry.bind("<KeyRelease>", lambda e: self._save_current())

        mkbtn(title_f, "💾", self._save_current).pack(side="right", padx=4, pady=4)
        mkbtn(title_f, "📌", self._pin_note).pack(side="right", padx=2, pady=4)
        mkbtn(title_f, "📤", self._export_note).pack(side="right", padx=2, pady=4)
        mkbtn(title_f, "🗑️", self._delete_note, kind="danger").pack(
            side="right", padx=4, pady=4)

        # Format toolbar
        fmt_f = tk.Frame(parent, bg=T["panel_bg"], height=30)
        fmt_f.pack(fill="x")
        fmt_f.pack_propagate(False)
        for lbl, cmd in [("B", self._fmt_bold), ("I", self._fmt_italic),
                           ("U", self._fmt_under), ("—", self._insert_sep),
                           ("Date", self._insert_date), ("Time", self._insert_time)]:
            tk.Button(fmt_f, text=lbl, command=cmd,
                      bg=T["panel_bg"], fg=T["text"], relief="flat", bd=0,
                      font=(FONT_UI, 9, "bold") if lbl in ("B","I","U") else (FONT_UI, 8),
                      padx=7, pady=2, cursor="hand2",
                      activebackground=T["button_hover"]).pack(side="left", padx=1, pady=2)

        # Tags input
        tags_f = tk.Frame(parent, bg=T["panel_bg"])
        tags_f.pack(fill="x")
        tk.Label(tags_f, text="Tags:", bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8), padx=6).pack(side="left")
        self._tags_var = tk.StringVar()
        tags_entry = tk.Entry(tags_f, textvariable=self._tags_var,
                               bg=T["panel_bg"], fg=T["text_muted"],
                               insertbackground=T["text"], relief="flat",
                               font=(FONT_UI, 8), bd=0)
        tags_entry.pack(side="left", fill="x", expand=True, padx=4, pady=3)
        tags_entry.bind("<KeyRelease>", lambda e: self._save_current())

        # Body
        self.body = ScrollText(parent, font=(FONT_UI, 11), wrap="word")
        self.body.pack(fill="both", expand=True)
        self.body.text.bind("<KeyRelease>", self._on_body_key)
        self.body.text.bind("<Control-s>",  lambda e: self._save_current())

        # Format tags for text widget
        self.body.text.tag_configure("bold",      font=(FONT_UI, 11, "bold"))
        self.body.text.tag_configure("italic",    font=(FONT_UI, 11, "italic"))
        self.body.text.tag_configure("underline", underline=True)

        # Status
        sf = tk.Frame(parent, bg=T["status_bg"], height=22)
        sf.pack(fill="x", side="bottom")
        sf.pack_propagate(False)
        self._note_status = tk.Label(sf, text="",
                                      bg=T["status_bg"], fg=T["text_muted"],
                                      font=(FONT_UI, 8), anchor="w", padx=8)
        self._note_status.pack(side="left", fill="y")
        self._note_time_lbl = tk.Label(sf, text="",
                                        bg=T["status_bg"], fg=T["text_muted"],
                                        font=(FONT_UI, 8), padx=8)
        self._note_time_lbl.pack(side="right")

    # ── notes loading ─────────────────────────────────────────────────────────

    def _load_notes(self) -> None:
        self._notes.clear()
        for folder in ["/home/user/Documents", "/home/user/Desktop"]:
            try:
                for name in self.wm.vfs.listdir(folder):
                    if name.endswith((".txt", ".md")):
                        path = folder + "/" + name
                        try:
                            content = self.wm.vfs.read(path)
                            st      = self.wm.vfs.stat(path)
                            self._notes.append({
                                "title":    name,
                                "path":     path,
                                "content":  content,
                                "modified": st["modified"],
                                "pinned":   False,
                                "tags":     [],
                            })
                        except Exception:
                            pass
            except Exception:
                pass
        self._sort_and_render()

    def _sort_and_render(self) -> None:
        key = self._sort_notes_key.get()
        if key == "name":
            self._notes.sort(key=lambda n: (not n["pinned"], n["title"].lower()))
        elif key == "date":
            self._notes.sort(key=lambda n: (not n["pinned"], -n["modified"]))
        elif key == "size":
            self._notes.sort(key=lambda n: (not n["pinned"], -len(n["content"])))
        self._render_note_list(self._notes)

    def _filter_notes(self) -> None:
        q = self._note_search.get().strip().lower()
        if not q or q.startswith("🔍"):
            filtered = self._notes
        else:
            filtered = [
                n for n in self._notes
                if q in n["title"].lower() or q in n["content"].lower()
                or any(q in t.lower() for t in n.get("tags", []))
            ]
        self._render_note_list(filtered)

    def _render_note_list(self, notes: List[Dict]) -> None:
        for w in self._notes_inner.winfo_children():
            w.destroy()
        self._count_lbl.config(text=str(len(notes)))

        for i, note in enumerate(notes):
            bg  = T["panel_bg"]
            row = tk.Frame(self._notes_inner, bg=bg, cursor="hand2",
                            padx=8, pady=6)
            row.pack(fill="x", pady=1)

            hdr_f = tk.Frame(row, bg=bg)
            hdr_f.pack(fill="x")

            pin_icon = "📌 " if note.get("pinned") else ""
            tk.Label(hdr_f, text=pin_icon + note["title"],
                     bg=bg, fg=T["text"],
                     font=(FONT_UI, 9, "bold"),
                     anchor="w").pack(side="left", fill="x", expand=True)

            dt = datetime.datetime.fromtimestamp(note["modified"]).strftime("%m/%d %H:%M")
            tk.Label(hdr_f, text=dt, bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 7)).pack(side="right")

            preview = note["content"].replace("\n", " ")[:60]
            tk.Label(row, text=preview, bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 8), anchor="w",
                     wraplength=180).pack(anchor="w")

            if note.get("tags"):
                tags_f = tk.Frame(row, bg=bg)
                tags_f.pack(anchor="w")
                for tag in note["tags"][:4]:
                    mktag(tags_f, tag).pack(side="left", padx=2, pady=1)

            idx = self._notes.index(note) if note in self._notes else -1
            for w in (row, hdr_f, *row.winfo_children()):
                w.bind("<Button-1>",  lambda e, i=idx: self._open_note(i))
                w.bind("<Enter>",     lambda e, r=row: r.config(bg=T["menu_hover"]))
                w.bind("<Leave>",     lambda e, r=row: r.config(bg=T["panel_bg"]))

    def _open_note(self, idx: int) -> None:
        if idx < 0 or idx >= len(self._notes):
            return
        self._cur_idx = idx
        note = self._notes[idx]
        self._title_var.set(note["title"])
        self.body.delete("1.0", "end")
        self.body.insert("1.0", note["content"])
        self._tags_var.set(", ".join(note.get("tags", [])))
        self._note_time_lbl.config(
            text=f"Modified: {fmt_time(note['modified'])}"
        )
        wc = len(note["content"].split())
        self._note_status.config(text=f"{wc} words  •  {len(note['content'])} chars")

    def _on_body_key(self, _: tk.Event) -> None:
        content = self.body.get("1.0", "end-1c")
        wc = len(content.split())
        self._note_status.config(text=f"{wc} words  •  {len(content)} chars")
        self._save_current()

    # ── note operations ───────────────────────────────────────────────────────

    def _new_note(self) -> None:
        tmpl_key = self._template_var.get()
        template = self.TEMPLATES.get(tmpl_key, "")
        now_str  = datetime.date.today().strftime("%Y-%m-%d")
        content  = template.replace("{date}", now_str)

        name  = simpledialog.askstring(
            "New Note", "Note name (with .txt):",
            initialvalue=f"note_{now_str}.txt",
            parent=self.wm.root,
        )
        if not name:
            return
        path = "/home/user/Documents/" + name
        self.wm.vfs.write(path, content)
        self._notes.append({
            "title":    name,
            "path":     path,
            "content":  content,
            "modified": time.time(),
            "pinned":   False,
            "tags":     [],
        })
        self._sort_and_render()
        self._open_note(len(self._notes) - 1)

    def _save_current(self) -> None:
        if self._cur_idx is None:
            return
        note    = self._notes[self._cur_idx]
        content = self.body.get("1.0", "end-1c")
        tags_raw = self._tags_var.get()
        note["content"]  = content
        note["modified"] = time.time()
        note["tags"]     = [t.strip() for t in tags_raw.split(",") if t.strip()]
        try:
            self.wm.vfs.write(note["path"], content)
        except Exception:
            pass

    def _delete_note(self) -> None:
        if self._cur_idx is None:
            return
        note = self._notes[self._cur_idx]
        if messagebox.askyesno("Delete", f"Delete '{note['title']}'?",
                                parent=self.wm.root):
            try:
                self.wm.vfs.remove(note["path"])
            except Exception:
                pass
            self._notes.pop(self._cur_idx)
            self._cur_idx = None
            self.body.delete("1.0", "end")
            self._title_var.set("")
            self._sort_and_render()

    def _pin_note(self) -> None:
        if self._cur_idx is not None:
            note = self._notes[self._cur_idx]
            note["pinned"] = not note.get("pinned", False)
            self._sort_and_render()

    def _export_note(self) -> None:
        if self._cur_idx is None:
            return
        note = self._notes[self._cur_idx]
        path = simpledialog.askstring(
            "Export", "Export to:",
            initialvalue=f"/home/user/Downloads/{note['title']}",
            parent=self.wm.root,
        )
        if path:
            self.wm.vfs.write(path, note["content"])
            self.wm.notifs.send("Notes", f"Exported: {path}", icon="📤")

    # ── formatting ────────────────────────────────────────────────────────────

    def _fmt_bold(self) -> None:
        try:
            self.body.text.tag_add("bold", "sel.first", "sel.last")
        except tk.TclError:
            pass

    def _fmt_italic(self) -> None:
        try:
            self.body.text.tag_add("italic", "sel.first", "sel.last")
        except tk.TclError:
            pass

    def _fmt_under(self) -> None:
        try:
            self.body.text.tag_add("underline", "sel.first", "sel.last")
        except tk.TclError:
            pass

    def _insert_sep(self) -> None:
        self.body.text.insert("insert", "\n" + "─" * 40 + "\n")

    def _insert_date(self) -> None:
        self.body.text.insert("insert", datetime.date.today().strftime("%Y-%m-%d"))

    def _insert_time(self) -> None:
        self.body.text.insert("insert", datetime.datetime.now().strftime("%H:%M:%S"))


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 25 — EMAIL CLIENT APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class EmailApp(BaseWin):
    """
    Simulated email client with:
      • Inbox, Sent, Drafts, Starred, Trash folders
      • Compose window (To, CC, Subject, Body, attachments)
      • Reply / Reply All / Forward
      • Star / Archive / Delete
      • Search across all mail
      • HTML-lite message rendering
      • Contact list sidebar
      • Unread count badges
    """

    SAMPLE_INBOX: List[Dict[str, Any]] = [
        {
            "id": "m001", "folder": "inbox",
            "from": "admin@pyos.local", "to": "user@pyos.local",
            "subject": "Welcome to PyOS!",
            "date": "2025-01-01 09:00",
            "body": "Welcome to PyOS v5.0!\n\nWe're thrilled to have you on board.\n\n"
                    "PyOS is a complete desktop OS simulation built entirely in Python.\n\n"
                    "Get started by exploring the desktop icons or opening the terminal.\n\n"
                    "Best regards,\nThe PyOS Team",
            "read": True, "starred": True, "attachments": [],
        },
        {
            "id": "m002", "folder": "inbox",
            "from": "system@pyos.local", "to": "user@pyos.local",
            "subject": "System Update Available — PyOS v5.1",
            "date": "2025-01-03 10:30",
            "body": "A new system update is available!\n\n"
                    "PyOS v5.1 includes:\n"
                    "- Performance improvements\n"
                    "- New Calendar app\n"
                    "- Bug fixes in the terminal\n"
                    "- Better syntax highlighting\n\n"
                    "To update: open the App Store and click 'Check for Updates'.\n\n"
                    "Regards,\nSystem Updater",
            "read": False, "starred": False, "attachments": ["changelog.txt"],
        },
        {
            "id": "m003", "folder": "inbox",
            "from": "boss@company.com", "to": "user@pyos.local",
            "subject": "Q1 Review Meeting — Tomorrow 3pm",
            "date": "2025-01-04 08:15",
            "body": "Hi,\n\nJust a reminder about our Q1 review meeting tomorrow at 3pm.\n\n"
                    "Agenda:\n1. Revenue performance\n2. Project status updates\n"
                    "3. Headcount planning\n4. Q2 roadmap\n\n"
                    "Please bring your progress reports.\n\nThanks,\nManager",
            "read": False, "starred": True, "attachments": [],
        },
        {
            "id": "m004", "folder": "inbox",
            "from": "newsletter@devnews.io", "to": "user@pyos.local",
            "subject": "Python Weekly: Top 10 Libraries in 2025",
            "date": "2025-01-05 12:00",
            "body": "Python Weekly Newsletter\n========================\n\n"
                    "This week's highlights:\n\n"
                    "1. FastAPI surpasses Flask in downloads\n"
                    "2. Python 3.14 beta features\n"
                    "3. NumPy 2.0 migration guide\n"
                    "4. Tkinter gets a facelift in Python 3.13\n"
                    "5. New async frameworks comparison\n\n"
                    "Read more at devnews.io/python-weekly",
            "read": True, "starred": False, "attachments": [],
        },
        {
            "id": "m005", "folder": "inbox",
            "from": "github@noreply.github.com", "to": "user@pyos.local",
            "subject": "[pyos/pyos] New issue: Terminal crashes on pipe",
            "date": "2025-01-06 15:44",
            "body": "A new issue was opened on pyos/pyos:\n\n"
                    "Title: Terminal crashes when using complex pipes\n"
                    "Author: contributor42\n\n"
                    "Description:\nWhen running 'cat file.txt | grep pattern | sort', "
                    "the terminal sometimes freezes.\n\n"
                    "Steps to reproduce:\n1. Open terminal\n2. Run the above command\n\n"
                    "View issue: https://github.com/pyos/pyos/issues/42",
            "read": False, "starred": False, "attachments": [],
        },
        {
            "id": "m006", "folder": "sent",
            "from": "user@pyos.local", "to": "boss@company.com",
            "subject": "Re: Q1 Review Meeting — Tomorrow 3pm",
            "date": "2025-01-04 09:02",
            "body": "Hi,\n\nThanks for the reminder. I'll be there.\n\n"
                    "I'll prepare the project status update slides.\n\nBest,\nUser",
            "read": True, "starred": False, "attachments": [],
        },
        {
            "id": "m007", "folder": "drafts",
            "from": "user@pyos.local", "to": "team@company.com",
            "subject": "Weekly Status Update",
            "date": "2025-01-06 17:00",
            "body": "Hi team,\n\nWeekly update:\n\n[DRAFT — not sent]\n",
            "read": True, "starred": False, "attachments": [],
        },
    ]

    CONTACTS = [
        {"name": "System Admin",   "email": "admin@pyos.local",          "avatar": "SA"},
        {"name": "PyOS System",    "email": "system@pyos.local",         "avatar": "PS"},
        {"name": "Manager",        "email": "boss@company.com",          "avatar": "MG"},
        {"name": "Dev Newsletter", "email": "newsletter@devnews.io",     "avatar": "DN"},
        {"name": "GitHub",         "email": "github@noreply.github.com", "avatar": "GH"},
        {"name": "Team",           "email": "team@company.com",          "avatar": "TM"},
    ]

    FOLDERS = [
        ("📥  Inbox",   "inbox"),
        ("📤  Sent",    "sent"),
        ("📝  Drafts",  "drafts"),
        ("⭐  Starred", "starred"),
        ("🗑️  Trash",  "trash"),
    ]

    def __init__(self, wm: WM) -> None:
        self._messages: List[Dict[str, Any]] = list(self.SAMPLE_INBOX)
        self._cur_folder  = "inbox"
        self._cur_msg_id: Optional[str] = None
        self._selected_msgs: set = set()
        super().__init__(wm, "Email", 100, 70, 980, 640, "📧",
                         min_w=600, min_h=400)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])

        # Main horizontal pane: sidebar | message list | message view
        pane = tk.PanedWindow(parent, orient="horizontal",
                               bg=T["panel_bg"], sashwidth=4, sashrelief="flat")
        pane.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(pane, bg=T["panel_bg"], width=180)
        pane.add(sidebar, minsize=150)
        self._build_sidebar(sidebar)

        # Message list
        msg_list = tk.Frame(pane, bg=T["win_bg"], width=280)
        pane.add(msg_list, minsize=220)
        self._build_msg_list_area(msg_list)

        # Message view
        msg_view = tk.Frame(pane, bg=T["win_bg"])
        pane.add(msg_view, minsize=300)
        self._build_msg_view(msg_view)

        self._render_msg_list()

    # ── sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, parent: tk.Frame) -> None:
        # Compose button
        mkbtn(parent, "✏️  Compose", self._compose,
              kind="accent").pack(fill="x", padx=8, pady=(10, 6))

        mksep(parent).pack(fill="x", padx=8)

        # Folder list
        self._folder_btns: Dict[str, tk.Button] = {}
        for label, key in self.FOLDERS:
            b = tk.Button(parent, text=label,
                          command=lambda k=key: self._switch_folder(k),
                          bg=T["accent"] if key == self._cur_folder else T["panel_bg"],
                          fg=T["text"], relief="flat", bd=0,
                          font=(FONT_UI, 9), anchor="w", padx=12, pady=5,
                          cursor="hand2", activebackground=T["menu_hover"])
            b.pack(fill="x")
            self._folder_btns[key] = b

        mksep(parent).pack(fill="x", padx=8, pady=6)

        # Contacts
        tk.Label(parent, text="CONTACTS", bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8, "bold"), padx=8).pack(anchor="w")
        for contact in self.CONTACTS:
            cf = tk.Frame(parent, bg=T["panel_bg"], cursor="hand2")
            cf.pack(fill="x", padx=4, pady=1)
            av = tk.Label(cf, text=contact["avatar"][0],
                          bg=T["accent"], fg="#fff",
                          font=(FONT_UI, 8, "bold"), width=2)
            av.pack(side="left", padx=4, pady=2)
            tk.Label(cf, text=contact["name"][:16],
                     bg=T["panel_bg"], fg=T["text"],
                     font=(FONT_UI, 8)).pack(side="left")
            cf.bind("<Button-1>",
                    lambda e, addr=contact["email"]: self._compose(to=addr))
            av.bind("<Button-1>",
                    lambda e, addr=contact["email"]: self._compose(to=addr))

        # Search
        mksep(parent).pack(fill="x", padx=8, pady=6)
        tk.Label(parent, text="SEARCH", bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8, "bold"), padx=8).pack(anchor="w")
        self._search_var = tk.StringVar()
        se = mkentry(parent, textvariable=self._search_var, width=18)
        se.pack(fill="x", padx=8, pady=4)
        self._search_var.trace("w", lambda *_: self._render_msg_list())

    def _switch_folder(self, folder: str) -> None:
        self._cur_folder = folder
        for k, b in self._folder_btns.items():
            b.config(bg=T["accent"] if k == folder else T["panel_bg"])
        self._render_msg_list()

    # ── message list area ─────────────────────────────────────────────────────

    def _build_msg_list_area(self, parent: tk.Frame) -> None:
        # Toolbar
        tb = tk.Frame(parent, bg=T["panel_alt"], height=32)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        for lbl, cmd in [("⟳", self._refresh_mail),("🗑️", self._delete_selected),
                          ("☆", self._star_selected)]:
            tk.Button(tb, text=lbl, command=cmd,
                      bg=T["panel_alt"], fg=T["text"], relief="flat", bd=0,
                      font=(FONT_EMOJI, 11), padx=6, cursor="hand2",
                      activebackground=T["button_hover"]).pack(side="left", padx=2, pady=3)

        # Count
        self._mail_count_lbl = tk.Label(tb, text="",
                                         bg=T["panel_alt"], fg=T["text_muted"],
                                         font=(FONT_UI, 8))
        self._mail_count_lbl.pack(side="right", padx=8)

        # Scrollable message list
        sf = ScrollableFrame(parent, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        self._msg_list_inner = sf.inner

    def _render_msg_list(self) -> None:
        for w in self._msg_list_inner.winfo_children():
            w.destroy()

        q = self._search_var.get().strip().lower() if hasattr(self, "_search_var") else ""

        if self._cur_folder == "starred":
            msgs = [m for m in self._messages if m.get("starred")]
        else:
            msgs = [m for m in self._messages if m.get("folder") == self._cur_folder]

        if q:
            msgs = [m for m in msgs
                    if q in m["subject"].lower()
                    or q in m["from"].lower()
                    or q in m["body"].lower()]

        unread = sum(1 for m in msgs if not m.get("read", True))
        self._mail_count_lbl.config(
            text=f"{len(msgs)} msgs" + (f"  •  {unread} unread" if unread else "")
        )

        for i, msg in enumerate(sorted(msgs, key=lambda m: m["date"], reverse=True)):
            is_sel   = msg["id"] == self._cur_msg_id
            is_unread= not msg.get("read", True)
            bg       = T["selection"] if is_sel else (
                       T["panel_bg"] if i % 2 == 0 else T["win_bg"])

            row = tk.Frame(self._msg_list_inner, bg=bg, cursor="hand2",
                            padx=8, pady=6)
            row.pack(fill="x")

            # From + star + date
            top = tk.Frame(row, bg=bg)
            top.pack(fill="x")

            from_short = msg["from"].split("@")[0][:18]
            weight     = "bold" if is_unread else "normal"
            tk.Label(top, text=from_short, bg=bg, fg=T["text"],
                     font=(FONT_UI, 9, weight)).pack(side="left")

            star = "⭐" if msg.get("starred") else "☆"
            tk.Label(top, text=star, bg=bg, fg=T["warning"],
                     font=(FONT_EMOJI, 9)).pack(side="right")
            tk.Label(top, text=msg["date"][-5:], bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 7)).pack(side="right", padx=4)

            # Subject
            subj = ("📎 " if msg.get("attachments") else "") + msg["subject"][:38]
            tk.Label(row, text=subj, bg=bg, fg=T["text"],
                     font=(FONT_UI, 8, weight), anchor="w").pack(anchor="w")

            # Preview
            preview = msg["body"].replace("\n", " ")[:55]
            tk.Label(row, text=preview, bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 7), anchor="w").pack(anchor="w")

            # Bindings
            for child in row.winfo_children() + [row]:
                child.bind("<Button-1>",   lambda e, m=msg: self._open_msg(m))
                child.bind("<Enter>",      lambda e, r=row: r.config(bg=T["menu_hover"]))
                child.bind("<Leave>",      lambda e, r=row, obg=bg: r.config(bg=obg))
                child.bind("<Button-3>",   lambda e, m=msg: self._msg_ctx(e, m))

    def _open_msg(self, msg: Dict[str, Any]) -> None:
        msg["read"]       = True
        self._cur_msg_id  = msg["id"]
        self._render_msg_view(msg)
        self._render_msg_list()

    def _msg_ctx(self, e: tk.Event, msg: Dict[str, Any]) -> None:
        m = tk.Menu(self.wm.root, tearoff=0, bg=T["menu_bg"], fg=T["text"],
                    activebackground=T["accent"], activeforeground=T["text_inverse"])
        m.add_command(label="📖  Open",    command=lambda: self._open_msg(msg))
        m.add_command(label="↩  Reply",   command=lambda: self._reply(msg))
        m.add_command(label="↪  Forward", command=lambda: self._forward(msg))
        m.add_separator()
        m.add_command(label="⭐  Star",   command=lambda: self._toggle_star(msg))
        m.add_command(label="🗑️  Delete", command=lambda: self._delete_msg(msg))
        m.post(e.x_root, e.y_root)

    # ── message view ──────────────────────────────────────────────────────────

    def _build_msg_view(self, parent: tk.Frame) -> None:
        # Toolbar
        tb = tk.Frame(parent, bg=T["panel_alt"], height=36)
        tb.pack(fill="x")
        tb.pack_propagate(False)
        self._view_tb = tb
        for lbl, cmd in [("↩ Reply", self._reply_cur), ("↪ Forward", self._forward_cur),
                          ("⭐ Star", self._star_cur),   ("🗑️ Delete", self._delete_cur),
                          ("📤 Move…", self._move_cur)]:
            tk.Button(tb, text=lbl, command=cmd,
                      bg=T["panel_alt"], fg=T["text"], relief="flat", bd=0,
                      font=(FONT_UI, 9), padx=8, pady=4, cursor="hand2",
                      activebackground=T["button_hover"]).pack(side="left", padx=1)

        # Header area
        self._msg_hdr = tk.Frame(parent, bg=T["panel_bg"], padx=12, pady=10)
        self._msg_hdr.pack(fill="x")
        self._msg_hdr_lbl = tk.Label(self._msg_hdr, text="Select a message",
                                      bg=T["panel_bg"], fg=T["text_muted"],
                                      font=(FONT_UI, 11))
        self._msg_hdr_lbl.pack()

        mksep(parent).pack(fill="x")

        # Body
        self._msg_body = ScrollText(parent, font=(FONT_UI, 11), wrap="word")
        self._msg_body.pack(fill="both", expand=True)
        self._msg_body.text.config(state="disabled")

        # Attachment bar
        self._attach_bar = tk.Frame(parent, bg=T["panel_alt"])

    def _render_msg_view(self, msg: Dict[str, Any]) -> None:
        # Clear header
        for w in self._msg_hdr.winfo_children():
            w.destroy()

        # Subject
        tk.Label(self._msg_hdr, text=msg["subject"],
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold"), anchor="w",
                 wraplength=440).pack(anchor="w")

        # Meta
        meta_f = tk.Frame(self._msg_hdr, bg=T["panel_bg"])
        meta_f.pack(fill="x", pady=(4, 0))
        for lbl, val in [("From:", msg["from"]), ("To:", msg["to"]),
                          ("Date:", msg["date"])]:
            row = tk.Frame(meta_f, bg=T["panel_bg"])
            row.pack(anchor="w")
            tk.Label(row, text=lbl, bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 8), width=5, anchor="e").pack(side="left")
            tk.Label(row, text=val, bg=T["panel_bg"], fg=T["text"],
                     font=(FONT_UI, 9)).pack(side="left", padx=4)

        # Attachments
        self._attach_bar.pack_forget()
        if msg.get("attachments"):
            self._attach_bar.pack(fill="x")
            for w in self._attach_bar.winfo_children():
                w.destroy()
            tk.Label(self._attach_bar, text="📎 Attachments: ",
                     bg=T["panel_alt"], fg=T["text_muted"],
                     font=(FONT_UI, 8)).pack(side="left", padx=8, pady=4)
            for att in msg["attachments"]:
                tk.Button(self._attach_bar, text=att,
                           bg=T["button_bg"], fg=T["text"], relief="flat", bd=0,
                           font=(FONT_UI, 8), padx=6, cursor="hand2",
                           activebackground=T["button_hover"]).pack(side="left", padx=2)

        # Body
        self._msg_body.text.config(state="normal")
        self._msg_body.delete("1.0", "end")
        self._msg_body.insert("1.0", msg["body"])
        self._msg_body.text.config(state="disabled")
        self._msg_body.see("1.0")

    # ── actions ───────────────────────────────────────────────────────────────

    def _get_cur_msg(self) -> Optional[Dict]:
        return next((m for m in self._messages if m["id"] == self._cur_msg_id), None)

    def _reply_cur(self)   -> None: self._reply(self._get_cur_msg())
    def _forward_cur(self) -> None: self._forward(self._get_cur_msg())
    def _star_cur(self)    -> None: self._toggle_star(self._get_cur_msg())
    def _delete_cur(self)  -> None: self._delete_msg(self._get_cur_msg())
    def _move_cur(self)    -> None:
        msg = self._get_cur_msg()
        if msg:
            folder = simpledialog.askstring(
                "Move to folder", "Folder (inbox/sent/drafts/starred/trash):",
                parent=self.wm.root,
            )
            if folder in ("inbox","sent","drafts","starred","trash"):
                msg["folder"] = folder
                self._render_msg_list()

    def _toggle_star(self, msg: Optional[Dict]) -> None:
        if msg:
            msg["starred"] = not msg.get("starred", False)
            self._render_msg_list()

    def _delete_msg(self, msg: Optional[Dict]) -> None:
        if msg:
            if msg["folder"] == "trash":
                self._messages.remove(msg)
            else:
                msg["folder"] = "trash"
            self._cur_msg_id = None
            self._render_msg_list()

    def _delete_selected(self) -> None:
        for msg in self._messages:
            if msg["id"] in self._selected_msgs:
                msg["folder"] = "trash"
        self._selected_msgs.clear()
        self._render_msg_list()

    def _star_selected(self) -> None:
        for msg in self._messages:
            if msg["id"] in self._selected_msgs:
                msg["starred"] = True
        self._render_msg_list()

    def _refresh_mail(self) -> None:
        self.wm.notifs.send("Email", "Mail refreshed — no new messages.", icon="📧")
        self._render_msg_list()

    def _reply(self, msg: Optional[Dict]) -> None:
        if msg:
            self._compose(to=msg["from"],
                          subject="Re: " + msg["subject"],
                          body="\n\n--- Original Message ---\n" + msg["body"])

    def _forward(self, msg: Optional[Dict]) -> None:
        if msg:
            self._compose(subject="Fwd: " + msg["subject"],
                          body="\n\n--- Forwarded Message ---\n"
                               f"From: {msg['from']}\nDate: {msg['date']}\n\n"
                               + msg["body"])

    def _compose(self, to: str = "", subject: str = "", body: str = "") -> None:
        """Open compose window."""
        d = tk.Toplevel(self.wm.root)
        d.title("Compose Email")
        d.config(bg=T["win_bg"])
        d.geometry("620x480")
        d.wm_attributes("-topmost", True)

        # Header fields
        fields_f = tk.Frame(d, bg=T["panel_bg"])
        fields_f.pack(fill="x")
        entries: Dict[str, tk.Entry] = {}
        for lbl, default in [("To:", to), ("CC:", ""), ("Subject:", subject)]:
            row = tk.Frame(fields_f, bg=T["panel_bg"])
            row.pack(fill="x", padx=8, pady=3)
            tk.Label(row, text=lbl, bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 9), width=8, anchor="e").pack(side="left")
            e = mkentry(row, width=52)
            e.pack(side="left", padx=4, fill="x", expand=True)
            e.insert(0, default)
            entries[lbl] = e

        mksep(d).pack(fill="x")

        # Body
        body_area = ScrollText(d, font=(FONT_UI, 11), wrap="word")
        body_area.pack(fill="both", expand=True, padx=8, pady=4)
        body_area.insert("1.0", body)

        # Footer
        btn_f = tk.Frame(d, bg=T["panel_bg"])
        btn_f.pack(fill="x", padx=8, pady=8)

        def send_msg() -> None:
            to_addr  = entries["To:"].get().strip()
            subj     = entries["Subject:"].get().strip()
            cc       = entries["CC:"].get().strip()
            msg_body = body_area.get("1.0", "end-1c")
            if not to_addr:
                messagebox.showwarning("Missing", "Please enter a recipient.", parent=d)
                return
            new_msg = {
                "id":          f"m{len(self._messages)+1:03d}",
                "folder":      "sent",
                "from":        f"{self.wm.users.current or 'user'}@pyos.local",
                "to":          to_addr,
                "cc":          cc,
                "subject":     subj or "(No Subject)",
                "date":        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "body":        msg_body,
                "read":        True,
                "starred":     False,
                "attachments": [],
            }
            self._messages.append(new_msg)
            d.destroy()
            self._render_msg_list()
            self.wm.notifs.send("Email", f"Message sent to {to_addr}", icon="📤")

        def save_draft() -> None:
            to_addr  = entries["To:"].get().strip()
            subj     = entries["Subject:"].get().strip()
            msg_body = body_area.get("1.0", "end-1c")
            draft = {
                "id":      f"d{len(self._messages)+1:03d}",
                "folder":  "drafts",
                "from":    f"{self.wm.users.current or 'user'}@pyos.local",
                "to":      to_addr, "subject": subj, "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "body":    msg_body, "read": True, "starred": False, "attachments": [],
            }
            self._messages.append(draft)
            d.destroy()
            self.wm.notifs.send("Email", "Draft saved.", icon="📝")

        mkbtn(btn_f, "📤  Send",    send_msg, kind="accent").pack(side="left", padx=6)
        mkbtn(btn_f, "💾  Draft",   save_draft).pack(side="left", padx=4)
        mkbtn(btn_f, "❌  Discard", d.destroy, kind="danger").pack(side="right", padx=6)
        entries["To:"].focus_set()


# =============================================================================
#  END OF PART 4
#  Defines: CalculatorApp (4 modes + unit converter),
#           ClockApp (5 tabs: clock/calendar/alarm/stopwatch/world),
#           TaskManagerApp (5 tabs: procs/perf/users/disk/network),
#           NotesApp (rich notes, templates, tags, pin),
#           EmailApp (compose/reply/forward/folders/contacts)
#
#  Part 5 covers: PasswordManagerApp, SpreadsheetApp, ImageViewerApp,
#                 DiskAnalyzerApp, CodeRunnerApp, ArchiveManagerApp
#  Part 6 covers: AppStoreApp, SystemMonitorApp, SettingsApp,
#                 Login/Lock screens, Boot animation, main()
# =============================================================================

if __name__ == "__main__":
    print(f"PyOS v{PYOS_VERSION} — Part 4 loaded.")
    print("CalculatorApp, ClockApp, TaskManagerApp, NotesApp, EmailApp defined.")
#!/usr/bin/env python3
# =============================================================================
#  PyOS v5.0 — PART 5
#  Sections: Password Manager, Spreadsheet, Image Viewer,
#            Disk Analyzer, Code Runner, Archive Manager
#  Requires: Parts 1–4 concatenated before this
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 26 — PASSWORD MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class PasswordManagerApp(BaseWin):
    """
    Secure password manager with:
      • Master password protected vault (SHA-256 hashed)
      • Add / edit / delete entries (site, username, password, URL, notes)
      • Password strength analyser with colour meter
      • Random password generator (length, symbols, digits, mixed case)
      • Show / hide password toggle
      • Copy to clipboard
      • Search / filter entries
      • Categories: Web, Email, Social, Banking, Work, Other
      • Import / export (simulated CSV)
      • Password age tracking
      • Breach check indicator (simulated)
    """

    CATEGORIES = ["All", "Web", "Email", "Social", "Banking", "Work", "Other"]

    SAMPLE_ENTRIES = [
        {"id":"pw001","site":"GitHub","username":"user@pyos.local","password":"Gh!t#2025xZ",
         "url":"https://github.com","category":"Web","notes":"Main dev account",
         "created":time.time()-86400*30,"modified":time.time()-86400*5},
        {"id":"pw002","site":"Gmail","username":"user@gmail.com","password":"Gm@ilP@ss99!",
         "url":"https://mail.google.com","category":"Email","notes":"Primary email",
         "created":time.time()-86400*60,"modified":time.time()-86400*10},
        {"id":"pw003","site":"LinkedIn","username":"user@pyos.local","password":"L!nk3d1n#Pro",
         "url":"https://linkedin.com","category":"Social","notes":"Professional profile",
         "created":time.time()-86400*90,"modified":time.time()-86400*20},
        {"id":"pw004","site":"Bank of Python","username":"user123","password":"B@nk$3cur3!99",
         "url":"https://bank.example.com","category":"Banking","notes":"Savings account",
         "created":time.time()-86400*120,"modified":time.time()-86400*2},
        {"id":"pw005","site":"Jira","username":"user@company.com","password":"J!r@W0rk2025",
         "url":"https://jira.company.com","category":"Work","notes":"Project tracker",
         "created":time.time()-86400*15,"modified":time.time()-86400*1},
    ]

    def __init__(self, wm: WM) -> None:
        self._entries: List[Dict[str, Any]] = list(self.SAMPLE_ENTRIES)
        self._unlocked   = False
        self._master_hash = hashlib.sha256(b"master").hexdigest()
        self._cur_id: Optional[str] = None
        self._show_pw    = False
        self._cat_filter = "All"
        super().__init__(wm, "Password Manager", 200, 80, 900, 600, "🔐",
                         min_w=600, min_h=400)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])
        self._show_lock_screen(parent)

    def _show_lock_screen(self, parent: tk.Frame) -> None:
        """Master password gate."""
        lf = tk.Frame(parent, bg=T["win_bg"])
        lf.pack(expand=True)

        tk.Label(lf, text="🔐", bg=T["win_bg"], fg=T["accent"],
                 font=(FONT_EMOJI, 48)).pack(pady=(30, 8))
        tk.Label(lf, text="Password Vault",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold")).pack()
        tk.Label(lf, text="Enter your master password to unlock",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 10)).pack(pady=(4, 20))

        pw_var = tk.StringVar()
        pw_entry = mkentry(lf, textvariable=pw_var, width=28, password=True)
        pw_entry.pack(pady=4)

        err_lbl = tk.Label(lf, text="",
                            bg=T["win_bg"], fg=T["danger"],
                            font=(FONT_UI, 9))
        err_lbl.pack(pady=2)

        def unlock(e=None) -> None:
            entered = hashlib.sha256(pw_var.get().encode()).hexdigest()
            if entered == self._master_hash or pw_var.get() == "master":
                self._unlocked = True
                for w in parent.winfo_children():
                    w.destroy()
                self._build_vault(parent)
            else:
                err_lbl.config(text="❌  Incorrect master password")
                pw_var.set("")
                pw_entry.focus_set()

        mkbtn(lf, "🔓  Unlock", unlock, kind="accent").pack(pady=8)
        tk.Label(lf, text="Hint: the default password is  master",
                 bg=T["win_bg"], fg=T["text_dim"],
                 font=(FONT_UI, 8)).pack()

        pw_entry.bind("<Return>", unlock)
        pw_entry.focus_set()

    def _build_vault(self, parent: tk.Frame) -> None:
        """Main vault UI after unlock."""
        parent.config(bg=T["win_bg"])

        # Top toolbar
        tb = tk.Frame(parent, bg=T["panel_bg"], height=44)
        tb.pack(fill="x")
        tb.pack_propagate(False)

        mkbtn(tb, "➕  New Entry", self._new_entry, kind="accent").pack(
            side="left", padx=6, pady=6)
        mkbtn(tb, "🔑  Generate", self._open_generator).pack(
            side="left", padx=2, pady=6)
        mkbtn(tb, "📥  Import", self._import_csv).pack(
            side="left", padx=2, pady=6)
        mkbtn(tb, "📤  Export", self._export_csv).pack(
            side="left", padx=2, pady=6)

        # Search
        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda *_: self._refresh())
        se = mkentry(tb, textvariable=self._search_var, width=22)
        se.pack(side="right", padx=8, pady=8)
        tk.Label(tb, text="🔍", bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 11)).pack(side="right")

        # Main pane
        pane = tk.PanedWindow(parent, orient="horizontal",
                               bg=T["panel_bg"], sashwidth=4)
        pane.pack(fill="both", expand=True)

        # Left: category + list
        left = tk.Frame(pane, bg=T["panel_bg"], width=250)
        pane.add(left, minsize=200)
        self._build_left(left)

        # Right: entry detail
        right = tk.Frame(pane, bg=T["win_bg"])
        pane.add(right, minsize=300)
        self._build_right(right)

        # Status bar
        sf = tk.Frame(parent, bg=T["status_bg"], height=22)
        sf.pack(fill="x", side="bottom")
        sf.pack_propagate(False)
        self._status_lbl = tk.Label(sf, text=f"{len(self._entries)} entries",
                                     bg=T["status_bg"], fg=T["text_muted"],
                                     font=(FONT_UI, 8), anchor="w", padx=8)
        self._status_lbl.pack(side="left", fill="y")
        tk.Label(sf, text="🔒 Vault locked on close",
                 bg=T["status_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8), padx=8).pack(side="right")

        self._refresh()

    def _build_left(self, parent: tk.Frame) -> None:
        # Category filter
        tk.Label(parent, text="CATEGORIES", bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8, "bold"), padx=8).pack(anchor="w", pady=(8, 2))

        cat_icons = {"All":"🗂️","Web":"🌐","Email":"📧","Social":"👥",
                      "Banking":"🏦","Work":"💼","Other":"📦"}
        self._cat_btns: Dict[str, tk.Button] = {}
        for cat in self.CATEGORIES:
            b = tk.Button(parent, text=f"{cat_icons.get(cat,'•')}  {cat}",
                          command=partial(self._set_cat, cat),
                          bg=T["accent"] if cat == self._cat_filter else T["panel_bg"],
                          fg=T["text"], relief="flat", bd=0,
                          font=(FONT_UI, 9), anchor="w", padx=12, pady=4,
                          cursor="hand2", activebackground=T["menu_hover"])
            b.pack(fill="x")
            self._cat_btns[cat] = b

        mksep(parent).pack(fill="x", padx=8, pady=6)
        tk.Label(parent, text="ENTRIES", bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8, "bold"), padx=8).pack(anchor="w", pady=(0, 2))

        sf = ScrollableFrame(parent, bg=T["panel_bg"])
        sf.pack(fill="both", expand=True)
        self._entries_inner = sf.inner

    def _build_right(self, parent: tk.Frame) -> None:
        self._detail_frame = parent
        self._show_placeholder()

    def _show_placeholder(self) -> None:
        for w in self._detail_frame.winfo_children():
            w.destroy()
        tk.Label(self._detail_frame,
                 text="🔐\n\nSelect an entry\nor create a new one",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 12), justify="center").pack(expand=True)

    def _set_cat(self, cat: str) -> None:
        self._cat_filter = cat
        for k, b in self._cat_btns.items():
            b.config(bg=T["accent"] if k == cat else T["panel_bg"])
        self._refresh()

    def _refresh(self) -> None:
        for w in self._entries_inner.winfo_children():
            w.destroy()
        q   = self._search_var.get().strip().lower() if hasattr(self, "_search_var") else ""
        entries = self._entries
        if self._cat_filter != "All":
            entries = [e for e in entries if e.get("category") == self._cat_filter]
        if q:
            entries = [e for e in entries
                       if q in e["site"].lower() or q in e["username"].lower()
                       or q in e.get("url","").lower()]

        for i, entry in enumerate(entries):
            is_sel = entry["id"] == self._cur_id
            bg     = T["accent"] if is_sel else (T["panel_bg"] if i % 2 == 0 else T["win_bg"])
            row    = tk.Frame(self._entries_inner, bg=bg, cursor="hand2",
                               padx=8, pady=6)
            row.pack(fill="x")
            # Site + category icon
            cat_icons = {"Web":"🌐","Email":"📧","Social":"👥",
                          "Banking":"🏦","Work":"💼","Other":"📦"}
            ico = cat_icons.get(entry.get("category","Other"), "📦")
            hdr = tk.Frame(row, bg=bg)
            hdr.pack(fill="x")
            tk.Label(hdr, text=ico, bg=bg, fg=T["text"],
                     font=(FONT_EMOJI, 11)).pack(side="left")
            tk.Label(hdr, text=entry["site"], bg=bg, fg=T["text"],
                     font=(FONT_UI, 10, "bold")).pack(side="left", padx=4)
            # Age warning
            age_days = int((time.time() - entry["modified"]) / 86400)
            if age_days > 90:
                tk.Label(hdr, text="⚠️", bg=bg, fg=T["warning"],
                         font=(FONT_EMOJI, 9)).pack(side="right")
            tk.Label(row, text=entry["username"], bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 8)).pack(anchor="w", padx=16)

            for child in row.winfo_children() + [row]:
                child.bind("<Button-1>", lambda e, eid=entry["id"]: self._open_entry(eid))
                child.bind("<Enter>",    lambda e, r=row: r.config(bg=T["menu_hover"]))
                child.bind("<Leave>",    lambda e, r=row, obg=bg: r.config(bg=obg))
                child.bind("<Button-3>", lambda e, eid=entry["id"]: self._entry_ctx(e, eid))

        total = len(self._entries)
        shown = len(entries)
        self._status_lbl.config(text=f"{shown} of {total} entries")

    def _open_entry(self, eid: str) -> None:
        self._cur_id = eid
        entry = next((e for e in self._entries if e["id"] == eid), None)
        if not entry:
            return
        self._refresh()
        self._show_entry_detail(entry)

    def _show_entry_detail(self, entry: Dict[str, Any]) -> None:
        for w in self._detail_frame.winfo_children():
            w.destroy()
        f = self._detail_frame

        # Header
        hdr = tk.Frame(f, bg=T["panel_alt"], padx=14, pady=10)
        hdr.pack(fill="x")
        cat_icons = {"Web":"🌐","Email":"📧","Social":"👥","Banking":"🏦","Work":"💼","Other":"📦"}
        ico = cat_icons.get(entry.get("category","Other"), "📦")
        tk.Label(hdr, text=f"{ico}  {entry['site']}",
                 bg=T["panel_alt"], fg=T["text"],
                 font=(FONT_UI, 16, "bold")).pack(side="left")
        cat_lbl = mktag(hdr, entry.get("category","Other"))
        cat_lbl.pack(side="right", padx=4)

        # Action buttons
        act_f = tk.Frame(f, bg=T["win_bg"])
        act_f.pack(fill="x", padx=10, pady=6)
        mkbtn(act_f, "✏️  Edit",   partial(self._edit_entry, entry["id"])).pack(side="left", padx=4)
        mkbtn(act_f, "📋  Copy PW", partial(self._copy_password, entry["id"])).pack(side="left", padx=4)
        mkbtn(act_f, "🗑️  Delete", partial(self._delete_entry, entry["id"]), kind="danger").pack(side="right", padx=4)

        # Fields
        fields_f = tk.Frame(f, bg=T["win_bg"])
        fields_f.pack(fill="x", padx=10)

        def make_field(label: str, value: str, copyable: bool = False, password: bool = False) -> None:
            row = tk.Frame(fields_f, bg=T["panel_alt"], padx=10, pady=6)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=label, bg=T["panel_alt"], fg=T["text_muted"],
                     font=(FONT_UI, 8), width=10, anchor="w").pack(side="left")
            display = "•" * len(value) if password and not self._show_pw else value
            val_lbl = tk.Label(row, text=display, bg=T["panel_alt"], fg=T["text"],
                                font=(FONT_MONO, 10))
            val_lbl.pack(side="left", padx=4)
            if copyable:
                tk.Button(row, text="📋", command=partial(self._copy_val, value),
                           bg=T["panel_alt"], fg=T["text"], relief="flat", bd=0,
                           font=(FONT_EMOJI, 10), cursor="hand2",
                           activebackground=T["button_hover"]).pack(side="right")

        make_field("Site",     entry["site"])
        make_field("Username", entry["username"], copyable=True)
        make_field("Password", entry["password"], copyable=True, password=True)
        make_field("URL",      entry.get("url","—"))
        make_field("Category", entry.get("category","Other"))

        # Show/hide password toggle
        def toggle_pw() -> None:
            self._show_pw = not self._show_pw
            self._show_entry_detail(entry)
        tk.Button(fields_f, text="👁  Show Password" if not self._show_pw else "🙈  Hide Password",
                  command=toggle_pw, bg=T["win_bg"], fg=T["accent"],
                  relief="flat", bd=0, font=(FONT_UI, 9), cursor="hand2",
                  activebackground=T["win_bg"]).pack(anchor="w", padx=10, pady=4)

        # Password strength
        strength, color, tips = self._analyse_password(entry["password"])
        st_f = tk.Frame(f, bg=T["win_bg"])
        st_f.pack(fill="x", padx=10, pady=4)
        tk.Label(st_f, text="Strength:", bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 9)).pack(side="left")
        tk.Label(st_f, text=strength, bg=T["win_bg"], fg=color,
                 font=(FONT_UI, 9, "bold")).pack(side="left", padx=6)
        bar = ProgressBar(st_f, width=120, height=6, color=color)
        bar.pack(side="left")
        score = {"Weak":0.25,"Fair":0.5,"Good":0.75,"Strong":0.9,"Very Strong":1.0}.get(strength,0.5)
        bar.set(score)

        # Tips
        if tips:
            tk.Label(f, text="💡 " + "  •  ".join(tips),
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 8), wraplength=400, justify="left").pack(
                anchor="w", padx=10, pady=2)

        # Notes
        if entry.get("notes"):
            mksep(f).pack(fill="x", padx=10, pady=6)
            tk.Label(f, text="Notes", bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 8, "bold")).pack(anchor="w", padx=10)
            tk.Label(f, text=entry["notes"], bg=T["panel_alt"], fg=T["text"],
                     font=(FONT_UI, 9), wraplength=420, justify="left",
                     padx=10, pady=6).pack(fill="x", padx=10, pady=4)

        # Age info
        age_days = int((time.time() - entry["modified"]) / 86400)
        age_color = T["danger"] if age_days > 90 else (T["warning"] if age_days > 30 else T["success"])
        tk.Label(f, text=f"Last changed: {fmt_time(entry['modified'])}  ({age_days}d ago)",
                 bg=T["win_bg"], fg=age_color, font=(FONT_UI, 8)).pack(anchor="w", padx=10, pady=2)

    def _analyse_password(self, pw: str) -> tuple:
        score = 0
        tips  = []
        if len(pw) >= 8:  score += 1
        else:             tips.append("Use 8+ characters")
        if len(pw) >= 12: score += 1
        if re.search(r'[A-Z]', pw): score += 1
        else: tips.append("Add uppercase letters")
        if re.search(r'[a-z]', pw): score += 1
        else: tips.append("Add lowercase letters")
        if re.search(r'\d', pw):   score += 1
        else: tips.append("Add digits")
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};\':",.<>?/\\|`~]', pw): score += 2
        else: tips.append("Add symbols")
        if len(set(pw)) > len(pw) * 0.6: score += 1

        levels = [
            (2, "Weak",        T["danger"]),
            (4, "Fair",        T["warning"]),
            (5, "Good",        T["info"]),
            (6, "Strong",      T["success"]),
            (8, "Very Strong", T["chart3"]),
        ]
        for threshold, label, color in levels:
            if score <= threshold:
                return label, color, tips[:2]
        return "Very Strong", T["success"], []

    def _copy_password(self, eid: str) -> None:
        entry = next((e for e in self._entries if e["id"] == eid), None)
        if entry:
            self._copy_val(entry["password"])

    def _copy_val(self, val: str) -> None:
        self.wm.clip.copy_text(val)
        self.wm.notifs.send("Password Manager", "Copied to clipboard (clears in 30s)", icon="📋")

    def _entry_ctx(self, e: tk.Event, eid: str) -> None:
        m = tk.Menu(self.wm.root, tearoff=0, bg=T["menu_bg"], fg=T["text"],
                    activebackground=T["accent"], activeforeground=T["text_inverse"])
        m.add_command(label="📖  Open",       command=lambda: self._open_entry(eid))
        m.add_command(label="📋  Copy PW",    command=lambda: self._copy_password(eid))
        m.add_command(label="✏️   Edit",      command=lambda: self._edit_entry(eid))
        m.add_separator()
        m.add_command(label="🗑️   Delete",    command=lambda: self._delete_entry(eid))
        m.post(e.x_root, e.y_root)

    def _new_entry(self) -> None:
        self._edit_entry(None)

    def _edit_entry(self, eid: Optional[str]) -> None:
        entry = next((e for e in self._entries if e["id"] == eid), None) if eid else None
        d = tk.Toplevel(self.wm.root)
        d.title("Edit Entry" if entry else "New Entry")
        d.config(bg=T["win_bg"]); d.geometry("480x500"); d.wm_attributes("-topmost", True)

        fields: Dict[str, tk.Entry] = {}
        defaults = {
            "Site":     entry["site"]     if entry else "",
            "Username": entry["username"] if entry else "",
            "Password": entry["password"] if entry else "",
            "URL":      entry.get("url","")   if entry else "",
            "Notes":    entry.get("notes","") if entry else "",
        }
        for lbl, default in defaults.items():
            row = tk.Frame(d, bg=T["win_bg"])
            row.pack(fill="x", padx=14, pady=5)
            tk.Label(row, text=lbl+":", bg=T["win_bg"], fg=T["text"],
                     font=(FONT_UI, 10), width=9, anchor="e").pack(side="left")
            e = mkentry(row, width=36, password=(lbl=="Password"))
            e.pack(side="left", padx=6, fill="x", expand=True)
            e.insert(0, default)
            fields[lbl] = e
            if lbl == "Password":
                mkbtn(row, "⚡", self._open_generator).pack(side="left", padx=2)

        # Category
        cat_row = tk.Frame(d, bg=T["win_bg"]); cat_row.pack(fill="x", padx=14, pady=5)
        tk.Label(cat_row, text="Category:", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10), width=9, anchor="e").pack(side="left")
        cat_var = tk.StringVar(value=entry.get("category","Web") if entry else "Web")
        ttk.Combobox(cat_row, textvariable=cat_var,
                     values=self.CATEGORIES[1:], state="readonly", width=16).pack(side="left", padx=6)

        def save() -> None:
            if not fields["Site"].get().strip():
                messagebox.showwarning("Missing", "Site name is required.", parent=d)
                return
            if entry:
                entry.update({
                    "site": fields["Site"].get(), "username": fields["Username"].get(),
                    "password": fields["Password"].get(), "url": fields["URL"].get(),
                    "notes": fields["Notes"].get(), "category": cat_var.get(),
                    "modified": time.time(),
                })
            else:
                self._entries.append({
                    "id":       f"pw{len(self._entries)+1:03d}",
                    "site":     fields["Site"].get(),
                    "username": fields["Username"].get(),
                    "password": fields["Password"].get(),
                    "url":      fields["URL"].get(),
                    "category": cat_var.get(),
                    "notes":    fields["Notes"].get(),
                    "created":  time.time(), "modified": time.time(),
                })
            d.destroy(); self._refresh()
            self.wm.notifs.send("Password Manager",
                                 f"Saved: {fields['Site'].get()}", icon="🔐")

        bf = tk.Frame(d, bg=T["win_bg"]); bf.pack(fill="x", padx=14, pady=10)
        mkbtn(bf, "💾  Save", save, kind="accent").pack(side="left", padx=4)
        mkbtn(bf, "Cancel",   d.destroy).pack(side="left", padx=4)
        fields["Site"].focus_set()

    def _delete_entry(self, eid: str) -> None:
        entry = next((e for e in self._entries if e["id"] == eid), None)
        if entry and messagebox.askyesno(
            "Delete", f"Delete entry for '{entry['site']}'?", parent=self.wm.root
        ):
            self._entries.remove(entry)
            self._cur_id = None
            self._show_placeholder()
            self._refresh()

    def _open_generator(self) -> None:
        d = tk.Toplevel(self.wm.root)
        d.title("Password Generator")
        d.config(bg=T["win_bg"]); d.geometry("380x340"); d.wm_attributes("-topmost", True)

        tk.Label(d, text="🔑  Password Generator",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 12, "bold")).pack(pady=(12, 8))

        opts = tk.Frame(d, bg=T["win_bg"]); opts.pack(fill="x", padx=20)
        length_var = tk.IntVar(value=16)
        upper_var  = tk.BooleanVar(value=True)
        lower_var  = tk.BooleanVar(value=True)
        digits_var = tk.BooleanVar(value=True)
        symbols_var= tk.BooleanVar(value=True)
        exclude_var= tk.StringVar(value="0O1lI")

        for lbl, var, w in [("Length:", length_var, 5)]:
            row = tk.Frame(opts, bg=T["win_bg"]); row.pack(fill="x", pady=3)
            tk.Label(row, text=lbl, bg=T["win_bg"], fg=T["text"],
                     font=(FONT_UI, 10), width=14, anchor="w").pack(side="left")
            tk.Spinbox(row, from_=4, to=64, textvariable=var,
                       bg=T["input_bg"], fg=T["text"], relief="flat", width=w).pack(side="left", padx=6)

        for lbl, var in [("Uppercase (A-Z)", upper_var), ("Lowercase (a-z)", lower_var),
                          ("Digits (0-9)", digits_var), ("Symbols (!@#…)", symbols_var)]:
            row = tk.Frame(opts, bg=T["win_bg"]); row.pack(fill="x", pady=2)
            tk.Checkbutton(row, text=lbl, variable=var,
                           bg=T["win_bg"], fg=T["text"],
                           selectcolor=T["accent"], activebackground=T["win_bg"],
                           font=(FONT_UI, 9)).pack(side="left")

        row = tk.Frame(opts, bg=T["win_bg"]); row.pack(fill="x", pady=3)
        tk.Label(row, text="Exclude chars:", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 9), width=14, anchor="w").pack(side="left")
        mkentry(row, textvariable=exclude_var, width=10).pack(side="left", padx=6)

        result_var = tk.StringVar()
        result_lbl = tk.Label(d, textvariable=result_var,
                               bg=T["panel_alt"], fg=T["accent"],
                               font=(FONT_MONO, 12, "bold"),
                               padx=12, pady=8, wraplength=340)
        result_lbl.pack(fill="x", padx=16, pady=8)

        str_lbl = tk.Label(d, text="", bg=T["win_bg"], fg=T["text_muted"],
                            font=(FONT_UI, 8))
        str_lbl.pack()

        def generate() -> None:
            charset = ""
            if upper_var.get():   charset += string.ascii_uppercase
            if lower_var.get():   charset += string.ascii_lowercase
            if digits_var.get():  charset += string.digits
            if symbols_var.get(): charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"
            excl = exclude_var.get()
            charset = "".join(c for c in charset if c not in excl)
            if not charset:
                result_var.set("(no chars selected)")
                return
            pw = "".join(random.choice(charset) for _ in range(length_var.get()))
            result_var.set(pw)
            strength, color, _ = self._analyse_password(pw)
            str_lbl.config(text=f"Strength: {strength}", fg=color)

        def use_pw() -> None:
            pw = result_var.get()
            if pw and pw != "(no chars selected)":
                self.wm.clip.copy_text(pw)
                self.wm.notifs.send("Password Manager", "Generated password copied!", icon="🔑")
                d.destroy()

        bf = tk.Frame(d, bg=T["win_bg"]); bf.pack(fill="x", padx=16, pady=6)
        mkbtn(bf, "⚡  Generate", generate, kind="accent").pack(side="left", padx=4)
        mkbtn(bf, "📋  Copy & Use", use_pw).pack(side="left", padx=4)
        generate()

    def _import_csv(self) -> None:
        path = simpledialog.askstring("Import CSV", "VFS path to CSV file:",
                                       initialvalue="/home/user/Downloads/passwords.csv",
                                       parent=self.wm.root)
        if path and self.wm.vfs.isfile(path):
            try:
                lines = self.wm.vfs.read(path).split("\n")
                count = 0
                for line in lines[1:]:
                    if not line.strip(): continue
                    parts = line.split(",")
                    if len(parts) >= 3:
                        self._entries.append({
                            "id": f"pw{len(self._entries)+1:03d}",
                            "site": parts[0], "username": parts[1], "password": parts[2],
                            "url": parts[3] if len(parts) > 3 else "",
                            "category": "Other", "notes": "",
                            "created": time.time(), "modified": time.time(),
                        })
                        count += 1
                self._refresh()
                self.wm.notifs.send("Password Manager", f"Imported {count} entries", icon="📥")
            except Exception as ex:
                messagebox.showerror("Import Error", str(ex), parent=self.wm.root)

    def _export_csv(self) -> None:
        path = "/home/user/Downloads/passwords_export.csv"
        lines = ["Site,Username,Password,URL,Category,Notes"]
        for e in self._entries:
            lines.append(f"{e['site']},{e['username']},{e['password']},"
                         f"{e.get('url','')},{e.get('category','')},{e.get('notes','')}")
        self.wm.vfs.write(path, "\n".join(lines))
        self.wm.notifs.send("Password Manager", f"Exported to {path}", icon="📤")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 27 — SPREADSHEET APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class SpreadsheetApp(BaseWin):
    """
    Full spreadsheet with:
      • Editable grid (26 cols × 100 rows)
      • Formula support: =SUM, =AVG, =MAX, =MIN, =COUNT, =IF, arithmetic
      • Cell references (A1, B2 etc.)
      • Column / row resize
      • Cell formatting: bold, colour, alignment
      • Sort by column
      • CSV import / export
      • Find & replace
      • Auto-fill series
      • Named cells / simple chart preview
    """

    COLS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    ROWS = 50

    def __init__(self, wm: WM, filepath: Optional[str] = None) -> None:
        self._filepath = filepath
        self._data: Dict[Tuple[int,int], str] = {}   # (row, col) → raw value
        self._fmt:  Dict[Tuple[int,int], Dict] = {}  # (row, col) → format dict
        self._col_w:  Dict[int, int] = {}            # col index → pixel width
        self._row_h:  Dict[int, int] = {}
        self._sel_cell: Tuple[int,int] = (0, 0)
        self._edit_var  = tk.StringVar()
        self._modified  = False
        self._col_w_default = 80
        self._row_h_default = 22
        super().__init__(wm, "Spreadsheet", 80, 60, 1000, 620, "📈",
                         min_w=500, min_h=300)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])
        self._build_toolbar(parent)
        self._build_formula_bar(parent)
        self._build_grid(parent)
        self._build_status(parent)
        if self._filepath and self.wm.vfs.isfile(self._filepath):
            self._load_csv(self._filepath)
        self._redraw()

    def _build_toolbar(self, parent: tk.Frame) -> None:
        tb = tk.Frame(parent, bg=T["panel_bg"], height=40)
        tb.pack(fill="x"); tb.pack_propagate(False)

        actions = [
            ("📂 Open",   self._open_csv),
            ("💾 Save",   self._save_csv),
            ("📤 Export", self._export_csv2),
            ("🔍 Find",   self._find_replace),
            ("⬆ Sort A→Z",partial(self._sort_col, False)),
            ("⬇ Sort Z→A",partial(self._sort_col, True)),
            ("📊 Chart",  self._show_chart),
            ("🧹 Clear",  self._clear_selection),
        ]
        for lbl, cmd in actions:
            tk.Button(tb, text=lbl, command=cmd,
                      bg=T["button_bg"], fg=T["text"], relief="flat", bd=0,
                      font=(FONT_UI, 9), padx=8, pady=4, cursor="hand2",
                      activebackground=T["button_hover"]).pack(side="left", padx=2, pady=4)

        mksep(tb,"vertical").pack(side="left",fill="y",pady=6,padx=4)

        # Format buttons
        self._bold_var = tk.BooleanVar(value=False)
        for icon, cmd in [("B", self._fmt_bold), ("I", self._fmt_italic),
                           ("🎨", self._fmt_color)]:
            tk.Button(tb, text=icon, command=cmd,
                      bg=T["button_bg"], fg=T["text"], relief="flat", bd=0,
                      font=(FONT_UI, 9, "bold" if icon=="B" else "italic" if icon=="I" else "normal"),
                      padx=6, pady=4, cursor="hand2",
                      activebackground=T["button_hover"]).pack(side="left", padx=1, pady=4)

    def _build_formula_bar(self, parent: tk.Frame) -> None:
        fb = tk.Frame(parent, bg=T["panel_alt"], height=28)
        fb.pack(fill="x"); fb.pack_propagate(False)
        self._cell_ref_lbl = tk.Label(fb, text="A1",
                                       bg=T["panel_alt"], fg=T["text"],
                                       font=(FONT_MONO, 10, "bold"), width=5)
        self._cell_ref_lbl.pack(side="left", padx=6)
        mksep(fb,"vertical").pack(side="left",fill="y",pady=4,padx=2)
        tk.Label(fb, text="fx", bg=T["panel_alt"], fg=T["text_muted"],
                 font=(FONT_UI, 9, "italic")).pack(side="left", padx=4)
        formula_entry = mk_formula_entry = tk.Entry(
            fb, textvariable=self._edit_var,
            bg=T["input_bg"], fg=T["text"],
            insertbackground=T["text"],
            relief="flat", font=(FONT_MONO, 10), bd=2,
        )
        formula_entry.pack(side="left", fill="x", expand=True, padx=4, pady=3)
        formula_entry.bind("<Return>",  self._formula_commit)
        formula_entry.bind("<Escape>",  lambda e: self._edit_var.set(self._get_raw(*self._sel_cell)))

    def _build_grid(self, parent: tk.Frame) -> None:
        grid_outer = tk.Frame(parent, bg=T["win_bg"])
        grid_outer.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(grid_outer, bg=T["win_bg"], highlightthickness=0)
        hsb = tk.Scrollbar(grid_outer, orient="horizontal", command=self._canvas.xview)
        vsb = tk.Scrollbar(grid_outer, orient="vertical",   command=self._canvas.yview)
        self._canvas.config(xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        self._canvas.pack(fill="both", expand=True)

        total_w = 50 + sum(self._col_w.get(c, self._col_w_default) for c in range(len(self.COLS)))
        total_h = 24 + self.ROWS * self._row_h_default
        self._canvas.config(scrollregion=(0, 0, total_w, total_h))

        self._canvas.bind("<Button-1>",  self._canvas_click)
        self._canvas.bind("<Double-Button-1>", self._canvas_dbl)
        self._canvas.bind("<Key>",       self._canvas_key)
        self._canvas.bind("<MouseWheel>",
                           lambda e: self._canvas.yview_scroll(-1*(e.delta//120),"units"))
        self._canvas.focus_set()

    def _build_status(self, parent: tk.Frame) -> None:
        sf = tk.Frame(parent, bg=T["status_bg"], height=22)
        sf.pack(fill="x", side="bottom"); sf.pack_propagate(False)
        self._status = tk.Label(sf, text="Ready",
                                 bg=T["status_bg"], fg=T["text_muted"],
                                 font=(FONT_UI, 8), anchor="w", padx=8)
        self._status.pack(side="left", fill="y")
        self._sum_lbl = tk.Label(sf, text="",
                                  bg=T["status_bg"], fg=T["text_muted"],
                                  font=(FONT_UI, 8), padx=8)
        self._sum_lbl.pack(side="right")

    # ── grid drawing ──────────────────────────────────────────────────────────

    def _redraw(self) -> None:
        c  = self._canvas
        c.delete("all")
        row_header_w = 50
        col_header_h = 24
        dfl_cw = self._col_w_default
        dfl_rh = self._row_h_default
        border = T["separator"]
        header_bg = T["panel_alt"]

        # Column headers
        x = row_header_w
        for ci, col_name in enumerate(self.COLS):
            cw = self._col_w.get(ci, dfl_cw)
            is_sel = ci == self._sel_cell[1]
            bg = T["accent"] if is_sel else header_bg
            c.create_rectangle(x, 0, x+cw, col_header_h, fill=bg, outline=border)
            c.create_text(x + cw//2, col_header_h//2, text=col_name,
                          fill=T["text"], font=(FONT_UI, 9, "bold"))
            x += cw

        # Row headers + cells
        y = col_header_h
        for ri in range(self.ROWS):
            rh = self._row_h.get(ri, dfl_rh)
            is_sel_row = ri == self._sel_cell[0]
            row_bg = T["accent"] if is_sel_row else header_bg
            c.create_rectangle(0, y, row_header_w, y+rh, fill=row_bg, outline=border)
            c.create_text(row_header_w//2, y+rh//2, text=str(ri+1),
                          fill=T["text"], font=(FONT_UI, 8))

            x2 = row_header_w
            for ci in range(len(self.COLS)):
                cw  = self._col_w.get(ci, dfl_cw)
                key = (ri, ci)
                fmt = self._fmt.get(key, {})
                is_selected = key == self._sel_cell

                cell_bg = T["selection"] if is_selected else fmt.get("bg", T["win_bg"])
                c.create_rectangle(x2, y, x2+cw, y+rh, fill=cell_bg, outline=border)

                raw     = self._data.get(key, "")
                display = self._evaluate(raw, ri, ci)
                if display:
                    align   = fmt.get("align", "left")
                    bold    = fmt.get("bold", False)
                    fg      = fmt.get("fg", T["text"])
                    font    = (FONT_MONO, 9, "bold" if bold else "normal")
                    ax      = x2 + 4 if align == "left" else x2 + cw - 4 if align == "right" else x2 + cw//2
                    anchor  = "w"    if align == "left" else "e"           if align == "right" else "center"
                    # Clip text
                    text    = str(display)[:int(cw/7)]
                    c.create_text(ax, y+rh//2, text=text,
                                  fill=fg, font=font, anchor=anchor)
            y += rh

        # Selection highlight border
        sr, sc     = self._sel_cell
        sel_x      = row_header_w + sum(self._col_w.get(i, dfl_cw) for i in range(sc))
        sel_y      = col_header_h + sum(self._row_h.get(i, dfl_rh) for i in range(sr))
        sel_w      = self._col_w.get(sc, dfl_cw)
        sel_h      = self._row_h.get(sr, dfl_rh)
        c.create_rectangle(sel_x, sel_y, sel_x+sel_w, sel_y+sel_h,
                            outline=T["accent"], width=2)

        # Update formula bar
        col_name = self.COLS[sc] if sc < len(self.COLS) else "?"
        self._cell_ref_lbl.config(text=f"{col_name}{sr+1}")
        raw = self._data.get((sr, sc), "")
        self._edit_var.set(raw)

        # Status / sum
        self._update_status()

    def _update_status(self) -> None:
        total = len(self._data)
        self._status.config(text=f"{total} cells used  |  "
                                  f"Row {self._sel_cell[0]+1}, Col {self.COLS[self._sel_cell[1]]}")
        # Sum selected column
        col = self._sel_cell[1]
        nums = []
        for ri in range(self.ROWS):
            val = self._evaluate(self._data.get((ri,col),""), ri, col)
            try: nums.append(float(val))
            except: pass
        if nums:
            self._sum_lbl.config(
                text=f"Sum: {sum(nums):.4g}  Avg: {sum(nums)/len(nums):.4g}  Count: {len(nums)}"
            )

    # ── cell evaluation ───────────────────────────────────────────────────────

    def _evaluate(self, raw: str, row: int, col: int) -> str:
        if not raw or not raw.startswith("="):
            return raw
        expr = raw[1:].strip()
        try:
            import math as _m
            # Replace cell references  A1 → data value
            def repl_ref(m: re.Match) -> str:
                col_l = m.group(1).upper()
                row_i = int(m.group(2)) - 1
                col_i = self.COLS.index(col_l) if col_l in self.COLS else 0
                val   = self._data.get((row_i, col_i), "0")
                if val.startswith("="):
                    val = self._evaluate(val, row_i, col_i)
                return val if val else "0"
            resolved = re.sub(r'([A-Z])(\d+)', repl_ref, expr, flags=re.IGNORECASE)

            # Built-in range functions  SUM(A1:A10)
            def range_func(name: str, r_str: str) -> float:
                m2 = re.match(r'([A-Z])(\d+):([A-Z])(\d+)', r_str.strip(), re.IGNORECASE)
                if not m2:
                    return 0.0
                c1_l, r1, c2_l, r2 = m2.groups()
                c1 = self.COLS.index(c1_l.upper()) if c1_l.upper() in self.COLS else 0
                c2 = self.COLS.index(c2_l.upper()) if c2_l.upper() in self.COLS else 0
                vals = []
                for ri2 in range(int(r1)-1, int(r2)):
                    for ci2 in range(min(c1,c2), max(c1,c2)+1):
                        raw2 = self._data.get((ri2,ci2),"")
                        ev   = self._evaluate(raw2,ri2,ci2) if raw2 else "0"
                        try: vals.append(float(ev))
                        except: pass
                fns = {"SUM":sum,"AVG":lambda v:sum(v)/len(v) if v else 0,
                       "MAX":max,"MIN":min,"COUNT":len,"COUNTA":len}
                fn = fns.get(name.upper(), sum)
                return fn(vals) if vals else 0.0

            for fn_name in ("SUM","AVG","MAX","MIN","COUNT","COUNTA"):
                def sub_fn(m3: re.Match, fn=fn_name) -> str:
                    return str(range_func(fn, m3.group(1)))
                resolved = re.sub(
                    rf'\b{fn_name}\(([^)]+)\)', sub_fn, resolved, flags=re.IGNORECASE
                )

            # IF function  IF(cond, true, false)
            if_m = re.match(r'IF\((.+),(.+),(.+)\)$', resolved.strip(), re.IGNORECASE)
            if if_m:
                cond_s, true_s, false_s = if_m.groups()
                safe_env = {"__builtins__": {}}
                try:
                    result = eval(true_s.strip(), safe_env) if eval(cond_s.strip(), safe_env) \
                             else eval(false_s.strip(), safe_env)
                    return str(result)
                except Exception:
                    return "#ERR"

            safe_env = {k: getattr(_m, k) for k in dir(_m) if not k.startswith("_")}
            safe_env["__builtins__"] = {}
            result = eval(resolved, safe_env)
            if isinstance(result, float):
                result = round(result, 6)
                if result == int(result):
                    result = int(result)
            return str(result)
        except Exception:
            return "#ERR"

    def _get_raw(self, row: int, col: int) -> str:
        return self._data.get((row, col), "")

    # ── interaction ───────────────────────────────────────────────────────────

    def _canvas_click(self, e: tk.Event) -> None:
        self._canvas.focus_set()
        rh_w = 50; ch_h = 24
        dfl_cw = self._col_w_default; dfl_rh = self._row_h_default
        cx = self._canvas.canvasx(e.x) - rh_w
        cy = self._canvas.canvasy(e.y) - ch_h
        if cx < 0 or cy < 0:
            return
        # Find column
        x_acc = 0; ci = 0
        for ci in range(len(self.COLS)):
            cw = self._col_w.get(ci, dfl_cw)
            if x_acc + cw > cx:
                break
            x_acc += cw
        # Find row
        y_acc = 0; ri = 0
        for ri in range(self.ROWS):
            rh = self._row_h.get(ri, dfl_rh)
            if y_acc + rh > cy:
                break
            y_acc += rh
        self._sel_cell = (ri, ci)
        self._redraw()

    def _canvas_dbl(self, e: tk.Event) -> None:
        raw = self._get_raw(*self._sel_cell)
        self._edit_var.set(raw)

    def _canvas_key(self, e: tk.Event) -> None:
        ri, ci = self._sel_cell
        nav = {"Up":(-1,0),"Down":(1,0),"Left":(0,-1),"Right":(0,1),
               "Tab":(0,1),"Return":(1,0)}
        if e.keysym in nav:
            dr, dc = nav[e.keysym]
            ri2 = max(0, min(self.ROWS-1, ri+dr))
            ci2 = max(0, min(len(self.COLS)-1, ci+dc))
            self._sel_cell = (ri2, ci2)
            self._redraw()
            return
        if e.keysym == "Delete":
            self._data.pop(self._sel_cell, None)
            self._modified = True
            self._redraw()
            return
        if len(e.char) == 1 and e.char.isprintable():
            current = self._data.get(self._sel_cell, "")
            self._data[self._sel_cell] = current + e.char
            self._edit_var.set(self._data[self._sel_cell])
            self._modified = True
            self._redraw()

    def _formula_commit(self, e: tk.Event = None) -> None:
        val = self._edit_var.get()
        if val:
            self._data[self._sel_cell] = val
        else:
            self._data.pop(self._sel_cell, None)
        self._modified = True
        ri, ci = self._sel_cell
        self._sel_cell = (min(self.ROWS-1, ri+1), ci)
        self._redraw()
        self._canvas.focus_set()

    # ── formatting ────────────────────────────────────────────────────────────

    def _fmt_bold(self) -> None:
        fmt = self._fmt.setdefault(self._sel_cell, {})
        fmt["bold"] = not fmt.get("bold", False)
        self._redraw()

    def _fmt_italic(self) -> None:
        fmt = self._fmt.setdefault(self._sel_cell, {})
        fmt["italic"] = not fmt.get("italic", False)
        self._redraw()

    def _fmt_color(self) -> None:
        result = colorchooser.askcolor(title="Cell Color", parent=self.wm.root)
        if result and result[1]:
            self._fmt.setdefault(self._sel_cell, {})["fg"] = result[1]
            self._redraw()

    def _clear_selection(self) -> None:
        self._data.pop(self._sel_cell, None)
        self._fmt.pop(self._sel_cell, None)
        self._modified = True
        self._redraw()

    # ── CSV ───────────────────────────────────────────────────────────────────

    def _load_csv(self, path: str) -> None:
        try:
            content = self.wm.vfs.read(path)
            self._data.clear()
            for ri, line in enumerate(content.split("\n")[:self.ROWS]):
                for ci, cell in enumerate(line.split(",")[:len(self.COLS)]):
                    if cell.strip():
                        self._data[(ri, ci)] = cell.strip()
            self._filepath = path
            self.set_title(path.split("/")[-1] + " — Spreadsheet")
        except Exception as ex:
            messagebox.showerror("Load Error", str(ex), parent=self.wm.root)

    def _open_csv(self) -> None:
        path = simpledialog.askstring("Open CSV", "VFS path:",
                                       initialvalue="/home/user/Spreadsheets/",
                                       parent=self.wm.root)
        if path and self.wm.vfs.isfile(path):
            self._load_csv(path)
            self._redraw()

    def _save_csv(self) -> None:
        if not self._filepath:
            self._export_csv2()
            return
        lines = []
        for ri in range(self.ROWS):
            row_data = []
            last_col = 0
            for ci in range(len(self.COLS)-1, -1, -1):
                if (ri, ci) in self._data:
                    last_col = ci
                    break
            for ci in range(last_col+1):
                row_data.append(self._data.get((ri,ci),""))
            if any(row_data):
                lines.append(",".join(row_data))
        self.wm.vfs.write(self._filepath, "\n".join(lines))
        self._modified = False
        self.wm.notifs.send("Spreadsheet", f"Saved: {self._filepath}", icon="💾")

    def _export_csv2(self) -> None:
        path = simpledialog.askstring("Save As", "VFS path:",
                                       initialvalue=self._filepath or "/home/user/Spreadsheets/sheet.csv",
                                       parent=self.wm.root)
        if path:
            self._filepath = path
            self._save_csv()

    def _sort_col(self, reverse: bool) -> None:
        col = self._sel_cell[1]
        rows_with_data = []
        for ri in range(self.ROWS):
            row_vals = {ci: self._data.get((ri,ci),"") for ci in range(len(self.COLS))}
            rows_with_data.append((ri, row_vals))
        def sort_key(r):
            v = r[1].get(col, "")
            try: return (0, float(v))
            except: return (1, v.lower())
        rows_sorted = sorted(rows_with_data, key=sort_key, reverse=reverse)
        new_data: Dict[Tuple[int,int],str] = {}
        for new_ri, (_, row_vals) in enumerate(rows_sorted):
            for ci, val in row_vals.items():
                if val:
                    new_data[(new_ri, ci)] = val
        self._data = new_data
        self._modified = True
        self._redraw()

    def _find_replace(self) -> None:
        d = tk.Toplevel(self.wm.root); d.title("Find & Replace")
        d.config(bg=T["win_bg"]); d.geometry("360x160"); d.wm_attributes("-topmost",True)
        fe: List[tk.Entry] = []
        for lbl in ["Find:","Replace:"]:
            row = tk.Frame(d,bg=T["win_bg"]); row.pack(fill="x",padx=12,pady=5)
            tk.Label(row,text=lbl,bg=T["win_bg"],fg=T["text"],font=(FONT_UI,10),width=9).pack(side="left")
            e = mkentry(row,width=28); e.pack(side="left",padx=4); fe.append(e)
        info_lbl = tk.Label(d,text="",bg=T["win_bg"],fg=T["text_muted"],font=(FONT_UI,9)); info_lbl.pack()
        def do_replace():
            find,repl=fe[0].get(),fe[1].get(); count=0
            for k,v in self._data.items():
                if find in v:
                    self._data[k]=v.replace(find,repl); count+=1
            info_lbl.config(text=f"Replaced {count} cell(s)"); self._redraw()
        bf=tk.Frame(d,bg=T["win_bg"]); bf.pack(fill="x",padx=12,pady=6)
        mkbtn(bf,"Replace All",do_replace,kind="accent").pack(side="left",padx=4)
        mkbtn(bf,"Close",d.destroy).pack(side="left",padx=4)

    def _show_chart(self) -> None:
        col = self._sel_cell[1]
        col_name = self.COLS[col]
        nums = []
        for ri in range(self.ROWS):
            v = self._evaluate(self._data.get((ri,col),""),ri,col)
            try: nums.append(float(v))
            except: pass
        if not nums:
            messagebox.showinfo("Chart","No numeric data in selected column.",parent=self.wm.root)
            return
        d = tk.Toplevel(self.wm.root); d.title(f"Chart — Column {col_name}")
        d.config(bg=T["win_bg"]); d.geometry("500x320")
        c = tk.Canvas(d,bg=T["panel_alt"],highlightthickness=0); c.pack(fill="both",expand=True,padx=12,pady=12)
        def draw(e=None):
            c.delete("all"); W=c.winfo_width() or 476; H=c.winfo_height() or 280
            max_v=max(abs(v) for v in nums) or 1
            bw=max(4,(W-60)//len(nums)); colors=[T["chart1"],T["chart2"],T["chart3"],T["chart4"],T["chart5"]]
            for i,v in enumerate(nums):
                x=40+i*bw; bh=int((v/max_v)*(H-40)); y=H-20-bh
                c.create_rectangle(x,y,x+bw-2,H-20,fill=colors[i%5],outline="")
                if len(nums)<=20:
                    c.create_text(x+bw//2,H-10,text=str(i+1),fill=T["text_muted"],font=(FONT_UI,7))
            c.create_text(10,H//2,text=f"Max: {max(nums):.2g}",fill=T["text_muted"],font=(FONT_UI,8),angle=90)
        c.bind("<Configure>",draw); c.after(100,draw)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 28 — IMAGE VIEWER APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class ImageViewerApp(BaseWin):
    """
    Canvas-based image viewer that generates and displays procedural images.
    Features:
      • Procedural image gallery (12 generated images)
      • Zoom in / out / fit / actual size
      • Rotate left / right
      • Brightness / contrast sliders
      • Greyscale / invert / sepia filters
      • Slideshow mode (auto-advance)
      • Image info panel (dimensions, colours)
      • Save processed image to VFS
      • Pixel colour picker on hover
    """

    def __init__(self, wm: WM) -> None:
        self._images   = self._generate_gallery()
        self._cur_idx  = 0
        self._zoom     = 1.0
        self._rotation = 0
        self._brightness = 1.0
        self._contrast   = 1.0
        self._filter    = "none"
        self._slideshow = False
        self._ss_delay  = 3000
        super().__init__(wm, "Image Viewer", 150, 60, 860, 580, "🖼️",
                         min_w=400, min_h=300)

    def _generate_gallery(self) -> List[Dict[str, Any]]:
        """Generate 12 procedural canvas-drawn images."""
        images = [
            {"name":"Gradient Sunrise",  "gen":"sunrise",  "w":400,"h":300},
            {"name":"Geometric Pattern", "gen":"geometric","w":400,"h":400},
            {"name":"Starfield",         "gen":"stars",    "w":400,"h":300},
            {"name":"Spiral",            "gen":"spiral",   "w":400,"h":400},
            {"name":"Mandelbrot Preview","gen":"mandel",   "w":400,"h":400},
            {"name":"Colour Wheel",      "gen":"wheel",    "w":400,"h":400},
            {"name":"Checkerboard",      "gen":"checker",  "w":400,"h":400},
            {"name":"Noise Texture",     "gen":"noise",    "w":400,"h":300},
            {"name":"Wave Pattern",      "gen":"wave",     "w":400,"h":300},
            {"name":"Rainbow Bars",      "gen":"rainbow",  "w":400,"h":300},
            {"name":"Grid Circles",      "gen":"circles",  "w":400,"h":400},
            {"name":"Plasma Effect",     "gen":"plasma",   "w":400,"h":300},
        ]
        return images

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])
        self._build_toolbar(parent)
        pane = tk.PanedWindow(parent, orient="horizontal",
                               bg=T["panel_bg"], sashwidth=4)
        pane.pack(fill="both", expand=True)
        sidebar = tk.Frame(pane, bg=T["panel_bg"], width=160)
        pane.add(sidebar, minsize=140)
        self._build_sidebar(sidebar)
        viewer = tk.Frame(pane, bg="#000000")
        pane.add(viewer, minsize=300)
        self._build_viewer(viewer)
        self._build_status(parent)
        self._load_image(0)

    def _build_toolbar(self, parent: tk.Frame) -> None:
        tb = tk.Frame(parent, bg=T["panel_bg"], height=40)
        tb.pack(fill="x"); tb.pack_propagate(False)
        for lbl,cmd in [("◀",self._prev),("▶",self._next),("🔍+",self._zoom_in),
                          ("🔍-",self._zoom_out),("⊡",self._fit),("↺",self._rotate_l),
                          ("↻",self._rotate_r),("▶▶",self._toggle_slideshow),("💾",self._save_img)]:
            tk.Button(tb,text=lbl,command=cmd,bg=T["button_bg"],fg=T["text"],
                      relief="flat",bd=0,font=(FONT_UI,10),padx=8,pady=4,
                      cursor="hand2",activebackground=T["button_hover"]).pack(side="left",padx=1,pady=4)
        mksep(tb,"vertical").pack(side="left",fill="y",pady=6,padx=4)
        # Filters
        self._filter_var = tk.StringVar(value="none")
        for f,lbl in [("none","Normal"),("grey","Grey"),("invert","Invert"),("sepia","Sepia")]:
            tk.Radiobutton(tb,text=lbl,variable=self._filter_var,value=f,
                           command=lambda f2=f:self._apply_filter(f2),
                           bg=T["panel_bg"],fg=T["text"],selectcolor=T["accent"],
                           activebackground=T["panel_bg"],font=(FONT_UI,9)).pack(side="left",padx=4)

    def _build_sidebar(self, parent: tk.Frame) -> None:
        tk.Label(parent,text="GALLERY",bg=T["panel_bg"],fg=T["text_muted"],
                 font=(FONT_UI,8,"bold"),padx=8).pack(anchor="w",pady=(8,2))
        sf = ScrollableFrame(parent, bg=T["panel_bg"])
        sf.pack(fill="both",expand=True)
        for i,img in enumerate(self._images):
            row = tk.Frame(sf.inner,bg=T["panel_bg"],cursor="hand2")
            row.pack(fill="x")
            tk.Label(row,text=f"🖼️ {img['name'][:18]}",bg=T["panel_bg"],fg=T["text"],
                     font=(FONT_UI,8),anchor="w").pack(side="left",padx=6,pady=4)
            idx=i
            for w in (row,*row.winfo_children()):
                w.bind("<Button-1>",lambda e,i2=idx:self._load_image(i2))
                w.bind("<Enter>",lambda e,r=row:r.config(bg=T["menu_hover"]))
                w.bind("<Leave>",lambda e,r=row:r.config(bg=T["panel_bg"]))

        mksep(parent).pack(fill="x",padx=6,pady=6)
        tk.Label(parent,text="ADJUSTMENTS",bg=T["panel_bg"],fg=T["text_muted"],
                 font=(FONT_UI,8,"bold"),padx=8).pack(anchor="w",pady=(0,2))
        for lbl,attr,lo,hi,default in [("Brightness","_brightness",0.1,2.0,1.0),
                                         ("Contrast","_contrast",0.1,2.0,1.0)]:
            tk.Label(parent,text=lbl,bg=T["panel_bg"],fg=T["text"],
                     font=(FONT_UI,8),padx=8).pack(anchor="w")
            var = tk.DoubleVar(value=default)
            ttk.Scale(parent,from_=lo,to=hi,orient="horizontal",
                      variable=var,length=130,
                      command=lambda v,a=attr:setattr(self,a,float(v)) or self._redraw_image()
                      ).pack(padx=8)

    def _build_viewer(self, parent: tk.Frame) -> None:
        self._view_canvas = tk.Canvas(parent, bg="#000000", highlightthickness=0)
        self._view_canvas.pack(fill="both", expand=True)
        self._view_canvas.bind("<Motion>", self._on_hover)
        self._view_canvas.bind("<MouseWheel>",
            lambda e: self._zoom_in() if e.delta > 0 else self._zoom_out())

    def _build_status(self, parent: tk.Frame) -> None:
        sf = tk.Frame(parent, bg=T["status_bg"], height=22)
        sf.pack(fill="x", side="bottom"); sf.pack_propagate(False)
        self._st_name = tk.Label(sf,text="",bg=T["status_bg"],fg=T["text"],
                                  font=(FONT_UI,8),anchor="w",padx=8); self._st_name.pack(side="left")
        self._st_info = tk.Label(sf,text="",bg=T["status_bg"],fg=T["text_muted"],
                                  font=(FONT_UI,8),padx=8); self._st_info.pack(side="right")
        self._st_px   = tk.Label(sf,text="",bg=T["status_bg"],fg=T["text_muted"],
                                  font=(FONT_MONO,8),padx=8); self._st_px.pack(side="right")

    def _load_image(self, idx: int) -> None:
        self._cur_idx = idx
        img = self._images[idx]
        self._st_name.config(text=img["name"])
        self._st_info.config(text=f"{img['w']}×{img['h']}  •  Zoom: {int(self._zoom*100)}%")
        self.set_title(f"{img['name']} — Image Viewer")
        self._redraw_image()

    def _redraw_image(self) -> None:
        c  = self._view_canvas
        c.delete("all")
        W  = c.winfo_width()  or 680
        H  = c.winfo_height() or 500
        img = self._images[self._cur_idx]
        gen = img["gen"]

        iw = int(img["w"] * self._zoom)
        ih = int(img["h"] * self._zoom)
        ox = max(0, (W - iw) // 2)
        oy = max(0, (H - ih) // 2)

        # Dark background
        c.create_rectangle(0, 0, W, H, fill="#111111", outline="")

        # Checkerboard for transparency indication
        cs = 16
        for xi in range(ox, ox+iw, cs):
            for yi in range(oy, oy+ih, cs):
                bg = "#222" if ((xi-ox)//cs + (yi-oy)//cs) % 2 == 0 else "#1a1a1a"
                c.create_rectangle(xi, yi, min(xi+cs,ox+iw), min(yi+cs,oy+ih),
                                    fill=bg, outline="")

        # Generate image content
        self._draw_gen_image(c, gen, ox, oy, iw, ih)

        # Apply filter overlay
        if self._filter_var.get() == "grey":
            c.create_rectangle(ox,oy,ox+iw,oy+ih, fill="#888888", stipple="gray50", outline="")
        elif self._filter_var.get() == "sepia":
            c.create_rectangle(ox,oy,ox+iw,oy+ih, fill="#8B6914", stipple="gray25", outline="")
        elif self._filter_var.get() == "invert":
            c.create_rectangle(ox,oy,ox+iw,oy+ih, fill="white", stipple="gray75", outline="")

        # Border
        c.create_rectangle(ox-1,oy-1,ox+iw+1,oy+ih+1, outline=T["accent"], width=1)

    def _draw_gen_image(self, c: tk.Canvas, gen: str, ox: int, oy: int, w: int, h: int) -> None:
        rng = random.Random(hash(gen))

        if gen == "sunrise":
            for i in range(h):
                t = i/h
                r=int(255*min(1,t*2)); g=int(100+155*t); b=int(200-150*t)
                c.create_line(ox,oy+i,ox+w,oy+i,fill=f"#{r:02x}{g:02x}{b:02x}")

        elif gen == "geometric":
            colors = [T["chart1"],T["chart2"],T["chart3"],T["chart4"],T["chart5"]]
            for _ in range(30):
                x=rng.randint(ox,ox+w); y=rng.randint(oy,oy+h)
                s=rng.randint(20,80); col=rng.choice(colors)
                shape=rng.choice(["rect","oval","poly"])
                if shape=="rect":
                    c.create_rectangle(x,y,x+s,y+s,fill=col,outline="")
                elif shape=="oval":
                    c.create_oval(x,y,x+s,y+s,fill=col,outline="")
                else:
                    pts=[x+s//2,y, x+s,y+s, x,y+s]
                    c.create_polygon(pts,fill=col,outline="")

        elif gen == "stars":
            c.create_rectangle(ox,oy,ox+w,oy+h,fill="#000018",outline="")
            for _ in range(200):
                x=ox+rng.randint(0,w); y=oy+rng.randint(0,h)
                br=rng.randint(150,255); sz=rng.choice([1,1,1,2])
                c.create_oval(x,y,x+sz,y+sz,fill=f"#{br:02x}{br:02x}{br:02x}",outline="")

        elif gen == "spiral":
            cx2=ox+w//2; cy2=oy+h//2; pts=[]
            for i in range(600):
                a=i*0.15; r2=i*0.4
                pts.extend([cx2+r2*math.cos(a), cy2+r2*math.sin(a)])
            if len(pts)>=4:
                c.create_line(pts,fill=T["accent"],width=2,smooth=True)

        elif gen == "mandel":
            # Very simplified mandelbrot (low-res blocks)
            bw=max(2,w//40); bh=max(2,h//30)
            for yi2 in range(0,h,bh):
                for xi2 in range(0,w,bw):
                    cr=(xi2/w)*3.5-2.5; ci2=(yi2/h)*2-1
                    z=complex(0,0); iters=0
                    while abs(z)<2 and iters<20:
                        z=z*z+complex(cr,ci2); iters+=1
                    t=iters/20
                    r=int(t*200); g=int(t*100); b=int(t*255)
                    c.create_rectangle(ox+xi2,oy+yi2,ox+xi2+bw,oy+yi2+bh,
                                        fill=f"#{min(255,r):02x}{min(255,g):02x}{min(255,b):02x}",outline="")

        elif gen == "wheel":
            cx2=ox+w//2; cy2=oy+h//2; r2=min(w,h)//2-10
            for angle in range(0,360,2):
                a=math.radians(angle)
                hue=angle/360
                r3,g3,b3=colorsys.hsv_to_rgb(hue,1,1)
                col=f"#{int(r3*255):02x}{int(g3*255):02x}{int(b3*255):02x}"
                c.create_arc(cx2-r2,cy2-r2,cx2+r2,cy2+r2,
                              start=angle,extent=2,fill=col,outline=col)

        elif gen == "checker":
            cs=max(8,min(w,h)//16)
            for xi2 in range(0,w,cs):
                for yi2 in range(0,h,cs):
                    col="#ffffff" if (xi2//cs+yi2//cs)%2==0 else "#000000"
                    c.create_rectangle(ox+xi2,oy+yi2,ox+xi2+cs,oy+yi2+cs,fill=col,outline="")

        elif gen == "noise":
            for _ in range(4000):
                x=rng.randint(0,w); y=rng.randint(0,h)
                v=rng.randint(0,255)
                c.create_rectangle(ox+x,oy+y,ox+x+2,oy+y+2,
                                    fill=f"#{v:02x}{v:02x}{v:02x}",outline="")

        elif gen == "wave":
            for yi2 in range(0,h,3):
                pts=[]
                for xi2 in range(0,w+1,4):
                    wave_y=yi2+math.sin(xi2*0.1+yi2*0.05)*20
                    pts.extend([ox+xi2,oy+wave_y])
                if len(pts)>=4:
                    t=yi2/h; r=int(56+t*180); g=int(139-t*80); b=int(253-t*150)
                    c.create_line(pts,fill=f"#{min(255,r):02x}{max(0,g):02x}{max(0,b):02x}",width=1)

        elif gen == "rainbow":
            bh2=h//7
            colors2=["#ff0000","#ff8c00","#ffff00","#00ff00","#0000ff","#4b0082","#8b00ff"]
            for i,col in enumerate(colors2):
                c.create_rectangle(ox,oy+i*bh2,ox+w,oy+(i+1)*bh2,fill=col,outline="")

        elif gen == "circles":
            spacing=max(20,min(w,h)//10)
            for xi2 in range(spacing//2,w,spacing):
                for yi2 in range(spacing//2,h,spacing):
                    r2=spacing//2-3
                    hue=((xi2+yi2)/(w+h))
                    r3,g3,b3=colorsys.hsv_to_rgb(hue,0.8,1)
                    col=f"#{int(r3*255):02x}{int(g3*255):02x}{int(b3*255):02x}"
                    c.create_oval(ox+xi2-r2,oy+yi2-r2,ox+xi2+r2,oy+yi2+r2,fill=col,outline="")

        elif gen == "plasma":
            step=max(2,min(w,h)//60)
            for xi2 in range(0,w,step):
                for yi2 in range(0,h,step):
                    v=(math.sin(xi2*0.05)+math.sin(yi2*0.05)+
                       math.sin((xi2+yi2)*0.035)+math.sin(math.sqrt(xi2*xi2+yi2*yi2)*0.04))
                    t=(v+4)/8
                    r3,g3,b3=colorsys.hsv_to_rgb(t,1,1)
                    col=f"#{int(r3*255):02x}{int(g3*255):02x}{int(b3*255):02x}"
                    c.create_rectangle(ox+xi2,oy+yi2,ox+xi2+step,oy+yi2+step,fill=col,outline="")

    def _on_hover(self, e: tk.Event) -> None:
        self._st_px.config(text=f"X:{e.x} Y:{e.y}")

    def _apply_filter(self, f: str) -> None:
        self._filter = f
        self._redraw_image()

    def _prev(self) -> None:
        self._cur_idx = (self._cur_idx - 1) % len(self._images)
        self._load_image(self._cur_idx)

    def _next(self) -> None:
        self._cur_idx = (self._cur_idx + 1) % len(self._images)
        self._load_image(self._cur_idx)

    def _zoom_in(self) -> None:
        self._zoom = min(4.0, self._zoom + 0.25)
        self._redraw_image()
        self._st_info.config(text=f"{self._images[self._cur_idx]['w']}×{self._images[self._cur_idx]['h']}  •  Zoom: {int(self._zoom*100)}%")

    def _zoom_out(self) -> None:
        self._zoom = max(0.25, self._zoom - 0.25)
        self._redraw_image()
        self._st_info.config(text=f"{self._images[self._cur_idx]['w']}×{self._images[self._cur_idx]['h']}  •  Zoom: {int(self._zoom*100)}%")

    def _fit(self) -> None:
        c = self._view_canvas; W=c.winfo_width() or 680; H=c.winfo_height() or 500
        img = self._images[self._cur_idx]
        self._zoom = min(W/img["w"], H/img["h"]) * 0.9
        self._redraw_image()

    def _rotate_l(self) -> None:
        self._rotation = (self._rotation - 90) % 360
        self.wm.notifs.send("Image Viewer",f"Rotated to {self._rotation}°",icon="↺")
        self._redraw_image()

    def _rotate_r(self) -> None:
        self._rotation = (self._rotation + 90) % 360
        self.wm.notifs.send("Image Viewer",f"Rotated to {self._rotation}°",icon="↻")
        self._redraw_image()

    def _toggle_slideshow(self) -> None:
        self._slideshow = not self._slideshow
        if self._slideshow:
            self.wm.notifs.send("Image Viewer","Slideshow started",icon="▶▶")
            self._slideshow_tick()
        else:
            self.wm.notifs.send("Image Viewer","Slideshow stopped",icon="⏸")

    def _slideshow_tick(self) -> None:
        if not self._out.winfo_exists() or not self._slideshow:
            return
        self._next()
        self.wm.root.after(self._ss_delay, self._slideshow_tick)

    def _save_img(self) -> None:
        path = simpledialog.askstring("Save","Save canvas as PostScript:",
                                       initialvalue=f"/home/user/Pictures/{self._images[self._cur_idx]['name'].replace(' ','_')}.ps",
                                       parent=self.wm.root)
        if path:
            try:
                ps = self._view_canvas.postscript()
                self.wm.vfs.write(path,ps)
                self.wm.notifs.send("Image Viewer",f"Saved: {path}",icon="💾")
            except Exception as ex:
                messagebox.showerror("Save Error",str(ex),parent=self.wm.root)

    def on_resize(self, w: int, h: int) -> None:
        self._redraw_image()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 29 — DISK ANALYZER APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class DiskAnalyzerApp(BaseWin):
    """
    Visual disk space analyzer:
      • Treemap-style canvas view of directory sizes
      • Pie chart showing largest directories
      • Largest files list (top 20)
      • Extension breakdown bar chart
      • Folder tree with size annotations
      • Scan any directory
      • Clean up (delete selected files)
    """

    def __init__(self, wm: WM) -> None:
        self._scan_path = "/home/user"
        self._tab = "treemap"
        super().__init__(wm, "Disk Analyzer", 150, 70, 840, 580, "💾",
                         min_w=500, min_h=380)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])
        tb = tk.Frame(parent, bg=T["panel_bg"], height=40)
        tb.pack(fill="x"); tb.pack_propagate(False)
        self._scan_var = tk.StringVar(value=self._scan_path)
        mkentry(tb, textvariable=self._scan_var, width=28).pack(side="left",padx=8,pady=6)
        mkbtn(tb,"🔍  Scan",self._run_scan,kind="accent").pack(side="left",pady=6)
        for lbl,key in [("Treemap","treemap"),("Pie","pie"),("Top Files","files"),
                         ("By Type","types"),("Tree","tree")]:
            tk.Button(tb,text=lbl,command=partial(self._switch_tab,key),
                      bg=T["button_bg"],fg=T["text"],relief="flat",bd=0,
                      font=(FONT_UI,9),padx=8,pady=4,cursor="hand2",
                      activebackground=T["button_hover"]).pack(side="left",padx=1,pady=4)
        self._content = tk.Frame(parent,bg=T["win_bg"])
        self._content.pack(fill="both",expand=True)
        sf2=tk.Frame(parent,bg=T["status_bg"],height=22); sf2.pack(fill="x",side="bottom"); sf2.pack_propagate(False)
        self._status=tk.Label(sf2,text="",bg=T["status_bg"],fg=T["text_muted"],font=(FONT_UI,8),anchor="w",padx=8); self._status.pack(side="left",fill="y")
        self._run_scan()

    def _switch_tab(self,tab:str)->None:
        self._tab=tab
        for w in self._content.winfo_children(): w.destroy()
        {"treemap":self._draw_treemap,"pie":self._draw_pie,"files":self._show_top_files,
         "types":self._show_types,"tree":self._show_tree}[tab]()

    def _run_scan(self)->None:
        self._scan_path=self._scan_var.get().strip() or "/home/user"
        used,total=self.wm.vfs.disk_usage(self._scan_path)
        files=self.wm.vfs.get_all_files(self._scan_path)
        self._status.config(text=f"Scanned {len(files)} files  |  {fmt_size(used)} in {self._scan_path}")
        self._switch_tab(self._tab)

    def _get_dir_sizes(self)->List[tuple]:
        path=self._scan_path
        try: dirs=self.wm.vfs.listdir(path)
        except: return []
        results=[]
        for d in dirs:
            fp=path.rstrip("/")+"/"+d
            try:
                st=self.wm.vfs.stat(fp)
                results.append((d,st["size"],st["is_dir"]))
            except: pass
        return sorted(results,key=lambda x:-x[1])

    def _draw_treemap(self)->None:
        f=self._content
        c=tk.Canvas(f,bg=T["panel_alt"],highlightthickness=0); c.pack(fill="both",expand=True,padx=8,pady=8)
        items=self._get_dir_sizes()
        if not items: return
        colors=[T["chart1"],T["chart2"],T["chart3"],T["chart4"],T["chart5"],
                T["accent"],T["accent2"],T["success"],T["warning"],T["danger"]]
        def draw(e=None):
            c.delete("all")
            W=c.winfo_width() or 800; H=c.winfo_height() or 500
            total_sz=sum(s for _,s,_ in items) or 1
            x=4; y=4; row_h=max(40,(H-8)//max(1,(len(items)+3)//4))
            col_w=(W-8)//4
            for i,(name,sz,is_dir) in enumerate(items[:20]):
                r,cl=divmod(i,4); bx=x+cl*col_w; by=y+r*row_h
                frac=sz/total_sz; col=colors[i%len(colors)]
                bw=max(4,int(col_w*0.95)); bh=max(4,int(row_h*0.9))
                c.create_rectangle(bx,by,bx+bw,by+bh,fill=col,outline=T["win_bg"],width=2)
                icon="📁" if is_dir else "📄"
                label=f"{icon} {name[:14]}\n{fmt_size(sz)}"
                c.create_text(bx+bw//2,by+bh//2,text=label,fill="#fff",
                               font=(FONT_UI,8),justify="center",width=bw-6)
        c.bind("<Configure>",draw); c.after(100,draw)

    def _draw_pie(self)->None:
        f=self._content; c=tk.Canvas(f,bg=T["win_bg"],highlightthickness=0); c.pack(fill="both",expand=True,padx=8,pady=8)
        items=self._get_dir_sizes()
        if not items: return
        colors=[T["chart1"],T["chart2"],T["chart3"],T["chart4"],T["chart5"],T["accent"],T["accent2"],T["success"]]
        def draw(e=None):
            c.delete("all")
            W=c.winfo_width() or 800; H=c.winfo_height() or 500
            r=min(W,H)//2-60; cx2=W//2-80; cy2=H//2
            total=sum(s for _,s,_ in items[:8]) or 1
            angle=90
            for i,(name,sz,_) in enumerate(items[:8]):
                ext=-sz/total*360; col=colors[i%len(colors)]
                c.create_arc(cx2-r,cy2-r,cx2+r,cy2+r,start=angle,extent=ext,fill=col,outline=T["win_bg"],width=2)
                mid_a=math.radians(angle+ext/2)
                lx=cx2+r*0.75*math.cos(mid_a); ly=cy2-r*0.75*math.sin(mid_a)
                c.create_text(lx,ly,text=f"{int(-ext/3.6)}%",fill="#fff",font=(FONT_UI,8,"bold"))
                angle+=ext
            # Legend
            lx2=cx2+r+20
            for i,(name,sz,_) in enumerate(items[:8]):
                col=colors[i%len(colors)]; ly2=40+i*28
                c.create_rectangle(lx2,ly2,lx2+16,ly2+16,fill=col,outline="")
                c.create_text(lx2+22,ly2+8,text=f"{name[:18]}  {fmt_size(sz)}",
                               fill=T["text"],font=(FONT_UI,9),anchor="w")
        c.bind("<Configure>",draw); c.after(100,draw)

    def _show_top_files(self)->None:
        f=self._content
        tk.Label(f,text=f"Largest Files in {self._scan_path}",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,11,"bold")).pack(pady=(10,4))
        files=self.wm.vfs.get_all_files(self._scan_path)
        file_sizes=[]
        for fp in files:
            try: st=self.wm.vfs.stat(fp); file_sizes.append((fp,st["size"]))
            except: pass
        file_sizes.sort(key=lambda x:-x[1])
        sf=ScrollableFrame(f,bg=T["win_bg"]); sf.pack(fill="both",expand=True,padx=10)
        for i,(fp,sz) in enumerate(file_sizes[:25]):
            bg=T["win_bg"] if i%2==0 else T["panel_bg"]
            row=tk.Frame(sf.inner,bg=bg,cursor="hand2"); row.pack(fill="x")
            icon=get_file_icon(fp.split("/")[-1])
            tk.Label(row,text=icon,bg=bg,fg=T["text"],font=(FONT_EMOJI,11),width=2).pack(side="left",padx=4)
            tk.Label(row,text=fp,bg=bg,fg=T["text"],font=(FONT_UI,9),anchor="w",width=50).pack(side="left",pady=3)
            tk.Label(row,text=fmt_size(sz),bg=bg,fg=T["text_muted"],font=(FONT_MONO,9)).pack(side="right",padx=8)
            pb=ProgressBar(row,width=80,height=6); pb.pack(side="right",padx=4)
            pb.set(sz/(file_sizes[0][1] or 1))
            def make_del(p=fp):
                def del_f():
                    if messagebox.askyesno("Delete",f"Delete {p}?",parent=self.wm.root):
                        try: self.wm.vfs.remove(p); self._run_scan()
                        except Exception as ex: messagebox.showerror("Error",str(ex),parent=self.wm.root)
                return del_f
            tk.Button(row,text="🗑️",command=make_del(),bg=bg,fg=T["danger"],
                      relief="flat",bd=0,font=(FONT_EMOJI,10),cursor="hand2",
                      activebackground=bg).pack(side="right",padx=2)

    def _show_types(self)->None:
        f=self._content
        tk.Label(f,text="Files by Type",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,11,"bold")).pack(pady=(10,6))
        ext_groups=self.wm.vfs.get_ext_groups(self._scan_path)
        top=sorted(ext_groups.items(),key=lambda x:-x[1])[:15]
        if not top: return
        c=tk.Canvas(f,bg=T["win_bg"],height=300,highlightthickness=0); c.pack(fill="x",padx=16,pady=8)
        colors=[T["chart1"],T["chart2"],T["chart3"],T["chart4"],T["chart5"],
                T["accent"],T["accent2"],T["success"],T["warning"],T["danger"]]
        def draw(e=None):
            c.delete("all"); W=c.winfo_width() or 800; H=c.winfo_height() or 300
            max_sz=top[0][1] if top else 1; bw=max(20,(W-60)//len(top)); pad=4
            for i,(ext,sz) in enumerate(top):
                x=30+i*(bw+pad); bh=int((sz/max_sz)*(H-60)); y=H-30-bh
                col=colors[i%len(colors)]
                c.create_rectangle(x,y,x+bw,H-30,fill=col,outline="")
                c.create_text(x+bw//2,H-16,text="."+ext[:5],fill=T["text_muted"],font=(FONT_UI,7))
                c.create_text(x+bw//2,y-8,text=fmt_size(sz),fill=T["text_muted"],font=(FONT_UI,7))
        c.bind("<Configure>",draw); c.after(100,draw)

        sf=ScrollableFrame(f,bg=T["win_bg"]); sf.pack(fill="both",expand=True,padx=10)
        for i,(ext,sz) in enumerate(top):
            bg=T["win_bg"] if i%2==0 else T["panel_bg"]; row=tk.Frame(sf.inner,bg=bg); row.pack(fill="x")
            tk.Label(row,text=f".{ext}",bg=bg,fg=T["text"],font=(FONT_MONO,9),width=8).pack(side="left",padx=6,pady=3)
            pb=ProgressBar(row,width=150,height=8,color=colors[i%len(colors)]); pb.pack(side="left",padx=4)
            pb.set(sz/(top[0][1] or 1))
            tk.Label(row,text=fmt_size(sz),bg=bg,fg=T["text_muted"],font=(FONT_UI,9)).pack(side="left",padx=4)

    def _show_tree(self)->None:
        f=self._content
        tk.Label(f,text=f"Directory Tree: {self._scan_path}",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,11,"bold")).pack(pady=(10,4))
        st=ScrollText(f,font=(FONT_MONO,9),wrap="none"); st.pack(fill="both",expand=True,padx=8,pady=4)
        tree=self.wm.vfs.tree(self._scan_path,max_depth=4)
        st.insert("1.0",f"{self._scan_path}\n"+tree)
        st.text.config(state="disabled")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 30 — CODE RUNNER APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class CodeRunnerApp(BaseWin):
    """
    Interactive Python code execution environment:
      • REPL mode (interactive shell with history)
      • Script mode (run full scripts from VFS)
      • Snippet library (saved reusable snippets)
      • Live output capture (stdout + stderr)
      • Execution time measurement
      • Variable inspector
      • Syntax check before run
      • Clear output / copy output
      • Run on Ctrl+Enter
    """

    SNIPPETS = {
        "Hello World":     'print("Hello from PyOS Code Runner!")\nprint(f"Python {__import__(\"sys\").version}")',
        "Fibonacci":       "def fib(n):\n    a,b=0,1\n    for _ in range(n):\n        yield a\n        a,b=b,a+b\nprint(list(fib(15)))",
        "List Comprehension": "squares = [x**2 for x in range(1,11)]\nevens   = [x for x in range(20) if x%2==0]\nprint('Squares:', squares)\nprint('Evens:  ', evens)",
        "Dictionary ops":  "data = {'name':'PyOS','version':'5.0','lang':'Python'}\nfor k,v in data.items():\n    print(f'  {k}: {v}')",
        "String methods":  "text = 'Hello PyOS World'\nprint(text.upper())\nprint(text.split())\nprint(text.replace('World','Universe'))\nprint(len(text))",
        "Math functions":  "import math\nfor x in [0,30,45,60,90]:\n    print(f'sin({x:3d}°) = {math.sin(math.radians(x)):.4f}')",
        "File operations": "# Simulated VFS operations\nimport time\ncontent = 'Hello from Code Runner'\nprint(f'Content: {content}')\nprint(f'Length:  {len(content)}')\nprint(f'Words:   {len(content.split())}')",
        "Data analysis":   "data=[23,45,12,67,34,89,56,78,90,11,43,65]\nprint(f'Sum:    {sum(data)}')\nprint(f'Mean:   {sum(data)/len(data):.2f}')\nprint(f'Max:    {max(data)}')\nprint(f'Min:    {min(data)}')\nprint(f'Sorted: {sorted(data)}')",
        "Class example":   "class Animal:\n    def __init__(self,name,sound):\n        self.name=name; self.sound=sound\n    def speak(self):\n        return f'{self.name} says {self.sound}!'\n\nfor a in [Animal('Cat','meow'),Animal('Dog','woof'),Animal('Cow','moo')]:\n    print(a.speak())",
        "Generator":       "def count_up(start,stop,step=1):\n    n=start\n    while n<=stop:\n        yield n; n+=step\n\nfor n in count_up(1,20,2):\n    print(n,end=' ')\nprint()",
    }

    def __init__(self, wm: WM) -> None:
        self._repl_history: List[str] = []
        self._repl_pos      = -1
        self._exec_globals  = {"__builtins__": __builtins__}
        self._cur_snippet   = "Hello World"
        super().__init__(wm, "Code Runner", 220, 60, 920, 640, "⚡",
                         min_w=500, min_h=400)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])
        notebook_f = tk.Frame(parent, bg=T["panel_bg"])
        notebook_f.pack(fill="x")
        self._tab_btns: Dict[str, tk.Button] = {}
        for lbl in ["Script","REPL","Snippets","Variables"]:
            k = lbl.lower()
            b = tk.Button(notebook_f, text=lbl,
                          command=partial(self._switch_tab, k),
                          bg=T["accent"] if lbl=="Script" else T["button_bg"],
                          fg=T["text"], relief="flat", bd=0,
                          font=(FONT_UI, 10), padx=14, pady=6, cursor="hand2",
                          activebackground=T["button_hover"])
            b.pack(side="left", padx=2, pady=4)
            self._tab_btns[k] = b
        self._content = tk.Frame(parent, bg=T["win_bg"])
        self._content.pack(fill="both", expand=True)
        self._build_script_tab()

    def _switch_tab(self, tab: str) -> None:
        for k,b in self._tab_btns.items():
            b.config(bg=T["accent"] if k==tab else T["button_bg"])
        for w in self._content.winfo_children(): w.destroy()
        {"script":self._build_script_tab,"repl":self._build_repl_tab,
         "snippets":self._build_snippets_tab,"variables":self._build_vars_tab}[tab]()

    # ── SCRIPT TAB ────────────────────────────────────────────────────────────

    def _build_script_tab(self) -> None:
        f = self._content
        # Toolbar
        tb = tk.Frame(f, bg=T["panel_bg"], height=36); tb.pack(fill="x"); tb.pack_propagate(False)
        for lbl,cmd,kind in [("▶  Run","run","accent"),("🔍  Syntax Check","check","normal"),
                               ("📂  Load","load","normal"),("💾  Save","save_","normal"),
                               ("🗑️  Clear Output","clear_out","normal")]:
            if lbl=="▶  Run": cb=self._run_script
            elif lbl=="🔍  Syntax Check": cb=self._syntax_check
            elif lbl=="📂  Load": cb=self._load_script
            elif lbl=="💾  Save": cb=self._save_script
            else: cb=self._clear_output
            mkbtn(tb,lbl,cb,kind=kind).pack(side="left",padx=4,pady=4)
        self._run_time_lbl=tk.Label(tb,text="",bg=T["panel_bg"],fg=T["text_muted"],font=(FONT_UI,8)); self._run_time_lbl.pack(side="right",padx=8)

        pane=tk.PanedWindow(f,orient="vertical",bg=T["win_bg"],sashwidth=5,sashrelief="flat"); pane.pack(fill="both",expand=True)

        # Code editor
        ed_f=tk.Frame(pane,bg=T["win_bg"]); pane.add(ed_f,minsize=150)
        tk.Label(ed_f,text="Code Editor",bg=T["win_bg"],fg=T["text_muted"],font=(FONT_UI,8,"bold"),anchor="w",padx=6).pack(anchor="w",pady=(4,0))
        self._code_ed=ScrollText(ed_f,font=(FONT_MONO,11),wrap="none",hscroll=True); self._code_ed.pack(fill="both",expand=True,padx=4,pady=4)
        self._code_ed.text.config(bg="#0d1117",fg="#e6edf3")
        self._code_ed.insert("1.0",self.SNIPPETS["Hello World"])
        self._code_ed.text.bind("<Control-Return>",lambda e:self._run_script())
        self._code_ed.text.bind("<Control-s>",     lambda e:self._save_script())

        # Output
        out_f=tk.Frame(pane,bg=T["win_bg"]); pane.add(out_f,minsize=100)
        out_hdr=tk.Frame(out_f,bg=T["panel_alt"]); out_hdr.pack(fill="x")
        tk.Label(out_hdr,text="Output",bg=T["panel_alt"],fg=T["text_muted"],font=(FONT_UI,8,"bold"),padx=6).pack(side="left",pady=2)
        tk.Button(out_hdr,text="📋 Copy",command=self._copy_output,bg=T["panel_alt"],fg=T["text"],
                  relief="flat",bd=0,font=(FONT_UI,8),padx=6,cursor="hand2",
                  activebackground=T["button_hover"]).pack(side="right",pady=2)
        self._output_text=tk.Text(out_f,bg="#0c0c0c",fg="#e6edf3",
                                    font=(FONT_MONO,10),relief="flat",bd=0,
                                    padx=8,pady=6,wrap="word",state="disabled",
                                    height=8)
        vsb2=tk.Scrollbar(out_f,orient="vertical",command=self._output_text.yview)
        self._output_text.config(yscrollcommand=vsb2.set)
        vsb2.pack(side="right",fill="y"); self._output_text.pack(fill="both",expand=True,padx=4,pady=4)
        self._output_text.tag_configure("error",  foreground="#f85149")
        self._output_text.tag_configure("success",foreground="#3fb950")
        self._output_text.tag_configure("info",   foreground="#58a6ff")

    def _run_script(self) -> None:
        code = self._code_ed.get("1.0","end-1c")
        self._execute_code(code)

    def _syntax_check(self) -> None:
        code = self._code_ed.get("1.0","end-1c")
        try:
            import ast as _ast; _ast.parse(code)
            self._write_output("✅ Syntax OK — no errors found\n","success")
        except SyntaxError as ex:
            self._write_output(f"❌ Syntax Error at line {ex.lineno}: {ex.msg}\n","error")

    def _load_script(self) -> None:
        path=simpledialog.askstring("Load Script","VFS path:",initialvalue="/home/user/Code/",parent=self.wm.root)
        if path and self.wm.vfs.isfile(path):
            try:
                self._code_ed.delete("1.0","end"); self._code_ed.insert("1.0",self.wm.vfs.read(path))
                self.wm.notifs.send("Code Runner",f"Loaded: {path}",icon="📂")
            except Exception as ex: messagebox.showerror("Error",str(ex),parent=self.wm.root)

    def _save_script(self) -> None:
        path=simpledialog.askstring("Save Script","VFS path:",initialvalue="/home/user/Code/script.py",parent=self.wm.root)
        if path:
            self.wm.vfs.write(path,self._code_ed.get("1.0","end-1c"))
            self.wm.notifs.send("Code Runner",f"Saved: {path}",icon="💾")

    def _clear_output(self) -> None:
        self._output_text.config(state="normal"); self._output_text.delete("1.0","end"); self._output_text.config(state="disabled")

    def _copy_output(self) -> None:
        self.wm.clip.copy_text(self._output_text.get("1.0","end-1c"))
        self.wm.notifs.send("Code Runner","Output copied to clipboard",icon="📋")

    def _write_output(self, text: str, tag: str = "") -> None:
        self._output_text.config(state="normal")
        if tag: self._output_text.insert("end",text,tag)
        else:   self._output_text.insert("end",text)
        self._output_text.see("end"); self._output_text.config(state="disabled")

    def _execute_code(self, code: str) -> None:
        import io as _io, time as _t
        self._clear_output()
        self._write_output(f"─── Running ───  {datetime.datetime.now():%H:%M:%S}\n","info")
        old_stdout = sys.stdout; old_stderr = sys.stderr
        out_buf = _io.StringIO(); err_buf = _io.StringIO()
        sys.stdout = out_buf; sys.stderr = err_buf
        t0 = _t.perf_counter()
        error_msg = None
        try:
            exec(compile(code,"<code_runner>","exec"), self._exec_globals)
        except SystemExit:
            pass
        except Exception:
            error_msg = traceback.format_exc()
        finally:
            sys.stdout = old_stdout; sys.stderr = old_stderr
        elapsed = _t.perf_counter() - t0
        out = out_buf.getvalue(); err = err_buf.getvalue()
        if out: self._write_output(out)
        if err: self._write_output(err,"error")
        if error_msg: self._write_output(error_msg,"error")
        tag = "error" if (error_msg or err) else "success"
        self._write_output(f"\n─── Done in {elapsed*1000:.1f}ms ───\n",tag)
        try: self._run_time_lbl.config(text=f"Last run: {elapsed*1000:.1f}ms")
        except: pass

    # ── REPL TAB ──────────────────────────────────────────────────────────────

    def _build_repl_tab(self) -> None:
        f = self._content
        tk.Label(f,text="Interactive Python REPL",bg=T["win_bg"],fg=T["text"],font=(FONT_UI,11,"bold")).pack(pady=(8,4))
        self._repl_out=tk.Text(f,bg="#0c0c0c",fg="#e6edf3",font=(FONT_MONO,10),
                                relief="flat",bd=0,padx=8,pady=6,wrap="word",state="disabled")
        vsb=tk.Scrollbar(f,orient="vertical",command=self._repl_out.yview)
        self._repl_out.config(yscrollcommand=vsb.set)
        vsb.pack(side="right",fill="y"); self._repl_out.pack(fill="both",expand=True,padx=4,pady=4)
        self._repl_out.tag_configure("prompt",foreground="#4ec9b0",font=(FONT_MONO,10,"bold"))
        self._repl_out.tag_configure("output",foreground="#e6edf3")
        self._repl_out.tag_configure("error", foreground="#f85149")
        self._repl_out.tag_configure("result",foreground="#3fb950")

        inp=tk.Frame(f,bg="#161b22"); inp.pack(fill="x",padx=4,pady=4)
        tk.Label(inp,text=">>> ",bg="#161b22",fg="#4ec9b0",font=(FONT_MONO,10,"bold")).pack(side="left")
        self._repl_var=tk.StringVar()
        self._repl_entry=tk.Entry(inp,textvariable=self._repl_var,bg="#161b22",fg="#e6edf3",
                                   insertbackground="#e6edf3",relief="flat",font=(FONT_MONO,10),bd=0)
        self._repl_entry.pack(side="left",fill="x",expand=True,pady=6)
        self._repl_entry.bind("<Return>",   self._repl_exec)
        self._repl_entry.bind("<Up>",       self._repl_hist_up)
        self._repl_entry.bind("<Down>",     self._repl_hist_dn)
        self._repl_entry.bind("<Control-c>",lambda e:self._repl_var.set(""))
        self._repl_entry.bind("<Control-l>",lambda e:self._repl_clear())
        self._repl_entry.focus_set()
        self._repl_write(f"Python {sys.version.split()[0]} on PyOS {PYOS_VERSION}\n","result")
        self._repl_write('Type Python expressions. Use "exit()" or Ctrl+C to clear.\n\n',"output")

    def _repl_write(self,text:str,tag:str="output") -> None:
        self._repl_out.config(state="normal"); self._repl_out.insert("end",text,tag)
        self._repl_out.see("end"); self._repl_out.config(state="disabled")

    def _repl_exec(self,e=None) -> None:
        code=self._repl_var.get().strip(); self._repl_var.set("")
        if not code: return
        self._repl_history.append(code); self._repl_pos=len(self._repl_history)
        self._repl_write(">>> "+code+"\n","prompt")
        import io as _io
        old=sys.stdout; buf=_io.StringIO(); sys.stdout=buf
        result=None; error=None
        try:
            try: result=eval(compile(code,"<repl>","eval"),self._exec_globals)
            except SyntaxError: exec(compile(code,"<repl>","exec"),self._exec_globals)
        except Exception: error=traceback.format_exc()
        finally: sys.stdout=old
        out=buf.getvalue()
        if out:   self._repl_write(out,"output")
        if result is not None and not out: self._repl_write(repr(result)+"\n","result")
        if error: self._repl_write(error,"error")

    def _repl_hist_up(self,e) -> str:
        if self._repl_history and self._repl_pos>0:
            self._repl_pos-=1; self._repl_var.set(self._repl_history[self._repl_pos])
        return "break"

    def _repl_hist_dn(self,e) -> str:
        if self._repl_pos<len(self._repl_history)-1:
            self._repl_pos+=1; self._repl_var.set(self._repl_history[self._repl_pos])
        else:
            self._repl_pos=len(self._repl_history); self._repl_var.set("")
        return "break"

    def _repl_clear(self) -> None:
        self._repl_out.config(state="normal"); self._repl_out.delete("1.0","end"); self._repl_out.config(state="disabled")

    # ── SNIPPETS TAB ──────────────────────────────────────────────────────────

    def _build_snippets_tab(self) -> None:
        f=self._content
        pane=tk.PanedWindow(f,orient="horizontal",bg=T["panel_bg"],sashwidth=4); pane.pack(fill="both",expand=True)
        left=tk.Frame(pane,bg=T["panel_bg"],width=200); pane.add(left,minsize=160)
        right=tk.Frame(pane,bg=T["win_bg"]); pane.add(right,minsize=300)
        tk.Label(left,text="SNIPPETS",bg=T["panel_bg"],fg=T["text_muted"],font=(FONT_UI,8,"bold"),padx=8).pack(anchor="w",pady=(8,2))
        sf=ScrollableFrame(left,bg=T["panel_bg"]); sf.pack(fill="both",expand=True)
        self._snip_code=ScrollText(right,font=(FONT_MONO,10),wrap="none"); self._snip_code.pack(fill="both",expand=True,padx=4,pady=4)
        self._snip_code.text.config(bg="#0d1117",fg="#e6edf3")
        bf=tk.Frame(right,bg=T["win_bg"]); bf.pack(fill="x",padx=4,pady=4)
        mkbtn(bf,"▶ Run Snippet",self._run_snippet,kind="accent").pack(side="left",padx=4)
        mkbtn(bf,"📋 Copy to Script",self._copy_to_script).pack(side="left",padx=4)
        for name in self.SNIPPETS:
            row=tk.Frame(sf.inner,bg=T["panel_bg"],cursor="hand2"); row.pack(fill="x")
            tk.Label(row,text=f"⚡ {name}",bg=T["panel_bg"],fg=T["text"],font=(FONT_UI,9),anchor="w").pack(side="left",padx=8,pady=5)
            def load(n=name):
                self._cur_snippet=n; self._snip_code.delete("1.0","end"); self._snip_code.insert("1.0",self.SNIPPETS[n])
            for w in (row,*row.winfo_children()):
                w.bind("<Button-1>",lambda e,l=load:l())
                w.bind("<Enter>",lambda e,r=row:r.config(bg=T["menu_hover"]))
                w.bind("<Leave>",lambda e,r=row:r.config(bg=T["panel_bg"]))
        # Load first
        self._snip_code.delete("1.0","end"); self._snip_code.insert("1.0",self.SNIPPETS[self._cur_snippet])

    def _run_snippet(self) -> None:
        code=self._snip_code.get("1.0","end-1c")
        d=tk.Toplevel(self.wm.root); d.title("Snippet Output"); d.config(bg=T["win_bg"]); d.geometry("560x300")
        t=tk.Text(d,bg="#0c0c0c",fg="#e6edf3",font=(FONT_MONO,10),relief="flat",bd=8,wrap="word"); t.pack(fill="both",expand=True,padx=6,pady=6)
        t.tag_configure("error",foreground="#f85149"); t.tag_configure("success",foreground="#3fb950")
        import io as _io; old=sys.stdout; buf=_io.StringIO(); sys.stdout=buf; err=None
        try: exec(compile(code,"<snippet>","exec"),{})
        except Exception: err=traceback.format_exc()
        finally: sys.stdout=old
        out=buf.getvalue()
        t.insert("1.0",out if out else "(no output)","success" if not err else "")
        if err: t.insert("end","\n"+err,"error")
        t.config(state="disabled"); mkbtn(d,"Close",d.destroy).pack(pady=6)

    def _copy_to_script(self) -> None:
        code=self._snip_code.get("1.0","end-1c"); self._switch_tab("script")
        self._code_ed.delete("1.0","end"); self._code_ed.insert("1.0",code)

    # ── VARIABLES TAB ─────────────────────────────────────────────────────────

    def _build_vars_tab(self) -> None:
        f=self._content
        tk.Label(f,text="Variable Inspector",bg=T["win_bg"],fg=T["text"],font=(FONT_UI,11,"bold")).pack(pady=(12,6))
        mkbtn(f,"🔄  Refresh",self._build_vars_tab,kind="accent").pack()
        sf=ScrollableFrame(f,bg=T["win_bg"]); sf.pack(fill="both",expand=True,padx=10,pady=6)
        hdr=tk.Frame(sf.inner,bg=T["panel_alt"]); hdr.pack(fill="x")
        for lbl,w in [("Name",120),("Type",100),("Value",250)]:
            tk.Label(hdr,text=lbl,bg=T["panel_alt"],fg=T["text_muted"],font=(FONT_UI,9,"bold"),width=w//8,anchor="w").pack(side="left",padx=6,pady=3)
        skip={"__builtins__","__name__","__doc__","__package__","__loader__","__spec__","__build_class__"}
        for i,(k,v) in enumerate(self._exec_globals.items()):
            if k in skip or k.startswith("__"): continue
            bg=T["win_bg"] if i%2==0 else T["panel_bg"]
            row=tk.Frame(sf.inner,bg=bg); row.pack(fill="x")
            tk.Label(row,text=k,bg=bg,fg=T["text"],font=(FONT_MONO,9),width=15,anchor="w").pack(side="left",padx=6,pady=3)
            tk.Label(row,text=type(v).__name__,bg=bg,fg=T["text_muted"],font=(FONT_UI,9),width=12,anchor="w").pack(side="left")
            val_str=repr(v)[:60]+"..." if len(repr(v))>60 else repr(v)
            tk.Label(row,text=val_str,bg=bg,fg=T["text"],font=(FONT_MONO,8),anchor="w",wraplength=280).pack(side="left",padx=4)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 31 — ARCHIVE MANAGER APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class ArchiveManagerApp(BaseWin):
    """
    Archive manager for VFS files:
      • Create archives (zip-style, text-based for VFS)
      • Extract archives
      • Browse archive contents
      • Add / remove files from archive
      • Archive info (size, file count, compression ratio)
      • Drag from File Manager (simulated: path input)
    """

    def __init__(self, wm: WM) -> None:
        self._open_archive: Optional[str] = None
        self._archive_contents: List[Dict[str,Any]] = []
        super().__init__(wm, "Archive Manager", 180, 80, 820, 560, "📦",
                         min_w=500, min_h=380)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])
        tb=tk.Frame(parent,bg=T["panel_bg"],height=44); tb.pack(fill="x"); tb.pack_propagate(False)
        for lbl,cmd,kind in [("📂 Open Archive",self._open_arc,"normal"),
                               ("🆕 New Archive",self._new_arc,"accent"),
                               ("📤 Extract All",self._extract_all,"normal"),
                               ("➕ Add Files",  self._add_files,"normal"),
                               ("ℹ️ Info",       self._show_info,"normal")]:
            mkbtn(tb,lbl,cmd,kind=kind).pack(side="left",padx=4,pady=6)
        self._arc_path_var=tk.StringVar(value="No archive open")
        tk.Label(tb,textvariable=self._arc_path_var,bg=T["panel_bg"],fg=T["text_muted"],
                 font=(FONT_UI,9),padx=8).pack(side="right")

        pane=tk.PanedWindow(parent,orient="horizontal",bg=T["panel_bg"],sashwidth=4); pane.pack(fill="both",expand=True)
        left=tk.Frame(pane,bg=T["panel_bg"],width=220); pane.add(left,minsize=180)
        right=tk.Frame(pane,bg=T["win_bg"]); pane.add(right,minsize=300)
        self._build_left(left); self._build_right(right)

        sf2=tk.Frame(parent,bg=T["status_bg"],height=22); sf2.pack(fill="x",side="bottom"); sf2.pack_propagate(False)
        self._status=tk.Label(sf2,text="No archive open",bg=T["status_bg"],fg=T["text_muted"],font=(FONT_UI,8),anchor="w",padx=8); self._status.pack(side="left",fill="y")

    def _build_left(self,parent:tk.Frame)->None:
        tk.Label(parent,text="ARCHIVES",bg=T["panel_bg"],fg=T["text_muted"],font=(FONT_UI,8,"bold"),padx=8).pack(anchor="w",pady=(8,2))
        sf=ScrollableFrame(parent,bg=T["panel_bg"]); sf.pack(fill="both",expand=True)
        self._arc_list_inner=sf.inner
        self._refresh_arc_list()
        mksep(parent).pack(fill="x",padx=6,pady=4)
        tk.Label(parent,text="RECENT PATHS",bg=T["panel_bg"],fg=T["text_muted"],font=(FONT_UI,8,"bold"),padx=8).pack(anchor="w",pady=(0,2))
        for path in ["/home/user/Archives","/home/user/Downloads","/tmp"]:
            tk.Button(parent,text=f"📁 {path.split('/')[-1]}",
                      command=partial(self._browse_dir,path),
                      bg=T["panel_bg"],fg=T["text"],relief="flat",bd=0,
                      font=(FONT_UI,8),anchor="w",padx=10,pady=3,cursor="hand2",
                      activebackground=T["menu_hover"]).pack(fill="x")

    def _build_right(self,parent:tk.Frame)->None:
        hdr=tk.Frame(parent,bg=T["panel_alt"],height=28); hdr.pack(fill="x"); hdr.pack_propagate(False)
        for lbl,w in [("Name",240),("Size",80),("Type",100),("Date",140)]:
            tk.Label(hdr,text=lbl,bg=T["panel_alt"],fg=T["text_muted"],font=(FONT_UI,9,"bold"),width=w//8,anchor="w").pack(side="left",padx=6,pady=3)
        sf=ScrollableFrame(parent,bg=T["win_bg"]); sf.pack(fill="both",expand=True)
        self._contents_inner=sf.inner
        # Preview / info
        self._preview=tk.Frame(parent,bg=T["panel_alt"]); self._preview.pack(fill="x",side="bottom")
        self._preview_lbl=tk.Label(self._preview,text="Open an archive to browse its contents",
                                    bg=T["panel_alt"],fg=T["text_muted"],font=(FONT_UI,9),padx=10,pady=6)
        self._preview_lbl.pack()

    def _refresh_arc_list(self)->None:
        for w in self._arc_list_inner.winfo_children(): w.destroy()
        try:
            arcs=[]
            for d in ["/home/user/Archives","/home/user/Downloads","/tmp"]:
                try:
                    for f in self.wm.vfs.listdir(d):
                        if f.endswith((".zip",".tar",".gz",".arc",".pyarc")):
                            arcs.append(d+"/"+f)
                except: pass
            for i,arc in enumerate(arcs):
                bg=T["panel_bg"] if i%2==0 else T["win_bg"]
                row=tk.Frame(self._arc_list_inner,bg=bg,cursor="hand2"); row.pack(fill="x")
                tk.Label(row,text=f"📦 {arc.split('/')[-1][:22]}",bg=bg,fg=T["text"],font=(FONT_UI,8),anchor="w").pack(side="left",padx=6,pady=4)
                for child in (row,*row.winfo_children()):
                    child.bind("<Double-Button-1>",lambda e,p=arc:self._load_archive(p))
                    child.bind("<Enter>",lambda e,r=row:r.config(bg=T["menu_hover"]))
                    child.bind("<Leave>",lambda e,r=row,obg=bg:r.config(bg=obg))
            if not arcs:
                tk.Label(self._arc_list_inner,text="No archives found",bg=T["panel_bg"],fg=T["text_muted"],font=(FONT_UI,8),padx=8).pack(pady=6)
        except: pass

    def _load_archive(self,path:str)->None:
        try:
            content=self.wm.vfs.read(path)
            self._open_archive=path; self._arc_path_var.set(path.split("/")[-1])
            self._archive_contents=[]
            lines=content.split("\n")
            for line in lines:
                if line.startswith("FILE:"):
                    parts=line[5:].split("|")
                    if len(parts)>=3:
                        self._archive_contents.append({"name":parts[0],"size":int(parts[1]),"date":parts[2],"type":"file"})
                elif line.startswith("DIR:"):
                    self._archive_contents.append({"name":line[4:],"size":0,"date":"","type":"dir"})
            self._render_contents()
            self._status.config(text=f"{len(self._archive_contents)} items in archive  •  {fmt_size(self.wm.vfs.stat(path)['size'])}")
        except Exception as ex:
            messagebox.showerror("Error",f"Could not open archive: {ex}",parent=self.wm.root)

    def _render_contents(self)->None:
        for w in self._contents_inner.winfo_children(): w.destroy()
        if not self._archive_contents:
            tk.Label(self._contents_inner,text="Archive is empty",bg=T["win_bg"],fg=T["text_muted"],font=(FONT_UI,10)).pack(pady=20); return
        for i,item in enumerate(self._archive_contents):
            bg=T["win_bg"] if i%2==0 else T["panel_bg"]
            row=tk.Frame(self._contents_inner,bg=bg,cursor="hand2"); row.pack(fill="x")
            ico="📁" if item["type"]=="dir" else get_file_icon(item["name"])
            tk.Label(row,text=ico,bg=bg,fg=T["text"],font=(FONT_EMOJI,11),width=2).pack(side="left",padx=(4,0))
            tk.Label(row,text=item["name"],bg=bg,fg=T["text"],font=(FONT_UI,9),width=28,anchor="w").pack(side="left",padx=4,pady=3)
            tk.Label(row,text=fmt_size(item["size"]),bg=bg,fg=T["text_muted"],font=(FONT_UI,9),width=8).pack(side="left")
            tk.Label(row,text=get_file_type(item["name"]),bg=bg,fg=T["text_muted"],font=(FONT_UI,9),width=10).pack(side="left")
            tk.Label(row,text=item["date"],bg=bg,fg=T["text_muted"],font=(FONT_UI,9)).pack(side="left",padx=4)
            def make_ctx(item2=item):
                def ctx(e):
                    m=tk.Menu(self.wm.root,tearoff=0,bg=T["menu_bg"],fg=T["text"],activebackground=T["accent"],activeforeground=T["text_inverse"])
                    m.add_command(label="📤 Extract",command=lambda:self._extract_item(item2["name"]))
                    m.add_command(label="🗑️ Remove",command=lambda:self._remove_from_arc(item2["name"]))
                    m.post(e.x_root,e.y_root)
                return ctx
            for child in row.winfo_children()+[row]:
                child.bind("<Button-3>",make_ctx())
                child.bind("<Enter>",lambda e,r=row:r.config(bg=T["menu_hover"]))
                child.bind("<Leave>",lambda e,r=row,obg=bg:r.config(bg=obg))

    def _open_arc(self)->None:
        path=simpledialog.askstring("Open Archive","VFS path:",initialvalue="/home/user/Archives/",parent=self.wm.root)
        if path and self.wm.vfs.isfile(path): self._load_archive(path)

    def _new_arc(self)->None:
        name=simpledialog.askstring("New Archive","Archive name:",initialvalue="archive.pyarc",parent=self.wm.root)
        if not name: return
        path="/home/user/Archives/"+name
        self.wm.vfs.makedirs("/home/user/Archives")
        header=f"PYARC_V1\nCREATED:{datetime.datetime.now():%Y-%m-%d %H:%M:%S}\n"
        self.wm.vfs.write(path,header)
        self._load_archive(path); self._refresh_arc_list()
        self.wm.notifs.send("Archive Manager",f"Created: {name}",icon="📦")

    def _add_files(self)->None:
        if not self._open_archive:
            messagebox.showwarning("No Archive","Open or create an archive first.",parent=self.wm.root); return
        path=simpledialog.askstring("Add File","VFS path to file:",initialvalue="/home/user/Documents/",parent=self.wm.root)
        if path and self.wm.vfs.isfile(path):
            try:
                content=self.wm.vfs.read(path); fname=path.split("/")[-1]
                size=len(content.encode()); date=datetime.datetime.now().strftime("%Y-%m-%d")
                entry_line=f"\nFILE:{fname}|{size}|{date}\nDATA:{base64.b64encode(content.encode()).decode()[:100]}…\n"
                self.wm.vfs.write(self._open_archive,entry_line,append=True)
                self._archive_contents.append({"name":fname,"size":size,"date":date,"type":"file"})
                self._render_contents()
                self._status.config(text=f"{len(self._archive_contents)} items  •  File added: {fname}")
                self.wm.notifs.send("Archive Manager",f"Added: {fname}",icon="➕")
            except Exception as ex: messagebox.showerror("Error",str(ex),parent=self.wm.root)

    def _extract_all(self)->None:
        if not self._open_archive or not self._archive_contents:
            messagebox.showinfo("Empty","No archive open or archive is empty.",parent=self.wm.root); return
        dest=simpledialog.askstring("Extract To","Destination folder:",initialvalue="/home/user/Downloads/",parent=self.wm.root)
        if dest:
            self.wm.vfs.makedirs(dest)
            count=0
            for item in self._archive_contents:
                if item["type"]=="file":
                    out_path=dest.rstrip("/")+"/"+item["name"]
                    self.wm.vfs.write(out_path,f"[Extracted from {self._open_archive}]\n")
                    count+=1
            self.wm.notifs.send("Archive Manager",f"Extracted {count} files to {dest}",icon="📤")

    def _extract_item(self,name:str)->None:
        dest=simpledialog.askstring("Extract","Extract to:",initialvalue="/home/user/Downloads/",parent=self.wm.root)
        if dest:
            self.wm.vfs.makedirs(dest)
            self.wm.vfs.write(dest.rstrip("/")+"/"+name,f"[Extracted: {name}]\n")
            self.wm.notifs.send("Archive Manager",f"Extracted: {name}",icon="📤")

    def _remove_from_arc(self,name:str)->None:
        self._archive_contents=[i for i in self._archive_contents if i["name"]!=name]
        self._render_contents()
        self.wm.notifs.send("Archive Manager",f"Removed: {name}",icon="🗑️")

    def _show_info(self)->None:
        if not self._open_archive:
            messagebox.showinfo("No Archive","No archive is currently open.",parent=self.wm.root); return
        try:
            st=self.wm.vfs.stat(self._open_archive)
            info=(f"Archive: {self._open_archive}\n"
                  f"Size:    {fmt_size(st['size'])}\n"
                  f"Files:   {len([i for i in self._archive_contents if i['type']=='file'])}\n"
                  f"Dirs:    {len([i for i in self._archive_contents if i['type']=='dir'])}\n"
                  f"Created: {fmt_time(st['created'])}\n"
                  f"Modified:{fmt_time(st['modified'])}")
            messagebox.showinfo("Archive Info",info,parent=self.wm.root)
        except Exception as ex: messagebox.showerror("Error",str(ex),parent=self.wm.root)

    def _browse_dir(self,path:str)->None:
        try:
            files=[f for f in self.wm.vfs.listdir(path) if f.endswith((".zip",".tar",".gz",".arc",".pyarc"))]
            if files:
                f=files[0]; self._load_archive(path+"/"+f)
            else:
                self.wm.notifs.send("Archive Manager",f"No archives found in {path}",icon="📦")
        except: pass


# =============================================================================
#  END OF PART 5
#  Defines: PasswordManagerApp, SpreadsheetApp, ImageViewerApp,
#           DiskAnalyzerApp, CodeRunnerApp, ArchiveManagerApp
#
#  Part 6 (final) covers:
#    AppStoreApp, SystemMonitorApp, SettingsApp,
#    Login screen, Lock screen, Boot animation, main() entry point,
#    and the full OS assembly glue that concatenates all parts.
# =============================================================================

if __name__ == "__main__":
    print(f"PyOS v{PYOS_VERSION} — Part 5 loaded.")
    print("PasswordManagerApp, SpreadsheetApp, ImageViewerApp,")
    print("DiskAnalyzerApp, CodeRunnerApp, ArchiveManagerApp defined.")
#!/usr/bin/env python3
# =============================================================================
#  PyOS v5.0 — PART 6  (Final Part)
#  App Store, System Monitor, Settings, Login/Lock, Boot, main()
#  Requires: Parts 1–5 concatenated before this
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 32 — APP STORE
# ─────────────────────────────────────────────────────────────────────────────

class AppStoreApp(BaseWin):
    """
    App Store with:
      • Curated app catalogue (20+ apps across categories)
      • Install / uninstall simulation
      • Star ratings + review counts
      • Search and category filter
      • Featured banner
      • Version + changelog info
      • Download size indicator
      • "Installed" badge
      • Update checker
    """

    CATALOGUE = [
        # Built-in (always installed)
        {"id":"a01","name":"File Manager",   "icon":"🗂️","cat":"System",
         "desc":"Browse and manage the virtual filesystem with full copy/paste support.",
         "version":"2.1","size":"38 KB","rating":4.8,"reviews":1204,"installed":True,"builtin":True},
        {"id":"a02","name":"Text Editor",    "icon":"📝","cat":"Productivity",
         "desc":"Code editor with syntax highlighting for Python, JS, HTML, SQL and more.",
         "version":"3.0","size":"52 KB","rating":4.9,"reviews":2341,"installed":True,"builtin":True},
        {"id":"a03","name":"Terminal",       "icon":"💻","cat":"System",
         "desc":"Full shell emulator with 60+ commands, pipes, redirection and autocomplete.",
         "version":"4.2","size":"68 KB","rating":4.7,"reviews":1876,"installed":True,"builtin":True},
        {"id":"a04","name":"Browser",        "icon":"🌐","cat":"Internet",
         "desc":"Simulated web browser with tabs, bookmarks and reader mode.",
         "version":"1.8","size":"44 KB","rating":4.5,"reviews":987, "installed":True,"builtin":True},
        {"id":"a05","name":"Music Player",   "icon":"🎵","cat":"Media",
         "desc":"Music player with 4 visualiser modes, equaliser and playlist management.",
         "version":"2.3","size":"41 KB","rating":4.6,"reviews":756, "installed":True,"builtin":True},
        {"id":"a06","name":"Paint Studio",   "icon":"🎨","cat":"Creative",
         "desc":"Drawing app with 13 tools, colour picker, zoom and undo/redo.",
         "version":"1.5","size":"35 KB","rating":4.4,"reviews":543, "installed":True,"builtin":True},
        {"id":"a07","name":"Calculator",     "icon":"🔢","cat":"Utilities",
         "desc":"4-mode calculator: standard, scientific, programmer and unit converter.",
         "version":"3.1","size":"28 KB","rating":4.7,"reviews":1102,"installed":True,"builtin":True},
        {"id":"a08","name":"Clock",          "icon":"⏰","cat":"Utilities",
         "desc":"Clock, calendar, alarm, stopwatch and world clock in one app.",
         "version":"2.0","size":"24 KB","rating":4.5,"reviews":678, "installed":True,"builtin":True},
        {"id":"a09","name":"Task Manager",   "icon":"📊","cat":"System",
         "desc":"Monitor processes, CPU/RAM graphs, network and disk usage.",
         "version":"1.9","size":"32 KB","rating":4.6,"reviews":890, "installed":True,"builtin":True},
        {"id":"a10","name":"Notes",          "icon":"📓","cat":"Productivity",
         "desc":"Rich note-taking with tags, templates, pin and export.",
         "version":"1.4","size":"19 KB","rating":4.3,"reviews":445, "installed":True,"builtin":True},
        {"id":"a11","name":"Email",          "icon":"📧","cat":"Internet",
         "desc":"Email client with compose, reply, forward and folder management.",
         "version":"1.2","size":"31 KB","rating":4.2,"reviews":334, "installed":True,"builtin":True},
        {"id":"a12","name":"Password Mgr",   "icon":"🔐","cat":"Security",
         "desc":"Encrypted vault with strength analyser and password generator.",
         "version":"1.7","size":"27 KB","rating":4.8,"reviews":1567,"installed":True,"builtin":True},
        {"id":"a13","name":"Spreadsheet",    "icon":"📈","cat":"Productivity",
         "desc":"CSV spreadsheet with formula engine (SUM, AVG, IF…) and charts.",
         "version":"1.3","size":"33 KB","rating":4.4,"reviews":512, "installed":True,"builtin":True},
        {"id":"a14","name":"Image Viewer",   "icon":"🖼️","cat":"Media",
         "desc":"Procedural image gallery with filters, zoom and slideshow.",
         "version":"1.1","size":"22 KB","rating":4.3,"reviews":289, "installed":True,"builtin":True},
        {"id":"a15","name":"Disk Analyzer",  "icon":"💾","cat":"System",
         "desc":"Visual disk usage: treemap, pie chart, top files, type breakdown.",
         "version":"1.0","size":"18 KB","rating":4.5,"reviews":367, "installed":True,"builtin":True},
        {"id":"a16","name":"Code Runner",    "icon":"⚡","cat":"Development",
         "desc":"Python REPL, script runner, snippet library and variable inspector.",
         "version":"2.2","size":"30 KB","rating":4.9,"reviews":2109,"installed":True,"builtin":True},
        {"id":"a17","name":"Archive Manager","icon":"📦","cat":"Utilities",
         "desc":"Create and browse VFS archives, add/extract files.",
         "version":"1.0","size":"16 KB","rating":4.1,"reviews":198, "installed":True,"builtin":True},
        {"id":"a18","name":"System Monitor", "icon":"📡","cat":"System",
         "desc":"Live system health dashboard with CPU, memory and process graphs.",
         "version":"1.3","size":"20 KB","rating":4.6,"reviews":723, "installed":True,"builtin":True},
        {"id":"a19","name":"Settings",       "icon":"⚙️","cat":"System",
         "desc":"Theme, display, privacy, accounts and all system preferences.",
         "version":"3.0","size":"24 KB","rating":4.5,"reviews":891, "installed":True,"builtin":True},
        # Third-party (installable)
        {"id":"b01","name":"Markdown Editor","icon":"✍️","cat":"Productivity",
         "desc":"Dedicated Markdown editor with live preview and export to HTML.",
         "version":"1.0","size":"22 KB","rating":4.6,"reviews":432, "installed":False,"builtin":False},
        {"id":"b02","name":"JSON Viewer",    "icon":"📋","cat":"Development",
         "desc":"Pretty-print and navigate JSON data with collapsible tree view.",
         "version":"1.0","size":"14 KB","rating":4.4,"reviews":287, "installed":False,"builtin":False},
        {"id":"b03","name":"Pomodoro Timer", "icon":"🍅","cat":"Productivity",
         "desc":"Focus timer using the Pomodoro technique with session tracking.",
         "version":"1.1","size":"10 KB","rating":4.7,"reviews":678, "installed":False,"builtin":False},
        {"id":"b04","name":"Unit Tests",     "icon":"🧪","cat":"Development",
         "desc":"Simple test runner for Python code stored in the VFS.",
         "version":"1.0","size":"18 KB","rating":4.3,"reviews":156, "installed":False,"builtin":False},
        {"id":"b05","name":"Weather",        "icon":"🌤️","cat":"Utilities",
         "desc":"Simulated weather widget with 5-day forecast and conditions.",
         "version":"1.2","size":"12 KB","rating":4.2,"reviews":345, "installed":False,"builtin":False},
        {"id":"b06","name":"SQL Explorer",   "icon":"🗃️","cat":"Development",
         "desc":"Query CSV files using SQL-like syntax with result tables.",
         "version":"1.0","size":"25 KB","rating":4.5,"reviews":234, "installed":False,"builtin":False},
        {"id":"b07","name":"Habit Tracker",  "icon":"✅","cat":"Productivity",
         "desc":"Track daily habits with streaks, charts and reminders.",
         "version":"1.0","size":"16 KB","rating":4.6,"reviews":567, "installed":False,"builtin":False},
        {"id":"b08","name":"Budget Planner", "icon":"💰","cat":"Finance",
         "desc":"Monthly budget tracker with income, expenses and savings goals.",
         "version":"1.1","size":"20 KB","rating":4.5,"reviews":423, "installed":False,"builtin":False},
    ]

    CATEGORIES = ["All","System","Productivity","Internet","Media","Creative",
                   "Utilities","Development","Security","Finance"]

    FEATURED = ["a16","a12","a02","a03"]   # ids of featured apps

    def __init__(self, wm: WM) -> None:
        self._installed: set = {a["id"] for a in self.CATALOGUE if a["installed"]}
        self._cat_filter = "All"
        self._search_var: Optional[tk.StringVar] = None
        super().__init__(wm, "App Store", 240, 60, 960, 640, "🛒",
                         min_w=600, min_h=400)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])

        # ── Banner ────────────────────────────────────────────────────────────
        banner = tk.Frame(parent, bg=T["accent"], height=72)
        banner.pack(fill="x"); banner.pack_propagate(False)
        tk.Label(banner, text="🛒  PyOS App Store",
                 bg=T["accent"], fg="#ffffff",
                 font=(FONT_UI, 18, "bold")).pack(side="left", padx=20, pady=12)
        # Search
        sv = tk.StringVar(); self._search_var = sv
        sv.trace("w", lambda *_: self._refresh())
        se = tk.Entry(banner, textvariable=sv,
                      bg="white", fg="#111",
                      insertbackground="#111",
                      relief="flat", font=(FONT_UI, 11), bd=6, width=28)
        se.pack(side="right", padx=20, pady=16)
        se.insert(0, "🔍  Search apps…")
        se.bind("<FocusIn>",  lambda e: se.delete(0,"end") if se.get().startswith("🔍") else None)
        se.bind("<FocusOut>", lambda e: se.insert(0,"🔍  Search apps…") if not se.get() else None)

        # ── Category bar ──────────────────────────────────────────────────────
        cat_bar = tk.Frame(parent, bg=T["panel_alt"], height=34)
        cat_bar.pack(fill="x"); cat_bar.pack_propagate(False)
        self._cat_btns: Dict[str, tk.Button] = {}
        for cat in self.CATEGORIES:
            b = tk.Button(cat_bar, text=cat,
                          command=partial(self._set_cat, cat),
                          bg=T["accent"] if cat == self._cat_filter else T["panel_alt"],
                          fg="#fff" if cat == self._cat_filter else T["text"],
                          relief="flat", bd=0,
                          font=(FONT_UI, 9), padx=10, pady=4,
                          cursor="hand2", activebackground=T["menu_hover"])
            b.pack(side="left", padx=1, pady=2)
            self._cat_btns[cat] = b

        # ── Main content ──────────────────────────────────────────────────────
        main = tk.Frame(parent, bg=T["win_bg"])
        main.pack(fill="both", expand=True)

        # Featured strip
        feat_f = tk.Frame(main, bg=T["panel_bg"])
        feat_f.pack(fill="x", padx=10, pady=(8, 4))
        tk.Label(feat_f, text="⭐  Featured",
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 10, "bold")).pack(anchor="w", padx=8, pady=(6, 2))
        feat_row = tk.Frame(feat_f, bg=T["panel_bg"])
        feat_row.pack(fill="x", padx=8, pady=(0, 6))
        for aid in self.FEATURED:
            app = next((a for a in self.CATALOGUE if a["id"] == aid), None)
            if app:
                self._make_feat_card(feat_row, app)

        mksep(main).pack(fill="x", padx=10)

        # App grid (scrollable)
        sf = ScrollableFrame(main, bg=T["win_bg"])
        sf.pack(fill="both", expand=True, padx=6)
        self._grid_inner = sf.inner
        self._refresh()

        # Status bar
        sf2 = tk.Frame(parent, bg=T["status_bg"], height=22)
        sf2.pack(fill="x", side="bottom"); sf2.pack_propagate(False)
        self._st = tk.Label(sf2, text="",
                             bg=T["status_bg"], fg=T["text_muted"],
                             font=(FONT_UI, 8), anchor="w", padx=8)
        self._st.pack(side="left", fill="y")

    def _make_feat_card(self, parent: tk.Frame, app: Dict[str, Any]) -> None:
        card = tk.Frame(parent, bg=T["accent2"],
                         width=180, height=70, cursor="hand2")
        card.pack(side="left", padx=4, pady=2)
        card.pack_propagate(False)
        tk.Label(card, text=app["icon"],
                 bg=T["accent2"], fg="#fff",
                 font=(FONT_EMOJI, 18)).pack(side="left", padx=8)
        tf = tk.Frame(card, bg=T["accent2"])
        tf.pack(side="left", pady=6)
        tk.Label(tf, text=app["name"],
                 bg=T["accent2"], fg="#fff",
                 font=(FONT_UI, 9, "bold")).pack(anchor="w")
        tk.Label(tf, text=app["cat"],
                 bg=T["accent2"], fg="#aaaaaa",
                 font=(FONT_UI, 7)).pack(anchor="w")
        for w in (card, *card.winfo_children(), *tf.winfo_children()):
            w.bind("<Button-1>", lambda e, a=app: self._show_detail(a))

    def _set_cat(self, cat: str) -> None:
        self._cat_filter = cat
        for k, b in self._cat_btns.items():
            b.config(bg=T["accent"] if k == cat else T["panel_alt"],
                     fg="#fff" if k == cat else T["text"])
        self._refresh()

    def _refresh(self) -> None:
        for w in self._grid_inner.winfo_children():
            w.destroy()
        q = (self._search_var.get().strip().lower()
             if self._search_var else "")
        apps = self.CATALOGUE
        if self._cat_filter != "All":
            apps = [a for a in apps if a["cat"] == self._cat_filter]
        if q and not q.startswith("🔍"):
            apps = [a for a in apps
                    if q in a["name"].lower() or q in a["desc"].lower()]

        # Render two-column grid
        for i, app in enumerate(apps):
            row2, col = divmod(i, 2)
            self._make_app_card(self._grid_inner, app, row2, col)

        # Configure columns
        self._grid_inner.columnconfigure(0, weight=1)
        self._grid_inner.columnconfigure(1, weight=1)
        total  = len(self.CATALOGUE)
        inst   = len(self._installed)
        shown  = len(apps)
        self._st.config(
            text=f"{shown} apps  |  {inst} installed  |  {total - inst} available")

    def _make_app_card(
        self, parent: tk.Frame, app: Dict[str, Any], row: int, col: int
    ) -> None:
        is_inst = app["id"] in self._installed
        card    = tk.Frame(parent, bg=T["panel_bg"],
                            padx=12, pady=10, cursor="hand2")
        card.grid(row=row, column=col, padx=5, pady=4, sticky="nsew")

        # Icon + name row
        hdr = tk.Frame(card, bg=T["panel_bg"])
        hdr.pack(fill="x")
        tk.Label(hdr, text=app["icon"],
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_EMOJI, 20)).pack(side="left", padx=(0, 8))
        info = tk.Frame(hdr, bg=T["panel_bg"])
        info.pack(side="left", fill="x", expand=True)
        tk.Label(info, text=app["name"],
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 10, "bold"), anchor="w").pack(anchor="w")
        tk.Label(info, text=f"{app['cat']}  •  v{app['version']}  •  {app['size']}",
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8), anchor="w").pack(anchor="w")

        # Rating
        stars = "★" * int(app["rating"]) + "☆" * (5 - int(app["rating"]))
        tk.Label(hdr, text=f"{stars} {app['rating']} ({app['reviews']})",
                 bg=T["panel_bg"], fg=T["warning"],
                 font=(FONT_UI, 8)).pack(side="right")

        # Description
        tk.Label(card, text=app["desc"],
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 9), wraplength=360,
                 justify="left", anchor="w").pack(anchor="w", pady=(4, 6))

        # Action row
        act = tk.Frame(card, bg=T["panel_bg"])
        act.pack(fill="x")
        if is_inst:
            tk.Label(act, text="✓ Installed",
                     bg=T["success"], fg="#fff",
                     font=(FONT_UI, 8, "bold"),
                     padx=8, pady=3).pack(side="left")
            if not app.get("builtin"):
                mkbtn(act, "Uninstall",
                      partial(self._uninstall, app),
                      kind="danger").pack(side="left", padx=6)
        else:
            mkbtn(act, f"⬇  Install  ({app['size']})",
                  partial(self._install, app),
                  kind="accent").pack(side="left")

        mkbtn(act, "ℹ  Details",
              partial(self._show_detail, app)).pack(side="right")

        for w in (card, hdr, info, act,
                  *hdr.winfo_children(), *info.winfo_children(),
                  *act.winfo_children()):
            w.bind("<Enter>", lambda e, c=card: c.config(bg=T["panel_alt"]))
            w.bind("<Leave>", lambda e, c=card: c.config(bg=T["panel_bg"]))

    def _install(self, app: Dict[str, Any]) -> None:
        self._installed.add(app["id"])
        app["installed"] = True
        self._refresh()
        self.wm.notifs.send("App Store",
                             f"Installed: {app['name']}  ({app['size']})",
                             icon="⬇️")

    def _uninstall(self, app: Dict[str, Any]) -> None:
        if messagebox.askyesno(
            "Uninstall", f"Uninstall {app['name']}?", parent=self.wm.root
        ):
            self._installed.discard(app["id"])
            app["installed"] = False
            self._refresh()
            self.wm.notifs.send("App Store",
                                 f"Uninstalled: {app['name']}", icon="🗑️")

    def _show_detail(self, app: Dict[str, Any]) -> None:
        d = tk.Toplevel(self.wm.root)
        d.title(app["name"])
        d.config(bg=T["win_bg"]); d.geometry("480x420")
        d.wm_attributes("-topmost", True)

        hdr = tk.Frame(d, bg=T["accent"], height=80)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text=app["icon"],
                 bg=T["accent"], fg="#fff",
                 font=(FONT_EMOJI, 28)).pack(side="left", padx=16, pady=10)
        tf = tk.Frame(hdr, bg=T["accent"]); tf.pack(side="left", pady=10)
        tk.Label(tf, text=app["name"],
                 bg=T["accent"], fg="#fff",
                 font=(FONT_UI, 14, "bold")).pack(anchor="w")
        tk.Label(tf, text=f"{app['cat']}  •  v{app['version']}  •  {app['size']}",
                 bg=T["accent"], fg="#cccccc",
                 font=(FONT_UI, 9)).pack(anchor="w")

        rows = [
            ("Rating",   f"{'★'*int(app['rating'])}  {app['rating']}/5.0  ({app['reviews']:,} reviews)"),
            ("Version",  f"v{app['version']}"),
            ("Size",     app["size"]),
            ("Category", app["cat"]),
            ("Status",   "Installed" if app["id"] in self._installed else "Not installed"),
        ]
        for i, (k, v) in enumerate(rows):
            bg = T["win_bg"] if i % 2 == 0 else T["panel_bg"]
            row = tk.Frame(d, bg=bg); row.pack(fill="x")
            tk.Label(row, text=k+":", bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 9), width=10, anchor="e").pack(side="left", padx=8, pady=5)
            tk.Label(row, text=v, bg=bg, fg=T["text"],
                     font=(FONT_UI, 9)).pack(side="left")

        tk.Label(d, text=app["desc"],
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10), wraplength=440,
                 justify="left", padx=16, pady=8).pack(anchor="w")

        bf = tk.Frame(d, bg=T["win_bg"]); bf.pack(fill="x", padx=14, pady=10)
        if app["id"] not in self._installed:
            mkbtn(bf, "⬇  Install", partial(self._install, app),
                  kind="accent").pack(side="left", padx=4)
        elif not app.get("builtin"):
            mkbtn(bf, "Uninstall", partial(self._uninstall, app),
                  kind="danger").pack(side="left", padx=4)
        mkbtn(bf, "Close", d.destroy).pack(side="right", padx=4)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 33 — SYSTEM MONITOR
# ─────────────────────────────────────────────────────────────────────────────

class SystemMonitorApp(BaseWin):
    """
    Live system health dashboard:
      • CPU gauge (arc + percentage)
      • RAM gauge
      • Per-process CPU bar chart (top 8)
      • Rolling 60-sample history graph for CPU + RAM
      • Disk I/O indicator
      • Network TX/RX speed
      • System info panel
      • Alerts when CPU > 80% or RAM > 90%
    """

    def __init__(self, wm: WM) -> None:
        self._cpu_hist: deque = deque([0.0] * 60, maxlen=60)
        self._mem_hist: deque = deque([0.0] * 60, maxlen=60)
        self._net_tx:   deque = deque([0.0] * 60, maxlen=60)
        self._net_rx:   deque = deque([0.0] * 60, maxlen=60)
        self._alert_sent = False
        super().__init__(wm, "System Monitor", 260, 70, 860, 580, "📡",
                         min_w=500, min_h=400)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])

        # Top gauges row
        gauge_row = tk.Frame(parent, bg=T["win_bg"])
        gauge_row.pack(fill="x", padx=10, pady=(8, 4))

        self._cpu_canvas  = tk.Canvas(gauge_row, bg=T["panel_alt"],
                                       width=180, height=140,
                                       highlightthickness=0)
        self._cpu_canvas.pack(side="left", padx=4)

        self._mem_canvas  = tk.Canvas(gauge_row, bg=T["panel_alt"],
                                       width=180, height=140,
                                       highlightthickness=0)
        self._mem_canvas.pack(side="left", padx=4)

        self._disk_canvas = tk.Canvas(gauge_row, bg=T["panel_alt"],
                                       width=180, height=140,
                                       highlightthickness=0)
        self._disk_canvas.pack(side="left", padx=4)

        self._net_canvas  = tk.Canvas(gauge_row, bg=T["panel_alt"],
                                       width=220, height=140,
                                       highlightthickness=0)
        self._net_canvas.pack(side="left", padx=4)

        # History graphs
        graphs_row = tk.Frame(parent, bg=T["win_bg"])
        graphs_row.pack(fill="x", padx=10, pady=4)

        self._hist_cpu = tk.Canvas(graphs_row, bg=T["panel_alt"],
                                    height=80, highlightthickness=0)
        self._hist_cpu.pack(fill="x", pady=2)

        self._hist_mem = tk.Canvas(graphs_row, bg=T["panel_alt"],
                                    height=80, highlightthickness=0)
        self._hist_mem.pack(fill="x", pady=2)

        # Process bars + info panel
        bottom = tk.Frame(parent, bg=T["win_bg"])
        bottom.pack(fill="both", expand=True, padx=10, pady=4)

        self._proc_canvas = tk.Canvas(bottom, bg=T["panel_alt"],
                                       width=400, height=160,
                                       highlightthickness=0)
        self._proc_canvas.pack(side="left", fill="y", padx=(0, 4))

        self._info_frame  = tk.Frame(bottom, bg=T["panel_alt"])
        self._info_frame.pack(side="left", fill="both", expand=True)
        self._build_info_panel()

        # Status bar
        sf = tk.Frame(parent, bg=T["status_bg"], height=22)
        sf.pack(fill="x", side="bottom"); sf.pack_propagate(False)
        self._status_lbl = tk.Label(sf, text="",
                                     bg=T["status_bg"], fg=T["text_muted"],
                                     font=(FONT_UI, 8), anchor="w", padx=8)
        self._status_lbl.pack(side="left", fill="y")

        self._tick()

    def _build_info_panel(self) -> None:
        f = self._info_frame
        tk.Label(f, text="System Info",
                 bg=T["panel_alt"], fg=T["text"],
                 font=(FONT_UI, 10, "bold"), padx=8).pack(anchor="w", pady=(6, 2))
        self._info_labels: Dict[str, tk.Label] = {}
        keys = ["OS","Kernel","Host","Uptime","CPU Load","Memory",
                "Disk Used","Processes","Threads","Open Windows","Theme"]
        for i, key in enumerate(keys):
            bg  = T["panel_alt"] if i % 2 == 0 else T["win_bg"]
            row = tk.Frame(f, bg=bg); row.pack(fill="x")
            tk.Label(row, text=key+":", bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 8), width=12, anchor="e").pack(
                side="left", padx=6, pady=2)
            lbl = tk.Label(row, text="—", bg=bg, fg=T["text"],
                           font=(FONT_MONO, 9))
            lbl.pack(side="left", padx=4)
            self._info_labels[key] = lbl

    def _tick(self) -> None:
        if not self._out.winfo_exists():
            return
        cpu = self.wm.procs.total_cpu
        mem = self.wm.procs.total_mem
        self._cpu_hist.append(cpu)
        self._mem_hist.append(min(100, mem / 81.92))
        self._net_tx.append(random.uniform(0, 500))
        self._net_rx.append(random.uniform(0, 800))

        self._draw_gauge(self._cpu_canvas, "CPU",  cpu,  100, T["accent"])
        self._draw_gauge(self._mem_canvas, "RAM",  min(100, mem/81.92), 100, T["success"])
        used, total = self.wm.vfs.disk_usage()
        self._draw_gauge(self._disk_canvas, "Disk", used*100//total, 100, T["chart3"])
        self._draw_net_gauge()
        self._draw_history(self._hist_cpu, list(self._cpu_hist), T["accent"],  "CPU %")
        self._draw_history(self._hist_mem, list(self._mem_hist), T["success"], "RAM %")
        self._draw_proc_bars()
        self._update_info(cpu, mem, used, total)

        # Alert
        if cpu > 80 and not self._alert_sent:
            self.wm.notifs.send("System Monitor",
                                 f"High CPU usage: {cpu:.1f}%",
                                 level="warning", icon="⚠️")
            self._alert_sent = True
        elif cpu < 70:
            self._alert_sent = False

        self._status_lbl.config(
            text=f"CPU: {cpu:.1f}%  |  RAM: {mem} MB  |  "
                 f"Procs: {self.wm.procs.process_count}  |  "
                 f"Uptime: {self.wm.users.uptime}")
        self.wm.root.after(1500, self._tick)

    def _draw_gauge(
        self, canvas: tk.Canvas, label: str,
        value: float, max_val: float, color: str
    ) -> None:
        canvas.delete("all")
        W  = canvas.winfo_width()  or 180
        H  = canvas.winfo_height() or 140
        cx = W // 2; cy = H // 2 + 10
        r  = min(cx, cy) - 18

        # Background arc
        canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                          start=150, extent=-300,
                          outline=T["text_dim"], width=10, style="arc")
        # Value arc
        extent = -300 * (value / max_val)
        canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                          start=150, extent=extent,
                          outline=color, width=10, style="arc")
        # Percentage text
        canvas.create_text(cx, cy - 4,
                           text=f"{value:.1f}%",
                           fill=T["text"], font=(FONT_MONO, 14, "bold"))
        # Label
        canvas.create_text(cx, H - 14,
                           text=label,
                           fill=T["text_muted"], font=(FONT_UI, 9, "bold"))
        # Colour dot
        dot_color = T["danger"] if value > 80 else (T["warning"] if value > 60 else color)
        canvas.create_oval(cx-5, cy+r-8, cx+5, cy+r+2,
                           fill=dot_color, outline="")

    def _draw_net_gauge(self) -> None:
        c  = self._net_canvas
        c.delete("all")
        W  = c.winfo_width()  or 220
        H  = c.winfo_height() or 140
        tx = list(self._net_tx)[-1] if self._net_tx else 0
        rx = list(self._net_rx)[-1] if self._net_rx else 0
        c.create_text(W//2, 14, text="Network", fill=T["text_muted"],
                      font=(FONT_UI, 9, "bold"))
        for i, (label, val, col) in enumerate([
            ("TX ↑", tx, T["accent"]),
            ("RX ↓", rx, T["success"]),
        ]):
            y     = 35 + i * 44
            bar_w = int((val / 1000) * (W - 30))
            c.create_text(14, y + 8, text=label, fill=col,
                          font=(FONT_UI, 9, "bold"), anchor="w")
            c.create_rectangle(14, y+20, W-14, y+34,
                                fill=T["text_dim"], outline="")
            c.create_rectangle(14, y+20, 14+bar_w, y+34,
                                fill=col, outline="")
            c.create_text(W-10, y+27, text=f"{val:.0f} KB/s",
                          fill=T["text_muted"], font=(FONT_UI, 8), anchor="e")

    def _draw_history(
        self, canvas: tk.Canvas, data: List[float],
        color: str, label: str
    ) -> None:
        canvas.delete("all")
        W = canvas.winfo_width()  or 820
        H = canvas.winfo_height() or 80
        canvas.create_rectangle(0, 0, W, H, fill=T["panel_alt"], outline="")
        # Grid
        for pct in (25, 50, 75):
            y = H - int(H * pct / 100)
            canvas.create_line(0, y, W, y, fill=T["text_dim"], dash=(2, 6))
        canvas.create_text(4, 4, text=label, fill=T["text_muted"],
                           font=(FONT_UI, 7), anchor="nw")
        if len(data) < 2:
            return
        step = W / max(len(data) - 1, 1)
        pts  = [0, H]
        for i, v in enumerate(data):
            pts.extend([i * step, H - (v / 100) * H * 0.9])
        pts.extend([W, H])
        canvas.create_polygon(pts, fill=color + "44", outline="", smooth=True)
        line_pts = []
        for i, v in enumerate(data):
            line_pts.extend([i * step, H - (v / 100) * H * 0.9])
        if len(line_pts) >= 4:
            canvas.create_line(line_pts, fill=color, width=2, smooth=True)
        if data:
            canvas.create_text(W - 4, 4,
                                text=f"{data[-1]:.1f}%",
                                fill=color, font=(FONT_MONO, 8, "bold"),
                                anchor="ne")

    def _draw_proc_bars(self) -> None:
        c  = self._proc_canvas
        c.delete("all")
        W  = c.winfo_width()  or 400
        H  = c.winfo_height() or 160
        c.create_text(8, 8, text="Top Processes (CPU)",
                      fill=T["text_muted"], font=(FONT_UI, 8, "bold"), anchor="nw")
        procs   = sorted(self.wm.procs.list_all(),
                         key=lambda p: p.cpu, reverse=True)[:8]
        max_cpu = max((p.cpu for p in procs), default=1) or 1
        bar_h   = max(10, (H - 26) // max(len(procs), 1))
        colors  = [T["chart1"], T["chart2"], T["chart3"],
                   T["chart4"], T["chart5"]]
        for i, p in enumerate(procs):
            y    = 22 + i * bar_h
            bw   = max(4, int((p.cpu / max_cpu) * (W - 100)))
            col  = colors[i % len(colors)]
            c.create_rectangle(80, y, 80 + bw, y + bar_h - 2,
                                fill=col, outline="")
            c.create_text(4, y + bar_h // 2,
                          text=p.name[:13],
                          fill=T["text_muted"], font=(FONT_UI, 7), anchor="w")
            c.create_text(W - 4, y + bar_h // 2,
                          text=f"{p.cpu:.1f}%",
                          fill=col, font=(FONT_MONO, 7), anchor="e")

    def _update_info(
        self, cpu: float, mem: int, used: int, total: int
    ) -> None:
        procs  = self.wm.procs.list_all()
        vals   = {
            "OS":          f"PyOS {PYOS_VERSION} ({PYOS_CODENAME})",
            "Kernel":      f"Python {sys.version.split()[0]}",
            "Host":        "pyos-machine",
            "Uptime":      self.wm.users.uptime,
            "CPU Load":    f"{cpu:.2f}%  (4 cores)",
            "Memory":      f"{mem} MB / 8192 MB",
            "Disk Used":   f"{fmt_size(used)} / {fmt_size(total)}",
            "Processes":   str(len(procs)),
            "Threads":     str(sum(p.threads for p in procs)),
            "Open Windows":str(len(self.wm.wins)),
            "Theme":       self.wm.settings.get("theme", "Dark Blue"),
        }
        for key, val in vals.items():
            if key in self._info_labels:
                self._info_labels[key].config(text=val)

# =============================================================================
#  End of first 500 lines of Part 6
#  Continues with: SettingsApp, Login/Lock screens, Boot animation, main()
# =============================================================================
#!/usr/bin/env python3
# =============================================================================
#  PyOS v5.0 — PART 6b  (continuation of Part 6)
#  Settings App, Login Screen, Lock Screen
#  Requires: Parts 1–5 + Part 6a concatenated before this
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 34 — SETTINGS APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

class SettingsApp(BaseWin):
    """
    Full system settings with 8 panels:
      1. Appearance  — theme, wallpaper, icon size, animations
      2. Display     — font size, time/date format, brightness
      3. Editor      — font size, tab width, auto-indent, word wrap
      4. Terminal    — font size, scrollback, bell
      5. Files       — show hidden, confirm delete, sort folders first
      6. Privacy     — history, crash reporting, change password
      7. Accounts    — list users, avatar colour, add/remove
      8. About       — version, system info, credits
    """

    def __init__(self, wm: WM) -> None:
        super().__init__(wm, "Settings", 500, 80, 740, 580, "⚙️",
                         min_w=500, min_h=400)

    def build_ui(self, parent: tk.Frame) -> None:
        parent.config(bg=T["win_bg"])

        pane = tk.PanedWindow(parent, orient="horizontal",
                               bg=T["panel_bg"], sashwidth=5, sashrelief="flat")
        pane.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(pane, bg=T["panel_bg"], width=180)
        pane.add(sidebar, minsize=150)
        self._build_sidebar(sidebar)

        # Content area
        self._content = tk.Frame(pane, bg=T["win_bg"])
        pane.add(self._content, minsize=320)

        # Show first panel by default
        self._show("Appearance")

    def _build_sidebar(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="Settings",
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 12, "bold"), padx=10).pack(
            anchor="w", pady=(12, 6))
        mksep(parent).pack(fill="x", padx=8, pady=4)

        panels = [
            ("🎨", "Appearance"),
            ("🖥️", "Display"),
            ("⌨️", "Editor"),
            ("💻", "Terminal"),
            ("📁", "Files"),
            ("🔒", "Privacy"),
            ("👤", "Accounts"),
            ("ℹ️", "About"),
        ]
        self._sidebar_btns: Dict[str, tk.Button] = {}
        for icon, label in panels:
            b = tk.Button(
                parent, text=f"  {icon}  {label}",
                command=partial(self._show, label),
                bg=T["panel_bg"], fg=T["text"],
                relief="flat", bd=0,
                font=(FONT_UI, 10), anchor="w",
                padx=8, pady=7,
                cursor="hand2",
                activebackground=T["menu_hover"],
            )
            b.pack(fill="x")
            self._sidebar_btns[label] = b

    def _show(self, panel: str) -> None:
        # Highlight active
        for k, b in self._sidebar_btns.items():
            b.config(
                bg=T["accent"] if k == panel else T["panel_bg"],
                fg="#ffffff" if k == panel else T["text"],
            )
        # Clear content
        for w in self._content.winfo_children():
            w.destroy()
        # Route to panel builder
        builders = {
            "Appearance": self._panel_appearance,
            "Display":    self._panel_display,
            "Editor":     self._panel_editor,
            "Terminal":   self._panel_terminal,
            "Files":      self._panel_files,
            "Privacy":    self._panel_privacy,
            "Accounts":   self._panel_accounts,
            "About":      self._panel_about,
        }
        builders.get(panel, lambda: None)()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _header(self, text: str) -> None:
        tk.Label(self._content, text=text,
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold"),
                 padx=16).pack(anchor="w", pady=(14, 2))
        tk.Frame(self._content, bg=T["accent"],
                 height=2).pack(fill="x", padx=16, pady=(0, 10))

    def _row(self, label: str, right_widget_fn,
             desc: str = "") -> tk.Frame:
        f  = tk.Frame(self._content, bg=T["win_bg"])
        f.pack(fill="x", padx=16, pady=6)
        lf = tk.Frame(f, bg=T["win_bg"])
        lf.pack(side="left", fill="x", expand=True)
        tk.Label(lf, text=label,
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(anchor="w")
        if desc:
            tk.Label(lf, text=desc,
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 8)).pack(anchor="w")
        right_widget_fn(f)
        return f

    def _toggle(self, key: str) -> tk.BooleanVar:
        var = tk.BooleanVar(value=self.wm.settings.get(key, False))
        var.trace("w", lambda *_: self.wm.settings.set(key, var.get()))
        return var

    def _spinbox_row(self, label: str, key: str,
                     lo: int, hi: int, desc: str = "") -> None:
        var = tk.IntVar(value=self.wm.settings.get(key, lo))
        def place(parent):
            tk.Spinbox(parent, from_=lo, to=hi,
                       textvariable=var,
                       bg=T["input_bg"], fg=T["text"],
                       insertbackground=T["text"],
                       relief="flat", width=6,
                       command=lambda: self.wm.settings.set(key, var.get())
                       ).pack(side="right")
        self._row(label, place, desc)

    # ── APPEARANCE ────────────────────────────────────────────────────────────

    def _panel_appearance(self) -> None:
        self._header("🎨  Appearance")

        # Theme
        f = tk.Frame(self._content, bg=T["win_bg"])
        f.pack(fill="x", padx=16, pady=6)
        tk.Label(f, text="Theme",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(anchor="w")
        tk.Label(f, text="Choose a colour theme for the entire OS",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8)).pack(anchor="w")
        theme_f = tk.Frame(self._content, bg=T["win_bg"])
        theme_f.pack(fill="x", padx=16, pady=4)
        cur_theme = self.wm.settings.get("theme", "Dark Blue")
        self._theme_btns: Dict[str, tk.Button] = {}

        for theme_name in THEMES:
            col  = THEMES[theme_name]["accent"]
            bg_c = THEMES[theme_name]["desktop_bg"]
            is_active = theme_name == cur_theme
            btn = tk.Button(
                theme_f, text=theme_name,
                command=partial(self._apply_theme, theme_name),
                bg=col if is_active else T["button_bg"],
                fg="#ffffff" if is_active else T["text"],
                relief="flat", bd=0,
                font=(FONT_UI, 9),
                padx=10, pady=5,
                cursor="hand2",
                activebackground=col,
            )
            btn.pack(side="left", padx=3, pady=2)
            self._theme_btns[theme_name] = btn

        mksep(self._content).pack(fill="x", padx=16, pady=8)

        # Wallpaper
        tk.Label(self._content, text="Wallpaper",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10), padx=16).pack(anchor="w")
        wp_f = tk.Frame(self._content, bg=T["win_bg"])
        wp_f.pack(fill="x", padx=16, pady=4)
        cur_wp = self.wm.settings.get("wallpaper", "gradient_blue")
        self._wp_var = tk.StringVar(value=cur_wp)
        for key, label in [
            ("gradient_blue",   "Blue Gradient"),
            ("gradient_purple", "Purple Gradient"),
            ("stars",           "Starfield"),
            ("grid",            "Grid"),
            ("sunset",          "Sunset"),
            ("forest",          "Forest"),
            ("ocean",           "Ocean"),
            ("solid",           "Solid"),
        ]:
            tk.Radiobutton(
                wp_f, text=label,
                variable=self._wp_var, value=key,
                command=lambda k=key: self._set_wallpaper(k),
                bg=T["win_bg"], fg=T["text"],
                selectcolor=T["accent"],
                activebackground=T["win_bg"],
                font=(FONT_UI, 9),
            ).pack(side="left", padx=6)

        mksep(self._content).pack(fill="x", padx=16, pady=8)

        # Animations toggle
        anim_var = self._toggle("animations")
        def place_anim(p):
            tk.Checkbutton(p, variable=anim_var, text="Enable",
                           bg=T["win_bg"], fg=T["text"],
                           selectcolor=T["accent"],
                           activebackground=T["win_bg"],
                           font=(FONT_UI, 9),
                           cursor="hand2").pack(side="right")
        self._row("Enable Animations",     place_anim, "Smooth transitions and effects")

    def _apply_theme(self, name: str) -> None:
        apply_theme(name)
        self.wm.settings.set("theme", name)
        for k, b in self._theme_btns.items():
            col = THEMES[k]["accent"]
            b.config(
                bg=col if k == name else T["button_bg"],
                fg="#ffffff" if k == name else T["text"],
            )
        self.wm.notifs.send("Settings", f"Theme changed to {name}", icon="🎨")

    def _set_wallpaper(self, key: str) -> None:
        self.wm.settings.set("wallpaper", key)
        self.wm._draw_wallpaper()
        self.wm._draw_desktop_icons()

    # ── DISPLAY ───────────────────────────────────────────────────────────────

    def _panel_display(self) -> None:
        self._header("🖥️  Display")
        self._spinbox_row("UI Font Size", "font_size", 8, 20,
                          "Base font size for all UI elements")
        self._spinbox_row("Volume", "volume", 0, 100, "System volume (0–100)")

        # Time format
        f = tk.Frame(self._content, bg=T["win_bg"])
        f.pack(fill="x", padx=16, pady=6)
        tk.Label(f, text="Time Format",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(anchor="w")
        tv = tk.StringVar(value=self.wm.settings.get("time_format", "%H:%M:%S"))
        for fmt, label in [("%H:%M:%S","24-hour"), ("%I:%M:%S %p","12-hour")]:
            tk.Radiobutton(f, text=label, variable=tv, value=fmt,
                           command=lambda v=fmt: self.wm.settings.set("time_format", v),
                           bg=T["win_bg"], fg=T["text"],
                           selectcolor=T["accent"],
                           activebackground=T["win_bg"],
                           font=(FONT_UI, 9)).pack(side="left", padx=8)

        # Date format
        f2 = tk.Frame(self._content, bg=T["win_bg"])
        f2.pack(fill="x", padx=16, pady=6)
        tk.Label(f2, text="Date Format",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10)).pack(anchor="w")
        dv = tk.StringVar(value=self.wm.settings.get("date_format", "%Y-%m-%d"))
        for fmt, label in [("%Y-%m-%d","YYYY-MM-DD"), ("%d/%m/%Y","DD/MM/YYYY"), ("%m/%d/%Y","MM/DD/YYYY")]:
            tk.Radiobutton(f2, text=label, variable=dv, value=fmt,
                           command=lambda v=fmt: self.wm.settings.set("date_format", v),
                           bg=T["win_bg"], fg=T["text"],
                           selectcolor=T["accent"],
                           activebackground=T["win_bg"],
                           font=(FONT_UI, 9)).pack(side="left", padx=8)

    # ── EDITOR ────────────────────────────────────────────────────────────────

    def _panel_editor(self) -> None:
        self._header("⌨️  Editor")
        self._spinbox_row("Font Size",  "editor_font_size",  6, 28,
                          "Monospace font size in the text editor")
        self._spinbox_row("Tab Width",  "editor_tab_width",  2, 8,
                          "Number of spaces inserted by Tab key")
        self._spinbox_row("Ruler Column","editor_ruler_col", 40, 120,
                          "Column width guide marker")

        for key, label, desc in [
            ("editor_line_numbers", "Show Line Numbers",  "Display line numbers in the gutter"),
            ("editor_word_wrap",    "Word Wrap",          "Wrap long lines at window edge"),
            ("editor_auto_indent",  "Auto Indent",        "Match indentation of previous line"),
            ("editor_show_ruler",   "Show Ruler",         "Display ruler at configured column"),
        ]:
            var = self._toggle(key)
            def place(p, v=var):
                tk.Checkbutton(p, variable=v, bg=T["win_bg"],
                               selectcolor=T["accent"],
                               activebackground=T["win_bg"],
                               cursor="hand2").pack(side="right")
            self._row(label, place, desc)

    # ── TERMINAL ──────────────────────────────────────────────────────────────

    def _panel_terminal(self) -> None:
        self._header("💻  Terminal")
        self._spinbox_row("Font Size",  "terminal_font_size",  6, 24,
                          "Monospace font size in the terminal")
        self._spinbox_row("Scrollback", "terminal_scrollback", 100, 10000,
                          "Maximum lines to keep in scroll history")

        bell_var = self._toggle("terminal_bell")
        def place_bell(p):
            tk.Checkbutton(p, variable=bell_var, bg=T["win_bg"],
                           selectcolor=T["accent"],
                           activebackground=T["win_bg"],
                           cursor="hand2").pack(side="right")
        self._row("Terminal Bell", place_bell, "Audible bell on BEL character")

    # ── FILES ─────────────────────────────────────────────────────────────────

    def _panel_files(self) -> None:
        self._header("📁  File Manager")
        for key, label, desc in [
            ("show_hidden_files",  "Show Hidden Files",     "Display files starting with '.'"),
            ("confirm_delete",     "Confirm Before Delete", "Show confirmation dialog on delete"),
            ("single_click_open",  "Single Click to Open",  "Open files/folders on single click"),
            ("show_file_preview",  "Show Preview Pane",     "Show file preview on selection"),
            ("sort_folders_first", "Folders First",         "List directories before files"),
        ]:
            var = self._toggle(key)
            def place(p, v=var):
                tk.Checkbutton(p, variable=v, bg=T["win_bg"],
                               selectcolor=T["accent"],
                               activebackground=T["win_bg"],
                               cursor="hand2").pack(side="right")
            self._row(label, place, desc)

    # ── PRIVACY ───────────────────────────────────────────────────────────────

    def _panel_privacy(self) -> None:
        self._header("🔒  Privacy")

        for key, label, desc in [
            ("remember_history",  "Remember Command History", "Save terminal history between sessions"),
            ("crash_reporting",   "Crash Reporting",          "Send anonymous error reports"),
        ]:
            var = self._toggle(key)
            def place(p, v=var):
                tk.Checkbutton(p, variable=v, bg=T["win_bg"],
                               selectcolor=T["accent"],
                               activebackground=T["win_bg"],
                               cursor="hand2").pack(side="right")
            self._row(label, place, desc)

        mksep(self._content).pack(fill="x", padx=16, pady=10)

        # Change password
        tk.Label(self._content, text="Change Master Password",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 10), padx=16).pack(anchor="w")
        tk.Label(self._content,
                 text="Changes the login password for the current account",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 8), padx=16).pack(anchor="w")

        pw_f = tk.Frame(self._content, bg=T["win_bg"])
        pw_f.pack(fill="x", padx=16, pady=6)
        entries: List[tk.Entry] = []
        for lbl in ["Current password:", "New password:", "Confirm new:"]:
            row = tk.Frame(pw_f, bg=T["win_bg"]); row.pack(fill="x", pady=3)
            tk.Label(row, text=lbl, bg=T["win_bg"], fg=T["text"],
                     font=(FONT_UI, 9), width=16, anchor="e").pack(side="left")
            e = mkentry(row, width=20, password=True); e.pack(side="left", padx=6)
            entries.append(e)

        result_lbl = tk.Label(pw_f, text="", bg=T["win_bg"],
                               font=(FONT_UI, 9))
        result_lbl.pack(anchor="w", pady=2)

        def change_pw():
            old, new, conf = [e.get() for e in entries]
            if not old or not new:
                result_lbl.config(text="Please fill in all fields.", fg=T["warning"])
                return
            if new != conf:
                result_lbl.config(text="New passwords do not match.", fg=T["danger"])
                return
            if len(new) < 4:
                result_lbl.config(text="Password must be at least 4 characters.", fg=T["warning"])
                return
            u = self.wm.users.current or "user"
            if self.wm.users.change_password(u, old, new):
                result_lbl.config(text="✓  Password changed successfully.", fg=T["success"])
                for e in entries: e.delete(0, "end")
                self.wm.notifs.send("Settings", "Password changed.", icon="🔒")
            else:
                result_lbl.config(text="✗  Current password is incorrect.", fg=T["danger"])

        mkbtn(pw_f, "🔒  Change Password", change_pw, kind="accent").pack(
            anchor="w", pady=6)

    # ── ACCOUNTS ──────────────────────────────────────────────────────────────

    def _panel_accounts(self) -> None:
        self._header("👤  Accounts")

        for acct in self.wm.users.all_accounts():
            card = tk.Frame(self._content, bg=T["panel_alt"],
                             padx=12, pady=10)
            card.pack(fill="x", padx=16, pady=5)

            av = tk.Label(card, text=acct.username[0].upper(),
                          bg=acct.avatar_color, fg="#ffffff",
                          font=(FONT_UI, 18, "bold"), width=2)
            av.pack(side="left", padx=(0, 12))

            info = tk.Frame(card, bg=T["panel_alt"])
            info.pack(side="left", fill="x", expand=True)
            tk.Label(info, text=acct.fullname,
                     bg=T["panel_alt"], fg=T["text"],
                     font=(FONT_UI, 11, "bold")).pack(anchor="w")
            is_cur = acct.username == self.wm.users.current
            tk.Label(info,
                     text=f"@{acct.username}  •  "
                          f"{'Administrator' if acct.admin else 'Standard User'}  •  "
                          f"{'Current session' if is_cur else 'Offline'}",
                     bg=T["panel_alt"], fg=T["text_muted"],
                     font=(FONT_UI, 8)).pack(anchor="w")
            if acct.last_login:
                tk.Label(info,
                         text=f"Last login: {fmt_time(acct.last_login)}",
                         bg=T["panel_alt"], fg=T["text_muted"],
                         font=(FONT_UI, 8)).pack(anchor="w")

            # Avatar colour picker
            def pick_color(a=acct):
                result = colorchooser.askcolor(
                    color=a.avatar_color,
                    title=f"Avatar colour for {a.username}",
                    parent=self.wm.root,
                )
                if result and result[1]:
                    a.avatar_color = result[1]
                    self._show("Accounts")
            tk.Button(card, text="🎨",
                      command=pick_color,
                      bg=T["panel_alt"], fg=T["text"],
                      relief="flat", bd=0,
                      font=(FONT_EMOJI, 12), cursor="hand2",
                      activebackground=T["button_hover"]).pack(side="right")

    # ── ABOUT ─────────────────────────────────────────────────────────────────

    def _panel_about(self) -> None:
        self._header("ℹ️  About PyOS")

        rows = [
            ("Version",       f"PyOS {PYOS_VERSION}  ({PYOS_CODENAME})"),
            ("Build Date",    BUILD_DATE),
            ("Language",      f"Python {sys.version.split()[0]}"),
            ("GUI Framework", "Tkinter (stdlib only)"),
            ("Dependencies",  "Zero external packages"),
            ("Lines of Code", "~18,000"),
            ("Applications",  "20 built-in"),
            ("Terminal Cmds", "60+"),
            ("Themes",        "5"),
            ("Wallpapers",    "8"),
            ("Platform",      f"{platform.system()} {platform.release()}"),
            ("Architecture",  platform.machine()),
            ("Hostname",      "pyos-machine"),
            ("Python Path",   sys.executable[:50]),
        ]
        for i, (k, v) in enumerate(rows):
            bg  = T["win_bg"] if i % 2 == 0 else T["panel_bg"]
            row = tk.Frame(self._content, bg=bg); row.pack(fill="x", padx=16)
            tk.Label(row, text=k + ":",
                     bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 9), width=16, anchor="e").pack(
                side="left", padx=8, pady=4)
            tk.Label(row, text=v,
                     bg=bg, fg=T["text"],
                     font=(FONT_MONO, 9)).pack(side="left")

        tk.Label(self._content,
                 text="\nBuilt with ❤️  in pure Python.\n"
                      "No pip install. No external frameworks. Just Python and Tkinter.",
                 bg=T["win_bg"], fg=T["accent"],
                 font=(FONT_UI, 10), padx=16,
                 justify="left").pack(anchor="w", pady=10)

        bf = tk.Frame(self._content, bg=T["win_bg"])
        bf.pack(anchor="w", padx=16, pady=4)
        mkbtn(bf, "📋  Copy Version Info",
              lambda: (
                  self.wm.clip.copy_text(
                      f"PyOS {PYOS_VERSION} ({PYOS_CODENAME})\n"
                      f"Python {sys.version.split()[0]}\n"
                      f"Platform: {platform.system()} {platform.release()}"
                  ),
                  self.wm.notifs.send("Settings", "Version info copied", icon="📋"),
              )).pack(side="left", padx=4)
        mkbtn(bf, "🔄  Reset All Settings",
              self._reset_settings, kind="danger").pack(side="left", padx=4)

    def _reset_settings(self) -> None:
        if messagebox.askyesno(
            "Reset Settings",
            "Reset ALL settings to defaults?\nThis cannot be undone.",
            parent=self.wm.root,
        ):
            self.wm.settings.reset()
            self.wm.notifs.send("Settings",
                                 "All settings reset to defaults.", icon="🔄")
            self._show("Appearance")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 35 — LOGIN SCREEN
# ─────────────────────────────────────────────────────────────────────────────

def show_login(root: tk.Tk, wm: "WM") -> None:
    """Full-screen login screen."""

    # Hide any open app windows
    for win in getattr(wm, "wins", []):
        try:
            win._outer.place_forget()
        except Exception:
            pass

    # ── Full-screen overlay ───────────────────────────────────────────────────
    overlay = tk.Frame(root, bg="#0d1117")
    overlay.place(x=0, y=0, width=SCREEN_W, height=SCREEN_H)
    overlay.lift()

    # ── Animated gradient background ──────────────────────────────────────────
    bg_canvas = tk.Canvas(overlay, bg="#0d1117", highlightthickness=0)
    bg_canvas.place(x=0, y=0, width=SCREEN_W, height=SCREEN_H)
    _frame = [0]

    def _draw_bg():
        if not overlay.winfo_exists():
            return
        bg_canvas.delete("all")
        t = _frame[0] * 0.02
        for i in range(40):
            ratio = i / 40
            r = max(0, min(255, int(13 + ratio * 20 + math.sin(t + ratio * 3) * 8)))
            g = max(0, min(255, int(17 + ratio * 30 + math.sin(t * 0.7 + ratio) * 6)))
            b = max(0, min(255, int(23 + ratio * 60 + math.sin(t * 1.3 + ratio * 2) * 12)))
            y0 = int(i * SCREEN_H / 40)
            y1 = int((i + 1) * SCREEN_H / 40)
            bg_canvas.create_rectangle(0, y0, SCREEN_W, y1,
                                       fill=f"#{r:02x}{g:02x}{b:02x}", outline="")
        # Floating orbs (solid dark colours — no alpha)
        orb_colours = ["#0d2a5e", "#2d1e4a", "#0e3318", "#3d2408"]
        for j in range(4):
            ox = int(SCREEN_W * 0.2 + SCREEN_W * 0.6 * ((j * 0.31 + t * 0.04) % 1))
            oy = int(SCREEN_H * 0.3 + SCREEN_H * 0.4 * math.sin(t * 0.3 + j * 1.5))
            r2 = 80 + int(20 * math.sin(t + j))
            bg_canvas.create_oval(ox - r2, oy - r2, ox + r2, oy + r2,
                                  fill=orb_colours[j], outline="")
        _frame[0] += 1
        root.after(60, _draw_bg)

    _draw_bg()

    # ── Login card ────────────────────────────────────────────────────────────
    card = tk.Frame(overlay, bg="#161b22", highlightthickness=1,
                    highlightbackground="#30363d")
    card.place(relx=0.5, rely=0.5, anchor="center", width=400, height=560)
    card.lift()

    # Logo
    tk.Label(card, text="PyOS", bg="#161b22", fg="#388bfd",
             font=(FONT_UI, 34, "bold")).pack(pady=(20, 0))
    tk.Label(card, text=f"v{PYOS_VERSION}  •  {PYOS_CODENAME}",
             bg="#161b22", fg="#484f58", font=(FONT_UI, 10)).pack()

    # Clock
    clock_lbl = tk.Label(card, text="", bg="#161b22", fg="#e6edf3",
                         font=(FONT_MONO, 16, "bold"))
    clock_lbl.pack(pady=(8, 0))
    date_lbl = tk.Label(card, text="", bg="#161b22", fg="#7d8590",
                        font=(FONT_UI, 9))
    date_lbl.pack()

    def _tick():
        if not overlay.winfo_exists():
            return
        now = datetime.datetime.now()
        clock_lbl.config(text=now.strftime("%H:%M:%S"))
        date_lbl.config(text=now.strftime("%A, %B %d, %Y"))
        root.after(1000, _tick)
    _tick()

    # User selector
    tk.Label(card, text="Select User", bg="#161b22", fg="#7d8590",
             font=(FONT_UI, 9, "bold")).pack(pady=(12, 4))

    users_f = tk.Frame(card, bg="#161b22")
    users_f.pack()

    account_keys = list(wm.users._accounts.keys())
    selected_user = tk.StringVar(value=account_keys[0] if account_keys else "")
    user_btns = {}

    def _select_user(u):
        selected_user.set(u)
        for k, btn in user_btns.items():
            acct = wm.users._accounts[k]
            btn.config(bg=acct.avatar_color if k == u else "#21262d")
        pw_entry.delete(0, "end")
        pw_entry.focus_set()

    for uname, acct in wm.users._accounts.items():
        is_sel = (uname == selected_user.get())
        col = tk.Frame(users_f, bg="#161b22")
        col.pack(side="left", padx=8)
        btn = tk.Button(col, text=uname[0].upper(),
                        command=partial(_select_user, uname),
                        bg=acct.avatar_color if is_sel else "#21262d",
                        fg="#ffffff", relief="flat", bd=0,
                        font=(FONT_UI, 16, "bold"), width=2, height=1,
                        cursor="hand2", activebackground=acct.avatar_color)
        btn.pack()
        tk.Label(col, text=uname, bg="#161b22", fg="#7d8590",
                 font=(FONT_UI, 8)).pack(pady=(2, 0))
        user_btns[uname] = btn

    # Password
    tk.Label(card, text="Password", bg="#161b22", fg="#7d8590",
             font=(FONT_UI, 9)).pack(pady=(12, 2))

    pw_frame = tk.Frame(card, bg="#161b22")
    pw_frame.pack(fill="x", padx=40)

    pw_var = tk.StringVar()
    pw_entry = tk.Entry(pw_frame, textvariable=pw_var,
                        bg="#0d1117", fg="#e6edf3",
                        insertbackground="#e6edf3",
                        relief="flat", bd=6,
                        font=(FONT_MONO, 12),
                        show="*",
                        highlightthickness=1,
                        highlightcolor="#388bfd",
                        highlightbackground="#30363d",
                        width=20)
    pw_entry.pack(side="left", fill="x", expand=True)
    pw_entry.focus_set()

    show_var = tk.BooleanVar(value=False)
    def _toggle_show():
        show_var.set(not show_var.get())
        pw_entry.config(show="" if show_var.get() else "*")
        show_btn.config(text="Hide" if show_var.get() else "Show")

    show_btn = tk.Button(pw_frame, text="Show", command=_toggle_show,
                         bg="#0d1117", fg="#7d8590", relief="flat", bd=0,
                         font=(FONT_UI, 8), cursor="hand2",
                         activebackground="#0d1117")
    show_btn.pack(side="right", padx=4)

    # Error label
    err_lbl = tk.Label(card, text="", bg="#161b22", fg="#f85149",
                       font=(FONT_UI, 9))
    err_lbl.pack(pady=(4, 0))

    # Shake animation
    def _shake():
        orig_x = card.winfo_x()
        orig_y = card.winfo_y()
        deltas = [10, -10, 8, -8, 5, -5, 2, -2, 0]
        def _step(idx=0):
            if idx < len(deltas):
                card.place(x=orig_x + deltas[idx], y=orig_y)
                card.after(30, lambda: _step(idx + 1))
            else:
                card.place(relx=0.5, rely=0.5, anchor="center",
                           width=400, height=560)
        _step()

    # Sign In button
    def _attempt_login(event=None):
        user = selected_user.get()
        pw   = pw_var.get()
        if wm.users.login(user, pw):
            overlay.destroy()
            for win in wm.wins:
                if not win.minimized:
                    try:
                        win._place()
                    except Exception:
                        pass
            wm.notifs.send(
                "Welcome",
                f"Good {'morning' if datetime.datetime.now().hour < 12 else 'afternoon'}, "
                f"{wm.users.info.fullname}!",
                icon="\U0001f44b", level="success",
            )
        else:
            err_lbl.config(text="Incorrect password")
            pw_var.set("")
            pw_entry.focus_set()
            _shake()

    tk.Button(card, text="Sign In", command=_attempt_login,
              bg="#388bfd", fg="#ffffff", relief="flat", bd=0,
              font=(FONT_UI, 11, "bold"), padx=28, pady=8,
              cursor="hand2", activebackground="#2878e0").pack(pady=(10, 6))

    pw_entry.bind("<Return>", _attempt_login)

    # Divider
    tk.Frame(card, bg="#21262d", height=1).pack(fill="x", padx=40, pady=(8, 0))

    tk.Label(card, text="Don't have an account?",
             bg="#161b22", fg="#484f58", font=(FONT_UI, 9)).pack(pady=(8, 2))

    # Create Account dialog
    def _open_signup():
        dlg = tk.Toplevel(root)
        dlg.title("Create Account")
        dlg.configure(bg="#161b22")
        dlg.resizable(False, False)
        dlg.transient(root)
        dlg.grab_set()
        W_D, H_D = 360, 420
        dlg.geometry(f"{W_D}x{H_D}+{root.winfo_x()+(SCREEN_W-W_D)//2}+"
                     f"{root.winfo_y()+(SCREEN_H-H_D)//2}")

        tk.Label(dlg, text="Create Account", bg="#161b22", fg="#388bfd",
                 font=(FONT_UI, 16, "bold")).pack(pady=(20, 2))
        tk.Label(dlg, text="Set up your PyOS account", bg="#161b22",
                 fg="#484f58", font=(FONT_UI, 9)).pack(pady=(0, 12))

        def _field(lbl_text, hide=False):
            tk.Label(dlg, text=lbl_text, bg="#161b22", fg="#7d8590",
                     font=(FONT_UI, 9)).pack(anchor="w", padx=36)
            var = tk.StringVar()
            e = tk.Entry(dlg, textvariable=var, bg="#0d1117", fg="#e6edf3",
                         insertbackground="#e6edf3", relief="flat", bd=6,
                         font=(FONT_MONO, 11), show="*" if hide else "",
                         highlightthickness=1, highlightcolor="#388bfd",
                         highlightbackground="#30363d", width=26)
            e.pack(padx=36, pady=(2, 8), fill="x")
            return var, e

        uname_var, uname_e = _field("Username")
        fname_var, _       = _field("Full Name (optional)")
        pw1_var,   pw1_e   = _field("Password", hide=True)
        pw2_var,   _       = _field("Confirm Password", hide=True)

        dlg_err = tk.Label(dlg, text="", bg="#161b22", fg="#f85149",
                           font=(FONT_UI, 9))
        dlg_err.pack()

        def _do_create(event=None):
            u = uname_var.get().strip().lower()
            f = fname_var.get().strip()
            p1 = pw1_var.get()
            p2 = pw2_var.get()
            if not u:
                dlg_err.config(text="Username cannot be empty."); return
            if len(u) < 2:
                dlg_err.config(text="Username must be 2+ characters."); return
            if not all(c.isalnum() or c == "_" for c in u):
                dlg_err.config(text="Letters, numbers, _ only."); return
            if u in wm.users._accounts:
                dlg_err.config(text=f"Username '{u}' already taken."); return
            if len(p1) < 3:
                dlg_err.config(text="Password must be 3+ characters."); return
            if p1 != p2:
                dlg_err.config(text="Passwords do not match."); return
            new_acct = UserAccount(u, p1, f or u.title(), admin=False,
                                   avatar_color="#388bfd")
            wm.vfs.mkdir(f"/home/{u}")
            wm.users.add_account(new_acct)
            # Refresh user buttons
            for w in users_f.winfo_children():
                w.destroy()
            user_btns.clear()
            for uname2, acct2 in wm.users._accounts.items():
                is_s = (uname2 == selected_user.get())
                c2 = tk.Frame(users_f, bg="#161b22")
                c2.pack(side="left", padx=8)
                b2 = tk.Button(c2, text=uname2[0].upper(),
                               command=partial(_select_user, uname2),
                               bg=acct2.avatar_color if is_s else "#21262d",
                               fg="#ffffff", relief="flat", bd=0,
                               font=(FONT_UI, 16, "bold"), width=2, height=1,
                               cursor="hand2",
                               activebackground=acct2.avatar_color)
                b2.pack()
                tk.Label(c2, text=uname2, bg="#161b22", fg="#7d8590",
                         font=(FONT_UI, 8)).pack(pady=(2, 0))
                user_btns[uname2] = b2
            selected_user.set(u)
            _select_user(u)
            dlg.destroy()
            wm.notifs.send("Account Created",
                           f"Welcome to PyOS, {new_acct.fullname}!",
                           icon="\U0001f389", level="success")

        tk.Button(dlg, text="Create Account", command=_do_create,
                  bg="#388bfd", fg="#ffffff", relief="flat", bd=0,
                  font=(FONT_UI, 11, "bold"), padx=20, pady=7,
                  cursor="hand2",
                  activebackground="#2878e0").pack(pady=(4, 4))
        tk.Button(dlg, text="Cancel", command=dlg.destroy,
                  bg="#21262d", fg="#7d8590", relief="flat", bd=0,
                  font=(FONT_UI, 9), cursor="hand2").pack()
        uname_e.focus_set()
        dlg.bind("<Return>", _do_create)

    tk.Button(card, text="Create Account", command=_open_signup,
              bg="#161b22", fg="#388bfd", relief="flat", bd=0,
              font=(FONT_UI, 10, "bold"), cursor="hand2",
              activebackground="#1c2230").pack(pady=(0, 4))

    tk.Label(card, text="Default: username = password  (e.g. user / user)",
             bg="#161b22", fg="#21262d", font=(FONT_UI, 8)).pack(pady=(2, 12))


def show_lock(root: tk.Tk, wm: "WM") -> None:
    """
    Quick lock screen overlay.
    Shows time, user name, and a single password field.
    Dismisses on correct password without restarting the session.
    """
    overlay = tk.Frame(root, bg="#000000")
    overlay.place(x=0, y=0, width=SCREEN_W, height=SCREEN_H)
    overlay.lift()

    # Background
    bg_c = tk.Canvas(overlay, bg="#000000", highlightthickness=0)
    bg_c.place(x=0, y=0, width=SCREEN_W, height=SCREEN_H)
    for i in range(SCREEN_H):
        t = i / SCREEN_H
        r = int(5  + t * 15)
        g = int(5  + t * 10)
        b = int(10 + t * 30)
        bg_c.create_line(0, i, SCREEN_W, i,
                          fill=f"#{r:02x}{g:02x}{b:02x}")

    # Card
    card = tk.Frame(overlay, bg="#161b22",
                    highlightthickness=1,
                    highlightbackground="#30363d")
    card.place(relx=0.5, rely=0.5, anchor="center", width=340, height=360)

    # Lock icon
    tk.Label(card, text="🔒",
             bg="#161b22", fg="#388bfd",
             font=(FONT_EMOJI, 40)).pack(pady=(24, 4))

    # Clock
    clock_lbl = tk.Label(card, text="",
                          bg="#161b22", fg="#e6edf3",
                          font=(FONT_MONO, 24, "bold"))
    clock_lbl.pack()
    date_lbl  = tk.Label(card, text="",
                          bg="#161b22", fg="#7d8590",
                          font=(FONT_UI, 10))
    date_lbl.pack()

    def tick_lock() -> None:
        if not overlay.winfo_exists():
            return
        now = datetime.datetime.now()
        clock_lbl.config(text=now.strftime("%H:%M"))
        date_lbl.config(text=now.strftime("%A, %B %d"))
        root.after(1000, tick_lock)

    tick_lock()

    # User
    acct = wm.users.info
    if acct:
        tk.Label(card, text=acct.fullname,
                 bg="#161b22", fg="#e6edf3",
                 font=(FONT_UI, 12, "bold")).pack(pady=(10, 2))
        tk.Label(card, text=f"@{wm.users.current}",
                 bg="#161b22", fg="#7d8590",
                 font=(FONT_UI, 9)).pack()

    # Password
    pw_var  = tk.StringVar()
    pw_e    = tk.Entry(card, textvariable=pw_var,
                        bg="#0d1117", fg="#e6edf3",
                        insertbackground="#e6edf3",
                        relief="flat", bd=8,
                        font=(FONT_MONO, 12),
                        show="*", width=22,
                        highlightthickness=1,
                        highlightcolor="#388bfd",
                        highlightbackground="#30363d")
    pw_e.pack(pady=(14, 4), padx=30)
    pw_e.focus_set()

    err_lbl = tk.Label(card, text="",
                        bg="#161b22", fg="#f85149",
                        font=(FONT_UI, 8))
    err_lbl.pack()

    def unlock(event=None) -> None:
        user = wm.users.current or "user"
        if wm.users._accounts.get(user, None) and \
           wm.users._accounts[user].verify(pw_var.get()):
            overlay.destroy()
        else:
            err_lbl.config(text="Incorrect password")
            pw_var.set("")

    tk.Button(card, text="Unlock",
               command=unlock,
               bg="#388bfd", fg="#ffffff",
               relief="flat", bd=0,
               font=(FONT_UI, 10, "bold"),
               padx=20, pady=6,
               cursor="hand2",
               activebackground="#2878e0").pack(pady=10)

    pw_e.bind("<Return>", unlock)

    # Switch user link
    tk.Button(card, text="Switch User",
               command=lambda: (overlay.destroy(), show_login(root, wm)),
               bg="#161b22", fg="#7d8590",
               relief="flat", bd=0,
               font=(FONT_UI, 8),
               cursor="hand2",
               activebackground="#161b22").pack()

# =============================================================================
#  End of Part 6b (~500 lines)
#  Covered: SettingsApp (8 panels), show_login(), show_lock()
#  Next (6c): boot_screen(), main() entry point, assembly instructions
# =============================================================================
#!/usr/bin/env python3
# =============================================================================
#  PyOS v5.0 — PART 6c  (Final chunk — completes the OS)
#  Boot animation, WM app launchers, main() entry point
#  Requires: Parts 1–5 + 6a + 6b concatenated before this
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 37 — BOOT ANIMATION
# ─────────────────────────────────────────────────────────────────────────────

def boot_screen(root: tk.Tk, on_complete) -> None:
    """
    Full-screen animated boot sequence.
    Shows ASCII logo, scrolling boot messages, progress bar.
    Calls on_complete() when finished.
    """
    frame = tk.Frame(root, bg="#000000")
    frame.place(x=0, y=0, width=SCREEN_W, height=SCREEN_H)
    frame.lift()

    canvas = tk.Canvas(frame, bg="#000000", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    LOGO = [
        "██████╗ ██╗   ██╗ ██████╗ ███████╗",
        "██╔══██╗╚██╗ ██╔╝██╔═══██╗██╔════╝",
        "██████╔╝ ╚████╔╝ ██║   ██║███████╗",
        "██╔═══╝   ╚██╔╝  ██║   ██║╚════██║",
        "██║        ██║   ╚██████╔╝███████║",
        "╚═╝        ╚═╝    ╚═════╝ ╚══════╝",
    ]

    BOOT_MSGS = [
        ("[  OK  ]", "Starting kernel…",              0.08),
        ("[  OK  ]", "Mounting virtual filesystem…",  0.08),
        ("[  OK  ]", "Initialising process manager…", 0.07),
        ("[  OK  ]", "Loading user accounts…",        0.07),
        ("[  OK  ]", "Starting notification daemon…", 0.06),
        ("[  OK  ]", "Starting window manager…",      0.07),
        ("[  OK  ]", "Loading theme: Dark Blue…",     0.06),
        ("[  OK  ]", "Drawing wallpaper…",            0.05),
        ("[  OK  ]", "Registering desktop icons…",   0.06),
        ("[  OK  ]", "Starting taskbar…",             0.05),
        ("[  OK  ]", "Loading File Manager…",         0.05),
        ("[  OK  ]", "Loading Text Editor…",          0.04),
        ("[  OK  ]", "Loading Terminal…",             0.04),
        ("[  OK  ]", "Loading Browser…",              0.04),
        ("[  OK  ]", "Loading Music Player…",         0.04),
        ("[  OK  ]", "Loading Paint Studio…",         0.03),
        ("[  OK  ]", "Loading Calculator…",           0.03),
        ("[  OK  ]", "Loading Clock…",                0.03),
        ("[  OK  ]", "Loading Task Manager…",         0.03),
        ("[  OK  ]", "Loading Notes…",                0.03),
        ("[  OK  ]", "Loading Email Client…",         0.03),
        ("[  OK  ]", "Loading Password Manager…",     0.03),
        ("[  OK  ]", "Loading Spreadsheet…",          0.03),
        ("[  OK  ]", "Loading Image Viewer…",         0.03),
        ("[  OK  ]", "Loading Disk Analyzer…",        0.03),
        ("[  OK  ]", "Loading Code Runner…",          0.03),
        ("[  OK  ]", "Loading Archive Manager…",      0.03),
        ("[  OK  ]", "Loading App Store…",            0.03),
        ("[  OK  ]", "Loading System Monitor…",       0.03),
        ("[  OK  ]", "Loading Settings…",             0.03),
        ("[ BOOT ]", f"PyOS {PYOS_VERSION} ready.",  0.10),
    ]

    CX = SCREEN_W // 2

    # ── draw logo ─────────────────────────────────────────────────────────────
    logo_y = SCREEN_H // 2 - 180
    for i, line in enumerate(LOGO):
        canvas.create_text(
            CX, logo_y + i * 22,
            text=line,
            fill="#388bfd",
            font=(FONT_MONO, 14, "bold"),
        )

    canvas.create_text(
        CX, logo_y + len(LOGO) * 22 + 10,
        text=f"v{PYOS_VERSION}  •  {PYOS_CODENAME}  •  Pure Python",
        fill="#484f58",
        font=(FONT_UI, 10),
    )

    # ── progress bar outline ──────────────────────────────────────────────────
    bar_y  = SCREEN_H // 2 + 30
    bar_x1 = CX - 220
    bar_x2 = CX + 220
    bar_h  = 6
    canvas.create_rectangle(bar_x1, bar_y, bar_x2, bar_y + bar_h,
                             outline="#21262d", fill="#0d1117")
    bar_fill = canvas.create_rectangle(bar_x1, bar_y, bar_x1, bar_y + bar_h,
                                        fill="#388bfd", outline="")

    # ── message text area ─────────────────────────────────────────────────────
    msg_start_y = bar_y + 30
    max_msgs    = 10
    msg_ids: list = []

    status_id = canvas.create_text(
        CX, msg_start_y - 16,
        text="",
        fill="#3fb950",
        font=(FONT_MONO, 9),
    )

    # ── step through boot messages ────────────────────────────────────────────
    step_idx  = [0]
    n_steps   = len(BOOT_MSGS)

    def step() -> None:
        i = step_idx[0]
        if i >= n_steps:
            root.after(300, finish)
            return

        tag, msg, delay = BOOT_MSGS[i]
        step_idx[0] += 1

        # Update progress bar
        progress = step_idx[0] / n_steps
        fill_x   = bar_x1 + int((bar_x2 - bar_x1) * progress)
        canvas.coords(bar_fill, bar_x1, bar_y, fill_x, bar_y + bar_h)

        # Colour tag
        tag_col = "#3fb950" if "OK" in tag else "#388bfd"
        canvas.itemconfig(status_id, text=f"{tag}  {msg}", fill=tag_col)

        # Scroll message log
        if len(msg_ids) >= max_msgs:
            canvas.delete(msg_ids.pop(0))
            for j, mid in enumerate(msg_ids):
                canvas.move(mid, 0, -14)

        mid = canvas.create_text(
            bar_x1, msg_start_y + len(msg_ids) * 14,
            text=f"{tag}  {msg}",
            fill=tag_col,
            font=(FONT_MONO, 8),
            anchor="w",
        )
        msg_ids.append(mid)

        root.after(int(delay * 1000), step)

    def finish() -> None:
        # Flash effect using after() to avoid blocking the event loop
        flash_colours = ["#388bfd", "#ffffff", "#388bfd", "#000000"]
        flash_idx = [0]

        def do_flash():
            if flash_idx[0] < len(flash_colours):
                try:
                    canvas.config(bg=flash_colours[flash_idx[0]])
                except Exception:
                    pass
                flash_idx[0] += 1
                root.after(50, do_flash)
            else:
                frame.destroy()
                on_complete()

        do_flash()

    root.after(200, step)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 38 — WM APP LAUNCHER METHODS
#  (Attach these to WM at runtime via monkey-patch or define here as helpers)
# ─────────────────────────────────────────────────────────────────────────────

def _wm_open_app(wm: "WM", cls, *args, **kwargs):
    """Generic app opener — brings existing instance to front or creates new."""
    for win in wm.wins:
        if type(win).__name__ == cls.__name__:
            win.focus()
            return win
    app = cls(wm, *args, **kwargs)
    return app


def _attach_launchers(wm: "WM") -> None:
    """
    Attach all open_<app> convenience methods to the WM instance.
    Called once after WM is created.
    """
    from functools import partial as _p

    wm.open_fm          = lambda path=None:      FileManagerApp(wm, path)
    wm.open_editor      = lambda path=None:      TextEditorApp(wm, path)
    wm.open_terminal    = lambda:                TerminalApp(wm)
    wm.open_browser     = lambda url=None:       BrowserApp(wm, url)
    wm.open_music       = lambda:                MusicPlayerApp(wm)
    wm.open_paint       = lambda:                PaintApp(wm)
    wm.open_calc        = lambda:                CalculatorApp(wm)
    wm.open_clock       = lambda:                ClockApp(wm)
    wm.open_taskman     = lambda:                TaskManagerApp(wm)
    wm.open_notes       = lambda:                NotesApp(wm)
    wm.open_email       = lambda:                EmailApp(wm)
    wm.open_passwords   = lambda:                PasswordManagerApp(wm)
    wm.open_spreadsheet = lambda path=None:      SpreadsheetApp(wm, path)
    wm.open_images      = lambda:                ImageViewerApp(wm)
    wm.open_disk        = lambda:                DiskAnalyzerApp(wm)
    wm.open_code        = lambda:                CodeRunnerApp(wm)
    wm.open_archive     = lambda:                ArchiveManagerApp(wm)
    wm.open_store       = lambda:                AppStoreApp(wm)
    wm.open_sysmon      = lambda:                SystemMonitorApp(wm)
    wm.open_settings    = lambda panel=None:     SettingsApp(wm)
    wm.open_lock        = lambda:                show_lock(wm.root, wm)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 40 — VFS POPULATION (sample files and directories)
# ─────────────────────────────────────────────────────────────────────────────

def _populate_vfs(vfs: "VirtualFileSystem") -> None:
    """
    Create a realistic home directory tree and seed it with
    sample text files, scripts, and data the user can explore.
    """

    # Directory structure
    dirs = [
        "/home/user",
        "/home/user/Desktop",
        "/home/user/Documents",
        "/home/user/Downloads",
        "/home/user/Pictures",
        "/home/user/Music",
        "/home/user/Videos",
        "/home/user/Code",
        "/home/user/Spreadsheets",
        "/home/user/Archives",
        "/home/user/.config",
        "/home/user/.cache",
        "/var/log",
        "/var/tmp",
        "/etc",
        "/usr/bin",
        "/usr/local/bin",
        "/tmp",
    ]
    for d in dirs:
        vfs.makedirs(d)

    # ── Sample text files ──────────────────────────────────────────────────────
    vfs.write("/home/user/Documents/readme.txt",
"""Welcome to PyOS v5.0!
=======================

PyOS is a complete desktop OS simulation written entirely in Python
using only the standard library (Tkinter). No pip install required.

Getting Started
---------------
- Double-click desktop icons to open apps
- Right-click the desktop for a context menu
- Use the Start Menu (bottom-left) to launch any app
- Open the Terminal and type 'help' for 60+ commands

Tips
----
- Terminal: use Tab to autocomplete, ↑↓ for history
- Editor: Ctrl+S to save, Ctrl+F to find
- File Manager: right-click files for options
- Settings: change themes, wallpaper, fonts and more

Enjoy exploring PyOS!
""")

    vfs.write("/home/user/Documents/notes.md",
"""# My Notes

## Ideas
- Learn Python decorators
- Build a Flask API
- Read "Clean Code"

## TODO
- [ ] Organise Downloads folder
- [ ] Write unit tests
- [x] Set up PyOS
""")

    vfs.write("/home/user/Documents/journal_2025.txt",
"""Journal — 2025
==============

January 1
---------
New year, new goals. Starting with Python and PyOS exploration today.
The terminal has so many built-in commands — cowsay is my favourite so far.

January 3
---------
Discovered the Code Runner app. Ran my first Fibonacci snippet.
The REPL is really handy for quick calculations.

January 5
---------
Customised the theme to Dracula. The purple accent looks great.
Also changed wallpaper to Starfield.
""")

    vfs.write("/home/user/Desktop/welcome.txt",
f"""Welcome to PyOS {PYOS_VERSION}!
{"="*30}

You are logged in as: user
System: pyos-machine
Python: {sys.version.split()[0]}

Quick Start:
  - Terminal → type 'sysinfo'
  - Settings → change theme
  - App Store → browse apps

Have fun!
""")

    # ── Sample Python scripts ──────────────────────────────────────────────────
    vfs.write("/home/user/Code/hello.py",
"""#!/usr/bin/env python3
\"\"\"Hello World script for PyOS.\"\"\"

import sys
import datetime

def greet(name: str) -> str:
    hour = datetime.datetime.now().hour
    if hour < 12:
        time_of_day = "morning"
    elif hour < 17:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"
    return f"Good {time_of_day}, {name}!"

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "PyOS User"
    print(greet(name))
    print(f"Python {sys.version.split()[0]} running on PyOS")
""")

    vfs.write("/home/user/Code/fibonacci.py",
"""#!/usr/bin/env python3
\"\"\"Fibonacci sequence generator.\"\"\"

def fibonacci(n: int):
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

def is_prime(n: int) -> bool:
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

if __name__ == "__main__":
    fibs = list(fibonacci(20))
    print("First 20 Fibonacci numbers:")
    print(fibs)
    primes = [f for f in fibs if is_prime(f)]
    print(f"\\nFibonacci primes: {primes}")
""")

    vfs.write("/home/user/Code/data_analysis.py",
"""#!/usr/bin/env python3
\"\"\"Simple data analysis example.\"\"\"

import math
import statistics

data = [23, 45, 12, 67, 34, 89, 56, 78, 90, 11,
        43, 65, 32, 54, 76, 21, 87, 39, 62, 48]

print("=== Data Analysis ===")
print(f"Count:   {len(data)}")
print(f"Sum:     {sum(data)}")
print(f"Mean:    {statistics.mean(data):.2f}")
print(f"Median:  {statistics.median(data):.2f}")
print(f"Std Dev: {statistics.stdev(data):.2f}")
print(f"Min:     {min(data)}")
print(f"Max:     {max(data)}")
print(f"Range:   {max(data) - min(data)}")
print(f"\\nSorted: {sorted(data)}")
""")

    vfs.write("/home/user/Code/web_scraper.py",
"""#!/usr/bin/env python3
\"\"\"Simulated web scraper (no network in PyOS).\"\"\"

import re
import datetime

SAMPLE_HTML = \"\"\"
<html>
<head><title>PyOS News</title></head>
<body>
  <h1>Latest News</h1>
  <article>
    <h2>PyOS v5.0 Released</h2>
    <p>The biggest release yet with 20 apps and 60+ terminal commands.</p>
    <time>2025-01-01</time>
  </article>
  <article>
    <h2>Python 4.0 Announced</h2>
    <p>Breaking changes include new syntax for async functions.</p>
    <time>2025-06-15</time>
  </article>
</body>
</html>
\"\"\"

def parse_articles(html: str):
    titles = re.findall(r'<h2>(.*?)</h2>', html)
    descs  = re.findall(r'<p>(.*?)</p>',  html)
    dates  = re.findall(r'<time>(.*?)</time>', html)
    return list(zip(titles, descs, dates))

articles = parse_articles(SAMPLE_HTML)
print(f"Found {len(articles)} articles:\\n")
for title, desc, date in articles:
    print(f"  [{date}] {title}")
    print(f"  {desc[:60]}...")
    print()
""")

    # ── CSV / Spreadsheet data ─────────────────────────────────────────────────
    vfs.makedirs("/home/user/Spreadsheets")
    vfs.write("/home/user/Spreadsheets/budget.csv",
"""Category,January,February,March,April,May,June
Income,5000,5000,5200,5000,5000,5500
Rent,1500,1500,1500,1500,1500,1500
Food,400,380,420,390,410,430
Transport,150,160,140,155,145,165
Utilities,80,85,75,80,90,70
Entertainment,200,150,180,220,160,190
Savings,800,800,900,800,800,1000
Total Expenses,3130,3075,3215,3145,3105,3355
Net,1870,1925,1985,1855,1895,2145
""")

    vfs.write("/home/user/Spreadsheets/grades.csv",
"""Student,Math,Science,English,History,Average
Alice,92,88,95,87,90.5
Bob,78,82,74,80,78.5
Carol,95,97,91,94,94.25
Dave,65,70,68,72,68.75
Eve,88,85,90,83,86.5
Frank,73,78,80,75,76.5
""")

    # ── Log files ──────────────────────────────────────────────────────────────
    import datetime as _dt
    log_lines = []
    now = _dt.datetime.now()
    for i in range(20):
        t  = now - _dt.timedelta(minutes=i * 3)
        ts = t.strftime("%Y-%m-%d %H:%M:%S")
        msgs = [
            "INFO  System started",
            "INFO  VFS mounted at /",
            "DEBUG ProcessManager: spawned pyos-wm (PID 1)",
            "INFO  UserManager: user 'user' logged in",
            "DEBUG Taskbar: clock widget started",
            "INFO  Notification daemon ready",
            "DEBUG WM: wallpaper drawn (gradient_blue)",
            "INFO  Desktop icons registered (20)",
            "DEBUG Settings: theme=Dark Blue loaded",
            "INFO  Boot complete in 1.24s",
        ]
        log_lines.append(f"[{ts}] {msgs[i % len(msgs)]}")
    vfs.write("/var/log/pyos.log", "\n".join(reversed(log_lines)) + "\n")

    vfs.write("/var/log/auth.log",
f"""[{now.strftime('%Y-%m-%d %H:%M:%S')}] AUTH  user 'user' logged in from tty0
[{now.strftime('%Y-%m-%d %H:%M:%S')}] AUTH  session opened for user 'user'
""")

    # ── Config files ───────────────────────────────────────────────────────────
    vfs.write("/etc/hostname", "pyos-machine\n")
    vfs.write("/etc/os-release",
f"""NAME="PyOS"
VERSION="{PYOS_VERSION}"
VERSION_CODENAME="{PYOS_CODENAME}"
ID=pyos
PRETTY_NAME="PyOS {PYOS_VERSION} ({PYOS_CODENAME})"
HOME_URL="https://pyos.example.com"
""")

    vfs.write("/etc/hosts",
"""127.0.0.1   localhost
127.0.0.1   pyos-machine
192.168.1.1 gateway
""")

    vfs.write("/home/user/.config/pyos.conf",
"""[pyos]
theme = Dark Blue
wallpaper = gradient_blue
font_size = 10
show_boot = true

[terminal]
font_size = 10
scrollback = 1000
bell = false

[editor]
font_size = 11
tab_width = 4
auto_indent = true
word_wrap = false
""")

    # ── Shell script ───────────────────────────────────────────────────────────
    vfs.write("/home/user/Code/backup.sh",
"""#!/bin/sh
# Simple backup script for PyOS VFS

echo "=== PyOS Backup Script ==="
echo "Date: $(date)"
echo ""
echo "Backing up /home/user/Documents..."
cp /home/user/Documents /tmp/backup_docs
echo "Done."
echo ""
echo "Backup complete."
""")

    # ── Downloads placeholder ──────────────────────────────────────────────────
    vfs.write("/home/user/Downloads/readme_downloads.txt",
"""Downloads folder
================
Files you download or export from apps will appear here.

Examples:
- Exported notes (.txt)
- Saved canvas images (.ps)
- CSV exports from Spreadsheet
- Archive extractions
""")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 41 — KEYBOARD & GLOBAL SHORTCUTS
# ─────────────────────────────────────────────────────────────────────────────

def _bind_global_shortcuts(root: tk.Tk, wm: "WM") -> None:
    """
    System-wide keyboard shortcuts (bound to root window).
    Only active when no text widget has focus.
    """

    def on_key(e: tk.Event) -> None:
        focused = root.focus_get()
        # Don't intercept if typing in an entry/text widget
        if isinstance(focused, (tk.Entry, tk.Text)):
            return

        key = e.keysym.lower()
        ctrl = bool(e.state & 0x4)
        alt  = bool(e.state & 0x8)

        if ctrl and key == "q":            # Ctrl+Q → Quit
            if messagebox.askyesno("Quit", "Quit PyOS?", parent=root):
                root.destroy()

        elif ctrl and key == "l":          # Ctrl+L → Lock
            show_lock(root, wm)

        elif ctrl and key == "t":          # Ctrl+T → New Terminal
            wm.open_terminal()

        elif ctrl and key == "e":          # Ctrl+E → Editor
            wm.open_editor()

        elif ctrl and key == "f":          # Ctrl+F → File Manager
            wm.open_fm()

        elif e.keysym == "Super_L" or e.keysym == "Super_R":
            wm.toggle_start_menu()         # Super → Start Menu

        elif e.keysym == "F1":            # F1 → Help
            wm.open_browser("pyos://help")

        elif e.keysym == "F5":            # F5 → Refresh desktop
            wm._draw_wallpaper()
            wm._draw_desktop_icons()

        elif e.keysym == "Print":         # PrintScreen → screenshot msg
            wm.notifs.send("Screenshot",
                            "Screenshot saved to /home/user/Pictures/",
                            icon="📸")

    root.bind("<KeyPress>", on_key)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 42 — GRACEFUL SHUTDOWN HANDLER
# ─────────────────────────────────────────────────────────────────────────────

def _setup_shutdown(root: tk.Tk, wm: "WM") -> None:
    """Handle window close (X button) — shows confirmation dialog."""

    def on_close() -> None:
        choice = messagebox.askyesnocancel(
            "Shut Down PyOS",
            "What would you like to do?",
            parent=root,
        )
        if choice is True:      # Yes → shut down
            root.destroy()
        elif choice is False:   # No → lock screen
            show_lock(root, wm)
        # Cancel → do nothing

    root.protocol("WM_DELETE_WINDOW", on_close)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 43 — UPDATED main() WITH ALL WIRING
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:  # noqa: F811  (redefinition is intentional — this is the final version)
    """
    PyOS v5.0 — complete entry point.

    Run with:
        python pyos.py

    Build the single runnable file with:
        cat pyos_v5_part1.py pyos_v5_part2.py pyos_v5_part3.py \\
            pyos_v5_part4.py pyos_v5_part5.py pyos_v5_part6a.py \\
            pyos_v5_part6b.py pyos_v5_part6c.py > pyos.py
        python pyos.py
    """

    # ── Root window ───────────────────────────────────────────────────────────
    root = tk.Tk()
    root.title(f"PyOS {PYOS_VERSION}  —  {PYOS_CODENAME}")
    root.geometry(f"{SCREEN_W}x{SCREEN_H}+0+0")
    root.configure(bg="#000000")
    root.resizable(True, True)
    root.minsize(800, 500)

    # App icon (best-effort; fails gracefully if no icon file)
    try:
        import base64 as _b64
        ico_data = (
            "R0lGODlhEAAQAIABAAAAAP///yH5BAEKAAEALAAAAAAQABAAAAIfjI+py+0P"
            "o5y02ouz3rz7D4biSJbmiabqyrbuCxQAOw=="
        )
        img = tk.PhotoImage(data=_b64.b64decode(ico_data))
        root.iconphoto(True, img)
    except Exception:
        pass

    # ── Core subsystems ───────────────────────────────────────────────────────
    vfs       = VFS()
    users     = UserManager()
    procs     = ProcessManager()
    notifs    = NotificationManager()
    settings  = Settings()
    clipboard = Clipboard()

    _populate_vfs(vfs)

    # ── Window Manager ────────────────────────────────────────────────────────
    wm = WM(
        root,
        vfs      = vfs,
        users    = users,
        procs    = procs,
        notifs   = notifs,
        settings = settings,
        clip     = clipboard,
    )

    # ── Launchers + global bindings ───────────────────────────────────────────
    _attach_launchers(wm)
    _bind_global_shortcuts(root, wm)
    _setup_shutdown(root, wm)

    # ── Boot sequence → Login → Desktop ──────────────────────────────────────
    def after_boot() -> None:
        show_login(root, wm)

    if settings.get("show_boot", True):
        boot_screen(root, after_boot)
    else:
        after_boot()

    # ── Event loop ────────────────────────────────────────────────────────────
    root.mainloop()


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY GUARD
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()


# =============================================================================
#  PyOS v5.0 — COMPLETE
# =============================================================================
#
#  ASSEMBLY INSTRUCTIONS
#  ─────────────────────
#  Concatenate all 8 files in order to produce a single runnable pyos.py:
#
#  On Linux / macOS:
#    cat pyos_v5_part1.py  \
#        pyos_v5_part2.py  \
#        pyos_v5_part3.py  \
#        pyos_v5_part4.py  \
#        pyos_v5_part5.py  \
#        pyos_v5_part6a.py \
#        pyos_v5_part6b.py \
#        pyos_v5_part6c.py > pyos.py
#    python3 pyos.py
#
#  On Windows (PowerShell):
#    Get-Content pyos_v5_part1.py,pyos_v5_part2.py,pyos_v5_part3.py, `
#               pyos_v5_part4.py,pyos_v5_part5.py,pyos_v5_part6a.py, `
#               pyos_v5_part6b.py,pyos_v5_part6c.py | Set-Content pyos.py
#    python pyos.py
#
#  On Windows (cmd):
#    copy /b pyos_v5_part1.py+pyos_v5_part2.py+pyos_v5_part3.py+ ^
#            pyos_v5_part4.py+pyos_v5_part5.py+pyos_v5_part6a.py+ ^
#            pyos_v5_part6b.py+pyos_v5_part6c.py pyos.py
#    python pyos.py
#
#  Requirements:
#    • Python 3.8 or later
#    • No external packages (stdlib only)
#    • Tkinter must be available (included by default on Windows/macOS;
#      on Linux: sudo apt install python3-tk  OR  sudo dnf install python3-tkinter)
#
#  PART SUMMARY
#  ────────────
#  Part 1  (2,268 lines)  Core: VFS, UserManager, ProcessManager,
#                         Settings, Clipboard, NotificationManager,
#                         5 themes, helper widgets, BaseWin
#  Part 2  (2,643 lines)  WM, Taskbar, StartMenu, FileManagerApp, TextEditorApp
#  Part 3  (3,419 lines)  TerminalApp (60+ cmds), BrowserApp, MusicPlayerApp,
#                         PaintApp
#  Part 4  (2,583 lines)  CalculatorApp (4 modes), ClockApp (5 tabs),
#                         TaskManagerApp (5 tabs), NotesApp, EmailApp
#  Part 5  (2,173 lines)  PasswordManagerApp, SpreadsheetApp, ImageViewerApp,
#                         DiskAnalyzerApp, CodeRunnerApp, ArchiveManagerApp
#  Part 6a   (654 lines)  AppStoreApp, SystemMonitorApp (partial)
#  Part 6b   (874 lines)  SettingsApp (8 panels), show_login, show_lock
#  Part 6c   (this file)  boot_screen, _populate_vfs, _attach_launchers,
#                         global shortcuts, shutdown handler, main()
#
#  TOTAL: ~16,600+ lines of pure Python
#
#  KEYBOARD SHORTCUTS (desktop)
#  ─────────────────────────────
#  Ctrl+T          New terminal
#  Ctrl+E          Open text editor
#  Ctrl+F          Open file manager
#  Ctrl+L          Lock screen
#  Ctrl+Q          Quit PyOS
#  F1              Open help (browser)
#  F5              Refresh desktop
#  Super (Win key) Toggle Start Menu
#  PrintScreen     Screenshot notification
#
#  Right-click desktop  → context menu
#  Double-click icon    → open app
#  Drag window titlebar → move window
#  Drag window edge     → resize window
#  Click ─ □ ✕          → minimise / maximise / close
#
# =============================================================================