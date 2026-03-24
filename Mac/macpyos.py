#!/usr/bin/env python3
# =============================================================================
#  MacPyOS v1.0 — macOS-Style Desktop OS Simulation
#  Pure Python + Tkinter ONLY. Zero external dependencies.
#
#  APPLICATIONS (20 total):
#    Finder, TextEdit, Terminal (60+ cmds), Safari, Music,
#    Preview, Calculator, Clock/World Clock, Activity Monitor,
#    Notes, Mail, Keychain, Numbers, Photos, Disk Utility,
#    Script Editor, App Store, System Preferences, Archive Utility,
#    Contacts
#
#  FEATURES:
#    • Full virtual filesystem (VFS) with Unix-like paths
#    • Multi-user login system with password hashing
#    • Draggable/resizable floating windows (macOS style)
#    • Menu bar (top) with Apple menu, app menus, status icons, clock
#    • Dock with magnification, bounce animation, labels
#    • Desktop with wallpaper, icons, right-click menus
#    • Notification Center (top-right banners)
#    • Clipboard (text + file)
#    • Process manager with live CPU/RAM simulation
#    • Theme engine (5 themes: Monterey, Ventura, Sonoma, Dark, High Contrast)
#    • Lock screen with blur effect simulation
#    • Boot animation (Apple logo)
#    • Spotlight search (Cmd+Space)
#    • Mission Control (swipe up / Ctrl+Up)
#    • Traffic light window controls (red/yellow/green)
#
#  Run:  python macpyos.py
# =============================================================================

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, simpledialog, font as tkfont
import os, sys, time, datetime, math, random, threading, json, re
import hashlib, calendar, traceback, uuid, base64, platform, io, copy
import colorsys, struct, zipfile, gzip, textwrap, string, queue
from collections import deque, defaultdict, OrderedDict
from functools import partial, lru_cache
from typing import Dict, List, Optional, Tuple, Any, Callable


# ── Windows-compatible strftime helper ───────────────────────────────────────
import platform as _platform

def _strftime(fmt: str, dt=None) -> str:
    """strftime that works on Windows (no %-d etc)."""
    import datetime as _dt
    if dt is None:
        dt = _dt.datetime.now()
    if _platform.system() == "Windows":
        fmt = fmt.replace("%-d", "%d").replace("%-I", "%I") \
                 .replace("%-H", "%H").replace("%-m", "%m") \
                 .replace("%-M", "%M").replace("%-S", "%S")
        result = dt.strftime(fmt)
        # Remove leading zeros manually for day and hour
        import re as _re
        result = _re.sub(r'(?<![\d])(0)(\d)', r'\2', result)
        return result
    return dt.strftime(fmt)
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 1 — GLOBAL CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

MACPYOS_VERSION  = "1.0.0"
MACPYOS_CODENAME = "Sequoia"
BUILD_DATE       = "2025"

import tkinter as _tk_probe
_probe = _tk_probe.Tk(); _probe.withdraw()
SCREEN_W  = _probe.winfo_screenwidth()
SCREEN_H  = _probe.winfo_screenheight()
_probe.destroy(); del _probe, _tk_probe
MENUBAR_H = 28
DOCK_H    = 72
TITLEBAR_H       = 28        # window title bar
WIN_MIN_W        = 280
WIN_MIN_H        = 180
BORDER_W         = 1         # macOS uses thin borders
ICON_SIZE        = 64        # desktop icon cell size
DOCK_ICON_SIZE   = 56        # normal dock icon size
DOCK_ICON_MAG    = 76        # magnified dock icon size
GRID_COLS        = 2         # desktop icon columns

# Traffic-light button sizes
TL_SIZE          = 12        # diameter of traffic light dots
TL_GAP           = 8         # gap between dots
TL_X             = 10        # left margin

# Font stack (macOS system fonts → fallbacks)
# Font stack — Windows/cross-platform compatible
import sys as _sys
_on_windows = _sys.platform == "win32"
FONT_UI    = "Segoe UI"   if _on_windows else "SF Pro Display"
FONT_MONO  = "Consolas"   if _on_windows else "SF Mono"
FONT_EMOJI = "Segoe UI Emoji" if _on_windows else "Apple Color Emoji"
del _sys, _on_windows

# macOS-style corner radius (simulated)
CORNER_R         = 10

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 2 — THEME ENGINE  (macOS inspired palettes)
# ─────────────────────────────────────────────────────────────────────────────

THEMES: Dict[str, Dict[str, str]] = {

    # ── Monterey Light (default) ─────────────────────────────────────────────
    "Monterey": {
        "desktop_bg":         "#1e6bb8",   # default macOS blue wallpaper feel
        "menubar_bg":         "#ececec",
        "menubar_fg":         "#1d1d1f",
        "menubar_border":     "#c8c8c8",
        "win_title_active":   "#ececec",
        "win_title_inactive": "#f5f5f5",
        "win_title_fg":       "#1d1d1f",
        "win_title_fg_in":    "#adadad",
        "win_border":         "#c8c8c8",
        "win_border_active":  "#c8c8c8",
        "win_bg":             "#ffffff",
        "panel_bg":           "#f5f5f5",
        "panel_alt":          "#ebebeb",
        "sidebar_bg":         "#e8e8e8",
        "accent":             "#007aff",   # macOS blue
        "accent2":            "#5856d6",   # macOS purple
        "accent3":            "#34c759",   # macOS green
        "danger":             "#ff3b30",   # macOS red
        "success":            "#34c759",
        "warning":            "#ff9500",
        "info":               "#007aff",
        "text":               "#1d1d1f",
        "text_muted":         "#6e6e73",
        "text_dim":           "#c7c7cc",
        "text_inverse":       "#ffffff",
        "input_bg":           "#ffffff",
        "input_border":       "#c8c8c8",
        "input_focus":        "#007aff",
        "button_bg":          "#007aff",
        "button_fg":          "#ffffff",
        "button_hover":       "#0066d6",
        "button_secondary":   "#e5e5ea",
        "menu_bg":            "#f0f0f0",
        "menu_hover":         "#007aff",
        "menu_fg":            "#1d1d1f",
        "menu_fg_hover":      "#ffffff",
        "menu_border":        "#c8c8c8",
        "selection":          "#b3d4ff",
        "scrollbar":          "transparent",
        "scrollbar_thumb":    "#c7c7cc",
        "status_bg":          "#f5f5f5",
        "status_border":      "#e5e5ea",
        "tag_bg":             "#e5f0ff",
        "tag_fg":             "#007aff",
        "code_bg":            "#f5f5f5",
        "code_fg":            "#1d1d1f",
        "tooltip_bg":         "#1d1d1f",
        "tooltip_fg":         "#ffffff",
        "shadow":             "#000000",
        "badge_bg":           "#ff3b30",
        "badge_fg":           "#ffffff",
        "progress_bg":        "#e5e5ea",
        "progress_fg":        "#007aff",
        "link":               "#007aff",
        "separator":          "#c8c8c8",
        "dock_bg":            "#ffffff",
        "dock_border":        "#ffffff",
        "tl_red":             "#ff5f57",
        "tl_yellow":          "#ffbd2e",
        "tl_green":           "#28c940",
        "tl_red_h":           "#e0443e",
        "tl_yellow_h":        "#dfa020",
        "tl_green_h":         "#1aab29",
        "chart1":             "#007aff",
        "chart2":             "#34c759",
        "chart3":             "#ff9500",
        "chart4":             "#ff3b30",
        "chart5":             "#5856d6",
        "vibrancy":           "#ffffff",
    },

    # ── Ventura Dark ─────────────────────────────────────────────────────────
    "Ventura Dark": {
        "desktop_bg":         "#1c1c1e",
        "menubar_bg":         "#2c2c2e",
        "menubar_fg":         "#f5f5f7",
        "menubar_border":     "#3a3a3c",
        "win_title_active":   "#2c2c2e",
        "win_title_inactive": "#242424",
        "win_title_fg":       "#f5f5f7",
        "win_title_fg_in":    "#636366",
        "win_border":         "#3a3a3c",
        "win_border_active":  "#3a3a3c",
        "win_bg":             "#1c1c1e",
        "panel_bg":           "#2c2c2e",
        "panel_alt":          "#3a3a3c",
        "sidebar_bg":         "#242426",
        "accent":             "#0a84ff",
        "accent2":            "#5e5ce6",
        "accent3":            "#30d158",
        "danger":             "#ff453a",
        "success":            "#30d158",
        "warning":            "#ff9f0a",
        "info":               "#0a84ff",
        "text":               "#f5f5f7",
        "text_muted":         "#8e8e93",
        "text_dim":           "#3a3a3c",
        "text_inverse":       "#1c1c1e",
        "input_bg":           "#3a3a3c",
        "input_border":       "#48484a",
        "input_focus":        "#0a84ff",
        "button_bg":          "#0a84ff",
        "button_fg":          "#ffffff",
        "button_hover":       "#0070e0",
        "button_secondary":   "#3a3a3c",
        "menu_bg":            "#2c2c2e",
        "menu_hover":         "#0a84ff",
        "menu_fg":            "#f5f5f7",
        "menu_fg_hover":      "#ffffff",
        "menu_border":        "#48484a",
        "selection":          "#0a4070",
        "scrollbar":          "transparent",
        "scrollbar_thumb":    "#636366",
        "status_bg":          "#2c2c2e",
        "status_border":      "#3a3a3c",
        "tag_bg":             "#0a3060",
        "tag_fg":             "#0a84ff",
        "code_bg":            "#2c2c2e",
        "code_fg":            "#f5f5f7",
        "tooltip_bg":         "#3a3a3c",
        "tooltip_fg":         "#f5f5f7",
        "shadow":             "#000000",
        "badge_bg":           "#ff453a",
        "badge_fg":           "#ffffff",
        "progress_bg":        "#3a3a3c",
        "progress_fg":        "#0a84ff",
        "link":               "#0a84ff",
        "separator":          "#3a3a3c",
        "dock_bg":            "#2c2c2e",
        "dock_border":        "#48484a",
        "tl_red":             "#ff5f57",
        "tl_yellow":          "#ffbd2e",
        "tl_green":           "#28c940",
        "tl_red_h":           "#e0443e",
        "tl_yellow_h":        "#dfa020",
        "tl_green_h":         "#1aab29",
        "chart1":             "#0a84ff",
        "chart2":             "#30d158",
        "chart3":             "#ff9f0a",
        "chart4":             "#ff453a",
        "chart5":             "#5e5ce6",
        "vibrancy":           "#2c2c2e",
    },

    # ── Sonoma (warm/sand tones) ──────────────────────────────────────────────
    "Sonoma": {
        "desktop_bg":         "#4a3728",
        "menubar_bg":         "#f2ede8",
        "menubar_fg":         "#2c2117",
        "menubar_border":     "#ddd5cc",
        "win_title_active":   "#f2ede8",
        "win_title_inactive": "#f7f4f1",
        "win_title_fg":       "#2c2117",
        "win_title_fg_in":    "#b0a89f",
        "win_border":         "#ddd5cc",
        "win_border_active":  "#ddd5cc",
        "win_bg":             "#ffffff",
        "panel_bg":           "#f7f4f1",
        "panel_alt":          "#eee8e2",
        "sidebar_bg":         "#ece5de",
        "accent":             "#d4500c",
        "accent2":            "#8c5e3c",
        "accent3":            "#4a8c3f",
        "danger":             "#c0392b",
        "success":            "#4a8c3f",
        "warning":            "#e67e22",
        "info":               "#d4500c",
        "text":               "#2c2117",
        "text_muted":         "#7d6e62",
        "text_dim":           "#c9bfb7",
        "text_inverse":       "#ffffff",
        "input_bg":           "#ffffff",
        "input_border":       "#ddd5cc",
        "input_focus":        "#d4500c",
        "button_bg":          "#d4500c",
        "button_fg":          "#ffffff",
        "button_hover":       "#b84309",
        "button_secondary":   "#ece5de",
        "menu_bg":            "#f2ede8",
        "menu_hover":         "#d4500c",
        "menu_fg":            "#2c2117",
        "menu_fg_hover":      "#ffffff",
        "menu_border":        "#ddd5cc",
        "selection":          "#f5c9a8",
        "scrollbar":          "transparent",
        "scrollbar_thumb":    "#c9bfb7",
        "status_bg":          "#f7f4f1",
        "status_border":      "#ece5de",
        "tag_bg":             "#fde8d8",
        "tag_fg":             "#d4500c",
        "code_bg":            "#f7f4f1",
        "code_fg":            "#2c2117",
        "tooltip_bg":         "#2c2117",
        "tooltip_fg":         "#f7f4f1",
        "shadow":             "#3c2a18",
        "badge_bg":           "#c0392b",
        "badge_fg":           "#ffffff",
        "progress_bg":        "#ece5de",
        "progress_fg":        "#d4500c",
        "link":               "#d4500c",
        "separator":          "#ddd5cc",
        "dock_bg":            "#f2ede8",
        "dock_border":        "#ddd5cc",
        "tl_red":             "#ff5f57",
        "tl_yellow":          "#ffbd2e",
        "tl_green":           "#28c940",
        "tl_red_h":           "#e0443e",
        "tl_yellow_h":        "#dfa020",
        "tl_green_h":         "#1aab29",
        "chart1":             "#d4500c",
        "chart2":             "#4a8c3f",
        "chart3":             "#e67e22",
        "chart4":             "#c0392b",
        "chart5":             "#8c5e3c",
        "vibrancy":           "#f2ede8",
    },

    # ── High Sierra (classic Aqua) ────────────────────────────────────────────
    "Aqua": {
        "desktop_bg":         "#1e5fa8",
        "menubar_bg":         "#e8e8e8",
        "menubar_fg":         "#000000",
        "menubar_border":     "#b8b8b8",
        "win_title_active":   "#d4d4d4",
        "win_title_inactive": "#efefef",
        "win_title_fg":       "#000000",
        "win_title_fg_in":    "#909090",
        "win_border":         "#a8a8a8",
        "win_border_active":  "#a8a8a8",
        "win_bg":             "#f0f0f0",
        "panel_bg":           "#f0f0f0",
        "panel_alt":          "#e8e8e8",
        "sidebar_bg":         "#e0e0e0",
        "accent":             "#4a90d9",
        "accent2":            "#7b68ee",
        "accent3":            "#5cb85c",
        "danger":             "#d9534f",
        "success":            "#5cb85c",
        "warning":            "#f0ad4e",
        "info":               "#4a90d9",
        "text":               "#000000",
        "text_muted":         "#555555",
        "text_dim":           "#b0b0b0",
        "text_inverse":       "#ffffff",
        "input_bg":           "#ffffff",
        "input_border":       "#aaaaaa",
        "input_focus":        "#4a90d9",
        "button_bg":          "#4a90d9",
        "button_fg":          "#ffffff",
        "button_hover":       "#357abd",
        "button_secondary":   "#e8e8e8",
        "menu_bg":            "#f0f0f0",
        "menu_hover":         "#4a90d9",
        "menu_fg":            "#000000",
        "menu_fg_hover":      "#ffffff",
        "menu_border":        "#c0c0c0",
        "selection":          "#b8d4f0",
        "scrollbar":          "#e8e8e8",
        "scrollbar_thumb":    "#9090a0",
        "status_bg":          "#f0f0f0",
        "status_border":      "#c0c0c0",
        "tag_bg":             "#d0e8f8",
        "tag_fg":             "#4a90d9",
        "code_bg":            "#f8f8f8",
        "code_fg":            "#000000",
        "tooltip_bg":         "#ffffe0",
        "tooltip_fg":         "#000000",
        "shadow":             "#000000",
        "badge_bg":           "#d9534f",
        "badge_fg":           "#ffffff",
        "progress_bg":        "#d8d8d8",
        "progress_fg":        "#4a90d9",
        "link":               "#0000ee",
        "separator":          "#c0c0c0",
        "dock_bg":            "#e8e8e8",
        "dock_border":        "#a8a8a8",
        "tl_red":             "#ff5f57",
        "tl_yellow":          "#ffbd2e",
        "tl_green":           "#28c940",
        "tl_red_h":           "#e0443e",
        "tl_yellow_h":        "#dfa020",
        "tl_green_h":         "#1aab29",
        "chart1":             "#4a90d9",
        "chart2":             "#5cb85c",
        "chart3":             "#f0ad4e",
        "chart4":             "#d9534f",
        "chart5":             "#7b68ee",
        "vibrancy":           "#f0f0f0",
    },

    # ── OLED Black ───────────────────────────────────────────────────────────
    "OLED Black": {
        "desktop_bg":         "#000000",
        "menubar_bg":         "#0a0a0a",
        "menubar_fg":         "#f5f5f7",
        "menubar_border":     "#1c1c1c",
        "win_title_active":   "#111111",
        "win_title_inactive": "#080808",
        "win_title_fg":       "#f5f5f7",
        "win_title_fg_in":    "#444444",
        "win_border":         "#1c1c1c",
        "win_border_active":  "#333333",
        "win_bg":             "#000000",
        "panel_bg":           "#0a0a0a",
        "panel_alt":          "#111111",
        "sidebar_bg":         "#080808",
        "accent":             "#0a84ff",
        "accent2":            "#5e5ce6",
        "accent3":            "#30d158",
        "danger":             "#ff453a",
        "success":            "#30d158",
        "warning":            "#ff9f0a",
        "info":               "#0a84ff",
        "text":               "#f5f5f7",
        "text_muted":         "#636366",
        "text_dim":           "#2c2c2e",
        "text_inverse":       "#000000",
        "input_bg":           "#111111",
        "input_border":       "#2c2c2e",
        "input_focus":        "#0a84ff",
        "button_bg":          "#0a84ff",
        "button_fg":          "#ffffff",
        "button_hover":       "#0070e0",
        "button_secondary":   "#1c1c1e",
        "menu_bg":            "#0a0a0a",
        "menu_hover":         "#0a84ff",
        "menu_fg":            "#f5f5f7",
        "menu_fg_hover":      "#ffffff",
        "menu_border":        "#2c2c2e",
        "selection":          "#0a3060",
        "scrollbar":          "transparent",
        "scrollbar_thumb":    "#3a3a3c",
        "status_bg":          "#0a0a0a",
        "status_border":      "#1c1c1e",
        "tag_bg":             "#051830",
        "tag_fg":             "#0a84ff",
        "code_bg":            "#0a0a0a",
        "code_fg":            "#f5f5f7",
        "tooltip_bg":         "#1c1c1e",
        "tooltip_fg":         "#f5f5f7",
        "shadow":             "#000000",
        "badge_bg":           "#ff453a",
        "badge_fg":           "#ffffff",
        "progress_bg":        "#1c1c1e",
        "progress_fg":        "#0a84ff",
        "link":               "#0a84ff",
        "separator":          "#1c1c1e",
        "dock_bg":            "#111111",
        "dock_border":        "#333333",
        "tl_red":             "#ff5f57",
        "tl_yellow":          "#ffbd2e",
        "tl_green":           "#28c940",
        "tl_red_h":           "#e0443e",
        "tl_yellow_h":        "#dfa020",
        "tl_green_h":         "#1aab29",
        "chart1":             "#0a84ff",
        "chart2":             "#30d158",
        "chart3":             "#ff9f0a",
        "chart4":             "#ff453a",
        "chart5":             "#5e5ce6",
        "vibrancy":           "#111111",
    },
}

# Active theme — mutable dict updated when user changes theme
T: Dict[str, str] = dict(THEMES["Monterey"])

def apply_theme(name: str) -> None:
    """Apply a named theme globally by updating the T dict in-place."""
    global T
    if name in THEMES:
        T.clear()
        T.update(THEMES[name])


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 3 — VIRTUAL FILE SYSTEM  (macOS-style paths)
# ─────────────────────────────────────────────────────────────────────────────

class VFSNode:
    """A single node (file or directory) in the virtual file system."""

    __slots__ = (
        "name", "is_dir", "_content", "children", "parent",
        "created", "modified", "accessed",
        "permissions", "owner", "group", "metadata",
        "bundle",     # macOS .app bundle flag
    )

    def __init__(
        self,
        name: str,
        is_dir: bool = False,
        content: str = "",
        parent: Optional["VFSNode"] = None,
        owner: str = "user",
        bundle: bool = False,
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
        self.permissions = "drwxr-xr-x" if is_dir else "-rw-r--r--"
        self.owner       = owner
        self.group       = "staff"
        self.metadata: Dict[str, Any] = {}
        self.bundle      = bundle

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value
        self.modified = time.time()

    def size(self) -> int:
        if self.is_dir:
            return sum(c.size() for c in self.children.values())
        return len(self._content.encode("utf-8"))

    def __repr__(self) -> str:
        kind = "DIR" if self.is_dir else "FILE"
        return f"<VFSNode {kind} {self.name!r}>"


class VFS:
    """
    Virtual Filesystem -- macOS-style tree with /Users/user as home.

    Files are ALSO persisted to a real folder on disk so that
    your data survives between sessions.

    Real-disk root (Windows default):
        C:/Users/<you>/MacPyOS           <- vfs /Users/user maps here
        C:/Users/<you>/MacPyOS/system   <- vfs /Applications, /Library ... map here

    Override at startup by setting the env-var  MACPYOS_ROOT  e.g.:
        set MACPYOS_ROOT=D:/MyMacPyOS && python macpyos.py
    """

    HOME          = "/Users/user"
    DEFAULT_USER  = "user"

    # -- Real-disk helpers -------------------------------------------------

    @staticmethod
    def _get_real_root() -> str:
        env = os.environ.get("MACPYOS_ROOT", "").strip()
        if env:
            return env
        home = os.path.expanduser("~")
        return os.path.join(home, "MacPyOS")

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
                        content = fh.read()
                    self._write_mem(vfs_file, content)
                except Exception:
                    pass

    # -- Memory-only helpers (used during init / restore) ------------------

    def _mkdir_mem(self, path: str) -> None:
        path = self.resolve(path)
        if path == "/":
            return
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        name = path.split("/")[-1]
        parent = self._get_node(parent_path)
        if parent is None:
            self._mkdir_mem(parent_path)
            parent = self._get_node(parent_path)
        if parent and name not in parent.children:
            node = VFSNode(name, is_dir=True, parent=parent)
            parent.children[name] = node
            parent.modified = time.time()

    def _write_mem(self, path: str, content: str, append: bool = False) -> None:
        path = self.resolve(path)
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        name = path.split("/")[-1]
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
            parent.modified = time.time()

    def __init__(self) -> None:
        self.root = VFSNode("/", is_dir=True, owner="root")
        self.cwd  = self.HOME
        # -- Real-disk root (created automatically) ------------------------
        self._real_root: str = self._get_real_root()
        os.makedirs(self._real_root, exist_ok=True)
        # -- Build default tree, then restore any saved files from disk ----
        self._build_tree()
        self._populate_defaults()
        self._load_from_disk()

    # -- tree builder ------------------------------------------------------

    def _build_tree(self) -> None:
        """Create the default macOS-like directory hierarchy."""
        dirs = [
            # macOS root dirs
            "/Applications",
            "/Library",
            "/Library/Application Support",
            "/Library/Preferences",
            "/Library/Caches",
            "/System",
            "/System/Library",
            "/private",
            "/private/tmp",
            "/private/var",
            "/Volumes",
            "/usr",
            "/usr/bin",
            "/usr/local",
            "/usr/local/bin",
            # Home dir structure
            "/Users",
            "/Users/user",
            "/Users/user/Desktop",
            "/Users/user/Documents",
            "/Users/user/Downloads",
            "/Users/user/Movies",
            "/Users/user/Music",
            "/Users/user/Music/Music",
            "/Users/user/Music/Music/Media",
            "/Users/user/Pictures",
            "/Users/user/Pictures/Photos Library.photoslibrary",
            "/Users/user/Public",
            "/Users/user/Library",
            "/Users/user/Library/Application Support",
            "/Users/user/Library/Preferences",
            "/Users/user/Library/Caches",
            "/Users/user/Developer",
            "/Users/user/Developer/Projects",
            "/Users/user/Developer/Scripts",
            "/Users/user/Spreadsheets",
            "/tmp",
        ]
        for d in dirs:
            self.mkdir(d)

    def _populate_defaults(self) -> None:
        """Create sample files inside the VFS."""
        default_files: Dict[str, str] = {

            "/Users/user/Documents/ReadMe.txt":
                "Welcome to MacPyOS — a macOS-style desktop simulation.\n\n"
                "Built with pure Python + Tkinter.\n"
                "No external dependencies required.\n\n"
                "Enjoy the Aqua experience!\n",

            "/Users/user/Documents/Notes.txt":
                "Meeting notes — 2025-01-15\n"
                "─────────────────────────\n"
                "• Q1 planning complete\n"
                "• Design review on Friday\n"
                "• Follow up with engineering team\n",

            "/Users/user/Documents/Ideas.md":
                "# Ideas\n\n"
                "## MacPyOS Features\n"
                "- [ ] Spotlight search\n"
                "- [x] Traffic light buttons\n"
                "- [x] Dock with magnification\n"
                "- [ ] Notification Center\n"
                "- [ ] Quick Look\n\n"
                "## Future Apps\n"
                "- FaceTime clone\n"
                "- Maps clone\n"
                "- Reminders\n",

            "/Users/user/Desktop/about.txt":
                f"MacPyOS v{MACPYOS_VERSION} ({MACPYOS_CODENAME})\n"
                "macOS-style Python Desktop OS\n"
                "Built with Tkinter\n"
                "Zero external dependencies\n",

            "/Users/user/Developer/Projects/hello.py":
                "#!/usr/bin/env python3\n"
                '"""Hello World — MacPyOS Demo Script"""\n\n\n'
                "def greet(name: str) -> str:\n"
                '    return f"Hello, {name}! Welcome to MacPyOS."\n\n\n'
                'if __name__ == "__main__":\n'
                '    print(greet("World"))\n',

            "/Users/user/Developer/Projects/fibonacci.py":
                "#!/usr/bin/env python3\n"
                '"""Fibonacci generator demo."""\n\n'
                "from typing import Generator\n\n\n"
                "def fibonacci(n: int) -> Generator[int, None, None]:\n"
                '    """Yield the first n Fibonacci numbers."""\n'
                "    a, b = 0, 1\n"
                "    for _ in range(n):\n"
                "        yield a\n"
                "        a, b = b, a + b\n\n\n"
                'if __name__ == "__main__":\n'
                "    result = list(fibonacci(20))\n"
                "    print('First 20 Fibonacci numbers:')\n"
                "    print(result)\n"
                "    print(f'Sum: {sum(result)}')\n",

            "/Users/user/Developer/Scripts/backup.sh":
                "#!/bin/bash\n"
                "# Simple backup script\n"
                "SRC=\"$HOME/Documents\"\n"
                "DST=\"$HOME/Downloads/backup_$(date +%Y%m%d)\"\n"
                "mkdir -p \"$DST\"\n"
                "cp -r \"$SRC\" \"$DST\"\n"
                'echo "Backup complete: $DST"\n',

            "/Users/user/Spreadsheets/budget.csv":
                "Month,Income,Expenses,Savings,Notes\n"
                "January,6500.00,3800.00,2700.00,Good start\n"
                "February,6500.00,3400.00,3100.00,Reduced dining out\n"
                "March,7000.00,3600.00,3400.00,Got a raise\n"
                "April,7000.00,4100.00,2900.00,Car repair\n"
                "May,7500.00,3700.00,3800.00,Bonus month\n"
                "June,7500.00,4200.00,3300.00,Vacation planned\n",

            "/Users/user/Music/playlist.m3u":
                "# MacPyOS Music Playlist\n"
                "#EXTM3U\n"
                "#EXTINF:213,Cyber Dreams\n"
                "Cyber_Dreams.mp3\n"
                "#EXTINF:187,Digital Rain\n"
                "Digital_Rain.mp3\n"
                "#EXTINF:234,Electric Pulse\n"
                "Electric_Pulse.mp3\n",

            "/Users/user/Library/Preferences/com.macpyos.plist":
                '<?xml version="1.0" encoding="UTF-8"?>\n'
                '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">\n'
                '<plist version="1.0">\n'
                '<dict>\n'
                '    <key>theme</key>\n'
                '    <string>Monterey</string>\n'
                '    <key>dock_position</key>\n'
                '    <string>bottom</string>\n'
                '    <key>show_boot</key>\n'
                '    <true/>\n'
                '</dict>\n'
                '</plist>\n',

            "/tmp/README":
                "This is the /tmp directory.\n"
                "Files here are temporary and may be cleared on restart.\n",
        }

        for path, content in default_files.items():
            self.write(path, content)

    # ── internal path helpers ─────────────────────────────────────────────────

    def resolve(self, path: str) -> str:
        """Resolve path to absolute canonical string."""
        if path.startswith("~"):
            path = self.HOME + path[1:]
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
        path        = self.resolve(path)
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
        name = path.split("/")[-1]
        parent = self._get_node(parent_path)
        if parent is None:
            self.makedirs(parent_path)
            parent = self._get_node(parent_path)
        if name in parent.children and parent.children[name].is_dir:
            raise IsADirectoryError(path)
        if append and name in parent.children:
            parent.children[name]._content += content
            parent.children[name].modified = time.time()
        else:
            node = VFSNode(name, is_dir=False, content=content, parent=parent)
            parent.children[name] = node
            parent.modified = time.time()
        # mirror to real disk
        final = (self._get_node(path)._content or "") if self._get_node(path) else content
        self._disk_write(path, final)

    def mkdir(self, path: str) -> None:
        path = self.resolve(path)
        if path == "/":
            return
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        name = path.split("/")[-1]
        parent = self._get_node(parent_path)
        if parent is None:
            raise FileNotFoundError(f"No such directory: {parent_path}")
        if name not in parent.children:
            node = VFSNode(name, is_dir=True, parent=parent)
            parent.children[name] = node
            parent.modified = time.time()
        # mirror to real disk
        self._disk_mkdir(path)

    def makedirs(self, path: str) -> None:
        path = self.resolve(path)
        parts = [p for p in path.split("/") if p]
        current = "/"
        for part in parts:
            next_path = current.rstrip("/") + "/" + part
            if not self.exists(next_path):
                self.mkdir(next_path)
            current = next_path

    def remove(self, path: str) -> None:
        rpath = self.resolve(path)
        parent, name = self._parent_and_name(path)
        if name not in parent.children:
            raise FileNotFoundError(path)
        del parent.children[name]
        parent.modified = time.time()
        # mirror to real disk
        self._disk_delete(rpath)

    def rename(self, src: str, dst: str) -> None:
        src_r = self.resolve(src)
        dst_r = self.resolve(dst)
        src_parent, src_name = self._parent_and_name(src)
        dst_parent, dst_name = self._parent_and_name(dst)
        if src_name not in src_parent.children:
            raise FileNotFoundError(src)
        node = src_parent.children.pop(src_name)
        node.name = dst_name
        node.parent = dst_parent
        dst_parent.children[dst_name] = node
        src_parent.modified = time.time()
        dst_parent.modified = time.time()
        # mirror to real disk
        self._disk_rename(src_r, dst_r)

    def copy(self, src: str, dst: str) -> None:
        src_node = self._get_node(src)
        if src_node is None:
            raise FileNotFoundError(src)
        if src_node.is_dir:
            self.mkdir(dst)
            for child_name in src_node.children:
                self.copy(src + "/" + child_name, dst + "/" + child_name)
        else:
            self.write(dst, src_node._content)

    def stat(self, path: str) -> Dict[str, Any]:
        n = self._get_node(path)
        if n is None:
            raise FileNotFoundError(path)
        return {
            "name":        n.name,
            "is_dir":      n.is_dir,
            "size":        n.size(),
            "created":     n.created,
            "modified":    n.modified,
            "accessed":    n.accessed,
            "permissions": n.permissions,
            "owner":       n.owner,
            "group":       n.group,
        }

    def find(self, root: str, name_pattern: str) -> List[str]:
        results: List[str] = []
        def _walk(path: str) -> None:
            try:
                for entry in self.listdir(path):
                    full = path.rstrip("/") + "/" + entry
                    if re.search(name_pattern, entry, re.IGNORECASE):
                        results.append(full)
                    if self.isdir(full):
                        _walk(full)
            except Exception:
                pass
        _walk(root)
        return results

    def tree(self, path: str = "/", prefix: str = "", max_depth: int = 4, _depth: int = 0) -> str:
        if _depth > max_depth:
            return ""
        lines: List[str] = []
        try:
            entries = self.listdir(path)
        except Exception:
            return ""
        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)
            connector = "└── " if is_last else "├── "
            full = path.rstrip("/") + "/" + entry
            icon = "📁 " if self.isdir(full) else "📄 "
            lines.append(prefix + connector + icon + entry)
            if self.isdir(full):
                extension = "    " if is_last else "│   "
                lines.append(self.tree(full, prefix + extension, max_depth, _depth + 1))
        return "\n".join(filter(None, lines))

    @property
    def home(self) -> str:
        return self.HOME


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 4 — USER MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class UserManager:
    """Multi-user authentication with password hashing."""

    def __init__(self) -> None:
        self._users: Dict[str, Dict[str, Any]] = {}
        self._current: Optional[str]           = None
        self._add("user",  "user",  "User",  "🧑")
        self._add("admin", "admin", "Admin", "👑")
        self._add("guest", "",      "Guest", "👤")

    def _hash(self, pw: str) -> str:
        return hashlib.sha256(pw.encode()).hexdigest()

    def _add(self, username: str, password: str, display: str, avatar: str) -> None:
        self._users[username] = {
            "password":     self._hash(password),
            "display_name": display,
            "avatar":       avatar,
            "home":         f"/Users/{username}",
            "shell":        "/bin/zsh",
            "groups":       ["staff", "admin"] if username == "admin" else ["staff"],
            "last_login":   None,
            "created":      time.time(),
        }

    def login(self, username: str, password: str) -> bool:
        if username not in self._users:
            return False
        if self._users[username]["password"] == self._hash(password):
            self._current = username
            self._users[username]["last_login"] = time.time()
            return True
        return False

    def logout(self) -> None:
        self._current = None

    def current_user(self) -> Optional[str]:
        return self._current

    def display_name(self, username: Optional[str] = None) -> str:
        u = username or self._current or ""
        return self._users.get(u, {}).get("display_name", u)

    def avatar(self, username: Optional[str] = None) -> str:
        u = username or self._current or ""
        return self._users.get(u, {}).get("avatar", "👤")

    def is_admin(self, username: Optional[str] = None) -> bool:
        u = username or self._current or ""
        return "admin" in self._users.get(u, {}).get("groups", [])

    def list_users(self) -> List[str]:
        return list(self._users.keys())

    def home_dir(self, username: Optional[str] = None) -> str:
        u = username or self._current or "user"
        return self._users.get(u, {}).get("home", f"/Users/{u}")

    def change_password(self, username: str, old_pw: str, new_pw: str) -> bool:
        if username not in self._users:
            return False
        if self._users[username]["password"] != self._hash(old_pw):
            return False
        self._users[username]["password"] = self._hash(new_pw)
        return True


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 5 — PROCESS MANAGER  (simulated)
# ─────────────────────────────────────────────────────────────────────────────

class Process:
    """Represents a running process."""

    _next_pid: int = 100   # macOS PIDs start higher

    def __init__(self, name: str, app: str = "", user: str = "user") -> None:
        Process._next_pid += random.randint(1, 8)
        self.pid        = Process._next_pid
        self.name       = name
        self.app        = app
        self.user       = user
        self.cpu        = random.uniform(0.0, 2.0)
        self.ram        = random.uniform(20, 200)   # MB
        self.started    = time.time()
        self.state      = "running"
        self._tick      = 0

    def update(self) -> None:
        self._tick += 1
        # Gentle random walk for CPU
        delta = random.uniform(-0.5, 0.5)
        self.cpu = max(0.0, min(100.0, self.cpu + delta))
        # RAM drifts slowly
        self.ram = max(10, self.ram + random.uniform(-2, 2))

    @property
    def uptime(self) -> str:
        s = int(time.time() - self.started)
        h, rem = divmod(s, 3600)
        m, sec = divmod(rem, 60)
        if h:
            return f"{h}:{m:02d}:{sec:02d}"
        return f"{m}:{sec:02d}"


class ProcessManager:
    """Tracks all simulated processes."""

    def __init__(self) -> None:
        self._procs: Dict[int, Process] = {}
        self._lock  = threading.Lock()
        self._spawn_system_procs()

    def _spawn_system_procs(self) -> None:
        """Spawn macOS-like background system processes."""
        system_procs = [
            ("kernel_task",   "kernel_task"),
            ("launchd",       "launchd"),
            ("WindowServer",  "WindowServer"),
            ("Dock",          "Dock"),
            ("Finder",        "Finder"),
            ("SystemUIServer","SystemUIServer"),
            ("coreaudiod",    "coreaudiod"),
            ("cloudd",        "cloudd"),
            ("mds",           "mds"),
            ("mdworker",      "mdworker"),
        ]
        for name, app in system_procs:
            p = Process(name, app, user="root")
            p.cpu = random.uniform(0.0, 1.5)
            p.ram = random.uniform(30, 400)
            with self._lock:
                self._procs[p.pid] = p

    def spawn(self, name: str, app: str = "", user: str = "user") -> Process:
        p = Process(name, app, user)
        with self._lock:
            self._procs[p.pid] = p
        return p

    def kill(self, pid: int) -> bool:
        with self._lock:
            if pid in self._procs:
                self._procs[pid].state = "zombie"
                del self._procs[pid]
                return True
        return False

    def list_all(self) -> List[Process]:
        with self._lock:
            return list(self._procs.values())

    def update_all(self) -> None:
        with self._lock:
            for p in self._procs.values():
                p.update()

    def total_cpu(self) -> float:
        with self._lock:
            return min(100.0, sum(p.cpu for p in self._procs.values()))

    def total_ram(self) -> float:
        with self._lock:
            return sum(p.ram for p in self._procs.values())


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 6 — SETTINGS
# ─────────────────────────────────────────────────────────────────────────────

class Settings:
    """Persistent-like key-value store for OS preferences."""

    DEFAULTS: Dict[str, Any] = {
        "theme":              "Monterey",
        "accent_color":       "#007aff",
        "wallpaper":          "gradient_blue",
        "dock_position":      "bottom",
        "dock_autohide":      False,
        "dock_magnification": True,
        "show_boot":          True,
        "menu_bar_clock":     True,
        "font_size":          13,
        "font_ui":            "SF Pro Display",
        "font_mono":          "SF Mono",
        "sound_enabled":      True,
        "dark_mode":          False,
        "reduce_motion":      False,
        "show_scroll_bars":   "automatic",
        "click_in_scroll":    True,
        "natural_scrolling":  True,
        "tap_to_click":       True,
        "screen_saver":       "flurry",
        "screen_saver_delay": 5,
        "require_password":   True,
        "notifications":      True,
        "do_not_disturb":     False,
        "timezone":           "America/New_York",
        "language":           "English",
        "date_format":        "medium",
        "time_format":        "12h",
        "username":           "user",
    }

    def __init__(self) -> None:
        self._data: Dict[str, Any] = dict(self.DEFAULTS)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def reset(self, key: str) -> None:
        if key in self.DEFAULTS:
            self._data[key] = self.DEFAULTS[key]

    def reset_all(self) -> None:
        self._data = dict(self.DEFAULTS)

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._data)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 7 — CLIPBOARD
# ─────────────────────────────────────────────────────────────────────────────

class Clipboard:
    """System clipboard supporting text and file references."""

    def __init__(self) -> None:
        self._text:      str             = ""
        self._files:     List[str]       = []
        self._mode:      str             = "text"    # "text" | "copy" | "cut"
        self._history:   List[str]       = []
        self._max_hist:  int             = 20

    def copy_text(self, text: str) -> None:
        self._text = text
        self._files = []
        self._mode  = "text"
        self._push_history(text)

    def copy_files(self, paths: List[str], cut: bool = False) -> None:
        self._files = list(paths)
        self._text  = ""
        self._mode  = "cut" if cut else "copy"

    def paste_text(self) -> str:
        return self._text

    def paste_files(self) -> Tuple[List[str], str]:
        return self._files, self._mode

    def clear(self) -> None:
        self._text  = ""
        self._files = []
        self._mode  = "text"

    def has_text(self) -> bool:
        return bool(self._text)

    def has_files(self) -> bool:
        return bool(self._files)

    def _push_history(self, text: str) -> None:
        if text and (not self._history or self._history[-1] != text):
            self._history.append(text)
            if len(self._history) > self._max_hist:
                self._history.pop(0)

    def history(self) -> List[str]:
        return list(reversed(self._history))


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 8 — NOTIFICATION MANAGER  (macOS banner style)
# ─────────────────────────────────────────────────────────────────────────────

class Notification:
    """One notification banner."""

    def __init__(self, title: str, body: str, icon: str = "🔔",
                 app: str = "MacPyOS", duration: float = 4.0) -> None:
        self.id       = str(uuid.uuid4())[:8]
        self.title    = title
        self.body     = body
        self.icon     = icon
        self.app      = app
        self.duration = duration
        self.ts       = time.time()
        self.read     = False


class NotificationManager:
    """Queues and delivers notification banners."""

    def __init__(self) -> None:
        self._queue:   queue.Queue    = queue.Queue()
        self._history: List[Notification] = []
        self._max_hist = 50
        self._callback: Optional[Callable] = None

    def send(self, title: str, body: str, icon: str = "🔔",
             app: str = "MacPyOS", duration: float = 4.0) -> None:
        n = Notification(title, body, icon, app, duration)
        self._history.append(n)
        if len(self._history) > self._max_hist:
            self._history.pop(0)
        self._queue.put(n)
        if self._callback:
            self._callback(n)

    def set_callback(self, fn: Callable) -> None:
        self._callback = fn

    def poll(self) -> Optional[Notification]:
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def unread_count(self) -> int:
        return sum(1 for n in self._history if not n.read)

    def mark_all_read(self) -> None:
        for n in self._history:
            n.read = True

    def get_history(self) -> List[Notification]:
        return list(reversed(self._history))

    def clear_history(self) -> None:
        self._history.clear()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 9 — HELPER WIDGETS
# ─────────────────────────────────────────────────────────────────────────────

def make_tooltip(widget: tk.Widget, text: str, delay: int = 600) -> None:
    """Attach a macOS-style tooltip to a widget."""
    tip_win: List[Optional[tk.Toplevel]] = [None]
    after_id: List[Optional[str]] = [None]

    def show(_: tk.Event) -> None:
        def _show() -> None:
            x = widget.winfo_rootx() + widget.winfo_width() // 2
            y = widget.winfo_rooty() + widget.winfo_height() + 4
            tip = tk.Toplevel(widget)
            tip.wm_overrideredirect(True)
            tip.wm_geometry(f"+{x}+{y}")
            tip.configure(bg=T["tooltip_bg"])
            lbl = tk.Label(
                tip, text=text,
                bg=T["tooltip_bg"], fg=T["tooltip_fg"],
                font=(FONT_UI, 11),
                padx=8, pady=4,
            )
            lbl.pack()
            tip_win[0] = tip
        after_id[0] = widget.after(delay, _show)

    def hide(_: tk.Event) -> None:
        if after_id[0]:
            widget.after_cancel(after_id[0])
            after_id[0] = None
        if tip_win[0]:
            tip_win[0].destroy()
            tip_win[0] = None

    widget.bind("<Enter>", show, add="+")
    widget.bind("<Leave>", hide, add="+")


class MacScrolledFrame(tk.Frame):
    """A scrollable frame with macOS-style thin overlay scrollbar."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        bg = kwargs.pop("bg", T["win_bg"])
        super().__init__(parent, bg=bg, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(
            self, orient="vertical",
            command=self.canvas.yview,
            width=6,
            troughcolor=T.get("panel_bg", "#f5f5f5"),
            bg=T.get("scrollbar_thumb", "#c7c7cc"),
            relief="flat", bd=0,
        )
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win_id = self.canvas.create_window(
            (0, 0), window=self.inner, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.inner.bind("<Configure>", self._on_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.inner.bind("<MouseWheel>", self._on_mousewheel)

    def _on_configure(self, _: tk.Event) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, e: tk.Event) -> None:
        self.canvas.itemconfig(self._win_id, width=e.width)

    def _on_mousewheel(self, e: tk.Event) -> None:
        self.canvas.yview_scroll(-1 * (e.delta // 120), "units")


class MacButton(tk.Label):
    """A styled macOS-like button (uses Label for full styling control)."""

    def __init__(self, parent: tk.Widget, text: str = "",
                 command: Optional[Callable] = None,
                 style: str = "primary",   # "primary" | "secondary" | "destructive"
                 **kwargs) -> None:
        bg_map = {
            "primary":     T["button_bg"],
            "secondary":   T.get("button_secondary", T["panel_alt"]),
            "destructive": T["danger"],
        }
        fg_map = {
            "primary":     T.get("button_fg", "#ffffff"),
            "secondary":   T["text"],
            "destructive": "#ffffff",
        }
        bg = bg_map.get(style, T["button_bg"])
        fg = fg_map.get(style, "#ffffff")
        super().__init__(
            parent, text=text, bg=bg, fg=fg,
            font=(FONT_UI, 12),
            padx=14, pady=6,
            cursor="hand2",
            **kwargs
        )
        self._bg = bg
        self._hover = T.get("button_hover", "#0066d6")
        self._command = command
        self.bind("<Enter>", lambda _: self.configure(bg=self._hover))
        self.bind("<Leave>", lambda _: self.configure(bg=self._bg))
        self.bind("<Button-1>", self._click)

    def _click(self, _: tk.Event) -> None:
        if self._command:
            self._command()


class MacEntry(tk.Entry):
    """macOS-style text entry with focus ring."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        kwargs.setdefault("bg", T["input_bg"])
        kwargs.setdefault("fg", T["text"])
        kwargs.setdefault("insertbackground", T["text"])
        kwargs.setdefault("relief", "flat")
        kwargs.setdefault("font", (FONT_UI, 13))
        kwargs.setdefault("highlightthickness", 1)
        kwargs.setdefault("highlightbackground", T["input_border"])
        kwargs.setdefault("highlightcolor", T["input_focus"])
        super().__init__(parent, **kwargs)


class MacLabel(tk.Label):
    """Convenience label pre-styled for the active theme."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        kwargs.setdefault("bg", T["win_bg"])
        kwargs.setdefault("fg", T["text"])
        kwargs.setdefault("font", (FONT_UI, 13))
        super().__init__(parent, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 10 — BASE WINDOW  (macOS traffic-light titlebar)
# ─────────────────────────────────────────────────────────────────────────────

class BaseWin:
    """
    A floating, draggable, resizable window with a macOS-style titlebar.

    Traffic light buttons:
      ● Red    — close
      ● Yellow — minimise (iconify to Dock)
      ● Green  — full-screen / maximise toggle
    """

    # Class-level z-order tracking
    _z_stack: List["BaseWin"] = []

    def __init__(
        self,
        wm: "WM",
        title: str       = "Window",
        w: int           = 680,
        h: int           = 480,
        icon: str        = "🪟",
        resizable: bool  = True,
        min_w: int       = WIN_MIN_W,
        min_h: int       = WIN_MIN_H,
    ) -> None:
        self.wm        = wm
        self.root      = wm.root
        self.title_str = title
        self.icon      = icon
        self.resizable = resizable
        self.min_w     = min_w
        self.min_h     = min_h
        self._closed   = False
        self._minimised= False
        self._maximised= False
        self._prev_geo : Optional[Tuple[int,int,int,int]] = None
        self._proc     : Optional[Process] = wm.procs.spawn(title, title)

        # ── outer frame (sits on desktop canvas) ──────────────────────────────
        self.frame = tk.Frame(
            wm.desktop,
            bg=T["win_border"],
            bd=0,
            highlightthickness=0,
        )

        # ── title bar ─────────────────────────────────────────────────────────
        self.titlebar = tk.Frame(
            self.frame,
            bg=T["win_title_active"],
            height=TITLEBAR_H,
        )
        self.titlebar.pack(fill="x")
        self.titlebar.pack_propagate(False)

        # Traffic-light container
        tl_frame = tk.Frame(self.titlebar, bg=T["win_title_active"])
        tl_frame.place(x=TL_X, rely=0.5, anchor="w")

        def _tl_btn(color_key: str, hover_key: str) -> tk.Label:
            c = T[color_key]
            lbl = tk.Label(
                tl_frame,
                bg=c, width=TL_SIZE, height=TL_SIZE,
                cursor="hand2",
            )
            lbl.pack(side="left", padx=2)
            lbl.bind("<Enter>",  lambda _, k=hover_key, l=lbl: l.configure(bg=T[k]))
            lbl.bind("<Leave>",  lambda _, k=color_key, l=lbl: l.configure(bg=T[k]))
            return lbl

        self.btn_close = _tl_btn("tl_red",    "tl_red_h")
        self.btn_min   = _tl_btn("tl_yellow", "tl_yellow_h")
        self.btn_max   = _tl_btn("tl_green",  "tl_green_h")

        self.btn_close.bind("<Button-1>", lambda _: self.close())
        self.btn_min.bind  ("<Button-1>", lambda _: self.minimise())
        self.btn_max.bind  ("<Button-1>", lambda _: self.toggle_maximise())

        # Title label (centred)
        self.title_lbl = tk.Label(
            self.titlebar,
            text=f"{icon}  {title}",
            bg=T["win_title_active"],
            fg=T["win_title_fg"],
            font=(FONT_UI, 13),
        )
        self.title_lbl.place(relx=0.5, rely=0.5, anchor="center")

        # ── client area ───────────────────────────────────────────────────────
        self.client = tk.Frame(self.frame, bg=T["win_bg"])
        self.client.pack(fill="both", expand=True)

        # ── resize grip (bottom-right) ────────────────────────────────────────
        if self.resizable:
            self.grip = tk.Label(
                self.frame, text="⌟",
                bg=T["win_bg"],
                fg=T["text_muted"],
                font=(FONT_UI, 14),
                cursor="sizing",
            )
            self.grip.place(relx=1.0, rely=1.0, anchor="se")

        # ── place on desktop ──────────────────────────────────────────────────
        # Stagger new windows
        offset = len(BaseWin._z_stack) * 24 % 200
        self._x = 80  + offset
        self._y = 60  + offset
        self._w = w
        self._h = h
        self.frame.place(x=self._x, y=self._y, width=self._w, height=self._h)

        # ── drag / resize bindings ────────────────────────────────────────────
        self._drag_data: Dict[str, Any] = {}
        for widget in (self.titlebar, self.title_lbl):
            widget.bind("<ButtonPress-1>",   self._drag_start)
            widget.bind("<B1-Motion>",       self._drag_motion)
            widget.bind("<ButtonRelease-1>", self._drag_end)
            widget.bind("<Double-Button-1>", lambda _: self.toggle_maximise())

        if self.resizable:
            self.grip.bind("<ButtonPress-1>",   self._resize_start)
            self.grip.bind("<B1-Motion>",       self._resize_motion)
            self.grip.bind("<ButtonRelease-1>", self._resize_end)

        # Focus / raise on click
        self.frame.bind("<ButtonPress-1>", lambda _: self.raise_win(), add="+")
        self.client.bind("<ButtonPress-1>", lambda _: self.raise_win(), add="+")
        self.titlebar.bind("<ButtonPress-1>", lambda _: self.raise_win(), add="+")

        BaseWin._z_stack.append(self)
        self.raise_win()

        # Register with WM
        wm.register_win(self)

    # ── drag implementation ───────────────────────────────────────────────────

    def _drag_start(self, e: tk.Event) -> None:
        self._drag_data = {"x": e.x_root, "y": e.y_root,
                           "ox": self._x,  "oy": self._y}
        self.raise_win()

    def _drag_motion(self, e: tk.Event) -> None:
        if not self._drag_data or self._maximised:
            return
        dx = e.x_root - self._drag_data["x"]
        dy = e.y_root - self._drag_data["y"]
        self._x = max(0, self._drag_data["ox"] + dx)
        self._y = max(MENUBAR_H, self._drag_data["oy"] + dy)
        self.frame.place(x=self._x, y=self._y)

    def _drag_end(self, _: tk.Event) -> None:
        self._drag_data = {}

    # ── resize implementation ─────────────────────────────────────────────────

    def _resize_start(self, e: tk.Event) -> None:
        self._drag_data = {"x": e.x_root, "y": e.y_root,
                           "ow": self._w,  "oh": self._h}
        self.raise_win()

    def _resize_motion(self, e: tk.Event) -> None:
        if not self._drag_data:
            return
        dw = e.x_root - self._drag_data["x"]
        dh = e.y_root - self._drag_data["y"]
        self._w = max(self.min_w, self._drag_data["ow"] + dw)
        self._h = max(self.min_h, self._drag_data["oh"] + dh)
        self.frame.place(width=self._w, height=self._h)

    def _resize_end(self, _: tk.Event) -> None:
        self._drag_data = {}

    # ── window actions ────────────────────────────────────────────────────────

    def raise_win(self) -> None:
        self.frame.lift()
        if self in BaseWin._z_stack:
            BaseWin._z_stack.remove(self)
        BaseWin._z_stack.append(self)
        # Dim other windows' titlebars
        for win in BaseWin._z_stack[:-1]:
            win.titlebar.configure(bg=T["win_title_inactive"])
            win.title_lbl.configure(
                bg=T["win_title_inactive"],
                fg=T["win_title_fg_in"],
            )
        self.titlebar.configure(bg=T["win_title_active"])
        self.title_lbl.configure(
            bg=T["win_title_active"],
            fg=T["win_title_fg"],
        )

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._proc:
            self.wm.procs.kill(self._proc.pid)
        self.wm.unregister_win(self)
        if self in BaseWin._z_stack:
            BaseWin._z_stack.remove(self)
        self.frame.destroy()
        self._on_close()

    def _on_close(self) -> None:
        """Override in subclasses for cleanup."""
        pass

    def minimise(self) -> None:
        self._minimised = True
        self.frame.place_forget()
        self.wm.taskbar.add_minimised(self)

    def restore(self) -> None:
        self._minimised = False
        self.frame.place(x=self._x, y=self._y, width=self._w, height=self._h)
        self.raise_win()
        self.wm.taskbar.remove_minimised(self)

    def toggle_maximise(self) -> None:
        if self._maximised:
            # restore
            if self._prev_geo:
                self._x, self._y, self._w, self._h = self._prev_geo
            self.frame.place(x=self._x, y=self._y, width=self._w, height=self._h)
            self._maximised = False
        else:
            self._prev_geo = (self._x, self._y, self._w, self._h)
            self._x = 0
            self._y = MENUBAR_H
            self._w = SCREEN_W
            self._h = SCREEN_H - MENUBAR_H - DOCK_H
            self.frame.place(x=0, y=MENUBAR_H, width=self._w, height=self._h)
            self._maximised = True

    def set_title(self, title: str) -> None:
        self.title_str = title
        self.title_lbl.configure(text=f"{self.icon}  {title}")
        self.frame.update_idletasks()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 11 — WINDOW MANAGER  (WM)
# ─────────────────────────────────────────────────────────────────────────────

class WM:
    """
    Central Window Manager — owns:
      • The Tk root window
      • Desktop canvas (wallpaper + icons)
      • Menu bar (top)
      • Dock (bottom)
      • Notification banners
      • All open windows
    """

    def __init__(
        self,
        root:     tk.Tk,
        vfs:      VFS,
        users:    UserManager,
        procs:    ProcessManager,
        notifs:   NotificationManager,
        settings: Settings,
        clip:     Clipboard,
    ) -> None:
        self.root     = root
        self.vfs      = vfs
        self.users    = users
        self.procs    = procs
        self.notifs   = notifs
        self.settings = settings
        self.clip     = clip
        self._wins:   List[BaseWin]        = []
        self._spotlight_open: bool         = False

        # ── desktop canvas ────────────────────────────────────────────────────
        self.desktop = tk.Canvas(
            root,
            bg=T["desktop_bg"],
            highlightthickness=0,
            cursor="arrow",
        )
        self.desktop.place(x=0, y=MENUBAR_H,
                           relwidth=1,
                           height=self.root.winfo_height() - MENUBAR_H - DOCK_H)

        # ── draw wallpaper ────────────────────────────────────────────────────
        self._draw_wallpaper()

        # ── desktop icons ─────────────────────────────────────────────────────
        self._draw_desktop_icons()

        # ── right-click desktop menu ──────────────────────────────────────────
        self.desktop.bind("<Button-2>", self._desktop_rclick)
        self.desktop.bind("<Button-3>", self._desktop_rclick)

        # ── menu bar ──────────────────────────────────────────────────────────
        self.menubar = MenuBar(self)

        # ── dock ──────────────────────────────────────────────────────────────
        self.taskbar = Dock(self)   # named taskbar for compatibility

        # ── notification banners ──────────────────────────────────────────────
        self.notifs.set_callback(self._on_notification)
        self._banner_y = MENUBAR_H + 8

        # ── process ticker ────────────────────────────────────────────────────
        self._tick_procs()

        # ── Spotlight overlay ─────────────────────────────────────────────────
        self._spotlight_frame: Optional[tk.Frame] = None

    # ── wallpaper ─────────────────────────────────────────────────────────────

    def _draw_wallpaper(self) -> None:
        self.desktop.delete("wallpaper")
        wp = self.settings.get("wallpaper", "gradient_blue")
        dw = SCREEN_W
        dh = SCREEN_H - MENUBAR_H - DOCK_H

        if wp == "gradient_blue":
            # macOS Monterey-style blue/purple gradient
            steps = 40
            for i in range(steps):
                t = i / steps
                r = int(0x1e + (0x6b - 0x1e) * t)
                g = int(0x6b + (0x1e - 0x6b) * t)
                b = int(0xb8 + (0x88 - 0xb8) * t)
                color = f"#{r:02x}{g:02x}{b:02x}"
                y0 = int(dh * i / steps)
                y1 = int(dh * (i + 1) / steps)
                self.desktop.create_rectangle(
                    0, y0, dw, y1, fill=color, outline="", tags="wallpaper"
                )
        elif wp == "gradient_sunset":
            colors = ["#ff6b6b", "#ffa94d", "#ffdb58", "#ff6b9d"]
            steps  = 40
            for i in range(steps):
                t  = i / steps
                ci = int(t * (len(colors) - 1))
                ci = min(ci, len(colors) - 2)
                lt = t * (len(colors) - 1) - ci
                c1 = colors[ci];  c2 = colors[ci + 1]
                def lerp_hex(a: str, b: str, f: float) -> str:
                    ar, ag, ab = int(a[1:3],16), int(a[3:5],16), int(a[5:7],16)
                    br, bg, bb = int(b[1:3],16), int(b[3:5],16), int(b[5:7],16)
                    return f"#{int(ar+(br-ar)*f):02x}{int(ag+(bg-ag)*f):02x}{int(ab+(bb-ab)*f):02x}"
                color = lerp_hex(c1, c2, lt)
                y0 = int(dh * i / steps)
                y1 = int(dh * (i + 1) / steps)
                self.desktop.create_rectangle(
                    0, y0, dw, y1, fill=color, outline="", tags="wallpaper"
                )
        elif wp == "solid_dark":
            self.desktop.create_rectangle(
                0, 0, dw, dh, fill="#1c1c1e", outline="", tags="wallpaper"
            )
        elif wp == "solid_sand":
            self.desktop.create_rectangle(
                0, 0, dw, dh, fill="#c8b89a", outline="", tags="wallpaper"
            )
        else:
            self.desktop.create_rectangle(
                0, 0, dw, dh, fill=T["desktop_bg"], outline="", tags="wallpaper"
            )

    # ── desktop icons ─────────────────────────────────────────────────────────

    def _draw_desktop_icons(self) -> None:
        self.desktop.delete("icon")
        icons = [
            ("#007aff", "F",  "Finder",   self.open_finder),
            ("#636366", "T",  "Trash",    self._open_trash),
            ("#ff9500", "E",  "TextEdit", self.open_textedit),
            ("#1c1c1e", ">_", "Terminal", self.open_terminal),
        ]
        col_w   = ICON_SIZE + 20
        row_h   = ICON_SIZE + 32
        start_x = SCREEN_W - col_w - 20
        start_y = 20
        for i, (color, letter, label, cmd) in enumerate(icons):
            cx  = start_x + col_w // 2
            cy  = start_y + i * row_h + ICON_SIZE // 2
            tag = f"icon_{i}"
            r   = 14
            x0, y0 = cx - 32, cy - 32
            x1, y1 = cx + 32, cy + 32
            # Rounded rectangle icon
            self.desktop.create_rectangle(x0+r,y0,x1-r,y1, fill=color,outline="",tags=("icon",tag))
            self.desktop.create_rectangle(x0,y0+r,x1,y1-r, fill=color,outline="",tags=("icon",tag))
            self.desktop.create_oval(x0,y0,x0+2*r,y0+2*r, fill=color,outline="",tags=("icon",tag))
            self.desktop.create_oval(x1-2*r,y0,x1,y0+2*r, fill=color,outline="",tags=("icon",tag))
            self.desktop.create_oval(x0,y1-2*r,x0+2*r,y1, fill=color,outline="",tags=("icon",tag))
            self.desktop.create_oval(x1-2*r,y1-2*r,x1,y1, fill=color,outline="",tags=("icon",tag))
            self.desktop.create_text(cx, cy, text=letter,
                font=(FONT_UI, 18, "bold"), fill="#ffffff", tags=("icon", tag))
            self.desktop.create_text(cx, y1+6, text=label,
                font=(FONT_UI, 11), fill="#ffffff",
                tags=("icon", tag+"_lbl"), anchor="n")
            self.desktop.tag_bind(tag,         "<Double-Button-1>", lambda _,c=cmd: c())
            self.desktop.tag_bind(tag+"_lbl",  "<Double-Button-1>", lambda _,c=cmd: c())

    def _open_trash(self) -> None:
        self.notifs.send("Trash", "Trash is empty.", icon="🗑️")

    # ── desktop right-click ───────────────────────────────────────────────────

    def _desktop_rclick(self, e: tk.Event) -> None:
        menu = tk.Menu(self.root, tearoff=False,
                       bg=T["menu_bg"], fg=T["menu_fg"],
                       activebackground=T["menu_hover"],
                       activeforeground=T["menu_fg_hover"],
                       font=(FONT_UI, 13), bd=0,
                       relief="flat")
        menu.add_command(label="New Folder",          command=lambda: self._new_desktop_folder(e.x, e.y))
        menu.add_command(label="New Text Document",   command=self.open_textedit)
        menu.add_separator()
        menu.add_command(label="Change Wallpaper…",   command=self._change_wallpaper_menu)
        menu.add_separator()
        menu.add_command(label="Get Info",            command=self._show_get_info)
        menu.add_command(label="Show View Options",   command=self._show_view_options)
        menu.add_separator()
        menu.add_command(label="Open Terminal Here",  command=self.open_terminal)
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def _new_desktop_folder(self, x: int, y: int) -> None:
        name = simpledialog.askstring("New Folder", "Folder name:", parent=self.root)
        if name:
            path = f"/Users/user/Desktop/{name}"
            self.vfs.makedirs(path)
            self.notifs.send("Finder", f"Folder '{name}' created on Desktop.", icon="📁")

    def _change_wallpaper_menu(self) -> None:
        self.open_preferences(panel="Desktop & Screen Saver")

    def _show_get_info(self) -> None:
        self.notifs.send("MacPyOS", f"Version {MACPYOS_VERSION} ({MACPYOS_CODENAME})", icon="ℹ️")

    def _show_view_options(self) -> None:
        self.notifs.send("View Options", "Coming soon.", icon="👁️")

    # ── notification banner ───────────────────────────────────────────────────

    def _on_notification(self, n: Notification) -> None:
        """Show a macOS-style banner in top-right."""
        if not self.settings.get("notifications", True):
            return
        if self.settings.get("do_not_disturb", False):
            return
        banner = tk.Frame(
            self.root,
            bg=T.get("vibrancy", T["panel_bg"]),
            bd=0,
            highlightthickness=1,
            highlightbackground=T["separator"],
        )
        icon_lbl = tk.Label(banner, text=n.icon,
                            bg=T.get("vibrancy", T["panel_bg"]),
                            font=(FONT_EMOJI, 22), padx=8, pady=8)
        icon_lbl.pack(side="left")
        text_frame = tk.Frame(banner, bg=T.get("vibrancy", T["panel_bg"]))
        text_frame.pack(side="left", fill="x", expand=True, pady=6, padx=(0, 10))
        tk.Label(text_frame, text=n.app,
                 bg=T.get("vibrancy", T["panel_bg"]),
                 fg=T["text_muted"], font=(FONT_UI, 10)).pack(anchor="w")
        tk.Label(text_frame, text=n.title,
                 bg=T.get("vibrancy", T["panel_bg"]),
                 fg=T["text"], font=(FONT_UI, 12, "bold")).pack(anchor="w")
        if n.body:
            tk.Label(text_frame, text=n.body,
                     bg=T.get("vibrancy", T["panel_bg"]),
                     fg=T["text_muted"], font=(FONT_UI, 11),
                     wraplength=200, justify="left").pack(anchor="w")

        bx = SCREEN_W - 300
        by = self._banner_y
        banner.place(x=bx, y=by, width=290)
        banner.lift()
        self._banner_y += 90

        def dismiss() -> None:
            banner.place_forget()
            banner.destroy()
            self._banner_y = max(MENUBAR_H + 8, self._banner_y - 90)
        banner.bind("<Button-1>", lambda _: dismiss())
        self.root.after(int(n.duration * 1000), dismiss)

    # ── process ticker ────────────────────────────────────────────────────────

    def _tick_procs(self) -> None:
        self.procs.update_all()
        self.root.after(2000, self._tick_procs)

    # ── window registration ───────────────────────────────────────────────────

    def register_win(self, win: BaseWin) -> None:
        self._wins.append(win)
        self.taskbar.refresh()

    def unregister_win(self, win: BaseWin) -> None:
        if win in self._wins:
            self._wins.remove(win)
        self.taskbar.refresh()

    def all_wins(self) -> List[BaseWin]:
        return list(self._wins)

    # ── Spotlight ─────────────────────────────────────────────────────────────

    def toggle_spotlight(self) -> None:
        if self._spotlight_open:
            self._close_spotlight()
        else:
            self._open_spotlight()

    def _open_spotlight(self) -> None:
        self._spotlight_open = True
        overlay = tk.Frame(self.root, bg="#000000")
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()

        search_frame = tk.Frame(
            overlay,
            bg=T.get("vibrancy", T["panel_bg"]),
            bd=0,
            highlightthickness=1,
            highlightbackground=T["separator"],
        )
        search_frame.place(
            x=self.root.winfo_width() // 2 - 280,
            y=self.root.winfo_height() // 4,
            width=560,
        )

        hdr = tk.Frame(search_frame, bg=T.get("vibrancy", T["panel_bg"]))
        hdr.pack(fill="x", padx=12, pady=(12, 4))
        tk.Label(hdr, text="🔍", bg=T.get("vibrancy", T["panel_bg"]),
                 font=(FONT_EMOJI, 20)).pack(side="left")
        entry = tk.Entry(
            hdr,
            bg=T.get("vibrancy", T["panel_bg"]),
            fg=T["text"],
            font=(FONT_UI, 22),
            insertbackground=T["text"],
            relief="flat",
            highlightthickness=0,
        )
        entry.pack(side="left", fill="x", expand=True, padx=8)
        entry.focus_set()

        results_frame = tk.Frame(search_frame, bg=T.get("vibrancy", T["panel_bg"]))
        results_frame.pack(fill="x", padx=12, pady=(0, 12))

        def search(event: Optional[tk.Event] = None) -> None:
            query = entry.get().strip()
            for w in results_frame.winfo_children():
                w.destroy()
            if not query:
                return
            # Search VFS
            hits = self.vfs.find("/", query)
            # Search app names
            app_hits = [a for a in DOCK_APPS if query.lower() in a[1].lower()]
            all_hits: List[Tuple[str, str, Callable]] = []
            for emoji, name, cmd in app_hits:
                all_hits.append((emoji, f"App: {name}", cmd))
            for path in hits[:8]:
                all_hits.append(("📄", path, lambda p=path: self._spotlight_open_file(p)))
            for emoji, label, cmd in all_hits[:10]:
                row = tk.Frame(results_frame, bg=T.get("vibrancy", T["panel_bg"]), cursor="hand2")
                row.pack(fill="x", pady=1)
                tk.Label(row, text=emoji,
                         bg=T.get("vibrancy", T["panel_bg"]),
                         font=(FONT_EMOJI, 16), width=3).pack(side="left")
                tk.Label(row, text=label,
                         bg=T.get("vibrancy", T["panel_bg"]),
                         fg=T["text"], font=(FONT_UI, 14),
                         anchor="w").pack(side="left", fill="x", expand=True)
                row.bind("<Button-1>", lambda _, c=cmd: (self._close_spotlight(), c()))
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda _, c=cmd: (self._close_spotlight(), c()))

        entry.bind("<KeyRelease>", search)
        entry.bind("<Escape>", lambda _: self._close_spotlight())
        overlay.bind("<Escape>", lambda _: self._close_spotlight())
        overlay.bind("<Button-1>", lambda e: (self._close_spotlight()
                                               if e.widget == overlay else None))
        self._spotlight_frame = overlay

    def _close_spotlight(self) -> None:
        self._spotlight_open = False
        if self._spotlight_frame:
            self._spotlight_frame.destroy()
            self._spotlight_frame = None

    def _spotlight_open_file(self, path: str) -> None:
        if self.vfs.isfile(path):
            self.open_textedit(path=path)

    # ── app launchers ─────────────────────────────────────────────────────────

    def open_finder(self, path: Optional[str] = None) -> None:
        FinderApp(self, start_path=path or self.vfs.HOME)

    def open_textedit(self, path: Optional[str] = None) -> None:
        TextEditApp(self, path=path)

    def open_terminal(self, cwd: Optional[str] = None) -> None:
        TerminalApp(self, cwd=cwd)

    def open_safari(self, url: str = "macpyos://home") -> None:
        SafariApp(self, url=url)

    def open_music(self) -> None:
        MusicApp(self)

    def open_preview(self, path: Optional[str] = None) -> None:
        PreviewApp(self, path=path)

    def open_calculator(self) -> None:
        CalculatorApp(self)

    def open_clock(self) -> None:
        ClockApp(self)

    def open_activity_monitor(self) -> None:
        ActivityMonitorApp(self)

    def open_notes(self) -> None:
        NotesApp(self)

    def open_mail(self) -> None:
        MailApp(self)

    def open_keychain(self) -> None:
        KeychainApp(self)

    def open_numbers(self, path: Optional[str] = None) -> None:
        NumbersApp(self, path=path)

    def open_photos(self) -> None:
        PhotosApp(self)

    def open_disk_utility(self) -> None:
        DiskUtilityApp(self)

    def open_script_editor(self) -> None:
        ScriptEditorApp(self)

    def open_app_store(self) -> None:
        AppStoreApp(self)

    def open_preferences(self, panel: Optional[str] = None) -> None:
        SystemPreferencesApp(self, panel=panel)

    def open_archive_utility(self) -> None:
        ArchiveUtilityApp(self)

    def open_contacts(self) -> None:
        ContactsApp(self)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 12 — DOCK APPS LIST  (used by Spotlight and Dock)
# ─────────────────────────────────────────────────────────────────────────────

# (populated after WM is defined — forward reference resolved at module level)
DOCK_APPS: List[Tuple[str, str, Any]] = []   # (emoji, name, launcher_fn)


def _build_dock_apps(wm: "WM") -> List[Tuple[str, str, Callable]]:
    return [
        ("🖥️",  "Finder",              wm.open_finder),
        ("🗒️",  "Notes",               wm.open_notes),
        ("🌐",  "Safari",              wm.open_safari),
        ("📧",  "Mail",                wm.open_mail),
        ("🎵",  "Music",               wm.open_music),
        ("🖼️",  "Preview",             wm.open_preview),
        ("🗂️",  "TextEdit",            wm.open_textedit),
        ("💻",  "Terminal",            wm.open_terminal),
        ("🧮",  "Calculator",          wm.open_calculator),
        ("⏰",  "Clock",               wm.open_clock),
        ("📊",  "Numbers",             wm.open_numbers),
        ("🔑",  "Keychain Access",     wm.open_keychain),
        ("📸",  "Photos",              wm.open_photos),
        ("💿",  "Disk Utility",        wm.open_disk_utility),
        ("📝",  "Script Editor",       wm.open_script_editor),
        ("📱",  "Activity Monitor",    wm.open_activity_monitor),
        ("🏪",  "App Store",           wm.open_app_store),
        ("⚙️",  "System Preferences",  wm.open_preferences),
        ("🗜️",  "Archive Utility",     wm.open_archive_utility),
        ("👥",  "Contacts",            wm.open_contacts),
    ]


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 13 — MENU BAR
# ─────────────────────────────────────────────────────────────────────────────

class MenuBar:
    """
    macOS-style top menu bar:
    [ Apple  |  App menus  ]           [ Status icons | Clock ]
    """

    def __init__(self, wm: "WM") -> None:
        self.wm = wm
        self.frame = tk.Frame(
            wm.root,
            bg=T["menubar_bg"],
            height=MENUBAR_H,
            bd=0,
            highlightthickness=1,
            highlightbackground=T["menubar_border"],
        )
        self.frame.place(x=0, y=0, relwidth=1, height=MENUBAR_H)
        self.frame.lift()
        self.frame.pack_propagate(False)

        # ── Apple logo (left) ─────────────────────────────────────────────────
        self._apple = tk.Label(
            self.frame, text="",
            bg=T["menubar_bg"], fg=T["menubar_fg"],
            font=(FONT_EMOJI, 16),
            padx=10, cursor="hand2",
        )
        self._apple.pack(side="left")
        self._apple.bind("<Button-1>", lambda _: self._apple_menu())

        # ── App-level menus ───────────────────────────────────────────────────
        self._add_menu("Finder",  self._finder_menu)
        self._add_menu("File",    self._file_menu)
        self._add_menu("Edit",    self._edit_menu)
        self._add_menu("View",    self._view_menu)
        self._add_menu("Go",      self._go_menu)
        self._add_menu("Window",  self._window_menu)
        self._add_menu("Help",    self._help_menu)

        # ── right side ────────────────────────────────────────────────────────
        right_frame = tk.Frame(self.frame, bg=T["menubar_bg"])
        right_frame.pack(side="right")

        # Clock
        self._clock_lbl = tk.Label(
            right_frame, text="",
            bg=T["menubar_bg"], fg=T["menubar_fg"],
            font=(FONT_UI, 12), padx=10,
        )
        self._clock_lbl.pack(side="right")
        self._update_clock()

        # Notification Center
        notif_btn = tk.Label(
            right_frame, text="🔔",
            bg=T["menubar_bg"], fg=T["menubar_fg"],
            font=(FONT_EMOJI, 13), padx=6, cursor="hand2",
        )
        notif_btn.pack(side="right")
        notif_btn.bind("<Button-1>", lambda _: self._toggle_notif_center())

        # Spotlight
        spot_btn = tk.Label(
            right_frame, text="🔍",
            bg=T["menubar_bg"], fg=T["menubar_fg"],
            font=(FONT_EMOJI, 13), padx=6, cursor="hand2",
        )
        spot_btn.pack(side="right")
        spot_btn.bind("<Button-1>", lambda _: wm.toggle_spotlight())

        # WiFi indicator
        tk.Label(right_frame, text="WiFi",
                 bg=T["menubar_bg"], fg=T["menubar_fg"],
                 font=(FONT_UI, 11), padx=4).pack(side="right")

        # Battery indicator
        self._battery_lbl = tk.Label(
            right_frame, text="🔋 98%",
            bg=T["menubar_bg"], fg=T["menubar_fg"],
            font=(FONT_UI, 11), padx=4,
        )
        self._battery_lbl.pack(side="right")
        self._update_battery()

    def _add_menu(self, label: str, builder: Callable) -> None:
        btn = tk.Label(
            self.frame, text=label,
            bg=T["menubar_bg"], fg=T["menubar_fg"],
            font=(FONT_UI, 13), padx=8,
            cursor="hand2",
        )
        btn.pack(side="left")
        btn.bind("<Enter>", lambda _, b=btn: b.configure(bg=T["menu_hover"], fg=T["menu_fg_hover"]))
        btn.bind("<Leave>", lambda _, b=btn: b.configure(bg=T["menubar_bg"], fg=T["menubar_fg"]))
        btn.bind("<Button-1>", lambda e, build=builder, b=btn: self._show_menu(e, build, b))

    def _show_menu(self, e: tk.Event, builder: Callable, btn: tk.Label) -> None:
        menu = tk.Menu(
            self.wm.root, tearoff=False,
            bg=T["menu_bg"], fg=T["menu_fg"],
            activebackground=T["menu_hover"],
            activeforeground=T["menu_fg_hover"],
            font=(FONT_UI, 13), bd=0, relief="flat",
        )
        builder(menu)
        try:
            menu.tk_popup(btn.winfo_rootx(), btn.winfo_rooty() + MENUBAR_H)
        finally:
            menu.grab_release()

    # ── Apple menu ────────────────────────────────────────────────────────────

    def _apple_menu(self) -> None:
        menu = tk.Menu(
            self.wm.root, tearoff=False,
            bg=T["menu_bg"], fg=T["menu_fg"],
            activebackground=T["menu_hover"],
            activeforeground=T["menu_fg_hover"],
            font=(FONT_UI, 13), bd=0, relief="flat",
        )
        menu.add_command(label="About MacPyOS",      command=self._about)
        menu.add_separator()
        menu.add_command(label="System Preferences…", command=self.wm.open_preferences)
        menu.add_command(label="App Store…",          command=self.wm.open_app_store)
        menu.add_separator()
        menu.add_command(label="Recent Items ▶",      command=lambda: None)
        menu.add_separator()
        menu.add_command(label="Force Quit…",         command=self._force_quit)
        menu.add_separator()
        menu.add_command(label="Sleep",               command=lambda: None)
        menu.add_command(label="Restart…",            command=self._restart)
        menu.add_command(label="Shut Down…",          command=self._shutdown)
        menu.add_separator()
        menu.add_command(label="Lock Screen",         command=lambda: show_lock(self.wm.root, self.wm))
        menu.add_command(label=f"Log Out {self.wm.users.display_name()}…",
                         command=lambda: show_login(self.wm.root, self.wm))
        try:
            menu.tk_popup(0, MENUBAR_H)
        finally:
            menu.grab_release()

    def _about(self) -> None:
        messagebox.showinfo(
            "About MacPyOS",
            f"MacPyOS {MACPYOS_VERSION} ({MACPYOS_CODENAME})\n\n"
            "A macOS-style desktop simulation\n"
            "built with pure Python + Tkinter.\n\n"
            "No external dependencies.\n"
            f"Build {BUILD_DATE}",
            parent=self.wm.root,
        )

    def _force_quit(self) -> None:
        wins = self.wm.all_wins()
        if not wins:
            messagebox.showinfo("Force Quit Applications",
                                "No applications are open.", parent=self.wm.root)
            return
        ForceQuitDialog(self.wm)

    def _restart(self) -> None:
        if messagebox.askyesno("Restart", "Are you sure you want to restart MacPyOS?",
                               parent=self.wm.root):
            self.wm.root.destroy()

    def _shutdown(self) -> None:
        if messagebox.askyesno("Shut Down", "Are you sure you want to shut down MacPyOS?",
                               parent=self.wm.root):
            self.wm.root.destroy()

    # ── app menus (stub implementations) ──────────────────────────────────────

    def _finder_menu(self, menu: tk.Menu) -> None:
        menu.add_command(label="About Finder",  command=self._about)
        menu.add_separator()
        menu.add_command(label="Preferences…",  command=self.wm.open_preferences)
        menu.add_separator()
        menu.add_command(label="Empty Trash…",  command=lambda:
                         self.wm.notifs.send("Finder", "Trash emptied.", icon="🗑️"))
        menu.add_separator()
        menu.add_command(label="Hide Finder",   command=lambda: None)
        menu.add_command(label="Hide Others",   command=lambda: None)
        menu.add_command(label="Show All",      command=lambda: None)

    def _file_menu(self, menu: tk.Menu) -> None:
        menu.add_command(label="New Finder Window",    command=self.wm.open_finder,   accelerator="⌘N")
        menu.add_command(label="New Folder",           command=lambda: None,          accelerator="⌘⇧N")
        menu.add_command(label="New TextEdit Document",command=self.wm.open_textedit, accelerator="⌘T")
        menu.add_separator()
        menu.add_command(label="Open…",                command=self.wm.open_finder,   accelerator="⌘O")
        menu.add_command(label="Close Window",         command=lambda: None,          accelerator="⌘W")
        menu.add_separator()
        menu.add_command(label="Get Info",             command=lambda: None,          accelerator="⌘I")
        menu.add_separator()
        menu.add_command(label="Move to Trash",        command=lambda: None,          accelerator="⌘⌫")

    def _edit_menu(self, menu: tk.Menu) -> None:
        menu.add_command(label="Undo",       command=lambda: None, accelerator="⌘Z")
        menu.add_command(label="Redo",       command=lambda: None, accelerator="⌘⇧Z")
        menu.add_separator()
        menu.add_command(label="Cut",        command=lambda: None, accelerator="⌘X")
        menu.add_command(label="Copy",       command=lambda: None, accelerator="⌘C")
        menu.add_command(label="Paste",      command=lambda: None, accelerator="⌘V")
        menu.add_command(label="Select All", command=lambda: None, accelerator="⌘A")
        menu.add_separator()
        menu.add_command(label="Find…",      command=lambda: None, accelerator="⌘F")

    def _view_menu(self, menu: tk.Menu) -> None:
        menu.add_command(label="as Icons",   command=lambda: None, accelerator="⌘1")
        menu.add_command(label="as List",    command=lambda: None, accelerator="⌘2")
        menu.add_command(label="as Columns", command=lambda: None, accelerator="⌘3")
        menu.add_command(label="as Gallery", command=lambda: None, accelerator="⌘4")
        menu.add_separator()
        menu.add_command(label="Show Sidebar",     command=lambda: None)
        menu.add_command(label="Show Path Bar",    command=lambda: None)
        menu.add_command(label="Show Status Bar",  command=lambda: None)
        menu.add_separator()
        menu.add_command(label="Enter Full Screen", command=lambda: None, accelerator="⌃⌘F")

    def _go_menu(self, menu: tk.Menu) -> None:
        wm = self.wm
        menu.add_command(label="Back",         command=lambda: None, accelerator="⌘[")
        menu.add_command(label="Forward",      command=lambda: None, accelerator="⌘]")
        menu.add_separator()
        menu.add_command(label="Home",         command=lambda: wm.open_finder(wm.vfs.HOME))
        menu.add_command(label="Desktop",      command=lambda: wm.open_finder("/Users/user/Desktop"))
        menu.add_command(label="Documents",    command=lambda: wm.open_finder("/Users/user/Documents"))
        menu.add_command(label="Downloads",    command=lambda: wm.open_finder("/Users/user/Downloads"))
        menu.add_command(label="Applications", command=lambda: wm.open_finder("/Applications"))
        menu.add_command(label="Utilities",    command=lambda: wm.open_terminal())
        menu.add_separator()
        menu.add_command(label="Go to Folder…", command=self._go_to_folder, accelerator="⌘⇧G")

    def _go_to_folder(self) -> None:
        path = simpledialog.askstring("Go to Folder", "Enter path:", parent=self.wm.root)
        if path:
            self.wm.open_finder(path=path)

    def _window_menu(self, menu: tk.Menu) -> None:
        menu.add_command(label="Minimise",   command=lambda: None, accelerator="⌘M")
        menu.add_command(label="Zoom",       command=lambda: None)
        menu.add_separator()
        for win in self.wm.all_wins():
            menu.add_command(
                label=f"{win.icon} {win.title_str}",
                command=win.raise_win,
            )

    def _help_menu(self, menu: tk.Menu) -> None:
        menu.add_command(label="MacPyOS Help", command=lambda: self.wm.open_safari("macpyos://help"))
        menu.add_separator()
        menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)

    def _show_shortcuts(self) -> None:
        messagebox.showinfo(
            "Keyboard Shortcuts",
            "⌘Space  Spotlight\n"
            "⌘T       New Terminal\n"
            "⌘N       New Finder Window\n"
            "⌘E       Open TextEdit\n"
            "⌘L       Lock Screen\n"
            "⌘Q       Quit\n"
            "⌃⌘F     Full Screen\n"
            "F5        Refresh Desktop",
            parent=self.wm.root,
        )

    # ── clock & battery ───────────────────────────────────────────────────────

    def _update_clock(self) -> None:
        if self.wm.settings.get("menu_bar_clock", True):
            now = datetime.datetime.now()
            fmt_12 = self.wm.settings.get("time_format", "12h") == "12h"
            if fmt_12:
                t = _strftime("%a %b %-d  %-I:%M %p", now)
            else:
                t = _strftime("%a %b %-d  %H:%M", now)
            self._clock_lbl.configure(text=t)
        self.wm.root.after(15000, self._update_clock)

    def _update_battery(self) -> None:
        # Simulate slowly draining battery
        cur = self._battery_lbl.cget("text")
        try:
            pct = int(cur.split("% ")[0].replace("🔋 ", "").replace("🔌 ", ""))
        except Exception:
            pct = 98
        pct = max(1, pct - random.randint(0, 1))
        icon = "🔌" if pct > 95 else "🔋"
        self._battery_lbl.configure(text=f"{icon} {pct}%")
        self.wm.root.after(60000, self._update_battery)

    def _toggle_notif_center(self) -> None:
        self.wm.notifs.send(
            "Notification Center",
            f"{self.wm.notifs.unread_count()} unread notifications.",
            icon="🔔",
        )
        self.wm.notifs.mark_all_read()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 14 — DOCK
# ─────────────────────────────────────────────────────────────────────────────

class Dock:
    """macOS-style Dock — Windows compatible, coloured tile icons."""

    # App definitions: (background_color, short_label, full_name, launcher_attr)
    APP_DEFS = [
        ("#007aff", "F",   "Finder",            "open_finder"),
        ("#1a1a2e", "N",   "Notes",             "open_notes"),
        ("#0a84ff", "Safari","Safari",           "open_safari"),
        ("#c0392b", "Mail", "Mail",             "open_mail"),
        ("#1db954", "Music","Music",            "open_music"),
        ("#e74c3c", "Prev", "Preview",          "open_preview"),
        ("#ff9500", "Edit", "TextEdit",         "open_textedit"),
        ("#1c1c1e", ">_",  "Terminal",          "open_terminal"),
        ("#636366", "Calc", "Calculator",       "open_calculator"),
        ("#2c2c2e", "Clock","Clock",            "open_clock"),
        ("#34c759", "Nums", "Numbers",          "open_numbers"),
        ("#5856d6", "Key",  "Keychain",         "open_keychain"),
        ("#ff2d55", "Foto", "Photos",           "open_photos"),
        ("#8e8e93", "Disk", "Disk Utility",     "open_disk_utility"),
        ("#ff6b00", "Scr",  "Script Editor",    "open_script_editor"),
        ("#30b0c7", "Act",  "Activity Monitor", "open_activity_monitor"),
        ("#007aff", "Store","App Store",        "open_app_store"),
        ("#636366", "Pref", "Preferences",      "open_preferences"),
        ("#48484a", "Zip",  "Archive Utility",  "open_archive_utility"),
        ("#5e5ce6", "Cont", "Contacts",         "open_contacts"),
    ]

    def __init__(self, wm: "WM") -> None:
        self.wm         = wm
        self._minimised: List["BaseWin"] = []
        self._apps      = self.APP_DEFS
        global DOCK_APPS
        DOCK_APPS = [(c, n, getattr(wm, a, lambda: None))
                     for c, s, n, a in self.APP_DEFS]

        self.frame = tk.Frame(wm.root, bg="#1c1c1e",
                              highlightthickness=1,
                              highlightbackground="#3a3a3c")
        # Place after window is ready
        wm.root.after(100, self._place_and_build)

    def _place_and_build(self) -> None:
        w = self.wm.root.winfo_width()
        h = self.wm.root.winfo_height()
        if w < 100:   # not ready yet
            self.wm.root.after(100, self._place_and_build)
            return
        self.frame.place(x=0, y=h - DOCK_H, width=w, height=DOCK_H)
        self.frame.lift()
        self._build_dock()
        # Re-place on window resize
        self.wm.root.bind("<Configure>", self._on_resize, add="+")

    def _on_resize(self, _: tk.Event) -> None:
        w = self.wm.root.winfo_width()
        h = self.wm.root.winfo_height()
        if w > 100:
            self.frame.place(x=0, y=h - DOCK_H, width=w, height=DOCK_H)

    def _build_dock(self) -> None:
        for widget in self.frame.winfo_children():
            widget.destroy()

        canvas = tk.Canvas(self.frame, bg="#1c1c1e",
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        icon_size = 48
        gap       = 6
        apps      = self._apps
        total_w   = len(apps) * (icon_size + gap) + gap
        root_w    = self.wm.root.winfo_width()
        start_x   = max(gap, (root_w - total_w) // 2)
        y_center  = DOCK_H // 2

        for i, (color, label, name, attr) in enumerate(apps):
            x = start_x + i * (icon_size + gap)
            x1, y1 = x, y_center - icon_size // 2
            x2, y2 = x + icon_size, y_center + icon_size // 2
            r = 10
            tag = f"dock_{i}"

            # Draw rounded rect
            canvas.create_rectangle(x1+r,y1, x2-r,y2,
                fill=color, outline="", tags=tag)
            canvas.create_rectangle(x1,y1+r, x2,y2-r,
                fill=color, outline="", tags=tag)
            canvas.create_oval(x1,y1, x1+2*r,y1+2*r,
                fill=color, outline="", tags=tag)
            canvas.create_oval(x2-2*r,y1, x2,y1+2*r,
                fill=color, outline="", tags=tag)
            canvas.create_oval(x1,y2-2*r, x1+2*r,y2,
                fill=color, outline="", tags=tag)
            canvas.create_oval(x2-2*r,y2-2*r, x2,y2,
                fill=color, outline="", tags=tag)

            # Short label text
            canvas.create_text((x1+x2)//2, (y1+y2)//2,
                text=label, fill="#ffffff",
                font=(FONT_UI, 9, "bold"), tags=tag)

            # Bind click
            cmd = getattr(self.wm, attr, None)
            if cmd:
                canvas.tag_bind(tag, "<Button-1>",
                                lambda _, c=cmd: c())
                canvas.tag_bind(tag, "<Enter>",
                                lambda _, tg=tag, cv=canvas, c=color:
                                cv.itemconfigure(tg, fill=self._lighten(c)))
                canvas.tag_bind(tag, "<Leave>",
                                lambda _, tg=tag, cv=canvas, c=color:
                                cv.itemconfigure(tg, fill=c))

            # Tooltip
            make_tooltip(canvas, name, delay=400)

        # Minimised window section
        if self._minimised:
            sep_x = start_x + len(apps)*(icon_size+gap) + gap
            canvas.create_line(sep_x, 8, sep_x, DOCK_H-8,
                fill="#3a3a3c", width=1)
            for j, win in enumerate(self._minimised):
                x = sep_x + gap + j*(icon_size//2 + gap)
                canvas.create_rectangle(x, y_center-20, x+40, y_center+20,
                    fill="#2c2c2e", outline="#3a3a3c")
                canvas.create_text(x+20, y_center,
                    text=win.title_str[:5], fill="#ffffff",
                    font=(FONT_UI, 8))
                canvas.tag_bind(f"min_{j}", "<Button-1>",
                                lambda _, w=win: w.restore())

    @staticmethod
    def _lighten(hex_color: str) -> str:
        try:
            r = min(255, int(hex_color[1:3], 16) + 40)
            g = min(255, int(hex_color[3:5], 16) + 40)
            b = min(255, int(hex_color[5:7], 16) + 40)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def add_minimised(self, win: "BaseWin") -> None:
        if win not in self._minimised:
            self._minimised.append(win)
        self._build_dock()

    def remove_minimised(self, win: "BaseWin") -> None:
        if win in self._minimised:
            self._minimised.remove(win)
        self._build_dock()

    def refresh(self) -> None:
        self._build_dock()


class ForceQuitDialog:
    """macOS-style Force Quit Applications dialog."""

    def __init__(self, wm: "WM") -> None:
        self.wm = wm
        dlg = tk.Toplevel(wm.root)
        dlg.title("Force Quit Applications")
        dlg.geometry("400x320")
        dlg.configure(bg=T["panel_bg"])
        dlg.resizable(False, False)
        dlg.transient(wm.root)
        dlg.grab_set()

        tk.Label(dlg, text="Force Quit Applications",
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 15, "bold")).pack(pady=(16, 4))
        tk.Label(dlg, text="Select an application to force quit:",
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 12)).pack()

        listbox = tk.Listbox(
            dlg, bg=T["win_bg"], fg=T["text"],
            selectbackground=T["selection"],
            font=(FONT_UI, 13), relief="flat",
            highlightthickness=1,
            highlightbackground=T["input_border"],
            bd=0,
        )
        listbox.pack(fill="both", expand=True, padx=16, pady=10)

        for win in wm.all_wins():
            listbox.insert("end", f"{win.icon}  {win.title_str}")

        btn_frame = tk.Frame(dlg, bg=T["panel_bg"])
        btn_frame.pack(pady=(0, 16))

        def force_quit() -> None:
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            wins = wm.all_wins()
            if idx < len(wins):
                wins[idx].close()
                listbox.delete(idx)

        tk.Button(btn_frame, text="Force Quit",
                  bg=T["danger"], fg="#ffffff",
                  font=(FONT_UI, 13), relief="flat",
                  padx=16, pady=6, cursor="hand2",
                  command=force_quit).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancel",
                  bg=T["button_secondary"], fg=T["text"],
                  font=(FONT_UI, 13), relief="flat",
                  padx=16, pady=6, cursor="hand2",
                  command=dlg.destroy).pack(side="left", padx=6)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 16 — FINDER APP
# ─────────────────────────────────────────────────────────────────────────────

class FinderApp(BaseWin):
    """
    macOS Finder clone.
    Layout: Sidebar (favourites) | Path bar | Content (icon/list/column view)
    """

    FAVOURITES = [
        ("🏠", "Home",        "/Users/user"),
        ("🖥️", "Desktop",     "/Users/user/Desktop"),
        ("📄", "Documents",   "/Users/user/Documents"),
        ("⬇️", "Downloads",   "/Users/user/Downloads"),
        ("🎵", "Music",       "/Users/user/Music"),
        ("🖼️", "Pictures",    "/Users/user/Pictures"),
        ("🎬", "Movies",      "/Users/user/Movies"),
        ("💻", "Developer",   "/Users/user/Developer"),
        ("📱", "Applications","/Applications"),
        ("🗂️", "Recents",     "/Users/user/Documents"),
    ]

    FILE_ICONS: Dict[str, str] = {
        ".py":   "🐍", ".txt":  "📄", ".md":   "📝",
        ".csv":  "📊", ".json": "📋", ".sh":   "⚙️",
        ".mp3":  "🎵", ".mp4":  "🎬", ".jpg":  "🖼️",
        ".png":  "🖼️", ".pdf":  "📕", ".zip":  "🗜️",
        ".html": "🌐", ".css":  "🎨", ".js":   "📜",
        ".plist":"🔧", ".m3u":  "🎶",
    }

    def __init__(self, wm: "WM", start_path: Optional[str] = None) -> None:
        super().__init__(wm, title="Finder", w=860, h=540, icon="🖥️")
        self._path      = start_path or wm.vfs.HOME
        self._history:  List[str] = [self._path]
        self._hist_idx: int       = 0
        self._view_mode: str      = "icon"   # "icon" | "list" | "column"
        self._selected: Optional[str] = None
        self._sort_key: str       = "name"
        self._sort_rev: bool      = False
        self._search_var = tk.StringVar()

        self._build_ui()
        self._load(self._path)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        c = self.client

        # ── toolbar ───────────────────────────────────────────────────────────
        toolbar = tk.Frame(c, bg=T["panel_bg"],
                           highlightthickness=1,
                           highlightbackground=T["separator"])
        toolbar.pack(fill="x")

        def tb_btn(text: str, cmd: Callable, tip: str = "") -> tk.Label:
            b = tk.Label(toolbar, text=text, bg=T["panel_bg"],
                         fg=T["text"], font=(FONT_EMOJI, 14),
                         padx=8, pady=4, cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>", lambda _: cmd())
            b.bind("<Enter>", lambda _, lb=b: lb.configure(bg=T["panel_alt"]))
            b.bind("<Leave>", lambda _, lb=b: lb.configure(bg=T["panel_bg"]))
            if tip:
                make_tooltip(b, tip)
            return b

        tb_btn("◀",  self._go_back,    "Back")
        tb_btn("▶",  self._go_forward, "Forward")
        tb_btn("⬆",  self._go_up,      "Enclosing Folder")
        tk.Frame(toolbar, bg=T["separator"], width=1,
                 height=20).pack(side="left", padx=4, pady=4)

        # View buttons
        for sym, mode, tip in [("⊞","icon","Icon View"),
                                ("≡","list","List View"),
                                ("|||","column","Column View")]:
            b = tk.Label(toolbar, text=sym, bg=T["panel_bg"],
                         fg=T["text"], font=(FONT_UI, 13),
                         padx=6, pady=4, cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>", lambda _, m=mode: self._set_view(m))
            make_tooltip(b, tip)

        tk.Frame(toolbar, bg=T["separator"], width=1,
                 height=20).pack(side="left", padx=4)
        tb_btn("🔍", lambda: self._search_entry.focus_set(), "Search")

        # Search box
        self._search_entry = tk.Entry(
            toolbar, textvariable=self._search_var,
            bg=T["input_bg"], fg=T["text"],
            insertbackground=T["text"],
            relief="flat", font=(FONT_UI, 12),
            highlightthickness=1,
            highlightbackground=T["input_border"],
            highlightcolor=T["input_focus"],
            width=18,
        )
        self._search_entry.pack(side="right", padx=8, pady=4)
        self._search_var.trace_add("write", lambda *_: self._do_search())

        # Action buttons
        tb_btn("🗂️", self._new_folder,   "New Folder")
        tb_btn("🗑️", self._delete_sel,   "Move to Trash")
        tb_btn("ℹ️",  self._get_info,     "Get Info")

        # ── path bar ──────────────────────────────────────────────────────────
        self._pathbar = tk.Frame(c, bg=T["panel_alt"],
                                 highlightthickness=1,
                                 highlightbackground=T["separator"])
        self._pathbar.pack(fill="x")

        # ── main pane (sidebar + content) ─────────────────────────────────────
        pane = tk.Frame(c, bg=T["win_bg"])
        pane.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(pane, bg=T["sidebar_bg"], width=160)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="FAVOURITES",
                 bg=T["sidebar_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 10, "bold"),
                 padx=12, pady=6).pack(anchor="w")

        for emoji, label, path in self.FAVOURITES:
            row = tk.Frame(sidebar, bg=T["sidebar_bg"], cursor="hand2")
            row.pack(fill="x")
            tk.Label(row, text=emoji,
                     bg=T["sidebar_bg"], font=(FONT_EMOJI, 13),
                     padx=8).pack(side="left")
            lbl = tk.Label(row, text=label,
                           bg=T["sidebar_bg"], fg=T["text"],
                           font=(FONT_UI, 12), anchor="w")
            lbl.pack(side="left", fill="x", expand=True, pady=3)
            for w in (row, lbl):
                w.bind("<Button-1>",   lambda _, p=path: self._navigate(p))
                w.bind("<Enter>",      lambda _, r=row: r.configure(bg=T["menu_hover"]))
                w.bind("<Leave>",      lambda _, r=row: r.configure(bg=T["sidebar_bg"]))

        tk.Frame(sidebar, bg=T["separator"], height=1).pack(fill="x", pady=4)
        tk.Label(sidebar, text="LOCATIONS",
                 bg=T["sidebar_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 10, "bold"),
                 padx=12, pady=4).pack(anchor="w")
        for emoji, label, path in [("💻","MacPyOS","/"),
                                    ("🗑️","Trash","/Users/user/.Trash")]:
            row = tk.Frame(sidebar, bg=T["sidebar_bg"], cursor="hand2")
            row.pack(fill="x")
            tk.Label(row, text=emoji, bg=T["sidebar_bg"],
                     font=(FONT_EMOJI, 13), padx=8).pack(side="left")
            lbl = tk.Label(row, text=label, bg=T["sidebar_bg"],
                           fg=T["text"], font=(FONT_UI, 12), anchor="w")
            lbl.pack(side="left", fill="x", expand=True, pady=3)
            for w in (row, lbl):
                w.bind("<Button-1>",   lambda _, p=path: self._navigate(p))
                w.bind("<Enter>",      lambda _, r=row: r.configure(bg=T["menu_hover"]))
                w.bind("<Leave>",      lambda _, r=row: r.configure(bg=T["sidebar_bg"]))

        # Vertical separator
        tk.Frame(pane, bg=T["separator"], width=1).pack(side="left", fill="y")

        # Content area
        self._content = tk.Frame(pane, bg=T["win_bg"])
        self._content.pack(side="left", fill="both", expand=True)

        # Status bar
        self._status = tk.Label(c, text="",
                                bg=T["status_bg"], fg=T["text_muted"],
                                font=(FONT_UI, 11),
                                highlightthickness=1,
                                highlightbackground=T["status_border"],
                                anchor="w", padx=10)
        self._status.pack(fill="x")

    # ── navigation ────────────────────────────────────────────────────────────

    def _navigate(self, path: str) -> None:
        if not self.wm.vfs.exists(path):
            self.wm.notifs.send("Finder", f"'{path}' not found.", icon="⚠️")
            return
        # Trim forward history on new navigation
        self._history = self._history[:self._hist_idx + 1]
        self._history.append(path)
        self._hist_idx = len(self._history) - 1
        self._load(path)

    def _go_back(self) -> None:
        if self._hist_idx > 0:
            self._hist_idx -= 1
            self._load(self._history[self._hist_idx])

    def _go_forward(self) -> None:
        if self._hist_idx < len(self._history) - 1:
            self._hist_idx += 1
            self._load(self._history[self._hist_idx])

    def _go_up(self) -> None:
        parent = "/".join(self._path.rstrip("/").split("/")[:-1]) or "/"
        self._navigate(parent)

    def _set_view(self, mode: str) -> None:
        self._view_mode = mode
        self._load(self._path)

    # ── path bar refresh ──────────────────────────────────────────────────────

    def _refresh_pathbar(self) -> None:
        for w in self._pathbar.winfo_children():
            w.destroy()
        parts = [p for p in self._path.split("/") if p]
        cumulative = "/"
        tk.Label(self._pathbar, text="💻",
                 bg=T["panel_alt"], fg=T["text_muted"],
                 font=(FONT_EMOJI, 11), padx=4).pack(side="left")
        for i, part in enumerate(parts):
            cumulative = cumulative.rstrip("/") + "/" + part
            if i > 0:
                tk.Label(self._pathbar, text=" › ",
                         bg=T["panel_alt"], fg=T["text_muted"],
                         font=(FONT_UI, 11)).pack(side="left")
            p = cumulative
            lbl = tk.Label(self._pathbar, text=part,
                           bg=T["panel_alt"], fg=T["accent"],
                           font=(FONT_UI, 11), cursor="hand2", padx=2)
            lbl.pack(side="left")
            lbl.bind("<Button-1>", lambda _, path=p: self._navigate(path))

    # ── directory loader ──────────────────────────────────────────────────────

    def _load(self, path: str) -> None:
        self._path = path
        self.set_title(f"Finder — {path.split('/')[-1] or '/'}")
        self._refresh_pathbar()
        self._selected = None

        for w in self._content.winfo_children():
            w.destroy()

        if not self.wm.vfs.exists(path):
            tk.Label(self._content, text="Folder not found.",
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 14)).pack(pady=40)
            return

        if self.wm.vfs.isfile(path):
            self._open_item(path)
            self._navigate("/".join(path.split("/")[:-1]) or "/")
            return

        try:
            entries = self.wm.vfs.listdir(path)
        except Exception as ex:
            tk.Label(self._content, text=str(ex),
                     bg=T["win_bg"], fg=T["danger"],
                     font=(FONT_UI, 13)).pack(pady=20)
            return

        # Build full paths and sort
        items: List[Tuple[str, bool]] = []
        for name in entries:
            full = path.rstrip("/") + "/" + name
            is_dir = self.wm.vfs.isdir(full)
            items.append((full, is_dir))

        # Dirs first, then files
        items.sort(key=lambda x: (not x[1], x[0].split("/")[-1].lower()))
        if self._sort_rev:
            items.sort(key=lambda x: x[0].split("/")[-1].lower(), reverse=True)

        if self._view_mode == "list":
            self._render_list(items)
        elif self._view_mode == "column":
            self._render_column(items)
        else:
            self._render_icon(items)

        # Status bar
        ndirs  = sum(1 for _, d in items if d)
        nfiles = len(items) - ndirs
        self._status.configure(
            text=f"  {len(items)} items  ({ndirs} folders, {nfiles} files)"
        )

    def _get_icon(self, path: str, is_dir: bool) -> str:
        if is_dir:
            return "📁"
        ext = os.path.splitext(path)[1].lower()
        return self.FILE_ICONS.get(ext, "📄")

    # ── icon view ─────────────────────────────────────────────────────────────

    def _render_icon(self, items: List[Tuple[str, bool]]) -> None:
        sf = MacScrolledFrame(self._content, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner

        CELL_W = 90
        CELL_H = 90
        cols   = max(1, (self._content.winfo_width() or 600) // CELL_W)

        for idx, (full, is_dir) in enumerate(items):
            name = full.split("/")[-1]
            icon = self._get_icon(full, is_dir)
            col  = idx % cols
            row  = idx // cols

            cell = tk.Frame(inner, bg=T["win_bg"],
                            width=CELL_W, height=CELL_H, cursor="hand2")
            cell.grid(row=row, column=col, padx=4, pady=4)
            cell.grid_propagate(False)

            emo = tk.Label(cell, text=icon,
                           bg=T["win_bg"],
                           font=(FONT_EMOJI, 30))
            emo.place(relx=0.5, y=24, anchor="center")

            short = name if len(name) <= 14 else name[:12] + "…"
            lbl = tk.Label(cell, text=short,
                           bg=T["win_bg"], fg=T["text"],
                           font=(FONT_UI, 10), wraplength=CELL_W - 8,
                           justify="center")
            lbl.place(relx=0.5, y=58, anchor="n")

            def on_enter(_, c=cell, e=emo, l=lbl) -> None:
                c.configure(bg=T["selection"])
                e.configure(bg=T["selection"])
                l.configure(bg=T["selection"])

            def on_leave(_, c=cell, e=emo, l=lbl) -> None:
                c.configure(bg=T["win_bg"])
                e.configure(bg=T["win_bg"])
                l.configure(bg=T["win_bg"])

            for w in (cell, emo, lbl):
                w.bind("<Enter>",           on_enter)
                w.bind("<Leave>",           on_leave)
                w.bind("<Double-Button-1>", lambda _, p=full, d=is_dir: self._open_item(p) if not d else self._navigate(p))
                w.bind("<Button-1>",        lambda _, p=full: self._select(p))
                w.bind("<Button-2>",        lambda e, p=full, d=is_dir: self._item_context(e, p, d))
                w.bind("<Button-3>",        lambda e, p=full, d=is_dir: self._item_context(e, p, d))

    # ── list view ─────────────────────────────────────────────────────────────

    def _render_list(self, items: List[Tuple[str, bool]]) -> None:
        sf = MacScrolledFrame(self._content, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner

        # Header
        hdr = tk.Frame(inner, bg=T["panel_alt"])
        hdr.pack(fill="x")
        for text, width in [("Name", 300), ("Date Modified", 160), ("Size", 80), ("Kind", 120)]:
            lbl = tk.Label(hdr, text=text,
                           bg=T["panel_alt"], fg=T["text_muted"],
                           font=(FONT_UI, 11, "bold"),
                           width=width // 8, anchor="w", padx=4, pady=4)
            lbl.pack(side="left")

        tk.Frame(inner, bg=T["separator"], height=1).pack(fill="x")

        for idx, (full, is_dir) in enumerate(items):
            name = full.split("/")[-1]
            icon = self._get_icon(full, is_dir)
            bg   = T["win_bg"] if idx % 2 == 0 else T["panel_bg"]

            row = tk.Frame(inner, bg=bg, cursor="hand2")
            row.pack(fill="x")

            # Name column
            name_frame = tk.Frame(row, bg=bg, width=300)
            name_frame.pack(side="left")
            name_frame.pack_propagate(False)
            tk.Label(name_frame, text=icon,
                     bg=bg, font=(FONT_EMOJI, 13),
                     padx=4).pack(side="left")
            tk.Label(name_frame, text=name,
                     bg=bg, fg=T["text"],
                     font=(FONT_UI, 12), anchor="w").pack(side="left")

            # Date
            try:
                stat = self.wm.vfs.stat(full)
                mod  = datetime.datetime.fromtimestamp(stat["modified"]).strftime("%b %d, %Y")
                size = self._fmt_size(stat["size"]) if not is_dir else "—"
                kind = "Folder" if is_dir else self._get_kind(name)
            except Exception:
                mod, size, kind = "—", "—", "—"

            for val, w in [(mod, 160), (size, 80), (kind, 120)]:
                tk.Label(row, text=val,
                         bg=bg, fg=T["text_muted"],
                         font=(FONT_UI, 12),
                         width=w // 8, anchor="w",
                         padx=4, pady=4).pack(side="left")

            def on_enter(_, r=row) -> None:
                for w in r.winfo_children():
                    if isinstance(w, (tk.Frame, tk.Label)):
                        try: w.configure(bg=T["selection"])
                        except: pass

            def on_leave(_, r=row, b=bg) -> None:
                for w in r.winfo_children():
                    if isinstance(w, (tk.Frame, tk.Label)):
                        try: w.configure(bg=b)
                        except: pass

            for w in row.winfo_children() + [row]:
                w.bind("<Enter>",           lambda e, r=row: on_enter(e, r))
                w.bind("<Leave>",           lambda e, r=row, b=bg: on_leave(e, r, b))
                w.bind("<Button-1>",        lambda _, p=full: self._select(p))
                w.bind("<Double-Button-1>", lambda _, p=full, d=is_dir:
                        self._open_item(p) if not d else self._navigate(p))
                w.bind("<Button-2>",        lambda e, p=full, d=is_dir: self._item_context(e, p, d))
                w.bind("<Button-3>",        lambda e, p=full, d=is_dir: self._item_context(e, p, d))

    # ── column view ───────────────────────────────────────────────────────────

    def _render_column(self, items: List[Tuple[str, bool]]) -> None:
        """Simplified column view showing path components."""
        outer = tk.Frame(self._content, bg=T["win_bg"])
        outer.pack(fill="both", expand=True)

        # Show parent column + current column side by side
        parts = [p for p in self._path.split("/") if p]
        cols_to_show = min(3, len(parts) + 1)

        for ci in range(cols_to_show):
            col_frame = tk.Frame(outer, bg=T["win_bg"],
                                 highlightthickness=1,
                                 highlightbackground=T["separator"],
                                 width=200)
            col_frame.pack(side="left", fill="y")
            col_frame.pack_propagate(False)

            if ci < len(parts):
                # Build path up to this point
                col_path = "/" + "/".join(parts[:ci + 1])
                parent_path = "/" + "/".join(parts[:ci]) if ci > 0 else "/"
            else:
                col_path = self._path
                parent_path = self._path

            try:
                entries = self.wm.vfs.listdir(parent_path if ci > 0 else "/")
            except Exception:
                entries = []

            sf = tk.Frame(col_frame, bg=T["win_bg"])
            sf.pack(fill="both", expand=True)

            for name in entries:
                full = parent_path.rstrip("/") + "/" + name if ci > 0 else "/" + name
                is_dir = self.wm.vfs.isdir(full)
                icon = self._get_icon(full, is_dir)
                active = full == col_path or (ci == cols_to_show - 1 and full == self._path)
                bg = T["selection"] if active else T["win_bg"]
                fg = T["text"]

                row = tk.Frame(sf, bg=bg, cursor="hand2")
                row.pack(fill="x")
                tk.Label(row, text=icon, bg=bg,
                         font=(FONT_EMOJI, 12), padx=4).pack(side="left")
                tk.Label(row, text=name, bg=bg, fg=fg,
                         font=(FONT_UI, 12), anchor="w",
                         pady=3).pack(side="left", fill="x", expand=True)
                if is_dir:
                    tk.Label(row, text="›", bg=bg, fg=T["text_muted"],
                             font=(FONT_UI, 12), padx=4).pack(side="right")

                for w in (row,) + row.winfo_children():
                    w.bind("<Button-1>",        lambda _, p=full, d=is_dir:
                            self._navigate(p) if d else self._select(p))
                    w.bind("<Double-Button-1>", lambda _, p=full, d=is_dir:
                            self._open_item(p) if not d else self._navigate(p))

        # Preview panel
        preview = tk.Frame(outer, bg=T["panel_bg"])
        preview.pack(side="left", fill="both", expand=True)
        if self._selected and self.wm.vfs.isfile(self._selected):
            self._show_preview_panel(preview, self._selected)
        else:
            tk.Label(preview, text="Select a file\nto preview",
                     bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 13), justify="center").place(relx=0.5, rely=0.5, anchor="center")

    # ── item actions ──────────────────────────────────────────────────────────

    def _select(self, path: str) -> None:
        self._selected = path
        name = path.split("/")[-1]
        try:
            stat = self.wm.vfs.stat(path)
            size = self._fmt_size(stat["size"])
        except Exception:
            size = "—"
        self._status.configure(text=f'  "{name}"  |  {size}')

    def _open_item(self, path: str) -> None:
        if self.wm.vfs.isdir(path):
            self._navigate(path)
            return
        ext = os.path.splitext(path)[1].lower()
        if ext in (".py", ".txt", ".md", ".sh", ".plist", ".json", ".csv", ".html", ".css", ".js"):
            self.wm.open_textedit(path=path)
        elif ext in (".mp3", ".m3u"):
            self.wm.open_music()
        elif ext in (".jpg", ".png", ".gif"):
            self.wm.open_preview(path=path)
        elif ext == ".csv":
            self.wm.open_numbers(path=path)
        else:
            self.wm.open_textedit(path=path)

    def _item_context(self, e: tk.Event, path: str, is_dir: bool) -> None:
        self._select(path)
        menu = tk.Menu(self.wm.root, tearoff=False,
                       bg=T["menu_bg"], fg=T["menu_fg"],
                       activebackground=T["menu_hover"],
                       activeforeground=T["menu_fg_hover"],
                       font=(FONT_UI, 13), bd=0, relief="flat")
        name = path.split("/")[-1]
        menu.add_command(label=f'Open "{name}"',    command=lambda: self._open_item(path))
        menu.add_command(label="Open With ▶",       command=lambda: None)
        menu.add_separator()
        menu.add_command(label="Get Info",           command=lambda: self._get_info(path))
        menu.add_command(label="Rename…",            command=lambda: self._rename_item(path))
        menu.add_command(label="Duplicate",          command=lambda: self._duplicate(path))
        menu.add_command(label="Move to Trash",      command=lambda: self._delete(path))
        menu.add_separator()
        menu.add_command(label="Copy",               command=lambda: self.wm.clip.copy_files([path]))
        menu.add_command(label="Paste",              command=lambda: self._paste())
        menu.add_separator()
        if not is_dir:
            menu.add_command(label="Quick Look",     command=lambda: self.wm.open_preview(path=path))
        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def _new_folder(self) -> None:
        name = simpledialog.askstring("New Folder", "Folder name:",
                                      initialvalue="untitled folder",
                                      parent=self.wm.root)
        if name:
            path = self._path.rstrip("/") + "/" + name
            self.wm.vfs.makedirs(path)
            self._load(self._path)

    def _delete_sel(self) -> None:
        if self._selected:
            self._delete(self._selected)

    def _delete(self, path: str) -> None:
        name = path.split("/")[-1]
        if messagebox.askyesno("Move to Trash",
                               f"Move '{name}' to Trash?",
                               parent=self.wm.root):
            try:
                self.wm.vfs.remove(path)
                self._selected = None
                self._load(self._path)
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self.wm.root)

    def _rename_item(self, path: str) -> None:
        old_name = path.split("/")[-1]
        new_name = simpledialog.askstring("Rename", "New name:",
                                          initialvalue=old_name,
                                          parent=self.wm.root)
        if new_name and new_name != old_name:
            parent_dir = "/".join(path.split("/")[:-1]) or "/"
            new_path   = parent_dir.rstrip("/") + "/" + new_name
            try:
                self.wm.vfs.rename(path, new_path)
                self._load(self._path)
            except Exception as ex:
                messagebox.showerror("Error", str(ex), parent=self.wm.root)

    def _duplicate(self, path: str) -> None:
        name = path.split("/")[-1]
        base, ext = os.path.splitext(name)
        new_name = f"{base} copy{ext}"
        parent   = "/".join(path.split("/")[:-1]) or "/"
        new_path = parent.rstrip("/") + "/" + new_name
        try:
            self.wm.vfs.copy(path, new_path)
            self._load(self._path)
        except Exception as ex:
            messagebox.showerror("Error", str(ex), parent=self.wm.root)

    def _paste(self) -> None:
        files, mode = self.wm.clip.paste_files()
        for src in files:
            name = src.split("/")[-1]
            dst  = self._path.rstrip("/") + "/" + name
            try:
                self.wm.vfs.copy(src, dst)
                if mode == "cut":
                    self.wm.vfs.remove(src)
            except Exception:
                pass
        self.wm.clip.clear()
        self._load(self._path)

    def _get_info(self, path: Optional[str] = None) -> None:
        path = path or self._selected or self._path
        try:
            stat = self.wm.vfs.stat(path)
        except Exception:
            return
        name  = stat["name"]
        kind  = "Folder" if stat["is_dir"] else self._get_kind(name)
        size  = self._fmt_size(stat["size"])
        mod   = datetime.datetime.fromtimestamp(stat["modified"]).strftime("%b %d, %Y at %I:%M %p")
        cre   = datetime.datetime.fromtimestamp(stat["created"]).strftime("%b %d, %Y at %I:%M %p")
        messagebox.showinfo(
            f"Info: {name}",
            f"Name:      {name}\n"
            f"Kind:      {kind}\n"
            f"Size:      {size}\n"
            f"Location:  {path}\n"
            f"Created:   {cre}\n"
            f"Modified:  {mod}\n"
            f"Owner:     {stat['owner']}\n"
            f"Permissions: {stat['permissions']}",
            parent=self.wm.root,
        )

    def _do_search(self) -> None:
        query = self._search_var.get().strip()
        if not query:
            self._load(self._path)
            return
        hits = self.wm.vfs.find("/Users/user", query)
        for w in self._content.winfo_children():
            w.destroy()
        items = [(p, self.wm.vfs.isdir(p)) for p in hits]
        if self._view_mode == "list":
            self._render_list(items)
        else:
            self._render_icon(items)
        self._status.configure(text=f"  Search: '{query}'  |  {len(hits)} results")

    def _show_preview_panel(self, parent: tk.Frame, path: str) -> None:
        name = path.split("/")[-1]
        icon = self._get_icon(path, False)
        tk.Label(parent, text=icon,
                 bg=T["panel_bg"], font=(FONT_EMOJI, 48)).pack(pady=(30, 8))
        tk.Label(parent, text=name,
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold"),
                 wraplength=180, justify="center").pack()
        try:
            stat = self.wm.vfs.stat(path)
            mod  = datetime.datetime.fromtimestamp(stat["modified"]).strftime("%b %d, %Y")
            tk.Label(parent, text=f"{self._fmt_size(stat['size'])}  ·  {mod}",
                     bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 11)).pack(pady=4)
            content = self.wm.vfs.read(path)
            preview_text = content[:200] + ("…" if len(content) > 200 else "")
            tk.Label(parent, text=preview_text,
                     bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_MONO, 10),
                     wraplength=180, justify="left",
                     padx=8).pack(pady=8)
        except Exception:
            pass

    # ── helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _fmt_size(n: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024:
                return f"{n:.0f} {unit}"
            n /= 1024
        return f"{n:.1f} TB"

    @staticmethod
    def _get_kind(name: str) -> str:
        ext_map = {
            ".py":"Python Script", ".txt":"Plain Text", ".md":"Markdown",
            ".csv":"CSV File", ".json":"JSON", ".sh":"Shell Script",
            ".mp3":"MP3 Audio", ".jpg":"JPEG Image", ".png":"PNG Image",
            ".pdf":"PDF Document", ".zip":"ZIP Archive", ".html":"HTML",
            ".plist":"Property List",
        }
        ext = os.path.splitext(name)[1].lower()
        return ext_map.get(ext, "Document")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 17 — TEXTEDIT APP
# ─────────────────────────────────────────────────────────────────────────────

class TextEditApp(BaseWin):
    """
    macOS TextEdit clone.
    Features: syntax highlighting, line numbers, find/replace, word count.
    """

    SYNTAX: Dict[str, List[Tuple[str, str]]] = {
        "python": [
            (r"\b(def|class|import|from|return|if|elif|else|for|while|"
             r"in|not|and|or|is|None|True|False|pass|break|continue|"
             r"try|except|finally|with|as|yield|lambda|global|nonlocal|"
             r"del|raise|assert|print)\b",              "#cf8e6d"),
            (r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'',    "#6aab73"),
            (r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'', "#6aab73"),
            (r"#[^\n]*",                                "#7f7f7f"),
            (r"\b\d+\.?\d*\b",                          "#2aacb8"),
            (r"\b[A-Z][a-zA-Z0-9_]*\b",                "#ffc66d"),
        ],
        "markdown": [
            (r"^#{1,6}\s.*$",                           "#cf8e6d"),
            (r"\*\*[^*]+\*\*",                          "#ffffff"),
            (r"\*[^*]+\*",                              "#6aab73"),
            (r"`[^`]+`",                                "#2aacb8"),
            (r"^\s*[-*+]\s",                            "#ffc66d"),
            (r"https?://\S+",                           "#6897bb"),
        ],
        "shell": [
            (r"^#[^\n]*",                               "#7f7f7f"),
            (r"\b(echo|cd|ls|mkdir|rm|cp|mv|cat|grep|find|chmod|sudo|"
             r"export|source|if|then|else|fi|for|do|done|while|case|esac)\b", "#cf8e6d"),
            (r'"[^"]*"',                                "#6aab73"),
            (r"'\''[^'\'']*'\''",                        "#6aab73"),
            (r"\$\w+|\$\{[^}]+\}",                      "#2aacb8"),
        ],
    }

    def __init__(self, wm: "WM", path: Optional[str] = None) -> None:
        super().__init__(wm, title="TextEdit", w=760, h=560, icon="🗂️")
        self._path          = path
        self._modified      = False
        self._syntax_mode   = "none"
        self._show_lines    = True
        self._find_bar_open = False
        self._undo_stack:   List[str] = []
        self._redo_stack:   List[str] = []
        self._find_var      = tk.StringVar()
        self._replace_var   = tk.StringVar()

        self._build_ui()
        if path:
            self._open_file(path)
        else:
            self._new_doc()
        self._detect_syntax()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        c = self.client

        # Toolbar
        toolbar = tk.Frame(c, bg=T["panel_bg"],
                           highlightthickness=1,
                           highlightbackground=T["separator"])
        toolbar.pack(fill="x")

        def tb(text: str, cmd: Callable, tip: str = "") -> tk.Label:
            b = tk.Label(toolbar, text=text, bg=T["panel_bg"],
                         fg=T["text"], font=(FONT_UI, 12),
                         padx=8, pady=4, cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>", lambda _: cmd())
            b.bind("<Enter>", lambda _, lb=b: lb.configure(bg=T["panel_alt"]))
            b.bind("<Leave>", lambda _, lb=b: lb.configure(bg=T["panel_bg"]))
            if tip:
                make_tooltip(b, tip)
            return b

        tb("📄 New",   self._new_doc,    "New Document (⌘N)")
        tb("📂 Open",  self._open_dialog,"Open File (⌘O)")
        tb("💾 Save",  self._save,       "Save (⌘S)")
        tb("💾 Save As…", self._save_as, "Save As…")
        tk.Frame(toolbar, bg=T["separator"], width=1,
                 height=20).pack(side="left", padx=4, pady=4)
        tb("🔍 Find",  self._toggle_find, "Find/Replace (⌘F)")
        tb("⚙️ Syntax", self._syntax_menu, "Syntax Highlighting")

        # Word count label
        self._wc_lbl = tk.Label(toolbar, text="",
                                bg=T["panel_bg"], fg=T["text_muted"],
                                font=(FONT_UI, 11))
        self._wc_lbl.pack(side="right", padx=8)

        # Find bar (hidden initially)
        self._find_bar = tk.Frame(c, bg=T["panel_alt"],
                                  highlightthickness=1,
                                  highlightbackground=T["separator"])

        # Editor area (line numbers + text widget)
        editor_frame = tk.Frame(c, bg=T["code_bg"])
        editor_frame.pack(fill="both", expand=True)

        # Line numbers
        self._line_nums = tk.Text(
            editor_frame,
            width=4, bg=T["panel_alt"],
            fg=T["text_muted"],
            font=(FONT_MONO, 13),
            relief="flat", bd=0,
            highlightthickness=0,
            state="disabled", cursor="arrow",
            padx=4,
        )
        if self._show_lines:
            self._line_nums.pack(side="left", fill="y")

        # Scrollbar
        vscroll = tk.Scrollbar(editor_frame, orient="vertical",
                               width=8, relief="flat")
        vscroll.pack(side="right", fill="y")

        # Main text editor
        self._text = tk.Text(
            editor_frame,
            bg=T["code_bg"], fg=T["code_fg"],
            insertbackground=T["text"],
            selectbackground=T["selection"],
            font=(FONT_MONO, 13),
            relief="flat", bd=0,
            highlightthickness=0,
            undo=True,
            yscrollcommand=self._on_yscroll,
            wrap="none",
            padx=8, pady=6,
            tabs=("1c",),
        )
        self._text.pack(side="left", fill="both", expand=True)
        vscroll.configure(command=self._on_vscroll)

        hscroll = tk.Scrollbar(c, orient="horizontal", relief="flat", width=8)
        hscroll.pack(fill="x")
        self._text.configure(xscrollcommand=hscroll.set)
        hscroll.configure(command=self._text.xview)

        # Status bar
        self._status = tk.Label(c, text="",
                                bg=T["status_bg"], fg=T["text_muted"],
                                font=(FONT_UI, 11), anchor="w", padx=10,
                                highlightthickness=1,
                                highlightbackground=T["status_border"])
        self._status.pack(fill="x")

        # Configure syntax tags
        self._text.tag_configure("kw",     foreground="#cf8e6d")
        self._text.tag_configure("string", foreground="#6aab73")
        self._text.tag_configure("comment",foreground="#7f7f7f", font=(FONT_MONO, 13, "italic"))
        self._text.tag_configure("number", foreground="#2aacb8")
        self._text.tag_configure("class",  foreground="#ffc66d")
        self._text.tag_configure("find_hl",background="#ffdd00", foreground="#000000")

        # Bindings
        self._text.bind("<KeyRelease>",    self._on_key)
        self._text.bind("<Button-1>",      self._update_cursor_pos)
        self._text.bind("<Control-s>",     lambda _: self._save())
        self._text.bind("<Control-n>",     lambda _: self._new_doc())
        self._text.bind("<Control-o>",     lambda _: self._open_dialog())
        self._text.bind("<Control-f>",     lambda _: self._toggle_find())
        self._text.bind("<Control-z>",     lambda _: None)
        self._text.bind("<Control-y>",     lambda _: None)

    # ── document operations ───────────────────────────────────────────────────

    def _new_doc(self) -> None:
        self._path = None
        self._text.delete("1.0", "end")
        self._modified = False
        self.set_title("TextEdit — Untitled")
        self._update_line_numbers()
        self._update_status()

    def _open_file(self, path: str) -> None:
        try:
            content = self.wm.vfs.read(path)
            self._text.delete("1.0", "end")
            self._text.insert("1.0", content)
            self._path = path
            name = path.split("/")[-1]
            self.set_title(f"TextEdit — {name}")
            self._modified = False
            self._update_line_numbers()
            self._detect_syntax()
            self._apply_syntax()
            self._update_status()
        except Exception as ex:
            messagebox.showerror("Open Error", str(ex), parent=self.wm.root)

    def _open_dialog(self) -> None:
        path = simpledialog.askstring(
            "Open File", "Enter file path:",
            initialvalue=self._path or self.wm.vfs.HOME + "/",
            parent=self.wm.root,
        )
        if path:
            self._open_file(path)

    def _save(self) -> None:
        if not self._path:
            self._save_as()
            return
        content = self._text.get("1.0", "end-1c")
        try:
            self.wm.vfs.write(self._path, content)
            self._modified = False
            name = self._path.split("/")[-1]
            self.set_title(f"TextEdit — {name}")
            self._status.configure(text=f"  Saved: {self._path}")
        except Exception as ex:
            messagebox.showerror("Save Error", str(ex), parent=self.wm.root)

    def _save_as(self) -> None:
        default = self._path or self.wm.vfs.HOME + "/Documents/Untitled.txt"
        path = simpledialog.askstring("Save As",
                                      "Save to path:",
                                      initialvalue=default,
                                      parent=self.wm.root)
        if path:
            self._path = path
            self._save()

    # ── find/replace ──────────────────────────────────────────────────────────

    def _toggle_find(self) -> None:
        if self._find_bar_open:
            self._find_bar.pack_forget()
            self._find_bar_open = False
        else:
            self._find_bar.pack(fill="x", before=self._text.master)
            self._find_bar_open = True
            self._build_find_bar()

    def _build_find_bar(self) -> None:
        for w in self._find_bar.winfo_children():
            w.destroy()
        tk.Label(self._find_bar, text="Find:",
                 bg=T["panel_alt"], fg=T["text"],
                 font=(FONT_UI, 12), padx=4).pack(side="left")
        find_entry = tk.Entry(self._find_bar, textvariable=self._find_var,
                              bg=T["input_bg"], fg=T["text"],
                              font=(FONT_UI, 12), relief="flat",
                              highlightthickness=1,
                              highlightbackground=T["input_border"],
                              width=20)
        find_entry.pack(side="left", padx=4, pady=4)
        find_entry.focus_set()

        tk.Label(self._find_bar, text="Replace:",
                 bg=T["panel_alt"], fg=T["text"],
                 font=(FONT_UI, 12), padx=4).pack(side="left")
        repl_entry = tk.Entry(self._find_bar, textvariable=self._replace_var,
                              bg=T["input_bg"], fg=T["text"],
                              font=(FONT_UI, 12), relief="flat",
                              highlightthickness=1,
                              highlightbackground=T["input_border"],
                              width=20)
        repl_entry.pack(side="left", padx=4, pady=4)

        for label, cmd in [("Find", self._do_find),
                            ("Replace", self._do_replace),
                            ("Replace All", self._do_replace_all)]:
            tk.Label(self._find_bar, text=label,
                     bg=T["accent"], fg="#ffffff",
                     font=(FONT_UI, 11), padx=8, pady=3,
                     cursor="hand2").pack(side="left", padx=3)

        tk.Label(self._find_bar, text="✕",
                 bg=T["panel_alt"], fg=T["text_muted"],
                 font=(FONT_UI, 12), padx=6, cursor="hand2").pack(side="right")

        self._find_results = tk.Label(self._find_bar, text="",
                                      bg=T["panel_alt"], fg=T["text_muted"],
                                      font=(FONT_UI, 11))
        self._find_results.pack(side="left", padx=8)
        find_entry.bind("<Return>", lambda _: self._do_find())

    def _do_find(self) -> None:
        query = self._find_var.get()
        if not query:
            return
        self._text.tag_remove("find_hl", "1.0", "end")
        count = 0
        start = "1.0"
        while True:
            pos = self._text.search(query, start, stopindex="end", nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(query)}c"
            self._text.tag_add("find_hl", pos, end)
            start = end
            count += 1
        if count:
            self._text.see(self._text.tag_ranges("find_hl")[0])
        if hasattr(self, "_find_results"):
            self._find_results.configure(text=f"{count} results")

    def _do_replace(self) -> None:
        query   = self._find_var.get()
        replace = self._replace_var.get()
        if not query:
            return
        pos = self._text.search(query, "insert", stopindex="end", nocase=True)
        if pos:
            end = f"{pos}+{len(query)}c"
            self._text.delete(pos, end)
            self._text.insert(pos, replace)

    def _do_replace_all(self) -> None:
        query   = self._find_var.get()
        replace = self._replace_var.get()
        if not query:
            return
        content = self._text.get("1.0", "end-1c")
        new     = re.sub(re.escape(query), replace, content, flags=re.IGNORECASE)
        self._text.delete("1.0", "end")
        self._text.insert("1.0", new)

    # ── syntax highlighting ───────────────────────────────────────────────────

    def _detect_syntax(self) -> None:
        if not self._path:
            self._syntax_mode = "none"
            return
        ext = os.path.splitext(self._path)[1].lower()
        if ext == ".py":
            self._syntax_mode = "python"
        elif ext == ".md":
            self._syntax_mode = "markdown"
        elif ext in (".sh", ".bash", ".zsh"):
            self._syntax_mode = "shell"
        else:
            self._syntax_mode = "none"

    def _apply_syntax(self) -> None:
        if self._syntax_mode == "none":
            return
        patterns = self.SYNTAX.get(self._syntax_mode, [])
        tag_names = ["kw", "string", "comment", "number", "class"]
        for i, (pattern, color) in enumerate(patterns):
            tag = tag_names[i] if i < len(tag_names) else f"syn_{i}"
            self._text.tag_configure(tag, foreground=color)
            self._text.tag_remove(tag, "1.0", "end")
            content = self._text.get("1.0", "end")
            for m in re.finditer(pattern, content, re.MULTILINE):
                start_idx = f"1.0+{m.start()}c"
                end_idx   = f"1.0+{m.end()}c"
                self._text.tag_add(tag, start_idx, end_idx)

    def _syntax_menu(self) -> None:
        menu = tk.Menu(self.wm.root, tearoff=False,
                       bg=T["menu_bg"], fg=T["menu_fg"],
                       activebackground=T["menu_hover"],
                       activeforeground=T["menu_fg_hover"],
                       font=(FONT_UI, 13))
        for mode in ["none", "python", "markdown", "shell"]:
            label = mode.capitalize()
            if mode == self._syntax_mode:
                label = "✓ " + label
            menu.add_command(label=label,
                             command=lambda m=mode: self._set_syntax(m))
        try:
            menu.tk_popup(self.wm.root.winfo_pointerx(),
                          self.wm.root.winfo_pointery())
        finally:
            menu.grab_release()

    def _set_syntax(self, mode: str) -> None:
        self._syntax_mode = mode
        self._apply_syntax()

    # ── event handlers ────────────────────────────────────────────────────────

    def _on_key(self, _: tk.Event) -> None:
        self._modified = True
        name = (self._path or "Untitled").split("/")[-1]
        self.set_title(f"TextEdit — {name} •")
        self._update_line_numbers()
        self._update_word_count()
        self._update_cursor_pos()
        # Incremental syntax highlight (throttle to every 10 keystrokes)
        if random.random() < 0.1:
            self._apply_syntax()

    def _on_yscroll(self, *args) -> None:
        self._line_nums.yview_moveto(args[0])

    def _on_vscroll(self, *args) -> None:
        self._text.yview(*args)
        self._line_nums.yview(*args)

    def _update_line_numbers(self) -> None:
        if not self._show_lines:
            return
        content  = self._text.get("1.0", "end-1c")
        n_lines  = content.count("\n") + 1
        nums     = "\n".join(str(i) for i in range(1, n_lines + 1))
        self._line_nums.configure(state="normal")
        self._line_nums.delete("1.0", "end")
        self._line_nums.insert("1.0", nums)
        self._line_nums.configure(state="disabled")

    def _update_word_count(self) -> None:
        content = self._text.get("1.0", "end-1c")
        words   = len(content.split())
        chars   = len(content)
        self._wc_lbl.configure(text=f"{words} words  {chars} chars")

    def _update_cursor_pos(self, _: Optional[tk.Event] = None) -> None:
        try:
            pos  = self._text.index("insert")
            line, col = pos.split(".")
            self._status.configure(text=f"  Line {line}, Col {int(col)+1}  |  {self._syntax_mode.capitalize()}")
        except Exception:
            pass

    def _update_status(self) -> None:
        path_str = self._path or "Untitled"
        self._status.configure(text=f"  {path_str}")
        self._update_word_count()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 18 — TERMINAL APP
# ─────────────────────────────────────────────────────────────────────────────

class TerminalApp(BaseWin):
    """
    macOS Terminal clone (zsh-style prompt).
    Supports 65+ commands.
    """

    BANNER = (
        f"MacPyOS {MACPYOS_VERSION} ({MACPYOS_CODENAME})\n"
        "Type 'help' for a list of commands.\n"
        "──────────────────────────────────────\n"
    )

    def __init__(self, wm: "WM", cwd: Optional[str] = None) -> None:
        super().__init__(wm, title="Terminal", w=760, h=500, icon="💻",
                         min_w=400, min_h=200)
        self._cwd      = cwd or wm.vfs.HOME
        self._env: Dict[str, str] = {
            "HOME":  wm.vfs.HOME,
            "USER":  wm.users.current_user() or "user",
            "SHELL": "/bin/zsh",
            "TERM":  "xterm-256color",
            "PATH":  "/usr/local/bin:/usr/bin:/bin",
            "PWD":   self._cwd,
        }
        self._history:     List[str] = []
        self._hist_idx:    int       = -1
        self._aliases:     Dict[str, str] = {
            "ll": "ls -l", "la": "ls -a", "l": "ls",
            "..": "cd ..", "...": "cd ../..",
            "~":  "cd ~",  "clr": "clear",
            "py": "python3",
        }
        self._bg_color = "#1e1e1e"   # Terminal always dark
        self._fg_color = "#f0f0f0"
        self._build_ui()
        self._write(self.BANNER)
        self._prompt()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        c = self.client
        c.configure(bg=self._bg_color)

        # Tab bar (like macOS Terminal tabs)
        self._tabbar = tk.Frame(c, bg="#2d2d2d", height=28)
        self._tabbar.pack(fill="x")
        self._tabbar.pack_propagate(False)
        self._tab_lbl = tk.Label(self._tabbar,
                                 text="zsh — MacPyOS",
                                 bg="#3c3c3c", fg="#ffffff",
                                 font=(FONT_UI, 11), padx=12, pady=4)
        self._tab_lbl.pack(side="left")
        tk.Label(self._tabbar, text="＋",
                 bg="#2d2d2d", fg="#888888",
                 font=(FONT_UI, 14), padx=8, cursor="hand2").pack(side="left")

        # Output area
        text_frame = tk.Frame(c, bg=self._bg_color)
        text_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(text_frame, orient="vertical",
                                 bg="#3c3c3c", troughcolor="#2d2d2d",
                                 width=8, relief="flat")
        scrollbar.pack(side="right", fill="y")

        self._out = tk.Text(
            text_frame,
            bg=self._bg_color, fg=self._fg_color,
            insertbackground=self._fg_color,
            selectbackground="#404040",
            font=(FONT_MONO, 13),
            relief="flat", bd=0,
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
            wrap="word",
            state="disabled",
            padx=10, pady=8,
            cursor="xterm",
        )
        self._out.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self._out.yview)

        # Input line
        input_frame = tk.Frame(c, bg=self._bg_color)
        input_frame.pack(fill="x")

        self._prompt_lbl = tk.Label(
            input_frame, text="",
            bg=self._bg_color, fg="#00ff88",
            font=(FONT_MONO, 13), padx=8,
        )
        self._prompt_lbl.pack(side="left")

        self._input = tk.Entry(
            input_frame,
            bg=self._bg_color, fg=self._fg_color,
            insertbackground=self._fg_color,
            font=(FONT_MONO, 13),
            relief="flat", bd=0,
            highlightthickness=0,
        )
        self._input.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=4)
        self._input.focus_set()

        # Text colour tags
        self._out.tag_configure("prompt",  foreground="#00ff88")
        self._out.tag_configure("cmd",     foreground="#ffffff")
        self._out.tag_configure("error",   foreground="#ff5555")
        self._out.tag_configure("success", foreground="#50fa7b")
        self._out.tag_configure("info",    foreground="#8be9fd")
        self._out.tag_configure("warn",    foreground="#ffb86c")
        self._out.tag_configure("dir",     foreground="#6272a4")
        self._out.tag_configure("bold",    font=(FONT_MONO, 13, "bold"))
        self._out.tag_configure("dim",     foreground="#888888")

        # Bindings
        self._input.bind("<Return>",    self._on_enter)
        self._input.bind("<Up>",        self._hist_up)
        self._input.bind("<Down>",      self._hist_down)
        self._input.bind("<Tab>",       self._tab_complete)
        self._input.bind("<Control-c>", self._ctrl_c)
        self._input.bind("<Control-l>", lambda _: self._cmd_clear([]))

    # ── output helpers ────────────────────────────────────────────────────────

    def _write(self, text: str, tag: str = "") -> None:
        self._out.configure(state="normal")
        if tag:
            self._out.insert("end", text, tag)
        else:
            self._out.insert("end", text)
        self._out.configure(state="disabled")
        self._out.see("end")

    def _writeln(self, text: str = "", tag: str = "") -> None:
        self._write(text + "\n", tag)

    def _prompt(self) -> None:
        user    = self._env.get("USER", "user")
        host    = "MacPyOS"
        short   = self._cwd.replace(self.wm.vfs.HOME, "~")
        prompt  = f"{user}@{host} {short} % "
        self._prompt_lbl.configure(text=prompt)
        self._tab_lbl.configure(text=f"zsh — {short}")
        self._input.delete(0, "end")

    # ── input handling ────────────────────────────────────────────────────────

    def _on_enter(self, _: tk.Event) -> None:
        line = self._input.get().strip()
        self._input.delete(0, "end")
        if not line:
            self._prompt()
            return

        # Echo command
        user  = self._env.get("USER", "user")
        short = self._cwd.replace(self.wm.vfs.HOME, "~")
        self._write(f"{user}@MacPyOS {short} % ", "prompt")
        self._writeln(line, "cmd")

        # History
        if not self._history or self._history[-1] != line:
            self._history.append(line)
        self._hist_idx = len(self._history)

        # Expand aliases
        parts = line.split()
        if parts and parts[0] in self._aliases:
            line = self._aliases[parts[0]] + (" " + " ".join(parts[1:]) if len(parts) > 1 else "")

        self._dispatch(line)
        self._prompt()

    def _hist_up(self, _: tk.Event) -> None:
        if self._hist_idx > 0:
            self._hist_idx -= 1
            self._input.delete(0, "end")
            self._input.insert(0, self._history[self._hist_idx])

    def _hist_down(self, _: tk.Event) -> None:
        if self._hist_idx < len(self._history) - 1:
            self._hist_idx += 1
            self._input.delete(0, "end")
            self._input.insert(0, self._history[self._hist_idx])
        else:
            self._hist_idx = len(self._history)
            self._input.delete(0, "end")

    def _tab_complete(self, _: tk.Event) -> str:
        text  = self._input.get()
        parts = text.split()
        if not parts:
            return "break"
        prefix = parts[-1]
        try:
            entries = self.wm.vfs.listdir(self._cwd)
        except Exception:
            entries = []
        matches = [e for e in entries if e.startswith(prefix)]
        if len(matches) == 1:
            parts[-1] = matches[0]
            if self.wm.vfs.isdir(self._cwd + "/" + matches[0]):
                parts[-1] += "/"
            self._input.delete(0, "end")
            self._input.insert(0, " ".join(parts))
        elif len(matches) > 1:
            self._writeln("  ".join(matches), "info")
        return "break"

    def _ctrl_c(self, _: tk.Event) -> None:
        self._writeln("^C", "error")
        self._prompt()

    # ── command dispatcher ────────────────────────────────────────────────────

    def _dispatch(self, line: str) -> None:
        # Handle pipes (simplified)
        if "|" in line:
            parts = [p.strip() for p in line.split("|")]
            output = ""
            for p in parts:
                output = self._exec_with_input(p, output)
            if output:
                self._write(output)
            return

        # Handle redirects
        stdout_file = None
        append_mode = False
        if ">>" in line:
            line, stdout_file = line.split(">>", 1)
            line = line.strip(); stdout_file = stdout_file.strip()
            append_mode = True
        elif ">" in line:
            line, stdout_file = line.split(">", 1)
            line = line.strip(); stdout_file = stdout_file.strip()

        tokens = self._tokenize(line)
        if not tokens:
            return
        cmd, args = tokens[0], tokens[1:]

        # Expand ~ and env vars
        args = [self._expand(a) for a in args]

        # Capture output for redirect
        if stdout_file:
            import io
            old_write = self._writeln
            buf: List[str] = []
            self._writeln = lambda t="", tag="": buf.append(t + "\n")  # type: ignore
            self._run_cmd(cmd, args)
            self._writeln = old_write  # type: ignore
            content = "".join(buf)
            path = self._resolve(stdout_file)
            self.wm.vfs.write(path, content, append=append_mode)
        else:
            self._run_cmd(cmd, args)

    def _exec_with_input(self, line: str, stdin: str) -> str:
        """Execute a command and return its output as a string."""
        tokens = self._tokenize(line)
        if not tokens:
            return stdin
        cmd, args = tokens[0], tokens[1:]
        buf: List[str] = []
        old_write = self._writeln
        self._writeln = lambda t="", tag="": buf.append(t + "\n")  # type: ignore
        if cmd == "grep":
            pattern = args[0] if args else ""
            for line in stdin.splitlines():
                if re.search(pattern, line, re.IGNORECASE):
                    buf.append(line + "\n")
        elif cmd == "wc":
            lines = stdin.count("\n")
            words = len(stdin.split())
            chars = len(stdin)
            buf.append(f"  {lines}  {words}  {chars}\n")
        elif cmd == "sort":
            lines = sorted(stdin.splitlines())
            buf.extend(l + "\n" for l in lines)
        elif cmd == "head":
            n = int(args[0]) if args and args[0].lstrip("-").isdigit() else 10
            for l in stdin.splitlines()[:n]:
                buf.append(l + "\n")
        elif cmd == "tail":
            n = int(args[0]) if args and args[0].lstrip("-").isdigit() else 10
            for l in stdin.splitlines()[-n:]:
                buf.append(l + "\n")
        elif cmd == "cat":
            buf.append(stdin)
        else:
            buf.append(stdin)
        self._writeln = old_write  # type: ignore
        return "".join(buf)

    def _run_cmd(self, cmd: str, args: List[str]) -> None:
        COMMANDS = {
            "ls": self._cmd_ls, "ll": self._cmd_ll,
            "cd": self._cmd_cd, "pwd": self._cmd_pwd,
            "mkdir": self._cmd_mkdir, "rmdir": self._cmd_rmdir,
            "touch": self._cmd_touch, "rm": self._cmd_rm,
            "cp": self._cmd_cp, "mv": self._cmd_mv,
            "cat": self._cmd_cat, "head": self._cmd_head,
            "tail": self._cmd_tail, "wc": self._cmd_wc,
            "echo": self._cmd_echo, "printf": self._cmd_printf,
            "clear": self._cmd_clear, "reset": self._cmd_clear,
            "help": self._cmd_help, "man": self._cmd_man,
            "which": self._cmd_which, "type": self._cmd_type,
            "whoami": self._cmd_whoami, "id": self._cmd_id,
            "hostname": self._cmd_hostname, "uname": self._cmd_uname,
            "date": self._cmd_date, "uptime": self._cmd_uptime,
            "env": self._cmd_env, "export": self._cmd_export,
            "unset": self._cmd_unset, "printenv": self._cmd_printenv,
            "alias": self._cmd_alias, "unalias": self._cmd_unalias,
            "history": self._cmd_history,
            "find": self._cmd_find, "grep": self._cmd_grep,
            "sort": self._cmd_sort, "uniq": self._cmd_uniq,
            "tr": self._cmd_tr, "sed": self._cmd_sed,
            "awk": self._cmd_awk, "cut": self._cmd_cut,
            "stat": self._cmd_stat, "file": self._cmd_file,
            "diff": self._cmd_diff, "wc": self._cmd_wc,
            "du": self._cmd_du, "df": self._cmd_df,
            "ps": self._cmd_ps, "kill": self._cmd_kill,
            "top": self._cmd_top, "jobs": self._cmd_jobs,
            "sleep": self._cmd_sleep, "time": self._cmd_time_cmd,
            "python3": self._cmd_python3, "python": self._cmd_python3,
            "pip3": self._cmd_pip, "pip": self._cmd_pip,
            "open": self._cmd_open, "nano": self._cmd_nano,
            "vi": self._cmd_vi, "vim": self._cmd_vi,
            "less": self._cmd_less, "more": self._cmd_less,
            "curl": self._cmd_curl, "wget": self._cmd_wget,
            "ping": self._cmd_ping, "ifconfig": self._cmd_ifconfig,
            "ssh": self._cmd_ssh, "scp": self._cmd_scp,
            "zip": self._cmd_zip, "unzip": self._cmd_unzip,
            "tar": self._cmd_tar, "gzip": self._cmd_gzip,
            "tree": self._cmd_tree, "ls": self._cmd_ls,
            "chmod": self._cmd_chmod, "chown": self._cmd_chown,
            "ln": self._cmd_ln, "readlink": self._cmd_readlink,
            "basename": self._cmd_basename, "dirname": self._cmd_dirname,
            "realpath": self._cmd_realpath,
            "sw_vers": self._cmd_sw_vers, "system_profiler": self._cmd_system_profiler,
            "defaults": self._cmd_defaults, "plutil": self._cmd_plutil,
            "caffeinate": self._cmd_caffeinate,
            "say": self._cmd_say, "screensaver": self._cmd_screensaver,
            "exit": self._cmd_exit, "logout": self._cmd_exit,
            "sudo": self._cmd_sudo,
            "xargs": self._cmd_xargs,
            "yes": self._cmd_yes, "false": self._cmd_false,
            "true": self._cmd_true,
            "seq": self._cmd_seq, "expr": self._cmd_expr,
            "bc": self._cmd_bc,
        }
        fn = COMMANDS.get(cmd)
        if fn:
            fn(args)
        else:
            self._writeln(f"zsh: command not found: {cmd}", "error")
            self._writeln(f"Did you mean one of: {', '.join(list(COMMANDS)[:5])}?", "dim")

    # ── individual commands ───────────────────────────────────────────────────

    def _cmd_ls(self, args: List[str]) -> None:
        show_all = "-a" in args or "-la" in args or "-al" in args
        long_fmt = "-l" in args or "-la" in args or "-al" in args
        path_arg = next((a for a in args if not a.startswith("-")), self._cwd)
        path     = self._resolve(path_arg)
        try:
            entries = self.wm.vfs.listdir(path)
        except FileNotFoundError:
            self._writeln(f"ls: {path_arg}: No such file or directory", "error"); return
        except NotADirectoryError:
            self._writeln(f"ls: {path_arg}: Not a directory", "error"); return

        if not show_all:
            entries = [e for e in entries if not e.startswith(".")]

        if long_fmt:
            self._writeln(f"total {len(entries)}", "dim")
            for name in entries:
                full  = path.rstrip("/") + "/" + name
                is_dir = self.wm.vfs.isdir(full)
                try:
                    st    = self.wm.vfs.stat(full)
                    perms = st["permissions"]
                    size  = st["size"]
                    mod   = datetime.datetime.fromtimestamp(st["modified"]).strftime("%b %d %H:%M")
                    owner = st["owner"]
                except Exception:
                    perms = "----------"; size = 0; mod = ""; owner = "user"
                tag = "dir" if is_dir else ""
                self._write(f"{perms}  1 {owner:<8} staff {size:>8}  {mod}  ")
                self._writeln(name, tag)
        else:
            cols   = 4
            padded = [e.ljust(24) for e in entries]
            for i in range(0, len(padded), cols):
                row = "  ".join(padded[i:i + cols])
                line_parts = entries[i:i + cols]
                self._writeln(row)

    def _cmd_ll(self, args: List[str]) -> None:
        self._cmd_ls(["-l"] + args)

    def _cmd_cd(self, args: List[str]) -> None:
        target = args[0] if args else self.wm.vfs.HOME
        path   = self._resolve(target)
        if not self.wm.vfs.exists(path):
            self._writeln(f"cd: no such file or directory: {target}", "error")
        elif not self.wm.vfs.isdir(path):
            self._writeln(f"cd: not a directory: {target}", "error")
        else:
            self._cwd = path
            self._env["PWD"] = path
            self.wm.vfs.cwd = path

    def _cmd_pwd(self, args: List[str]) -> None:
        self._writeln(self._cwd)

    def _cmd_mkdir(self, args: List[str]) -> None:
        if not args:
            self._writeln("mkdir: missing operand", "error"); return
        parents = "-p" in args
        for a in [x for x in args if not x.startswith("-")]:
            path = self._resolve(a)
            try:
                if parents:
                    self.wm.vfs.makedirs(path)
                else:
                    self.wm.vfs.mkdir(path)
            except Exception as ex:
                self._writeln(f"mkdir: {ex}", "error")

    def _cmd_rmdir(self, args: List[str]) -> None:
        for a in args:
            path = self._resolve(a)
            try:
                if self.wm.vfs.listdir(path):
                    self._writeln(f"rmdir: {a}: Directory not empty", "error")
                else:
                    self.wm.vfs.remove(path)
            except Exception as ex:
                self._writeln(f"rmdir: {ex}", "error")

    def _cmd_touch(self, args: List[str]) -> None:
        for a in [x for x in args if not x.startswith("-")]:
            path = self._resolve(a)
            if not self.wm.vfs.exists(path):
                self.wm.vfs.write(path, "")
            else:
                # Update mtime
                n = self.wm.vfs._get_node(path)
                if n:
                    n.modified = time.time()
                    n.accessed = time.time()

    def _cmd_rm(self, args: List[str]) -> None:
        recursive = "-r" in args or "-rf" in args or "-fr" in args
        force     = "-f" in args or "-rf" in args
        targets   = [a for a in args if not a.startswith("-")]
        for a in targets:
            path = self._resolve(a)
            if not self.wm.vfs.exists(path):
                if not force:
                    self._writeln(f"rm: {a}: No such file or directory", "error")
                continue
            if self.wm.vfs.isdir(path) and not recursive:
                self._writeln(f"rm: {a}: is a directory", "error"); continue
            try:
                self.wm.vfs.remove(path)
            except Exception as ex:
                self._writeln(f"rm: {ex}", "error")

    def _cmd_cp(self, args: List[str]) -> None:
        targets = [a for a in args if not a.startswith("-")]
        if len(targets) < 2:
            self._writeln("cp: missing destination", "error"); return
        src, dst = targets[0], targets[-1]
        try:
            self.wm.vfs.copy(self._resolve(src), self._resolve(dst))
        except Exception as ex:
            self._writeln(f"cp: {ex}", "error")

    def _cmd_mv(self, args: List[str]) -> None:
        targets = [a for a in args if not a.startswith("-")]
        if len(targets) < 2:
            self._writeln("mv: missing destination", "error"); return
        src = self._resolve(targets[0])
        dst = self._resolve(targets[-1])
        if self.wm.vfs.isdir(dst):
            dst = dst.rstrip("/") + "/" + src.split("/")[-1]
        try:
            self.wm.vfs.rename(src, dst)
        except Exception as ex:
            self._writeln(f"mv: {ex}", "error")

    def _cmd_cat(self, args: List[str]) -> None:
        if not args:
            self._writeln("(reading stdin — press Ctrl+C to cancel)", "dim"); return
        for a in args:
            path = self._resolve(a)
            try:
                content = self.wm.vfs.read(path)
                self._write(content)
                if not content.endswith("\n"):
                    self._writeln()
            except Exception as ex:
                self._writeln(f"cat: {a}: {ex}", "error")

    def _cmd_head(self, args: List[str]) -> None:
        n = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] in ("-n",) and i + 1 < len(args):
                n = int(args[i + 1]); i += 2
            elif args[i].startswith("-") and args[i][1:].isdigit():
                n = int(args[i][1:]); i += 1
            else:
                files.append(args[i]); i += 1
        for f in files:
            path = self._resolve(f)
            try:
                lines = self.wm.vfs.read(path).splitlines()
                for ln in lines[:n]:
                    self._writeln(ln)
            except Exception as ex:
                self._writeln(f"head: {f}: {ex}", "error")

    def _cmd_tail(self, args: List[str]) -> None:
        n = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] == "-n" and i + 1 < len(args):
                n = int(args[i + 1]); i += 2
            elif args[i].startswith("-") and args[i][1:].isdigit():
                n = int(args[i][1:]); i += 1
            else:
                files.append(args[i]); i += 1
        for f in files:
            path = self._resolve(f)
            try:
                lines = self.wm.vfs.read(path).splitlines()
                for ln in lines[-n:]:
                    self._writeln(ln)
            except Exception as ex:
                self._writeln(f"tail: {f}: {ex}", "error")

    def _cmd_wc(self, args: List[str]) -> None:
        files = [a for a in args if not a.startswith("-")]
        if not files:
            self._writeln("wc: no files specified", "error"); return
        for f in files:
            path = self._resolve(f)
            try:
                c = self.wm.vfs.read(path)
                self._writeln(f"  {c.count(chr(10)):6}  {len(c.split()):6}  {len(c):6}  {f}")
            except Exception as ex:
                self._writeln(f"wc: {f}: {ex}", "error")

    def _cmd_echo(self, args: List[str]) -> None:
        no_newline = "-n" in args
        parts      = [a for a in args if a != "-n"]
        text       = " ".join(parts)
        # Expand $VAR
        text = re.sub(r"\$(\w+)", lambda m: self._env.get(m.group(1), ""), text)
        if no_newline:
            self._write(text)
        else:
            self._writeln(text)

    def _cmd_printf(self, args: List[str]) -> None:
        if not args:
            return
        fmt  = args[0]
        rest = args[1:]
        try:
            out = fmt.replace("\\n", "\n").replace("\\t", "\t")
            if rest:
                out = out % tuple(rest)
            self._write(out)
        except Exception:
            self._write(fmt.replace("\\n", "\n"))

    def _cmd_clear(self, args: List[str]) -> None:
        self._out.configure(state="normal")
        self._out.delete("1.0", "end")
        self._out.configure(state="disabled")

    def _cmd_help(self, args: List[str]) -> None:
        self._writeln("MacPyOS Terminal — Available Commands", "bold")
        self._writeln("─" * 50, "dim")
        groups = {
            "File & Directory": "ls ll cd pwd mkdir rmdir touch rm cp mv tree stat file du",
            "Text Processing":  "cat head tail wc grep sort uniq tr sed awk cut diff less more",
            "System":           "ps kill top jobs sleep uptime date uname hostname whoami id env",
            "Shell":            "echo printf clear history alias unalias export unset which type",
            "Network":          "curl wget ping ifconfig ssh scp",
            "Archive":          "zip unzip tar gzip",
            "macOS Specific":   "open nano vi less sw_vers system_profiler defaults say caffeinate",
            "Misc":             "python3 pip3 sudo exit seq expr bc xargs yes true false",
        }
        for group, cmds in groups.items():
            self._writeln(f"\n  {group}:", "info")
            self._writeln(f"    {cmds}", "dim")
        self._writeln()

    def _cmd_man(self, args: List[str]) -> None:
        if not args:
            self._writeln("man: what manual page do you want?", "error"); return
        cmd = args[0]
        manpages: Dict[str, str] = {
            "ls":   "ls — list directory contents\nUsage: ls [-l] [-a] [path]",
            "cd":   "cd — change directory\nUsage: cd [path]",
            "grep": "grep — search for patterns\nUsage: grep pattern [file...]",
            "cat":  "cat — concatenate files\nUsage: cat [file...]",
            "find": "find — find files\nUsage: find [path] [-name pattern]",
            "rm":   "rm — remove files\nUsage: rm [-r] [-f] file...",
            "cp":   "cp — copy files\nUsage: cp source dest",
            "mv":   "mv — move/rename files\nUsage: mv source dest",
        }
        if cmd in manpages:
            self._writeln(f"MANUAL PAGE: {cmd}", "bold")
            self._writeln("─" * 40, "dim")
            self._writeln(manpages[cmd])
        else:
            self._writeln(f"man: no manual entry for {cmd}", "error")

    def _cmd_which(self, args: List[str]) -> None:
        for cmd in args:
            self._writeln(f"/usr/bin/{cmd}")

    def _cmd_type(self, args: List[str]) -> None:
        for cmd in args:
            if cmd in self._aliases:
                self._writeln(f"{cmd} is an alias for '{self._aliases[cmd]}'")
            else:
                self._writeln(f"{cmd} is /usr/bin/{cmd}")

    def _cmd_whoami(self, args: List[str]) -> None:
        self._writeln(self._env.get("USER", "user"))

    def _cmd_id(self, args: List[str]) -> None:
        user = self._env.get("USER", "user")
        self._writeln(f"uid=501({user}) gid=20(staff) groups=20(staff),12(everyone),61(localaccounts)")

    def _cmd_hostname(self, args: List[str]) -> None:
        self._writeln("MacPyOS.local")

    def _cmd_uname(self, args: List[str]) -> None:
        if "-a" in args:
            self._writeln(f"Darwin MacPyOS.local 23.0.0 Darwin Kernel Version 23.0.0 x86_64 MacPyOS")
        elif "-r" in args:
            self._writeln("23.0.0")
        elif "-m" in args:
            self._writeln("x86_64")
        elif "-s" in args:
            self._writeln("Darwin")
        else:
            self._writeln("Darwin")

    def _cmd_date(self, args: List[str]) -> None:
        if args and args[0].startswith("+"):
            fmt = args[0][1:].replace("%Y", str(datetime.datetime.now().year)) \
                             .replace("%m", f"{datetime.datetime.now().month:02d}") \
                             .replace("%d", f"{datetime.datetime.now().day:02d}") \
                             .replace("%H", f"{datetime.datetime.now().hour:02d}") \
                             .replace("%M", f"{datetime.datetime.now().minute:02d}") \
                             .replace("%S", f"{datetime.datetime.now().second:02d}")
            self._writeln(fmt)
        else:
            self._writeln(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y"))

    def _cmd_uptime(self, args: List[str]) -> None:
        import time as _time
        now = datetime.datetime.now()
        self._writeln(f"{now.strftime('%H:%M')}  up 2 days, 14:32,  1 user,  load average: 1.42, 1.58, 1.61")

    def _cmd_env(self, args: List[str]) -> None:
        for k, v in sorted(self._env.items()):
            self._writeln(f"{k}={v}")

    def _cmd_export(self, args: List[str]) -> None:
        for a in args:
            if "=" in a:
                k, v = a.split("=", 1)
                self._env[k] = self._expand(v)
            else:
                self._writeln(f"export: {a}: not a valid identifier", "error")

    def _cmd_unset(self, args: List[str]) -> None:
        for a in args:
            self._env.pop(a, None)

    def _cmd_printenv(self, args: List[str]) -> None:
        if args:
            for a in args:
                self._writeln(self._env.get(a, ""))
        else:
            self._cmd_env([])

    def _cmd_alias(self, args: List[str]) -> None:
        if not args:
            for k, v in sorted(self._aliases.items()):
                self._writeln(f"alias {k}='{v}'")
        else:
            for a in args:
                if "=" in a:
                    k, v = a.split("=", 1)
                    self._aliases[k.strip()] = v.strip("'\"")
                else:
                    if a in self._aliases:
                        self._writeln(f"alias {a}='{self._aliases[a]}'")

    def _cmd_unalias(self, args: List[str]) -> None:
        for a in args:
            self._aliases.pop(a, None)

    def _cmd_history(self, args: List[str]) -> None:
        n = int(args[0]) if args and args[0].isdigit() else len(self._history)
        for i, cmd in enumerate(self._history[-n:], 1):
            self._writeln(f"  {i:4}  {cmd}", "dim")

    def _cmd_find(self, args: List[str]) -> None:
        root    = self._cwd
        pattern = ""
        i = 0
        while i < len(args):
            if args[i] == "-name" and i + 1 < len(args):
                pattern = args[i + 1].replace("*", ".*").replace("?", ".")
                i += 2
            elif not args[i].startswith("-"):
                root = self._resolve(args[i]); i += 1
            else:
                i += 1
        results = self.wm.vfs.find(root, pattern or ".")
        for r in results:
            self._writeln(r)
        self._writeln(f"({len(results)} results)", "dim")

    def _cmd_grep(self, args: List[str]) -> None:
        if len(args) < 2:
            self._writeln("grep: usage: grep pattern file", "error"); return
        ignore_case = "-i" in args
        args        = [a for a in args if not a.startswith("-")]
        pattern, files = args[0], args[1:]
        flags = re.IGNORECASE if ignore_case else 0
        for f in files:
            path = self._resolve(f)
            try:
                for i, line in enumerate(self.wm.vfs.read(path).splitlines(), 1):
                    if re.search(pattern, line, flags):
                        self._writeln(f"{f}:{i}:{line}", "success")
            except Exception as ex:
                self._writeln(f"grep: {f}: {ex}", "error")

    def _cmd_sort(self, args: List[str]) -> None:
        files = [a for a in args if not a.startswith("-")]
        reverse = "-r" in args
        for f in files:
            path = self._resolve(f)
            try:
                lines = sorted(self.wm.vfs.read(path).splitlines(), reverse=reverse)
                for l in lines:
                    self._writeln(l)
            except Exception as ex:
                self._writeln(f"sort: {f}: {ex}", "error")

    def _cmd_uniq(self, args: List[str]) -> None:
        files = [a for a in args if not a.startswith("-")]
        for f in files:
            path = self._resolve(f)
            try:
                lines = self.wm.vfs.read(path).splitlines()
                prev  = None
                for l in lines:
                    if l != prev:
                        self._writeln(l)
                    prev = l
            except Exception as ex:
                self._writeln(f"uniq: {f}: {ex}", "error")

    def _cmd_tr(self, args: List[str]) -> None:
        if len(args) < 3:
            self._writeln("tr: usage: tr set1 set2 file", "error"); return
        s1, s2 = args[0], args[1]
        f      = args[2] if len(args) > 2 else None
        if f:
            path = self._resolve(f)
            try:
                content = self.wm.vfs.read(path)
                table   = str.maketrans(s1, s2[:len(s1)])
                self._write(content.translate(table))
            except Exception as ex:
                self._writeln(f"tr: {ex}", "error")

    def _cmd_sed(self, args: List[str]) -> None:
        if not args:
            self._writeln("sed: no expression", "error"); return
        expr = args[0]
        files = args[1:] if len(args) > 1 else []
        m = re.match(r"s/([^/]+)/([^/]*)/([gi]*)", expr)
        if not m:
            self._writeln("sed: only s/pattern/replace/flags supported", "error"); return
        pat, repl, flags_str = m.group(1), m.group(2), m.group(3)
        re_flags = re.IGNORECASE if "i" in flags_str else 0
        count = 0 if "g" in flags_str else 1
        for f in files:
            path = self._resolve(f)
            try:
                content = self.wm.vfs.read(path)
                out = re.sub(pat, repl, content, count=count, flags=re_flags)
                self._write(out)
            except Exception as ex:
                self._writeln(f"sed: {f}: {ex}", "error")

    def _cmd_awk(self, args: List[str]) -> None:
        self._writeln("awk: basic field printing supported", "dim")
        prog  = args[0] if args else ""
        files = args[1:] if len(args) > 1 else []
        for f in files:
            path = self._resolve(f)
            try:
                for line in self.wm.vfs.read(path).splitlines():
                    fields = line.split()
                    if "{print $" in prog:
                        import re as _re
                        idxs = _re.findall(r"\$(\d+)", prog)
                        out_parts = []
                        for idx in idxs:
                            i = int(idx) - 1
                            out_parts.append(fields[i] if i < len(fields) else "")
                        self._writeln(" ".join(out_parts))
                    else:
                        self._writeln(line)
            except Exception as ex:
                self._writeln(f"awk: {f}: {ex}", "error")

    def _cmd_cut(self, args: List[str]) -> None:
        delimiter = "\t"
        fields    = []
        files     = []
        i = 0
        while i < len(args):
            if args[i] == "-d" and i + 1 < len(args):
                delimiter = args[i + 1]; i += 2
            elif args[i] == "-f" and i + 1 < len(args):
                fields = [int(x) - 1 for x in args[i + 1].split(",")]; i += 2
            elif args[i].startswith("-d"):
                delimiter = args[i][2:]; i += 1
            elif args[i].startswith("-f"):
                fields = [int(x) - 1 for x in args[i][2:].split(",")]; i += 1
            else:
                files.append(args[i]); i += 1
        for f in files:
            path = self._resolve(f)
            try:
                for line in self.wm.vfs.read(path).splitlines():
                    parts = line.split(delimiter)
                    out   = delimiter.join(parts[j] for j in fields if j < len(parts))
                    self._writeln(out)
            except Exception as ex:
                self._writeln(f"cut: {f}: {ex}", "error")

    def _cmd_stat(self, args: List[str]) -> None:
        for a in [x for x in args if not x.startswith("-")]:
            path = self._resolve(a)
            try:
                st = self.wm.vfs.stat(path)
                self._writeln(f"  File: {path}")
                self._writeln(f"  Size: {st['size']} bytes")
                self._writeln(f"  Type: {'directory' if st['is_dir'] else 'regular file'}")
                self._writeln(f" Owner: {st['owner']}")
                self._writeln(f"  Mode: {st['permissions']}")
                self._writeln(f"Modify: {datetime.datetime.fromtimestamp(st['modified'])}")
            except Exception as ex:
                self._writeln(f"stat: {a}: {ex}", "error")

    def _cmd_file(self, args: List[str]) -> None:
        for a in args:
            path = self._resolve(a)
            if not self.wm.vfs.exists(path):
                self._writeln(f"{a}: cannot open (No such file or directory)", "error"); continue
            if self.wm.vfs.isdir(path):
                self._writeln(f"{a}: directory")
            else:
                ext = os.path.splitext(a)[1].lower()
                types = {".py":"Python script", ".txt":"ASCII text", ".sh":"Bourne-Again shell script",
                         ".json":"JSON data", ".csv":"CSV text", ".md":"Markdown text"}
                self._writeln(f"{a}: {types.get(ext, 'ASCII text')}")

    def _cmd_diff(self, args: List[str]) -> None:
        files = [a for a in args if not a.startswith("-")]
        if len(files) < 2:
            self._writeln("diff: missing operand", "error"); return
        try:
            a = self.wm.vfs.read(self._resolve(files[0])).splitlines()
            b = self.wm.vfs.read(self._resolve(files[1])).splitlines()
            import difflib
            for line in difflib.unified_diff(a, b, fromfile=files[0], tofile=files[1]):
                tag = "success" if line.startswith("+") else "error" if line.startswith("-") else "dim"
                self._writeln(line, tag)
        except Exception as ex:
            self._writeln(f"diff: {ex}", "error")

    def _cmd_du(self, args: List[str]) -> None:
        human = "-h" in args
        path  = next((a for a in args if not a.startswith("-")), self._cwd)
        path  = self._resolve(path)
        try:
            for name in self.wm.vfs.listdir(path):
                full = path.rstrip("/") + "/" + name
                sz   = self.wm.vfs._get_node(full).size() if self.wm.vfs.exists(full) else 0
                if human:
                    for unit in ("B", "K", "M", "G"):
                        if sz < 1024:
                            self._writeln(f"{sz:6.0f}{unit}  {full}"); break
                        sz /= 1024
                else:
                    self._writeln(f"{sz//1024:8}  {full}")
        except Exception as ex:
            self._writeln(f"du: {ex}", "error")

    def _cmd_df(self, args: List[str]) -> None:
        self._writeln("Filesystem      Size   Used  Avail  Capacity  Mounted on", "bold")
        self._writeln("/dev/disk1s5   500G   120G   380G      24%   /")
        self._writeln("devfs          192K   192K     0B     100%   /dev")
        self._writeln("tmpfs          1.0G    12M   1012M       1%   /tmp")

    def _cmd_ps(self, args: List[str]) -> None:
        self._writeln(f"{'PID':>6}  {'USER':<8}  {'CPU%':>5}  {'MEM':>6}  COMMAND", "bold")
        for p in self.wm.procs.list_all()[:20]:
            self._writeln(f"{p.pid:>6}  {p.user:<8}  {p.cpu:>4.1f}%  {p.ram:>5.0f}M  {p.name}")

    def _cmd_kill(self, args: List[str]) -> None:
        pids = [a for a in args if not a.startswith("-")]
        for pidstr in pids:
            try:
                pid = int(pidstr)
                if self.wm.procs.kill(pid):
                    self._writeln(f"Process {pid} terminated.", "success")
                else:
                    self._writeln(f"kill: ({pid}): No such process", "error")
            except ValueError:
                self._writeln(f"kill: illegal pid: {pidstr}", "error")

    def _cmd_top(self, args: List[str]) -> None:
        self._writeln("Processes: {} total (MacPyOS simulation)".format(
            len(self.wm.procs.list_all())), "info")
        self._writeln(f"CPU usage: {self.wm.procs.total_cpu():.1f}%  "
                      f"RAM: {self.wm.procs.total_ram():.0f}MB", "dim")
        self._writeln(f"{'PID':>6}  {'COMMAND':<20}  {'CPU%':>5}  {'MEM':>6}", "bold")
        procs = sorted(self.wm.procs.list_all(), key=lambda p: p.cpu, reverse=True)
        for p in procs[:15]:
            self._writeln(f"{p.pid:>6}  {p.name:<20}  {p.cpu:>4.1f}%  {p.ram:>5.0f}M")

    def _cmd_jobs(self, args: List[str]) -> None:
        self._writeln("[1]+  Running  (no background jobs)", "dim")

    def _cmd_sleep(self, args: List[str]) -> None:
        if args:
            try:
                n = float(args[0])
                self._writeln(f"(sleeping {n}s...)", "dim")
            except ValueError:
                self._writeln("sleep: invalid time interval", "error")

    def _cmd_time_cmd(self, args: List[str]) -> None:
        import time as _t
        start = _t.time()
        if args:
            self._run_cmd(args[0], args[1:])
        elapsed = _t.time() - start
        self._writeln(f"\nreal  {elapsed:.3f}s", "dim")

    def _cmd_python3(self, args: List[str]) -> None:
        if not args:
            self._writeln("Python 3.11.0 (MacPyOS) — interactive mode not supported.", "warn")
            self._writeln("Use 'python3 script.py' to run a file.", "dim")
            return
        path = self._resolve(args[0])
        try:
            code = self.wm.vfs.read(path)
        except FileNotFoundError:
            self._writeln(f"python3: can't open file '{args[0]}': No such file or directory", "error")
            return
        import io, contextlib
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                exec(compile(code, path, "exec"), {"__name__": "__main__"})
            out = buf.getvalue()
            if out:
                self._write(out)
        except SystemExit:
            pass
        except Exception as ex:
            self._writeln(f"Traceback: {ex}", "error")

    def _cmd_pip(self, args: List[str]) -> None:
        self._writeln("pip3: package management not available in MacPyOS VFS.", "warn")
        self._writeln("(This is a simulated terminal.)", "dim")

    def _cmd_open(self, args: List[str]) -> None:
        for a in [x for x in args if not x.startswith("-")]:
            path = self._resolve(a)
            if self.wm.vfs.exists(path):
                if self.wm.vfs.isdir(path):
                    self.wm.open_finder(path)
                else:
                    self.wm.open_textedit(path=path)
            elif a.startswith("http"):
                self.wm.open_safari(a)
            else:
                self._writeln(f"open: {a}: No such file or directory", "error")

    def _cmd_nano(self, args: List[str]) -> None:
        path = self._resolve(args[0]) if args else None
        self.wm.open_textedit(path=path)

    def _cmd_vi(self, args: List[str]) -> None:
        path = self._resolve(args[0]) if args else None
        self.wm.open_textedit(path=path)
        self._writeln("(Opening in TextEdit — vi mode not fully supported)", "dim")

    def _cmd_less(self, args: List[str]) -> None:
        files = [a for a in args if not a.startswith("-")]
        if not files:
            self._writeln("less: missing file operand", "error"); return
        for f in files:
            path = self._resolve(f)
            try:
                content = self.wm.vfs.read(path)
                lines   = content.splitlines()
                for ln in lines[:50]:
                    self._writeln(ln)
                if len(lines) > 50:
                    self._writeln(f"... ({len(lines) - 50} more lines — use 'cat' to view all)", "dim")
            except Exception as ex:
                self._writeln(f"less: {f}: {ex}", "error")

    def _cmd_curl(self, args: List[str]) -> None:
        url = next((a for a in args if a.startswith("http")), None)
        if not url:
            self._writeln("curl: no URL specified", "error"); return
        self._writeln(f"curl: {url}", "dim")
        self._writeln("(Network access is simulated in MacPyOS)", "warn")
        self._writeln('{"status": "simulated", "url": "' + url + '"}')

    def _cmd_wget(self, args: List[str]) -> None:
        url = next((a for a in args if a.startswith("http")), None)
        if not url:
            self._writeln("wget: no URL", "error"); return
        self._writeln(f"--{datetime.datetime.now().strftime('%H:%M:%S')}--  {url}", "dim")
        self._writeln("(Simulated download — no actual network access)", "warn")
        self._writeln("100% [=============================>] 0 K/s  done.")

    def _cmd_ping(self, args: List[str]) -> None:
        host = next((a for a in args if not a.startswith("-")), "localhost")
        self._writeln(f"PING {host}: 56 data bytes", "info")
        for i in range(4):
            ms = random.uniform(0.5, 5.0)
            self._writeln(f"64 bytes from {host}: icmp_seq={i} ttl=64 time={ms:.3f} ms")
        self._writeln(f"\n--- {host} ping statistics ---")
        self._writeln("4 packets transmitted, 4 received, 0.0% packet loss")

    def _cmd_ifconfig(self, args: List[str]) -> None:
        self._writeln("lo0: flags=8049<UP,LOOPBACK>", "info")
        self._writeln("    inet 127.0.0.1 netmask 0xff000000")
        self._writeln("en0: flags=8863<UP,BROADCAST,RUNNING>", "info")
        self._writeln("    ether aa:bb:cc:dd:ee:ff")
        self._writeln("    inet 192.168.1.42 netmask 0xffffff00 broadcast 192.168.1.255")

    def _cmd_ssh(self, args: List[str]) -> None:
        self._writeln("ssh: remote connections not available in MacPyOS.", "warn")

    def _cmd_scp(self, args: List[str]) -> None:
        self._writeln("scp: remote copy not available in MacPyOS.", "warn")

    def _cmd_zip(self, args: List[str]) -> None:
        files = [a for a in args if not a.startswith("-")]
        if len(files) < 2:
            self._writeln("zip: usage: zip archive.zip file...", "error"); return
        archive, sources = files[0], files[1:]
        apath = self._resolve(archive)
        content = f"ZIP archive: {archive}\nContents: {', '.join(sources)}\n"
        self.wm.vfs.write(apath, content)
        self._writeln(f"  adding: {', '.join(sources)}", "success")
        self._writeln(f"Created {archive}", "success")

    def _cmd_unzip(self, args: List[str]) -> None:
        files = [a for a in args if not a.startswith("-")]
        if not files:
            self._writeln("unzip: missing archive", "error"); return
        self._writeln(f"Archive:  {files[0]}", "info")
        self._writeln("(Simulated unzip — VFS zip support)", "dim")

    def _cmd_tar(self, args: List[str]) -> None:
        self._writeln("tar: archive operations simulated in MacPyOS.", "dim")

    def _cmd_gzip(self, args: List[str]) -> None:
        for a in [x for x in args if not x.startswith("-")]:
            path = self._resolve(a)
            if self.wm.vfs.isfile(path):
                self._writeln(f"{a}: compressed (simulated)", "success")
            else:
                self._writeln(f"gzip: {a}: No such file", "error")

    def _cmd_tree(self, args: List[str]) -> None:
        path = self._resolve(args[0]) if args else self._cwd
        self._writeln(path, "info")
        self._writeln(self.wm.vfs.tree(path, max_depth=3))

    def _cmd_chmod(self, args: List[str]) -> None:
        self._writeln("chmod: permission simulation (VFS only)", "dim")

    def _cmd_chown(self, args: List[str]) -> None:
        self._writeln("chown: ownership simulation (VFS only)", "dim")

    def _cmd_ln(self, args: List[str]) -> None:
        self._writeln("ln: symbolic links are simulated", "dim")

    def _cmd_readlink(self, args: List[str]) -> None:
        for a in [x for x in args if not x.startswith("-")]:
            self._writeln(self._resolve(a))

    def _cmd_basename(self, args: List[str]) -> None:
        if args:
            self._writeln(args[0].rstrip("/").split("/")[-1])

    def _cmd_dirname(self, args: List[str]) -> None:
        if args:
            self._writeln("/".join(args[0].rstrip("/").split("/")[:-1]) or "/")

    def _cmd_realpath(self, args: List[str]) -> None:
        for a in args:
            self._writeln(self._resolve(a))

    def _cmd_sw_vers(self, args: List[str]) -> None:
        self._writeln(f"ProductName:    macOS (MacPyOS simulation)")
        self._writeln(f"ProductVersion: {MACPYOS_VERSION}")
        self._writeln(f"BuildVersion:   {BUILD_DATE}A001")

    def _cmd_system_profiler(self, args: List[str]) -> None:
        self._writeln("MacPyOS System Profile", "bold")
        self._writeln("─" * 40, "dim")
        self._writeln("  Hardware Overview:")
        self._writeln("    CPU: MacPyOS Virtual CPU @ 3.0 GHz")
        self._writeln("    RAM: 16 GB simulated")
        self._writeln("    Disk: 500 GB VFS")
        self._writeln("  Software Overview:")
        self._writeln(f"    OS: MacPyOS {MACPYOS_VERSION} ({MACPYOS_CODENAME})")
        self._writeln("    Python: 3.11.x")

    def _cmd_defaults(self, args: List[str]) -> None:
        if not args:
            self._writeln("defaults: read/write/delete preference keys", "dim"); return
        if args[0] == "read":
            self._writeln(str(self.wm.settings.as_dict()), "dim")
        elif args[0] == "write" and len(args) >= 3:
            self.wm.settings.set(args[1], args[2])
            self._writeln(f"Set {args[1]} = {args[2]}", "success")
        else:
            self._writeln("defaults: usage: defaults read|write|delete key [value]", "dim")

    def _cmd_plutil(self, args: List[str]) -> None:
        self._writeln("plutil: property list utility (simulated)", "dim")

    def _cmd_caffeinate(self, args: List[str]) -> None:
        self._writeln("caffeinate: preventing display sleep... (simulated)", "info")

    def _cmd_say(self, args: List[str]) -> None:
        text = " ".join(args)
        self._writeln(f'say: "{text}" (text-to-speech simulated)', "info")

    def _cmd_screensaver(self, args: List[str]) -> None:
        self._writeln("ScreenSaverEngine: launching... (simulated)", "dim")

    def _cmd_exit(self, args: List[str]) -> None:
        self._writeln("[Process completed]", "dim")
        self.wm.root.after(500, self.close)

    def _cmd_sudo(self, args: List[str]) -> None:
        if not args:
            self._writeln("sudo: usage: sudo command [args]", "error"); return
        self._writeln("Password: (simulated authentication)", "warn")
        self._run_cmd(args[0], args[1:])

    def _cmd_xargs(self, args: List[str]) -> None:
        self._writeln("xargs: pipe-based execution (partial support)", "dim")

    def _cmd_yes(self, args: List[str]) -> None:
        text = args[0] if args else "y"
        for _ in range(5):
            self._writeln(text)
        self._writeln("...(truncated)", "dim")

    def _cmd_false(self, args: List[str]) -> None:
        pass   # Returns exit code 1 (simulated)

    def _cmd_true(self, args: List[str]) -> None:
        pass   # Returns exit code 0

    def _cmd_seq(self, args: List[str]) -> None:
        nums = [a for a in args if not a.startswith("-")]
        try:
            if len(nums) == 1:
                for i in range(1, int(nums[0]) + 1):
                    self._writeln(str(i))
            elif len(nums) == 2:
                for i in range(int(nums[0]), int(nums[1]) + 1):
                    self._writeln(str(i))
            elif len(nums) == 3:
                step = int(nums[1])
                for i in range(int(nums[0]), int(nums[2]) + step, step):
                    self._writeln(str(i))
        except ValueError:
            self._writeln("seq: invalid number", "error")

    def _cmd_expr(self, args: List[str]) -> None:
        expr = " ".join(args)
        try:
            result = eval(expr.replace("\\*", "*"))
            self._writeln(str(result))
        except Exception:
            self._writeln("expr: syntax error", "error")

    def _cmd_bc(self, args: List[str]) -> None:
        self._writeln("bc: basic calculator — type expressions (simulated)", "dim")
        self._writeln("Example: use 'expr' command instead.", "dim")

    # ── utilities ─────────────────────────────────────────────────────────────

    def _resolve(self, path: str) -> str:
        return self.wm.vfs.resolve(path) if path else self._cwd

    def _expand(self, s: str) -> str:
        """Expand ~ and $VAR in a string."""
        if s.startswith("~"):
            s = self.wm.vfs.HOME + s[1:]
        s = re.sub(r"\$(\w+)", lambda m: self._env.get(m.group(1), ""), s)
        return s

    @staticmethod
    def _tokenize(line: str) -> List[str]:
        """Simple shell tokenizer respecting quoted strings."""
        tokens: List[str] = []
        current = ""
        in_single = False
        in_double = False
        for ch in line:
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif ch == " " and not in_single and not in_double:
                if current:
                    tokens.append(current)
                    current = ""
            else:
                current += ch
        if current:
            tokens.append(current)
        return tokens


# =============================================================================
#  MacPyOS — PART 3
#  Safari, Music, Preview, Calculator
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 19 — SAFARI APP
# ─────────────────────────────────────────────────────────────────────────────

class SafariApp(BaseWin):
    """macOS Safari browser clone with tab support and built-in pages."""

    BUILTIN_PAGES: Dict[str, str] = {}   # populated by _register_pages()

    def __init__(self, wm: "WM", url: str = "macpyos://home") -> None:
        super().__init__(wm, title="Safari", w=980, h=640, icon="🌐")
        self._tabs:     List[Dict[str, Any]] = []
        self._active:   int                  = 0
        self._register_pages()
        self._build_ui()
        self._new_tab(url)

    # ── page definitions ──────────────────────────────────────────────────────

    def _register_pages(self) -> None:
        self.BUILTIN_PAGES = {
            "macpyos://home":    self._page_home,
            "macpyos://help":    self._page_help,
            "macpyos://about":   self._page_about,
            "macpyos://history": self._page_history,
            "macpyos://news":    self._page_news,
            "macpyos://settings":self._page_settings_page,
        }

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        c = self.client

        # Tab bar
        self._tabbar = tk.Frame(c, bg=T["panel_alt"],
                                highlightthickness=1,
                                highlightbackground=T["separator"])
        self._tabbar.pack(fill="x")

        # Address bar / toolbar
        nav = tk.Frame(c, bg=T["panel_bg"],
                       highlightthickness=1,
                       highlightbackground=T["separator"])
        nav.pack(fill="x")

        def nav_btn(text: str, cmd: Callable) -> tk.Label:
            b = tk.Label(nav, text=text, bg=T["panel_bg"], fg=T["text"],
                         font=(FONT_UI, 13), padx=8, pady=4, cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>", lambda _: cmd())
            b.bind("<Enter>", lambda _, lb=b: lb.configure(bg=T["panel_alt"]))
            b.bind("<Leave>", lambda _, lb=b: lb.configure(bg=T["panel_bg"]))
            return b

        nav_btn("◀", self._go_back)
        nav_btn("▶", self._go_forward)
        nav_btn("↺", self._reload)

        # URL bar
        self._url_var = tk.StringVar()
        url_entry = tk.Entry(
            nav, textvariable=self._url_var,
            bg=T["input_bg"], fg=T["text"],
            insertbackground=T["text"],
            font=(FONT_UI, 13), relief="flat",
            highlightthickness=1,
            highlightbackground=T["input_border"],
            highlightcolor=T["input_focus"],
        )
        url_entry.pack(side="left", fill="x", expand=True, padx=8, pady=4)
        url_entry.bind("<Return>", lambda _: self._navigate(self._url_var.get()))

        nav_btn("＋", lambda: self._new_tab("macpyos://home"))
        nav_btn("⬇", lambda: self._downloads_info())
        nav_btn("☆", lambda: self._add_bookmark())

        # Content area
        self._content_frame = tk.Frame(c, bg=T["win_bg"])
        self._content_frame.pack(fill="both", expand=True)

        # Status bar
        self._status = tk.Label(c, text="",
                                bg=T["status_bg"], fg=T["text_muted"],
                                font=(FONT_UI, 11), anchor="w", padx=10,
                                highlightthickness=1,
                                highlightbackground=T["status_border"])
        self._status.pack(fill="x")

    # ── tab management ────────────────────────────────────────────────────────

    def _new_tab(self, url: str = "macpyos://home") -> None:
        tab = {
            "url":     url,
            "title":   "New Tab",
            "history": [url],
            "hist_idx": 0,
        }
        self._tabs.append(tab)
        self._active = len(self._tabs) - 1
        self._refresh_tabbar()
        self._navigate(url)

    def _close_tab(self, idx: int) -> None:
        if len(self._tabs) <= 1:
            self.close()
            return
        self._tabs.pop(idx)
        self._active = max(0, min(self._active, len(self._tabs) - 1))
        self._refresh_tabbar()
        self._load_current()

    def _switch_tab(self, idx: int) -> None:
        self._active = idx
        self._refresh_tabbar()
        self._load_current()

    def _refresh_tabbar(self) -> None:
        for w in self._tabbar.winfo_children():
            w.destroy()
        for i, tab in enumerate(self._tabs):
            active = (i == self._active)
            bg = T["win_bg"] if active else T["panel_alt"]
            frame = tk.Frame(self._tabbar, bg=bg, cursor="hand2",
                             highlightthickness=1 if active else 0,
                             highlightbackground=T["separator"])
            frame.pack(side="left", padx=1, pady=2)

            title = tab.get("title", "New Tab")
            short = title[:18] + "…" if len(title) > 20 else title
            tk.Label(frame, text=f"🌐  {short}",
                     bg=bg, fg=T["text"],
                     font=(FONT_UI, 11), padx=8, pady=3).pack(side="left")

            close_btn = tk.Label(frame, text="✕",
                                 bg=bg, fg=T["text_muted"],
                                 font=(FONT_UI, 10), padx=4, cursor="hand2")
            close_btn.pack(side="left")
            close_btn.bind("<Button-1>", lambda _, idx=i: self._close_tab(idx))
            frame.bind("<Button-1>", lambda _, idx=i: self._switch_tab(idx))

        # New tab button
        tk.Label(self._tabbar, text="＋",
                 bg=T["panel_alt"], fg=T["text_muted"],
                 font=(FONT_UI, 13), padx=8, cursor="hand2").pack(side="left")

    # ── navigation ────────────────────────────────────────────────────────────

    def _navigate(self, url: str) -> None:
        url = url.strip()
        if not url:
            return
        if not url.startswith(("http", "macpyos://", "file://")):
            # Treat as search
            url = f"https://duckduckgo.com/?q={url.replace(' ', '+')}"

        tab = self._tabs[self._active]
        tab["url"] = url
        # Trim forward history
        tab["history"] = tab["history"][:tab["hist_idx"] + 1]
        tab["history"].append(url)
        tab["hist_idx"] = len(tab["history"]) - 1

        self._url_var.set(url)
        self._render_page(url)

    def _load_current(self) -> None:
        tab = self._tabs[self._active]
        self._url_var.set(tab["url"])
        self._render_page(tab["url"])

    def _go_back(self) -> None:
        tab = self._tabs[self._active]
        if tab["hist_idx"] > 0:
            tab["hist_idx"] -= 1
            tab["url"] = tab["history"][tab["hist_idx"]]
            self._url_var.set(tab["url"])
            self._render_page(tab["url"])

    def _go_forward(self) -> None:
        tab = self._tabs[self._active]
        if tab["hist_idx"] < len(tab["history"]) - 1:
            tab["hist_idx"] += 1
            tab["url"] = tab["history"][tab["hist_idx"]]
            self._url_var.set(tab["url"])
            self._render_page(tab["url"])

    def _reload(self) -> None:
        self._load_current()

    def _downloads_info(self) -> None:
        self.wm.notifs.send("Safari", "No downloads in progress.", icon="⬇️")

    def _add_bookmark(self) -> None:
        url = self._url_var.get()
        self.wm.notifs.send("Safari", f"Bookmarked: {url}", icon="☆")

    # ── page renderer ─────────────────────────────────────────────────────────

    def _render_page(self, url: str) -> None:
        for w in self._content_frame.winfo_children():
            w.destroy()

        self._status.configure(text=f"  Loading {url}…")
        tab = self._tabs[self._active]

        if url in self.BUILTIN_PAGES:
            self.BUILTIN_PAGES[url](self._content_frame)
            tab["title"] = self._get_title(url)
        elif url.startswith("macpyos://"):
            self._page_404(self._content_frame, url)
            tab["title"] = "Not Found"
        else:
            self._page_external(self._content_frame, url)
            tab["title"] = url[:40]

        self._refresh_tabbar()
        self.set_title(f"Safari — {tab['title']}")
        self._status.configure(text=f"  {url}")

    def _get_title(self, url: str) -> str:
        titles = {
            "macpyos://home":    "MacPyOS Start Page",
            "macpyos://help":    "MacPyOS Help",
            "macpyos://about":   "About MacPyOS",
            "macpyos://news":    "MacPyOS News",
            "macpyos://history": "History",
            "macpyos://settings":"Settings",
        }
        return titles.get(url, url)

    # ── built-in pages ────────────────────────────────────────────────────────

    def _page_home(self, parent: tk.Frame) -> None:
        bg = T["win_bg"]
        sf = MacScrolledFrame(parent, bg=bg)
        sf.pack(fill="both", expand=True)
        inner = sf.inner
        inner.configure(bg=bg)

        # Hero section
        hero = tk.Frame(inner, bg=T["accent"], pady=40)
        hero.pack(fill="x")
        tk.Label(hero, text="🌐", bg=T["accent"],
                 font=(FONT_EMOJI, 48)).pack()
        tk.Label(hero, text="Safari",
                 bg=T["accent"], fg="#ffffff",
                 font=(FONT_UI, 28, "bold")).pack()
        tk.Label(hero, text="MacPyOS Browser",
                 bg=T["accent"], fg="#ffffff",
                 font=(FONT_UI, 14)).pack()

        # Search bar
        search_frame = tk.Frame(inner, bg=bg, pady=20)
        search_frame.pack(fill="x", padx=100)
        search_var = tk.StringVar()
        se = tk.Entry(search_frame, textvariable=search_var,
                      bg=T["input_bg"], fg=T["text"],
                      font=(FONT_UI, 14), relief="flat",
                      highlightthickness=2,
                      highlightbackground=T["input_border"],
                      highlightcolor=T["input_focus"],
                      justify="center")
        se.pack(fill="x", ipady=8)
        se.insert(0, "Search or enter website name")
        se.bind("<FocusIn>",  lambda e: se.delete(0, "end") if se.get().startswith("Search") else None)
        se.bind("<Return>",   lambda _: self._navigate(search_var.get()))

        # Favourites
        tk.Label(inner, text="Favourites",
                 bg=bg, fg=T["text"],
                 font=(FONT_UI, 16, "bold"), pady=8).pack(anchor="w", padx=20)
        fav_frame = tk.Frame(inner, bg=bg)
        fav_frame.pack(fill="x", padx=20, pady=4)
        favs = [
            ("🔵", "MacPyOS", "macpyos://home"),
            ("❓", "Help",    "macpyos://help"),
            ("📰", "News",    "macpyos://news"),
            ("ℹ️", "About",  "macpyos://about"),
        ]
        for emoji, label, url in favs:
            col = tk.Frame(fav_frame, bg=T["panel_bg"],
                           width=100, height=80, cursor="hand2")
            col.pack(side="left", padx=8, pady=4)
            col.pack_propagate(False)
            tk.Label(col, text=emoji, bg=T["panel_bg"],
                     font=(FONT_EMOJI, 24)).place(relx=0.5, y=28, anchor="center")
            tk.Label(col, text=label, bg=T["panel_bg"], fg=T["text"],
                     font=(FONT_UI, 11)).place(relx=0.5, y=58, anchor="center")
            for w in col.winfo_children() + [col]:
                w.bind("<Button-1>", lambda _, u=url: self._navigate(u))

        # Recently visited
        tk.Label(inner, text="Recently Visited",
                 bg=bg, fg=T["text"],
                 font=(FONT_UI, 16, "bold"), pady=8).pack(anchor="w", padx=20)
        for tab in self._tabs:
            for h_url in tab.get("history", [])[-5:]:
                row = tk.Frame(inner, bg=bg, cursor="hand2")
                row.pack(fill="x", padx=24, pady=1)
                tk.Label(row, text="🌐", bg=bg,
                         font=(FONT_EMOJI, 12), padx=4).pack(side="left")
                lbl = tk.Label(row, text=h_url, bg=bg,
                               fg=T["link"], font=(FONT_UI, 12),
                               anchor="w", cursor="hand2")
                lbl.pack(side="left")
                lbl.bind("<Button-1>", lambda _, u=h_url: self._navigate(u))

    def _page_help(self, parent: tk.Frame) -> None:
        sf = MacScrolledFrame(parent, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner

        tk.Label(inner, text="MacPyOS Help",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 22, "bold"), pady=16).pack(anchor="w", padx=24)

        sections = [
            ("🖥️ Desktop", [
                "Double-click icons to open apps",
                "Right-click desktop for context menu",
                "Cmd+Space opens Spotlight search",
            ]),
            ("🪟 Windows", [
                "● Red button — close window",
                "● Yellow button — minimise to Dock",
                "● Green button — full screen / maximise",
                "Drag title bar to move windows",
                "Drag bottom-right corner to resize",
            ]),
            ("⌨️ Keyboard Shortcuts", [
                "⌘Space  Spotlight Search",
                "⌘T      New Terminal",
                "⌘N      New Finder Window",
                "⌘E      Open TextEdit",
                "⌘L      Lock Screen",
                "⌘Q      Quit MacPyOS",
                "F5      Refresh Desktop",
            ]),
            ("📱 Applications", [
                "Finder — file manager with icon/list/column views",
                "TextEdit — text editor with syntax highlighting",
                "Terminal — full zsh-style terminal (65+ commands)",
                "Safari — tabbed web browser with built-in pages",
                "Music — audio player with visualiser",
                "Calculator — standard, scientific, programmer modes",
                "Notes — persistent note-taking app",
                "System Preferences — theme, wallpaper, fonts, and more",
            ]),
        ]

        for title, items in sections:
            tk.Label(inner, text=title,
                     bg=T["win_bg"], fg=T["accent"],
                     font=(FONT_UI, 15, "bold"),
                     pady=6, padx=24).pack(anchor="w")
            for item in items:
                tk.Label(inner, text=f"  • {item}",
                         bg=T["win_bg"], fg=T["text"],
                         font=(FONT_UI, 13),
                         padx=32, anchor="w").pack(fill="x")
            tk.Frame(inner, bg=T["separator"], height=1).pack(fill="x", padx=24, pady=6)

    def _page_about(self, parent: tk.Frame) -> None:
        bg = T["win_bg"]
        tk.Label(parent, text="",
                 bg=bg, font=(FONT_EMOJI, 64)).pack(pady=(40, 8))
        tk.Label(parent, text=f"MacPyOS {MACPYOS_VERSION}",
                 bg=bg, fg=T["text"],
                 font=(FONT_UI, 28, "bold")).pack()
        tk.Label(parent, text=f'"{MACPYOS_CODENAME}"',
                 bg=bg, fg=T["text_muted"],
                 font=(FONT_UI, 16, "italic")).pack()
        tk.Frame(parent, bg=T["separator"], height=1).pack(fill="x", padx=60, pady=20)
        info = [
            ("Platform",     "macOS-style Desktop Simulation"),
            ("Engine",       "Python + Tkinter"),
            ("Build",        BUILD_DATE),
            ("License",      "MIT"),
            ("Dependencies", "None (stdlib only)"),
        ]
        for label, value in info:
            row = tk.Frame(parent, bg=bg)
            row.pack(pady=2)
            tk.Label(row, text=f"{label}:",
                     bg=bg, fg=T["text_muted"],
                     font=(FONT_UI, 13), width=14, anchor="e").pack(side="left")
            tk.Label(row, text=value,
                     bg=bg, fg=T["text"],
                     font=(FONT_UI, 13), anchor="w").pack(side="left", padx=8)

    def _page_history(self, parent: tk.Frame) -> None:
        sf = MacScrolledFrame(parent, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner
        tk.Label(inner, text="History",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 20, "bold"), pady=12, padx=20).pack(anchor="w")
        for tab in self._tabs:
            for h_url in reversed(tab.get("history", [])):
                row = tk.Frame(inner, bg=T["win_bg"], cursor="hand2")
                row.pack(fill="x", padx=20, pady=1)
                tk.Label(row, text="🕒", bg=T["win_bg"],
                         font=(FONT_EMOJI, 12), padx=6).pack(side="left")
                lbl = tk.Label(row, text=h_url,
                               bg=T["win_bg"], fg=T["link"],
                               font=(FONT_UI, 12), anchor="w")
                lbl.pack(side="left")
                lbl.bind("<Button-1>", lambda _, u=h_url: self._navigate(u))

    def _page_news(self, parent: tk.Frame) -> None:
        sf = MacScrolledFrame(parent, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner
        tk.Label(inner, text="MacPyOS News",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 22, "bold"), pady=12, padx=20).pack(anchor="w")
        articles = [
            ("🎉 MacPyOS 1.0 Released",
             "The first version of MacPyOS, the macOS-style Python desktop simulation, is now available."),
            ("🖥️ New Finder Gets Column View",
             "The revamped Finder now supports icon, list, and column views just like the real macOS Finder."),
            ("💻 Terminal Now Has 65+ Commands",
             "The built-in Terminal supports a wide range of shell commands with full VFS integration."),
            ("🎵 Music App Adds Visualiser",
             "The Music app now includes a real-time audio visualiser built with pure Tkinter canvas."),
            ("⚙️ System Preferences Expanded",
             "System Preferences now includes 10 panels covering appearance, dock, notifications, and more."),
        ]
        for title, body in articles:
            card = tk.Frame(inner, bg=T["panel_bg"],
                            highlightthickness=1,
                            highlightbackground=T["separator"])
            card.pack(fill="x", padx=20, pady=6)
            tk.Label(card, text=title,
                     bg=T["panel_bg"], fg=T["text"],
                     font=(FONT_UI, 14, "bold"),
                     anchor="w", padx=12, pady=6).pack(fill="x")
            tk.Label(card, text=body,
                     bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 12), anchor="w",
                     wraplength=700, justify="left",
                     padx=12, pady=(0, 8)).pack(fill="x")

    def _page_settings_page(self, parent: tk.Frame) -> None:
        tk.Label(parent, text="Opening System Preferences…",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 14)).pack(pady=40)
        self.wm.root.after(200, self.wm.open_preferences)

    def _page_404(self, parent: tk.Frame, url: str) -> None:
        tk.Label(parent, text="🔍",
                 bg=T["win_bg"], font=(FONT_EMOJI, 48)).pack(pady=(60, 8))
        tk.Label(parent, text="Safari Can't Find the Page",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold")).pack()
        tk.Label(parent, text=f'The address "{url}" was not found.',
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 13)).pack(pady=4)

    def _page_external(self, parent: tk.Frame, url: str) -> None:
        tk.Label(parent, text="🌐",
                 bg=T["win_bg"], font=(FONT_EMOJI, 48)).pack(pady=(60, 8))
        tk.Label(parent, text="External Website",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold")).pack()
        tk.Label(parent, text=url,
                 bg=T["win_bg"], fg=T["link"],
                 font=(FONT_UI, 13)).pack(pady=4)
        tk.Label(parent,
                 text="MacPyOS runs in a virtual environment.\nActual network access is not available.",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 12), justify="center").pack(pady=8)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 20 — MUSIC APP
# ─────────────────────────────────────────────────────────────────────────────

class MusicApp(BaseWin):
    """macOS Music app clone with library, player controls, and visualiser."""

    SAMPLE_TRACKS = [
        {"title": "Cyber Dreams",      "artist": "PyOS Audio",    "album": "Digital Soundscapes", "duration": 213, "genre": "Electronic"},
        {"title": "Digital Rain",      "artist": "Tkinter Band",  "album": "Code Vibes",          "duration": 187, "genre": "Ambient"},
        {"title": "Electric Pulse",    "artist": "ByteWave",      "album": "Waveform",            "duration": 234, "genre": "Synthwave"},
        {"title": "Neon Nights",       "artist": "PyOS Audio",    "album": "Digital Soundscapes", "duration": 198, "genre": "Electronic"},
        {"title": "Algorithm Blues",   "artist": "Debug Mode",    "album": "Stack Overflow",      "duration": 241, "genre": "Blues"},
        {"title": "Binary Sunset",     "artist": "ByteWave",      "album": "Waveform",            "duration": 179, "genre": "Ambient"},
        {"title": "Recursion",         "artist": "Tkinter Band",  "album": "Code Vibes",          "duration": 256, "genre": "Jazz"},
        {"title": "Memory Leak",       "artist": "Debug Mode",    "album": "Stack Overflow",      "duration": 203, "genre": "Rock"},
        {"title": "Lambda Function",   "artist": "PyOS Audio",    "album": "Pure Python",         "duration": 167, "genre": "Classical"},
        {"title": "Dark Mode",         "artist": "ByteWave",      "album": "Themes",              "duration": 221, "genre": "Synthwave"},
        {"title": "Compile Time",      "artist": "Debug Mode",    "album": "Stack Overflow",      "duration": 195, "genre": "Jazz"},
        {"title": "Git Commit",        "artist": "Tkinter Band",  "album": "Version Control",     "duration": 183, "genre": "Rock"},
    ]

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, title="Music", w=900, h=580, icon="🎵")
        self._tracks      = list(self.SAMPLE_TRACKS)
        self._queue:      List[int] = list(range(len(self._tracks)))
        self._cur_idx:    int       = 0
        self._playing:    bool      = False
        self._progress:   float     = 0.0    # 0.0–1.0
        self._volume:     float     = 0.8
        self._shuffle:    bool      = False
        self._repeat:     str       = "none"  # "none" | "one" | "all"
        self._viz_data:   List[float] = [0.0] * 32
        self._view:       str       = "songs"  # "songs" | "albums" | "artists"
        self._ticker_id:  Optional[str] = None

        self._build_ui()
        self._refresh_library()
        self._start_ticker()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        c = self.client

        # Main split: sidebar | content
        main = tk.Frame(c, bg=T["win_bg"])
        main.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(main, bg=T["sidebar_bg"], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="Library",
                 bg=T["sidebar_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 10, "bold"),
                 padx=12, pady=8).pack(anchor="w")

        for label, view in [("🎵 Songs", "songs"), ("💿 Albums", "albums"), ("🎤 Artists", "artists")]:
            row = tk.Frame(sidebar, bg=T["sidebar_bg"], cursor="hand2")
            row.pack(fill="x")
            lbl = tk.Label(row, text=label, bg=T["sidebar_bg"],
                           fg=T["text"], font=(FONT_UI, 13), padx=12, pady=5)
            lbl.pack(side="left", fill="x", expand=True)
            for w in (row, lbl):
                w.bind("<Button-1>",  lambda _, v=view: self._set_view(v))
                w.bind("<Enter>",     lambda _, r=row: r.configure(bg=T["menu_hover"]))
                w.bind("<Leave>",     lambda _, r=row: r.configure(bg=T["sidebar_bg"]))

        tk.Frame(sidebar, bg=T["separator"], height=1).pack(fill="x", pady=4, padx=8)
        tk.Label(sidebar, text="Playlists",
                 bg=T["sidebar_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 10, "bold"), padx=12, pady=4).pack(anchor="w")

        for pl in ["Recently Added", "My Playlist", "Favourites"]:
            row = tk.Frame(sidebar, bg=T["sidebar_bg"], cursor="hand2")
            row.pack(fill="x")
            tk.Label(row, text=f"♫  {pl}",
                     bg=T["sidebar_bg"], fg=T["text"],
                     font=(FONT_UI, 12), padx=12, pady=4).pack(side="left")
            row.bind("<Enter>", lambda _, r=row: r.configure(bg=T["menu_hover"]))
            row.bind("<Leave>", lambda _, r=row: r.configure(bg=T["sidebar_bg"]))

        # Vertical separator
        tk.Frame(main, bg=T["separator"], width=1).pack(side="left", fill="y")

        # Right pane
        right = tk.Frame(main, bg=T["win_bg"])
        right.pack(side="left", fill="both", expand=True)

        # Now-playing bar (top of content)
        self._now_playing_bar = tk.Frame(right, bg=T["panel_bg"],
                                         highlightthickness=1,
                                         highlightbackground=T["separator"])
        self._now_playing_bar.pack(fill="x")
        self._build_now_playing(self._now_playing_bar)

        # Visualiser canvas
        self._viz_canvas = tk.Canvas(right, bg="#1a1a2e",
                                     height=80, highlightthickness=0)
        self._viz_canvas.pack(fill="x")

        # Library content
        self._lib_frame = tk.Frame(right, bg=T["win_bg"])
        self._lib_frame.pack(fill="both", expand=True)

        # Transport controls (bottom)
        self._transport = tk.Frame(right, bg=T["panel_bg"],
                                   highlightthickness=1,
                                   highlightbackground=T["separator"])
        self._transport.pack(fill="x")
        self._build_transport(self._transport)

    def _build_now_playing(self, parent: tk.Frame) -> None:
        self._track_emoji = tk.Label(parent, text="🎵",
                                     bg=T["panel_bg"],
                                     font=(FONT_EMOJI, 32), padx=12, pady=8)
        self._track_emoji.pack(side="left")

        info = tk.Frame(parent, bg=T["panel_bg"])
        info.pack(side="left", fill="x", expand=True, pady=8)
        self._title_lbl = tk.Label(info, text="Not Playing",
                                   bg=T["panel_bg"], fg=T["text"],
                                   font=(FONT_UI, 14, "bold"), anchor="w")
        self._title_lbl.pack(fill="x")
        self._artist_lbl = tk.Label(info, text="—",
                                    bg=T["panel_bg"], fg=T["text_muted"],
                                    font=(FONT_UI, 12), anchor="w")
        self._artist_lbl.pack(fill="x")

        # Progress bar
        prog_frame = tk.Frame(info, bg=T["panel_bg"])
        prog_frame.pack(fill="x", pady=4)
        self._time_lbl = tk.Label(prog_frame, text="0:00",
                                  bg=T["panel_bg"], fg=T["text_muted"],
                                  font=(FONT_UI, 10), width=5)
        self._time_lbl.pack(side="left")
        self._prog_bar = tk.Canvas(prog_frame, bg=T["progress_bg"],
                                   height=4, highlightthickness=0)
        self._prog_bar.pack(side="left", fill="x", expand=True)
        self._prog_bar.bind("<Button-1>", self._seek)
        self._dur_lbl = tk.Label(prog_frame, text="0:00",
                                 bg=T["panel_bg"], fg=T["text_muted"],
                                 font=(FONT_UI, 10), width=5)
        self._dur_lbl.pack(side="left")

    def _build_transport(self, parent: tk.Frame) -> None:
        frame = tk.Frame(parent, bg=T["panel_bg"])
        frame.pack(pady=8)

        def ctrl_btn(text: str, cmd: Callable, font_size: int = 16) -> tk.Label:
            b = tk.Label(frame, text=text, bg=T["panel_bg"],
                         fg=T["text"], font=(FONT_EMOJI, font_size),
                         padx=8, cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>", lambda _: cmd())
            return b

        ctrl_btn("⇄",  self._toggle_shuffle, 13)
        ctrl_btn("⏮",  self._prev_track)
        self._play_btn = ctrl_btn("▶",  self._toggle_play, 20)
        ctrl_btn("⏭",  self._next_track)
        ctrl_btn("↺",  self._cycle_repeat, 13)

        # Volume slider
        tk.Label(frame, text="🔈", bg=T["panel_bg"],
                 font=(FONT_EMOJI, 13), padx=8).pack(side="left")
        self._vol_canvas = tk.Canvas(frame, bg=T["progress_bg"],
                                     width=80, height=4, highlightthickness=0)
        self._vol_canvas.pack(side="left")
        self._vol_canvas.bind("<Button-1>", self._set_volume)
        self._draw_volume()
        tk.Label(frame, text="🔊", bg=T["panel_bg"],
                 font=(FONT_EMOJI, 13), padx=4).pack(side="left")

    # ── library views ─────────────────────────────────────────────────────────

    def _set_view(self, view: str) -> None:
        self._view = view
        self._refresh_library()

    def _refresh_library(self) -> None:
        for w in self._lib_frame.winfo_children():
            w.destroy()

        if self._view == "songs":
            self._render_songs()
        elif self._view == "albums":
            self._render_albums()
        elif self._view == "artists":
            self._render_artists()

    def _render_songs(self) -> None:
        sf = MacScrolledFrame(self._lib_frame, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner

        # Header row
        hdr = tk.Frame(inner, bg=T["panel_alt"])
        hdr.pack(fill="x")
        for label, width in [("#", 3), ("Title", 22), ("Artist", 16), ("Album", 18), ("Time", 6)]:
            tk.Label(hdr, text=label, bg=T["panel_alt"], fg=T["text_muted"],
                     font=(FONT_UI, 11, "bold"), width=width, anchor="w",
                     padx=4, pady=4).pack(side="left")
        tk.Frame(inner, bg=T["separator"], height=1).pack(fill="x")

        for idx, track in enumerate(self._tracks):
            active = (idx == self._cur_idx)
            bg = T["selection"] if active else (T["win_bg"] if idx % 2 == 0 else T["panel_bg"])
            row = tk.Frame(inner, bg=bg, cursor="hand2")
            row.pack(fill="x")

            num_text = "♫" if active and self._playing else str(idx + 1)
            tk.Label(row, text=num_text, bg=bg,
                     fg=T["accent"] if active else T["text_muted"],
                     font=(FONT_UI, 11), width=3, padx=4, pady=5).pack(side="left")
            tk.Label(row, text=track["title"], bg=bg,
                     fg=T["accent"] if active else T["text"],
                     font=(FONT_UI, 12, "bold" if active else "normal"),
                     width=22, anchor="w", padx=4).pack(side="left")
            tk.Label(row, text=track["artist"], bg=bg,
                     fg=T["text_muted"], font=(FONT_UI, 12),
                     width=16, anchor="w", padx=4).pack(side="left")
            tk.Label(row, text=track["album"], bg=bg,
                     fg=T["text_muted"], font=(FONT_UI, 12),
                     width=18, anchor="w", padx=4).pack(side="left")
            dur = track["duration"]
            tk.Label(row, text=f"{dur//60}:{dur%60:02d}", bg=bg,
                     fg=T["text_muted"], font=(FONT_UI, 12),
                     width=6, anchor="w", padx=4).pack(side="left")

            for w in row.winfo_children() + [row]:
                w.bind("<Double-Button-1>", lambda _, i=idx: self._play_track(i))
                w.bind("<Button-1>",        lambda _, i=idx: self._select_track(i))
                w.bind("<Enter>",           lambda _, r=row, b=bg: r.configure(bg=T["panel_alt"]))
                w.bind("<Leave>",           lambda _, r=row, b=bg: r.configure(bg=b))

    def _render_albums(self) -> None:
        sf = MacScrolledFrame(self._lib_frame, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner
        inner.configure(bg=T["win_bg"])

        albums: Dict[str, List[Dict]] = {}
        for t in self._tracks:
            albums.setdefault(t["album"], []).append(t)

        grid = tk.Frame(inner, bg=T["win_bg"])
        grid.pack(fill="both", padx=16, pady=16)

        for col_idx, (album, tracks) in enumerate(albums.items()):
            artist = tracks[0]["artist"]
            col = tk.Frame(grid, bg=T["panel_bg"],
                           width=140, height=170, cursor="hand2")
            col.grid(row=col_idx // 4, column=col_idx % 4, padx=8, pady=8)
            col.grid_propagate(False)
            # Album art placeholder
            art = tk.Canvas(col, bg=T["accent"], width=120, height=100,
                            highlightthickness=0)
            art.place(x=10, y=10)
            art.create_text(60, 50, text="💿", font=(FONT_EMOJI, 28))
            tk.Label(col, text=album[:18],
                     bg=T["panel_bg"], fg=T["text"],
                     font=(FONT_UI, 11, "bold"), wraplength=130).place(x=8, y=118)
            tk.Label(col, text=artist[:18],
                     bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 10)).place(x=8, y=138)

    def _render_artists(self) -> None:
        sf = MacScrolledFrame(self._lib_frame, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner

        artists: Dict[str, int] = {}
        for t in self._tracks:
            artists[t["artist"]] = artists.get(t["artist"], 0) + 1

        for artist, count in sorted(artists.items()):
            row = tk.Frame(inner, bg=T["win_bg"], cursor="hand2")
            row.pack(fill="x", padx=16, pady=2)
            tk.Label(row, text="🎤", bg=T["win_bg"],
                     font=(FONT_EMOJI, 20), padx=8).pack(side="left")
            tk.Label(row, text=artist, bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 13),
                     anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(row, text=f"{count} songs",
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 11)).pack(side="right", padx=8)
            row.bind("<Enter>", lambda _, r=row: r.configure(bg=T["panel_alt"]))
            row.bind("<Leave>", lambda _, r=row: r.configure(bg=T["win_bg"]))

    # ── playback ──────────────────────────────────────────────────────────────

    def _select_track(self, idx: int) -> None:
        self._cur_idx = idx
        self._refresh_library()

    def _play_track(self, idx: int) -> None:
        self._cur_idx = idx
        self._playing = True
        self._progress = 0.0
        self._update_now_playing()
        self._refresh_library()

    def _toggle_play(self) -> None:
        self._playing = not self._playing
        self._play_btn.configure(text="⏸" if self._playing else "▶")
        self._update_now_playing()

    def _prev_track(self) -> None:
        if self._progress > 0.05:
            self._progress = 0.0
        else:
            self._cur_idx = (self._cur_idx - 1) % len(self._tracks)
        self._playing = True
        self._update_now_playing()
        self._refresh_library()

    def _next_track(self) -> None:
        if self._shuffle:
            self._cur_idx = random.randint(0, len(self._tracks) - 1)
        else:
            self._cur_idx = (self._cur_idx + 1) % len(self._tracks)
        self._playing = True
        self._progress = 0.0
        self._update_now_playing()
        self._refresh_library()

    def _toggle_shuffle(self) -> None:
        self._shuffle = not self._shuffle
        self.wm.notifs.send("Music",
                            f"Shuffle {'on' if self._shuffle else 'off'}",
                            icon="⇄")

    def _cycle_repeat(self) -> None:
        modes = ["none", "all", "one"]
        self._repeat = modes[(modes.index(self._repeat) + 1) % len(modes)]
        self.wm.notifs.send("Music", f"Repeat: {self._repeat}", icon="↺")

    def _seek(self, e: tk.Event) -> None:
        w = self._prog_bar.winfo_width()
        if w > 0:
            self._progress = max(0.0, min(1.0, e.x / w))
            self._update_now_playing()

    def _set_volume(self, e: tk.Event) -> None:
        w = self._vol_canvas.winfo_width()
        if w > 0:
            self._volume = max(0.0, min(1.0, e.x / w))
            self._draw_volume()

    def _draw_volume(self) -> None:
        self._vol_canvas.delete("all")
        w = self._vol_canvas.winfo_width() or 80
        fill_w = int(w * self._volume)
        self._vol_canvas.create_rectangle(0, 0, w, 4,
                                          fill=T["progress_bg"], outline="")
        self._vol_canvas.create_rectangle(0, 0, fill_w, 4,
                                          fill=T["accent"], outline="")

    def _update_now_playing(self) -> None:
        if not self._tracks:
            return
        track = self._tracks[self._cur_idx]
        self._title_lbl.configure(text=track["title"])
        self._artist_lbl.configure(text=f"{track['artist']} — {track['album']}")
        self._play_btn.configure(text="⏸" if self._playing else "▶")

        dur  = track["duration"]
        cur  = int(self._progress * dur)
        self._time_lbl.configure(text=f"{cur//60}:{cur%60:02d}")
        self._dur_lbl.configure(text=f"{dur//60}:{dur%60:02d}")

        # Progress bar
        self._prog_bar.delete("all")
        w = self._prog_bar.winfo_width() or 300
        self._prog_bar.create_rectangle(0, 0, w, 4,
                                        fill=T["progress_bg"], outline="")
        self._prog_bar.create_rectangle(0, 0, int(w * self._progress), 4,
                                        fill=T["accent"], outline="")

    # ── visualiser ────────────────────────────────────────────────────────────

    def _start_ticker(self) -> None:
        self._tick()

    def _tick(self) -> None:
        if self._closed:
            return
        if self._playing:
            track = self._tracks[self._cur_idx]
            dur   = track["duration"]
            step  = 1 / (dur * 4)   # progress per 250ms tick
            self._progress = min(1.0, self._progress + step)
            if self._progress >= 1.0:
                if self._repeat == "one":
                    self._progress = 0.0
                elif self._repeat == "all" or True:
                    self._next_track()
            self._update_now_playing()
            self._animate_viz()
        self._ticker_id = self.root.after(250, self._tick)

    def _animate_viz(self) -> None:
        for i in range(len(self._viz_data)):
            self._viz_data[i] = max(0.0, min(1.0,
                self._viz_data[i] * 0.85 + random.uniform(-0.15, 0.25)))

        self._viz_canvas.delete("all")
        w = self._viz_canvas.winfo_width() or 600
        h = 80
        n = len(self._viz_data)
        bar_w = w / n
        for i, val in enumerate(self._viz_data):
            x0 = int(i * bar_w) + 1
            x1 = int((i + 1) * bar_w) - 1
            bh = int(val * (h - 8)) + 2
            # Colour gradient from accent to accent2
            ratio = i / n
            r1, g1, b1 = int(T["accent"][1:3], 16), int(T["accent"][3:5], 16), int(T["accent"][5:7], 16)
            r2, g2, b2 = int(T["accent2"][1:3], 16), int(T["accent2"][3:5], 16), int(T["accent2"][5:7], 16)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            col = f"#{r:02x}{g:02x}{b:02x}"
            self._viz_canvas.create_rectangle(x0, h - bh, x1, h,
                                              fill=col, outline="")

    def _on_close(self) -> None:
        if self._ticker_id:
            self.root.after_cancel(self._ticker_id)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 21 — PREVIEW APP
# ─────────────────────────────────────────────────────────────────────────────

class PreviewApp(BaseWin):
    """macOS Preview clone — image viewer / PDF viewer / document inspector."""

    def __init__(self, wm: "WM", path: Optional[str] = None) -> None:
        super().__init__(wm, title="Preview", w=700, h=520, icon="🖼️")
        self._path   = path
        self._zoom   = 1.0
        self._page   = 0
        self._pages: List[str] = []   # list of content strings for multi-page
        self._build_ui()
        if path:
            self._load(path)
        else:
            self._show_welcome()

    def _build_ui(self) -> None:
        c = self.client

        # Toolbar
        tb = tk.Frame(c, bg=T["panel_bg"],
                      highlightthickness=1,
                      highlightbackground=T["separator"])
        tb.pack(fill="x")

        def btn(text: str, cmd: Callable, tip: str = "") -> tk.Label:
            b = tk.Label(tb, text=text, bg=T["panel_bg"],
                         fg=T["text"], font=(FONT_UI, 12),
                         padx=8, pady=4, cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>", lambda _: cmd())
            b.bind("<Enter>", lambda _, lb=b: lb.configure(bg=T["panel_alt"]))
            b.bind("<Leave>", lambda _, lb=b: lb.configure(bg=T["panel_bg"]))
            if tip:
                make_tooltip(b, tip)
            return b

        btn("📂 Open",  self._open_dialog, "Open File")
        tk.Frame(tb, bg=T["separator"], width=1, height=20).pack(side="left", padx=4, pady=4)
        btn("🔍+", self._zoom_in,  "Zoom In")
        btn("🔍-", self._zoom_out, "Zoom Out")
        btn("⊡",  self._zoom_fit, "Fit to Window")
        btn("100%",self._zoom_reset,"Actual Size")
        tk.Frame(tb, bg=T["separator"], width=1, height=20).pack(side="left", padx=4, pady=4)
        btn("◀",  self._prev_page, "Previous Page")
        self._page_lbl = tk.Label(tb, text="",
                                  bg=T["panel_bg"], fg=T["text_muted"],
                                  font=(FONT_UI, 11), padx=8)
        self._page_lbl.pack(side="left")
        btn("▶",  self._next_page, "Next Page")
        tk.Frame(tb, bg=T["separator"], width=1, height=20).pack(side="left", padx=4, pady=4)
        btn("↺",  self._rotate,    "Rotate")
        btn("⬇",  self._export,    "Export")

        # Main area
        main = tk.Frame(c, bg=T["win_bg"])
        main.pack(fill="both", expand=True)

        # Thumbnail sidebar
        self._thumb_sidebar = tk.Frame(main, bg=T["panel_bg"], width=80)
        self._thumb_sidebar.pack(side="left", fill="y")
        self._thumb_sidebar.pack_propagate(False)

        tk.Frame(main, bg=T["separator"], width=1).pack(side="left", fill="y")

        # Canvas area
        self._canvas_frame = tk.Frame(main, bg=T["panel_alt"])
        self._canvas_frame.pack(side="left", fill="both", expand=True)

        self._canvas = tk.Canvas(self._canvas_frame,
                                 bg=T["panel_alt"],
                                 highlightthickness=0)
        vscroll = tk.Scrollbar(self._canvas_frame, orient="vertical",
                               command=self._canvas.yview, width=8)
        hscroll = tk.Scrollbar(self._canvas_frame, orient="horizontal",
                               command=self._canvas.xview, width=8)
        self._canvas.configure(yscrollcommand=vscroll.set,
                               xscrollcommand=hscroll.set)
        vscroll.pack(side="right", fill="y")
        hscroll.pack(side="bottom", fill="x")
        self._canvas.pack(fill="both", expand=True)

        self._canvas.bind("<MouseWheel>",
                          lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # Inspector panel (right)
        self._inspector = tk.Frame(main, bg=T["panel_bg"], width=180)
        self._inspector.pack(side="right", fill="y")
        self._inspector.pack_propagate(False)
        tk.Label(self._inspector, text="Inspector",
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 12, "bold"), pady=8).pack()
        tk.Frame(self._inspector, bg=T["separator"], height=1).pack(fill="x")

        # Status bar
        self._status = tk.Label(c, text="",
                                bg=T["status_bg"], fg=T["text_muted"],
                                font=(FONT_UI, 11), anchor="w", padx=10,
                                highlightthickness=1,
                                highlightbackground=T["status_border"])
        self._status.pack(fill="x")

    # ── file loading ──────────────────────────────────────────────────────────

    def _open_dialog(self) -> None:
        path = simpledialog.askstring("Open File", "Enter path:",
                                      initialvalue=self.wm.vfs.HOME + "/",
                                      parent=self.wm.root)
        if path:
            self._load(path)

    def _load(self, path: str) -> None:
        self._path = path
        name = path.split("/")[-1]
        ext  = os.path.splitext(name)[1].lower()
        self.set_title(f"Preview — {name}")

        if not self.wm.vfs.exists(path):
            self._show_message("File not found", "The file could not be opened.", "⚠️")
            return

        if ext in (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"):
            self._show_image_placeholder(path, name)
        elif ext == ".pdf":
            self._show_pdf_placeholder(path, name)
        elif ext in (".txt", ".md", ".py", ".sh", ".json", ".csv"):
            self._show_text_file(path, name)
        else:
            self._show_text_file(path, name)

        self._update_inspector(path)

    def _show_welcome(self) -> None:
        self._canvas.delete("all")
        cw = self._canvas.winfo_width() or 580
        ch = self._canvas.winfo_height() or 400
        self._canvas.create_text(cw // 2, ch // 2 - 40,
                                 text="🖼️", font=(FONT_EMOJI, 64),
                                 fill=T["text_muted"])
        self._canvas.create_text(cw // 2, ch // 2 + 20,
                                 text="Preview",
                                 font=(FONT_UI, 20, "bold"),
                                 fill=T["text"])
        self._canvas.create_text(cw // 2, ch // 2 + 50,
                                 text="Open a file to preview it",
                                 font=(FONT_UI, 13),
                                 fill=T["text_muted"])

    def _show_image_placeholder(self, path: str, name: str) -> None:
        self._canvas.delete("all")
        self._canvas.update_idletasks()
        cw = max(100, self._canvas.winfo_width())
        ch = max(100, self._canvas.winfo_height())

        # Draw simulated image (gradient pattern)
        w, h = int(300 * self._zoom), int(240 * self._zoom)
        x0 = (cw - w) // 2
        y0 = (ch - h) // 2

        # Checkerboard background (transparent simulation)
        cell = 20
        for ci in range(w // cell + 1):
            for ri in range(h // cell + 1):
                x = x0 + ci * cell
                y = y0 + ri * cell
                col = "#cccccc" if (ci + ri) % 2 == 0 else "#ffffff"
                self._canvas.create_rectangle(x, y, x + cell, y + cell,
                                              fill=col, outline="")

        # Image frame
        self._canvas.create_rectangle(x0, y0, x0 + w, y0 + h,
                                      fill="", outline=T["separator"], width=1)

        # Image icon
        self._canvas.create_text(x0 + w // 2, y0 + h // 2,
                                 text="🖼️", font=(FONT_EMOJI, int(48 * self._zoom)))
        self._canvas.create_text(x0 + w // 2, y0 + h // 2 + 40,
                                 text=name, font=(FONT_UI, 11),
                                 fill=T["text_muted"])

        self._canvas.configure(scrollregion=(0, 0, cw, ch))
        self._status.configure(text=f"  {name}  |  300×240 (simulated)  |  {int(self._zoom*100)}%")

    def _show_pdf_placeholder(self, path: str, name: str) -> None:
        try:
            content = self.wm.vfs.read(path)
            lines   = content.splitlines()
            self._pages = ["\n".join(lines[i:i + 40]) for i in range(0, len(lines), 40)]
        except Exception:
            self._pages = ["[Could not read file]"]
        self._page = 0
        self._render_text_page()
        self._build_thumbs()
        self._page_lbl.configure(text=f"Page {self._page+1} of {len(self._pages)}")
        self._status.configure(text=f"  PDF: {name}  |  {len(self._pages)} pages")

    def _show_text_file(self, path: str, name: str) -> None:
        try:
            content = self.wm.vfs.read(path)
        except Exception as ex:
            content = str(ex)
        lines   = content.splitlines()
        self._pages = ["\n".join(lines[i:i + 50]) for i in range(0, max(1, len(lines)), 50)]
        self._page  = 0
        self._render_text_page()
        self._page_lbl.configure(text=f"Page {self._page+1} of {len(self._pages)}")
        self._status.configure(text=f"  {name}  |  {len(lines)} lines  |  {int(self._zoom*100)}%")

    def _render_text_page(self) -> None:
        self._canvas.delete("all")
        self._canvas.update_idletasks()
        cw = max(100, self._canvas.winfo_width())

        page_w = int(500 * self._zoom)
        page_h = int(650 * self._zoom)
        x0     = max(0, (cw - page_w) // 2)
        y0     = 20

        # Page shadow
        self._canvas.create_rectangle(x0 + 4, y0 + 4, x0 + page_w + 4, y0 + page_h + 4,
                                      fill="#000000", outline="")
        # Page background
        self._canvas.create_rectangle(x0, y0, x0 + page_w, y0 + page_h,
                                      fill="#ffffff", outline=T["separator"])

        # Text content
        if self._pages:
            content = self._pages[self._page]
            font_size = max(8, int(13 * self._zoom))
            self._canvas.create_text(
                x0 + 24, y0 + 24,
                text=content,
                font=(FONT_MONO, font_size),
                fill="#000000",
                anchor="nw",
                width=page_w - 48,
            )

        self._canvas.configure(scrollregion=(0, 0, cw, page_h + 60))

    def _build_thumbs(self) -> None:
        for w in self._thumb_sidebar.winfo_children():
            w.destroy()
        for i in range(len(self._pages)):
            bg = T["accent"] if i == self._page else T["panel_bg"]
            thumb = tk.Frame(self._thumb_sidebar, bg=bg,
                             width=64, height=80, cursor="hand2")
            thumb.pack(pady=4)
            thumb.pack_propagate(False)
            tk.Label(thumb, text=f"📄\n{i+1}",
                     bg=bg, fg=T["text"] if i != self._page else "#ffffff",
                     font=(FONT_UI, 10)).place(relx=0.5, rely=0.5, anchor="center")
            thumb.bind("<Button-1>", lambda _, idx=i: self._jump_page(idx))

    def _jump_page(self, idx: int) -> None:
        self._page = idx
        self._render_text_page()
        self._build_thumbs()
        self._page_lbl.configure(text=f"Page {self._page+1} of {len(self._pages)}")

    def _prev_page(self) -> None:
        if self._page > 0:
            self._jump_page(self._page - 1)

    def _next_page(self) -> None:
        if self._page < len(self._pages) - 1:
            self._jump_page(self._page + 1)

    def _zoom_in(self) -> None:
        self._zoom = min(4.0, self._zoom * 1.25)
        self._re_render()

    def _zoom_out(self) -> None:
        self._zoom = max(0.1, self._zoom / 1.25)
        self._re_render()

    def _zoom_fit(self) -> None:
        self._zoom = 1.0
        self._re_render()

    def _zoom_reset(self) -> None:
        self._zoom = 1.0
        self._re_render()

    def _rotate(self) -> None:
        self.wm.notifs.send("Preview", "Rotation simulated.", icon="↺")

    def _export(self) -> None:
        self.wm.notifs.send("Preview", "Export not available in simulation.", icon="⬇️")

    def _re_render(self) -> None:
        if self._path:
            ext = os.path.splitext(self._path)[1].lower()
            if ext in (".jpg", ".png", ".gif"):
                self._show_image_placeholder(self._path, self._path.split("/")[-1])
            else:
                self._render_text_page()
        self._status.configure(text=f"  {int(self._zoom*100)}%")

    def _show_message(self, title: str, body: str, icon: str = "ℹ️") -> None:
        self._canvas.delete("all")
        cw = self._canvas.winfo_width() or 580
        ch = self._canvas.winfo_height() or 400
        self._canvas.create_text(cw // 2, ch // 2 - 30,
                                 text=icon, font=(FONT_EMOJI, 40))
        self._canvas.create_text(cw // 2, ch // 2 + 10,
                                 text=title, font=(FONT_UI, 16, "bold"),
                                 fill=T["text"])
        self._canvas.create_text(cw // 2, ch // 2 + 35,
                                 text=body, font=(FONT_UI, 12),
                                 fill=T["text_muted"])

    def _update_inspector(self, path: str) -> None:
        for w in self._inspector.winfo_children()[2:]:
            w.destroy()
        try:
            stat = self.wm.vfs.stat(path)
            items = [
                ("Name",  stat["name"]),
                ("Size",  FinderApp._fmt_size(stat["size"])),
                ("Kind",  FinderApp._get_kind(stat["name"])),
                ("Modified", datetime.datetime.fromtimestamp(stat["modified"]).strftime("%b %d, %Y")),
                ("Owner", stat["owner"]),
            ]
            for label, val in items:
                tk.Label(self._inspector, text=label,
                         bg=T["panel_bg"], fg=T["text_muted"],
                         font=(FONT_UI, 10), padx=8, anchor="w").pack(fill="x")
                tk.Label(self._inspector, text=val,
                         bg=T["panel_bg"], fg=T["text"],
                         font=(FONT_UI, 11), padx=8, anchor="w",
                         wraplength=160).pack(fill="x")
                tk.Frame(self._inspector, bg=T["separator"], height=1).pack(fill="x")
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 22 — CALCULATOR APP
# ─────────────────────────────────────────────────────────────────────────────

class CalculatorApp(BaseWin):
    """macOS Calculator clone — Standard, Scientific, Programmer, Currency modes."""

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, title="Calculator", w=340, h=520,
                         icon="🧮", resizable=False)
        self._mode        = "standard"   # standard | scientific | programmer | currency
        self._display_var = tk.StringVar(value="0")
        self._expr:       List[str]  = []
        self._current:    str        = "0"
        self._has_dot:    bool       = False
        self._just_op:    bool       = False
        self._memory:     float      = 0.0
        self._history:    List[str]  = []
        self._build_ui()

    def _build_ui(self) -> None:
        c = self.client
        c.configure(bg="#1c1c1e")

        # Mode selector
        mode_bar = tk.Frame(c, bg="#2c2c2e")
        mode_bar.pack(fill="x")
        modes = [("Standard", "standard"), ("Scientific", "scientific"),
                 ("Programmer", "programmer")]
        for label, mode in modes:
            b = tk.Label(mode_bar, text=label,
                         bg="#2c2c2e" if mode != self._mode else T["accent"],
                         fg="#ffffff", font=(FONT_UI, 11),
                         padx=8, pady=4, cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>", lambda _, m=mode: self._set_mode(m))

        # Display
        disp_frame = tk.Frame(c, bg="#1c1c1e")
        disp_frame.pack(fill="x", padx=0)

        # Expression label
        self._expr_lbl = tk.Label(disp_frame, text="",
                                  bg="#1c1c1e", fg="#888888",
                                  font=(FONT_UI, 13),
                                  anchor="e", padx=16)
        self._expr_lbl.pack(fill="x")

        self._disp = tk.Label(disp_frame,
                              textvariable=self._display_var,
                              bg="#1c1c1e", fg="#ffffff",
                              font=(FONT_UI, 42, "bold"),
                              anchor="e", padx=16, pady=8)
        self._disp.pack(fill="x")

        # History button
        self._hist_btn = tk.Label(disp_frame, text="History ▾",
                                  bg="#1c1c1e", fg="#888888",
                                  font=(FONT_UI, 10), cursor="hand2", padx=16)
        self._hist_btn.pack(anchor="e")
        self._hist_btn.bind("<Button-1>", lambda _: self._show_history())

        # Button grid
        self._btn_frame = tk.Frame(c, bg="#1c1c1e")
        self._btn_frame.pack(fill="both", expand=True)
        self._build_buttons()

    def _set_mode(self, mode: str) -> None:
        self._mode = mode
        self.set_title(f"Calculator — {mode.capitalize()}")
        for w in self._btn_frame.winfo_children():
            w.destroy()
        # Rebuild mode bar colours
        for w in self.client.winfo_children():
            if isinstance(w, tk.Frame) and w.winfo_height() < 40:
                for b in w.winfo_children():
                    if isinstance(b, tk.Label):
                        mode_name = b.cget("text").lower()
                        b.configure(bg=T["accent"] if mode_name == mode else "#2c2c2e")
        self._build_buttons()

    def _build_buttons(self) -> None:
        f = self._btn_frame

        if self._mode == "scientific":
            layout = self._sci_layout()
        elif self._mode == "programmer":
            layout = self._prog_layout()
        else:
            layout = self._std_layout()

        for row_idx, row in enumerate(layout):
            row_frame = tk.Frame(f, bg="#1c1c1e")
            row_frame.pack(fill="x", expand=True)
            for col_idx, (label, cmd, style) in enumerate(row):
                color_map = {
                    "op":       "#ff9f0a",
                    "func":     "#555555",
                    "digit":    "#333333",
                    "special":  "#3a3a3c",
                    "equals":   "#ff9f0a",
                    "memory":   "#444444",
                }
                bg  = color_map.get(style, "#333333")
                fg  = "#1c1c1e" if style == "equals" else "#ffffff"
                btn = tk.Frame(row_frame, bg=bg, cursor="hand2",
                               highlightthickness=1,
                               highlightbackground="#1c1c1e")
                btn.pack(side="left", fill="both", expand=True, padx=1, pady=1)
                lbl = tk.Label(btn, text=label, bg=bg, fg=fg,
                               font=(FONT_UI, 16), pady=10)
                lbl.pack(expand=True)
                lbl.bind("<Button-1>", lambda _, c=cmd: self._button(c))
                btn.bind("<Button-1>",  lambda _, c=cmd: self._button(c))
                btn.bind("<Enter>", lambda _, b=btn, orig=bg:
                         b.configure(bg=self._lighten(orig)))
                btn.bind("<Leave>", lambda _, b=btn, orig=bg:
                         b.configure(bg=orig))

    def _std_layout(self) -> List:
        return [
            [("AC","ac","special"), ("±","sign","special"), ("%","percent","special"), ("÷","÷","op")],
            [("7","7","digit"), ("8","8","digit"), ("9","9","digit"), ("×","×","op")],
            [("4","4","digit"), ("5","5","digit"), ("6","6","digit"), ("−","−","op")],
            [("1","1","digit"), ("2","2","digit"), ("3","3","digit"), ("+","+","op")],
            [("0","0","digit"), (".","dot","digit"), ("=","=","equals")],
        ]

    def _sci_layout(self) -> List:
        return [
            [("(",  "(", "func"), (")",  ")", "func"), ("mc","mc","memory"), ("m+","m+","memory"), ("m-","m-","memory"), ("mr","mr","memory")],
            [("2ⁿᵈ","2nd","func"), ("x²","sq","func"), ("x³","cube","func"), ("xʸ","pow","func"), ("eˣ","exp_e","func"), ("10ˣ","exp_10","func")],
            [("1/x","inv","func"), ("√x","sqrt","func"), ("∛x","cbrt","func"), ("y√x","yroot","func"), ("ln","ln","func"), ("log₁₀","log10","func")],
            [("x!","fact","func"), ("sin","sin","func"), ("cos","cos","func"), ("tan","tan","func"), ("e","const_e","func"), ("EE","ee","func")],
            [("AC","ac","special"), ("±","sign","special"), ("%","percent","special"), ("÷","÷","op")],
            [("7","7","digit"), ("8","8","digit"), ("9","9","digit"), ("×","×","op")],
            [("4","4","digit"), ("5","5","digit"), ("6","6","digit"), ("−","−","op")],
            [("1","1","digit"), ("2","2","digit"), ("3","3","digit"), ("+","+","op")],
            [("0","0","digit"), (".","dot","digit"), ("=","=","equals")],
        ]

    def _prog_layout(self) -> List:
        return [
            [("AND","AND","func"),("OR","OR","func"),("XOR","XOR","func"),("NOT","NOT","func")],
            [("<<","SHL","func"),(">>","SHR","func"),("0x","hex_prefix","func"),("0b","bin_prefix","func")],
            [("A","A","func"),("B","B","func"),("C","C","func"),("D","D","func")],
            [("E","E","func"),("F","F","func"),("AC","ac","special"),("÷","÷","op")],
            [("7","7","digit"),("8","8","digit"),("9","9","digit"),("×","×","op")],
            [("4","4","digit"),("5","5","digit"),("6","6","digit"),("−","−","op")],
            [("1","1","digit"),("2","2","digit"),("3","3","digit"),("+","+","op")],
            [("0","0","digit"),(".","dot","digit"),("=","=","equals")],
        ]

    # ── button logic ──────────────────────────────────────────────────────────

    def _button(self, cmd: str) -> None:
        cur = self._current

        if cmd == "ac":
            self._current = "0"
            self._expr    = []
            self._has_dot = False
        elif cmd == "sign":
            if cur != "0":
                if cur.startswith("-"):
                    self._current = cur[1:]
                else:
                    self._current = "-" + cur
        elif cmd == "percent":
            try:
                self._current = str(float(cur) / 100)
            except Exception:
                pass
        elif cmd == "dot":
            if not self._has_dot:
                self._current += "."
                self._has_dot  = True
        elif cmd in ("0","1","2","3","4","5","6","7","8","9",
                     "A","B","C","D","E","F"):
            if self._just_op or self._current == "0":
                self._current = cmd
                self._has_dot = False
            else:
                self._current += cmd
            self._just_op = False
        elif cmd in ("+", "−", "×", "÷"):
            self._expr.append(self._current)
            self._expr.append(cmd)
            self._just_op = True
            self._has_dot = False
        elif cmd == "=":
            self._expr.append(self._current)
            result = self._evaluate()
            expr_str = " ".join(self._expr) + " ="
            self._history.append(f"{expr_str}  {result}")
            self._expr    = []
            self._current = result
            self._has_dot = "." in result
            self._just_op = False
        # Scientific functions
        elif cmd in ("sq", "cube", "inv", "sqrt", "cbrt", "ln", "log10",
                     "sin", "cos", "tan", "fact", "exp_e", "exp_10"):
            try:
                x = float(cur)
                fns = {
                    "sq":      lambda v: v ** 2,
                    "cube":    lambda v: v ** 3,
                    "inv":     lambda v: 1 / v,
                    "sqrt":    lambda v: math.sqrt(v),
                    "cbrt":    lambda v: v ** (1/3),
                    "ln":      lambda v: math.log(v),
                    "log10":   lambda v: math.log10(v),
                    "sin":     lambda v: math.sin(math.radians(v)),
                    "cos":     lambda v: math.cos(math.radians(v)),
                    "tan":     lambda v: math.tan(math.radians(v)),
                    "fact":    lambda v: math.factorial(int(v)),
                    "exp_e":   lambda v: math.e ** v,
                    "exp_10":  lambda v: 10 ** v,
                }
                r = fns[cmd](x)
                self._current = self._fmt_num(r)
            except Exception as ex:
                self._current = "Error"
        elif cmd == "const_e":
            self._current = str(math.e)
        elif cmd == "pow":
            self._expr.append(self._current)
            self._expr.append("^")
            self._just_op = True
        elif cmd in ("mc", "m+", "m-", "mr"):
            try:
                if cmd == "mc":   self._memory = 0.0
                elif cmd == "m+": self._memory += float(self._current)
                elif cmd == "m-": self._memory -= float(self._current)
                elif cmd == "mr": self._current = self._fmt_num(self._memory)
            except Exception:
                pass
        elif cmd in ("AND", "OR", "XOR", "NOT", "SHL", "SHR"):
            try:
                a = int(float(self._current))
                self._expr.append(str(a))
                self._expr.append(cmd)
                self._just_op = True
            except Exception:
                pass
        elif cmd == "2nd":
            pass  # Toggle secondary functions (simplified)
        elif cmd == "hex_prefix":
            try:
                self._current = hex(int(float(self._current)))
            except Exception:
                pass
        elif cmd == "bin_prefix":
            try:
                self._current = bin(int(float(self._current)))
            except Exception:
                pass

        # Update display
        display = self._current
        try:
            # Format large numbers with commas
            if "." not in display and "0x" not in display and "0b" not in display:
                n = float(display)
                if abs(n) < 1e15 and n == int(n):
                    display = f"{int(n):,}"
        except Exception:
            pass

        self._display_var.set(display)
        self._expr_lbl.configure(text=" ".join(self._expr))

    def _evaluate(self) -> str:
        tokens = list(self._expr)
        try:
            # Handle programmer bitwise ops
            if any(t in ("AND","OR","XOR","NOT","SHL","SHR") for t in tokens):
                a = int(float(tokens[0]))
                op = tokens[1]
                b = int(float(tokens[2])) if len(tokens) > 2 else 0
                ops = {
                    "AND": a & b, "OR": a | b, "XOR": a ^ b,
                    "NOT": ~a, "SHL": a << b, "SHR": a >> b,
                }
                return str(ops.get(op, "Error"))

            # Build a Python expression
            expr_str = ""
            for tok in tokens:
                if tok == "÷":   expr_str += "/"
                elif tok == "×": expr_str += "*"
                elif tok == "−": expr_str += "-"
                elif tok == "^": expr_str += "**"
                else:            expr_str += tok
            result = eval(expr_str)
            return self._fmt_num(result)
        except ZeroDivisionError:
            return "Division by Zero"
        except Exception:
            return "Error"

    @staticmethod
    def _fmt_num(n: float) -> str:
        if isinstance(n, int) or (isinstance(n, float) and n == int(n)):
            return str(int(n))
        s = f"{n:.10f}".rstrip("0").rstrip(".")
        return s

    @staticmethod
    def _lighten(hex_color: str) -> str:
        try:
            r = min(255, int(hex_color[1:3], 16) + 30)
            g = min(255, int(hex_color[3:5], 16) + 30)
            b = min(255, int(hex_color[5:7], 16) + 30)
            return f"#{r:02x}{g:02x}{b:02x}"
        except Exception:
            return hex_color

    def _show_history(self) -> None:
        if not self._history:
            self.wm.notifs.send("Calculator", "No history yet.", icon="🧮")
            return
        dlg = tk.Toplevel(self.wm.root)
        dlg.title("Calculator History")
        dlg.geometry("320x400")
        dlg.configure(bg="#1c1c1e")
        dlg.transient(self.wm.root)
        tk.Label(dlg, text="History",
                 bg="#1c1c1e", fg="#ffffff",
                 font=(FONT_UI, 16, "bold"), pady=12).pack()
        sf = MacScrolledFrame(dlg, bg="#1c1c1e")
        sf.pack(fill="both", expand=True)
        inner = sf.inner
        inner.configure(bg="#1c1c1e")
        for entry in reversed(self._history[-50:]):
            tk.Label(inner, text=entry,
                     bg="#2c2c2e", fg="#ffffff",
                     font=(FONT_MONO, 12), anchor="e",
                     padx=12, pady=4).pack(fill="x", pady=1)
        tk.Button(dlg, text="Clear History",
                  bg=T["danger"], fg="#ffffff",
                  font=(FONT_UI, 12), relief="flat",
                  command=lambda: (self._history.clear(), dlg.destroy())).pack(pady=8)


# =============================================================================
#  MacPyOS — PART 4
#  Clock, Activity Monitor, Notes, Mail
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 24 — CLOCK APP
# ─────────────────────────────────────────────────────────────────────────────

class ClockApp(BaseWin):
    """macOS Clock — World Clock, Alarm, Stopwatch, Timer tabs."""

    WORLD_CITIES = [
        ("🇺🇸", "New York",       "America/New_York",    -5),
        ("🇺🇸", "Los Angeles",    "America/Los_Angeles", -8),
        ("🇬🇧", "London",         "Europe/London",        0),
        ("🇫🇷", "Paris",          "Europe/Paris",         1),
        ("🇩🇪", "Berlin",         "Europe/Berlin",        1),
        ("🇷🇺", "Moscow",         "Europe/Moscow",        3),
        ("🇦🇪", "Dubai",          "Asia/Dubai",           4),
        ("🇮🇳", "Mumbai",         "Asia/Kolkata",        5),
        ("🇨🇳", "Shanghai",       "Asia/Shanghai",        8),
        ("🇯🇵", "Tokyo",          "Asia/Tokyo",           9),
        ("🇦🇺", "Sydney",         "Australia/Sydney",    10),
        ("🇧🇷", "São Paulo",      "America/Sao_Paulo",   -3),
    ]

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "Clock", w=520, h=460, icon="⏰")
        self._tab      = "world"
        self._running  = False
        self._sw_start : Optional[float] = None
        self._sw_accum : float = 0.0
        self._sw_laps  : List[str] = []
        self._timer_sec: int = 0
        self._timer_rem: int = 0
        self._timer_running = False
        self._alarms   : List[Dict] = []
        self._build_ui()
        self._tick()

    def _build_ui(self) -> None:
        # Tab bar
        tab_bar = tk.Frame(self.client, bg=T["panel_bg"])
        tab_bar.pack(fill="x")
        self._tab_btns: Dict[str, tk.Label] = {}
        for key, label in [("world","World Clock"),("alarm","Alarm"),
                            ("stopwatch","Stopwatch"),("timer","Timer")]:
            btn = tk.Label(tab_bar, text=label,
                           bg=T["panel_bg"], fg=T["text_muted"],
                           font=(FONT_UI, 12), padx=14, pady=8, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda _, k=key: self._switch_tab(k))
            self._tab_btns[key] = btn

        self._content = tk.Frame(self.client, bg=T["win_bg"])
        self._content.pack(fill="both", expand=True)
        self._switch_tab("world")

    def _switch_tab(self, tab: str) -> None:
        self._tab = tab
        for k, btn in self._tab_btns.items():
            if k == tab:
                btn.configure(fg=T["accent"],
                              font=(FONT_UI, 12, "bold"))
            else:
                btn.configure(fg=T["text_muted"],
                              font=(FONT_UI, 12))
        for w in self._content.winfo_children():
            w.destroy()
        {"world":     self._build_world,
         "alarm":     self._build_alarm,
         "stopwatch": self._build_stopwatch,
         "timer":     self._build_timer}[tab]()

    # ── World Clock ───────────────────────────────────────────────────────────

    def _build_world(self) -> None:
        sf = MacScrolledFrame(self._content, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        self._world_labels: Dict[str, tk.Label] = {}
        for flag, city, tz, offset in self.WORLD_CITIES:
            row = tk.Frame(sf.inner, bg=T["win_bg"])
            row.pack(fill="x", padx=20, pady=4)
            tk.Label(row, text=flag, bg=T["win_bg"],
                     font=(FONT_EMOJI, 22), width=3).pack(side="left")
            info = tk.Frame(row, bg=T["win_bg"])
            info.pack(side="left", fill="x", expand=True, padx=8)
            tk.Label(info, text=city, bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 14, "bold"),
                     anchor="w").pack(anchor="w")
            tk.Label(info, text=tz, bg=T["win_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 11),
                     anchor="w").pack(anchor="w")
            time_lbl = tk.Label(row, text="--:--",
                                bg=T["win_bg"], fg=T["text"],
                                font=(FONT_UI, 20))
            time_lbl.pack(side="right")
            self._world_labels[city] = (time_lbl, offset)
            tk.Frame(sf.inner, bg=T["separator"], height=1).pack(fill="x",
                                                                   padx=20)

    def _update_world(self) -> None:
        if self._tab != "world":
            return
        if not hasattr(self, "_world_labels"):
            return
        now_utc = datetime.datetime.utcnow()
        for city, (lbl, offset) in self._world_labels.items():
            city_time = now_utc + datetime.timedelta(hours=offset)
            lbl.configure(text=city_time.strftime("%I:%M %p"))

    # ── Alarm ─────────────────────────────────────────────────────────────────

    def _build_alarm(self) -> None:
        top = tk.Frame(self._content, bg=T["win_bg"])
        top.pack(fill="x", padx=20, pady=12)
        tk.Label(top, text="Alarms", bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 16, "bold")).pack(side="left")
        tk.Label(top, text="＋ Add", bg=T["win_bg"], fg=T["accent"],
                 font=(FONT_UI, 13), cursor="hand2").pack(side="right")

        self._alarm_frame = tk.Frame(self._content, bg=T["win_bg"])
        self._alarm_frame.pack(fill="both", expand=True)
        self._refresh_alarms()

        add_frame = tk.Frame(self._content, bg=T["panel_bg"])
        add_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(add_frame, text="Hour:", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 12)).pack(side="left")
        self._alarm_h = tk.Spinbox(add_frame, from_=0, to=23, width=3,
                                    bg=T["input_bg"], fg=T["text"],
                                    font=(FONT_UI, 13), relief="flat")
        self._alarm_h.pack(side="left", padx=4)
        tk.Label(add_frame, text="Min:", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 12)).pack(side="left")
        self._alarm_m = tk.Spinbox(add_frame, from_=0, to=59, width=3,
                                    bg=T["input_bg"], fg=T["text"],
                                    font=(FONT_UI, 13), relief="flat")
        self._alarm_m.pack(side="left", padx=4)
        tk.Label(add_frame, text="Label:", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 12)).pack(side="left", padx=(8,0))
        self._alarm_lbl_var = tk.StringVar(value="Alarm")
        tk.Entry(add_frame, textvariable=self._alarm_lbl_var,
                 bg=T["input_bg"], fg=T["text"],
                 font=(FONT_UI, 12), relief="flat", width=10).pack(side="left", padx=4)
        tk.Button(add_frame, text="Add Alarm",
                  bg=T["accent"], fg="#ffffff",
                  font=(FONT_UI, 12), relief="flat",
                  command=self._add_alarm).pack(side="left", padx=8)

    def _refresh_alarms(self) -> None:
        for w in self._alarm_frame.winfo_children():
            w.destroy()
        if not self._alarms:
            tk.Label(self._alarm_frame, text="No alarms set",
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 13)).pack(pady=30)
            return
        for i, alarm in enumerate(self._alarms):
            row = tk.Frame(self._alarm_frame, bg=T["win_bg"])
            row.pack(fill="x", padx=20, pady=6)
            time_str = f"{alarm['h']:02d}:{alarm['m']:02d}"
            tk.Label(row, text=time_str, bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 28, "bold")).pack(side="left")
            tk.Label(row, text=alarm.get("label","Alarm"),
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 13)).pack(side="left", padx=12)
            # Toggle
            var = tk.BooleanVar(value=alarm.get("enabled", True))
            chk = tk.Checkbutton(row, variable=var, bg=T["win_bg"],
                                  activebackground=T["win_bg"],
                                  command=lambda i=i, v=var: self._toggle_alarm(i, v.get()))
            chk.pack(side="right")
            tk.Label(row, text="🗑️", bg=T["win_bg"], cursor="hand2",
                     font=(FONT_EMOJI, 14)).pack(side="right", padx=4)

    def _add_alarm(self) -> None:
        try:
            h = int(self._alarm_h.get())
            m = int(self._alarm_m.get())
        except ValueError:
            return
        self._alarms.append({"h": h, "m": m,
                              "label": self._alarm_lbl_var.get(),
                              "enabled": True})
        self._refresh_alarms()
        self.wm.notifs.send("Clock", f"Alarm set for {h:02d}:{m:02d}", icon="⏰")

    def _toggle_alarm(self, idx: int, enabled: bool) -> None:
        if idx < len(self._alarms):
            self._alarms[idx]["enabled"] = enabled

    # ── Stopwatch ─────────────────────────────────────────────────────────────

    def _build_stopwatch(self) -> None:
        self._sw_display = tk.Label(
            self._content, text="00:00.00",
            bg=T["win_bg"], fg=T["text"],
            font=(FONT_MONO, 52, "bold"),
        )
        self._sw_display.pack(pady=30)

        btn_row = tk.Frame(self._content, bg=T["win_bg"])
        btn_row.pack()
        self._sw_start_btn = tk.Button(
            btn_row, text="Start",
            bg=T["accent3"], fg="#ffffff",
            font=(FONT_UI, 15), relief="flat",
            padx=24, pady=8, cursor="hand2",
            command=self._sw_toggle,
        )
        self._sw_start_btn.pack(side="left", padx=8)
        tk.Button(btn_row, text="Lap",
                  bg=T["button_secondary"], fg=T["text"],
                  font=(FONT_UI, 15), relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=self._sw_lap).pack(side="left", padx=8)
        tk.Button(btn_row, text="Reset",
                  bg=T["button_secondary"], fg=T["text"],
                  font=(FONT_UI, 15), relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=self._sw_reset).pack(side="left", padx=8)

        self._lap_box = tk.Text(
            self._content, height=5,
            bg=T["panel_bg"], fg=T["text"],
            font=(FONT_MONO, 12), relief="flat",
            state="disabled",
        )
        self._lap_box.pack(fill="x", padx=20, pady=12)

    def _sw_toggle(self) -> None:
        if not self._running:
            self._sw_start = time.time()
            self._running  = True
            self._sw_start_btn.configure(text="Stop", bg=T["danger"])
        else:
            self._sw_accum += time.time() - (self._sw_start or time.time())
            self._sw_start  = None
            self._running   = False
            self._sw_start_btn.configure(text="Start", bg=T["accent3"])

    def _sw_lap(self) -> None:
        elapsed = self._sw_accum
        if self._running and self._sw_start:
            elapsed += time.time() - self._sw_start
        s = elapsed
        mins, secs = divmod(s, 60)
        lap_str = f"Lap {len(self._sw_laps)+1:>2}:  {int(mins):02d}:{secs:05.2f}"
        self._sw_laps.append(lap_str)
        self._lap_box.configure(state="normal")
        self._lap_box.insert("end", lap_str + "\n")
        self._lap_box.see("end")
        self._lap_box.configure(state="disabled")

    def _sw_reset(self) -> None:
        self._running   = False
        self._sw_start  = None
        self._sw_accum  = 0.0
        self._sw_laps   = []
        if hasattr(self, "_sw_display"):
            self._sw_display.configure(text="00:00.00")
        if hasattr(self, "_sw_start_btn"):
            self._sw_start_btn.configure(text="Start", bg=T["accent3"])
        if hasattr(self, "_lap_box"):
            self._lap_box.configure(state="normal")
            self._lap_box.delete("1.0", "end")
            self._lap_box.configure(state="disabled")

    def _update_sw(self) -> None:
        if not hasattr(self, "_sw_display"):
            return
        if self._tab != "stopwatch":
            return
        elapsed = self._sw_accum
        if self._running and self._sw_start:
            elapsed += time.time() - self._sw_start
        mins, secs = divmod(elapsed, 60)
        self._sw_display.configure(text=f"{int(mins):02d}:{secs:05.2f}")

    # ── Timer ─────────────────────────────────────────────────────────────────

    def _build_timer(self) -> None:
        tk.Label(self._content, text="Set Timer",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold")).pack(pady=(20, 8))

        set_row = tk.Frame(self._content, bg=T["win_bg"])
        set_row.pack()
        for label, from_, to, attr in [("Hours", 0, 23, "_t_h"),
                                        ("Min",   0, 59, "_t_m"),
                                        ("Sec",   0, 59, "_t_s")]:
            col = tk.Frame(set_row, bg=T["win_bg"])
            col.pack(side="left", padx=10)
            sp = tk.Spinbox(col, from_=from_, to=to, width=3,
                            bg=T["input_bg"], fg=T["text"],
                            font=(FONT_MONO, 28), relief="flat",
                            justify="center")
            sp.pack()
            tk.Label(col, text=label, bg=T["win_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 10)).pack()
            setattr(self, attr, sp)

        self._timer_display = tk.Label(
            self._content, text="00:00:00",
            bg=T["win_bg"], fg=T["accent"],
            font=(FONT_MONO, 48, "bold"),
        )
        self._timer_display.pack(pady=20)

        btn_row = tk.Frame(self._content, bg=T["win_bg"])
        btn_row.pack()
        self._timer_btn = tk.Button(
            btn_row, text="Start",
            bg=T["accent"], fg="#ffffff",
            font=(FONT_UI, 15), relief="flat",
            padx=24, pady=8, cursor="hand2",
            command=self._timer_toggle,
        )
        self._timer_btn.pack(side="left", padx=8)
        tk.Button(btn_row, text="Reset",
                  bg=T["button_secondary"], fg=T["text"],
                  font=(FONT_UI, 15), relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=self._timer_reset).pack(side="left", padx=8)

    def _timer_toggle(self) -> None:
        if not self._timer_running:
            try:
                h = int(self._t_h.get())
                m = int(self._t_m.get())
                s = int(self._t_s.get())
            except Exception:
                h = m = s = 0
            self._timer_rem = h * 3600 + m * 60 + s
            if self._timer_rem <= 0:
                return
            self._timer_running = True
            self._timer_btn.configure(text="Pause", bg=T["warning"])
        else:
            self._timer_running = False
            self._timer_btn.configure(text="Resume", bg=T["accent"])

    def _timer_reset(self) -> None:
        self._timer_running = False
        self._timer_rem     = 0
        if hasattr(self, "_timer_display"):
            self._timer_display.configure(text="00:00:00", fg=T["accent"])
        if hasattr(self, "_timer_btn"):
            self._timer_btn.configure(text="Start", bg=T["accent"])

    def _update_timer(self) -> None:
        if not hasattr(self, "_timer_display"):
            return
        if self._tab != "timer":
            return
        if self._timer_running and self._timer_rem > 0:
            self._timer_rem -= 1
            if self._timer_rem <= 0:
                self._timer_running = False
                self._timer_display.configure(text="00:00:00", fg=T["danger"])
                self.wm.notifs.send("Clock", "Timer finished!", icon="⏰")
                if hasattr(self, "_timer_btn"):
                    self._timer_btn.configure(text="Start", bg=T["accent"])
                return
        h, rem = divmod(self._timer_rem, 3600)
        m, s   = divmod(rem, 60)
        self._timer_display.configure(text=f"{h:02d}:{m:02d}:{s:02d}")

    # ── tick ──────────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        if self._closed:
            return
        self._update_world()
        self._update_sw()
        self._update_timer()
        self._check_alarms()
        self.client.after(1000, self._tick)

    def _check_alarms(self) -> None:
        now = datetime.datetime.now()
        for alarm in self._alarms:
            if (alarm.get("enabled") and
                    alarm["h"] == now.hour and
                    alarm["m"] == now.minute and
                    now.second == 0):
                self.wm.notifs.send(
                    "Alarm",
                    alarm.get("label", "Alarm") + f" — {alarm['h']:02d}:{alarm['m']:02d}",
                    icon="⏰", duration=8.0,
                )


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 25 — ACTIVITY MONITOR APP
# ─────────────────────────────────────────────────────────────────────────────

class ActivityMonitorApp(BaseWin):
    """macOS Activity Monitor — CPU, Memory, Energy, Disk, Network tabs."""

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "Activity Monitor", w=740, h=520, icon="📊")
        self._tab = "cpu"
        self._cpu_history:  deque = deque([0.0] * 60, maxlen=60)
        self._ram_history:  deque = deque([0.0] * 60, maxlen=60)
        self._disk_read:    deque = deque([0.0] * 60, maxlen=60)
        self._disk_write:   deque = deque([0.0] * 60, maxlen=60)
        self._net_in:       deque = deque([0.0] * 60, maxlen=60)
        self._net_out:      deque = deque([0.0] * 60, maxlen=60)
        self._build_ui()
        self._tick()

    def _build_ui(self) -> None:
        # Toolbar
        tb = tk.Frame(self.client, bg=T["panel_bg"], pady=6)
        tb.pack(fill="x")

        # Search
        search_var = tk.StringVar()
        search_e = tk.Entry(tb, textvariable=search_var,
                            bg=T["input_bg"], fg=T["text"],
                            font=(FONT_UI, 12), relief="flat",
                            highlightthickness=1,
                            highlightbackground=T["input_border"],
                            highlightcolor=T["input_focus"],
                            width=18)
        search_e.pack(side="right", padx=10)
        tk.Label(tb, text="🔍", bg=T["panel_bg"],
                 font=(FONT_EMOJI, 13)).pack(side="right")

        # Tab buttons
        self._tab_btns: Dict[str, tk.Label] = {}
        for key, emoji, label in [
            ("cpu",     "🧠", "CPU"),
            ("memory",  "💾", "Memory"),
            ("energy",  "⚡", "Energy"),
            ("disk",    "💿", "Disk"),
            ("network", "🌐", "Network"),
        ]:
            btn = tk.Label(tb, text=f"{emoji} {label}",
                           bg=T["panel_bg"], fg=T["text_muted"],
                           font=(FONT_UI, 12), padx=10, cursor="hand2")
            btn.pack(side="left", padx=2)
            btn.bind("<Button-1>", lambda _, k=key: self._switch_tab(k))
            self._tab_btns[key] = btn

        self._content = tk.Frame(self.client, bg=T["win_bg"])
        self._content.pack(fill="both", expand=True)
        self._switch_tab("cpu")

    def _switch_tab(self, tab: str) -> None:
        self._tab = tab
        for k, btn in self._tab_btns.items():
            btn.configure(
                fg=T["accent"] if k == tab else T["text_muted"],
                font=(FONT_UI, 12, "bold") if k == tab else (FONT_UI, 12),
            )
        for w in self._content.winfo_children():
            w.destroy()
        {
            "cpu":     self._build_cpu,
            "memory":  self._build_memory,
            "energy":  self._build_energy,
            "disk":    self._build_disk,
            "network": self._build_network,
        }[tab]()

    # ── CPU tab ───────────────────────────────────────────────────────────────

    def _build_cpu(self) -> None:
        pane = tk.Frame(self._content, bg=T["win_bg"])
        pane.pack(fill="both", expand=True)

        # Process list (top)
        cols = ("Process", "PID", "User", "% CPU", "Threads")
        self._cpu_tree = ttk.Treeview(pane, columns=cols, show="headings", height=10)
        for col in cols:
            w = {"Process": 200, "PID": 60, "User": 80, "% CPU": 80, "Threads": 70}[col]
            self._cpu_tree.heading(col, text=col)
            self._cpu_tree.column(col, width=w, anchor="w" if col == "Process" else "center")
        sb = ttk.Scrollbar(pane, orient="vertical", command=self._cpu_tree.yview)
        self._cpu_tree.configure(yscrollcommand=sb.set)
        self._cpu_tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        sb.pack(side="left", fill="y", pady=10)

        # Bottom stats
        bottom = tk.Frame(self._content, bg=T["panel_bg"])
        bottom.pack(fill="x", side="bottom")

        # Mini CPU graph
        self._cpu_canvas = tk.Canvas(bottom, bg="#1c1c1e", height=80,
                                      highlightthickness=0)
        self._cpu_canvas.pack(fill="x", padx=10, pady=8)

        stats_row = tk.Frame(bottom, bg=T["panel_bg"])
        stats_row.pack(fill="x", padx=10, pady=(0, 8))
        self._cpu_stat_vars: Dict[str, tk.StringVar] = {}
        for label in ["% User", "% System", "% Idle", "Cores"]:
            col = tk.Frame(stats_row, bg=T["panel_bg"])
            col.pack(side="left", expand=True)
            tk.Label(col, text=label, bg=T["panel_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 10)).pack()
            var = tk.StringVar(value="—")
            tk.Label(col, textvariable=var, bg=T["panel_bg"],
                     fg=T["text"], font=(FONT_UI, 13, "bold")).pack()
            self._cpu_stat_vars[label] = var

    def _update_cpu_tab(self) -> None:
        if self._tab != "cpu":
            return
        procs = self.wm.procs.list_all()
        procs.sort(key=lambda p: p.cpu, reverse=True)

        if hasattr(self, "_cpu_tree"):
            self._cpu_tree.delete(*self._cpu_tree.get_children())
            for p in procs[:40]:
                self._cpu_tree.insert("", "end", values=(
                    p.name, p.pid, p.user,
                    f"{p.cpu:.1f}",
                    str(random.randint(1, 12)),
                ))

        total = self.wm.procs.total_cpu()
        self._cpu_history.append(total)
        user   = total * 0.6
        system = total * 0.4
        idle   = max(0.0, 100.0 - total)

        if hasattr(self, "_cpu_stat_vars"):
            self._cpu_stat_vars["% User"].set(f"{user:.1f}")
            self._cpu_stat_vars["% System"].set(f"{system:.1f}")
            self._cpu_stat_vars["% Idle"].set(f"{idle:.1f}")
            self._cpu_stat_vars["Cores"].set("8")

        if hasattr(self, "_cpu_canvas"):
            self._draw_graph(self._cpu_canvas, list(self._cpu_history),
                             100.0, T["chart1"], "CPU %")

    # ── Memory tab ────────────────────────────────────────────────────────────

    def _build_memory(self) -> None:
        pane = tk.Frame(self._content, bg=T["win_bg"])
        pane.pack(fill="both", expand=True)

        cols = ("Process", "PID", "User", "Memory (MB)", "Compressed")
        self._mem_tree = ttk.Treeview(pane, columns=cols, show="headings", height=10)
        for col in cols:
            w = {"Process":180,"PID":60,"User":80,"Memory (MB)":100,"Compressed":90}[col]
            self._mem_tree.heading(col, text=col)
            self._mem_tree.column(col, width=w, anchor="w" if col in ("Process","User") else "center")
        sb = ttk.Scrollbar(pane, orient="vertical", command=self._mem_tree.yview)
        self._mem_tree.configure(yscrollcommand=sb.set)
        self._mem_tree.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        sb.pack(side="left", fill="y", pady=10)

        bottom = tk.Frame(self._content, bg=T["panel_bg"])
        bottom.pack(fill="x", side="bottom")
        self._ram_canvas = tk.Canvas(bottom, bg="#1c1c1e", height=80,
                                      highlightthickness=0)
        self._ram_canvas.pack(fill="x", padx=10, pady=8)

        stats_row = tk.Frame(bottom, bg=T["panel_bg"])
        stats_row.pack(fill="x", padx=10, pady=(0,8))
        self._mem_stat_vars: Dict[str, tk.StringVar] = {}
        for label in ["Used", "Wired", "Compressed", "Physical"]:
            col = tk.Frame(stats_row, bg=T["panel_bg"])
            col.pack(side="left", expand=True)
            tk.Label(col, text=label, bg=T["panel_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 10)).pack()
            var = tk.StringVar(value="—")
            tk.Label(col, textvariable=var, bg=T["panel_bg"],
                     fg=T["text"], font=(FONT_UI, 13, "bold")).pack()
            self._mem_stat_vars[label] = var

    def _update_memory_tab(self) -> None:
        if self._tab != "memory":
            return
        procs = sorted(self.wm.procs.list_all(), key=lambda p: p.ram, reverse=True)
        if hasattr(self, "_mem_tree"):
            self._mem_tree.delete(*self._mem_tree.get_children())
            for p in procs[:40]:
                self._mem_tree.insert("", "end", values=(
                    p.name, p.pid, p.user,
                    f"{p.ram:.1f}",
                    f"{p.ram * 0.05:.1f}",
                ))
        total_mb = self.wm.procs.total_ram()
        self._ram_history.append(min(total_mb, 16384))
        if hasattr(self, "_mem_stat_vars"):
            self._mem_stat_vars["Used"].set(f"{total_mb/1024:.2f} GB")
            self._mem_stat_vars["Wired"].set(f"{total_mb*0.25/1024:.2f} GB")
            self._mem_stat_vars["Compressed"].set(f"{total_mb*0.05/1024:.2f} GB")
            self._mem_stat_vars["Physical"].set("16.00 GB")
        if hasattr(self, "_ram_canvas"):
            self._draw_graph(self._ram_canvas, list(self._ram_history),
                             16384, T["chart2"], "RAM MB")

    # ── Energy tab ────────────────────────────────────────────────────────────

    def _build_energy(self) -> None:
        cols = ("App", "Energy Impact", "Avg Energy", "Wake-ups/sec")
        self._nrg_tree = ttk.Treeview(self._content, columns=cols,
                                       show="headings", height=16)
        for col in cols:
            w = {"App":200,"Energy Impact":120,"Avg Energy":120,"Wake-ups/sec":120}[col]
            self._nrg_tree.heading(col, text=col)
            self._nrg_tree.column(col, width=w, anchor="w" if col=="App" else "center")
        sb = ttk.Scrollbar(self._content, orient="vertical",
                           command=self._nrg_tree.yview)
        self._nrg_tree.configure(yscrollcommand=sb.set)
        self._nrg_tree.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        sb.pack(side="left", fill="y", pady=10)

        bottom = tk.Frame(self._content, bg=T["panel_bg"])
        bottom.pack(fill="x", side="bottom")
        for label, val in [("Battery Remaining","—"),("Time on Battery","—"),
                           ("Energy Used Today","—")]:
            row = tk.Frame(bottom, bg=T["panel_bg"])
            row.pack(fill="x", padx=16, pady=3)
            tk.Label(row, text=label, bg=T["panel_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 12)).pack(side="left")
            tk.Label(row, text=val, bg=T["panel_bg"],
                     fg=T["text"], font=(FONT_UI, 12)).pack(side="right")

    def _update_energy_tab(self) -> None:
        if self._tab != "energy" or not hasattr(self, "_nrg_tree"):
            return
        self._nrg_tree.delete(*self._nrg_tree.get_children())
        procs = sorted(self.wm.procs.list_all(), key=lambda p: p.cpu, reverse=True)
        for p in procs[:30]:
            impact = p.cpu * 0.5
            label = ("High" if impact > 20 else "Medium" if impact > 5 else "Low")
            self._nrg_tree.insert("", "end", values=(
                p.name, label, f"{impact:.1f}", str(random.randint(0, 30))
            ))

    # ── Disk tab ──────────────────────────────────────────────────────────────

    def _build_disk(self) -> None:
        pane = tk.Frame(self._content, bg=T["win_bg"])
        pane.pack(fill="both", expand=True)
        cols = ("Process", "PID", "Read MB/s", "Write MB/s", "Read Bytes", "Write Bytes")
        self._disk_tree = ttk.Treeview(pane, columns=cols, show="headings", height=10)
        for col in cols:
            w = {"Process":160,"PID":60,"Read MB/s":90,"Write MB/s":90,
                 "Read Bytes":100,"Write Bytes":100}[col]
            self._disk_tree.heading(col, text=col)
            self._disk_tree.column(col, width=w, anchor="center")
        sb = ttk.Scrollbar(pane, orient="vertical", command=self._disk_tree.yview)
        self._disk_tree.configure(yscrollcommand=sb.set)
        self._disk_tree.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        sb.pack(side="left", fill="y", pady=10)

        bottom = tk.Frame(self._content, bg=T["panel_bg"])
        bottom.pack(fill="x", side="bottom")
        self._disk_canvas = tk.Canvas(bottom, bg="#1c1c1e", height=60,
                                       highlightthickness=0)
        self._disk_canvas.pack(fill="x", padx=10, pady=6)

    def _update_disk_tab(self) -> None:
        if self._tab != "disk" or not hasattr(self, "_disk_tree"):
            return
        self._disk_tree.delete(*self._disk_tree.get_children())
        for p in self.wm.procs.list_all()[:30]:
            r = random.uniform(0, 2)
            w = random.uniform(0, 1)
            self._disk_tree.insert("", "end", values=(
                p.name, p.pid,
                f"{r:.2f}", f"{w:.2f}",
                f"{r*1024*1024:.0f}", f"{w*1024*1024:.0f}",
            ))
        dr = random.uniform(0, 5)
        dw = random.uniform(0, 3)
        self._disk_read.append(dr)
        self._disk_write.append(dw)

    # ── Network tab ───────────────────────────────────────────────────────────

    def _build_network(self) -> None:
        pane = tk.Frame(self._content, bg=T["win_bg"])
        pane.pack(fill="both", expand=True)
        cols = ("Process", "PID", "Sent MB/s", "Recv MB/s", "Packets In", "Packets Out")
        self._net_tree = ttk.Treeview(pane, columns=cols, show="headings", height=10)
        for col in cols:
            w = {"Process":160,"PID":60,"Sent MB/s":90,"Recv MB/s":90,
                 "Packets In":100,"Packets Out":100}[col]
            self._net_tree.heading(col, text=col)
            self._net_tree.column(col, width=w, anchor="center")
        sb = ttk.Scrollbar(pane, orient="vertical", command=self._net_tree.yview)
        self._net_tree.configure(yscrollcommand=sb.set)
        self._net_tree.pack(side="left", fill="both", expand=True, padx=(10,0), pady=10)
        sb.pack(side="left", fill="y", pady=10)

        bottom = tk.Frame(self._content, bg=T["panel_bg"])
        bottom.pack(fill="x", side="bottom")
        self._net_canvas = tk.Canvas(bottom, bg="#1c1c1e", height=60,
                                      highlightthickness=0)
        self._net_canvas.pack(fill="x", padx=10, pady=6)

        stats_row = tk.Frame(bottom, bg=T["panel_bg"])
        stats_row.pack(fill="x", padx=10, pady=(0, 8))
        self._net_vars: Dict[str, tk.StringVar] = {}
        for label in ["Packets In", "Packets Out", "Data In", "Data Out"]:
            col = tk.Frame(stats_row, bg=T["panel_bg"])
            col.pack(side="left", expand=True)
            tk.Label(col, text=label, bg=T["panel_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 10)).pack()
            var = tk.StringVar(value="0")
            tk.Label(col, textvariable=var, bg=T["panel_bg"],
                     fg=T["text"], font=(FONT_UI, 12, "bold")).pack()
            self._net_vars[label] = var

    def _update_network_tab(self) -> None:
        if self._tab != "network" or not hasattr(self, "_net_tree"):
            return
        self._net_tree.delete(*self._net_tree.get_children())
        for p in self.wm.procs.list_all()[:30]:
            s = random.uniform(0, 0.5)
            r = random.uniform(0, 1)
            self._net_tree.insert("", "end", values=(
                p.name, p.pid,
                f"{s:.3f}", f"{r:.3f}",
                str(random.randint(0, 500)),
                str(random.randint(0, 200)),
            ))
        ni = random.uniform(0, 2)
        no = random.uniform(0, 1)
        self._net_in.append(ni)
        self._net_out.append(no)
        if hasattr(self, "_net_vars"):
            self._net_vars["Packets In"].set(str(random.randint(1000, 9999)))
            self._net_vars["Packets Out"].set(str(random.randint(500, 4999)))
            self._net_vars["Data In"].set(f"{ni*1024:.0f} KB/s")
            self._net_vars["Data Out"].set(f"{no*1024:.0f} KB/s")

    # ── shared graph helper ───────────────────────────────────────────────────

    def _draw_graph(self, canvas: tk.Canvas, data: List[float],
                    max_val: float, color: str, label: str) -> None:
        canvas.delete("all")
        w = canvas.winfo_width() or 700
        h = canvas.winfo_height() or 80
        if not data or max_val <= 0:
            return
        step = w / max(len(data) - 1, 1)
        pts: List[float] = []
        for i, v in enumerate(data):
            x = i * step
            y = h - (v / max_val) * (h - 4) - 2
            pts.extend([x, y])
        if len(pts) >= 4:
            canvas.create_line(*pts, fill=color, width=2, smooth=True)
        # Fill under line
        fill_pts = [0, h] + pts + [w, h]
        if len(fill_pts) >= 6:
            try:
                # lighten the color for fill
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                fill_color = f"#{r:02x}{g:02x}{b:02x}44"
                canvas.create_polygon(*fill_pts, fill=fill_color, outline="")
            except Exception:
                pass
        canvas.create_text(8, 8, text=label, fill=color,
                           font=(FONT_UI, 9), anchor="nw")
        canvas.create_text(w - 4, 8,
                           text=f"{data[-1]:.1f}" if data else "",
                           fill=color, font=(FONT_UI, 9), anchor="ne")

    # ── tick ──────────────────────────────────────────────────────────────────

    def _tick(self) -> None:
        if self._closed:
            return
        self._update_cpu_tab()
        self._update_memory_tab()
        self._update_energy_tab()
        self._update_disk_tab()
        self._update_network_tab()
        self.client.after(2000, self._tick)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 26 — NOTES APP
# ─────────────────────────────────────────────────────────────────────────────

class NotesApp(BaseWin):
    """macOS Notes — sidebar with note list + editor, persistent in VFS."""

    NOTES_DIR = "/Users/user/Documents/Notes"

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "Notes", w=680, h=520, icon="🗒️")
        wm.vfs.makedirs(self.NOTES_DIR)
        self._current_note: Optional[str] = None
        self._build_ui()
        self._load_notes()

    def _build_ui(self) -> None:
        # Toolbar
        tb = tk.Frame(self.client, bg=T["panel_bg"], pady=6)
        tb.pack(fill="x")
        tk.Label(tb, text="Notes", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 14, "bold"),
                 padx=12).pack(side="left")
        tk.Label(tb, text="＋", bg=T["panel_bg"],
                 fg=T["accent"], font=(FONT_UI, 20),
                 cursor="hand2", padx=8).pack(side="right",
                 ).bind("<Button-1>", lambda _: self._new_note())
        tk.Label(tb, text="🗑️", bg=T["panel_bg"],
                 fg=T["danger"], font=(FONT_EMOJI, 14),
                 cursor="hand2", padx=8).pack(side="right",
                 ).bind("<Button-1>", lambda _: self._delete_note())

        # Search
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._filter_notes())
        search_frame = tk.Frame(self.client, bg=T["panel_bg"], pady=4)
        search_frame.pack(fill="x", padx=8)
        tk.Label(search_frame, text="🔍", bg=T["panel_bg"],
                 font=(FONT_EMOJI, 12)).pack(side="left")
        tk.Entry(search_frame, textvariable=self._search_var,
                 bg=T["input_bg"], fg=T["text"],
                 font=(FONT_UI, 12), relief="flat",
                 highlightthickness=1,
                 highlightbackground=T["input_border"]).pack(
                 side="left", fill="x", expand=True, padx=4)

        # Paned layout
        pane = tk.PanedWindow(self.client, orient="horizontal",
                              bg=T["separator"], sashwidth=1,
                              sashrelief="flat")
        pane.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(pane, bg=T["sidebar_bg"], width=200)
        sidebar.pack_propagate(False)
        pane.add(sidebar, width=200)

        self._note_listbox = tk.Listbox(
            sidebar,
            bg=T["sidebar_bg"], fg=T["text"],
            selectbackground=T["selection"],
            selectforeground=T["text"],
            font=(FONT_UI, 13),
            relief="flat", bd=0,
            highlightthickness=0,
            activestyle="none",
        )
        self._note_listbox.pack(fill="both", expand=True, padx=4, pady=4)
        self._note_listbox.bind("<<ListboxSelect>>", self._on_select)

        # Editor
        editor_frame = tk.Frame(pane, bg=T["win_bg"])
        pane.add(editor_frame)

        # Note title bar
        title_bar = tk.Frame(editor_frame, bg=T["panel_bg"], pady=6)
        title_bar.pack(fill="x")
        self._note_title_var = tk.StringVar()
        self._note_title_entry = tk.Entry(
            title_bar, textvariable=self._note_title_var,
            bg=T["panel_bg"], fg=T["text"],
            font=(FONT_UI, 16, "bold"), relief="flat",
            highlightthickness=0,
        )
        self._note_title_entry.pack(fill="x", padx=12)
        self._note_title_entry.bind("<FocusOut>", lambda _: self._save_current())

        # Date label
        self._note_date_lbl = tk.Label(
            editor_frame, text="",
            bg=T["win_bg"], fg=T["text_muted"],
            font=(FONT_UI, 10),
        )
        self._note_date_lbl.pack(anchor="w", padx=12)

        tk.Frame(editor_frame, bg=T["separator"], height=1).pack(fill="x")

        # Text editor
        self._editor = tk.Text(
            editor_frame,
            bg=T["win_bg"], fg=T["text"],
            font=(FONT_UI, 14),
            relief="flat", bd=0,
            padx=16, pady=12,
            wrap="word",
            insertbackground=T["text"],
            selectbackground=T["selection"],
            undo=True,
        )
        self._editor.pack(fill="both", expand=True)
        self._editor.bind("<KeyRelease>", lambda _: self._save_current())

        # Format toolbar
        fmt_bar = tk.Frame(editor_frame, bg=T["panel_bg"], pady=4)
        fmt_bar.pack(fill="x", side="bottom")
        for symbol, font_mod in [("B", "bold"), ("I", "italic"), ("U", "underline")]:
            btn = tk.Label(fmt_bar, text=symbol,
                           bg=T["panel_bg"], fg=T["text"],
                           font=(FONT_UI, 13, font_mod),
                           padx=8, cursor="hand2")
            btn.pack(side="left")
        self._word_count_lbl = tk.Label(fmt_bar, text="0 words",
                                         bg=T["panel_bg"], fg=T["text_muted"],
                                         font=(FONT_UI, 10))
        self._word_count_lbl.pack(side="right", padx=8)
        self._editor.bind("<KeyRelease>", self._on_key)

    def _on_key(self, _: tk.Event) -> None:
        self._save_current()
        content = self._editor.get("1.0", "end-1c")
        words = len(content.split())
        self._word_count_lbl.configure(text=f"{words} word{'s' if words != 1 else ''}")

    def _load_notes(self) -> None:
        self._notes: Dict[str, str] = {}
        try:
            for fname in self.wm.vfs.listdir(self.NOTES_DIR):
                if fname.endswith(".txt") or fname.endswith(".md"):
                    path = f"{self.NOTES_DIR}/{fname}"
                    content = self.wm.vfs.read(path)
                    self._notes[fname] = content
        except Exception:
            pass
        # Create default note if empty
        if not self._notes:
            self._notes["Welcome.txt"] = (
                "Welcome to Notes\n\n"
                "This is your first note. Click + to create a new note.\n"
            )
            self.wm.vfs.write(f"{self.NOTES_DIR}/Welcome.txt",
                               self._notes["Welcome.txt"])
        self._refresh_list()
        if self._notes:
            first = next(iter(self._notes))
            self._open_note(first)

    def _refresh_list(self, filter_str: str = "") -> None:
        self._note_listbox.delete(0, "end")
        self._list_keys: List[str] = []
        for name in sorted(self._notes.keys()):
            if filter_str.lower() in name.lower() or \
               filter_str.lower() in self._notes[name].lower():
                display = name.replace(".txt","").replace(".md","")
                self._note_listbox.insert("end", f"🗒️  {display}")
                self._list_keys.append(name)

    def _filter_notes(self) -> None:
        self._refresh_list(self._search_var.get())

    def _on_select(self, _: tk.Event) -> None:
        sel = self._note_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(self._list_keys):
            self._open_note(self._list_keys[idx])

    def _open_note(self, name: str) -> None:
        self._save_current()
        self._current_note = name
        content = self._notes.get(name, "")
        title   = name.replace(".txt","").replace(".md","")
        self._note_title_var.set(title)
        self._editor.delete("1.0", "end")
        self._editor.insert("1.0", content)
        now = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
        self._note_date_lbl.configure(text=now)

    def _save_current(self) -> None:
        if not self._current_note:
            return
        content = self._editor.get("1.0", "end-1c")
        self._notes[self._current_note] = content
        path = f"{self.NOTES_DIR}/{self._current_note}"
        try:
            self.wm.vfs.write(path, content)
        except Exception:
            pass

    def _new_note(self) -> None:
        name = simpledialog.askstring("New Note", "Note title:",
                                       parent=self.wm.root)
        if not name:
            name = f"Note {len(self._notes)+1}"
        fname = name + ".txt"
        self._notes[fname] = ""
        self.wm.vfs.write(f"{self.NOTES_DIR}/{fname}", "")
        self._refresh_list()
        self._open_note(fname)
        self._editor.focus_set()

    def _delete_note(self) -> None:
        if not self._current_note:
            return
        if messagebox.askyesno("Delete Note",
                               f"Delete '{self._current_note}'?",
                               parent=self.wm.root):
            path = f"{self.NOTES_DIR}/{self._current_note}"
            try:
                self.wm.vfs.remove(path)
            except Exception:
                pass
            del self._notes[self._current_note]
            self._current_note = None
            self._editor.delete("1.0", "end")
            self._note_title_var.set("")
            self._refresh_list()
            if self._notes:
                first = next(iter(self._notes))
                self._open_note(first)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 27 — MAIL APP
# ─────────────────────────────────────────────────────────────────────────────

class MailApp(BaseWin):
    """macOS Mail — three-pane layout: Mailboxes | Message List | Message."""

    SAMPLE_MESSAGES = [
        {
            "from": "Tim Cook <tim@apple.com>",
            "to":   "user@macpyos.local",
            "subject": "Welcome to MacPyOS!",
            "date":    "Today, 9:41 AM",
            "preview": "Hi there! Welcome to your new MacPyOS experience...",
            "body":    "Hi there!\n\nWelcome to MacPyOS — your new Python-powered "
                       "macOS simulation.\n\nWe hope you enjoy the experience.\n\n"
                       "Best regards,\nTim",
            "read":    False,
            "starred": True,
            "mailbox": "Inbox",
        },
        {
            "from": "App Store <no-reply@apple.com>",
            "to":   "user@macpyos.local",
            "subject": "Your receipt from the App Store",
            "date":    "Yesterday, 3:22 PM",
            "preview": "Thank you for your purchase. Items: MacPyOS Pro...",
            "body":    "Thank you for your purchase!\n\nOrder #: MPY-2025-001\n"
                       "MacPyOS Pro Upgrade — $0.00 (FREE)\n\nThank you!",
            "read":    True,
            "starred": False,
            "mailbox": "Inbox",
        },
        {
            "from": "GitHub <noreply@github.com>",
            "to":   "user@macpyos.local",
            "subject": "[macpyos/macpyos] New issue opened: Feature request",
            "date":    "Mon, 9:14 AM",
            "preview": "A new issue has been opened in macpyos/macpyos...",
            "body":    "A new issue has been opened:\n\n"
                       "Title: Add Dark Mode support\n"
                       "Author: contributor42\n\n"
                       "Please add proper dark mode with system preference detection.",
            "read":    True,
            "starred": False,
            "mailbox": "Inbox",
        },
        {
            "from": "newsletters@medium.com",
            "to":   "user@macpyos.local",
            "subject": "Top Python stories this week",
            "date":    "Sun, 6:00 AM",
            "preview": "Building desktop GUIs in Python — a deep dive...",
            "body":    "This week on Medium:\n\n"
                       "1. Building desktop GUIs in Python\n"
                       "2. Why Tkinter is still relevant in 2025\n"
                       "3. From script to app — packaging Python programs\n",
            "read":    True,
            "starred": False,
            "mailbox": "Inbox",
        },
        {
            "from": "user@macpyos.local",
            "to":   "friend@example.com",
            "subject": "Check out MacPyOS!",
            "date":    "Fri, 2:30 PM",
            "preview": "Hey! I've been using this amazing Python desktop sim...",
            "body":    "Hey!\n\nYou have to check out MacPyOS — it's a full "
                       "desktop OS simulation built with Python and Tkinter.\n\n"
                       "No external deps, runs anywhere!\n\nCheers",
            "read":    True,
            "starred": False,
            "mailbox": "Sent",
        },
        {
            "from": "boss@company.com",
            "to":   "user@macpyos.local",
            "subject": "Meeting tomorrow",
            "date":    "Thu, 4:15 PM",
            "preview": "Don't forget we have the Q1 review at 10am...",
            "body":    "Hi,\n\nJust a reminder that we have the Q1 review "
                       "meeting tomorrow at 10:00 AM in Conference Room B.\n\n"
                       "Please prepare your slides.\n\nThanks",
            "read":    False,
            "starred": True,
            "mailbox": "Inbox",
        },
    ]

    MAILBOXES = ["Inbox", "Sent", "Drafts", "Junk", "Trash", "Archive"]

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "Mail", w=900, h=580, icon="📧")
        self._messages      = [dict(m) for m in self.SAMPLE_MESSAGES]
        self._current_box   = "Inbox"
        self._current_msg   : Optional[int] = None
        self._build_ui()

    def _build_ui(self) -> None:
        # Toolbar
        tb = tk.Frame(self.client, bg=T["panel_bg"], pady=6)
        tb.pack(fill="x")

        for text, cmd in [("✉️ Get Mail", self._get_mail),
                          ("✏️ Compose",  self._compose),
                          ("↩️ Reply",    self._reply),
                          ("🗑️ Delete",   self._delete_msg)]:
            btn = tk.Label(tb, text=text, bg=T["panel_bg"], fg=T["text"],
                           font=(FONT_UI, 12), padx=10, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda _, c=cmd: c())

        # Search
        sv = tk.StringVar()
        sv.trace_add("write", lambda *_: self._search(sv.get()))
        tk.Entry(tb, textvariable=sv, bg=T["input_bg"], fg=T["text"],
                 font=(FONT_UI, 12), relief="flat",
                 highlightthickness=1,
                 highlightbackground=T["input_border"],
                 width=20).pack(side="right", padx=10)
        tk.Label(tb, text="🔍", bg=T["panel_bg"],
                 font=(FONT_EMOJI, 12)).pack(side="right")

        # Three-pane
        outer = tk.PanedWindow(self.client, orient="horizontal",
                               bg=T["separator"], sashwidth=1)
        outer.pack(fill="both", expand=True)

        # Mailbox sidebar
        mbx_frame = tk.Frame(outer, bg=T["sidebar_bg"], width=160)
        mbx_frame.pack_propagate(False)
        outer.add(mbx_frame, width=160)

        tk.Label(mbx_frame, text="Mailboxes", bg=T["sidebar_bg"],
                 fg=T["text_muted"], font=(FONT_UI, 11, "bold"),
                 padx=12, pady=8).pack(anchor="w")

        self._mbx_btns: Dict[str, tk.Label] = {}
        for box in self.MAILBOXES:
            count = sum(1 for m in self._messages
                        if m["mailbox"] == box and not m["read"])
            lbl_text = box
            row = tk.Frame(mbx_frame, bg=T["sidebar_bg"], cursor="hand2")
            row.pack(fill="x")
            icon_map = {"Inbox":"📥","Sent":"📤","Drafts":"📝",
                        "Junk":"🚫","Trash":"🗑️","Archive":"📦"}
            tk.Label(row, text=icon_map.get(box,"📁"),
                     bg=T["sidebar_bg"], font=(FONT_EMOJI, 13),
                     padx=8).pack(side="left")
            name_lbl = tk.Label(row, text=lbl_text,
                                bg=T["sidebar_bg"], fg=T["text"],
                                font=(FONT_UI, 13), anchor="w")
            name_lbl.pack(side="left", fill="x", expand=True)
            if count > 0:
                tk.Label(row, text=str(count),
                         bg=T["accent"], fg="#ffffff",
                         font=(FONT_UI, 10),
                         padx=5, pady=1).pack(side="right", padx=6)
            row.bind("<Button-1>", lambda _, b=box: self._switch_mailbox(b))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda _, b=box: self._switch_mailbox(b))
            self._mbx_btns[box] = row

        # Message list + reader
        right = tk.PanedWindow(outer, orient="horizontal",
                               bg=T["separator"], sashwidth=1)
        outer.add(right)

        # Message list
        list_frame = tk.Frame(right, bg=T["panel_bg"], width=280)
        list_frame.pack_propagate(False)
        right.add(list_frame, width=280)

        self._msg_list = tk.Frame(list_frame, bg=T["panel_bg"])
        self._msg_list.pack(fill="both", expand=True)

        # Reader
        reader_frame = tk.Frame(right, bg=T["win_bg"])
        right.add(reader_frame)

        # Header area
        self._msg_header = tk.Frame(reader_frame, bg=T["panel_bg"], pady=12)
        self._msg_header.pack(fill="x")

        self._h_subject = tk.Label(self._msg_header, text="",
                                    bg=T["panel_bg"], fg=T["text"],
                                    font=(FONT_UI, 16, "bold"),
                                    wraplength=420, justify="left",
                                    padx=16)
        self._h_subject.pack(anchor="w")
        self._h_from = tk.Label(self._msg_header, text="",
                                 bg=T["panel_bg"], fg=T["text_muted"],
                                 font=(FONT_UI, 12), padx=16)
        self._h_from.pack(anchor="w")
        self._h_date = tk.Label(self._msg_header, text="",
                                 bg=T["panel_bg"], fg=T["text_muted"],
                                 font=(FONT_UI, 11), padx=16)
        self._h_date.pack(anchor="w")

        tk.Frame(reader_frame, bg=T["separator"], height=1).pack(fill="x")

        self._msg_body = tk.Text(
            reader_frame,
            bg=T["win_bg"], fg=T["text"],
            font=(FONT_UI, 13), relief="flat", bd=0,
            padx=20, pady=16, wrap="word",
            state="disabled",
        )
        self._msg_body.pack(fill="both", expand=True)

        self._switch_mailbox("Inbox")

    def _switch_mailbox(self, box: str) -> None:
        self._current_box = box
        self._current_msg = None
        for w in self._msg_list.winfo_children():
            w.destroy()
        msgs = [m for m in self._messages if m["mailbox"] == box]
        if not msgs:
            tk.Label(self._msg_list, text="No messages",
                     bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 13)).pack(pady=40)
            return
        for i, msg in enumerate(msgs):
            orig_idx = self._messages.index(msg)
            row = tk.Frame(self._msg_list,
                           bg=T["win_bg"] if msg["read"] else T["panel_alt"],
                           cursor="hand2")
            row.pack(fill="x")
            tk.Frame(row, bg=T["separator"], height=1).pack(fill="x")
            inner = tk.Frame(row, bg=row.cget("bg"))
            inner.pack(fill="x", padx=10, pady=6)
            # Unread dot
            dot_color = T["accent"] if not msg["read"] else row.cget("bg")
            tk.Label(inner, text="●", bg=row.cget("bg"),
                     fg=dot_color, font=(FONT_UI, 8)).pack(side="left")
            info = tk.Frame(inner, bg=row.cget("bg"))
            info.pack(side="left", fill="x", expand=True, padx=4)
            sender = msg["from"].split("<")[0].strip()
            tk.Label(info, text=sender, bg=row.cget("bg"),
                     fg=T["text"],
                     font=(FONT_UI, 12, "bold" if not msg["read"] else "normal"),
                     anchor="w").pack(anchor="w")
            tk.Label(info, text=msg["subject"], bg=row.cget("bg"),
                     fg=T["text"], font=(FONT_UI, 11), anchor="w").pack(anchor="w")
            tk.Label(info, text=msg["preview"][:50] + "…",
                     bg=row.cget("bg"), fg=T["text_muted"],
                     font=(FONT_UI, 10), anchor="w").pack(anchor="w")
            tk.Label(inner, text=msg["date"], bg=row.cget("bg"),
                     fg=T["text_muted"], font=(FONT_UI, 10)).pack(side="right", anchor="n")
            if msg.get("starred"):
                tk.Label(inner, text="⭐", bg=row.cget("bg"),
                         font=(FONT_EMOJI, 11)).pack(side="right")

            row.bind("<Button-1>", lambda _, idx=orig_idx: self._open_msg(idx))
            for child in row.winfo_children() + inner.winfo_children() + info.winfo_children():
                child.bind("<Button-1>", lambda _, idx=orig_idx: self._open_msg(idx))

    def _open_msg(self, idx: int) -> None:
        self._current_msg = idx
        msg = self._messages[idx]
        msg["read"] = True
        self._h_subject.configure(text=msg["subject"])
        self._h_from.configure(text=f"From: {msg['from']}   To: {msg['to']}")
        self._h_date.configure(text=msg["date"])
        self._msg_body.configure(state="normal")
        self._msg_body.delete("1.0", "end")
        self._msg_body.insert("1.0", msg["body"])
        self._msg_body.configure(state="disabled")

    def _get_mail(self) -> None:
        self.wm.notifs.send("Mail", "Inbox is up to date.", icon="📧")

    def _compose(self) -> None:
        ComposeMailDialog(self.wm, self._messages)

    def _reply(self) -> None:
        if self._current_msg is None:
            return
        msg = self._messages[self._current_msg]
        ComposeMailDialog(self.wm, self._messages,
                          to=msg["from"], subject="Re: " + msg["subject"])

    def _delete_msg(self) -> None:
        if self._current_msg is None:
            return
        self._messages[self._current_msg]["mailbox"] = "Trash"
        self._current_msg = None
        self._h_subject.configure(text="")
        self._h_from.configure(text="")
        self._h_date.configure(text="")
        self._msg_body.configure(state="normal")
        self._msg_body.delete("1.0", "end")
        self._msg_body.configure(state="disabled")
        self._switch_mailbox(self._current_box)
        self.wm.notifs.send("Mail", "Message moved to Trash.", icon="🗑️")

    def _search(self, query: str) -> None:
        if not query:
            self._switch_mailbox(self._current_box)
            return
        for w in self._msg_list.winfo_children():
            w.destroy()
        hits = [m for m in self._messages
                if query.lower() in m["subject"].lower() or
                   query.lower() in m["body"].lower() or
                   query.lower() in m["from"].lower()]
        for msg in hits:
            orig_idx = self._messages.index(msg)
            row = tk.Frame(self._msg_list, bg=T["panel_bg"], cursor="hand2")
            row.pack(fill="x")
            tk.Label(row, text=msg["subject"], bg=T["panel_bg"],
                     fg=T["text"], font=(FONT_UI, 12), padx=10, pady=6,
                     anchor="w").pack(anchor="w")
            row.bind("<Button-1>", lambda _, i=orig_idx: self._open_msg(i))


class ComposeMailDialog:
    """Compose new mail dialog."""

    def __init__(self, wm: "WM", messages: List[Dict],
                 to: str = "", subject: str = "") -> None:
        self.wm       = wm
        self.messages = messages
        dlg = tk.Toplevel(wm.root)
        dlg.title("New Message")
        dlg.geometry("560x440")
        dlg.configure(bg=T["win_bg"])
        dlg.transient(wm.root)

        tb = tk.Frame(dlg, bg=T["panel_bg"], pady=6)
        tb.pack(fill="x")
        tk.Label(tb, text="New Message", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 13, "bold"),
                 padx=12).pack(side="left")
        tk.Button(tb, text="Send ✈️",
                  bg=T["accent"], fg="#ffffff",
                  font=(FONT_UI, 12), relief="flat",
                  padx=12, command=lambda: self._send(dlg, to_e, sub_e, body_t)
                  ).pack(side="right", padx=8)

        for label, default in [("To:", to), ("Cc:", ""), ("Subject:", subject)]:
            row = tk.Frame(dlg, bg=T["win_bg"])
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=label, bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 12), width=8, anchor="e").pack(side="left")
            e = tk.Entry(row, bg=T["input_bg"], fg=T["text"],
                         font=(FONT_UI, 13), relief="flat",
                         highlightthickness=1,
                         highlightbackground=T["input_border"])
            e.pack(side="left", fill="x", expand=True, padx=4)
            e.insert(0, default)
            if "To" in label:   to_e  = e
            if "Subject" in label: sub_e = e

        tk.Frame(dlg, bg=T["separator"], height=1).pack(fill="x", padx=12)

        body_t = tk.Text(dlg, bg=T["win_bg"], fg=T["text"],
                         font=(FONT_UI, 13), relief="flat", bd=0,
                         padx=16, pady=12, wrap="word",
                         insertbackground=T["text"])
        body_t.pack(fill="both", expand=True)
        body_t.focus_set()

    def _send(self, dlg: tk.Toplevel, to_e: tk.Entry,
              sub_e: tk.Entry, body_t: tk.Text) -> None:
        to      = to_e.get().strip()
        subject = sub_e.get().strip() or "(No Subject)"
        body    = body_t.get("1.0", "end-1c")
        if not to:
            messagebox.showwarning("No Recipient",
                                   "Please enter a recipient.", parent=dlg)
            return
        self.messages.append({
            "from":    "user@macpyos.local",
            "to":      to,
            "subject": subject,
            "date":    datetime.datetime.now().strftime("%b %d, %I:%M %p"),
            "preview": body[:60],
            "body":    body,
            "read":    True,
            "starred": False,
            "mailbox": "Sent",
        })
        self.wm.notifs.send("Mail", f"Message sent to {to}", icon="✈️")
        dlg.destroy()



# =============================================================================
#  MacPyOS — PART 3
#  Clock, Activity Monitor, Notes, Mail
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 26 — CLOCK APP
# ─────────────────────────────────────────────────────────────────────────────

class ClockApp(BaseWin):
    """macOS Clock with World Clock, Alarm, Stopwatch, Timer tabs."""

    WORLD_CLOCKS = [
        ("US", "New York",    -5),
        ("GB", "London",       0),
        ("FR", "Paris",        1),
        ("DE", "Berlin",       1),
        ("JP", "Tokyo",        9),
        ("CN", "Shanghai",     8),
        ("AU", "Sydney",      10),
        ("IN", "Mumbai",     5.5),
        ("BR", "Sao Paulo",   -3),
        ("CA", "Vancouver",   -8),
        ("AE", "Dubai",        4),
        ("SG", "Singapore",    8),
    ]

    def __init__(self, wm):
        super().__init__(wm, title="Clock", w=460, h=520, icon="clock")
        self._tab = "world"
        self._running = False
        self._sw_start = None
        self._sw_elapsed = 0.0
        self._sw_laps = []
        self._timer_running = False
        self._timer_end = None
        self._alarms = []
        self._build_ui()
        self._tick()

    def _build_ui(self):
        c = self.client
        tab_bar = tk.Frame(c, bg=T["panel_bg"],
                           highlightthickness=1, highlightbackground=T["separator"])
        tab_bar.pack(fill="x")
        self._tab_btns = {}
        for key, label in [("world","World Clock"),("alarm","Alarm"),
                            ("stopwatch","Stopwatch"),("timer","Timer")]:
            btn = tk.Label(tab_bar, text=label, bg=T["panel_bg"],
                           fg=T["text_muted"], font=(FONT_UI,12),
                           padx=14, pady=6, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda _, k=key: self._switch_tab(k))
            self._tab_btns[key] = btn
        self._content = tk.Frame(c, bg=T["win_bg"])
        self._content.pack(fill="both", expand=True)
        self._switch_tab("world")

    def _switch_tab(self, key):
        self._tab = key
        for k, b in self._tab_btns.items():
            b.configure(bg=T["accent"] if k==key else T["panel_bg"],
                        fg="#ffffff" if k==key else T["text_muted"])
        for w in self._content.winfo_children():
            w.destroy()
        {"world":self._build_world,"alarm":self._build_alarm,
         "stopwatch":self._build_stopwatch,"timer":self._build_timer}[key]()

    def _build_world(self):
        f = self._content
        self._clock_canvas = tk.Canvas(f, width=180, height=180,
                                       bg=T["win_bg"], highlightthickness=0)
        self._clock_canvas.pack(pady=12)
        self._draw_analog()
        tk.Frame(f, bg=T["separator"], height=1).pack(fill="x")
        sf = MacScrolledFrame(f, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner
        inner.configure(bg=T["win_bg"])
        now_utc = datetime.datetime.utcnow()
        for cc, city, offset in self.WORLD_CLOCKS:
            local_time = now_utc + datetime.timedelta(hours=offset)
            time_str = local_time.strftime("%I:%M %p")
            date_str = local_time.strftime("%a, %b %d")
            row = tk.Frame(inner, bg=T["win_bg"],
                           highlightthickness=1, highlightbackground=T["separator"])
            row.pack(fill="x", padx=12, pady=2)
            tk.Label(row, text=cc, bg=T["win_bg"],
                     font=(FONT_UI,14), padx=8, fg=T["text_muted"]).pack(side="left")
            info = tk.Frame(row, bg=T["win_bg"])
            info.pack(side="left", fill="x", expand=True, pady=4)
            tk.Label(info, text=city, bg=T["win_bg"], fg=T["text"],
                     font=(FONT_UI,13,"bold"), anchor="w").pack(anchor="w")
            tk.Label(info, text=date_str, bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI,11), anchor="w").pack(anchor="w")
            tk.Label(row, text=time_str, bg=T["win_bg"], fg=T["text"],
                     font=(FONT_UI,16), padx=12).pack(side="right")

    def _draw_analog(self):
        cv = self._clock_canvas
        cv.delete("all")
        cx, cy, r = 90, 90, 80
        cv.create_oval(cx-r, cy-r, cx+r, cy+r,
                       fill=T["panel_bg"], outline=T["separator"], width=2)
        for i in range(12):
            angle = math.radians(i*30-90)
            r1=r-6; r2=r-12
            x1=cx+r1*math.cos(angle); y1=cy+r1*math.sin(angle)
            x2=cx+r2*math.cos(angle); y2=cy+r2*math.sin(angle)
            cv.create_line(x1,y1,x2,y2,fill=T["text"],width=2)
        now = datetime.datetime.now()
        h,m,s = now.hour%12, now.minute, now.second
        def hand(length, angle_deg, color, width):
            angle = math.radians(angle_deg-90)
            ex=cx+length*math.cos(angle); ey=cy+length*math.sin(angle)
            cv.create_line(cx,cy,ex,ey,fill=color,width=width,capstyle="round")
        hand(45,(h*30)+(m*0.5),T["text"],4)
        hand(60,m*6,T["text"],3)
        hand(68,s*6,T["danger"],2)
        cv.create_oval(cx-4,cy-4,cx+4,cy+4,fill=T["danger"],outline="")

    def _build_alarm(self):
        f = self._content
        tk.Label(f,text="Alarms",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,16,"bold"),pady=12).pack()
        add_frame = tk.Frame(f,bg=T["panel_bg"],
                             highlightthickness=1,highlightbackground=T["separator"])
        add_frame.pack(fill="x",padx=16,pady=4)
        tk.Label(add_frame,text="Add:",bg=T["panel_bg"],fg=T["text"],
                 font=(FONT_UI,12)).pack(side="left",padx=8)
        self._alarm_hour = tk.Spinbox(add_frame,from_=0,to=23,width=3,
                                      bg=T["input_bg"],fg=T["text"],
                                      font=(FONT_UI,12),relief="flat")
        self._alarm_hour.pack(side="left",padx=2)
        tk.Label(add_frame,text=":",bg=T["panel_bg"],fg=T["text"],
                 font=(FONT_UI,12)).pack(side="left")
        self._alarm_min = tk.Spinbox(add_frame,from_=0,to=59,width=3,
                                     bg=T["input_bg"],fg=T["text"],
                                     font=(FONT_UI,12),relief="flat")
        self._alarm_min.pack(side="left",padx=2)
        self._alarm_label_var = tk.StringVar(value="Alarm")
        tk.Entry(add_frame,textvariable=self._alarm_label_var,
                 bg=T["input_bg"],fg=T["text"],
                 font=(FONT_UI,12),width=10,relief="flat").pack(side="left",padx=4)
        tk.Button(add_frame,text="Add",bg=T["accent"],fg="#ffffff",
                  font=(FONT_UI,12),relief="flat",
                  command=self._add_alarm).pack(side="left",padx=8,pady=4)
        self._alarm_list = tk.Frame(f,bg=T["win_bg"])
        self._alarm_list.pack(fill="both",expand=True,padx=16,pady=4)
        self._refresh_alarms()

    def _add_alarm(self):
        h=int(self._alarm_hour.get()); m=int(self._alarm_min.get())
        lbl=self._alarm_label_var.get() or "Alarm"
        self._alarms.append({"hour":h,"minute":m,"label":lbl,"active":True})
        self._refresh_alarms()

    def _refresh_alarms(self):
        for w in self._alarm_list.winfo_children():
            w.destroy()
        if not self._alarms:
            tk.Label(self._alarm_list,text="No alarms",bg=T["win_bg"],
                     fg=T["text_muted"],font=(FONT_UI,13)).pack(pady=20)
            return
        for i, alarm in enumerate(self._alarms):
            row = tk.Frame(self._alarm_list,bg=T["panel_bg"],
                           highlightthickness=1,highlightbackground=T["separator"])
            row.pack(fill="x",pady=2)
            time_str = f"{alarm['hour']:02d}:{alarm['minute']:02d}"
            tk.Label(row,text=time_str,bg=T["panel_bg"],fg=T["text"],
                     font=(FONT_UI,22),padx=12).pack(side="left")
            info = tk.Frame(row,bg=T["panel_bg"])
            info.pack(side="left",fill="x",expand=True,pady=4)
            tk.Label(info,text=alarm["label"],bg=T["panel_bg"],fg=T["text"],
                     font=(FONT_UI,13,"bold"),anchor="w").pack(anchor="w")
            tk.Label(info,text="Every Day",bg=T["panel_bg"],fg=T["text_muted"],
                     font=(FONT_UI,11)).pack(anchor="w")
            var = tk.BooleanVar(value=alarm["active"])
            def toggle(v=var, a=alarm): a["active"] = v.get()
            tk.Checkbutton(row,variable=var,command=toggle,
                           bg=T["panel_bg"]).pack(side="right",padx=4)
            tk.Button(row,text="X",bg=T["panel_bg"],fg=T["danger"],
                      font=(FONT_UI,12),relief="flat",cursor="hand2",
                      command=lambda idx=i: (self._alarms.pop(idx),self._refresh_alarms())
                      ).pack(side="right",padx=4)

    def _build_stopwatch(self):
        f = self._content
        self._sw_display = tk.Label(f,text="00:00.00",bg=T["win_bg"],
                                    fg=T["text"],font=(FONT_MONO,48))
        self._sw_display.pack(pady=30)
        btn_frame = tk.Frame(f,bg=T["win_bg"])
        btn_frame.pack()
        self._sw_start_btn = tk.Button(btn_frame,text="Start",
                                       bg=T["accent3"],fg="#ffffff",
                                       font=(FONT_UI,16),relief="flat",
                                       width=8,cursor="hand2",command=self._sw_toggle)
        self._sw_start_btn.pack(side="left",padx=8)
        tk.Button(btn_frame,text="Lap",bg=T["button_secondary"],fg=T["text"],
                  font=(FONT_UI,16),relief="flat",width=8,cursor="hand2",
                  command=self._sw_lap).pack(side="left",padx=8)
        tk.Button(btn_frame,text="Reset",bg=T["button_secondary"],fg=T["text"],
                  font=(FONT_UI,16),relief="flat",width=8,cursor="hand2",
                  command=self._sw_reset).pack(side="left",padx=8)
        self._sw_lap_frame = tk.Frame(f,bg=T["win_bg"])
        self._sw_lap_frame.pack(fill="both",expand=True,padx=20,pady=10)

    def _sw_toggle(self):
        if self._running:
            self._sw_elapsed += time.time()-self._sw_start
            self._running = False
            self._sw_start_btn.configure(text="Start",bg=T["accent3"])
        else:
            self._sw_start = time.time()
            self._running = True
            self._sw_start_btn.configure(text="Stop",bg=T["danger"])

    def _sw_lap(self):
        if self._running:
            elapsed = self._sw_elapsed+(time.time()-self._sw_start)
            self._sw_laps.append(elapsed)
            for w in self._sw_lap_frame.winfo_children(): w.destroy()
            for i, lap in enumerate(reversed(self._sw_laps[-10:])):
                m,s = divmod(lap,60)
                lap_str = f"Lap {len(self._sw_laps)-i}   {int(m):02d}:{s:05.2f}"
                tk.Label(self._sw_lap_frame,text=lap_str,
                         bg=T["panel_bg"],fg=T["text"],
                         font=(FONT_MONO,13),anchor="w",
                         padx=10,pady=3).pack(fill="x",pady=1)

    def _sw_reset(self):
        self._running = False; self._sw_elapsed = 0.0; self._sw_laps.clear()
        self._sw_start_btn.configure(text="Start",bg=T["accent3"])
        if hasattr(self,"_sw_display"): self._sw_display.configure(text="00:00.00")
        for w in self._sw_lap_frame.winfo_children(): w.destroy()

    def _build_timer(self):
        f = self._content
        tk.Label(f,text="Set Timer",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,16,"bold"),pady=12).pack()
        spin_frame = tk.Frame(f,bg=T["win_bg"])
        spin_frame.pack()
        for label, var_name, max_val in [("Hours","_t_hours",23),
                                          ("Minutes","_t_minutes",59),
                                          ("Seconds","_t_seconds",59)]:
            col = tk.Frame(spin_frame,bg=T["win_bg"])
            col.pack(side="left",padx=12)
            spin = tk.Spinbox(col,from_=0,to=max_val,width=4,
                              bg=T["input_bg"],fg=T["text"],
                              font=(FONT_UI,36),relief="flat",justify="center")
            spin.pack()
            tk.Label(col,text=label,bg=T["win_bg"],fg=T["text_muted"],
                     font=(FONT_UI,11)).pack()
            setattr(self,var_name,spin)
        self._timer_display = tk.Label(f,text="",bg=T["win_bg"],
                                       fg=T["accent"],font=(FONT_MONO,48))
        self._timer_display.pack(pady=10)
        btn_frame = tk.Frame(f,bg=T["win_bg"])
        btn_frame.pack()
        self._timer_btn = tk.Button(btn_frame,text="Start",
                                    bg=T["accent"],fg="#ffffff",
                                    font=(FONT_UI,16),relief="flat",
                                    width=10,cursor="hand2",command=self._timer_toggle)
        self._timer_btn.pack(side="left",padx=8)
        tk.Button(btn_frame,text="Cancel",bg=T["button_secondary"],fg=T["text"],
                  font=(FONT_UI,16),relief="flat",width=10,cursor="hand2",
                  command=self._timer_cancel).pack(side="left",padx=8)

    def _timer_toggle(self):
        if self._timer_running:
            self._timer_running = False
            self._timer_btn.configure(text="Resume",bg=T["accent"])
        else:
            if not self._timer_end:
                h=int(self._t_hours.get()); m=int(self._t_minutes.get()); s=int(self._t_seconds.get())
                total = h*3600+m*60+s
                if total <= 0: return
                self._timer_end = time.time()+total
            self._timer_running = True
            self._timer_btn.configure(text="Pause",bg=T["warning"])

    def _timer_cancel(self):
        self._timer_running = False; self._timer_end = None
        if hasattr(self,"_timer_display"): self._timer_display.configure(text="")
        if hasattr(self,"_timer_btn"): self._timer_btn.configure(text="Start",bg=T["accent"])

    def _tick(self):
        if self._closed: return
        if self._tab=="world" and hasattr(self,"_clock_canvas"):
            self._draw_analog()
        if self._tab=="stopwatch" and hasattr(self,"_sw_display"):
            elapsed = (self._sw_elapsed+(time.time()-self._sw_start)) if self._running else self._sw_elapsed
            m,s = divmod(elapsed,60)
            self._sw_display.configure(text=f"{int(m):02d}:{s:05.2f}")
        if self._tab=="timer" and hasattr(self,"_timer_display"):
            if self._timer_running and self._timer_end:
                remaining = max(0,self._timer_end-time.time())
                h,rem = divmod(int(remaining),3600); m,s = divmod(rem,60)
                self._timer_display.configure(
                    text=f"{h:02d}:{m:02d}:{s:02d}",
                    fg=T["danger"] if remaining<10 else T["accent"])
                if remaining<=0:
                    self._timer_running=False; self._timer_end=None
                    self.wm.notifs.send("Clock","Timer finished!",icon="clock")
                    if hasattr(self,"_timer_btn"): self._timer_btn.configure(text="Start",bg=T["accent"])
        now = datetime.datetime.now()
        for alarm in self._alarms:
            if alarm["active"] and alarm["hour"]==now.hour and alarm["minute"]==now.minute and now.second==0:
                self.wm.notifs.send("Clock",f"Alarm: {alarm['label']}",icon="clock")
        self.wm.root.after(100,self._tick)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 27 — ACTIVITY MONITOR
# ─────────────────────────────────────────────────────────────────────────────

class ActivityMonitorApp(BaseWin):
    """macOS Activity Monitor."""

    def __init__(self, wm):
        super().__init__(wm,title="Activity Monitor",w=720,h=540,icon="chart")
        self._tab = "cpu"
        self._cpu_history = [0.0]*60
        self._ram_history = [0.0]*60
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        c = self.client
        toolbar = tk.Frame(c,bg=T["panel_bg"],
                           highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        self._tab_btns = {}
        for key,label in [("cpu","CPU"),("memory","Memory"),
                           ("energy","Energy"),("disk","Disk"),("network","Network")]:
            btn = tk.Label(toolbar,text=label,bg=T["panel_bg"],
                           fg=T["text_muted"],font=(FONT_UI,12),
                           padx=14,pady=6,cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>",lambda _,k=key: self._switch(k))
            self._tab_btns[key] = btn
        self._search_var = tk.StringVar()
        se = tk.Entry(toolbar,textvariable=self._search_var,
                      bg=T["input_bg"],fg=T["text"],font=(FONT_UI,12),
                      relief="flat",highlightthickness=1,
                      highlightbackground=T["input_border"],
                      highlightcolor=T["input_focus"],width=16)
        se.pack(side="right",padx=8,pady=4)
        tk.Label(toolbar,text="Search",bg=T["panel_bg"],fg=T["text_muted"],
                 font=(FONT_UI,11)).pack(side="right")
        self._search_var.trace_add("write",lambda *_: self._refresh_table())
        self._content = tk.Frame(c,bg=T["win_bg"])
        self._content.pack(fill="both",expand=True)
        self._summary = tk.Frame(c,bg=T["panel_bg"],
                                  highlightthickness=1,highlightbackground=T["separator"])
        self._summary.pack(fill="x")
        self._summary_labels = {}
        for key in ["cpu_lbl","threads","procs","ram_lbl","ram_used"]:
            lbl = tk.Label(self._summary,text="",bg=T["panel_bg"],
                           fg=T["text_muted"],font=(FONT_UI,11),padx=12)
            lbl.pack(side="left")
            self._summary_labels[key] = lbl
        self._switch("cpu")

    def _switch(self,tab):
        self._tab = tab
        for k,b in self._tab_btns.items():
            b.configure(bg=T["accent"] if k==tab else T["panel_bg"],
                        fg="#ffffff" if k==tab else T["text_muted"])
        for w in self._content.winfo_children(): w.destroy()
        if tab in ("cpu","memory","energy"): self._build_process_table(tab)
        elif tab=="disk": self._build_disk_tab()
        elif tab=="network": self._build_network_tab()

    def _build_process_table(self,tab):
        f = self._content
        chart_frame = tk.Frame(f,bg=T["panel_bg"],height=120)
        chart_frame.pack(fill="x"); chart_frame.pack_propagate(False)
        self._chart_cv = tk.Canvas(chart_frame,bg=T["panel_bg"],
                                    height=120,highlightthickness=0)
        self._chart_cv.pack(fill="both",expand=True,padx=8,pady=4)
        headers = tk.Frame(f,bg=T["panel_alt"],
                           highlightthickness=1,highlightbackground=T["separator"])
        headers.pack(fill="x")
        for col_name, width in [("Process Name",200),("PID",60),
                                  ("% CPU",80),("Threads",70),("RAM (MB)",90)]:
            tk.Label(headers,text=col_name,bg=T["panel_alt"],fg=T["text_muted"],
                     font=(FONT_UI,11,"bold"),width=width//7,padx=4).pack(side="left")
        self._proc_frame = MacScrolledFrame(f,bg=T["win_bg"])
        self._proc_frame.pack(fill="both",expand=True)
        self._proc_inner = self._proc_frame.inner
        self._proc_inner.configure(bg=T["win_bg"])
        self._refresh_table()

    def _refresh_table(self):
        if not hasattr(self,"_proc_inner"): return
        for w in self._proc_inner.winfo_children(): w.destroy()
        query = self._search_var.get().lower() if hasattr(self,"_search_var") else ""
        procs = self.wm.procs.list_all()
        procs.sort(key=lambda p: p.cpu,reverse=True)
        for i,p in enumerate(procs[:60]):
            if query and query not in p.name.lower(): continue
            row_bg = T["win_bg"] if i%2==0 else T["panel_bg"]
            row = tk.Frame(self._proc_inner,bg=row_bg,cursor="hand2")
            row.pack(fill="x")
            row.bind("<Button-1>",lambda _,proc=p: self._select_proc(proc))
            cpu_color = T["danger"] if p.cpu>50 else (T["warning"] if p.cpu>20 else T["text"])
            vals = [(p.name[:28],200,"w",T["text"]),(str(p.pid),60,"center",T["text_muted"]),
                    (f"{p.cpu:.1f}",80,"e",cpu_color),(str(random.randint(1,12)),70,"e",T["text_muted"]),
                    (f"{p.ram:.1f}",90,"e",T["text_muted"])]
            for val, width, anchor, fg in vals:
                tk.Label(row,text=val,bg=row_bg,fg=fg,font=(FONT_UI,12),
                         width=width//7,anchor=anchor,padx=4).pack(side="left")
        if hasattr(self,"_chart_cv"): self._draw_chart()

    def _select_proc(self,p):
        msg = f"Process: {p.name}\nPID: {p.pid}\nCPU: {p.cpu:.1f}%\nRAM: {p.ram:.1f} MB\nUser: {p.user}"
        if messagebox.askyesno("Process Info",f"{msg}\n\nForce quit?",parent=self.wm.root):
            self.wm.procs.kill(p.pid); self._refresh_table()

    def _draw_chart(self):
        cv = self._chart_cv; cv.delete("all")
        w = cv.winfo_width() or 400; h = 110
        for i in range(0,101,25):
            y = h-(i/100*h)
            cv.create_line(0,y,w,y,fill=T["separator"],dash=(2,4))
            cv.create_text(4,y,text=f"{i}%",anchor="w",fill=T["text_muted"],font=(FONT_UI,9))
        hist = self._cpu_history[-50:]
        if len(hist)>1:
            step = w/(len(hist)-1)
            pts = [(i*step,h-(v/100*h)) for i,v in enumerate(hist)]
            poly_pts = [0,h]+[c for p in pts for c in p]+[w,h]
            cv.create_polygon(poly_pts,fill=T["chart1"]+"44",outline="")
            for i in range(len(pts)-1):
                cv.create_line(*pts[i],*pts[i+1],fill=T["chart1"],width=2)
        cv.create_text(w-4,8,text=f"CPU: {self._cpu_history[-1]:.1f}%",
                       anchor="e",fill=T["chart1"],font=(FONT_UI,11,"bold"))

    def _build_disk_tab(self):
        f = self._content
        tk.Label(f,text="Disk Activity",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,16,"bold"),pady=12).pack()
        for label,used,total,color in [("MacPyOS SSD",128,512,T["chart1"]),
                                        ("Backup Drive",320,1000,T["chart2"])]:
            row = tk.Frame(f,bg=T["win_bg"])
            row.pack(fill="x",padx=24,pady=8)
            tk.Label(row,text=label,bg=T["win_bg"],fg=T["text"],
                     font=(FONT_UI,13),anchor="w").pack(anchor="w")
            bar_bg = tk.Frame(row,bg=T["progress_bg"],height=14)
            bar_bg.pack(fill="x",pady=2); bar_bg.update_idletasks()
            pct = used/total
            bar_fg = tk.Frame(bar_bg,bg=color,height=14)
            bar_fg.place(x=0,y=0,relwidth=pct,height=14)
            tk.Label(row,text=f"{used} GB used of {total} GB",
                     bg=T["win_bg"],fg=T["text_muted"],font=(FONT_UI,11)).pack(anchor="w")

    def _build_network_tab(self):
        f = self._content
        tk.Label(f,text="Network",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,16,"bold"),pady=12).pack()
        for label,val in [("Interface:","en0 (Wi-Fi)"),
                           ("Packets in:",f"{random.randint(1000,9999):,}"),
                           ("Packets out:",f"{random.randint(500,5000):,}"),
                           ("Data received:",f"{random.uniform(10,200):.1f} MB"),
                           ("Data sent:",f"{random.uniform(5,100):.1f} MB"),
                           ("IP Address:","192.168.1."+str(random.randint(2,254))),
                           ("Router:","192.168.1.1")]:
            row = tk.Frame(f,bg=T["win_bg"])
            row.pack(fill="x",padx=24,pady=3)
            tk.Label(row,text=label,bg=T["win_bg"],fg=T["text_muted"],
                     font=(FONT_UI,12),width=18,anchor="w").pack(side="left")
            tk.Label(row,text=val,bg=T["win_bg"],fg=T["text"],
                     font=(FONT_UI,12)).pack(side="left")

    def _refresh(self):
        if self._closed: return
        cpu = self.wm.procs.total_cpu(); ram = self.wm.procs.total_ram()
        self._cpu_history.append(cpu); self._cpu_history = self._cpu_history[-60:]
        self._ram_history.append(ram); self._ram_history = self._ram_history[-60:]
        procs = self.wm.procs.list_all(); n = len(procs)
        if "procs" in self._summary_labels:
            self._summary_labels["procs"].configure(text=f"Processes: {n}")
            self._summary_labels["cpu_lbl"].configure(text=f"CPU: {cpu:.1f}%")
            self._summary_labels["ram_lbl"].configure(text=f"RAM: {ram:.0f} MB")
        if self._tab in ("cpu","memory","energy"): self._refresh_table()
        self.wm.root.after(2000,self._refresh)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 28 — NOTES APP
# ─────────────────────────────────────────────────────────────────────────────

class NotesApp(BaseWin):
    """macOS Notes — sidebar + editor."""

    def __init__(self, wm):
        super().__init__(wm,title="Notes",w=700,h=520,icon="notes")
        self._notes = [
            {"title":"Welcome to Notes","body":"Start writing your thoughts here.\n\nNotes saves as you type.","ts":time.time()-3600},
            {"title":"Shopping List","body":"- Apples\n- Bread\n- Milk\n- Coffee\n- Eggs","ts":time.time()-7200},
            {"title":"Project Ideas","body":"1. Build a macOS sim in Python\n2. Learn SwiftUI\n3. Write a blog post","ts":time.time()-86400},
            {"title":"Meeting Notes","body":"Q2 Planning - Jan 15\n\n- Review roadmap\n- Assign tasks\n- Follow up Friday","ts":time.time()-172800},
        ]
        self._current_idx = None
        self._build_ui()

    def _build_ui(self):
        c = self.client
        pane = tk.Frame(c,bg=T["win_bg"])
        pane.pack(fill="both",expand=True)
        sidebar = tk.Frame(pane,bg=T["sidebar_bg"],width=220)
        sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
        sidebar_tb = tk.Frame(sidebar,bg=T["sidebar_bg"])
        sidebar_tb.pack(fill="x")
        tk.Label(sidebar_tb,text="Notes",bg=T["sidebar_bg"],fg=T["text"],
                 font=(FONT_UI,14,"bold"),padx=12,pady=8).pack(side="left")
        new_btn = tk.Label(sidebar_tb,text="+",bg=T["sidebar_bg"],fg=T["accent"],
                           font=(FONT_UI,20),cursor="hand2",padx=8)
        new_btn.pack(side="right")
        new_btn.bind("<Button-1>",lambda _: self._new_note())
        self._search_var = tk.StringVar()
        se = tk.Entry(sidebar,textvariable=self._search_var,
                      bg=T["input_bg"],fg=T["text"],font=(FONT_UI,12),
                      relief="flat",highlightthickness=1,
                      highlightbackground=T["input_border"],
                      highlightcolor=T["input_focus"])
        se.pack(fill="x",padx=8,pady=4)
        self._search_var.trace_add("write",lambda *_: self._refresh_list())
        tk.Frame(sidebar,bg=T["separator"],height=1).pack(fill="x")
        self._list_frame = MacScrolledFrame(sidebar,bg=T["sidebar_bg"])
        self._list_frame.pack(fill="both",expand=True)
        self._list_inner = self._list_frame.inner
        self._list_inner.configure(bg=T["sidebar_bg"])
        tk.Frame(pane,bg=T["separator"],width=1).pack(side="left",fill="y")
        editor_pane = tk.Frame(pane,bg=T["win_bg"])
        editor_pane.pack(side="left",fill="both",expand=True)
        editor_tb = tk.Frame(editor_pane,bg=T["panel_bg"],
                             highlightthickness=1,highlightbackground=T["separator"])
        editor_tb.pack(fill="x")
        for sym,tip,fn in [("B","Bold",self._toggle_bold),("I","Italic",self._toggle_italic),
                            ("*","List",self._insert_list)]:
            b = tk.Label(editor_tb,text=sym,bg=T["panel_bg"],fg=T["text"],
                         font=(FONT_UI,13),padx=8,pady=4,cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>",lambda _,f=fn: f())
            make_tooltip(b,tip)
        del_btn = tk.Label(editor_tb,text="Delete",bg=T["panel_bg"],fg=T["danger"],
                           font=(FONT_UI,11),padx=8,cursor="hand2")
        del_btn.pack(side="right")
        del_btn.bind("<Button-1>",lambda _: self._delete_note())
        self._title_var = tk.StringVar()
        title_entry = tk.Entry(editor_pane,textvariable=self._title_var,
                               bg=T["win_bg"],fg=T["text"],
                               font=(FONT_UI,18,"bold"),
                               relief="flat",insertbackground=T["text"],
                               highlightthickness=0)
        title_entry.pack(fill="x",padx=16,pady=(12,4))
        self._title_var.trace_add("write",lambda *_: self._save_current())
        tk.Frame(editor_pane,bg=T["separator"],height=1).pack(fill="x",padx=16)
        self._body_text = tk.Text(editor_pane,bg=T["win_bg"],fg=T["text"],
                                   font=(FONT_UI,14),relief="flat",
                                   insertbackground=T["text"],wrap="word",
                                   padx=16,pady=8,
                                   selectbackground=T["selection"],
                                   highlightthickness=0)
        self._body_text.pack(fill="both",expand=True)
        self._body_text.bind("<KeyRelease>",lambda _: self._save_current())
        self._refresh_list()
        if self._notes: self._open_note(0)

    def _refresh_list(self):
        for w in self._list_inner.winfo_children(): w.destroy()
        q = self._search_var.get().lower()
        for i,note in enumerate(self._notes):
            if q and q not in note["title"].lower() and q not in note["body"].lower(): continue
            is_sel = (i==self._current_idx)
            bg = T["accent"] if is_sel else T["sidebar_bg"]
            fg = "#ffffff" if is_sel else T["text"]
            fg_m = "#ffffff" if is_sel else T["text_muted"]
            row = tk.Frame(self._list_inner,bg=bg,cursor="hand2")
            row.pack(fill="x",pady=1)
            row.bind("<Button-1>",lambda _,idx=i: self._open_note(idx))
            preview = note["body"].replace("\n"," ")[:40]
            ts = datetime.datetime.fromtimestamp(note["ts"]).strftime("%m/%d/%y")
            tk.Label(row,text=note["title"][:24],bg=bg,fg=fg,
                     font=(FONT_UI,12,"bold"),anchor="w",padx=10,pady=4).pack(anchor="w")
            sub = tk.Frame(row,bg=bg); sub.pack(fill="x",padx=10,pady=(0,4))
            tk.Label(sub,text=ts,bg=bg,fg=fg_m,font=(FONT_UI,10)).pack(side="left")
            tk.Label(sub,text="  "+preview,bg=bg,fg=fg_m,font=(FONT_UI,10)).pack(side="left")
            for child in row.winfo_children():
                child.bind("<Button-1>",lambda _,idx=i: self._open_note(idx))

    def _open_note(self,idx):
        self._current_idx = idx
        note = self._notes[idx]
        self._title_var.set(note["title"])
        self._body_text.delete("1.0","end")
        self._body_text.insert("1.0",note["body"])
        self._refresh_list()

    def _save_current(self):
        if self._current_idx is None: return
        self._notes[self._current_idx]["title"] = self._title_var.get()
        self._notes[self._current_idx]["body"]  = self._body_text.get("1.0","end-1c")
        self._notes[self._current_idx]["ts"]    = time.time()

    def _new_note(self):
        self._notes.insert(0,{"title":"New Note","body":"","ts":time.time()})
        self._current_idx = 0
        self._refresh_list(); self._open_note(0)

    def _delete_note(self):
        if self._current_idx is None: return
        if messagebox.askyesno("Delete Note",
                                f"Delete '{self._notes[self._current_idx]['title']}'?",
                                parent=self.wm.root):
            self._notes.pop(self._current_idx); self._current_idx = None
            self._title_var.set(""); self._body_text.delete("1.0","end")
            self._refresh_list()

    def _toggle_bold(self):
        try:
            sel = self._body_text.tag_ranges("sel")
            if sel:
                if "bold" in self._body_text.tag_names(sel[0]):
                    self._body_text.tag_remove("bold",*sel)
                else:
                    self._body_text.tag_add("bold",*sel)
                    self._body_text.tag_configure("bold",font=(FONT_UI,14,"bold"))
        except Exception: pass

    def _toggle_italic(self):
        try:
            sel = self._body_text.tag_ranges("sel")
            if sel:
                if "italic" in self._body_text.tag_names(sel[0]):
                    self._body_text.tag_remove("italic",*sel)
                else:
                    self._body_text.tag_add("italic",*sel)
                    self._body_text.tag_configure("italic",font=(FONT_UI,14,"italic"))
        except Exception: pass

    def _insert_list(self):
        self._body_text.insert("insert","\n- ")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 29 — MAIL APP
# ─────────────────────────────────────────────────────────────────────────────

class MailApp(BaseWin):
    """macOS Mail."""

    SAMPLE = [
        {"from":"apple@apple.com","to":"user@macpyos.local","subject":"Your Apple ID was used to sign in",
         "body":"Dear User,\n\nYour Apple ID was used to sign in to MacPyOS.\n\nIf this was you, no action is required.\n\nBest,\nApple","ts":time.time()-300,"read":False,"starred":False},
        {"from":"team@github.com","to":"user@macpyos.local","subject":"Pull request #42 merged",
         "body":"Your pull request 'Add macOS theme' has been merged into main.","ts":time.time()-3600,"read":True,"starred":True},
        {"from":"noreply@notion.so","to":"user@macpyos.local","subject":"Weekly digest - 5 updates",
         "body":"Here is what happened in your workspace:\n\n- 3 pages edited\n- 2 comments\n- 1 new member","ts":time.time()-86400,"read":True,"starred":False},
        {"from":"boss@company.com","to":"user@macpyos.local","subject":"Q2 Planning - action required",
         "body":"Hi,\n\nPlease review the Q2 doc before Friday.\n\nThanks","ts":time.time()-172800,"read":False,"starred":True},
        {"from":"newsletter@medium.com","to":"user@macpyos.local","subject":"5 Python tips",
         "body":"This week in Python:\n1. Use dataclasses\n2. Type hints\n3. f-strings\n4. itertools\n5. asyncio","ts":time.time()-259200,"read":True,"starred":False},
    ]

    def __init__(self, wm):
        super().__init__(wm,title="Mail",w=840,h=560,icon="mail")
        self._emails = [dict(e) for e in self.SAMPLE]
        self._selected = None; self._folder = "Inbox"
        self._build_ui()

    def _build_ui(self):
        c = self.client
        toolbar = tk.Frame(c,bg=T["panel_bg"],
                           highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        def tb_btn(text,cmd,tip=""):
            b = tk.Label(toolbar,text=text,bg=T["panel_bg"],fg=T["text"],
                         font=(FONT_UI,13),padx=8,pady=5,cursor="hand2")
            b.pack(side="left"); b.bind("<Button-1>",lambda _: cmd())
            if tip: make_tooltip(b,tip)
            return b
        tb_btn("Compose",self._compose,"New message")
        tb_btn("Reply",lambda: None,"Reply")
        tb_btn("Delete",self._delete_selected,"Delete")
        tb_btn("Flag",self._star_selected,"Flag")
        tb_btn("Mark Read",self._mark_read,"Mark as read")
        self._search_var = tk.StringVar()
        se = tk.Entry(toolbar,textvariable=self._search_var,
                      bg=T["input_bg"],fg=T["text"],font=(FONT_UI,12),
                      relief="flat",highlightthickness=1,
                      highlightbackground=T["input_border"],
                      highlightcolor=T["input_focus"],width=20)
        se.pack(side="right",padx=8,pady=4)
        pane = tk.Frame(c,bg=T["win_bg"])
        pane.pack(fill="both",expand=True)
        folder_sidebar = tk.Frame(pane,bg=T["sidebar_bg"],width=160)
        folder_sidebar.pack(side="left",fill="y"); folder_sidebar.pack_propagate(False)
        tk.Label(folder_sidebar,text="Mailboxes",bg=T["sidebar_bg"],fg=T["text"],
                 font=(FONT_UI,13,"bold"),padx=12,pady=8).pack(anchor="w")
        unread = sum(1 for e in self._emails if not e["read"])
        for folder, badge in [("Inbox",str(unread) if unread else ""),("Starred",""),
                               ("Sent",""),("Drafts",""),("Junk",""),("Trash","")]:
            icon_map={"Inbox":"[In]","Starred":"[*]","Sent":"[->]","Drafts":"[D]","Junk":"[!]","Trash":"[x]"}
            row = tk.Frame(folder_sidebar,bg=T["sidebar_bg"],cursor="hand2")
            row.pack(fill="x")
            tk.Label(row,text=icon_map.get(folder,"[f]"),bg=T["sidebar_bg"],
                     fg=T["accent"],font=(FONT_UI,11),padx=6).pack(side="left")
            tk.Label(row,text=folder,bg=T["sidebar_bg"],fg=T["text"],
                     font=(FONT_UI,12),anchor="w",pady=4).pack(side="left",fill="x",expand=True)
            if badge:
                tk.Label(row,text=badge,bg=T["badge_bg"],fg=T["badge_fg"],
                         font=(FONT_UI,10),padx=4).pack(side="right",padx=4)
            row.bind("<Button-1>",lambda _,f=folder: self._set_folder(f))
        tk.Frame(pane,bg=T["separator"],width=1).pack(side="left",fill="y")
        list_frame = tk.Frame(pane,bg=T["win_bg"],width=280)
        list_frame.pack(side="left",fill="y"); list_frame.pack_propagate(False)
        list_header = tk.Frame(list_frame,bg=T["panel_bg"],
                               highlightthickness=1,highlightbackground=T["separator"])
        list_header.pack(fill="x")
        self._folder_lbl = tk.Label(list_header,text="Inbox",bg=T["panel_bg"],
                                    fg=T["text"],font=(FONT_UI,14,"bold"),padx=12,pady=6)
        self._folder_lbl.pack(side="left")
        self._email_list = MacScrolledFrame(list_frame,bg=T["win_bg"])
        self._email_list.pack(fill="both",expand=True)
        self._email_inner = self._email_list.inner
        self._email_inner.configure(bg=T["win_bg"])
        tk.Frame(pane,bg=T["separator"],width=1).pack(side="left",fill="y")
        self._read_pane = tk.Frame(pane,bg=T["win_bg"])
        self._read_pane.pack(side="left",fill="both",expand=True)
        self._refresh_list()

    def _set_folder(self,folder):
        self._folder=folder; self._folder_lbl.configure(text=folder); self._refresh_list()

    def _refresh_list(self):
        for w in self._email_inner.winfo_children(): w.destroy()
        q = self._search_var.get().lower() if hasattr(self,"_search_var") else ""
        emails = self._emails if self._folder!="Starred" else [e for e in self._emails if e["starred"]]
        for i,email in enumerate(emails):
            if q and q not in email["subject"].lower() and q not in email["from"].lower(): continue
            is_sel = (i==self._selected)
            bg = T["selection"] if is_sel else (T["win_bg"] if i%2==0 else T["panel_bg"])
            row = tk.Frame(self._email_inner,bg=bg,cursor="hand2",
                           highlightthickness=1,highlightbackground=T["separator"])
            row.pack(fill="x",pady=1)
            row.bind("<Button-1>",lambda _,idx=i: self._open_email(idx))
            top_row = tk.Frame(row,bg=bg); top_row.pack(fill="x",padx=10,pady=(6,0))
            sender = email["from"].split("@")[0]
            bold_font = (FONT_UI,12,"bold") if not email["read"] else (FONT_UI,12)
            tk.Label(top_row,text=("* " if email["starred"] else "")+sender,
                     bg=bg,fg=T["text"],font=bold_font,anchor="w").pack(side="left",fill="x",expand=True)
            ts = datetime.datetime.fromtimestamp(email["ts"])
            now = datetime.datetime.now()
            time_str = ts.strftime("%I:%M %p") if (now-ts).days==0 else ts.strftime("%m/%d/%y")
            tk.Label(top_row,text=time_str,bg=bg,fg=T["text_muted"],font=(FONT_UI,10)).pack(side="right")
            subj_row = tk.Frame(row,bg=bg); subj_row.pack(fill="x",padx=10)
            tk.Label(subj_row,text=email["subject"][:36],bg=bg,fg=T["text"],
                     font=bold_font,anchor="w").pack(anchor="w")
            preview = email["body"].replace("\n"," ")[:50]+"..."
            tk.Label(row,text=preview,bg=bg,fg=T["text_muted"],
                     font=(FONT_UI,11),anchor="w",padx=10,pady=(0,6)).pack(anchor="w")
            for child in list(row.winfo_children())+[row]:
                child.bind("<Button-1>",lambda _,idx=i: self._open_email(idx))

    def _open_email(self,idx):
        self._selected=idx; self._emails[idx]["read"]=True
        for w in self._read_pane.winfo_children(): w.destroy()
        email = self._emails[idx]
        header = tk.Frame(self._read_pane,bg=T["panel_bg"],
                          highlightthickness=1,highlightbackground=T["separator"])
        header.pack(fill="x")
        tk.Label(header,text=email["subject"],bg=T["panel_bg"],fg=T["text"],
                 font=(FONT_UI,15,"bold"),padx=16,pady=10,
                 wraplength=400,justify="left").pack(anchor="w")
        meta = tk.Frame(header,bg=T["panel_bg"]); meta.pack(fill="x",padx=16,pady=(0,8))
        tk.Label(meta,text=f"From: {email['from']}",bg=T["panel_bg"],
                 fg=T["text_muted"],font=(FONT_UI,11)).pack(anchor="w")
        tk.Label(meta,text=f"To: {email['to']}",bg=T["panel_bg"],
                 fg=T["text_muted"],font=(FONT_UI,11)).pack(anchor="w")
        ts = datetime.datetime.fromtimestamp(email["ts"]).strftime("%B %d, %Y at %I:%M %p")
        tk.Label(meta,text=ts,bg=T["panel_bg"],fg=T["text_muted"],font=(FONT_UI,11)).pack(anchor="w")
        btn_row = tk.Frame(header,bg=T["panel_bg"]); btn_row.pack(fill="x",padx=16,pady=(4,8))
        for lbl,cmd in [("Reply",lambda e=email: self._compose(reply_to=e)),
                         ("Delete",self._delete_selected)]:
            tk.Button(btn_row,text=lbl,bg=T["button_secondary"],fg=T["text"],
                      font=(FONT_UI,11),relief="flat",padx=10,pady=3,
                      cursor="hand2",command=cmd).pack(side="left",padx=2)
        tk.Frame(self._read_pane,bg=T["separator"],height=1).pack(fill="x")
        body_text = tk.Text(self._read_pane,bg=T["win_bg"],fg=T["text"],
                            font=(FONT_UI,13),relief="flat",wrap="word",
                            padx=16,pady=12,highlightthickness=0,state="disabled")
        body_text.pack(fill="both",expand=True)
        body_text.configure(state="normal"); body_text.insert("1.0",email["body"]); body_text.configure(state="disabled")
        self._refresh_list()

    def _compose(self,reply_to=None):
        dlg = tk.Toplevel(self.wm.root); dlg.title("New Message")
        dlg.geometry("580x440"); dlg.configure(bg=T["win_bg"]); dlg.transient(self.wm.root)
        toolbar = tk.Frame(dlg,bg=T["panel_bg"],highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        to_var = tk.StringVar(value=reply_to["from"] if reply_to else "")
        subj_var = tk.StringVar(value=("Re: "+reply_to["subject"]) if reply_to else "")
        tk.Button(toolbar,text="Send",bg=T["accent"],fg="#ffffff",font=(FONT_UI,13),
                  relief="flat",padx=12,pady=4,cursor="hand2",
                  command=lambda: self._send_email(dlg,to_var,subj_var,body_text)).pack(side="left",padx=8,pady=4)
        tk.Button(toolbar,text="Cancel",bg=T["button_secondary"],fg=T["text"],
                  font=(FONT_UI,13),relief="flat",padx=12,pady=4,
                  cursor="hand2",command=dlg.destroy).pack(side="left")
        for label,var in [("To:",to_var),("Subject:",subj_var)]:
            row = tk.Frame(dlg,bg=T["win_bg"],highlightthickness=1,highlightbackground=T["separator"])
            row.pack(fill="x")
            tk.Label(row,text=label,bg=T["win_bg"],fg=T["text_muted"],
                     font=(FONT_UI,12),width=10,anchor="e",padx=4).pack(side="left")
            tk.Entry(row,textvariable=var,bg=T["win_bg"],fg=T["text"],
                     font=(FONT_UI,13),relief="flat",highlightthickness=0
                     ).pack(side="left",fill="x",expand=True,pady=4)
        body_text = tk.Text(dlg,bg=T["win_bg"],fg=T["text"],font=(FONT_UI,13),
                            relief="flat",insertbackground=T["text"],wrap="word",
                            padx=12,pady=8,highlightthickness=0)
        body_text.pack(fill="both",expand=True)
        if reply_to:
            quoted="\n\n---\n"+"\n".join("> "+l for l in reply_to["body"].splitlines())
            body_text.insert("1.0",quoted); body_text.mark_set("insert","1.0")

    def _send_email(self,dlg,to_var,subj_var,body_text):
        sent={"from":"user@macpyos.local","to":to_var.get(),"subject":subj_var.get(),
              "body":body_text.get("1.0","end-1c"),"ts":time.time(),"read":True,"starred":False}
        self._emails.insert(0,sent)
        self.wm.notifs.send("Mail",f"Sent to {sent['to']}",icon="mail")
        dlg.destroy(); self._refresh_list()

    def _delete_selected(self):
        if self._selected is not None and self._selected<len(self._emails):
            self._emails.pop(self._selected); self._selected=None
            for w in self._read_pane.winfo_children(): w.destroy()
            self._refresh_list()

    def _star_selected(self):
        if self._selected is not None:
            self._emails[self._selected]["starred"] = not self._emails[self._selected]["starred"]
            self._refresh_list()

    def _mark_read(self):
        if self._selected is not None:
            self._emails[self._selected]["read"]=True; self._refresh_list()


# =============================================================================
#  MacPyOS — PART 5
#  Keychain Access, Numbers, Photos, Disk Utility, Script Editor, Archive Utility
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 28 — KEYCHAIN ACCESS
# ─────────────────────────────────────────────────────────────────────────────

class KeychainApp(BaseWin):
    """macOS Keychain Access — password vault with categories."""

    CATEGORIES = ["All Items", "Passwords", "Secure Notes", "Certificates", "Keys"]

    SAMPLE_ENTRIES = [
        {"type":"password","name":"iCloud","account":"user@icloud.com",     "pw":"iCloud2025!",  "url":"https://icloud.com",     "notes":"Primary iCloud account"},
        {"type":"password","name":"GitHub","account":"devuser",              "pw":"gh_tok_abc123","url":"https://github.com",      "notes":"Personal GitHub"},
        {"type":"password","name":"Gmail", "account":"user@gmail.com",       "pw":"G00glePass!",  "url":"https://gmail.com",       "notes":""},
        {"type":"password","name":"Twitter","account":"@pyuser",             "pw":"TwtR#2025",    "url":"https://twitter.com",     "notes":""},
        {"type":"password","name":"AWS",   "account":"user@company.com",     "pw":"AWS_Sec!23",   "url":"https://aws.amazon.com",  "notes":"Work AWS account"},
        {"type":"note",    "name":"SSH Key Passphrase","account":"",         "pw":"ssh_pass_2025","url":"",                        "notes":"MacBook Pro SSH key"},
        {"type":"password","name":"Netflix","account":"user@gmail.com",      "pw":"Nflx2025$",   "url":"https://netflix.com",     "notes":"Family plan"},
        {"type":"password","name":"Spotify","account":"user@gmail.com",      "pw":"Sp0tify!",    "url":"https://spotify.com",     "notes":"Premium"},
    ]

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "Keychain Access", w=760, h=520, icon="🔑")
        self._entries   = [dict(e) for e in self.SAMPLE_ENTRIES]
        self._category  = "All Items"
        self._show_pw   = False
        self._authenticated = False
        self._build_ui()

    def _build_ui(self) -> None:
        # Toolbar
        tb = tk.Frame(self.client, bg=T["panel_bg"], pady=6)
        tb.pack(fill="x")
        tk.Label(tb, text="🔒 Keychain Access", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 14, "bold"), padx=12).pack(side="left")
        tk.Label(tb, text="＋ Add", bg=T["panel_bg"], fg=T["accent"],
                 font=(FONT_UI, 13), cursor="hand2",
                 padx=8).pack(side="right").bind("<Button-1>",
                 lambda _: self._add_entry())
        tk.Label(tb, text="🔍", bg=T["panel_bg"],
                 font=(FONT_EMOJI, 13), padx=4).pack(side="right")
        sv = tk.StringVar()
        sv.trace_add("write", lambda *_: self._filter(sv.get()))
        tk.Entry(tb, textvariable=sv, bg=T["input_bg"], fg=T["text"],
                 font=(FONT_UI, 12), relief="flat",
                 highlightthickness=1,
                 highlightbackground=T["input_border"],
                 width=16).pack(side="right", padx=4)

        # Main pane
        pane = tk.PanedWindow(self.client, orient="horizontal",
                              bg=T["separator"], sashwidth=1)
        pane.pack(fill="both", expand=True)

        # Sidebar — categories
        sidebar = tk.Frame(pane, bg=T["sidebar_bg"], width=180)
        sidebar.pack_propagate(False)
        pane.add(sidebar, width=180)

        tk.Label(sidebar, text="Category", bg=T["sidebar_bg"],
                 fg=T["text_muted"], font=(FONT_UI, 11, "bold"),
                 padx=12, pady=8).pack(anchor="w")
        self._cat_btns: Dict[str, tk.Label] = {}
        for cat in self.CATEGORIES:
            row = tk.Frame(sidebar, bg=T["sidebar_bg"], cursor="hand2")
            row.pack(fill="x")
            lbl = tk.Label(row, text=cat, bg=T["sidebar_bg"],
                           fg=T["text"], font=(FONT_UI, 13),
                           padx=16, pady=5, anchor="w")
            lbl.pack(fill="x")
            row.bind("<Button-1>", lambda _, c=cat: self._switch_cat(c))
            lbl.bind("<Button-1>",  lambda _, c=cat: self._switch_cat(c))
            self._cat_btns[cat] = lbl

        # Right — list + detail
        right = tk.Frame(pane, bg=T["win_bg"])
        pane.add(right)

        # Column headers
        hdr = tk.Frame(right, bg=T["panel_bg"])
        hdr.pack(fill="x")
        for text, width in [("Name",200),("Account",180),("Type",80),("Modified",120)]:
            tk.Label(hdr, text=text, bg=T["panel_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 11),
                     width=width//8, anchor="w", padx=8, pady=4).pack(side="left")

        # List
        cols = ("Name","Account","Type","Modified")
        self._tree = ttk.Treeview(right, columns=cols, show="headings", height=12)
        for col in cols:
            w = {"Name":200,"Account":180,"Type":80,"Modified":120}[col]
            self._tree.heading(col, text=col)
            self._tree.column(col, width=w)
        sb = ttk.Scrollbar(right, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side="left", fill="both", expand=True, padx=(8,0), pady=8)
        sb.pack(side="left", fill="y", pady=8)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-Button-1>", lambda _: self._view_entry())

        # Detail panel
        self._detail = tk.Frame(right, bg=T["panel_bg"], height=130)
        self._detail.pack(fill="x", side="bottom", padx=8, pady=(0,8))
        self._detail.pack_propagate(False)
        tk.Label(self._detail, text="Select an item to view details",
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 12)).pack(pady=20)

        self._switch_cat("All Items")

    def _switch_cat(self, cat: str) -> None:
        self._category = cat
        for c, lbl in self._cat_btns.items():
            lbl.configure(
                bg=T["selection"] if c == cat else T["sidebar_bg"],
                fg=T["accent"] if c == cat else T["text"],
            )
        self._refresh_list()

    def _refresh_list(self, filter_str: str = "") -> None:
        self._tree.delete(*self._tree.get_children())
        for e in self._entries:
            if self._category not in ("All Items",) and \
               not (self._category == "Passwords" and e["type"] == "password") and \
               not (self._category == "Secure Notes" and e["type"] == "note"):
                continue
            if filter_str and filter_str.lower() not in e["name"].lower() and \
               filter_str.lower() not in e.get("account","").lower():
                continue
            self._tree.insert("", "end", values=(
                e["name"], e.get("account",""),
                e["type"].title(),
                datetime.datetime.now().strftime("%b %d, %Y"),
            ), iid=str(self._entries.index(e)))

    def _filter(self, query: str) -> None:
        self._refresh_list(query)

    def _on_select(self, _: tk.Event) -> None:
        sel = self._tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        e   = self._entries[idx]
        for w in self._detail.winfo_children():
            w.destroy()
        tk.Label(self._detail, text=e["name"],
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold"), padx=12, pady=6).pack(anchor="w")
        tk.Label(self._detail, text=f"Account: {e.get('account','')}",
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 12), padx=12).pack(anchor="w")
        if e.get("url"):
            tk.Label(self._detail, text=f"URL: {e['url']}",
                     bg=T["panel_bg"], fg=T["link"],
                     font=(FONT_UI, 12), padx=12).pack(anchor="w")
        pw_frame = tk.Frame(self._detail, bg=T["panel_bg"])
        pw_frame.pack(anchor="w", padx=12, pady=4)
        tk.Label(pw_frame, text="Password: ",
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 12)).pack(side="left")
        pw_var = tk.StringVar(value="••••••••")
        pw_lbl = tk.Label(pw_frame, textvariable=pw_var,
                          bg=T["panel_bg"], fg=T["text"],
                          font=(FONT_MONO, 12))
        pw_lbl.pack(side="left")
        show_var = tk.BooleanVar(value=False)
        def toggle_pw(idx=idx, var=pw_var, sv=show_var):
            if not self._authenticated:
                pw = simpledialog.askstring("Authenticate",
                    "Enter your macOS password to view:",
                    show="•", parent=self.wm.root)
                if pw != "user":
                    self.wm.notifs.send("Keychain", "Authentication failed.", icon="🔒")
                    return
                self._authenticated = True
            sv.set(not sv.get())
            var.set(self._entries[idx]["pw"] if sv.get() else "••••••••")
        tk.Button(pw_frame, text="Show",
                  bg=T["button_secondary"], fg=T["text"],
                  font=(FONT_UI, 11), relief="flat",
                  command=toggle_pw).pack(side="left", padx=8)
        tk.Button(pw_frame, text="Copy",
                  bg=T["accent"], fg="#ffffff",
                  font=(FONT_UI, 11), relief="flat",
                  command=lambda idx=idx: (
                      self.wm.clip.copy_text(self._entries[idx]["pw"]),
                      self.wm.notifs.send("Keychain","Password copied to clipboard",icon="📋")
                  )).pack(side="left")

    def _view_entry(self) -> None:
        self._on_select(None)

    def _add_entry(self) -> None:
        AddKeychainDialog(self.wm, self._entries, self._refresh_list)


class AddKeychainDialog:
    def __init__(self, wm: "WM", entries: List[Dict], refresh: Callable) -> None:
        dlg = tk.Toplevel(wm.root)
        dlg.title("Add Password")
        dlg.geometry("420x320")
        dlg.configure(bg=T["win_bg"])
        dlg.transient(wm.root)
        dlg.grab_set()

        tk.Label(dlg, text="Add New Password",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 16, "bold"), pady=12).pack()

        fields: Dict[str, tk.Entry] = {}
        for label, show in [("Name",""),("Account",""),("URL",""),("Password","•")]:
            row = tk.Frame(dlg, bg=T["win_bg"])
            row.pack(fill="x", padx=20, pady=4)
            tk.Label(row, text=label+":", bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 12), width=10, anchor="e").pack(side="left")
            e = tk.Entry(row, bg=T["input_bg"], fg=T["text"],
                         font=(FONT_UI, 13), relief="flat",
                         show=show,
                         highlightthickness=1,
                         highlightbackground=T["input_border"])
            e.pack(side="left", fill="x", expand=True, padx=8)
            fields[label] = e

        def save():
            name = fields["Name"].get().strip()
            if not name:
                return
            entries.append({
                "type":    "password",
                "name":    name,
                "account": fields["Account"].get(),
                "pw":      fields["Password"].get(),
                "url":     fields["URL"].get(),
                "notes":   "",
            })
            refresh()
            wm.notifs.send("Keychain", f"'{name}' added to Keychain.", icon="🔑")
            dlg.destroy()

        btn_row = tk.Frame(dlg, bg=T["win_bg"])
        btn_row.pack(pady=12)
        tk.Button(btn_row, text="Add to Keychain",
                  bg=T["accent"], fg="#ffffff",
                  font=(FONT_UI, 13), relief="flat",
                  padx=16, command=save).pack(side="left", padx=6)
        tk.Button(btn_row, text="Cancel",
                  bg=T["button_secondary"], fg=T["text"],
                  font=(FONT_UI, 13), relief="flat",
                  padx=16, command=dlg.destroy).pack(side="left", padx=6)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 29 — NUMBERS APP  (Spreadsheet)
# ─────────────────────────────────────────────────────────────────────────────

class NumbersApp(BaseWin):
    """macOS Numbers — spreadsheet with multiple sheets, formula evaluation."""

    ROWS    = 50
    COLS    = 20
    COL_W   = 90
    ROW_H   = 24
    HDR_W   = 44
    HDR_H   = 24

    def __init__(self, wm: "WM", path: Optional[str] = None) -> None:
        super().__init__(wm, "Numbers", w=900, h=600, icon="📊", resizable=True)
        self._sheets: Dict[str, Dict[Tuple[int,int], str]] = {"Sheet 1": {}}
        self._current_sheet = "Sheet 1"
        self._sel: Optional[Tuple[int,int]] = None
        self._path = path
        self._build_ui()
        if path and wm.vfs.isfile(path):
            self._load_csv(path)

    def _build_ui(self) -> None:
        # Toolbar
        tb = tk.Frame(self.client, bg=T["panel_bg"], pady=4)
        tb.pack(fill="x")

        for label, cmd in [("＋ Sheet", self._add_sheet),
                           ("📂 Open",  self._open_file),
                           ("💾 Save",  self._save_file),
                           ("📊 Chart", self._insert_chart)]:
            btn = tk.Label(tb, text=label, bg=T["panel_bg"], fg=T["text"],
                           font=(FONT_UI, 12), padx=8, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda _, c=cmd: c())

        # Formula bar
        formula_bar = tk.Frame(self.client, bg=T["panel_bg"], pady=3)
        formula_bar.pack(fill="x")
        self._cell_ref_var = tk.StringVar(value="A1")
        tk.Entry(formula_bar, textvariable=self._cell_ref_var,
                 bg=T["input_bg"], fg=T["text"],
                 font=(FONT_MONO, 12), relief="flat",
                 highlightthickness=1,
                 highlightbackground=T["input_border"],
                 width=6).pack(side="left", padx=6)
        tk.Label(formula_bar, text="ƒ𝑥", bg=T["panel_bg"],
                 fg=T["accent"], font=(FONT_UI, 13, "bold"),
                 padx=4).pack(side="left")
        self._formula_var = tk.StringVar()
        formula_entry = tk.Entry(formula_bar, textvariable=self._formula_var,
                                  bg=T["input_bg"], fg=T["text"],
                                  font=(FONT_MONO, 13), relief="flat",
                                  highlightthickness=1,
                                  highlightbackground=T["input_border"])
        formula_entry.pack(side="left", fill="x", expand=True, padx=6)
        formula_entry.bind("<Return>", self._formula_commit)

        # Sheet area
        sheet_container = tk.Frame(self.client, bg=T["win_bg"])
        sheet_container.pack(fill="both", expand=True)

        # Canvas for grid
        self._canvas = tk.Canvas(sheet_container, bg=T["win_bg"],
                                  highlightthickness=0)
        self._h_scroll = tk.Scrollbar(sheet_container, orient="horizontal",
                                       command=self._canvas.xview)
        self._v_scroll = tk.Scrollbar(sheet_container, orient="vertical",
                                       command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=self._h_scroll.set,
                                yscrollcommand=self._v_scroll.set)
        self._v_scroll.pack(side="right", fill="y")
        self._h_scroll.pack(side="bottom", fill="x")
        self._canvas.pack(fill="both", expand=True)

        # Grid frame inside canvas
        self._grid_frame = tk.Frame(self._canvas, bg=T["win_bg"])
        self._canvas_win = self._canvas.create_window(
            (0, 0), window=self._grid_frame, anchor="nw"
        )
        self._grid_frame.bind("<Configure>",
                               lambda _: self._canvas.configure(
                                   scrollregion=self._canvas.bbox("all")))

        self._build_grid()

        # Sheet tabs
        self._tab_bar = tk.Frame(self.client, bg=T["panel_bg"], pady=3)
        self._tab_bar.pack(fill="x", side="bottom")
        self._refresh_tabs()

    def _col_letter(self, idx: int) -> str:
        result = ""
        while idx >= 0:
            result = chr(idx % 26 + 65) + result
            idx = idx // 26 - 1
        return result

    def _build_grid(self) -> None:
        for w in self._grid_frame.winfo_children():
            w.destroy()
        self._cell_widgets: Dict[Tuple[int,int], tk.Entry] = {}

        # Corner
        tk.Label(self._grid_frame, text="",
                 bg=T["panel_alt"], fg=T["text_muted"],
                 width=self.HDR_W//8, height=1,
                 relief="flat", bd=0,
                 font=(FONT_UI, 10)).grid(row=0, column=0,
                 sticky="nsew", padx=(0,1), pady=(0,1))

        # Column headers
        for col in range(self.COLS):
            tk.Label(self._grid_frame,
                     text=self._col_letter(col),
                     bg=T["panel_alt"], fg=T["text_muted"],
                     font=(FONT_UI, 10, "bold"),
                     width=self.COL_W//8, relief="flat", bd=0).grid(
                     row=0, column=col+1,
                     sticky="nsew", padx=(0,1), pady=(0,1))

        # Rows
        for row in range(self.ROWS):
            # Row header
            tk.Label(self._grid_frame, text=str(row+1),
                     bg=T["panel_alt"], fg=T["text_muted"],
                     font=(FONT_UI, 10),
                     width=self.HDR_W//8, relief="flat", bd=0).grid(
                     row=row+1, column=0,
                     sticky="nsew", padx=(0,1), pady=(0,1))
            # Cells
            for col in range(self.COLS):
                var = tk.StringVar()
                data = self._sheets[self._current_sheet]
                stored = data.get((row, col), "")
                if stored.startswith("="):
                    var.set(self._eval_formula(stored))
                else:
                    var.set(stored)
                e = tk.Entry(self._grid_frame, textvariable=var,
                             bg=T["win_bg"], fg=T["text"],
                             font=(FONT_UI, 11), relief="flat", bd=0,
                             highlightthickness=1,
                             highlightbackground=T["separator"],
                             highlightcolor=T["accent"],
                             width=self.COL_W//8)
                e.grid(row=row+1, column=col+1, sticky="nsew",
                       padx=(0,1), pady=(0,1))
                e.bind("<FocusIn>",  lambda ev, r=row, c=col: self._cell_focus(r, c, ev))
                e.bind("<FocusOut>", lambda ev, r=row, c=col: self._cell_blur(r, c, ev))
                e.bind("<Return>",   lambda ev, r=row, c=col: self._next_cell(r, c))
                e.bind("<Tab>",      lambda ev, r=row, c=col: self._next_col(r, c))
                self._cell_widgets[(row, col)] = e

    def _cell_focus(self, row: int, col: int, _: tk.Event) -> None:
        self._sel = (row, col)
        ref = self._col_letter(col) + str(row + 1)
        self._cell_ref_var.set(ref)
        stored = self._sheets[self._current_sheet].get((row, col), "")
        self._formula_var.set(stored)

    def _cell_blur(self, row: int, col: int, e: tk.Event) -> None:
        widget = self._cell_widgets.get((row, col))
        if widget:
            val = widget.get()
            self._sheets[self._current_sheet][(row, col)] = val
            if val.startswith("="):
                widget.delete(0, "end")
                widget.insert(0, self._eval_formula(val))

    def _next_cell(self, row: int, col: int) -> None:
        if row + 1 < self.ROWS:
            next_w = self._cell_widgets.get((row + 1, col))
            if next_w:
                next_w.focus_set()

    def _next_col(self, row: int, col: int) -> None:
        if col + 1 < self.COLS:
            next_w = self._cell_widgets.get((row, col + 1))
            if next_w:
                next_w.focus_set()

    def _formula_commit(self, _: tk.Event) -> None:
        if not self._sel:
            return
        row, col = self._sel
        val = self._formula_var.get()
        self._sheets[self._current_sheet][(row, col)] = val
        widget = self._cell_widgets.get((row, col))
        if widget:
            widget.delete(0, "end")
            if val.startswith("="):
                widget.insert(0, self._eval_formula(val))
            else:
                widget.insert(0, val)

    def _eval_formula(self, formula: str) -> str:
        """Evaluate a spreadsheet formula."""
        try:
            expr = formula[1:].strip()
            # SUM(A1:A10) style
            sum_m = re.match(r'SUM\(([A-Z]+)(\d+):([A-Z]+)(\d+)\)', expr, re.I)
            if sum_m:
                c1 = ord(sum_m.group(1).upper()) - 65
                r1 = int(sum_m.group(2)) - 1
                c2 = ord(sum_m.group(3).upper()) - 65
                r2 = int(sum_m.group(4)) - 1
                total = 0.0
                data  = self._sheets[self._current_sheet]
                for r in range(r1, r2+1):
                    for c in range(c1, c2+1):
                        try:
                            total += float(data.get((r,c),"0") or "0")
                        except ValueError:
                            pass
                return str(int(total) if total == int(total) else round(total, 4))
            # AVG(A1:A10)
            avg_m = re.match(r'AVG(?:ERAGE)?\(([A-Z]+)(\d+):([A-Z]+)(\d+)\)', expr, re.I)
            if avg_m:
                c1 = ord(avg_m.group(1).upper()) - 65
                r1 = int(avg_m.group(2)) - 1
                c2 = ord(avg_m.group(3).upper()) - 65
                r2 = int(avg_m.group(4)) - 1
                vals = []
                data = self._sheets[self._current_sheet]
                for r in range(r1, r2+1):
                    for c in range(c1, c2+1):
                        try:
                            vals.append(float(data.get((r,c),"") or "0"))
                        except ValueError:
                            pass
                if not vals:
                    return "0"
                avg = sum(vals) / len(vals)
                return str(round(avg, 4))
            # Cell references like A1+B2
            def replace_cell(m: re.Match) -> str:
                col_l = m.group(1).upper()
                row_n = int(m.group(2)) - 1
                col_n = ord(col_l) - 65
                val   = self._sheets[self._current_sheet].get((row_n, col_n), "0")
                try:
                    float(val)
                    return str(val)
                except ValueError:
                    return "0"
            expr2 = re.sub(r'([A-Z]+)(\d+)', replace_cell, expr)
            result = eval(expr2)
            if isinstance(result, float) and result == int(result):
                return str(int(result))
            return str(round(result, 6))
        except Exception:
            return "#ERROR"

    def _add_sheet(self) -> None:
        name = f"Sheet {len(self._sheets)+1}"
        self._sheets[name] = {}
        self._current_sheet = name
        self._build_grid()
        self._refresh_tabs()

    def _refresh_tabs(self) -> None:
        for w in self._tab_bar.winfo_children():
            w.destroy()
        for sheet in self._sheets:
            active = sheet == self._current_sheet
            btn = tk.Label(self._tab_bar, text=sheet,
                           bg=T["win_bg"] if active else T["panel_bg"],
                           fg=T["accent"] if active else T["text"],
                           font=(FONT_UI, 12, "bold" if active else "normal"),
                           padx=14, pady=4, cursor="hand2",
                           relief="flat", bd=0)
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda _, s=sheet: self._switch_sheet(s))

    def _switch_sheet(self, name: str) -> None:
        self._current_sheet = name
        self._build_grid()
        self._refresh_tabs()

    def _open_file(self) -> None:
        path = simpledialog.askstring("Open File",
            "Enter CSV path (e.g. /Users/user/Spreadsheets/budget.csv):",
            parent=self.wm.root)
        if path and self.wm.vfs.isfile(path):
            self._load_csv(path)

    def _load_csv(self, path: str) -> None:
        try:
            content = self.wm.vfs.read(path)
            lines   = content.strip().split("\n")
            data    = self._sheets[self._current_sheet]
            data.clear()
            for r, line in enumerate(lines):
                for c, val in enumerate(line.split(",")):
                    data[(r, c)] = val.strip()
            self._build_grid()
            fname = path.split("/")[-1]
            self.set_title(f"Numbers — {fname}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex), parent=self.wm.root)

    def _save_file(self) -> None:
        path = simpledialog.askstring("Save As",
            "Save to path (e.g. /Users/user/Spreadsheets/data.csv):",
            parent=self.wm.root)
        if not path:
            return
        data  = self._sheets[self._current_sheet]
        rows: Dict[int, Dict[int, str]] = defaultdict(dict)
        for (r, c), v in data.items():
            rows[r][c] = v
        lines = []
        for r in sorted(rows):
            max_c = max(rows[r].keys(), default=0)
            line  = ",".join(rows[r].get(c, "") for c in range(max_c+1))
            lines.append(line)
        self.wm.vfs.write(path, "\n".join(lines))
        self.wm.notifs.send("Numbers", f"Saved to {path}", icon="💾")

    def _insert_chart(self) -> None:
        self.wm.notifs.send("Numbers", "Chart feature coming soon.", icon="📊")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 30 — PHOTOS APP
# ─────────────────────────────────────────────────────────────────────────────

class PhotosApp(BaseWin):
    """macOS Photos — displays procedurally generated photo thumbnails."""

    ALBUMS = ["Recents", "Favourites", "Screenshots", "Selfies", "Nature", "Travel"]

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "Photos", w=860, h=580, icon="📸")
        self._album    = "Recents"
        self._photos   = self._gen_photos()
        self._selected : Optional[int] = None
        self._build_ui()

    def _gen_photos(self) -> List[Dict]:
        """Generate placeholder photo metadata."""
        photos = []
        palettes = [
            ("#ff6b6b","#ffa94d"), ("#74c0fc","#a9e34b"),
            ("#da77f2","#ff8787"), ("#63e6be","#ffd43b"),
            ("#748ffc","#66d9e8"), ("#f783ac","#ffc9c9"),
        ]
        albums = self.ALBUMS
        for i in range(48):
            pal = palettes[i % len(palettes)]
            photos.append({
                "id":    i,
                "title": f"Photo {i+1:03d}",
                "date":  f"2025-{(i%12)+1:02d}-{(i%28)+1:02d}",
                "color1": pal[0],
                "color2": pal[1],
                "album":  albums[i % len(albums)],
                "fav":    (i % 7 == 0),
                "width":  random.randint(1200, 4000),
                "height": random.randint(800, 3000),
            })
        return photos

    def _make_thumb(self, c1: str, c2: str, size: int = 80) -> tk.PhotoImage:
        """Create a gradient thumbnail PhotoImage."""
        img = tk.PhotoImage(width=size, height=size)
        for y in range(size):
            t  = y / size
            r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
            r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
            r = int(r1 + (r2-r1)*t)
            g = int(g1 + (g2-g1)*t)
            b = int(b1 + (b2-b1)*t)
            row_data = "{" + " ".join(f"#{r:02x}{g:02x}{b:02x}" for _ in range(size)) + "}"
            img.put(row_data, to=(0, y))
        return img

    def _build_ui(self) -> None:
        # Toolbar
        tb = tk.Frame(self.client, bg=T["panel_bg"], pady=6)
        tb.pack(fill="x")
        tk.Label(tb, text="📸 Photos", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 14, "bold"), padx=12).pack(side="left")

        # View mode
        self._view_mode = tk.StringVar(value="grid")
        for mode, icon in [("grid","⊞"),("list","☰")]:
            rb = tk.Label(tb, text=icon, bg=T["panel_bg"],
                          fg=T["text"], font=(FONT_UI, 14),
                          padx=6, cursor="hand2")
            rb.pack(side="right", padx=2)
            rb.bind("<Button-1>", lambda _, m=mode: self._set_view(m))

        # Search
        sv = tk.StringVar()
        sv.trace_add("write", lambda *_: self._search(sv.get()))
        tk.Entry(tb, textvariable=sv, bg=T["input_bg"], fg=T["text"],
                 font=(FONT_UI, 12), relief="flat",
                 highlightthickness=1,
                 highlightbackground=T["input_border"],
                 width=16).pack(side="right", padx=8)
        tk.Label(tb, text="🔍", bg=T["panel_bg"],
                 font=(FONT_EMOJI, 12)).pack(side="right")

        # Main pane
        pane = tk.PanedWindow(self.client, orient="horizontal",
                              bg=T["separator"], sashwidth=1)
        pane.pack(fill="both", expand=True)

        # Sidebar — albums
        sidebar = tk.Frame(pane, bg=T["sidebar_bg"], width=170)
        sidebar.pack_propagate(False)
        pane.add(sidebar, width=170)

        tk.Label(sidebar, text="Library", bg=T["sidebar_bg"],
                 fg=T["text_muted"], font=(FONT_UI, 11, "bold"),
                 padx=12, pady=8).pack(anchor="w")
        for album in self.ALBUMS:
            count = sum(1 for p in self._photos if p["album"] == album)
            row = tk.Frame(sidebar, bg=T["sidebar_bg"], cursor="hand2")
            row.pack(fill="x")
            icons = {"Recents":"🕐","Favourites":"❤️","Screenshots":"📷",
                     "Selfies":"🤳","Nature":"🌿","Travel":"✈️"}
            tk.Label(row, text=icons.get(album,"🖼️"),
                     bg=T["sidebar_bg"], font=(FONT_EMOJI, 13),
                     padx=8).pack(side="left")
            tk.Label(row, text=album, bg=T["sidebar_bg"],
                     fg=T["text"], font=(FONT_UI, 13), anchor="w").pack(
                     side="left", fill="x", expand=True)
            tk.Label(row, text=str(count), bg=T["sidebar_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 11),
                     padx=8).pack(side="right")
            row.bind("<Button-1>", lambda _, a=album: self._switch_album(a))
            for child in row.winfo_children():
                child.bind("<Button-1>", lambda _, a=album: self._switch_album(a))

        # Photo grid
        right = tk.Frame(pane, bg=T["win_bg"])
        pane.add(right)

        self._album_lbl = tk.Label(right, text="Recents",
                                    bg=T["win_bg"], fg=T["text"],
                                    font=(FONT_UI, 18, "bold"),
                                    anchor="w", padx=16, pady=8)
        self._album_lbl.pack(anchor="w")

        self._grid_sf = MacScrolledFrame(right, bg=T["win_bg"])
        self._grid_sf.pack(fill="both", expand=True)
        self._inner  = self._grid_sf.inner

        self._switch_album("Recents")

    def _switch_album(self, album: str) -> None:
        self._album = album
        self._album_lbl.configure(text=album)
        self._render_grid([p for p in self._photos if p["album"] == album])

    def _search(self, query: str) -> None:
        if not query:
            self._switch_album(self._album)
            return
        hits = [p for p in self._photos if query.lower() in p["title"].lower()
                or query in p["date"]]
        self._album_lbl.configure(text=f'Search: "{query}"')
        self._render_grid(hits)

    def _set_view(self, mode: str) -> None:
        self._view_mode.set(mode)
        self._switch_album(self._album)

    def _render_grid(self, photos: List[Dict]) -> None:
        for w in self._inner.winfo_children():
            w.destroy()
        self._thumb_refs: List[tk.PhotoImage] = []

        if not photos:
            tk.Label(self._inner, text="No photos",
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 14)).pack(pady=40)
            return

        if self._view_mode.get() == "list":
            for photo in photos:
                row = tk.Frame(self._inner, bg=T["win_bg"], cursor="hand2")
                row.pack(fill="x", pady=1)
                tk.Frame(row, bg=photo["color1"], width=40, height=40).pack(
                    side="left", padx=8, pady=4)
                info = tk.Frame(row, bg=T["win_bg"])
                info.pack(side="left", fill="x", expand=True)
                tk.Label(info, text=photo["title"],
                         bg=T["win_bg"], fg=T["text"],
                         font=(FONT_UI, 13), anchor="w").pack(anchor="w")
                tk.Label(info, text=f"{photo['date']}  •  {photo['width']}×{photo['height']}",
                         bg=T["win_bg"], fg=T["text_muted"],
                         font=(FONT_UI, 11), anchor="w").pack(anchor="w")
                if photo["fav"]:
                    tk.Label(row, text="❤️", bg=T["win_bg"],
                             font=(FONT_EMOJI, 12), padx=8).pack(side="right")
                tk.Frame(self._inner, bg=T["separator"], height=1).pack(fill="x")
        else:
            # Grid — 5 columns
            cols = 5
            thumb_size = 80
            for i, photo in enumerate(photos):
                row_idx = i // cols
                col_idx = i % cols
                if col_idx == 0:
                    row_frame = tk.Frame(self._inner, bg=T["win_bg"])
                    row_frame.pack(fill="x", padx=8, pady=2)
                cell = tk.Frame(row_frame, bg=T["win_bg"], cursor="hand2")
                cell.pack(side="left", padx=4)
                try:
                    thumb = self._make_thumb(photo["color1"],
                                             photo["color2"], thumb_size)
                    self._thumb_refs.append(thumb)
                    lbl = tk.Label(cell, image=thumb,
                                   bg=T["win_bg"],
                                   relief="flat", bd=2,
                                   highlightthickness=0)
                    lbl.pack()
                except Exception:
                    tk.Frame(cell, bg=photo["color1"],
                              width=thumb_size, height=thumb_size).pack()
                if photo["fav"]:
                    tk.Label(cell, text="❤️", bg=T["win_bg"],
                             font=(FONT_EMOJI, 9)).pack()
                cell.bind("<Double-Button-1>",
                          lambda _, p=photo: self._open_photo(p))

    def _open_photo(self, photo: Dict) -> None:
        dlg = tk.Toplevel(self.wm.root)
        dlg.title(photo["title"])
        dlg.geometry("600x480")
        dlg.configure(bg="#000000")
        dlg.transient(self.wm.root)

        # Full-size gradient render
        canvas = tk.Canvas(dlg, bg="#000000", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def draw(_: Optional[tk.Event] = None) -> None:
            w = canvas.winfo_width() or 600
            h = canvas.winfo_height() or 480
            canvas.delete("all")
            steps = 60
            c1, c2 = photo["color1"], photo["color2"]
            for i in range(steps):
                t  = i / steps
                r1,g1,b1 = int(c1[1:3],16),int(c1[3:5],16),int(c1[5:7],16)
                r2,g2,b2 = int(c2[1:3],16),int(c2[3:5],16),int(c2[5:7],16)
                r  = int(r1+(r2-r1)*t)
                g  = int(g1+(g2-g1)*t)
                b  = int(b1+(b2-b1)*t)
                color = f"#{r:02x}{g:02x}{b:02x}"
                y0 = int(h*i/steps)
                y1 = int(h*(i+1)/steps)
                canvas.create_rectangle(0,y0,w,y1,fill=color,outline="")
            canvas.create_text(w//2, h-40, text=photo["title"],
                                fill="#ffffff", font=(FONT_UI, 16, "bold"))
            canvas.create_text(w//2, h-20,
                                text=f"{photo['width']}×{photo['height']}  •  {photo['date']}",
                                fill="#ffffff", font=(FONT_UI, 11))

        canvas.bind("<Configure>", draw)
        dlg.after(50, draw)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 31 — DISK UTILITY APP
# ─────────────────────────────────────────────────────────────────────────────

class DiskUtilityApp(BaseWin):
    """macOS Disk Utility — shows VFS tree as disk usage."""

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "Disk Utility", w=740, h=520, icon="💿")
        self._build_ui()
        self._scan()

    def _build_ui(self) -> None:
        # Toolbar
        tb = tk.Frame(self.client, bg=T["panel_bg"], pady=6)
        tb.pack(fill="x")
        tk.Label(tb, text="💿 Disk Utility", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 14, "bold"), padx=12).pack(side="left")
        for label, cmd in [("🔍 First Aid", self._first_aid),
                           ("✂️ Partition", self._partition),
                           ("⏏️ Eject",     self._eject),
                           ("ℹ️ Info",       self._info)]:
            btn = tk.Label(tb, text=label, bg=T["panel_bg"], fg=T["text"],
                           font=(FONT_UI, 12), padx=8, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda _, c=cmd: c())

        # Main pane
        pane = tk.PanedWindow(self.client, orient="horizontal",
                              bg=T["separator"], sashwidth=1)
        pane.pack(fill="both", expand=True)

        # Disk list sidebar
        sidebar = tk.Frame(pane, bg=T["sidebar_bg"], width=200)
        sidebar.pack_propagate(False)
        pane.add(sidebar, width=200)
        tk.Label(sidebar, text="Devices", bg=T["sidebar_bg"],
                 fg=T["text_muted"], font=(FONT_UI, 11, "bold"),
                 padx=12, pady=6).pack(anchor="w")

        self._disk_list = tk.Listbox(
            sidebar, bg=T["sidebar_bg"], fg=T["text"],
            selectbackground=T["selection"],
            font=(FONT_UI, 13), relief="flat", bd=0,
            highlightthickness=0, activestyle="none",
        )
        self._disk_list.pack(fill="both", expand=True, padx=4)
        self._disk_list.bind("<<ListboxSelect>>", self._on_select)

        # Add simulated disks
        for disk in ["💻  Macintosh HD", "💾  Data", "📀  External Drive",
                     "📀  Time Machine"]:
            self._disk_list.insert("end", disk)

        # Detail panel
        right = tk.Frame(pane, bg=T["win_bg"])
        pane.add(right)

        self._detail_top = tk.Frame(right, bg=T["win_bg"])
        self._detail_top.pack(fill="x", padx=20, pady=16)

        self._disk_icon_lbl = tk.Label(self._detail_top, text="💿",
                                        bg=T["win_bg"], font=(FONT_EMOJI, 48))
        self._disk_icon_lbl.pack(side="left")

        info_frame = tk.Frame(self._detail_top, bg=T["win_bg"])
        info_frame.pack(side="left", padx=16)
        self._disk_name_lbl = tk.Label(info_frame, text="Select a disk",
                                        bg=T["win_bg"], fg=T["text"],
                                        font=(FONT_UI, 18, "bold"), anchor="w")
        self._disk_name_lbl.pack(anchor="w")
        self._disk_info_lbl = tk.Label(info_frame, text="",
                                        bg=T["win_bg"], fg=T["text_muted"],
                                        font=(FONT_UI, 12), anchor="w")
        self._disk_info_lbl.pack(anchor="w")

        # Usage bar
        usage_frame = tk.Frame(right, bg=T["win_bg"])
        usage_frame.pack(fill="x", padx=20, pady=8)
        tk.Label(usage_frame, text="Storage Used",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 11)).pack(anchor="w")
        self._usage_canvas = tk.Canvas(usage_frame, height=28,
                                        bg=T["progress_bg"],
                                        highlightthickness=0)
        self._usage_canvas.pack(fill="x", pady=4)

        self._usage_lbl = tk.Label(usage_frame, text="",
                                    bg=T["win_bg"], fg=T["text_muted"],
                                    font=(FONT_UI, 11))
        self._usage_lbl.pack(anchor="w")

        # VFS tree
        tk.Label(right, text="Volume Contents",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold"),
                 padx=20, pady=8).pack(anchor="w")

        tree_frame = tk.Frame(right, bg=T["win_bg"])
        tree_frame.pack(fill="both", expand=True, padx=10)
        cols = ("Path", "Size", "Type")
        self._vfs_tree = ttk.Treeview(tree_frame, columns=cols,
                                       show="headings", height=10)
        for col in cols:
            w = {"Path": 300, "Size": 100, "Type": 80}[col]
            self._vfs_tree.heading(col, text=col)
            self._vfs_tree.column(col, width=w)
        sb2 = ttk.Scrollbar(tree_frame, orient="vertical",
                             command=self._vfs_tree.yview)
        self._vfs_tree.configure(yscrollcommand=sb2.set)
        self._vfs_tree.pack(side="left", fill="both", expand=True)
        sb2.pack(side="left", fill="y")

    def _scan(self) -> None:
        """Populate VFS tree with top-level directories."""
        self._vfs_tree.delete(*self._vfs_tree.get_children())
        try:
            for entry in self.wm.vfs.listdir("/Users/user"):
                full = f"/Users/user/{entry}"
                size = self.wm.vfs._get_node(full).size()
                kind = "Folder" if self.wm.vfs.isdir(full) else "File"
                self._vfs_tree.insert("", "end", values=(
                    full,
                    self._fmt_size(size),
                    kind,
                ))
        except Exception:
            pass

    def _fmt_size(self, b: int) -> str:
        if b < 1024:      return f"{b} B"
        elif b < 1048576: return f"{b/1024:.1f} KB"
        elif b < 1073741824: return f"{b/1048576:.1f} MB"
        return f"{b/1073741824:.2f} GB"

    def _on_select(self, _: tk.Event) -> None:
        sel = self._disk_list.curselection()
        if not sel:
            return
        names = ["Macintosh HD", "Data", "External Drive", "Time Machine"]
        sizes = [512, 512, 2048, 4000]
        used  = [342, 180, 1100, 2800]
        idx   = sel[0]
        name  = names[min(idx, len(names)-1)]
        sz    = sizes[min(idx, len(sizes)-1)]
        us    = used[min(idx, len(used)-1)]
        self._disk_name_lbl.configure(text=name)
        self._disk_info_lbl.configure(
            text=f"APFS Volume  •  {sz} GB  •  Mac OS Extended"
        )
        # Usage bar
        self._usage_canvas.delete("all")
        w = self._usage_canvas.winfo_width() or 400
        ratio = us / sz
        # Coloured segments
        segments = [
            ("Apps",    0.30, T["chart1"]),
            ("Photos",  0.20, T["chart2"]),
            ("Docs",    0.15, T["chart3"]),
            ("System",  0.10, T["chart4"]),
            ("Other",   ratio - 0.75, T["chart5"]),
        ]
        x = 0
        for label, frac, color in segments:
            if frac <= 0:
                continue
            bw = max(1, int(w * frac))
            self._usage_canvas.create_rectangle(
                x, 0, x+bw, 28, fill=color, outline=""
            )
            if bw > 40:
                self._usage_canvas.create_text(
                    x + bw//2, 14, text=label,
                    fill="#ffffff", font=(FONT_UI, 9)
                )
            x += bw
        # Free space
        self._usage_canvas.create_rectangle(x, 0, w, 28,
                                             fill=T["progress_bg"], outline="")
        free = sz - us
        self._usage_lbl.configure(
            text=f"{us} GB used of {sz} GB  •  {free} GB available"
        )

    def _first_aid(self) -> None:
        self.wm.notifs.send("Disk Utility",
                             "First Aid completed — no errors found.", icon="✅")

    def _partition(self) -> None:
        messagebox.showinfo("Partition", "Partitioning not supported in simulation.",
                            parent=self.wm.root)

    def _eject(self) -> None:
        self.wm.notifs.send("Disk Utility", "Disk ejected safely.", icon="⏏️")

    def _info(self) -> None:
        messagebox.showinfo("Disk Info",
                            "MacPyOS Virtual Disk\n"
                            "Type: Virtual (in-memory VFS)\n"
                            "Format: PyFS v1.0\n"
                            "Total Nodes: " +
                            str(len(self.wm.vfs.find("/", ".*"))),
                            parent=self.wm.root)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 32 — SCRIPT EDITOR APP
# ─────────────────────────────────────────────────────────────────────────────

class ScriptEditorApp(BaseWin):
    """macOS Script Editor — run Python scripts inside MacPyOS."""

    SYNTAX = {
        "keyword":  (r'\b(def|class|import|from|return|if|elif|else|for|while|'
                      r'try|except|finally|with|as|in|not|and|or|is|pass|break|'
                      r'continue|raise|yield|lambda|global|nonlocal|del|assert|'
                      r'True|False|None)\b', "#c792ea"),
        "builtin":  (r'\b(print|len|range|str|int|float|list|dict|set|tuple|type|'
                      r'open|input|super|self|zip|map|filter|enumerate|sorted|'
                      r'reversed|abs|round|max|min|sum|any|all|isinstance)\b', "#82aaff"),
        "string":   (r'(\"\"\".*?\"\"\"|\'\'\'.*?\'\'\'|\"[^\"]*\"|\'[^\']*\')', "#c3e88d"),
        "comment":  (r'(#[^\n]*)',                                                 "#546e7a"),
        "number":   (r'\b(\d+\.?\d*)\b',                                           "#f78c6c"),
        "decorator":(r'(@\w+)',                                                    "#ffcb6b"),
    }

    def __init__(self, wm: "WM", path: Optional[str] = None) -> None:
        super().__init__(wm, "Script Editor", w=800, h=580, icon="📝")
        self._path     = path
        self._modified = False
        self._run_proc : Optional[Process] = None
        self._build_ui()
        if path and wm.vfs.isfile(path):
            self._load(path)
        else:
            self._editor.insert("1.0",
                "#!/usr/bin/env python3\n"
                '"""MacPyOS Script"""\n\n\n'
                "def main():\n"
                '    print("Hello from MacPyOS!")\n\n\n'
                'if __name__ == "__main__":\n'
                "    main()\n")
            self._highlight()

    def _build_ui(self) -> None:
        # Toolbar
        tb = tk.Frame(self.client, bg=T["panel_bg"], pady=6)
        tb.pack(fill="x")
        for label, cmd, color in [
            ("▶  Run",      self._run,  T["accent3"]),
            ("⏹  Stop",     self._stop, T["danger"]),
            ("📂 Open",     self._open, T["accent"]),
            ("💾 Save",     self._save, T["accent"]),
            ("🔍 Check",    self._syntax_check, T["warning"]),
        ]:
            btn = tk.Label(tb, text=label, bg=T["panel_bg"], fg=color,
                           font=(FONT_UI, 12, "bold"), padx=8, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda _, c=cmd: c())

        # File path
        self._path_var = tk.StringVar(value=self._path or "Untitled.py")
        tk.Entry(tb, textvariable=self._path_var,
                 bg=T["input_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 11), relief="flat",
                 highlightthickness=0,
                 width=30).pack(side="right", padx=10)

        # Paned editor + output
        pane = tk.PanedWindow(self.client, orient="vertical",
                              bg=T["separator"], sashwidth=3)
        pane.pack(fill="both", expand=True)

        # Editor
        editor_frame = tk.Frame(pane, bg="#1e1e2e")
        pane.add(editor_frame, height=380)

        # Line numbers + editor
        line_num_frame = tk.Frame(editor_frame, bg="#1e1e2e")
        line_num_frame.pack(fill="both", expand=True)

        self._line_nums = tk.Text(
            line_num_frame,
            width=4, bg="#1e1e2e", fg="#546e7a",
            font=(FONT_MONO, 13), relief="flat", bd=0,
            state="disabled", cursor="arrow",
        )
        self._line_nums.pack(side="left", fill="y")

        self._editor = tk.Text(
            line_num_frame,
            bg="#1e1e2e", fg="#cdd6f4",
            font=(FONT_MONO, 13),
            relief="flat", bd=0,
            padx=8, pady=4,
            insertbackground="#cdd6f4",
            selectbackground="#313244",
            undo=True, wrap="none",
            tabs=("4c",),
        )
        editor_sb = tk.Scrollbar(line_num_frame, orient="vertical",
                                  command=self._editor.yview)
        self._editor.configure(yscrollcommand=editor_sb.set)
        editor_sb.pack(side="right", fill="y")
        self._editor.pack(side="left", fill="both", expand=True)
        self._editor.bind("<KeyRelease>", self._on_key)
        self._editor.bind("<Tab>", self._insert_tab)

        # Output console
        output_frame = tk.Frame(pane, bg="#11111b")
        pane.add(output_frame, height=160)

        console_hdr = tk.Frame(output_frame, bg="#1e1e2e", pady=4)
        console_hdr.pack(fill="x")
        tk.Label(console_hdr, text="Console Output",
                 bg="#1e1e2e", fg="#a6adc8",
                 font=(FONT_UI, 11, "bold"), padx=10).pack(side="left")
        tk.Label(console_hdr, text="Clear", bg="#1e1e2e",
                 fg=T["text_muted"], font=(FONT_UI, 11),
                 cursor="hand2", padx=8).pack(side="right").bind(
                 "<Button-1>", lambda _: self._clear_output())

        self._output = tk.Text(
            output_frame,
            bg="#11111b", fg="#a6e3a1",
            font=(FONT_MONO, 12),
            relief="flat", bd=0,
            padx=8, pady=4,
            state="disabled", wrap="word",
        )
        out_sb = tk.Scrollbar(output_frame, orient="vertical",
                               command=self._output.yview)
        self._output.configure(yscrollcommand=out_sb.set)
        out_sb.pack(side="right", fill="y")
        self._output.pack(fill="both", expand=True)

        # Status bar
        status = tk.Frame(self.client, bg=T["panel_bg"], pady=3)
        status.pack(fill="x", side="bottom")
        self._status_var = tk.StringVar(value="Ready")
        tk.Label(status, textvariable=self._status_var,
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 10), padx=10).pack(side="left")
        self._cur_pos = tk.StringVar(value="Ln 1, Col 1")
        tk.Label(status, textvariable=self._cur_pos,
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 10), padx=10).pack(side="right")

    def _on_key(self, _: tk.Event) -> None:
        self._modified = True
        self._highlight()
        self._update_line_nums()
        # Update cursor position
        pos = self._editor.index("insert")
        line, col = pos.split(".")
        self._cur_pos.set(f"Ln {line}, Col {int(col)+1}")

    def _insert_tab(self, _: tk.Event) -> str:
        self._editor.insert("insert", "    ")
        return "break"

    def _update_line_nums(self) -> None:
        self._line_nums.configure(state="normal")
        self._line_nums.delete("1.0", "end")
        content = self._editor.get("1.0", "end-1c")
        lines   = content.count("\n") + 1
        self._line_nums.insert("1.0", "\n".join(str(i) for i in range(1, lines+1)))
        self._line_nums.configure(state="disabled")

    def _highlight(self) -> None:
        """Apply syntax highlighting tags."""
        content = self._editor.get("1.0", "end-1c")
        # Remove all tags
        for tag in self.SYNTAX:
            self._editor.tag_remove(tag, "1.0", "end")

        for tag, (pattern, color) in self.SYNTAX.items():
            self._editor.tag_configure(tag, foreground=color)
            for m in re.finditer(pattern, content, re.DOTALL | re.MULTILINE):
                start = f"1.0 + {m.start()} chars"
                end   = f"1.0 + {m.end()} chars"
                self._editor.tag_add(tag, start, end)

    def _run(self) -> None:
        code = self._editor.get("1.0", "end-1c")
        self._clear_output()
        self._status_var.set("Running…")
        self._print_output(f"▶  Running script…\n{'─'*40}\n")

        def _exec():
            import io as _io
            stdout_capture = _io.StringIO()
            stderr_capture = _io.StringIO()
            import sys as _sys
            old_out, old_err = _sys.stdout, _sys.stderr
            _sys.stdout = stdout_capture
            _sys.stderr = stderr_capture
            try:
                exec(compile(code, "<script>", "exec"), {})
                out = stdout_capture.getvalue()
                err = stderr_capture.getvalue()
                self.client.after(0, lambda: self._print_output(
                    out + (f"\n⚠️  {err}" if err else "") +
                    "\n" + "─"*40 + "\n✅  Script finished successfully.\n"
                ))
                self.client.after(0, lambda: self._status_var.set("Finished"))
            except Exception as e:
                tb = traceback.format_exc()
                self.client.after(0, lambda tb=tb: self._print_output(
                    f"❌  Error:\n{tb}\n"
                ))
                self.client.after(0, lambda: self._status_var.set("Error"))
            finally:
                _sys.stdout = old_out
                _sys.stderr = old_err

        threading.Thread(target=_exec, daemon=True).start()

    def _stop(self) -> None:
        self._status_var.set("Stopped")
        self._print_output("\n⏹  Execution stopped.\n")

    def _syntax_check(self) -> None:
        code = self._editor.get("1.0", "end-1c")
        try:
            compile(code, "<script>", "exec")
            self._print_output("✅  Syntax OK — no errors found.\n")
            self._status_var.set("Syntax OK")
        except SyntaxError as e:
            self._print_output(f"❌  Syntax Error at line {e.lineno}: {e.msg}\n")
            self._status_var.set(f"Syntax Error: line {e.lineno}")

    def _print_output(self, text: str) -> None:
        self._output.configure(state="normal")
        self._output.insert("end", text)
        self._output.see("end")
        self._output.configure(state="disabled")

    def _clear_output(self) -> None:
        self._output.configure(state="normal")
        self._output.delete("1.0", "end")
        self._output.configure(state="disabled")

    def _open(self) -> None:
        path = simpledialog.askstring("Open Script",
            "Enter path to Python file:",
            parent=self.wm.root)
        if path and self.wm.vfs.isfile(path):
            self._load(path)

    def _load(self, path: str) -> None:
        try:
            content = self.wm.vfs.read(path)
            self._editor.delete("1.0", "end")
            self._editor.insert("1.0", content)
            self._path = path
            self._path_var.set(path)
            self._highlight()
            self._update_line_nums()
            fname = path.split("/")[-1]
            self.set_title(f"Script Editor — {fname}")
        except Exception as ex:
            messagebox.showerror("Error", str(ex), parent=self.wm.root)

    def _save(self) -> None:
        path = self._path_var.get().strip()
        if not path or path == "Untitled.py":
            path = simpledialog.askstring("Save Script",
                "Save to path:",
                initialvalue="/Users/user/Developer/Scripts/script.py",
                parent=self.wm.root)
            if not path:
                return
        content = self._editor.get("1.0", "end-1c")
        self.wm.vfs.write(path, content)
        self._path = path
        self._path_var.set(path)
        self._modified = False
        self._status_var.set("Saved")
        self.wm.notifs.send("Script Editor", f"Saved to {path}", icon="💾")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 33 — ARCHIVE UTILITY APP
# ─────────────────────────────────────────────────────────────────────────────

class ArchiveUtilityApp(BaseWin):
    """macOS Archive Utility — compress/decompress files in VFS."""

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "Archive Utility", w=560, h=440, icon="🗜️")
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(self.client, text="🗜️  Archive Utility",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=16).pack()
        tk.Label(self.client,
                 text="Compress and expand files in the virtual filesystem.",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 12)).pack()

        # Tabs
        nb = tk.Frame(self.client, bg=T["panel_bg"])
        nb.pack(fill="x", pady=12)
        self._tab = tk.StringVar(value="compress")
        for val, label in [("compress","Compress"),("expand","Expand"),
                            ("list","List Contents")]:
            rb = tk.Radiobutton(nb, text=label, variable=self._tab, value=val,
                                bg=T["panel_bg"], fg=T["text"],
                                selectcolor=T["panel_bg"],
                                font=(FONT_UI, 13), padx=10,
                                command=self._switch_tab)
            rb.pack(side="left")

        self._content = tk.Frame(self.client, bg=T["win_bg"])
        self._content.pack(fill="both", expand=True, padx=20)
        self._switch_tab()

    def _switch_tab(self) -> None:
        for w in self._content.winfo_children():
            w.destroy()
        mode = self._tab.get()
        if mode == "compress":
            self._build_compress()
        elif mode == "expand":
            self._build_expand()
        else:
            self._build_list()

    def _field(self, parent: tk.Widget, label: str, default: str = "") -> tk.Entry:
        row = tk.Frame(parent, bg=T["win_bg"])
        row.pack(fill="x", pady=4)
        tk.Label(row, text=label, bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 12), width=14, anchor="e").pack(side="left")
        e = tk.Entry(row, bg=T["input_bg"], fg=T["text"],
                     font=(FONT_UI, 13), relief="flat",
                     highlightthickness=1,
                     highlightbackground=T["input_border"])
        e.pack(side="left", fill="x", expand=True, padx=8)
        e.insert(0, default)
        return e

    def _build_compress(self) -> None:
        tk.Label(self._content, text="Compress Files",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold"), pady=8).pack(anchor="w")
        self._c_src  = self._field(self._content, "Source path:",
                                    "/Users/user/Documents")
        self._c_dst  = self._field(self._content, "Archive name:",
                                    "/Users/user/Downloads/archive.zip")
        fmt_row = tk.Frame(self._content, bg=T["win_bg"])
        fmt_row.pack(fill="x", pady=4)
        tk.Label(fmt_row, text="Format:", bg=T["win_bg"],
                 fg=T["text"], font=(FONT_UI, 12), width=14, anchor="e").pack(side="left")
        self._c_fmt = ttk.Combobox(fmt_row, values=["ZIP","TAR.GZ","TAR"],
                                    font=(FONT_UI, 12), state="readonly", width=12)
        self._c_fmt.set("ZIP")
        self._c_fmt.pack(side="left", padx=8)
        tk.Button(self._content, text="Compress",
                  bg=T["accent"], fg="#ffffff",
                  font=(FONT_UI, 13), relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=self._do_compress).pack(pady=12)
        self._c_log = tk.Text(self._content, height=6,
                               bg=T["panel_bg"], fg=T["text"],
                               font=(FONT_MONO, 11), relief="flat",
                               state="disabled")
        self._c_log.pack(fill="x")

    def _do_compress(self) -> None:
        src  = self._c_src.get().strip()
        dst  = self._c_dst.get().strip()
        fmt  = self._c_fmt.get()
        if not src or not dst:
            return
        if not self.wm.vfs.exists(src):
            self._c_log_msg(f"❌  Source not found: {src}\n")
            return
        # Simulate compression
        import io as _io
        buf  = _io.BytesIO()
        size = 0
        try:
            if self.wm.vfs.isfile(src):
                files = [(src, self.wm.vfs.read(src))]
            else:
                files = []
                for path in self.wm.vfs.find(src, ".*"):
                    if self.wm.vfs.isfile(path):
                        files.append((path, self.wm.vfs.read(path)))
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for path, content in files:
                    arc_name = path.replace(src, "").lstrip("/")
                    zf.writestr(arc_name or path.split("/")[-1], content)
                    size += len(content)
            # Store zip as base64 in VFS
            compressed = base64.b64encode(buf.getvalue()).decode()
            self.wm.vfs.write(dst, compressed)
            ratio = len(compressed) / max(size, 1)
            self._c_log_msg(
                f"✅  Archive created: {dst}\n"
                f"    Files: {len(files)}  |  "
                f"Original: {size} B  |  "
                f"Compressed: {len(buf.getvalue())} B  |  "
                f"Ratio: {ratio:.2f}x\n"
            )
            self.wm.notifs.send("Archive Utility",
                                 f"Archive created: {dst.split('/')[-1]}", icon="🗜️")
        except Exception as ex:
            self._c_log_msg(f"❌  Error: {ex}\n")

    def _c_log_msg(self, msg: str) -> None:
        self._c_log.configure(state="normal")
        self._c_log.insert("end", msg)
        self._c_log.see("end")
        self._c_log.configure(state="disabled")

    def _build_expand(self) -> None:
        tk.Label(self._content, text="Expand Archive",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold"), pady=8).pack(anchor="w")
        self._e_src = self._field(self._content, "Archive path:",
                                   "/Users/user/Downloads/archive.zip")
        self._e_dst = self._field(self._content, "Extract to:",
                                   "/Users/user/Downloads/")
        tk.Button(self._content, text="Expand",
                  bg=T["accent"], fg="#ffffff",
                  font=(FONT_UI, 13), relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=self._do_expand).pack(pady=12)
        self._e_log = tk.Text(self._content, height=6,
                               bg=T["panel_bg"], fg=T["text"],
                               font=(FONT_MONO, 11), relief="flat",
                               state="disabled")
        self._e_log.pack(fill="x")

    def _do_expand(self) -> None:
        src = self._e_src.get().strip()
        dst = self._e_dst.get().strip()
        if not self.wm.vfs.isfile(src):
            self._e_log_msg(f"❌  Archive not found: {src}\n")
            return
        try:
            raw = base64.b64decode(self.wm.vfs.read(src))
            import io as _io
            with zipfile.ZipFile(_io.BytesIO(raw)) as zf:
                for name in zf.namelist():
                    content = zf.read(name).decode("utf-8", errors="replace")
                    out_path = dst.rstrip("/") + "/" + name
                    self.wm.vfs.write(out_path, content)
                    self._e_log_msg(f"  ✅  {out_path}\n")
            self._e_log_msg(f"Done — extracted to {dst}\n")
            self.wm.notifs.send("Archive Utility", "Archive expanded.", icon="📂")
        except Exception as ex:
            self._e_log_msg(f"❌  Error: {ex}\n")

    def _e_log_msg(self, msg: str) -> None:
        self._e_log.configure(state="normal")
        self._e_log.insert("end", msg)
        self._e_log.see("end")
        self._e_log.configure(state="disabled")

    def _build_list(self) -> None:
        tk.Label(self._content, text="List Archive Contents",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold"), pady=8).pack(anchor="w")
        self._l_src = self._field(self._content, "Archive path:",
                                   "/Users/user/Downloads/archive.zip")
        tk.Button(self._content, text="List Contents",
                  bg=T["accent"], fg="#ffffff",
                  font=(FONT_UI, 13), relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=self._do_list).pack(pady=12)
        self._l_log = tk.Text(self._content, height=8,
                               bg=T["panel_bg"], fg=T["text"],
                               font=(FONT_MONO, 11), relief="flat",
                               state="disabled")
        self._l_log.pack(fill="x")

    def _do_list(self) -> None:
        src = self._l_src.get().strip()
        if not self.wm.vfs.isfile(src):
            self._l_log_msg(f"❌  File not found: {src}\n")
            return
        try:
            raw = base64.b64decode(self.wm.vfs.read(src))
            import io as _io
            with zipfile.ZipFile(_io.BytesIO(raw)) as zf:
                self._l_log_msg(f"Archive: {src}\n{'─'*40}\n")
                for info in zf.infolist():
                    self._l_log_msg(
                        f"  {info.filename:<40}  {info.file_size:>8} B\n"
                    )
                self._l_log_msg(f"{'─'*40}\n{len(zf.namelist())} files\n")
        except Exception as ex:
            self._l_log_msg(f"❌  Error: {ex}\n")

    def _l_log_msg(self, msg: str) -> None:
        self._l_log.configure(state="normal")
        self._l_log.insert("end", msg)
        self._l_log.see("end")
        self._l_log.configure(state="disabled")



# =============================================================================
#  MacPyOS — PART 4
#  Keychain Access, Numbers, Photos, Disk Utility, Script Editor
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 30 — KEYCHAIN ACCESS
# ─────────────────────────────────────────────────────────────────────────────

class KeychainApp(BaseWin):
    """macOS Keychain Access — password manager."""

    CATEGORIES = ["All Items","Passwords","Secure Notes","Certificates","Keys"]

    def __init__(self, wm):
        super().__init__(wm,title="Keychain Access",w=700,h=480,icon="key")
        self._items = [
            {"name":"iCloud","account":"user@icloud.com","kind":"Internet Password",
             "where":"icloud.com","pw":"••••••••","created":time.time()-864000},
            {"name":"GitHub","account":"user@github.com","kind":"Internet Password",
             "where":"github.com","pw":"••••••••","created":time.time()-432000},
            {"name":"Wi-Fi Home","account":"HomeNetwork","kind":"Network Password",
             "where":"AirPort","pw":"••••••••","created":time.time()-1296000},
            {"name":"App Store","account":"user@apple.com","kind":"Internet Password",
             "where":"apple.com","pw":"••••••••","created":time.time()-259200},
            {"name":"Gmail","account":"user@gmail.com","kind":"Internet Password",
             "where":"google.com","pw":"••••••••","created":time.time()-172800},
            {"name":"Secure Note","account":"","kind":"Secure Note",
             "where":"","pw":"PIN: 1234","created":time.time()-86400},
        ]
        self._selected = None
        self._category = "All Items"
        self._build_ui()

    def _build_ui(self):
        c = self.client
        # Toolbar
        toolbar = tk.Frame(c,bg=T["panel_bg"],
                           highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        def tb_btn(text,cmd,tip=""):
            b = tk.Label(toolbar,text=text,bg=T["panel_bg"],fg=T["text"],
                         font=(FONT_UI,12),padx=8,pady=5,cursor="hand2")
            b.pack(side="left"); b.bind("<Button-1>",lambda _: cmd())
            if tip: make_tooltip(b,tip)
        tb_btn("+ Add",self._add_item,"Add new item")
        tb_btn("- Delete",self._delete_item,"Delete selected")
        tb_btn("Show Info",self._show_info,"Show item info")
        self._search_var = tk.StringVar()
        se = tk.Entry(toolbar,textvariable=self._search_var,bg=T["input_bg"],
                      fg=T["text"],font=(FONT_UI,12),relief="flat",
                      highlightthickness=1,highlightbackground=T["input_border"],
                      highlightcolor=T["input_focus"],width=20)
        se.pack(side="right",padx=8,pady=4)
        tk.Label(toolbar,text="Search",bg=T["panel_bg"],fg=T["text_muted"],
                 font=(FONT_UI,11)).pack(side="right")
        self._search_var.trace_add("write",lambda *_: self._refresh_list())

        pane = tk.Frame(c,bg=T["win_bg"])
        pane.pack(fill="both",expand=True)

        # Category sidebar
        sidebar = tk.Frame(pane,bg=T["sidebar_bg"],width=170)
        sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
        tk.Label(sidebar,text="Keychains",bg=T["sidebar_bg"],fg=T["text"],
                 font=(FONT_UI,12,"bold"),padx=12,pady=6).pack(anchor="w")
        icons={"All Items":"[All]","Passwords":"[PW]","Secure Notes":"[N]",
               "Certificates":"[C]","Keys":"[K]"}
        for cat in self.CATEGORIES:
            row = tk.Frame(sidebar,bg=T["sidebar_bg"],cursor="hand2")
            row.pack(fill="x")
            tk.Label(row,text=icons.get(cat,"[?]"),bg=T["sidebar_bg"],
                     fg=T["accent"],font=(FONT_UI,11),padx=8).pack(side="left")
            lbl = tk.Label(row,text=cat,bg=T["sidebar_bg"],fg=T["text"],
                           font=(FONT_UI,12),anchor="w",pady=4)
            lbl.pack(side="left",fill="x",expand=True)
            for w in (row,lbl):
                w.bind("<Button-1>",lambda _,cc=cat: self._set_category(cc))
                w.bind("<Enter>",lambda _,r=row: r.configure(bg=T["menu_hover"]))
                w.bind("<Leave>",lambda _,r=row: r.configure(bg=T["sidebar_bg"]))

        tk.Frame(pane,bg=T["separator"],width=1).pack(side="left",fill="y")

        # Item list
        right = tk.Frame(pane,bg=T["win_bg"])
        right.pack(side="left",fill="both",expand=True)
        # Column headers
        headers = tk.Frame(right,bg=T["panel_alt"],
                           highlightthickness=1,highlightbackground=T["separator"])
        headers.pack(fill="x")
        for col,w in [("Name",180),("Account",160),("Kind",140),("Where",120)]:
            tk.Label(headers,text=col,bg=T["panel_alt"],fg=T["text_muted"],
                     font=(FONT_UI,11,"bold"),width=w//7,anchor="w",padx=4).pack(side="left")
        self._list_frame = MacScrolledFrame(right,bg=T["win_bg"])
        self._list_frame.pack(fill="both",expand=True)
        self._list_inner = self._list_frame.inner
        self._list_inner.configure(bg=T["win_bg"])
        self._refresh_list()

        # Detail pane at bottom
        self._detail = tk.Frame(c,bg=T["panel_bg"],height=100,
                                highlightthickness=1,highlightbackground=T["separator"])
        self._detail.pack(fill="x")
        self._detail.pack_propagate(False)
        self._detail_lbl = tk.Label(self._detail,text="Select an item to view details",
                                    bg=T["panel_bg"],fg=T["text_muted"],font=(FONT_UI,12))
        self._detail_lbl.pack(expand=True)

    def _set_category(self,cat):
        self._category = cat; self._refresh_list()

    def _refresh_list(self):
        for w in self._list_inner.winfo_children(): w.destroy()
        q = self._search_var.get().lower() if hasattr(self,"_search_var") else ""
        for i,item in enumerate(self._items):
            if self._category!="All Items" and self._category not in item["kind"]: continue
            if q and q not in item["name"].lower() and q not in item["account"].lower(): continue
            is_sel=(i==self._selected)
            bg = T["selection"] if is_sel else (T["win_bg"] if i%2==0 else T["panel_bg"])
            row = tk.Frame(self._list_inner,bg=bg,cursor="hand2")
            row.pack(fill="x")
            row.bind("<Button-1>",lambda _,idx=i: self._select(idx))
            for val,width in [(item["name"],180),(item["account"],160),
                               (item["kind"],140),(item["where"],120)]:
                lbl = tk.Label(row,text=val[:22],bg=bg,fg=T["text"],
                               font=(FONT_UI,12),width=width//7,anchor="w",padx=4,pady=4)
                lbl.pack(side="left")
                lbl.bind("<Button-1>",lambda _,idx=i: self._select(idx))

    def _select(self,idx):
        self._selected=idx
        item = self._items[idx]
        ts = datetime.datetime.fromtimestamp(item["created"]).strftime("%B %d, %Y")
        self._detail_lbl.configure(
            text=f"  Name: {item['name']}   Account: {item['account']}   Kind: {item['kind']}   Created: {ts}")
        self._refresh_list()

    def _add_item(self):
        dlg = tk.Toplevel(self.wm.root); dlg.title("Add Password")
        dlg.geometry("380x280"); dlg.configure(bg=T["win_bg"]); dlg.transient(self.wm.root)
        fields={}
        for label,key in [("Name:","name"),("Account:","account"),("Where:","where"),("Password:","pw")]:
            row=tk.Frame(dlg,bg=T["win_bg"]); row.pack(fill="x",padx=16,pady=4)
            tk.Label(row,text=label,bg=T["win_bg"],fg=T["text"],
                     font=(FONT_UI,12),width=10,anchor="e").pack(side="left")
            show = "*" if key=="pw" else ""
            e=tk.Entry(row,bg=T["input_bg"],fg=T["text"],font=(FONT_UI,13),
                       relief="flat",show=show,
                       highlightthickness=1,highlightbackground=T["input_border"])
            e.pack(side="left",fill="x",expand=True); fields[key]=e
        def save():
            item={k:v.get() for k,v in fields.items()}
            item["kind"]="Internet Password"; item["created"]=time.time()
            self._items.append(item); dlg.destroy(); self._refresh_list()
        tk.Button(dlg,text="Add",bg=T["accent"],fg="#ffffff",font=(FONT_UI,13),
                  relief="flat",command=save).pack(pady=12)

    def _delete_item(self):
        if self._selected is not None:
            if messagebox.askyesno("Delete","Delete this keychain item?",parent=self.wm.root):
                self._items.pop(self._selected); self._selected=None; self._refresh_list()

    def _show_info(self):
        if self._selected is None:
            self.wm.notifs.send("Keychain","Select an item first.",icon="key"); return
        item = self._items[self._selected]
        result = messagebox.askyesno("Show Password",
            f"Name: {item['name']}\nAccount: {item['account']}\n\nShow password?",
            parent=self.wm.root)
        if result:
            messagebox.showinfo("Password",f"Password: {item['pw']}",parent=self.wm.root)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 31 — NUMBERS (SPREADSHEET)
# ─────────────────────────────────────────────────────────────────────────────

class NumbersApp(BaseWin):
    """macOS Numbers — spreadsheet editor."""

    COLS = list("ABCDEFGHIJ")
    ROWS = 30

    def __init__(self, wm, path=None):
        super().__init__(wm,title="Numbers",w=800,h=560,icon="spreadsheet")
        self._path = path
        self._data: Dict[str,str] = {}
        self._selected_cell = None
        self._formula_var = tk.StringVar()
        if path and wm.vfs.isfile(path):
            self._load_csv(wm.vfs.read(path))
        self._build_ui()

    def _load_csv(self,content):
        lines = content.strip().split("\n")
        for r,line in enumerate(lines):
            for c,val in enumerate(line.split(",")):
                if c < len(self.COLS):
                    self._data[f"{self.COLS[c]}{r+1}"] = val.strip()

    def _build_ui(self):
        c = self.client
        # Toolbar
        toolbar = tk.Frame(c,bg=T["panel_bg"],
                           highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        for text,cmd,tip in [("New",self._new_sheet,"New"),("Open",self._open_file,"Open"),
                               ("Save",self._save_file,"Save"),("Export CSV",self._export_csv,"Export")]:
            b = tk.Label(toolbar,text=text,bg=T["panel_bg"],fg=T["text"],
                         font=(FONT_UI,12),padx=8,pady=5,cursor="hand2")
            b.pack(side="left"); b.bind("<Button-1>",lambda _,fn=cmd: fn()); make_tooltip(b,tip)
        # Formula bar
        formula_bar = tk.Frame(c,bg=T["panel_alt"],
                               highlightthickness=1,highlightbackground=T["separator"])
        formula_bar.pack(fill="x")
        self._cell_ref_lbl = tk.Label(formula_bar,text="  A1  ",bg=T["panel_alt"],
                                       fg=T["text"],font=(FONT_MONO,12),padx=4)
        self._cell_ref_lbl.pack(side="left")
        tk.Frame(formula_bar,bg=T["separator"],width=1,height=20).pack(side="left",pady=3)
        tk.Label(formula_bar,text=" fx ",bg=T["panel_alt"],fg=T["accent"],
                 font=(FONT_UI,12,"italic")).pack(side="left")
        self._formula_entry = tk.Entry(formula_bar,textvariable=self._formula_var,
                                       bg=T["input_bg"],fg=T["text"],
                                       font=(FONT_MONO,12),relief="flat",
                                       highlightthickness=0,
                                       insertbackground=T["text"])
        self._formula_entry.pack(side="left",fill="x",expand=True,padx=4,pady=3)
        self._formula_entry.bind("<Return>",self._commit_formula)

        # Sheet area
        sheet_container = tk.Frame(c,bg=T["win_bg"])
        sheet_container.pack(fill="both",expand=True)

        # Row number column
        row_header_frame = tk.Frame(sheet_container,bg=T["panel_alt"],width=40)
        row_header_frame.pack(side="left",fill="y"); row_header_frame.pack_propagate(False)

        # Canvas + scrollbars
        hscroll = tk.Scrollbar(sheet_container,orient="horizontal")
        hscroll.pack(side="bottom",fill="x")
        vscroll = tk.Scrollbar(sheet_container,orient="vertical")
        vscroll.pack(side="right",fill="y")
        self._cv = tk.Canvas(sheet_container,bg=T["win_bg"],
                             xscrollcommand=hscroll.set,
                             yscrollcommand=vscroll.set,
                             highlightthickness=0)
        self._cv.pack(fill="both",expand=True)
        hscroll.configure(command=self._cv.xview)
        vscroll.configure(command=self._cv.yview)

        self._cell_w = 96; self._cell_h = 24
        self._cells: Dict[str,tk.Entry] = {}
        self._draw_sheet()
        self._cv.configure(scrollregion=(0,0,
                                         len(self.COLS)*self._cell_w+40,
                                         self.ROWS*self._cell_h+28))
        self._cv.bind("<Button-1>",self._on_canvas_click)

    def _draw_sheet(self):
        self._cv.delete("all")
        cw = self._cell_w; ch = self._cell_h
        # Column headers
        for ci,col in enumerate(self.COLS):
            x = ci*cw+40
            self._cv.create_rectangle(x,0,x+cw,ch,
                                       fill=T["panel_alt"],outline=T["separator"])
            self._cv.create_text(x+cw//2,ch//2,text=col,
                                  fill=T["text_muted"],font=(FONT_UI,11,"bold"))
        # Row headers + cells
        for ri in range(self.ROWS):
            y = ri*ch+ch
            # Row number
            self._cv.create_rectangle(0,y,40,y+ch,
                                       fill=T["panel_alt"],outline=T["separator"])
            self._cv.create_text(20,y+ch//2,text=str(ri+1),
                                  fill=T["text_muted"],font=(FONT_UI,10))
            for ci,col in enumerate(self.COLS):
                x = ci*cw+40
                key = f"{col}{ri+1}"
                is_sel = (key==self._selected_cell)
                bg = T["selection"] if is_sel else T["win_bg"]
                self._cv.create_rectangle(x,y,x+cw,y+ch,
                                           fill=bg,outline=T["separator"])
                val = self._data.get(key,"")
                color = T["text"]
                # Color-code numbers
                try:
                    float(val.replace(",","").replace("$",""))
                    color = T["chart1"] if ri>0 else T["text_muted"]
                except: pass
                if val:
                    self._cv.create_text(x+4,y+ch//2,text=str(val)[:12],
                                          anchor="w",fill=color,font=(FONT_UI,11))

    def _on_canvas_click(self,e):
        cw=self._cell_w; ch=self._cell_h
        ci=int((e.x-40)//cw); ri=int((e.y-ch)//ch)
        if 0<=ci<len(self.COLS) and 0<=ri<self.ROWS:
            col=self.COLS[ci]; key=f"{col}{ri+1}"
            self._selected_cell=key
            self._cell_ref_lbl.configure(text=f"  {key}  ")
            val=self._data.get(key,"")
            self._formula_var.set(val)
            self._formula_entry.focus_set()
            self._formula_entry.icursor("end")
            self._draw_sheet()

    def _commit_formula(self,event=None):
        if self._selected_cell:
            val = self._formula_var.get()
            if val.startswith("="):
                val = self._eval_formula(val[1:])
            self._data[self._selected_cell] = val
            self._draw_sheet()

    def _eval_formula(self,expr):
        try:
            # Replace cell refs like A1, B2 etc.
            def replace_ref(m):
                ref = m.group(0)
                return self._data.get(ref.upper(),"0") or "0"
            expr2 = re.sub(r'[A-J]\d+',replace_ref,expr,flags=re.IGNORECASE)
            # SUM(A1:A5)
            def sum_range(m):
                c1,r1,c2,r2 = m.group(1),int(m.group(2)),m.group(3),int(m.group(4))
                total=0
                for r in range(r1,r2+1):
                    try: total+=float(self._data.get(f"{c1.upper()}{r}","0") or "0")
                    except: pass
                return str(total)
            expr2 = re.sub(r'SUM\(([A-J])(\d+):([A-J])(\d+)\)',sum_range,expr2,flags=re.IGNORECASE)
            result = eval(expr2)
            if isinstance(result,float) and result==int(result): return str(int(result))
            return str(round(result,4))
        except: return "ERROR"

    def _new_sheet(self):
        self._data.clear(); self._draw_sheet()

    def _open_file(self):
        path = simpledialog.askstring("Open","Path:",parent=self.wm.root)
        if path and self.wm.vfs.isfile(path):
            content = self.wm.vfs.read(path)
            self._load_csv(content); self._draw_sheet()

    def _save_file(self):
        if not self._path:
            self._path = simpledialog.askstring("Save As","Path:",parent=self.wm.root)
        if self._path:
            max_r = max((int(k[1:]) for k in self._data if k[1:].isdigit()),default=1)
            lines=[]
            for r in range(1,max_r+1):
                row=[self._data.get(f"{c}{r}","") for c in self.COLS]
                lines.append(",".join(row))
            self.wm.vfs.write(self._path,"\n".join(lines))
            self.wm.notifs.send("Numbers",f"Saved to {self._path}",icon="spreadsheet")

    def _export_csv(self):
        self._save_file()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 32 — PHOTOS APP
# ─────────────────────────────────────────────────────────────────────────────

class PhotosApp(BaseWin):
    """macOS Photos — generative photo gallery."""

    ALBUMS = ["Recents","Favourites","People","Places","Videos","Screenshots"]

    def __init__(self, wm):
        super().__init__(wm,title="Photos",w=780,h=560,icon="photo")
        self._album = "Recents"
        self._selected = None
        self._photos = self._gen_photos()
        self._build_ui()

    def _gen_photos(self):
        photos=[]
        captions=["Sunset at the beach","Mountain hike","Coffee morning","City lights",
                  "Garden in bloom","Rainy day","Autumn leaves","Snowy peaks","Ocean view",
                  "Desert road","Forest trail","Starry night","Golden hour","River bend",
                  "Misty morning","Harbor view","Valley green","Cliff edge","Sand dunes","Lakeside"]
        palettes=[["#ff6b6b","#ffa94d"],["#74b9ff","#a29bfe"],["#55efc4","#00b894"],
                  ["#fdcb6e","#e17055"],["#fd79a8","#e84393"],["#2d3436","#636e72"]]
        for i,cap in enumerate(captions):
            pal=palettes[i%len(palettes)]
            photos.append({"id":i,"caption":cap,"color1":pal[0],"color2":pal[1],
                           "ts":time.time()-i*86400,"fav":i%5==0})
        return photos

    def _build_ui(self):
        c = self.client
        pane = tk.Frame(c,bg=T["win_bg"])
        pane.pack(fill="both",expand=True)

        # Sidebar
        sidebar = tk.Frame(pane,bg=T["sidebar_bg"],width=180)
        sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
        tk.Label(sidebar,text="Library",bg=T["sidebar_bg"],fg=T["text"],
                 font=(FONT_UI,13,"bold"),padx=12,pady=8).pack(anchor="w")
        for album in self.ALBUMS:
            row=tk.Frame(sidebar,bg=T["sidebar_bg"],cursor="hand2")
            row.pack(fill="x")
            icon_map={"Recents":"[R]","Favourites":"[*]","People":"[P]",
                      "Places":"[Map]","Videos":"[V]","Screenshots":"[S]"}
            tk.Label(row,text=icon_map.get(album,"[A]"),bg=T["sidebar_bg"],
                     fg=T["accent"],font=(FONT_UI,11),padx=8).pack(side="left")
            lbl=tk.Label(row,text=album,bg=T["sidebar_bg"],fg=T["text"],
                         font=(FONT_UI,12),anchor="w",pady=4)
            lbl.pack(side="left",fill="x",expand=True)
            for w in (row,lbl):
                w.bind("<Button-1>",lambda _,a=album: self._set_album(a))
                w.bind("<Enter>",lambda _,r=row: r.configure(bg=T["menu_hover"]))
                w.bind("<Leave>",lambda _,r=row: r.configure(bg=T["sidebar_bg"]))

        tk.Frame(pane,bg=T["separator"],width=1).pack(side="left",fill="y")

        # Main area
        main = tk.Frame(pane,bg=T["win_bg"])
        main.pack(side="left",fill="both",expand=True)

        # Toolbar
        tb = tk.Frame(main,bg=T["panel_bg"],
                      highlightthickness=1,highlightbackground=T["separator"])
        tb.pack(fill="x")
        self._album_title = tk.Label(tb,text="Recents",bg=T["panel_bg"],
                                      fg=T["text"],font=(FONT_UI,14,"bold"),
                                      padx=12,pady=6)
        self._album_title.pack(side="left")
        tk.Label(tb,text=f"{len(self._photos)} Photos",bg=T["panel_bg"],
                 fg=T["text_muted"],font=(FONT_UI,11)).pack(side="left")
        self._search_var=tk.StringVar()
        se=tk.Entry(tb,textvariable=self._search_var,bg=T["input_bg"],fg=T["text"],
                    font=(FONT_UI,12),relief="flat",highlightthickness=1,
                    highlightbackground=T["input_border"],highlightcolor=T["input_focus"],width=18)
        se.pack(side="right",padx=8,pady=4)
        tk.Label(tb,text="Search",bg=T["panel_bg"],fg=T["text_muted"],
                 font=(FONT_UI,11)).pack(side="right")
        self._search_var.trace_add("write",lambda *_: self._refresh_grid())

        # Grid
        self._grid_sf = MacScrolledFrame(main,bg=T["win_bg"])
        self._grid_sf.pack(fill="both",expand=True)
        self._grid_inner = self._grid_sf.inner
        self._grid_inner.configure(bg=T["win_bg"])
        self._refresh_grid()

    def _set_album(self,album):
        self._album=album
        self._album_title.configure(text=album)
        self._refresh_grid()

    def _refresh_grid(self):
        for w in self._grid_inner.winfo_children(): w.destroy()
        q=self._search_var.get().lower() if hasattr(self,"_search_var") else ""
        photos=self._photos
        if self._album=="Favourites": photos=[p for p in photos if p["fav"]]
        if q: photos=[p for p in photos if q in p["caption"].lower()]

        THUMB=100; COLS_N=5; pad=4
        row_frame=None
        for i,photo in enumerate(photos):
            if i%COLS_N==0:
                row_frame=tk.Frame(self._grid_inner,bg=T["win_bg"])
                row_frame.pack(fill="x",pady=pad,padx=pad)
            cell=tk.Frame(row_frame,bg=T["win_bg"],cursor="hand2")
            cell.pack(side="left",padx=pad)
            # Thumbnail (gradient rectangle on canvas)
            cv=tk.Canvas(cell,width=THUMB,height=THUMB,
                         bg=T["win_bg"],highlightthickness=0)
            cv.pack()
            steps=10
            for s in range(steps):
                t=s/steps
                r1=int(photo["color1"][1:3],16); g1=int(photo["color1"][3:5],16); b1=int(photo["color1"][5:7],16)
                r2=int(photo["color2"][1:3],16); g2=int(photo["color2"][3:5],16); b2=int(photo["color2"][5:7],16)
                rc=int(r1+(r2-r1)*t); gc=int(g1+(g2-g1)*t); bc=int(b1+(b2-b1)*t)
                color=f"#{rc:02x}{gc:02x}{bc:02x}"
                y0=s*THUMB//steps; y1=(s+1)*THUMB//steps
                cv.create_rectangle(0,y0,THUMB,y1,fill=color,outline="")
            # Heart if fav
            if photo["fav"]:
                cv.create_text(THUMB-8,8,text="*",anchor="ne",
                               fill="#ffffff",font=(FONT_UI,14))
            tk.Label(cell,text=photo["caption"][:14],bg=T["win_bg"],
                     fg=T["text_muted"],font=(FONT_UI,9)).pack()
            for w in (cell,cv):
                w.bind("<Double-Button-1>",lambda _,p=photo: self._open_photo(p))

    def _open_photo(self,photo):
        dlg=tk.Toplevel(self.wm.root); dlg.title(photo["caption"])
        dlg.geometry("500x480"); dlg.configure(bg="#000000"); dlg.transient(self.wm.root)
        cv=tk.Canvas(dlg,bg="#000000",highlightthickness=0)
        cv.pack(fill="both",expand=True)
        cv.update_idletasks()
        w=cv.winfo_width() or 500; h=cv.winfo_height() or 420
        steps=20
        for s in range(steps):
            t=s/steps
            r1=int(photo["color1"][1:3],16); g1=int(photo["color1"][3:5],16); b1=int(photo["color1"][5:7],16)
            r2=int(photo["color2"][1:3],16); g2=int(photo["color2"][3:5],16); b2=int(photo["color2"][5:7],16)
            rc=int(r1+(r2-r1)*t); gc=int(g1+(g2-g1)*t); bc=int(b1+(b2-b1)*t)
            color=f"#{rc:02x}{gc:02x}{bc:02x}"
            y0=s*h//steps; y1=(s+1)*h//steps
            cv.create_rectangle(0,y0,w,y1,fill=color,outline="")
        cv.create_text(w//2,h//2,text=photo["caption"],fill="#ffffff",
                       font=(FONT_UI,18,"bold"),anchor="center")
        ts=datetime.datetime.fromtimestamp(photo["ts"]).strftime("%B %d, %Y")
        cv.create_text(w//2,h//2+30,text=ts,fill="#ffffff",
                       font=(FONT_UI,12),anchor="center")
        btn_frame=tk.Frame(dlg,bg="#000000"); btn_frame.pack(fill="x")
        def toggle_fav():
            photo["fav"]=not photo["fav"]
            self._refresh_grid()
        tk.Button(btn_frame,text="Favourite" if not photo["fav"] else "Unfavourite",
                  bg=T["accent2"],fg="#ffffff",font=(FONT_UI,12),
                  relief="flat",padx=12,pady=4,command=toggle_fav).pack(side="left",padx=8,pady=6)
        tk.Button(btn_frame,text="Share",bg=T["accent"],fg="#ffffff",
                  font=(FONT_UI,12),relief="flat",padx=12,pady=4,
                  command=lambda: self.wm.notifs.send("Photos","Photo shared!",icon="photo")).pack(side="left")
        tk.Button(btn_frame,text="Close",bg=T["button_secondary"],fg=T["text"],
                  font=(FONT_UI,12),relief="flat",padx=12,pady=4,
                  command=dlg.destroy).pack(side="right",padx=8)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 33 — DISK UTILITY
# ─────────────────────────────────────────────────────────────────────────────

class DiskUtilityApp(BaseWin):
    """macOS Disk Utility."""

    DISKS=[
        {"name":"MacPyOS SSD","dev":"/dev/disk0","size":512,"used":128,"type":"APFS","healthy":True},
        {"name":"Backup Drive","dev":"/dev/disk1","size":1000,"used":320,"type":"HFS+","healthy":True},
        {"name":"USB Flash","dev":"/dev/disk2","size":32,"used":8,"type":"ExFAT","healthy":False},
    ]

    def __init__(self, wm):
        super().__init__(wm,title="Disk Utility",w=680,h=500,icon="disk")
        self._selected=0; self._build_ui()

    def _build_ui(self):
        c=self.client
        # Toolbar
        toolbar=tk.Frame(c,bg=T["panel_bg"],
                         highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        for text,cmd,tip in [("First Aid",self._first_aid,"Run First Aid"),
                               ("Partition",self._partition,"Partition"),
                               ("Erase",self._erase,"Erase disk"),
                               ("Mount",self._mount,"Mount"),
                               ("Unmount",self._unmount,"Unmount"),
                               ("Info",self._info,"Get Info")]:
            b=tk.Label(toolbar,text=text,bg=T["panel_bg"],fg=T["text"],
                       font=(FONT_UI,12),padx=8,pady=5,cursor="hand2")
            b.pack(side="left"); b.bind("<Button-1>",lambda _,fn=cmd: fn()); make_tooltip(b,tip)
        pane=tk.Frame(c,bg=T["win_bg"]); pane.pack(fill="both",expand=True)
        # Disk list sidebar
        sidebar=tk.Frame(pane,bg=T["sidebar_bg"],width=210)
        sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
        tk.Label(sidebar,text="Devices",bg=T["sidebar_bg"],fg=T["text"],
                 font=(FONT_UI,12,"bold"),padx=12,pady=8).pack(anchor="w")
        self._disk_btns=[]
        for i,disk in enumerate(self.DISKS):
            row=tk.Frame(sidebar,bg=T["sidebar_bg"],cursor="hand2")
            row.pack(fill="x")
            health=T["accent3"] if disk["healthy"] else T["danger"]
            tk.Label(row,text="*",bg=T["sidebar_bg"],fg=health,
                     font=(FONT_UI,16),padx=8).pack(side="left")
            info=tk.Frame(row,bg=T["sidebar_bg"])
            info.pack(side="left",fill="x",expand=True,pady=4)
            tk.Label(info,text=disk["name"],bg=T["sidebar_bg"],fg=T["text"],
                     font=(FONT_UI,12,"bold"),anchor="w").pack(anchor="w")
            tk.Label(info,text=f"{disk['dev']}  {disk['size']} GB",
                     bg=T["sidebar_bg"],fg=T["text_muted"],font=(FONT_UI,10)).pack(anchor="w")
            for w in (row,info):
                w.bind("<Button-1>",lambda _,idx=i: self._select_disk(idx))
                w.bind("<Enter>",lambda _,r=row: r.configure(bg=T["menu_hover"]))
                w.bind("<Leave>",lambda _,r=row: r.configure(bg=T["sidebar_bg"]))
        tk.Frame(pane,bg=T["separator"],width=1).pack(side="left",fill="y")
        self._detail=tk.Frame(pane,bg=T["win_bg"])
        self._detail.pack(side="left",fill="both",expand=True)
        self._select_disk(0)

    def _select_disk(self,idx):
        self._selected=idx
        for w in self._detail.winfo_children(): w.destroy()
        disk=self.DISKS[idx]
        # Header
        tk.Label(self._detail,text=disk["name"],bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=16).pack()
        # Usage chart
        cv=tk.Canvas(self._detail,width=340,height=40,
                     bg=T["win_bg"],highlightthickness=0)
        cv.pack()
        bar_w=320; bar_h=24; bx=10; by=8
        pct=disk["used"]/disk["size"]
        cv.create_rectangle(bx,by,bx+bar_w,by+bar_h,fill=T["progress_bg"],outline=T["separator"])
        fill_color=T["accent3"] if pct<0.7 else (T["warning"] if pct<0.9 else T["danger"])
        cv.create_rectangle(bx,by,bx+int(bar_w*pct),by+bar_h,fill=fill_color,outline="")
        cv.create_text(bx+bar_w//2,by+bar_h//2,
                       text=f"{disk['used']} GB / {disk['size']} GB used",
                       fill=T["text"],font=(FONT_UI,11))
        # Details
        details_frame=tk.Frame(self._detail,bg=T["win_bg"])
        details_frame.pack(fill="x",padx=24,pady=12)
        health_str="Verified" if disk["healthy"] else "ERRORS FOUND"
        health_col=T["accent3"] if disk["healthy"] else T["danger"]
        for label,val,col in [
            ("Device:",disk["dev"],T["text"]),
            ("Capacity:",f"{disk['size']} GB",T["text"]),
            ("Available:",f"{disk['size']-disk['used']} GB",T["accent3"]),
            ("Used:",f"{disk['used']} GB",T["text"]),
            ("Format:",disk["type"],T["text"]),
            ("Health:",health_str,health_col),
            ("Mount Point:","/Volumes/"+disk["name"],T["text"]),
        ]:
            row=tk.Frame(details_frame,bg=T["win_bg"])
            row.pack(fill="x",pady=2)
            tk.Label(row,text=label,bg=T["win_bg"],fg=T["text_muted"],
                     font=(FONT_UI,12),width=14,anchor="e").pack(side="left")
            tk.Label(row,text=val,bg=T["win_bg"],fg=col,
                     font=(FONT_UI,12)).pack(side="left",padx=8)

    def _first_aid(self):
        disk=self.DISKS[self._selected]
        self.wm.notifs.send("Disk Utility",
                             f"Running First Aid on {disk['name']}...",icon="disk")
        self.wm.root.after(2000,lambda:
            self.wm.notifs.send("Disk Utility",
                                 f"{disk['name']}: No errors found.",icon="disk"))

    def _erase(self):
        disk=self.DISKS[self._selected]
        if messagebox.askyesno("Erase",
                                f"Erase '{disk['name']}'? This cannot be undone.",
                                parent=self.wm.root):
            disk["used"]=0
            self.wm.notifs.send("Disk Utility",f"{disk['name']} erased.",icon="disk")
            self._select_disk(self._selected)

    def _partition(self):
        self.wm.notifs.send("Disk Utility","Partitioning not available in simulation.",icon="disk")

    def _mount(self):
        self.wm.notifs.send("Disk Utility",
                             f"{self.DISKS[self._selected]['name']} mounted.",icon="disk")

    def _unmount(self):
        self.wm.notifs.send("Disk Utility",
                             f"{self.DISKS[self._selected]['name']} unmounted.",icon="disk")

    def _info(self):
        disk=self.DISKS[self._selected]
        messagebox.showinfo("Disk Info",
                             f"Name: {disk['name']}\nDevice: {disk['dev']}\n"
                             f"Size: {disk['size']} GB\nFormat: {disk['type']}\n"
                             f"Health: {'OK' if disk['healthy'] else 'ERRORS'}",
                             parent=self.wm.root)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 34 — SCRIPT EDITOR
# ─────────────────────────────────────────────────────────────────────────────

class ScriptEditorApp(BaseWin):
    """macOS Script Editor — Python IDE with run capability."""

    SAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""MacPyOS Script Editor — Sample Script"""

import math
import datetime

def greet(name):
    return f"Hello, {name}! Today is {datetime.date.today()}"

def fibonacci(n):
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

# Run
print(greet("MacPyOS"))
print(f"Pi = {math.pi:.6f}")
print(f"First 10 Fibonacci: {fibonacci(10)}")

for i in range(1, 6):
    stars = "*" * i
    print(f"{stars:10s}  {i**2:3d}")
'''

    KEYWORDS = ["def","class","import","from","return","if","elif","else",
                "for","while","in","not","and","or","try","except","with",
                "as","pass","break","continue","lambda","yield","True","False","None"]

    def __init__(self, wm):
        super().__init__(wm,title="Script Editor",w=760,h=560,icon="script")
        self._path=None; self._build_ui()

    def _build_ui(self):
        c=self.client
        # Toolbar
        toolbar=tk.Frame(c,bg=T["panel_bg"],
                         highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        for text,cmd,tip in [
            ("New",self._new,"New script"),("Open",self._open,"Open file"),
            ("Save",self._save,"Save"),("Run",self._run,"Run script"),
            ("Stop",self._stop,"Stop"),("Clear",self._clear_output,"Clear output")]:
            b=tk.Label(toolbar,text=text,bg=T["panel_bg"],fg=T["text"],
                       font=(FONT_UI,12),padx=8,pady=5,cursor="hand2")
            if text=="Run": b.configure(fg=T["accent3"])
            if text=="Stop": b.configure(fg=T["danger"])
            b.pack(side="left"); b.bind("<Button-1>",lambda _,fn=cmd: fn()); make_tooltip(b,tip)
        self._path_lbl=tk.Label(toolbar,text="Untitled.py",bg=T["panel_bg"],
                                 fg=T["text_muted"],font=(FONT_UI,11))
        self._path_lbl.pack(side="right",padx=12)

        # Editor + output split
        split=tk.Frame(c,bg=T["win_bg"]); split.pack(fill="both",expand=True)

        # Line numbers + editor
        editor_pane=tk.Frame(split,bg=T["code_bg"])
        editor_pane.pack(side="left",fill="both",expand=True)

        editor_top=tk.Frame(editor_pane,bg=T["code_bg"])
        editor_top.pack(fill="both",expand=True)
        self._line_nums=tk.Text(editor_top,width=4,bg=T["panel_alt"],
                                 fg=T["text_muted"],font=(FONT_MONO,12),
                                 relief="flat",state="disabled",
                                 highlightthickness=0,padx=4)
        self._line_nums.pack(side="left",fill="y")
        self._editor=tk.Text(editor_top,bg=T["code_bg"],fg=T["code_fg"],
                              font=(FONT_MONO,12),relief="flat",
                              insertbackground=T["text"],
                              selectbackground=T["selection"],
                              wrap="none",highlightthickness=0,
                              padx=8,pady=4,tabs=("1c",))
        self._editor.pack(side="left",fill="both",expand=True)
        self._editor.insert("1.0",self.SAMPLE_SCRIPT)
        self._editor.bind("<KeyRelease>",self._on_key)
        self._editor.bind("<Tab>",self._on_tab)
        self._setup_syntax_tags()
        self._highlight_syntax()
        self._update_line_numbers()

        # Divider
        tk.Frame(split,bg=T["separator"],width=1).pack(side="left",fill="y")

        # Output pane
        out_pane=tk.Frame(split,bg=T["code_bg"],width=280)
        out_pane.pack(side="left",fill="y"); out_pane.pack_propagate(False)
        tk.Label(out_pane,text="Output",bg=T["panel_alt"],fg=T["text_muted"],
                 font=(FONT_UI,11,"bold"),padx=8,pady=4,anchor="w").pack(fill="x")
        self._output=tk.Text(out_pane,bg="#1a1a1a",fg="#e0e0e0",
                              font=(FONT_MONO,11),relief="flat",
                              state="disabled",wrap="word",
                              highlightthickness=0,padx=8,pady=4)
        self._output.pack(fill="both",expand=True)
        self._running=False

        # Status bar
        self._status=tk.Label(c,text="Ready",bg=T["status_bg"],
                               fg=T["text_muted"],font=(FONT_UI,11),
                               anchor="w",padx=8,
                               highlightthickness=1,highlightbackground=T["separator"])
        self._status.pack(fill="x")

    def _setup_syntax_tags(self):
        self._editor.tag_configure("keyword",foreground="#ff79c6")
        self._editor.tag_configure("string",foreground="#f1fa8c")
        self._editor.tag_configure("comment",foreground="#6272a4")
        self._editor.tag_configure("number",foreground="#bd93f9")
        self._editor.tag_configure("builtin",foreground="#8be9fd")

    def _highlight_syntax(self):
        self._editor.tag_remove("keyword","1.0","end")
        self._editor.tag_remove("string","1.0","end")
        self._editor.tag_remove("comment","1.0","end")
        self._editor.tag_remove("number","1.0","end")
        content=self._editor.get("1.0","end")
        # Keywords
        for kw in self.KEYWORDS:
            start="1.0"
            while True:
                pos=self._editor.search(r'\b'+kw+r'\b',start,"end",regexp=True)
                if not pos: break
                end=f"{pos}+{len(kw)}c"
                self._editor.tag_add("keyword",pos,end)
                start=end
        # Strings (simple)
        for pattern in [r'"[^"]*"',r"'[^']*'"]:
            start="1.0"
            while True:
                pos=self._editor.search(pattern,start,"end",regexp=True)
                if not pos: break
                line=content.split("\n")[int(pos.split(".")[0])-1]
                m=re.search(pattern,line)
                if m:
                    end=f"{pos}+{m.end()-m.start()}c"
                    self._editor.tag_add("string",pos,end)
                    start=end
                else: break
        # Comments
        for i,line in enumerate(content.split("\n")):
            idx=line.find("#")
            if idx>=0:
                row=i+1
                self._editor.tag_add("comment",f"{row}.{idx}",f"{row}.end")
        # Numbers
        start="1.0"
        while True:
            pos=self._editor.search(r'\b\d+\.?\d*\b',start,"end",regexp=True)
            if not pos: break
            end=self._editor.index(f"{pos}+10c")
            m=re.match(r'\d+\.?\d*',self._editor.get(pos,end))
            if m:
                self._editor.tag_add("number",pos,f"{pos}+{m.end()}c")
                start=f"{pos}+{m.end()}c"
            else: break

    def _on_key(self,event=None):
        self._highlight_syntax()
        self._update_line_numbers()
        content=self._editor.get("1.0","end-1c")
        lines=len(content.split("\n"))
        chars=len(content)
        self._status.configure(text=f"Lines: {lines}  |  Chars: {chars}")

    def _on_tab(self,event):
        self._editor.insert("insert","    ")
        return "break"

    def _update_line_numbers(self):
        content=self._editor.get("1.0","end-1c")
        lines=content.split("\n")
        self._line_nums.configure(state="normal")
        self._line_nums.delete("1.0","end")
        for i in range(1,len(lines)+1):
            self._line_nums.insert("end",f"{i}\n")
        self._line_nums.configure(state="disabled")

    def _run(self):
        code=self._editor.get("1.0","end-1c")
        self._output.configure(state="normal"); self._output.delete("1.0","end")
        self._status.configure(text="Running...")
        def execute():
            import io, sys
            old_stdout=sys.stdout; old_stderr=sys.stderr
            sys.stdout=io.StringIO(); sys.stderr=io.StringIO()
            try:
                exec(code,{"__name__":"__main__"})
                out=sys.stdout.getvalue()
                err=sys.stderr.getvalue()
            except Exception as ex:
                out=""; err=traceback.format_exc()
            finally:
                sys.stdout=old_stdout; sys.stderr=old_stderr
            def update():
                self._output.configure(state="normal")
                self._output.delete("1.0","end")
                if out: self._output.insert("end",out,"")
                if err: self._output.insert("end",err,"error")
                self._output.tag_configure("error",foreground=T["danger"])
                self._output.configure(state="disabled")
                self._status.configure(text="Done" if not err else "Error")
            self.wm.root.after(0,update)
        threading.Thread(target=execute,daemon=True).start()

    def _stop(self):
        self._status.configure(text="Stopped")

    def _clear_output(self):
        self._output.configure(state="normal")
        self._output.delete("1.0","end")
        self._output.configure(state="disabled")

    def _new(self):
        self._editor.delete("1.0","end")
        self._editor.insert("1.0",'#!/usr/bin/env python3\n\n# New Script\n\nprint("Hello, MacPyOS!")\n')
        self._path=None; self._path_lbl.configure(text="Untitled.py")

    def _open(self):
        path=simpledialog.askstring("Open","Path:",parent=self.wm.root)
        if path and self.wm.vfs.isfile(path):
            content=self.wm.vfs.read(path)
            self._editor.delete("1.0","end"); self._editor.insert("1.0",content)
            self._path=path; self._path_lbl.configure(text=path.split("/")[-1])
            self._highlight_syntax(); self._update_line_numbers()

    def _save(self):
        if not self._path:
            self._path=simpledialog.askstring("Save As","Path:",parent=self.wm.root)
        if self._path:
            content=self._editor.get("1.0","end-1c")
            self.wm.vfs.write(self._path,content)
            self._path_lbl.configure(text=self._path.split("/")[-1])
            self.wm.notifs.send("Script Editor",f"Saved: {self._path}",icon="script")


# =============================================================================
#  MacPyOS — PART 6
#  Contacts, App Store, System Preferences
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 34 — CONTACTS APP
# ─────────────────────────────────────────────────────────────────────────────

class ContactsApp(BaseWin):
    """macOS Contacts — address book with vCard-style entries."""

    SAMPLE_CONTACTS = [
        {"first":"Tim",    "last":"Cook",     "company":"Apple Inc.",    "email":"tim@apple.com",     "phone":"(408) 555-0100","address":"One Apple Park Way, Cupertino, CA"},
        {"first":"Jony",   "last":"Ive",      "company":"LoveFrom",      "email":"jony@lovefrom.com", "phone":"(415) 555-0101","address":"San Francisco, CA"},
        {"first":"Craig",  "last":"Federighi","company":"Apple Inc.",    "email":"craig@apple.com",   "phone":"(408) 555-0102","address":"Cupertino, CA"},
        {"first":"Alice",  "last":"Johnson",  "company":"Tech Corp",     "email":"alice@tech.com",    "phone":"(212) 555-0201","address":"New York, NY"},
        {"first":"Bob",    "last":"Smith",    "company":"Design Studio", "email":"bob@design.io",     "phone":"(310) 555-0202","address":"Los Angeles, CA"},
        {"first":"Carol",  "last":"White",    "company":"StartupXYZ",   "email":"carol@startup.io",  "phone":"(628) 555-0203","address":"San Francisco, CA"},
        {"first":"David",  "last":"Brown",    "company":"Freelance",     "email":"david@email.com",   "phone":"(512) 555-0204","address":"Austin, TX"},
        {"first":"Eve",    "last":"Davis",    "company":"CloudSoft",     "email":"eve@cloudsoft.com", "phone":"(206) 555-0205","address":"Seattle, WA"},
        {"first":"Frank",  "last":"Miller",   "company":"Finance Ltd",   "email":"frank@finance.com", "phone":"(312) 555-0206","address":"Chicago, IL"},
        {"first":"Grace",  "last":"Lee",      "company":"UX Agency",     "email":"grace@ux.agency",   "phone":"(415) 555-0207","address":"San Francisco, CA"},
        {"first":"Henry",  "last":"Wilson",   "company":"OpenSource",    "email":"henry@oss.dev",     "phone":"(617) 555-0208","address":"Boston, MA"},
        {"first":"Iris",   "last":"Zhang",    "company":"AILab",         "email":"iris@ailab.ai",     "phone":"(650) 555-0209","address":"Palo Alto, CA"},
    ]

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "Contacts", w=720, h=520, icon="👥")
        self._contacts  = [dict(c) for c in self.SAMPLE_CONTACTS]
        self._filtered  = list(self._contacts)
        self._selected  : Optional[int] = None
        self._build_ui()

    def _build_ui(self) -> None:
        # Toolbar
        tb = tk.Frame(self.client, bg=T["panel_bg"], pady=6)
        tb.pack(fill="x")
        tk.Label(tb, text="Contacts", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 14, "bold"), padx=12).pack(side="left")
        tk.Label(tb, text="＋", bg=T["panel_bg"], fg=T["accent"],
                 font=(FONT_UI, 20), cursor="hand2",
                 padx=8).pack(side="right").bind("<Button-1>", lambda _: self._new_contact())

        # Search
        sv = tk.StringVar()
        sv.trace_add("write", lambda *_: self._search(sv.get()))
        search_row = tk.Frame(self.client, bg=T["panel_bg"], pady=4)
        search_row.pack(fill="x", padx=8, pady=(0,4))
        tk.Label(search_row, text="🔍", bg=T["panel_bg"],
                 font=(FONT_EMOJI, 12)).pack(side="left")
        tk.Entry(search_row, textvariable=sv,
                 bg=T["input_bg"], fg=T["text"],
                 font=(FONT_UI, 12), relief="flat",
                 highlightthickness=1,
                 highlightbackground=T["input_border"]).pack(
                 side="left", fill="x", expand=True, padx=4)

        # Paned
        pane = tk.PanedWindow(self.client, orient="horizontal",
                              bg=T["separator"], sashwidth=1)
        pane.pack(fill="both", expand=True)

        # List
        list_frame = tk.Frame(pane, bg=T["sidebar_bg"], width=240)
        list_frame.pack_propagate(False)
        pane.add(list_frame, width=240)

        self._listbox = tk.Listbox(
            list_frame,
            bg=T["sidebar_bg"], fg=T["text"],
            selectbackground=T["selection"],
            font=(FONT_UI, 13),
            relief="flat", bd=0,
            highlightthickness=0,
            activestyle="none",
        )
        sb = tk.Scrollbar(list_frame, orient="vertical",
                          command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._listbox.pack(fill="both", expand=True)
        self._listbox.bind("<<ListboxSelect>>", self._on_select)

        # Detail view
        self._detail = tk.Frame(pane, bg=T["win_bg"])
        pane.add(self._detail)

        self._refresh_list()
        if self._contacts:
            self._listbox.selection_set(0)
            self._open_contact(0)

    def _refresh_list(self) -> None:
        self._listbox.delete(0, "end")
        for c in self._filtered:
            name = f"{c['first']} {c['last']}"
            self._listbox.insert("end", f"  {name}")

    def _search(self, query: str) -> None:
        q = query.lower()
        self._filtered = [
            c for c in self._contacts
            if q in c["first"].lower() or
               q in c["last"].lower() or
               q in c.get("company","").lower() or
               q in c.get("email","").lower()
        ] if q else list(self._contacts)
        self._refresh_list()

    def _on_select(self, _: tk.Event) -> None:
        sel = self._listbox.curselection()
        if not sel:
            return
        self._open_contact(sel[0])

    def _open_contact(self, idx: int) -> None:
        if idx >= len(self._filtered):
            return
        self._selected = idx
        contact = self._filtered[idx]
        for w in self._detail.winfo_children():
            w.destroy()

        # Avatar circle
        avatar_frame = tk.Frame(self._detail, bg=T["win_bg"])
        avatar_frame.pack(pady=20)
        initials = contact["first"][0] + contact["last"][0]
        colors   = [T["chart1"], T["chart2"], T["chart3"], T["chart4"], T["chart5"]]
        color    = colors[(ord(contact["first"][0]) + ord(contact["last"][0])) % len(colors)]
        av_canvas = tk.Canvas(avatar_frame, width=80, height=80,
                               bg=T["win_bg"], highlightthickness=0)
        av_canvas.pack()
        av_canvas.create_oval(2, 2, 78, 78, fill=color, outline="")
        av_canvas.create_text(40, 40, text=initials,
                               fill="#ffffff", font=(FONT_UI, 28, "bold"))

        # Name
        tk.Label(self._detail,
                 text=f"{contact['first']} {contact['last']}",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 20, "bold")).pack()
        if contact.get("company"):
            tk.Label(self._detail, text=contact["company"],
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 13)).pack()

        # Action buttons
        btn_row = tk.Frame(self._detail, bg=T["win_bg"])
        btn_row.pack(pady=10)
        for icon, label, cmd in [
            ("📱","Call",    lambda c=contact: self._call(c)),
            ("✉️","Message", lambda c=contact: self._message(c)),
            ("📧","Mail",    lambda c=contact: self.wm.open_mail()),
            ("📹","FaceTime",lambda: self.wm.notifs.send("FaceTime","FaceTime not available",icon="📹")),
        ]:
            col = tk.Frame(btn_row, bg=T["win_bg"])
            col.pack(side="left", padx=10)
            tk.Label(col, text=icon, bg=T["accent"],
                     font=(FONT_EMOJI, 18),
                     width=3, cursor="hand2",
                     pady=6).pack()
            tk.Label(col, text=label, bg=T["win_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 10)).pack()
            col.bind("<Button-1>", lambda _, c=cmd: c())

        tk.Frame(self._detail, bg=T["separator"], height=1).pack(fill="x",
                                                                   padx=20, pady=8)

        # Fields
        fields = [
            ("📱 mobile",   contact.get("phone","")),
            ("📧 email",    contact.get("email","")),
            ("🏢 company",  contact.get("company","")),
            ("📍 address",  contact.get("address","")),
        ]
        for label, value in fields:
            if not value:
                continue
            row = tk.Frame(self._detail, bg=T["win_bg"])
            row.pack(fill="x", padx=24, pady=3)
            tk.Label(row, text=label, bg=T["win_bg"],
                     fg=T["text_muted"], font=(FONT_UI, 11),
                     width=12, anchor="e").pack(side="left")
            tk.Label(row, text=value, bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 13),
                     anchor="w").pack(side="left", padx=8)

        # Edit / Delete
        action_row = tk.Frame(self._detail, bg=T["win_bg"])
        action_row.pack(pady=16)
        tk.Button(action_row, text="Edit",
                  bg=T["button_secondary"], fg=T["text"],
                  font=(FONT_UI, 12), relief="flat",
                  padx=16, command=lambda: self._edit_contact(idx)).pack(side="left", padx=6)
        tk.Button(action_row, text="Delete",
                  bg=T["danger"], fg="#ffffff",
                  font=(FONT_UI, 12), relief="flat",
                  padx=16, command=lambda: self._delete_contact(idx)).pack(side="left", padx=6)

    def _call(self, contact: Dict) -> None:
        self.wm.notifs.send("Phone",
                             f"Calling {contact['first']} {contact['last']}…",
                             icon="📱")

    def _message(self, contact: Dict) -> None:
        self.wm.notifs.send("Messages",
                             f"Message to {contact['first']} {contact['last']}",
                             icon="💬")

    def _new_contact(self) -> None:
        EditContactDialog(self.wm, self._contacts, None, self._on_contact_saved)

    def _edit_contact(self, idx: int) -> None:
        EditContactDialog(self.wm, self._contacts, self._filtered[idx],
                          self._on_contact_saved)

    def _on_contact_saved(self) -> None:
        self._filtered = list(self._contacts)
        self._refresh_list()

    def _delete_contact(self, idx: int) -> None:
        contact = self._filtered[idx]
        if messagebox.askyesno("Delete Contact",
                                f"Delete {contact['first']} {contact['last']}?",
                                parent=self.wm.root):
            self._contacts.remove(contact)
            self._filtered = list(self._contacts)
            self._refresh_list()
            for w in self._detail.winfo_children():
                w.destroy()


class EditContactDialog:
    def __init__(self, wm: "WM", contacts: List[Dict],
                 contact: Optional[Dict], on_save: Callable) -> None:
        self.wm       = wm
        self.contacts = contacts
        self.contact  = contact
        self.on_save  = on_save
        dlg = tk.Toplevel(wm.root)
        dlg.title("Edit Contact" if contact else "New Contact")
        dlg.geometry("420x380")
        dlg.configure(bg=T["win_bg"])
        dlg.transient(wm.root)
        dlg.grab_set()

        tk.Label(dlg, text="Edit Contact" if contact else "New Contact",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 16, "bold"), pady=12).pack()

        fields: Dict[str, tk.Entry] = {}
        defaults = contact or {}
        for label, key in [("First Name","first"),("Last Name","last"),
                           ("Company","company"),("Email","email"),
                           ("Phone","phone"),("Address","address")]:
            row = tk.Frame(dlg, bg=T["win_bg"])
            row.pack(fill="x", padx=20, pady=3)
            tk.Label(row, text=label+":", bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 12),
                     width=12, anchor="e").pack(side="left")
            e = tk.Entry(row, bg=T["input_bg"], fg=T["text"],
                         font=(FONT_UI, 13), relief="flat",
                         highlightthickness=1,
                         highlightbackground=T["input_border"])
            e.pack(side="left", fill="x", expand=True, padx=8)
            e.insert(0, defaults.get(key, ""))
            fields[key] = e

        def save():
            data = {k: e.get().strip() for k, e in fields.items()}
            if not data["first"]:
                return
            if contact:
                contact.update(data)
            else:
                contacts.append(data)
            on_save()
            dlg.destroy()

        btn_row = tk.Frame(dlg, bg=T["win_bg"])
        btn_row.pack(pady=12)
        tk.Button(btn_row, text="Save",
                  bg=T["accent"], fg="#ffffff",
                  font=(FONT_UI, 13), relief="flat",
                  padx=16, command=save).pack(side="left", padx=6)
        tk.Button(btn_row, text="Cancel",
                  bg=T["button_secondary"], fg=T["text"],
                  font=(FONT_UI, 13), relief="flat",
                  padx=16, command=dlg.destroy).pack(side="left", padx=6)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 35 — APP STORE
# ─────────────────────────────────────────────────────────────────────────────

class AppStoreApp(BaseWin):
    """macOS App Store — featured, categories, updates."""

    FEATURED = [
        {"name":"Final Cut Pro",  "dev":"Apple","price":"Free","icon":"🎬","cat":"Video",   "rating":4.9,"desc":"Professional video editing software."},
        {"name":"Logic Pro",      "dev":"Apple","price":"Free","icon":"🎵","cat":"Music",   "rating":4.8,"desc":"Complete professional recording studio."},
        {"name":"Xcode",          "dev":"Apple","price":"Free","icon":"🔨","cat":"Dev",     "rating":4.5,"desc":"Build apps for Apple platforms."},
        {"name":"Pixelmator Pro", "dev":"Pixelmator","price":"Free","icon":"🎨","cat":"Graphics","rating":4.9,"desc":"Professional image editing."},
        {"name":"1Password",      "dev":"AgileBits","price":"Free","icon":"🔐","cat":"Utils","rating":4.7,"desc":"Password manager and secure wallet."},
        {"name":"Bear",           "dev":"Shiny Frog","price":"Free","icon":"🐻","cat":"Writing","rating":4.8,"desc":"Beautiful writing app for notes."},
        {"name":"Reeder",         "dev":"Silvio Rizzi","price":"Free","icon":"📰","cat":"News","rating":4.7,"desc":"Elegant RSS feed reader."},
        {"name":"Affinity Photo", "dev":"Serif","price":"Free","icon":"🖼️","cat":"Graphics","rating":4.8,"desc":"Professional photo editing."},
        {"name":"VS Code",        "dev":"Microsoft","price":"Free","icon":"💻","cat":"Dev","rating":4.9,"desc":"Lightweight code editor."},
        {"name":"Slack",          "dev":"Slack","price":"Free","icon":"💬","cat":"Business","rating":4.6,"desc":"Team messaging and collaboration."},
        {"name":"Figma",          "dev":"Figma Inc","price":"Free","icon":"✏️","cat":"Design","rating":4.9,"desc":"Collaborative design tool."},
        {"name":"Tot",            "dev":"Iconfactory","price":"Free","icon":"🟣","cat":"Utils","rating":4.7,"desc":"Collect and edit text snippets."},
    ]

    CATEGORIES = ["Featured","Top Charts","Categories","Updates"]

    def __init__(self, wm: "WM") -> None:
        super().__init__(wm, "App Store", w=860, h=580, icon="🏪")
        self._installed: List[str] = ["Finder","Notes","Safari","Mail","Music"]
        self._tab       = "Featured"
        self._build_ui()

    def _build_ui(self) -> None:
        # Nav bar
        nav = tk.Frame(self.client, bg=T["panel_bg"], pady=6)
        nav.pack(fill="x")
        tk.Label(nav, text="🏪 App Store", bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 15, "bold"), padx=12).pack(side="left")

        # Search
        sv = tk.StringVar()
        sv.trace_add("write", lambda *_: self._search(sv.get()))
        tk.Entry(nav, textvariable=sv, bg=T["input_bg"], fg=T["text"],
                 font=(FONT_UI, 12), relief="flat",
                 highlightthickness=1,
                 highlightbackground=T["input_border"],
                 width=22).pack(side="right", padx=10)
        tk.Label(nav, text="🔍", bg=T["panel_bg"],
                 font=(FONT_EMOJI, 12)).pack(side="right")

        # Tab bar
        tab_bar = tk.Frame(self.client, bg=T["sidebar_bg"])
        tab_bar.pack(fill="x")
        self._tab_btns: Dict[str, tk.Label] = {}
        for tab in self.CATEGORIES:
            btn = tk.Label(tab_bar, text=tab,
                           bg=T["sidebar_bg"], fg=T["text_muted"],
                           font=(FONT_UI, 12), padx=16, pady=8, cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>", lambda _, t=tab: self._switch_tab(t))
            self._tab_btns[tab] = btn

        self._content = MacScrolledFrame(self.client, bg=T["win_bg"])
        self._content.pack(fill="both", expand=True)
        self._switch_tab("Featured")

    def _switch_tab(self, tab: str) -> None:
        self._tab = tab
        for t, btn in self._tab_btns.items():
            btn.configure(
                fg=T["accent"] if t == tab else T["text_muted"],
                font=(FONT_UI, 12, "bold") if t == tab else (FONT_UI, 12),
            )
        inner = self._content.inner
        for w in inner.winfo_children():
            w.destroy()

        if tab == "Featured":
            self._render_featured(inner, self.FEATURED)
        elif tab == "Top Charts":
            self._render_charts(inner)
        elif tab == "Categories":
            self._render_categories(inner)
        elif tab == "Updates":
            self._render_updates(inner)

    def _render_featured(self, parent: tk.Widget, apps: List[Dict]) -> None:
        # Banner
        banner = tk.Frame(parent, bg=T["accent"], height=160)
        banner.pack(fill="x", padx=16, pady=12)
        banner.pack_propagate(False)
        tk.Label(banner, text="🏆  Editor's Choice",
                 bg=T["accent"], fg="#ffffff",
                 font=(FONT_UI, 11), padx=20, pady=8).pack(anchor="w")
        feat = apps[0]
        tk.Label(banner, text=f"{feat['icon']}  {feat['name']}",
                 bg=T["accent"], fg="#ffffff",
                 font=(FONT_UI, 22, "bold"), padx=20).pack(anchor="w")
        tk.Label(banner, text=feat["desc"],
                 bg=T["accent"], fg="#ffffff",
                 font=(FONT_UI, 12), padx=20).pack(anchor="w")

        # Grid
        tk.Label(parent, text="All Apps",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 16, "bold"), padx=16, pady=8).pack(anchor="w")
        cols = 3
        for i, app in enumerate(apps):
            if i % cols == 0:
                row_frame = tk.Frame(parent, bg=T["win_bg"])
                row_frame.pack(fill="x", padx=12, pady=4)
            self._app_card(row_frame, app)

    def _app_card(self, parent: tk.Widget, app: Dict) -> None:
        card = tk.Frame(parent, bg=T["panel_bg"],
                        highlightthickness=1,
                        highlightbackground=T["separator"])
        card.pack(side="left", fill="x", expand=True, padx=6, pady=4)

        top = tk.Frame(card, bg=T["panel_bg"])
        top.pack(fill="x", padx=10, pady=(10,4))
        tk.Label(top, text=app["icon"],
                 bg=T["panel_bg"], font=(FONT_EMOJI, 28)).pack(side="left")
        info = tk.Frame(top, bg=T["panel_bg"])
        info.pack(side="left", padx=8, fill="x", expand=True)
        tk.Label(info, text=app["name"],
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 13, "bold"), anchor="w").pack(anchor="w")
        tk.Label(info, text=app["dev"],
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 10), anchor="w").pack(anchor="w")
        stars = "★" * int(app["rating"]) + "☆" * (5 - int(app["rating"]))
        tk.Label(info, text=stars,
                 bg=T["panel_bg"], fg=T["warning"],
                 font=(FONT_UI, 10)).pack(anchor="w")

        tk.Label(card, text=app["desc"][:60] + ("…" if len(app["desc"])>60 else ""),
                 bg=T["panel_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 11), wraplength=220,
                 justify="left", padx=10).pack(anchor="w")

        is_installed = app["name"] in self._installed
        btn_text  = "✓ Installed" if is_installed else app["price"]
        btn_bg    = T["success"] if is_installed else T["accent"]
        btn_fg    = "#ffffff"
        btn = tk.Button(card, text=btn_text,
                        bg=btn_bg, fg=btn_fg,
                        font=(FONT_UI, 11), relief="flat",
                        padx=12, pady=4, cursor="hand2",
                        command=lambda a=app: self._install(a))
        btn.pack(pady=(4, 10))

    def _install(self, app: Dict) -> None:
        if app["name"] in self._installed:
            self.wm.notifs.send("App Store",
                                 f"{app['name']} is already installed.", icon="✅")
        else:
            self._installed.append(app["name"])
            self.wm.notifs.send("App Store",
                                 f"{app['name']} installed.", icon="🏪")
            self._switch_tab(self._tab)

    def _render_charts(self, parent: tk.Widget) -> None:
        for section, apps in [("Free Apps", self.FEATURED[:6]),
                               ("Top Paid", self.FEATURED[6:])]:
            tk.Label(parent, text=section,
                     bg=T["win_bg"], fg=T["text"],
                     font=(FONT_UI, 16, "bold"), padx=16, pady=8).pack(anchor="w")
            for i, app in enumerate(apps):
                row = tk.Frame(parent, bg=T["win_bg"], cursor="hand2")
                row.pack(fill="x", padx=16, pady=3)
                tk.Label(row, text=str(i+1),
                         bg=T["win_bg"], fg=T["text_muted"],
                         font=(FONT_UI, 14), width=3).pack(side="left")
                tk.Label(row, text=app["icon"],
                         bg=T["win_bg"],
                         font=(FONT_EMOJI, 24)).pack(side="left", padx=8)
                info = tk.Frame(row, bg=T["win_bg"])
                info.pack(side="left", fill="x", expand=True)
                tk.Label(info, text=app["name"],
                         bg=T["win_bg"], fg=T["text"],
                         font=(FONT_UI, 13, "bold"), anchor="w").pack(anchor="w")
                tk.Label(info, text=app["cat"],
                         bg=T["win_bg"], fg=T["text_muted"],
                         font=(FONT_UI, 10), anchor="w").pack(anchor="w")
                tk.Button(row, text=app["price"],
                          bg=T["accent"], fg="#ffffff",
                          font=(FONT_UI, 11), relief="flat",
                          padx=10, command=lambda a=app: self._install(a)).pack(side="right")
                tk.Frame(parent, bg=T["separator"], height=1).pack(fill="x", padx=16)

    def _render_categories(self, parent: tk.Widget) -> None:
        cats = [("🎨","Graphics & Design"),("💻","Developer Tools"),
                ("🎵","Music"),("📹","Video"),("📝","Productivity"),
                ("🎮","Games"),("📰","News"),("💼","Business"),
                ("🔒","Utilities"),("📚","Education")]
        cols = 2
        for i, (icon, name) in enumerate(cats):
            if i % cols == 0:
                row_frame = tk.Frame(parent, bg=T["win_bg"])
                row_frame.pack(fill="x", padx=12, pady=4)
            card = tk.Frame(row_frame, bg=T["panel_bg"],
                            highlightthickness=1,
                            highlightbackground=T["separator"],
                            cursor="hand2")
            card.pack(side="left", fill="x", expand=True, padx=6)
            tk.Label(card, text=f"{icon}  {name}",
                     bg=T["panel_bg"], fg=T["text"],
                     font=(FONT_UI, 14), padx=16, pady=14,
                     anchor="w").pack(anchor="w")

    def _render_updates(self, parent: tk.Widget) -> None:
        tk.Label(parent, text="All apps are up to date.",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 16), pady=40).pack()
        tk.Label(parent, text="✅  Last checked: Just now",
                 bg=T["win_bg"], fg=T["success"],
                 font=(FONT_UI, 13)).pack()

    def _search(self, query: str) -> None:
        if not query:
            self._switch_tab("Featured")
            return
        hits = [a for a in self.FEATURED
                if query.lower() in a["name"].lower() or
                   query.lower() in a["cat"].lower()]
        inner = self._content.inner
        for w in inner.winfo_children():
            w.destroy()
        if not hits:
            tk.Label(inner, text=f'No results for "{query}"',
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 14), pady=40).pack()
        else:
            tk.Label(inner, text=f'Results for "{query}"',
                     bg=T["win_bg"], fg=T["text"],
                     font=(FONT_UI, 16, "bold"), padx=16, pady=8).pack(anchor="w")
            cols = 3
            for i, app in enumerate(hits):
                if i % cols == 0:
                    row_frame = tk.Frame(inner, bg=T["win_bg"])
                    row_frame.pack(fill="x", padx=12, pady=4)
                self._app_card(row_frame, app)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 36 — SYSTEM PREFERENCES
# ─────────────────────────────────────────────────────────────────────────────

class SystemPreferencesApp(BaseWin):
    """macOS System Preferences — 10 preference panels."""

    PANELS = [
        ("👤","Apple ID",          "apple_id"),
        ("🖥️","Displays",          "displays"),
        ("🔊","Sound",             "sound"),
        ("🌐","Network",           "network"),
        ("🔵","Bluetooth",         "bluetooth"),
        ("🖼️","Desktop & Screen Saver","wallpaper"),
        ("💡","Appearance",        "appearance"),
        ("⌨️","Keyboard",          "keyboard"),
        ("🖱️","Trackpad",          "trackpad"),
        ("🔒","Security & Privacy","security"),
        ("⚡","Battery",           "battery"),
        ("🕐","Date & Time",       "datetime"),
        ("🌍","Language & Region", "language"),
        ("🔔","Notifications",     "notifications"),
        ("👥","Users & Groups",    "users"),
        ("♿","Accessibility",     "accessibility"),
    ]

    def __init__(self, wm: "WM", panel: Optional[str] = None) -> None:
        super().__init__(wm, "System Preferences", w=760, h=560, icon="⚙️")
        self._panel   = panel
        self._build_ui()
        if panel:
            # Find matching panel
            for _, name, key in self.PANELS:
                if panel.lower() in name.lower():
                    self._show_panel(key, name)
                    return

    def _build_ui(self) -> None:
        # Search bar
        search_bar = tk.Frame(self.client, bg=T["panel_bg"], pady=8)
        search_bar.pack(fill="x")
        tk.Label(search_bar, text="⚙️ System Preferences",
                 bg=T["panel_bg"], fg=T["text"],
                 font=(FONT_UI, 15, "bold"), padx=12).pack(side="left")
        sv = tk.StringVar()
        sv.trace_add("write", lambda *_: self._search(sv.get()))
        tk.Entry(search_bar, textvariable=sv,
                 bg=T["input_bg"], fg=T["text"],
                 font=(FONT_UI, 12), relief="flat",
                 highlightthickness=1,
                 highlightbackground=T["input_border"],
                 width=18).pack(side="right", padx=10)
        tk.Label(search_bar, text="🔍",
                 bg=T["panel_bg"], font=(FONT_EMOJI, 12)).pack(side="right")

        self._content = tk.Frame(self.client, bg=T["win_bg"])
        self._content.pack(fill="both", expand=True)
        self._show_grid(self.PANELS)

    def _show_grid(self, panels: List[Tuple]) -> None:
        for w in self._content.winfo_children():
            w.destroy()
        # Back button if in a panel
        sf = MacScrolledFrame(self._content, bg=T["win_bg"])
        sf.pack(fill="both", expand=True)
        inner = sf.inner
        cols = 4
        for i, (icon, name, key) in enumerate(panels):
            if i % cols == 0:
                row_frame = tk.Frame(inner, bg=T["win_bg"])
                row_frame.pack(fill="x", pady=8)
            cell = tk.Frame(row_frame, bg=T["win_bg"], cursor="hand2", width=160)
            cell.pack(side="left", expand=True)
            tk.Label(cell, text=icon, bg=T["win_bg"],
                     font=(FONT_EMOJI, 32)).pack(pady=(8,2))
            tk.Label(cell, text=name, bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 11),
                     wraplength=120, justify="center").pack()
            cell.bind("<Button-1>",
                      lambda _, k=key, n=name: self._show_panel(k, n))
            for child in cell.winfo_children():
                child.bind("<Button-1>",
                           lambda _, k=key, n=name: self._show_panel(k, n))

    def _show_panel(self, key: str, name: str) -> None:
        for w in self._content.winfo_children():
            w.destroy()
        # Back button
        back = tk.Frame(self._content, bg=T["panel_bg"], pady=6)
        back.pack(fill="x")
        tk.Label(back, text="◀  All Preferences",
                 bg=T["panel_bg"], fg=T["accent"],
                 font=(FONT_UI, 12), padx=12, cursor="hand2").pack(
                 side="left").bind("<Button-1>", lambda _: self._show_grid(self.PANELS))
        tk.Label(back, text=name, bg=T["panel_bg"],
                 fg=T["text"], font=(FONT_UI, 14, "bold")).pack(side="left", padx=12)

        panel_frame = tk.Frame(self._content, bg=T["win_bg"])
        panel_frame.pack(fill="both", expand=True, padx=20, pady=16)

        # Dispatch to panel builder
        builder = getattr(self, f"_panel_{key}", self._panel_generic)
        builder(panel_frame, name)

    def _panel_generic(self, parent: tk.Widget, name: str) -> None:
        tk.Label(parent, text=name,
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 20, "bold"), pady=12).pack()
        tk.Label(parent, text="Settings for this panel are managed here.",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 13)).pack()

    def _panel_appearance(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Appearance",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")

        # Appearance mode
        self._row(parent, "Appearance Mode")
        mode_frame = tk.Frame(parent, bg=T["win_bg"])
        mode_frame.pack(anchor="w", padx=20, pady=4)
        cur_theme = self.wm.settings.get("theme", "Monterey")
        theme_var = tk.StringVar(value=cur_theme)
        for theme in THEMES:
            rb = tk.Radiobutton(mode_frame, text=theme,
                                variable=theme_var, value=theme,
                                bg=T["win_bg"], fg=T["text"],
                                selectcolor=T["win_bg"],
                                font=(FONT_UI, 13),
                                command=lambda t=theme: self._change_theme(t))
            rb.pack(anchor="w", padx=20, pady=2)

        self._row(parent, "Accent Color")
        accent_frame = tk.Frame(parent, bg=T["win_bg"])
        accent_frame.pack(anchor="w", padx=20, pady=4)
        for color, label in [("#007aff","Blue"),("#5856d6","Purple"),
                              ("#ff2d55","Pink"),("#ff9500","Orange"),
                              ("#34c759","Green"),("#ff3b30","Red")]:
            dot = tk.Label(accent_frame, bg=color,
                           width=2, height=1, cursor="hand2",
                           relief="solid", bd=2)
            dot.pack(side="left", padx=4)
            make_tooltip(dot, label)
            dot.bind("<Button-1>", lambda _, c=color: self._change_accent(c))

    def _change_theme(self, theme: str) -> None:
        self.wm.settings.set("theme", theme)
        apply_theme(theme)
        self.wm.notifs.send("System Preferences",
                             f"Theme changed to {theme}.", icon="⚙️")

    def _change_accent(self, color: str) -> None:
        self.wm.settings.set("accent_color", color)
        T["accent"] = color
        self.wm.notifs.send("System Preferences",
                             "Accent color updated.", icon="🎨")

    def _panel_wallpaper(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Desktop & Screen Saver",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        tk.Label(parent, text="Choose a wallpaper:",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 12), pady=4).pack(anchor="w")

        cur = self.wm.settings.get("wallpaper", "gradient_blue")
        wp_var = tk.StringVar(value=cur)
        wallpapers = [
            ("gradient_blue",   "🌊 Blue Gradient (Default)"),
            ("gradient_sunset", "🌅 Sunset Gradient"),
            ("solid_dark",      "🌑 Solid Dark"),
            ("solid_sand",      "🏜️ Solid Sand"),
        ]
        for key, label in wallpapers:
            row = tk.Frame(parent, bg=T["win_bg"])
            row.pack(anchor="w", padx=20, pady=3)
            rb = tk.Radiobutton(row, text=label,
                                variable=wp_var, value=key,
                                bg=T["win_bg"], fg=T["text"],
                                selectcolor=T["win_bg"],
                                font=(FONT_UI, 13),
                                command=lambda k=key: self._change_wp(k))
            rb.pack(side="left")

        tk.Label(parent, text="Screen Saver",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 16, "bold"), pady=12).pack(anchor="w")
        for ss in ["Flurry","Arabesque","Shell","Hello"]:
            tk.Radiobutton(parent, text=ss,
                           bg=T["win_bg"], fg=T["text"],
                           selectcolor=T["win_bg"],
                           font=(FONT_UI, 13)).pack(anchor="w", padx=20, pady=2)

    def _change_wp(self, key: str) -> None:
        self.wm.settings.set("wallpaper", key)
        self.wm.menubar.frame.after(0, self.wm._draw_wallpaper)
        self.wm.notifs.send("System Preferences", "Wallpaper updated.", icon="🖼️")

    def _panel_sound(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Sound",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        self._row(parent, "Output Volume")
        vol_frame = tk.Frame(parent, bg=T["win_bg"])
        vol_frame.pack(fill="x", padx=20, pady=4)
        tk.Label(vol_frame, text="🔈", bg=T["win_bg"],
                 font=(FONT_EMOJI, 14)).pack(side="left")
        vol_slider = tk.Scale(vol_frame, from_=0, to=100,
                               orient="horizontal", length=300,
                               bg=T["win_bg"], fg=T["text"],
                               troughcolor=T["progress_bg"],
                               highlightthickness=0, bd=0)
        vol_slider.set(80)
        vol_slider.pack(side="left", padx=8)
        tk.Label(vol_frame, text="🔊", bg=T["win_bg"],
                 font=(FONT_EMOJI, 14)).pack(side="left")

        self._row(parent, "Alert Sounds")
        for sound in ["Basso","Blow","Bottle","Frog","Funk","Glass","Hero","Morse","Ping","Pop","Purr","Sosumi","Submarine","Tink"]:
            tk.Radiobutton(parent, text=sound,
                           bg=T["win_bg"], fg=T["text"],
                           selectcolor=T["win_bg"],
                           font=(FONT_UI, 12)).pack(anchor="w", padx=20)

        self._bool_pref(parent, "Play user interface sound effects",
                        "sound_enabled")
        self._bool_pref(parent, "Play feedback when volume is changed",
                        "sound_feedback")

    def _panel_notifications(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Notifications",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        self._bool_pref(parent, "Allow Notifications", "notifications")
        self._bool_pref(parent, "Do Not Disturb",      "do_not_disturb")
        tk.Label(parent, text="Notification Style",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold"), pady=8).pack(anchor="w")
        for style in ["None","Banners","Alerts"]:
            tk.Radiobutton(parent, text=style,
                           bg=T["win_bg"], fg=T["text"],
                           selectcolor=T["win_bg"],
                           font=(FONT_UI, 13)).pack(anchor="w", padx=20, pady=2)

    def _panel_displays(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Displays",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        tk.Label(parent, text=f"Built-in Display  —  {SCREEN_W}×{SCREEN_H}",
                 bg=T["win_bg"], fg=T["text"], font=(FONT_UI, 14)).pack(anchor="w", padx=20)
        self._row(parent, "Brightness")
        fr = tk.Frame(parent, bg=T["win_bg"])
        fr.pack(fill="x", padx=20, pady=4)
        tk.Label(fr, text="☀️", bg=T["win_bg"], font=(FONT_EMOJI,12)).pack(side="left")
        s = tk.Scale(fr, from_=0, to=100, orient="horizontal",
                      length=300, bg=T["win_bg"], fg=T["text"],
                      troughcolor=T["progress_bg"], highlightthickness=0, bd=0)
        s.set(75)
        s.pack(side="left", padx=8)
        tk.Label(fr, text="☀️☀️", bg=T["win_bg"], font=(FONT_EMOJI,14)).pack(side="left")
        self._bool_pref(parent, "True Tone", "true_tone")
        self._bool_pref(parent, "Night Shift", "night_shift")
        self._bool_pref(parent, "Automatically adjust brightness","auto_brightness")

    def _panel_battery(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Battery",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        # Battery indicator
        canvas = tk.Canvas(parent, width=200, height=100,
                            bg=T["win_bg"], highlightthickness=0)
        canvas.pack(pady=8)
        canvas.create_rectangle(20, 30, 160, 70, outline=T["text"], width=2)
        canvas.create_rectangle(160, 42, 168, 58, fill=T["text"], outline="")
        canvas.create_rectangle(22, 32, 130, 68, fill=T["accent3"], outline="")
        canvas.create_text(100, 90, text="98% — Charging",
                            fill=T["text"], font=(FONT_UI, 12))
        self._bool_pref(parent, "Show battery status in menu bar", "battery_menubar")
        self._bool_pref(parent, "Low Power Mode", "low_power")
        self._row(parent, "Turn display off after")
        sl = tk.Scale(parent, from_=1, to=60, orient="horizontal",
                       length=300, bg=T["win_bg"], fg=T["text"],
                       troughcolor=T["progress_bg"], highlightthickness=0, bd=0)
        sl.set(5)
        sl.pack(padx=20)

    def _panel_security(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Security & Privacy",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        tk.Label(parent, text="🔒  FileVault is ON",
                 bg=T["win_bg"], fg=T["success"],
                 font=(FONT_UI, 13), padx=20).pack(anchor="w")
        tk.Label(parent, text="🛡️  Firewall is ON",
                 bg=T["win_bg"], fg=T["success"],
                 font=(FONT_UI, 13), padx=20).pack(anchor="w")
        self._bool_pref(parent, "Require password after sleep",   "require_password")
        self._bool_pref(parent, "Allow apps from App Store only", "gatekeeper")
        self._bool_pref(parent, "Enable Touch ID",                "touch_id")
        tk.Label(parent, text="Privacy",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold"), pady=8).pack(anchor="w")
        for item in ["Location Services","Contacts","Calendar",
                     "Microphone","Camera","Full Disk Access"]:
            row = tk.Frame(parent, bg=T["win_bg"])
            row.pack(fill="x", padx=20, pady=2)
            tk.Label(row, text=item, bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 12)).pack(side="left")
            var = tk.BooleanVar(value=True)
            tk.Checkbutton(row, variable=var,
                           bg=T["win_bg"], activebackground=T["win_bg"],
                           selectcolor=T["win_bg"]).pack(side="right")

    def _panel_datetime(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Date & Time",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        now = datetime.datetime.now()
        tk.Label(parent, text=now.strftime("%A, %B %d, %Y"),
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 22, "bold"), pady=8).pack()
        tk.Label(parent, text=now.strftime("%I:%M:%S %p"),
                 bg=T["win_bg"], fg=T["accent"],
                 font=(FONT_MONO, 36, "bold")).pack()
        self._bool_pref(parent, "Set date and time automatically", "auto_time")
        self._bool_pref(parent, "Show 24-hour time", "time_24h")
        self._bool_pref(parent, "Show date in menu bar", "show_date")
        self._row(parent, "Time Zone")
        tz_var = tk.StringVar(value=self.wm.settings.get("timezone","America/New_York"))
        tz_combo = ttk.Combobox(parent, textvariable=tz_var,
                                 values=["America/New_York","America/Los_Angeles",
                                         "Europe/London","Europe/Paris","Asia/Tokyo",
                                         "Australia/Sydney"],
                                 font=(FONT_UI, 12), state="readonly", width=28)
        tz_combo.pack(padx=20, pady=4, anchor="w")
        tz_combo.bind("<<ComboboxSelected>>",
                       lambda _: self.wm.settings.set("timezone", tz_var.get()))

    def _panel_keyboard(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Keyboard",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        self._row(parent, "Key Repeat Rate")
        s1 = tk.Scale(parent, from_=1, to=10, orient="horizontal",
                       length=300, bg=T["win_bg"], fg=T["text"],
                       troughcolor=T["progress_bg"], highlightthickness=0, bd=0)
        s1.set(7)
        s1.pack(padx=20, anchor="w")
        self._row(parent, "Delay Until Repeat")
        s2 = tk.Scale(parent, from_=1, to=10, orient="horizontal",
                       length=300, bg=T["win_bg"], fg=T["text"],
                       troughcolor=T["progress_bg"], highlightthickness=0, bd=0)
        s2.set(5)
        s2.pack(padx=20, anchor="w")
        self._bool_pref(parent, "Use F1, F2 keys as standard function keys","fn_keys")
        self._bool_pref(parent, "Enable Dictation", "dictation")
        tk.Label(parent, text="Keyboard Shortcuts",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 14, "bold"), pady=8).pack(anchor="w")
        for shortcut, action in [("⌘Space","Spotlight"),("⌘Tab","Switch Apps"),
                                  ("⌘W","Close Window"),("⌘Q","Quit App"),
                                  ("⌃⌘F","Full Screen")]:
            row = tk.Frame(parent, bg=T["win_bg"])
            row.pack(fill="x", padx=20, pady=2)
            tk.Label(row, text=shortcut, bg=T["win_bg"],
                     fg=T["accent"], font=(FONT_MONO, 12), width=10).pack(side="left")
            tk.Label(row, text=action, bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 12)).pack(side="left")

    def _panel_trackpad(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Trackpad",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        self._bool_pref(parent, "Tap to Click",          "tap_to_click")
        self._bool_pref(parent, "Natural Scrolling",     "natural_scrolling")
        self._bool_pref(parent, "Force Click",           "force_click")
        self._bool_pref(parent, "Pinch to Zoom",         "pinch_zoom")
        self._bool_pref(parent, "Smart Zoom",            "smart_zoom")
        self._row(parent, "Tracking Speed")
        s = tk.Scale(parent, from_=1, to=10, orient="horizontal",
                      length=300, bg=T["win_bg"], fg=T["text"],
                      troughcolor=T["progress_bg"], highlightthickness=0, bd=0)
        s.set(6)
        s.pack(padx=20, anchor="w")

    def _panel_network(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Network",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        for iface, status, ip in [
            ("Wi-Fi",   "Connected",    "192.168.1.42"),
            ("Ethernet","Not Connected","—"),
            ("Bluetooth PAN","Off",     "—"),
        ]:
            row = tk.Frame(parent, bg=T["panel_bg"],
                           highlightthickness=1,
                           highlightbackground=T["separator"])
            row.pack(fill="x", padx=20, pady=4)
            color = T["success"] if status == "Connected" else T["text_muted"]
            tk.Label(row, text=f"●  {iface}",
                     bg=T["panel_bg"], fg=color,
                     font=(FONT_UI, 14, "bold"), padx=12, pady=8).pack(side="left")
            tk.Label(row, text=f"{status}\n{ip}",
                     bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 11)).pack(side="right", padx=12)

    def _panel_bluetooth(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Bluetooth",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        var = tk.BooleanVar(value=True)
        tk.Checkbutton(parent, text="Bluetooth: ON",
                       variable=var, bg=T["win_bg"],
                       fg=T["text"], font=(FONT_UI, 14),
                       selectcolor=T["win_bg"],
                       activebackground=T["win_bg"]).pack(anchor="w", padx=20, pady=8)
        tk.Label(parent, text="My Devices",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 11, "bold"), padx=20).pack(anchor="w")
        for device, status in [("AirPods Pro","Connected  🔊"),
                                ("Magic Mouse 2","Connected  🖱️"),
                                ("Magic Keyboard","Connected  ⌨️"),
                                ("iPhone 15","Not Connected")]:
            row = tk.Frame(parent, bg=T["win_bg"])
            row.pack(fill="x", padx=20, pady=3)
            tk.Label(row, text=device, bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 13)).pack(side="left")
            tk.Label(row, text=status, bg=T["win_bg"],
                     fg=T["text_muted"] if "Not" in status else T["success"],
                     font=(FONT_UI, 11)).pack(side="right")
            tk.Frame(parent, bg=T["separator"], height=1).pack(fill="x", padx=20)

    def _panel_apple_id(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Apple ID",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        # Avatar
        av = tk.Canvas(parent, width=80, height=80,
                        bg=T["win_bg"], highlightthickness=0)
        av.pack(pady=8)
        av.create_oval(2, 2, 78, 78, fill=T["accent"], outline="")
        av.create_text(40, 40, text="👤",
                        font=(FONT_EMOJI, 28))
        tk.Label(parent,
                 text=self.wm.users.display_name(),
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 16, "bold")).pack()
        tk.Label(parent, text="user@macpyos.local",
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 12)).pack()
        for svc, on in [("iCloud","✅"),("App Store","✅"),
                        ("FaceTime","✅"),("iMessage","✅"),("Find My","✅")]:
            row = tk.Frame(parent, bg=T["win_bg"])
            row.pack(fill="x", padx=20, pady=2)
            tk.Label(row, text=svc, bg=T["win_bg"],
                     fg=T["text"], font=(FONT_UI, 13)).pack(side="left")
            tk.Label(row, text=on, bg=T["win_bg"],
                     font=(FONT_EMOJI, 13)).pack(side="right")

    def _panel_users(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Users & Groups",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        for username in self.wm.users.list_users():
            row = tk.Frame(parent, bg=T["panel_bg"],
                           highlightthickness=1,
                           highlightbackground=T["separator"])
            row.pack(fill="x", padx=20, pady=4)
            tk.Label(row, text=self.wm.users.avatar(username),
                     bg=T["panel_bg"], font=(FONT_EMOJI, 28),
                     padx=10, pady=8).pack(side="left")
            info = tk.Frame(row, bg=T["panel_bg"])
            info.pack(side="left")
            tk.Label(info, text=self.wm.users.display_name(username),
                     bg=T["panel_bg"], fg=T["text"],
                     font=(FONT_UI, 13, "bold")).pack(anchor="w")
            role = "Admin" if self.wm.users.is_admin(username) else "Standard"
            tk.Label(info, text=f"{username}  •  {role}",
                     bg=T["panel_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 11)).pack(anchor="w")

    def _panel_language(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Language & Region",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        for label, options, key in [
            ("Language",     ["English","Español","Français","Deutsch","日本語","中文"],  "language"),
            ("Region",       ["United States","United Kingdom","Canada","Australia"],  "region"),
            ("Calendar",     ["Gregorian","Buddhist","Hebrew","Islamic"],              "calendar"),
            ("Temperature",  ["Fahrenheit","Celsius"],                                 "temp_unit"),
        ]:
            self._row(parent, label)
            var = tk.StringVar(value=self.wm.settings.get(key, options[0]))
            combo = ttk.Combobox(parent, textvariable=var, values=options,
                                  font=(FONT_UI, 12), state="readonly", width=24)
            combo.pack(padx=20, pady=3, anchor="w")
            combo.bind("<<ComboboxSelected>>",
                       lambda _, k=key, v=var: self.wm.settings.set(k, v.get()))

    def _panel_accessibility(self, parent: tk.Widget, _: str) -> None:
        tk.Label(parent, text="Accessibility",
                 bg=T["win_bg"], fg=T["text"],
                 font=(FONT_UI, 18, "bold"), pady=8).pack(anchor="w")
        for pref, key in [
            ("Increase Contrast",       "increase_contrast"),
            ("Reduce Motion",           "reduce_motion"),
            ("Reduce Transparency",     "reduce_transparency"),
            ("Bold Text",               "bold_text"),
            ("Larger Text",             "larger_text"),
            ("VoiceOver",               "voiceover"),
            ("Sticky Keys",             "sticky_keys"),
            ("Slow Keys",               "slow_keys"),
        ]:
            self._bool_pref(parent, pref, key)

    # ── helper methods ────────────────────────────────────────────────────────

    def _row(self, parent: tk.Widget, text: str) -> None:
        tk.Label(parent, text=text,
                 bg=T["win_bg"], fg=T["text_muted"],
                 font=(FONT_UI, 11, "bold"),
                 padx=20, pady=(8,0)).pack(anchor="w")

    def _bool_pref(self, parent: tk.Widget, label: str, key: str) -> None:
        var = tk.BooleanVar(value=bool(self.wm.settings.get(key, False)))
        row = tk.Frame(parent, bg=T["win_bg"])
        row.pack(fill="x", padx=20, pady=3)
        tk.Checkbutton(row, text=label, variable=var,
                        bg=T["win_bg"], fg=T["text"],
                        font=(FONT_UI, 13),
                        selectcolor=T["win_bg"],
                        activebackground=T["win_bg"],
                        command=lambda: self.wm.settings.set(key, var.get())
                        ).pack(side="left")

    def _search(self, query: str) -> None:
        if not query:
            self._show_grid(self.PANELS)
            return
        hits = [(icon, name, key) for icon, name, key in self.PANELS
                if query.lower() in name.lower()]
        if hits:
            self._show_grid(hits)
        else:
            for w in self._content.winfo_children():
                w.destroy()
            tk.Label(self._content, text=f'No results for "{query}"',
                     bg=T["win_bg"], fg=T["text_muted"],
                     font=(FONT_UI, 14), pady=40).pack()



# =============================================================================
#  MacPyOS — PART 5
#  App Store, System Preferences, Archive Utility, Contacts
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 35 — APP STORE
# ─────────────────────────────────────────────────────────────────────────────

class AppStoreApp(BaseWin):
    """macOS App Store."""

    FEATURED = [
        {"name":"Xcode","dev":"Apple","cat":"Developer Tools","rating":4.2,
         "price":"Free","desc":"Build apps for Apple platforms.","color":"#007aff","installed":True},
        {"name":"Final Cut Pro","dev":"Apple","cat":"Video","rating":4.7,
         "price":"$299.99","desc":"Professional video editing.","color":"#ff453a","installed":False},
        {"name":"Logic Pro","dev":"Apple","cat":"Music","rating":4.8,
         "price":"$199.99","desc":"Professional music production.","color":"#30d158","installed":False},
        {"name":"Affinity Designer","dev":"Serif","cat":"Graphics","rating":4.6,
         "price":"$69.99","desc":"Professional graphic design.","color":"#5e5ce6","installed":False},
        {"name":"Bear","dev":"Shiny Frog","cat":"Productivity","rating":4.7,
         "price":"Free","desc":"Writing app for notes.","color":"#ff9f0a","installed":True},
        {"name":"Reeder","dev":"Silvio Rizzi","cat":"News","rating":4.9,
         "price":"$4.99","desc":"The best RSS reader for Mac.","color":"#30d158","installed":False},
        {"name":"CleanMyMac","dev":"MacPaw","cat":"Utilities","rating":4.5,
         "price":"Free","desc":"Mac cleaning and optimization.","color":"#ff453a","installed":False},
        {"name":"Sketch","dev":"Sketch BV","cat":"Design","rating":4.4,
         "price":"$99/yr","desc":"Design toolkit for UI/UX.","color":"#ff9500","installed":False},
    ]

    CATEGORIES=["All","Developer Tools","Video","Music","Graphics","Productivity","Utilities","Design","News"]

    def __init__(self, wm):
        super().__init__(wm,title="App Store",w=800,h=560,icon="store")
        self._category="All"; self._tab="discover"
        self._installed=set(a["name"] for a in self.FEATURED if a["installed"])
        self._build_ui()

    def _build_ui(self):
        c=self.client
        # Toolbar
        toolbar=tk.Frame(c,bg=T["panel_bg"],
                         highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        self._tab_btns={}
        for key,label in [("discover","Discover"),("arcade","Arcade"),
                           ("create","Create"),("work","Work"),("play","Play"),
                           ("updates","Updates")]:
            btn=tk.Label(toolbar,text=label,bg=T["panel_bg"],
                         fg=T["text_muted"],font=(FONT_UI,12),
                         padx=12,pady=6,cursor="hand2")
            btn.pack(side="left")
            btn.bind("<Button-1>",lambda _,k=key: self._switch_tab(k))
            self._tab_btns[key]=btn
        self._search_var=tk.StringVar()
        se=tk.Entry(toolbar,textvariable=self._search_var,bg=T["input_bg"],
                    fg=T["text"],font=(FONT_UI,12),relief="flat",
                    highlightthickness=1,highlightbackground=T["input_border"],
                    highlightcolor=T["input_focus"],width=20)
        se.pack(side="right",padx=8,pady=4)
        tk.Label(toolbar,text="Search",bg=T["panel_bg"],fg=T["text_muted"],
                 font=(FONT_UI,11)).pack(side="right")
        self._search_var.trace_add("write",lambda *_: self._refresh_apps())

        self._content=tk.Frame(c,bg=T["win_bg"])
        self._content.pack(fill="both",expand=True)
        self._switch_tab("discover")

    def _switch_tab(self,tab):
        self._tab=tab
        for k,b in self._tab_btns.items():
            b.configure(bg=T["accent"] if k==tab else T["panel_bg"],
                        fg="#ffffff" if k==tab else T["text_muted"])
        for w in self._content.winfo_children(): w.destroy()
        if tab=="discover": self._build_discover()
        elif tab=="updates": self._build_updates()
        else: self._build_category(tab)

    def _build_discover(self):
        f=self._content
        # Hero banner
        hero=tk.Canvas(f,bg=T["accent"],height=140,highlightthickness=0)
        hero.pack(fill="x")
        hero.update_idletasks()
        w=hero.winfo_width() or 600
        for i in range(20):
            t=i/20
            r1=0;g1=0x7a;b1=0xff; r2=0x5e;g2=0x5c;b2=0xe6
            rc=int(r1+(r2-r1)*t); gc=int(g1+(g2-g1)*t); bc=int(b1+(b2-b1)*t)
            color=f"#{rc:02x}{gc:02x}{bc:02x}"
            hero.create_rectangle(i*w//20,0,(i+1)*w//20,140,fill=color,outline="")
        hero.create_text(w//2,50,text="App of the Day",fill="#ffffff",
                         font=(FONT_UI,13),anchor="center")
        hero.create_text(w//2,78,text="Discover amazing apps",fill="#ffffff",
                         font=(FONT_UI,22,"bold"),anchor="center")
        hero.create_text(w//2,108,text="Curated picks from the MacPyOS team",
                         fill="#ffffff",font=(FONT_UI,12),anchor="center")

        # Category filter
        cat_row=tk.Frame(f,bg=T["win_bg"]); cat_row.pack(fill="x",padx=12,pady=8)
        for cat in self.CATEGORIES:
            is_sel=(cat==self._category)
            b=tk.Label(cat_row,text=cat,cursor="hand2",
                       bg=T["accent"] if is_sel else T["panel_alt"],
                       fg="#ffffff" if is_sel else T["text"],
                       font=(FONT_UI,11),padx=10,pady=3)
            b.pack(side="left",padx=2)
            b.bind("<Button-1>",lambda _,cc=cat: self._set_category(cc))

        # App grid
        self._apps_sf=MacScrolledFrame(f,bg=T["win_bg"])
        self._apps_sf.pack(fill="both",expand=True)
        self._apps_inner=self._apps_sf.inner
        self._apps_inner.configure(bg=T["win_bg"])
        self._refresh_apps()

    def _set_category(self,cat):
        self._category=cat
        for w in self._content.winfo_children(): w.destroy()
        self._build_discover()

    def _refresh_apps(self):
        if not hasattr(self,"_apps_inner"): return
        for w in self._apps_inner.winfo_children(): w.destroy()
        q=self._search_var.get().lower() if hasattr(self,"_search_var") else ""
        apps=self.FEATURED
        if self._category!="All": apps=[a for a in apps if a["cat"]==self._category]
        if q: apps=[a for a in apps if q in a["name"].lower() or q in a["desc"].lower()]

        row_frame=None
        for i,app in enumerate(apps):
            if i%3==0:
                row_frame=tk.Frame(self._apps_inner,bg=T["win_bg"])
                row_frame.pack(fill="x",pady=6,padx=12)
            card=tk.Frame(row_frame,bg=T["panel_bg"],
                          highlightthickness=1,highlightbackground=T["separator"],
                          width=220)
            card.pack(side="left",padx=6); card.pack_propagate(False)
            # App icon (colored square)
            icon_cv=tk.Canvas(card,width=56,height=56,
                              bg=app["color"],highlightthickness=0)
            icon_cv.pack(padx=12,pady=(12,4))
            icon_cv.create_text(28,28,text=app["name"][0],fill="#ffffff",
                                font=(FONT_UI,24,"bold"))
            tk.Label(card,text=app["name"],bg=T["panel_bg"],fg=T["text"],
                     font=(FONT_UI,13,"bold")).pack(anchor="w",padx=12)
            tk.Label(card,text=app["dev"],bg=T["panel_bg"],fg=T["text_muted"],
                     font=(FONT_UI,11)).pack(anchor="w",padx=12)
            tk.Label(card,text=app["desc"],bg=T["panel_bg"],fg=T["text_muted"],
                     font=(FONT_UI,10),wraplength=180,justify="left").pack(anchor="w",padx=12,pady=2)
            # Rating
            stars="".join(["*" if j<int(app["rating"]) else "." for j in range(5)])
            tk.Label(card,text=f"{stars} {app['rating']}",bg=T["panel_bg"],
                     fg=T["warning"],font=(FONT_UI,11)).pack(anchor="w",padx=12)
            # Get/Open button
            installed=app["name"] in self._installed
            btn_text="Open" if installed else app["price"]
            btn_bg=T["button_secondary"] if installed else T["accent"]
            btn_fg=T["text"] if installed else "#ffffff"
            btn=tk.Button(card,text=btn_text,bg=btn_bg,fg=btn_fg,
                          font=(FONT_UI,11),relief="flat",padx=12,pady=3,
                          cursor="hand2",
                          command=lambda a=app: self._get_app(a))
            btn.pack(anchor="w",padx=12,pady=(4,12))

    def _get_app(self,app):
        if app["name"] in self._installed:
            self.wm.notifs.send(app["name"],"Launching...",icon="store")
        else:
            self._installed.add(app["name"])
            app["installed"]=True
            self.wm.notifs.send("App Store",
                                 f"{app['name']} installed successfully!",icon="store")
            self._refresh_apps()

    def _build_updates(self):
        f=self._content
        tk.Label(f,text="Updates",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=16).pack()
        tk.Button(f,text="Update All",bg=T["accent"],fg="#ffffff",
                  font=(FONT_UI,14),relief="flat",padx=20,pady=6,
                  cursor="hand2",
                  command=lambda: self.wm.notifs.send("App Store","All apps updated!",icon="store")
                  ).pack(pady=8)
        for app in self.FEATURED[:3]:
            row=tk.Frame(f,bg=T["panel_bg"],
                         highlightthickness=1,highlightbackground=T["separator"])
            row.pack(fill="x",padx=16,pady=4)
            tk.Label(row,text=app["name"],bg=T["panel_bg"],fg=T["text"],
                     font=(FONT_UI,13,"bold"),padx=12,pady=6).pack(side="left")
            tk.Label(row,text="Version 2.0 available",bg=T["panel_bg"],
                     fg=T["text_muted"],font=(FONT_UI,11)).pack(side="left")
            tk.Button(row,text="Update",bg=T["accent"],fg="#ffffff",
                      font=(FONT_UI,11),relief="flat",padx=10,pady=3,
                      cursor="hand2",
                      command=lambda a=app: self.wm.notifs.send("App Store",
                                                                  f"{a['name']} updated!",icon="store")
                      ).pack(side="right",padx=8)

    def _build_category(self,tab):
        f=self._content
        labels={"arcade":"Arcade Games","create":"Create","work":"Work","play":"Play"}
        tk.Label(f,text=labels.get(tab,tab.title()),bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,20,"bold"),pady=20).pack()
        tk.Label(f,text="Coming soon in MacPyOS 2.0",bg=T["win_bg"],
                 fg=T["text_muted"],font=(FONT_UI,14)).pack()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 36 — SYSTEM PREFERENCES
# ─────────────────────────────────────────────────────────────────────────────

class SystemPreferencesApp(BaseWin):
    """macOS System Preferences — 10 panels."""

    PANELS=[
        ("General",       "gen"),
        ("Desktop & Screen Saver", "desktop"),
        ("Dock",          "dock"),
        ("Notifications", "notifs"),
        ("Sound",         "sound"),
        ("Appearance",    "appearance"),
        ("Users & Groups","users"),
        ("Privacy",       "privacy"),
        ("Network",       "network"),
        ("Date & Time",   "datetime"),
    ]

    def __init__(self, wm, panel=None):
        super().__init__(wm,title="System Preferences",w=720,h=540,icon="prefs")
        self._panel=panel or "General"
        self._build_ui()
        # Open requested panel
        for name,key in self.PANELS:
            if name==panel: self._open_panel(name,key); break
        else:
            self._show_grid()

    def _build_ui(self):
        c=self.client
        # Toolbar
        toolbar=tk.Frame(c,bg=T["panel_bg"],
                         highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        self._back_btn=tk.Label(toolbar,text="< All Preferences",
                                 bg=T["panel_bg"],fg=T["accent"],
                                 font=(FONT_UI,12),padx=8,pady=5,cursor="hand2")
        self._back_btn.pack(side="left")
        self._back_btn.bind("<Button-1>",lambda _: self._show_grid())
        self._title_lbl=tk.Label(toolbar,text="System Preferences",
                                  bg=T["panel_bg"],fg=T["text"],
                                  font=(FONT_UI,14,"bold"),padx=8)
        self._title_lbl.pack(side="left")
        self._search_var=tk.StringVar()
        se=tk.Entry(toolbar,textvariable=self._search_var,bg=T["input_bg"],
                    fg=T["text"],font=(FONT_UI,12),relief="flat",
                    highlightthickness=1,highlightbackground=T["input_border"],
                    highlightcolor=T["input_focus"],width=18)
        se.pack(side="right",padx=8,pady=4)
        self._content=tk.Frame(c,bg=T["win_bg"])
        self._content.pack(fill="both",expand=True)
        self._show_grid()

    def _show_grid(self):
        for w in self._content.winfo_children(): w.destroy()
        self._title_lbl.configure(text="System Preferences")
        icons={"General":"[G]","Desktop & Screen Saver":"[D]","Dock":"[Dock]",
               "Notifications":"[N]","Sound":"[S]","Appearance":"[A]",
               "Users & Groups":"[U]","Privacy":"[P]","Network":"[Net]","Date & Time":"[T]"}
        sf=MacScrolledFrame(self._content,bg=T["win_bg"])
        sf.pack(fill="both",expand=True)
        inner=sf.inner; inner.configure(bg=T["win_bg"])
        row_frame=None
        for i,(name,key) in enumerate(self.PANELS):
            if i%5==0:
                row_frame=tk.Frame(inner,bg=T["win_bg"]); row_frame.pack(fill="x",pady=8,padx=20)
            cell=tk.Frame(row_frame,bg=T["win_bg"],width=110,cursor="hand2")
            cell.pack(side="left",padx=8); cell.pack_propagate(False)
            ic=tk.Label(cell,text=icons.get(name,"[?]"),bg=T["panel_bg"],
                        fg=T["accent"],font=(FONT_UI,20),width=3,height=2)
            ic.pack()
            lbl=tk.Label(cell,text=name,bg=T["win_bg"],fg=T["text"],
                         font=(FONT_UI,11),wraplength=90,justify="center")
            lbl.pack()
            for w in (cell,ic,lbl):
                w.bind("<Button-1>",lambda _,n=name,k=key: self._open_panel(n,k))

    def _open_panel(self,name,key):
        for w in self._content.winfo_children(): w.destroy()
        self._title_lbl.configure(text=name)
        panel_builders={
            "gen":self._panel_general,"desktop":self._panel_desktop,
            "dock":self._panel_dock,"notifs":self._panel_notifs,
            "sound":self._panel_sound,"appearance":self._panel_appearance,
            "users":self._panel_users,"privacy":self._panel_privacy,
            "network":self._panel_network,"datetime":self._panel_datetime,
        }
        builder=panel_builders.get(key,self._panel_stub)
        builder()

    def _panel_general(self):
        f=self._content
        tk.Label(f,text="General",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        s=self.wm.settings
        # Appearance
        row=tk.Frame(f,bg=T["win_bg"]); row.pack(fill="x",padx=20,pady=6)
        tk.Label(row,text="Appearance:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,13),width=18,anchor="e").pack(side="left")
        for val,label in [("Light","Light"),("Dark","Dark"),("Auto","Auto")]:
            v=s.get("appearance","Auto")
            rb=tk.Radiobutton(row,text=label,bg=T["win_bg"],fg=T["text"],
                               font=(FONT_UI,12),cursor="hand2",
                               activebackground=T["win_bg"],
                               command=lambda v=val: s.set("appearance",v))
            rb.pack(side="left",padx=4)
        # Theme
        row2=tk.Frame(f,bg=T["win_bg"]); row2.pack(fill="x",padx=20,pady=6)
        tk.Label(row2,text="Theme:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,13),width=18,anchor="e").pack(side="left")
        theme_var=tk.StringVar(value=s.get("theme","Monterey"))
        theme_menu=ttk.Combobox(row2,textvariable=theme_var,
                                 values=list(THEMES.keys()),
                                 state="readonly",width=18)
        theme_menu.pack(side="left",padx=8)
        def apply_theme_cb(*_):
            name=theme_var.get()
            apply_theme(name); s.set("theme",name)
            self.wm.notifs.send("System Preferences",
                                 f"Theme changed to {name}",icon="prefs")
        theme_var.trace_add("write",apply_theme_cb)
        # Font size
        row3=tk.Frame(f,bg=T["win_bg"]); row3.pack(fill="x",padx=20,pady=6)
        tk.Label(row3,text="Font size:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,13),width=18,anchor="e").pack(side="left")
        fs_var=tk.IntVar(value=s.get("font_size",13))
        tk.Scale(row3,variable=fs_var,from_=10,to=18,orient="horizontal",
                 bg=T["win_bg"],fg=T["text"],highlightthickness=0,
                 troughcolor=T["progress_bg"],activebackground=T["accent"],
                 command=lambda v: s.set("font_size",int(float(v)))).pack(side="left",padx=8)
        tk.Label(row3,textvariable=fs_var,bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,12)).pack(side="left")

    def _panel_desktop(self):
        f=self._content
        tk.Label(f,text="Desktop & Screen Saver",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        s=self.wm.settings
        tk.Label(f,text="Wallpaper:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,13),padx=20,pady=4).pack(anchor="w")
        wp_options=[("gradient_blue","Blue Gradient"),("gradient_sunset","Sunset"),
                    ("solid_dark","Solid Dark"),("solid_sand","Sand")]
        wp_var=tk.StringVar(value=s.get("wallpaper","gradient_blue"))
        for val,label in wp_options:
            row=tk.Frame(f,bg=T["win_bg"]); row.pack(fill="x",padx=40,pady=2)
            rb=tk.Radiobutton(row,text=label,variable=wp_var,value=val,
                               bg=T["win_bg"],fg=T["text"],font=(FONT_UI,13),
                               activebackground=T["win_bg"],cursor="hand2",
                               command=lambda v=val: (s.set("wallpaper",v),
                                                      self.wm._draw_wallpaper()))
            rb.pack(side="left")

    def _panel_dock(self):
        f=self._content
        tk.Label(f,text="Dock",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        s=self.wm.settings
        for key,label,default in [("dock_magnification","Magnification",True),
                                   ("dock_autohide","Auto-hide",False)]:
            row=tk.Frame(f,bg=T["win_bg"]); row.pack(fill="x",padx=20,pady=6)
            var=tk.BooleanVar(value=s.get(key,default))
            tk.Checkbutton(row,text=label,variable=var,bg=T["win_bg"],fg=T["text"],
                           font=(FONT_UI,13),activebackground=T["win_bg"],cursor="hand2",
                           command=lambda k=key,v=var: s.set(k,v.get())).pack(side="left")

    def _panel_notifs(self):
        f=self._content
        tk.Label(f,text="Notifications",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        s=self.wm.settings
        for key,label,default in [("notifications","Allow Notifications",True),
                                   ("do_not_disturb","Do Not Disturb",False)]:
            row=tk.Frame(f,bg=T["win_bg"]); row.pack(fill="x",padx=20,pady=6)
            var=tk.BooleanVar(value=s.get(key,default))
            tk.Checkbutton(row,text=label,variable=var,bg=T["win_bg"],fg=T["text"],
                           font=(FONT_UI,13),activebackground=T["win_bg"],cursor="hand2",
                           command=lambda k=key,v=var: s.set(k,v.get())).pack(side="left")

    def _panel_sound(self):
        f=self._content
        tk.Label(f,text="Sound",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        s=self.wm.settings
        row=tk.Frame(f,bg=T["win_bg"]); row.pack(fill="x",padx=20,pady=6)
        tk.Label(row,text="Output volume:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,13),width=18,anchor="e").pack(side="left")
        vol_var=tk.IntVar(value=75)
        tk.Scale(row,variable=vol_var,from_=0,to=100,orient="horizontal",
                 bg=T["win_bg"],fg=T["text"],highlightthickness=0,
                 troughcolor=T["progress_bg"],activebackground=T["accent"],
                 length=200).pack(side="left",padx=8)
        row2=tk.Frame(f,bg=T["win_bg"]); row2.pack(fill="x",padx=20,pady=6)
        var=tk.BooleanVar(value=s.get("sound_enabled",True))
        tk.Checkbutton(row2,text="Play sound effects",variable=var,
                       bg=T["win_bg"],fg=T["text"],font=(FONT_UI,13),
                       activebackground=T["win_bg"],cursor="hand2",
                       command=lambda: s.set("sound_enabled",var.get())).pack(side="left")

    def _panel_appearance(self):
        f=self._content
        tk.Label(f,text="Appearance",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        tk.Label(f,text="Accent Color:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,13),padx=20,pady=4).pack(anchor="w")
        colors_row=tk.Frame(f,bg=T["win_bg"]); colors_row.pack(fill="x",padx=20,pady=4)
        colors=[("#007aff","Blue"),("#ff453a","Red"),("#30d158","Green"),
                ("#ff9f0a","Orange"),("#5e5ce6","Purple"),("#ff375f","Pink"),
                ("#8e8e93","Graphite")]
        for color,name in colors:
            swatch=tk.Frame(colors_row,bg=color,width=28,height=28,cursor="hand2")
            swatch.pack(side="left",padx=4)
            swatch.bind("<Button-1>",lambda _,c=color: (self.wm.settings.set("accent_color",c),
                                                         self.wm.notifs.send("Appearance",f"Accent: {c}",icon="prefs")))
            make_tooltip(swatch,name)

    def _panel_users(self):
        f=self._content
        tk.Label(f,text="Users & Groups",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        for username in self.wm.users.list_users():
            row=tk.Frame(f,bg=T["panel_bg"],
                         highlightthickness=1,highlightbackground=T["separator"])
            row.pack(fill="x",padx=20,pady=4)
            avatar=self.wm.users.avatar(username)
            tk.Label(row,text=avatar,bg=T["panel_bg"],font=(FONT_UI,24),padx=10).pack(side="left")
            info=tk.Frame(row,bg=T["panel_bg"]); info.pack(side="left",pady=6)
            tk.Label(info,text=self.wm.users.display_name(username),bg=T["panel_bg"],
                     fg=T["text"],font=(FONT_UI,13,"bold")).pack(anchor="w")
            role="Admin" if self.wm.users.is_admin(username) else "Standard"
            tk.Label(info,text=role,bg=T["panel_bg"],fg=T["text_muted"],
                     font=(FONT_UI,11)).pack(anchor="w")
            if username==self.wm.users.current_user():
                tk.Label(row,text="Current",bg=T["panel_bg"],
                         fg=T["accent"],font=(FONT_UI,11)).pack(side="right",padx=12)

    def _panel_privacy(self):
        f=self._content
        tk.Label(f,text="Privacy & Security",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        for label in ["Location Services","Contacts","Calendars","Reminders",
                       "Photos","Camera","Microphone","Full Disk Access"]:
            row=tk.Frame(f,bg=T["win_bg"]); row.pack(fill="x",padx=20,pady=4)
            tk.Label(row,text=label,bg=T["win_bg"],fg=T["text"],
                     font=(FONT_UI,13),width=24,anchor="w").pack(side="left")
            var=tk.BooleanVar(value=random.choice([True,False]))
            tk.Checkbutton(row,variable=var,bg=T["win_bg"],
                           activebackground=T["win_bg"]).pack(side="left")

    def _panel_network(self):
        f=self._content
        tk.Label(f,text="Network",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        for iface,status,ip in [("Wi-Fi","Connected","192.168.1."+str(random.randint(2,254))),
                                  ("Ethernet","Not connected",""),
                                  ("Bluetooth PAN","Not connected",""),
                                  ("Thunderbolt Bridge","Not connected","")]:
            row=tk.Frame(f,bg=T["panel_bg"],
                         highlightthickness=1,highlightbackground=T["separator"])
            row.pack(fill="x",padx=20,pady=4)
            dot_color=T["accent3"] if "Connected"==status else T["text_muted"]
            tk.Label(row,text="*",bg=T["panel_bg"],fg=dot_color,
                     font=(FONT_UI,16),padx=8).pack(side="left")
            info=tk.Frame(row,bg=T["panel_bg"]); info.pack(side="left",pady=6)
            tk.Label(info,text=iface,bg=T["panel_bg"],fg=T["text"],
                     font=(FONT_UI,13,"bold")).pack(anchor="w")
            desc=f"{status}  {ip}".strip()
            tk.Label(info,text=desc,bg=T["panel_bg"],fg=T["text_muted"],
                     font=(FONT_UI,11)).pack(anchor="w")

    def _panel_datetime(self):
        f=self._content
        tk.Label(f,text="Date & Time",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12,padx=20).pack(anchor="w")
        now=datetime.datetime.now()
        tk.Label(f,text=now.strftime("%A, %B %d, %Y"),bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,20),pady=8).pack()
        tk.Label(f,text=now.strftime("%I:%M:%S %p"),bg=T["win_bg"],fg=T["accent"],
                 font=(FONT_MONO,36),pady=4).pack()
        s=self.wm.settings
        row=tk.Frame(f,bg=T["win_bg"]); row.pack(fill="x",padx=20,pady=8)
        tk.Label(row,text="Time format:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,13),width=16,anchor="e").pack(side="left")
        tf_var=tk.StringVar(value=s.get("time_format","12h"))
        for val,label in [("12h","12-hour"),("24h","24-hour")]:
            tk.Radiobutton(row,text=label,variable=tf_var,value=val,
                           bg=T["win_bg"],fg=T["text"],font=(FONT_UI,12),
                           activebackground=T["win_bg"],cursor="hand2",
                           command=lambda v=val: s.set("time_format",v)).pack(side="left",padx=4)
        tz_row=tk.Frame(f,bg=T["win_bg"]); tz_row.pack(fill="x",padx=20,pady=4)
        tk.Label(tz_row,text="Time zone:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,13),width=16,anchor="e").pack(side="left")
        tz_var=tk.StringVar(value=s.get("timezone","America/New_York"))
        tz_menu=ttk.Combobox(tz_row,textvariable=tz_var,width=24,state="readonly",
                              values=["America/New_York","America/Chicago",
                                      "America/Los_Angeles","Europe/London",
                                      "Europe/Paris","Asia/Tokyo","Asia/Shanghai",
                                      "Australia/Sydney"])
        tz_menu.pack(side="left",padx=8)
        tz_var.trace_add("write",lambda *_: s.set("timezone",tz_var.get()))

    def _panel_stub(self):
        f=self._content
        tk.Label(f,text="Panel not yet implemented",bg=T["win_bg"],fg=T["text_muted"],
                 font=(FONT_UI,14)).pack(expand=True)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 37 — ARCHIVE UTILITY
# ─────────────────────────────────────────────────────────────────────────────

class ArchiveUtilityApp(BaseWin):
    """macOS Archive Utility — zip/unzip files in the VFS."""

    def __init__(self, wm):
        super().__init__(wm,title="Archive Utility",w=560,h=440,icon="zip")
        self._build_ui()

    def _build_ui(self):
        c=self.client
        tk.Label(c,text="Archive Utility",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,18,"bold"),pady=12).pack()
        # Compress
        compress_frame=tk.LabelFrame(c,text="Compress",bg=T["win_bg"],fg=T["text"],
                                      font=(FONT_UI,13,"bold"),padx=12,pady=8)
        compress_frame.pack(fill="x",padx=20,pady=8)
        row=tk.Frame(compress_frame,bg=T["win_bg"]); row.pack(fill="x",pady=4)
        tk.Label(row,text="Source:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,12),width=12,anchor="e").pack(side="left")
        self._src_var=tk.StringVar(value="/Users/user/Documents")
        tk.Entry(row,textvariable=self._src_var,bg=T["input_bg"],fg=T["text"],
                 font=(FONT_UI,12),relief="flat",highlightthickness=1,
                 highlightbackground=T["input_border"],
                 highlightcolor=T["input_focus"]).pack(side="left",fill="x",expand=True,padx=4)
        row2=tk.Frame(compress_frame,bg=T["win_bg"]); row2.pack(fill="x",pady=4)
        tk.Label(row2,text="Archive name:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,12),width=12,anchor="e").pack(side="left")
        self._arc_var=tk.StringVar(value="Archive.zip")
        tk.Entry(row2,textvariable=self._arc_var,bg=T["input_bg"],fg=T["text"],
                 font=(FONT_UI,12),relief="flat",highlightthickness=1,
                 highlightbackground=T["input_border"],
                 highlightcolor=T["input_focus"]).pack(side="left",fill="x",expand=True,padx=4)
        tk.Button(compress_frame,text="Create Archive",bg=T["accent"],fg="#ffffff",
                  font=(FONT_UI,13),relief="flat",padx=16,pady=4,cursor="hand2",
                  command=self._compress).pack(pady=8)

        # Extract
        extract_frame=tk.LabelFrame(c,text="Extract",bg=T["win_bg"],fg=T["text"],
                                     font=(FONT_UI,13,"bold"),padx=12,pady=8)
        extract_frame.pack(fill="x",padx=20,pady=8)
        row3=tk.Frame(extract_frame,bg=T["win_bg"]); row3.pack(fill="x",pady=4)
        tk.Label(row3,text="Archive:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,12),width=12,anchor="e").pack(side="left")
        self._ext_src_var=tk.StringVar()
        tk.Entry(row3,textvariable=self._ext_src_var,bg=T["input_bg"],fg=T["text"],
                 font=(FONT_UI,12),relief="flat",highlightthickness=1,
                 highlightbackground=T["input_border"],
                 highlightcolor=T["input_focus"]).pack(side="left",fill="x",expand=True,padx=4)
        row4=tk.Frame(extract_frame,bg=T["win_bg"]); row4.pack(fill="x",pady=4)
        tk.Label(row4,text="Destination:",bg=T["win_bg"],fg=T["text"],
                 font=(FONT_UI,12),width=12,anchor="e").pack(side="left")
        self._ext_dst_var=tk.StringVar(value="/Users/user/Downloads")
        tk.Entry(row4,textvariable=self._ext_dst_var,bg=T["input_bg"],fg=T["text"],
                 font=(FONT_UI,12),relief="flat",highlightthickness=1,
                 highlightbackground=T["input_border"],
                 highlightcolor=T["input_focus"]).pack(side="left",fill="x",expand=True,padx=4)
        tk.Button(extract_frame,text="Extract Archive",bg=T["button_secondary"],fg=T["text"],
                  font=(FONT_UI,13),relief="flat",padx=16,pady=4,cursor="hand2",
                  command=self._extract).pack(pady=8)

        # Log
        log_frame=tk.LabelFrame(c,text="Log",bg=T["win_bg"],fg=T["text"],
                                 font=(FONT_UI,12),padx=8,pady=4)
        log_frame.pack(fill="both",expand=True,padx=20,pady=4)
        self._log=tk.Text(log_frame,bg=T["code_bg"],fg=T["code_fg"],
                           font=(FONT_MONO,11),relief="flat",height=5,
                           state="disabled",highlightthickness=0)
        self._log.pack(fill="both",expand=True)

    def _log_msg(self,msg):
        self._log.configure(state="normal")
        self._log.insert("end",msg+"\n")
        self._log.configure(state="disabled")
        self._log.see("end")

    def _compress(self):
        src=self._src_var.get(); arc_name=self._arc_var.get()
        if not self.wm.vfs.exists(src):
            self._log_msg(f"ERROR: Source not found: {src}"); return
        dst_path=f"/Users/user/Downloads/{arc_name}"
        # Simulate compression
        files=[]
        if self.wm.vfs.isdir(src):
            try: files=self.wm.vfs.listdir(src)
            except: pass
        manifest=f"Archive: {arc_name}\nSource: {src}\nFiles: {len(files)}\nCreated: {datetime.datetime.now()}\n"
        for f in files: manifest+=f"  + {f}\n"
        self.wm.vfs.write(dst_path,manifest)
        self._log_msg(f"Created {arc_name} ({len(files)} files) -> {dst_path}")
        self.wm.notifs.send("Archive Utility",f"Archive created: {arc_name}",icon="zip")

    def _extract(self):
        src=self._ext_src_var.get(); dst=self._ext_dst_var.get()
        if not self.wm.vfs.exists(src):
            self._log_msg(f"ERROR: Archive not found: {src}"); return
        arc_name=src.split("/")[-1].replace(".zip","").replace(".tar","").replace(".gz","")
        out_dir=dst.rstrip("/")+"/"+arc_name
        self.wm.vfs.makedirs(out_dir)
        content=self.wm.vfs.read(src) if self.wm.vfs.isfile(src) else ""
        self.wm.vfs.write(out_dir+"/CONTENTS.txt",content)
        self._log_msg(f"Extracted {src} -> {out_dir}")
        self.wm.notifs.send("Archive Utility",f"Extracted to {out_dir}",icon="zip")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 38 — CONTACTS
# ─────────────────────────────────────────────────────────────────────────────

class ContactsApp(BaseWin):
    """macOS Contacts — address book."""

    SAMPLE_CONTACTS=[
        {"first":"Alice","last":"Johnson","email":"alice@company.com","phone":"(415) 555-0101","company":"Apple Inc","group":"Work"},
        {"first":"Bob","last":"Smith","email":"bob@gmail.com","phone":"(650) 555-0102","company":"Google","group":"Work"},
        {"first":"Carol","last":"White","email":"carol@me.com","phone":"(408) 555-0103","company":"","group":"Friends"},
        {"first":"David","last":"Brown","email":"david@outlook.com","phone":"(510) 555-0104","company":"Microsoft","group":"Work"},
        {"first":"Eve","last":"Davis","email":"eve@icloud.com","phone":"(415) 555-0105","company":"","group":"Family"},
        {"first":"Frank","last":"Miller","email":"frank@yahoo.com","phone":"(650) 555-0106","company":"Meta","group":"Work"},
        {"first":"Grace","last":"Lee","email":"grace@gmail.com","phone":"(408) 555-0107","company":"","group":"Friends"},
        {"first":"Henry","last":"Wilson","email":"henry@company.com","phone":"(510) 555-0108","company":"Amazon","group":"Work"},
    ]

    def __init__(self, wm):
        super().__init__(wm,title="Contacts",w=680,h=520,icon="contacts")
        self._contacts=[dict(c) for c in self.SAMPLE_CONTACTS]
        self._selected=None; self._group="All"
        self._build_ui()

    def _build_ui(self):
        c=self.client
        # Toolbar
        toolbar=tk.Frame(c,bg=T["panel_bg"],
                         highlightthickness=1,highlightbackground=T["separator"])
        toolbar.pack(fill="x")
        def tb_btn(text,cmd,tip=""):
            b=tk.Label(toolbar,text=text,bg=T["panel_bg"],fg=T["text"],
                       font=(FONT_UI,12),padx=8,pady=5,cursor="hand2")
            b.pack(side="left"); b.bind("<Button-1>",lambda _: cmd())
            if tip: make_tooltip(b,tip)
        tb_btn("+ New",self._new_contact,"New contact")
        tb_btn("Edit",self._edit_contact,"Edit selected")
        tb_btn("Delete",self._delete_contact,"Delete selected")
        self._search_var=tk.StringVar()
        se=tk.Entry(toolbar,textvariable=self._search_var,bg=T["input_bg"],fg=T["text"],
                    font=(FONT_UI,12),relief="flat",highlightthickness=1,
                    highlightbackground=T["input_border"],
                    highlightcolor=T["input_focus"],width=20)
        se.pack(side="right",padx=8,pady=4)
        tk.Label(toolbar,text="Search",bg=T["panel_bg"],fg=T["text_muted"],
                 font=(FONT_UI,11)).pack(side="right")
        self._search_var.trace_add("write",lambda *_: self._refresh_list())

        pane=tk.Frame(c,bg=T["win_bg"]); pane.pack(fill="both",expand=True)

        # Group sidebar
        sidebar=tk.Frame(pane,bg=T["sidebar_bg"],width=150)
        sidebar.pack(side="left",fill="y"); sidebar.pack_propagate(False)
        tk.Label(sidebar,text="Groups",bg=T["sidebar_bg"],fg=T["text"],
                 font=(FONT_UI,12,"bold"),padx=12,pady=8).pack(anchor="w")
        groups=["All","Work","Friends","Family"]
        for g in groups:
            row=tk.Frame(sidebar,bg=T["sidebar_bg"],cursor="hand2")
            row.pack(fill="x")
            lbl=tk.Label(row,text=g,bg=T["sidebar_bg"],fg=T["text"],
                         font=(FONT_UI,12),anchor="w",padx=12,pady=4)
            lbl.pack(fill="x")
            for w in (row,lbl):
                w.bind("<Button-1>",lambda _,gr=g: self._set_group(gr))
                w.bind("<Enter>",lambda _,r=row: r.configure(bg=T["menu_hover"]))
                w.bind("<Leave>",lambda _,r=row: r.configure(bg=T["sidebar_bg"]))

        tk.Frame(pane,bg=T["separator"],width=1).pack(side="left",fill="y")

        # Contact list
        list_frame=tk.Frame(pane,bg=T["win_bg"],width=220)
        list_frame.pack(side="left",fill="y"); list_frame.pack_propagate(False)
        self._list_sf=MacScrolledFrame(list_frame,bg=T["win_bg"])
        self._list_sf.pack(fill="both",expand=True)
        self._list_inner=self._list_sf.inner
        self._list_inner.configure(bg=T["win_bg"])

        tk.Frame(pane,bg=T["separator"],width=1).pack(side="left",fill="y")

        # Detail pane
        self._detail=tk.Frame(pane,bg=T["win_bg"])
        self._detail.pack(side="left",fill="both",expand=True)

        self._refresh_list()

    def _set_group(self,group):
        self._group=group; self._refresh_list()

    def _refresh_list(self):
        for w in self._list_inner.winfo_children(): w.destroy()
        q=self._search_var.get().lower() if hasattr(self,"_search_var") else ""
        contacts=self._contacts
        if self._group!="All": contacts=[c for c in contacts if c["group"]==self._group]
        if q: contacts=[c for c in contacts if q in (c["first"]+" "+c["last"]).lower()
                         or q in c["email"].lower()]
        # Sort alphabetically
        contacts=sorted(contacts,key=lambda c: c["last"])
        current_letter=""
        for i,contact in enumerate(contacts):
            letter=contact["last"][0].upper() if contact["last"] else "#"
            if letter!=current_letter:
                current_letter=letter
                tk.Label(self._list_inner,text=letter,bg=T["panel_alt"],
                         fg=T["text_muted"],font=(FONT_UI,10,"bold"),
                         padx=8,pady=2).pack(fill="x")
            idx=self._contacts.index(contact)
            is_sel=(idx==self._selected)
            bg=T["selection"] if is_sel else T["win_bg"]
            row=tk.Frame(self._list_inner,bg=bg,cursor="hand2")
            row.pack(fill="x")
            row.bind("<Button-1>",lambda _,idx2=idx: self._select(idx2))
            # Avatar circle (initials)
            init=contact["first"][0]+contact["last"][0]
            colors=["#007aff","#30d158","#ff9f0a","#ff453a","#5e5ce6","#ff375f"]
            av_color=colors[idx%len(colors)]
            av=tk.Label(row,text=init,bg=av_color,fg="#ffffff",
                        font=(FONT_UI,11,"bold"),width=3)
            av.pack(side="left",padx=6,pady=4)
            name=f"{contact['first']} {contact['last']}"
            lbl=tk.Label(row,text=name,bg=bg,fg=T["text"],
                         font=(FONT_UI,12),anchor="w")
            lbl.pack(side="left",fill="x",expand=True)
            for w in (row,av,lbl):
                w.bind("<Button-1>",lambda _,idx2=idx: self._select(idx2))

    def _select(self,idx):
        self._selected=idx
        for w in self._detail.winfo_children(): w.destroy()
        c=self._contacts[idx]
        # Avatar
        colors=["#007aff","#30d158","#ff9f0a","#ff453a","#5e5ce6","#ff375f"]
        av_color=colors[idx%len(colors)]
        init=c["first"][0]+c["last"][0]
        av=tk.Label(self._detail,text=init,bg=av_color,fg="#ffffff",
                    font=(FONT_UI,36,"bold"),width=3,pady=10)
        av.pack(pady=20)
        tk.Label(self._detail,text=f"{c['first']} {c['last']}",
                 bg=T["win_bg"],fg=T["text"],font=(FONT_UI,20,"bold")).pack()
        if c["company"]:
            tk.Label(self._detail,text=c["company"],bg=T["win_bg"],
                     fg=T["text_muted"],font=(FONT_UI,13)).pack()
        tk.Frame(self._detail,bg=T["separator"],height=1).pack(fill="x",padx=20,pady=10)
        for icon,label,val in [("@","Email",c["email"]),("phone","Phone",c["phone"])]:
            if val:
                row=tk.Frame(self._detail,bg=T["win_bg"]); row.pack(fill="x",padx=20,pady=3)
                tk.Label(row,text=label,bg=T["win_bg"],fg=T["text_muted"],
                         font=(FONT_UI,11),width=8,anchor="e").pack(side="left")
                tk.Label(row,text=val,bg=T["win_bg"],fg=T["accent"],
                         font=(FONT_UI,13),cursor="hand2").pack(side="left",padx=8)
        # Action buttons
        btn_row=tk.Frame(self._detail,bg=T["win_bg"]); btn_row.pack(pady=16)
        for lbl,cmd in [("Send Email",lambda e=c["email"]: self.wm.open_mail()),
                         ("FaceTime",lambda: self.wm.notifs.send("FaceTime","Calling...",icon="contacts")),
                         ("Send Message",lambda: self.wm.notifs.send("Messages","Message sent",icon="contacts"))]:
            tk.Button(btn_row,text=lbl,bg=T["button_secondary"],fg=T["text"],
                      font=(FONT_UI,11),relief="flat",padx=10,pady=4,
                      cursor="hand2",command=cmd).pack(side="left",padx=4)
        self._refresh_list()

    def _new_contact(self):
        dlg=tk.Toplevel(self.wm.root); dlg.title("New Contact")
        dlg.geometry("380x320"); dlg.configure(bg=T["win_bg"]); dlg.transient(self.wm.root)
        fields={}
        for label,key,default in [("First Name:","first",""),("Last Name:","last",""),
                                    ("Email:","email",""),("Phone:","phone",""),
                                    ("Company:","company","")]:
            row=tk.Frame(dlg,bg=T["win_bg"]); row.pack(fill="x",padx=16,pady=3)
            tk.Label(row,text=label,bg=T["win_bg"],fg=T["text"],
                     font=(FONT_UI,12),width=12,anchor="e").pack(side="left")
            e=tk.Entry(row,bg=T["input_bg"],fg=T["text"],font=(FONT_UI,12),relief="flat",
                       highlightthickness=1,highlightbackground=T["input_border"])
            e.insert(0,default); e.pack(side="left",fill="x",expand=True,padx=4)
            fields[key]=e
        def save():
            contact={k:v.get() for k,v in fields.items()}
            contact["group"]="All"
            self._contacts.append(contact); dlg.destroy(); self._refresh_list()
        tk.Button(dlg,text="Add Contact",bg=T["accent"],fg="#ffffff",
                  font=(FONT_UI,13),relief="flat",padx=16,pady=6,
                  cursor="hand2",command=save).pack(pady=12)

    def _edit_contact(self):
        if self._selected is None:
            self.wm.notifs.send("Contacts","Select a contact first.",icon="contacts"); return
        c=self._contacts[self._selected]
        dlg=tk.Toplevel(self.wm.root); dlg.title("Edit Contact")
        dlg.geometry("380x320"); dlg.configure(bg=T["win_bg"]); dlg.transient(self.wm.root)
        fields={}
        for label,key in [("First Name:","first"),("Last Name:","last"),
                           ("Email:","email"),("Phone:","phone"),("Company:","company")]:
            row=tk.Frame(dlg,bg=T["win_bg"]); row.pack(fill="x",padx=16,pady=3)
            tk.Label(row,text=label,bg=T["win_bg"],fg=T["text"],
                     font=(FONT_UI,12),width=12,anchor="e").pack(side="left")
            e=tk.Entry(row,bg=T["input_bg"],fg=T["text"],font=(FONT_UI,12),relief="flat",
                       highlightthickness=1,highlightbackground=T["input_border"])
            e.insert(0,c.get(key,"")); e.pack(side="left",fill="x",expand=True,padx=4)
            fields[key]=e
        def save():
            for k,v in fields.items(): self._contacts[self._selected][k]=v.get()
            dlg.destroy(); self._refresh_list(); self._select(self._selected)
        tk.Button(dlg,text="Save",bg=T["accent"],fg="#ffffff",
                  font=(FONT_UI,13),relief="flat",padx=16,pady=6,
                  cursor="hand2",command=save).pack(pady=12)

    def _delete_contact(self):
        if self._selected is None: return
        name=f"{self._contacts[self._selected]['first']} {self._contacts[self._selected]['last']}"
        if messagebox.askyesno("Delete Contact",f"Delete {name}?",parent=self.wm.root):
            self._contacts.pop(self._selected); self._selected=None
            for w in self._detail.winfo_children(): w.destroy()
            self._refresh_list()


# =============================================================================
#  MacPyOS — PART 7  (FINAL)
#  WM app launchers, Boot animation, Login screen, Lock screen,
#  Global shortcuts, populate VFS, main()
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 37 — WM APP LAUNCHER METHODS  (patch WM class)
# ─────────────────────────────────────────────────────────────────────────────

def _wm_open_clock(self) -> None:
    ClockApp(self)

def _wm_open_activity_monitor(self) -> None:
    ActivityMonitorApp(self)

def _wm_open_notes(self) -> None:
    NotesApp(self)

def _wm_open_mail(self) -> None:
    MailApp(self)

def _wm_open_keychain(self) -> None:
    KeychainApp(self)

def _wm_open_numbers(self, path: Optional[str] = None) -> None:
    NumbersApp(self, path)

def _wm_open_photos(self) -> None:
    PhotosApp(self)

def _wm_open_disk_utility(self) -> None:
    DiskUtilityApp(self)

def _wm_open_script_editor(self, path: Optional[str] = None) -> None:
    ScriptEditorApp(self, path)

def _wm_open_archive_utility(self) -> None:
    ArchiveUtilityApp(self)

def _wm_open_contacts(self) -> None:
    ContactsApp(self)

def _wm_open_app_store(self) -> None:
    AppStoreApp(self)

def _wm_open_preferences(self, panel: Optional[str] = None) -> None:
    SystemPreferencesApp(self, panel)

def _wm_force_quit(self) -> None:
    ForceQuitDialog(self)

# Patch all launcher methods onto WM class
WM.open_clock            = _wm_open_clock
WM.open_activity_monitor = _wm_open_activity_monitor
WM.open_notes            = _wm_open_notes
WM.open_mail             = _wm_open_mail
WM.open_keychain         = _wm_open_keychain
WM.open_numbers          = _wm_open_numbers
WM.open_photos           = _wm_open_photos
WM.open_disk_utility     = _wm_open_disk_utility
WM.open_script_editor    = _wm_open_script_editor
WM.open_archive_utility  = _wm_open_archive_utility
WM.open_contacts         = _wm_open_contacts
WM.open_app_store        = _wm_open_app_store
WM.open_preferences      = _wm_open_preferences
WM.force_quit_dialog     = _wm_force_quit


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 38 — POPULATE VFS WITH RICHER DEFAULT FILES
# ─────────────────────────────────────────────────────────────────────────────

def populate_vfs(vfs: VFS) -> None:
    """Write default files and directories into the virtual filesystem."""

    # Developer / Scripts
    vfs.makedirs("/Users/user/Developer/Scripts")
    vfs.makedirs("/Users/user/Developer/Projects")
    vfs.write("/Users/user/Developer/Scripts/hello.py",
              '#!/usr/bin/env python3\n'
              '"""Hello, MacPyOS!"""\n\n'
              'import datetime\n\n\n'
              'def greet(name: str = "World") -> str:\n'
              '    now = datetime.datetime.now().strftime("%H:%M")\n'
              '    return f"Hello, {name}! The time is {now}."\n\n\n'
              'if __name__ == "__main__":\n'
              '    print(greet("MacPyOS"))\n')

    vfs.write("/Users/user/Developer/Scripts/fibonacci.py",
              '#!/usr/bin/env python3\n'
              '"""Fibonacci sequence generator."""\n\n\n'
              'def fib(n: int) -> list:\n'
              '    seq = [0, 1]\n'
              '    while len(seq) < n:\n'
              '        seq.append(seq[-1] + seq[-2])\n'
              '    return seq[:n]\n\n\n'
              'if __name__ == "__main__":\n'
              '    print("First 20 Fibonacci numbers:")\n'
              '    print(fib(20))\n')

    vfs.write("/Users/user/Developer/Scripts/sort_demo.py",
              '#!/usr/bin/env python3\n'
              '"""Sorting algorithm demonstrations."""\n\n'
              'import random\n\n\n'
              'def bubble_sort(arr):\n'
              '    n = len(arr)\n'
              '    for i in range(n):\n'
              '        for j in range(n - i - 1):\n'
              '            if arr[j] > arr[j+1]:\n'
              '                arr[j], arr[j+1] = arr[j+1], arr[j]\n'
              '    return arr\n\n\n'
              'if __name__ == "__main__":\n'
              '    data = random.sample(range(100), 10)\n'
              '    print("Before:", data)\n'
              '    print("After: ", bubble_sort(data))\n')

    # Documents
    vfs.makedirs("/Users/user/Documents/Notes")
    vfs.write("/Users/user/Documents/Notes/Welcome.txt",
              "Welcome to Notes\n\nThis is your first note.")
    vfs.write("/Users/user/Documents/Notes/Ideas.md",
              "# Ideas\n\n- MacPyOS themes\n- New apps\n- Performance tweaks\n")
    vfs.write("/Users/user/Documents/ReadMe.txt",
              "MacPyOS v1.0 — Sequoia\n"
              "A macOS-inspired desktop environment built with Python and Tkinter.\n\n"
              "Getting Started:\n"
              "  • Click apps in the Dock to open them\n"
              "  • Use ⌘Space (Ctrl+Space) to open Spotlight\n"
              "  • Right-click desktop for context menu\n"
              "  • Drag windows by their title bar\n"
              "  • Click traffic lights: ● close  ● minimise  ● fullscreen\n")

    vfs.write("/Users/user/Documents/budget.csv",
              "Month,Income,Expenses,Savings\n"
              "January,5000,3200,1800\n"
              "February,5200,3100,2100\n"
              "March,4800,3400,1400\n"
              "April,5500,2900,2600\n"
              "May,5100,3300,1800\n"
              "June,5300,3000,2300\n")

    # Spreadsheets dir
    vfs.makedirs("/Users/user/Spreadsheets")
    vfs.write("/Users/user/Spreadsheets/sample.csv",
              "Name,Q1,Q2,Q3,Q4,Total\n"
              "Alice,1200,1350,1100,1500,=SUM(B2:E2)\n"
              "Bob,980,1050,1200,1100,=SUM(B3:E3)\n"
              "Carol,1500,1400,1600,1700,=SUM(B4:E4)\n"
              "Total,=SUM(B2:B4),=SUM(C2:C4),=SUM(D2:D4),=SUM(E2:E4),\n")

    # Shell scripts
    vfs.write("/Users/user/Developer/Scripts/backup.sh",
              "#!/bin/zsh\n"
              "# Simple VFS backup script\n"
              "echo 'Starting backup...'\n"
              "cp -r ~/Documents ~/Desktop/backup_$(date +%Y%m%d)\n"
              "echo 'Backup complete!'\n")

    # Music playlists
    vfs.makedirs("/Users/user/Music/Playlists")
    vfs.write("/Users/user/Music/Playlists/Favourites.m3u",
              "#EXTM3U\n"
              "#EXTINF:213,Clair de Lune - Debussy\n"
              "clair_de_lune.mp3\n"
              "#EXTINF:245,Moonlight Sonata - Beethoven\n"
              "moonlight_sonata.mp3\n"
              "#EXTINF:180,Gymnopedie No.1 - Satie\n"
              "gymnopedie.mp3\n")

    # Desktop shortcuts / files
    vfs.write("/Users/user/Desktop/about.txt",
              "MacPyOS v1.0.0 'Sequoia'\n"
              "Built with Python 3 + Tkinter\n"
              "No external dependencies\n"
              "© 2025 MacPyOS Project\n")

    # Library / Preferences
    vfs.makedirs("/Users/user/Library/Preferences")
    vfs.write("/Users/user/Library/Preferences/com.macpyos.plist",
              '<?xml version="1.0" encoding="UTF-8"?>\n'
              '<plist version="1.0"><dict>\n'
              '  <key>theme</key><string>Monterey</string>\n'
              '  <key>wallpaper</key><string>gradient_blue</string>\n'
              '  <key>dock_position</key><string>bottom</string>\n'
              '</dict></plist>\n')

    # Pictures
    vfs.makedirs("/Users/user/Pictures/Screenshots")
    vfs.write("/Users/user/Pictures/Screenshots/readme.txt",
              "Screenshots are stored here.\n")

    # Downloads
    vfs.makedirs("/Users/user/Downloads")
    vfs.write("/Users/user/Downloads/readme.txt",
              "Files you download appear here.\n")

    # Movies
    vfs.makedirs("/Users/user/Movies")
    vfs.write("/Users/user/Movies/readme.txt",
              "Your movies and video recordings appear here.\n")


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 39 — BOOT ANIMATION
# ─────────────────────────────────────────────────────────────────────────────

class BootAnimation:
    """macOS-style boot screen: Apple logo + progress bar."""

    APPLE_LOGO = """
     ██████
   ██      ██
  ██  ████  ██
  ██  ████  ██
   ██      ██
    ████████
      ████
  ██████████
 ████████████
 ████████████
  ██████████
   █  ████
"""

    def __init__(self, root: tk.Tk, on_done: Callable) -> None:
        self.root    = root
        self.on_done = on_done
        self._build()
        self._progress = 0
        self._animate()

    def _build(self) -> None:
        self.frame = tk.Frame(self.root, bg="#000000")
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Centre container
        centre = tk.Frame(self.frame, bg="#000000")
        centre.place(relx=0.5, rely=0.45, anchor="center")

        # Apple  logo (text art)
        tk.Label(centre, text="",
                 bg="#000000", fg="#ffffff",
                 font=(FONT_EMOJI, 96)).pack()

        # Tagline
        tk.Label(centre, text="macOS",
                 bg="#000000", fg="#ffffff",
                 font=(FONT_UI, 28, "bold"), pady=8).pack()
        tk.Label(centre, text=f"MacPyOS  {MACPYOS_VERSION}  — Sequoia",
                 bg="#000000", fg="#888888",
                 font=(FONT_UI, 14)).pack()

        # Progress bar track
        track_w = 200
        bar_frame = tk.Frame(self.frame, bg="#000000")
        bar_frame.place(relx=0.5, rely=0.78, anchor="center")
        self.track = tk.Canvas(bar_frame, width=track_w, height=6,
                                bg="#333333", highlightthickness=0)
        self.track.pack()
        self.prog_bar = self.track.create_rectangle(
            0, 0, 0, 6, fill="#ffffff", outline=""
        )
        self._track_w = track_w

        tk.Label(self.frame, text=f"MacPyOS {MACPYOS_VERSION}",
                 bg="#000000", fg="#555555",
                 font=(FONT_UI, 10)).place(relx=0.5, rely=0.92, anchor="center")

    def _animate(self) -> None:
        if self._progress >= self._track_w:
            self.frame.after(300, self._finish)
            return
        step = random.randint(4, 14)
        self._progress = min(self._progress + step, self._track_w)
        self.track.coords(self.prog_bar, 0, 0, self._progress, 6)
        delay = random.randint(40, 120)
        self.frame.after(delay, self._animate)

    def _finish(self) -> None:
        self.frame.destroy()
        self.on_done()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 40 — LOGIN SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class LoginScreen:
    """macOS-style login screen with user avatars."""

    def __init__(self, root: tk.Tk, users: "UserManager",
                 on_login: Callable[[str], None]) -> None:
        self.root     = root
        self.users    = users
        self.on_login = on_login
        self._build()

    def _build(self) -> None:
        self.frame = tk.Frame(self.root, bg="#1c1c1e")
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Background gradient (canvas)
        bg_canvas = tk.Canvas(self.frame, bg="#1a1a2e",
                               highlightthickness=0)
        bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        bg_canvas.bind("<Configure>", self._draw_bg)

        self.bg_canvas = bg_canvas

        # Clock
        self.clock_lbl = tk.Label(self.frame, text="",
                                   bg="#1a1a2e", fg="#ffffff",
                                   font=(FONT_UI, 64, "bold"))
        self.clock_lbl.place(relx=0.5, rely=0.18, anchor="center")
        self.date_lbl = tk.Label(self.frame, text="",
                                  bg="#1a1a2e", fg="#ffffff",
                                  font=(FONT_UI, 18))
        self.date_lbl.place(relx=0.5, rely=0.28, anchor="center")
        self._update_clock()

        # User selector
        user_frame = tk.Frame(self.frame, bg="#1a1a2e")
        user_frame.place(relx=0.5, rely=0.52, anchor="center")
        self._selected_user: Optional[str] = None

        user_list = self.users.list_users()
        for uname in user_list:
            col = tk.Frame(user_frame, bg="#1a1a2e", cursor="hand2")
            col.pack(side="left", padx=20)
            avatar = tk.Label(col, text=self.users.avatar(uname),
                               bg="#2c2c2e", font=(FONT_EMOJI, 36),
                               width=3, height=2,
                               relief="flat")
            avatar.pack()
            tk.Label(col, text=self.users.display_name(uname),
                     bg="#1a1a2e", fg="#ffffff",
                     font=(FONT_UI, 13)).pack(pady=4)
            avatar.bind("<Button-1>",
                        lambda _, u=uname, av=avatar: self._select_user(u, av))
            col.bind("<Button-1>",
                     lambda _, u=uname, av=avatar: self._select_user(u, av))

        # Password entry
        self._pw_frame = tk.Frame(self.frame, bg="#1a1a2e")
        self._pw_frame.place(relx=0.5, rely=0.70, anchor="center")

        self._pw_user_lbl = tk.Label(self._pw_frame, text="",
                                      bg="#1a1a2e", fg="#ffffff",
                                      font=(FONT_UI, 16, "bold"))
        self._pw_user_lbl.pack()

        pw_row = tk.Frame(self._pw_frame, bg="#1a1a2e")
        pw_row.pack(pady=8)
        self._pw_entry = tk.Entry(pw_row, show="•",
                                   bg="#2c2c2e", fg="#ffffff",
                                   font=(FONT_UI, 16), relief="flat",
                                   highlightthickness=2,
                                   highlightbackground="#555555",
                                   highlightcolor="#ffffff",
                                   insertbackground="#ffffff",
                                   width=18)
        self._pw_entry.pack(side="left", padx=4)
        tk.Button(pw_row, text="→",
                  bg="#007aff", fg="#ffffff",
                  font=(FONT_UI, 16, "bold"),
                  relief="flat", cursor="hand2",
                  command=self._attempt_login).pack(side="left")
        self._pw_entry.bind("<Return>", lambda _: self._attempt_login())
        self._err_lbl = tk.Label(self._pw_frame, text="",
                                  bg="#1a1a2e", fg="#ff453a",
                                  font=(FONT_UI, 12))
        self._err_lbl.pack()

        # Select first user automatically
        if user_list:
            first_avatar = user_frame.winfo_children()[0].winfo_children()[0]
            self._select_user(user_list[0], first_avatar)

    def _draw_bg(self, _: tk.Event) -> None:
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        self.bg_canvas.delete("all")
        # Simple radial-ish gradient using lines
        steps = 30
        for i in range(steps):
            t = i / steps
            r = int(0x1a + (0x0d - 0x1a) * t)
            g = int(0x1a + (0x10 - 0x1a) * t)
            b = int(0x2e + (0x35 - 0x2e) * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.bg_canvas.create_rectangle(
                0, int(h * i / steps), w, int(h * (i+1) / steps),
                fill=color, outline=""
            )

    def _update_clock(self) -> None:
        try:
            if not self.frame.winfo_exists():
                return
        except Exception:
            return
        now = datetime.datetime.now()
        self.clock_lbl.configure(text=now.strftime("%I:%M"))
        self.date_lbl.configure(
            text=_strftime("%A, %B %-d", now) 
        )
        self.frame.after(10000, self._update_clock)

    def _select_user(self, username: str, avatar_widget: tk.Label) -> None:
        self._selected_user = username
        self._pw_user_lbl.configure(text=self.users.display_name(username))
        self._pw_entry.delete(0, "end")
        self._err_lbl.configure(text="")
        self._pw_entry.focus_set()

    def _attempt_login(self) -> None:
        if not self._selected_user:
            return
        pw = self._pw_entry.get()
        if self.users.authenticate(self._selected_user, pw):
            self.frame.destroy()
            self.on_login(self._selected_user)
        else:
            self._err_lbl.configure(text="Incorrect password. Try again.")
            self._pw_entry.delete(0, "end")
            self._pw_entry.configure(highlightbackground="#ff453a")
            self.frame.after(1500, lambda: self._pw_entry.configure(
                highlightbackground="#555555"))


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 41 — LOCK SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class LockScreen:
    """macOS-style lock screen — appears on lock, dismissed on correct password."""

    def __init__(self, wm: "WM") -> None:
        self.wm = wm
        self._build()

    def _build(self) -> None:
        self.frame = tk.Frame(self.wm.root, bg="#000000")
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.lift()

        # Background
        bg = tk.Canvas(self.frame, bg="#0a0a1a", highlightthickness=0)
        bg.place(x=0, y=0, relwidth=1, relheight=1)

        # Clock
        self.clock_lbl = tk.Label(self.frame, text="",
                                   bg="#0a0a1a", fg="#ffffff",
                                   font=(FONT_UI, 72, "bold"))
        self.clock_lbl.place(relx=0.5, rely=0.30, anchor="center")
        self.date_lbl = tk.Label(self.frame, text="",
                                  bg="#0a0a1a", fg="#ffffff",
                                  font=(FONT_UI, 20))
        self.date_lbl.place(relx=0.5, rely=0.42, anchor="center")

        # User info
        user = self.wm.users.current_user
        tk.Label(self.frame, text=self.wm.users.avatar(user),
                 bg="#0a0a1a", font=(FONT_EMOJI, 36),
                 ).place(relx=0.5, rely=0.57, anchor="center")
        tk.Label(self.frame, text=self.wm.users.display_name(user),
                 bg="#0a0a1a", fg="#ffffff",
                 font=(FONT_UI, 18, "bold")).place(relx=0.5, rely=0.65, anchor="center")

        # Password
        pw_frame = tk.Frame(self.frame, bg="#0a0a1a")
        pw_frame.place(relx=0.5, rely=0.75, anchor="center")
        pw_row = tk.Frame(pw_frame, bg="#0a0a1a")
        pw_row.pack()
        self._pw = tk.Entry(pw_row, show="•",
                             bg="#1c1c1e", fg="#ffffff",
                             font=(FONT_UI, 16), relief="flat",
                             highlightthickness=2,
                             highlightbackground="#555555",
                             highlightcolor="#007aff",
                             insertbackground="#ffffff",
                             width=18)
        self._pw.pack(side="left", padx=4)
        tk.Button(pw_row, text="→",
                  bg="#007aff", fg="#ffffff",
                  font=(FONT_UI, 16, "bold"), relief="flat",
                  command=self._unlock).pack(side="left")
        self._pw.bind("<Return>", lambda _: self._unlock())
        self._err = tk.Label(pw_frame, text="",
                              bg="#0a0a1a", fg="#ff453a",
                              font=(FONT_UI, 12))
        self._err.pack(pady=4)
        self._pw.focus_set()

        self._update_clock()

    def _update_clock(self) -> None:
        try:
            if not self.frame.winfo_exists():
                return
        except Exception:
            return
        now = datetime.datetime.now()
        self.clock_lbl.configure(text=now.strftime("%I:%M"))
        self.date_lbl.configure(text=now.strftime("%A, %B %d"))
        self.frame.after(10000, self._update_clock)

    def _unlock(self) -> None:
        pw = self._pw.get()
        user = self.wm.users.current_user
        if self.wm.users.authenticate(user, pw):
            self.frame.destroy()
            self.wm.notifs.send("MacPyOS",
                                 f"Welcome back, {self.wm.users.display_name(user)}!",
                                 icon="🔓")
        else:
            self._err.configure(text="Incorrect password.")
            self._pw.delete(0, "end")
            self._pw.configure(highlightbackground="#ff453a")
            self.frame.after(1500, lambda: self._pw.configure(
                highlightbackground="#555555"))


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 42 — GLOBAL KEYBOARD SHORTCUTS
# ─────────────────────────────────────────────────────────────────────────────

def bind_global_shortcuts(root: tk.Tk, wm: "WM") -> None:
    """Bind global macOS-style keyboard shortcuts."""

    def on_ctrl_space(_: tk.Event) -> None:
        wm.toggle_spotlight()

    def on_ctrl_tab(_: tk.Event) -> str:
        # Cycle through open windows
        wins = wm.all_wins()
        if wins:
            wins[0].frame.lift()
            wins[0].frame.focus_force()
        return "break"

    def on_ctrl_q(_: tk.Event) -> None:
        # Quit focused app
        focused = root.focus_get()
        if focused:
            w = focused
            while w and not isinstance(w, BaseWin):
                try:
                    w = w.master
                except AttributeError:
                    break
            if isinstance(w, BaseWin):
                w.close()

    def on_ctrl_m(_: tk.Event) -> None:
        # Minimise focused window
        focused = root.focus_get()
        if focused:
            w = focused
            while w and not isinstance(w, BaseWin):
                try:
                    w = w.master
                except AttributeError:
                    break
            if isinstance(w, BaseWin):
                w.minimise()

    def on_ctrl_f(_: tk.Event) -> None:
        # Fullscreen
        focused = root.focus_get()
        if focused:
            w = focused
            while w and not isinstance(w, BaseWin):
                try:
                    w = w.master
                except AttributeError:
                    break
            if isinstance(w, BaseWin):
                w.toggle_maximise()

    def on_ctrl_l(_: tk.Event) -> None:
        LockScreen(wm)

    def on_ctrl_n(_: tk.Event) -> None:
        wm.open_notes()

    def on_ctrl_t(_: tk.Event) -> None:
        wm.open_terminal()

    def on_ctrl_comma(_: tk.Event) -> None:
        wm.open_preferences()

    # macOS uses Cmd (Meta on Linux/Win) but we use Ctrl for portability
    bindings = [
        ("<Control-space>",  on_ctrl_space),
        ("<Control-Tab>",    on_ctrl_tab),
        ("<Control-q>",      on_ctrl_q),
        ("<Control-m>",      on_ctrl_m),
        ("<Control-f>",      on_ctrl_f),
        ("<Control-l>",      on_ctrl_l),
        ("<Control-n>",      on_ctrl_n),
        ("<Control-t>",      on_ctrl_t),
        ("<Control-comma>",  on_ctrl_comma),
    ]
    for key, handler in bindings:
        root.bind(key, handler)

    # Also bind Meta (Cmd key on macOS)
    for key, handler in bindings:
        meta_key = key.replace("Control", "Meta")
        try:
            root.bind(meta_key, handler)
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 43 — UserManager helpers needed by login/lock screens
# ─────────────────────────────────────────────────────────────────────────────

def _um_list_users(self) -> List[str]:
    return list(self._users.keys())

def _um_avatar(self, username: Optional[str] = None) -> str:
    u = username or self._current or "user"
    return {"user":"👤","admin":"🛡️","guest":"👥"}.get(u, "👤")

def _um_display_name(self, username: Optional[str] = None) -> str:
    u = username or self._current or "user"
    data = self._users.get(u, {})
    dn = data.get("display_name","")
    return dn if dn else u.title()

def _um_is_admin(self, username: Optional[str] = None) -> bool:
    u = username or self._current or "user"
    return "admin" in self._users.get(u, {}).get("groups", [])

def _um_avatar_color(self, username: Optional[str] = None) -> str:
    u = username or self._current or "user"
    return {"user":"#007aff","admin":"#5856d6","guest":"#8e8e93"}.get(u, "#007aff")

def _um_authenticate(self, username: str, password: str) -> bool:
    return self.login(username, password)

UserManager.list_users   = _um_list_users
UserManager.avatar       = _um_avatar
UserManager.display_name = _um_display_name
UserManager.is_admin     = _um_is_admin
UserManager.avatar_color = _um_avatar_color
if not hasattr(UserManager, "authenticate"):
    UserManager.authenticate = _um_authenticate


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 44 — MISSING IMPORTS CHECK  (top-level safeguard)
# ─────────────────────────────────────────────────────────────────────────────

# Ensure all standard-library modules used throughout are available
import base64
import zipfile
import traceback


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 45 — MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    """MacPyOS entry point — boot → login → desktop."""

    root = tk.Tk()
    root.title(f"MacPyOS {MACPYOS_VERSION} — Sequoia")
    root.geometry(f"{SCREEN_W}x{SCREEN_H}")
    root.resizable(False, False)
    root.configure(bg="#000000")

    # Try to set a nice window icon
    try:
        root.iconbitmap("")  # silently ignore missing .ico
    except Exception:
        pass

    # Initialise subsystems (shared across boot → login → desktop)
    vfs   = VFS()
    populate_vfs(vfs)
    users = UserManager()
    clip  = Clipboard()

    # ── Stage 1: Boot animation ───────────────────────────────────────────────
    def on_boot_done() -> None:
        _show_login()

    def _show_login() -> None:
        def on_logged_in(username: str) -> None:
            users.current_user = username
            _start_desktop(username)
        LoginScreen(root, users, on_logged_in)

    # ── Stage 2: Desktop ──────────────────────────────────────────────────────
    def _start_desktop(username: str) -> None:
        notifs = NotificationManager(root)
        procs  = ProcessManager()
        stg    = Settings()

        # Apply saved theme
        saved_theme = stg.get("theme", "Monterey")
        apply_theme(saved_theme)

        # Build the window manager
        wm = WM(root)
        wm.vfs    = vfs
        wm.users  = users
        wm.clip   = clip
        wm.notifs = notifs
        wm.procs  = procs
        wm.settings = stg

        # Populate VFS with richer defaults
        # (already called above but make sure notes dir exists)
        vfs.makedirs(f"/Users/{username}/Documents/Notes")

        # Build menubar and dock
        menubar = MenuBar(root, wm)
        wm.menubar = menubar
        dock    = Dock(root, wm)
        wm.dock = dock

        # Bind global shortcuts
        bind_global_shortcuts(root, wm)

        # Welcome notification (slight delay to let the UI settle)
        root.after(600, lambda: notifs.send(
            "MacPyOS",
            f"Welcome to MacPyOS {MACPYOS_VERSION}, "
            f"{users.display_name(username)}!",
            icon="🍎",
            duration=5.0,
        ))

        # Auto-open Finder on startup
        root.after(800, lambda: wm.open_finder())

    # Kick off boot animation
    BootAnimation(root, on_boot_done)

    root.mainloop()


if __name__ == "__main__":
    main()


# =============================================================================
#  MacPyOS — PART 7  (FINAL)
#  Boot Animation, Login Screen, Lock Screen, Global Shortcuts, main()
# =============================================================================

# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 37 — BOOT ANIMATION
# ─────────────────────────────────────────────────────────────────────────────

class BootScreen:
    """macOS-style Apple logo boot animation with progress bar."""

    def __init__(self, root: tk.Tk, on_done: Callable) -> None:
        self.root    = root
        self.on_done = on_done
        self._frame  = 0
        self._total  = 80
        self._build()
        self._animate()

    def _build(self) -> None:
        self.frame = tk.Frame(self.root, bg="#000000")
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.lift()

        center_x = self.root.winfo_width() // 2
        center_y = self.root.winfo_height() // 2

        self.canvas = tk.Canvas(
            self.frame,
            bg="#000000",
            highlightthickness=0,
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Apple logo (text-based)
        self.logo_id = self.canvas.create_text(
            center_x, center_y - 40,
            text="",
            fill="#ffffff",
            font=(FONT_EMOJI, 80),
        )
        self.ver_id = self.canvas.create_text(
            center_x, center_y + 60,
            text=f"macOS MacPyOS {MACPYOS_VERSION}",
            fill="#ffffff",
            font=(FONT_UI, 14),
        )
        # Progress bar background
        bar_w = 200
        bar_h = 4
        bar_x = center_x - bar_w // 2
        bar_y = center_y + 100
        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_w, bar_y + bar_h,
            fill="#333333", outline="",
        )
        self.prog_bar = self.canvas.create_rectangle(
            bar_x, bar_y, bar_x, bar_y + bar_h,
            fill="#ffffff", outline="",
        )
        self._bar_x   = bar_x
        self._bar_y   = bar_y
        self._bar_w   = bar_w
        self._bar_h   = bar_h

    def _animate(self) -> None:
        if self._frame >= self._total:
            self.frame.destroy()
            self.on_done()
            return
        progress = self._frame / self._total
        x1 = self._bar_x
        y1 = self._bar_y
        x2 = self._bar_x + int(self._bar_w * progress)
        y2 = self._bar_y + self._bar_h
        self.canvas.coords(self.prog_bar, x1, y1, x2, y2)

        # Fade-in Apple logo
        alpha = min(255, int(255 * (self._frame / 20)))
        hex_color = f"#{alpha:02x}{alpha:02x}{alpha:02x}"
        self.canvas.itemconfigure(self.logo_id, fill=hex_color)

        self._frame += 1
        self.root.after(25, self._animate)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 38 — LOGIN SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class LoginScreen:
    """macOS-style login screen with user selection and password entry."""

    def __init__(self, root: tk.Tk, users: "UserManager", on_login: Callable) -> None:
        self.root     = root
        self.users    = users
        self.on_login = on_login
        self._build()

    def _build(self) -> None:
        self.frame = tk.Frame(self.root, bg="#1c1c1e")
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.lift()

        # Gradient-style background
        canvas = tk.Canvas(self.frame, bg="#1c1c1e", highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # Draw gradient
        sw = self.root.winfo_width()
        sh = self.root.winfo_height()
        steps = 40
        for i in range(steps):
            t = i / steps
            r = int(0x1c + (0x0a - 0x1c) * t)
            g = int(0x1c + (0x0a - 0x1c) * t)
            b = int(0x1e + (0x1e - 0x1e) * t)
            color = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(sh * i / steps)
            y1 = int(sh * (i+1) / steps)
            canvas.create_rectangle(0, y0, sw, y1, fill=color, outline="")

        # Clock
        self.time_lbl = tk.Label(
            self.frame, text="",
            bg="#1c1c1e", fg="#ffffff",
            font=(FONT_UI, 48, "bold"),
        )
        self.time_lbl.place(relx=0.5, rely=0.18, anchor="center")
        self.date_lbl = tk.Label(
            self.frame, text="",
            bg="#1c1c1e", fg="#ffffff",
            font=(FONT_UI, 18),
        )
        self.date_lbl.place(relx=0.5, rely=0.25, anchor="center")
        self._update_clock()

        # User buttons
        user_frame = tk.Frame(self.frame, bg="#1c1c1e")
        user_frame.place(relx=0.5, rely=0.5, anchor="center")

        self._selected_user = tk.StringVar()
        for username in self.users.list_users():
            col = tk.Frame(user_frame, bg="#1c1c1e", cursor="hand2")
            col.pack(side="left", padx=20)
            av_canvas = tk.Canvas(col, width=80, height=80,
                                   bg="#1c1c1e", highlightthickness=2,
                                   highlightbackground="#3a3a3c")
            av_canvas.pack()
            color = self.users.avatar_color(username)
            av_canvas.create_oval(4, 4, 76, 76, fill=color, outline="")
            av_canvas.create_text(40, 40,
                                   text=self.users.avatar(username),
                                   font=(FONT_EMOJI, 26), fill="#ffffff")
            name_lbl = tk.Label(col, text=self.users.display_name(username),
                     bg="#1c1c1e", fg="#ffffff",
                     font=(FONT_UI, 13))
            name_lbl.pack(pady=4)
            for w in (col, av_canvas, name_lbl):
                w.bind("<Button-1>",
                         lambda _, u=username: self._select_user(u))

        # Password field
        pw_frame = tk.Frame(self.frame, bg="#1c1c1e")
        pw_frame.place(relx=0.5, rely=0.68, anchor="center")

        self._pw_entry = tk.Entry(
            pw_frame,
            show="•",
            bg="#2c2c2e", fg="#ffffff",
            font=(FONT_UI, 16),
            relief="flat",
            highlightthickness=2,
            highlightbackground="#3a3a3c",
            highlightcolor="#0a84ff",
            width=22,
            justify="center",
        )
        self._pw_entry.pack(side="left", ipady=8, padx=4)
        self._pw_entry.bind("<Return>", lambda _: self._try_login())

        tk.Button(pw_frame, text="→",
                  bg="#0a84ff", fg="#ffffff",
                  font=(FONT_UI, 16, "bold"), relief="flat",
                  padx=10, pady=6, cursor="hand2",
                  command=self._try_login).pack(side="left")

        self._msg_lbl = tk.Label(self.frame, text="",
                                  bg="#1c1c1e", fg="#ff453a",
                                  font=(FONT_UI, 13))
        self._msg_lbl.place(relx=0.5, rely=0.80, anchor="center")

        # Create Account button
        signup_btn = tk.Label(
            self.frame, text="＋  Create New Account",
            bg="#0a84ff", fg="#ffffff",
            font=(FONT_UI, 13, "bold"),
            cursor="hand2", padx=20, pady=8,
        )
        signup_btn.place(relx=0.5, rely=0.88, anchor="center")
        signup_btn.bind("<Button-1>", lambda _: self._show_signup())
        signup_btn.bind("<Enter>", lambda _: signup_btn.configure(bg="#0070e0"))
        signup_btn.bind("<Leave>", lambda _: signup_btn.configure(bg="#0a84ff"))

        # hint text
        tk.Label(self.frame,
                 text="Default passwords — user: 'user'  |  admin: 'admin'  |  guest: (blank)",
                 bg="#1c1c1e", fg="#636366",
                 font=(FONT_UI, 10)).place(relx=0.5, rely=0.95, anchor="center")

        # Select first user
        users_list = self.users.list_users()
        if users_list:
            self._select_user(users_list[0])

    def _show_signup(self) -> None:
        dlg = tk.Toplevel(self.root)
        dlg.title("Create New Account")
        dlg.configure(bg="#1c1c1e")
        dlg.resizable(False, False)
        dlg.grab_set()

        # Size and centre the dialog
        dlg.update_idletasks()
        dw, dh = 460, 580
        sx = self.root.winfo_x() + (self.root.winfo_width()  - dw) // 2
        sy = self.root.winfo_y() + (self.root.winfo_height() - dh) // 2
        dlg.geometry(f"{dw}x{dh}+{sx}+{sy}")

        # ── Header ───────────────────────────────────────────────────────────
        tk.Label(dlg, text="Create Account",
                 bg="#1c1c1e", fg="#ffffff",
                 font=(FONT_UI, 20, "bold"), pady=12).pack()
        tk.Label(dlg, text="Set up your MacPyOS user account",
                 bg="#1c1c1e", fg="#8e8e93",
                 font=(FONT_UI, 12)).pack()
        tk.Frame(dlg, bg="#3a3a3c", height=1).pack(fill="x", padx=20, pady=8)

        # ── Fields ────────────────────────────────────────────────────────────
        fields: Dict[str, tk.Entry] = {}
        for label, key, secret in [
            ("Full Name",        "full_name", False),
            ("Username",         "username",  False),
            ("Password",         "password",  True),
            ("Confirm Password", "confirm",   True),
        ]:
            row = tk.Frame(dlg, bg="#1c1c1e")
            row.pack(fill="x", padx=30, pady=4)
            tk.Label(row, text=label, bg="#1c1c1e", fg="#8e8e93",
                     font=(FONT_UI, 11), anchor="w").pack(anchor="w")
            e = tk.Entry(row,
                         show="•" if secret else "",
                         bg="#2c2c2e", fg="#ffffff",
                         font=(FONT_UI, 13), relief="flat",
                         highlightthickness=1,
                         highlightbackground="#3a3a3c",
                         highlightcolor="#0a84ff",
                         insertbackground="#ffffff")
            e.pack(fill="x", ipady=6)
            fields[key] = e

        # ── Avatar ────────────────────────────────────────────────────────────
        tk.Label(dlg, text="Choose Avatar",
                 bg="#1c1c1e", fg="#8e8e93",
                 font=(FONT_UI, 11), padx=30).pack(anchor="w", pady=(6, 2))
        avatar_var = tk.StringVar(value="👤")
        av_row = tk.Frame(dlg, bg="#1c1c1e")
        av_row.pack(padx=30, anchor="w")

        def select_avatar(em, btn):
            avatar_var.set(em)
            for w in av_row.winfo_children():
                w.configure(bg="#2c2c2e")
            btn.configure(bg="#0a84ff")

        for emoji in ["👤", "🧑", "👩", "👨", "🧒", "🧓", "🎅", "🧑‍💻", "🦸", "🧙"]:
            b = tk.Label(av_row, text=emoji, bg="#2c2c2e",
                         font=(FONT_EMOJI, 18), padx=6, pady=4, cursor="hand2")
            b.pack(side="left", padx=2)
            b.bind("<Button-1>", lambda _, em=emoji, btn=b: select_avatar(em, btn))

        # ── Error label ───────────────────────────────────────────────────────
        err_lbl = tk.Label(dlg, text="", bg="#1c1c1e", fg="#ff453a",
                           font=(FONT_UI, 11))
        err_lbl.pack(pady=4)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_frame = tk.Frame(dlg, bg="#1c1c1e")
        btn_frame.pack(pady=8)

        def do_signup():
            full     = fields["full_name"].get().strip()
            username = fields["username"].get().strip().lower()
            pw       = fields["password"].get()
            confirm  = fields["confirm"].get()

            if not full or not username:
                err_lbl.configure(text="Full name and username are required.")
                return
            if len(username) < 3:
                err_lbl.configure(text="Username must be at least 3 characters.")
                return
            if not pw:
                err_lbl.configure(text="Password cannot be empty.")
                return
            if pw != confirm:
                err_lbl.configure(text="Passwords do not match.")
                return
            if username in self.users.list_users():
                err_lbl.configure(text=f"Username '{username}' already exists.")
                return

            # Create the account
            self.users._add(username, pw, full, avatar_var.get())
            dlg.destroy()
            self._msg_lbl.configure(
                text=f"✅  Account '{username}' created! Click your avatar to sign in.",
                fg="#30d158")
            # Rebuild the login screen to show the new avatar
            self.frame.destroy()
            self._build()

        tk.Button(btn_frame, text="  Create Account  ",
                  bg="#0a84ff", fg="#ffffff",
                  font=(FONT_UI, 13, "bold"), relief="flat",
                  padx=16, pady=8, cursor="hand2",
                  command=do_signup).pack(side="left", padx=8)
        tk.Button(btn_frame, text="  Cancel  ",
                  bg="#3a3a3c", fg="#ffffff",
                  font=(FONT_UI, 13), relief="flat",
                  padx=16, pady=8, cursor="hand2",
                  command=dlg.destroy).pack(side="left", padx=8)

        fields["full_name"].focus_set()

    def _select_user(self, username: str) -> None:
        self._selected_user.set(username)
        self._pw_entry.delete(0, "end")
        self._pw_entry.focus_set()
        self._msg_lbl.configure(text="")

    def _try_login(self) -> None:
        username = self._selected_user.get()
        password = self._pw_entry.get()
        if self.users.authenticate(username, password):
            self.frame.destroy()
            self.on_login(username)
        else:
            self._msg_lbl.configure(text="Incorrect password. Try again.")
            self._pw_entry.delete(0, "end")
            self._pw_entry.configure(highlightbackground="#ff453a")
            self.root.after(1500, lambda: self._pw_entry.configure(
                highlightbackground="#3a3a3c"
            ))

    def _update_clock(self) -> None:
        try:
            if not self.frame.winfo_exists():
                return
            now = datetime.datetime.now()
            self.time_lbl.configure(text=now.strftime("%I:%M"))
            self.date_lbl.configure(text=now.strftime("%A, %B %d"))
            self.root.after(1000, self._update_clock)  # guarded above
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 39 — LOCK SCREEN
# ─────────────────────────────────────────────────────────────────────────────

class LockScreen:
    """macOS-style lock screen overlay."""

    def __init__(self, wm: "WM", on_unlock: Callable) -> None:
        self.wm        = wm
        self.on_unlock = on_unlock
        self._build()

    def _build(self) -> None:
        self.frame = tk.Frame(self.wm.root, bg="#000000")
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.lift()

        canvas = tk.Canvas(self.frame, bg="#000000", highlightthickness=0)
        canvas.place(x=0, y=0, relwidth=1, relheight=1)
        # Blurred-looking gradient
        steps = 30
        for i in range(steps):
            t = i / steps
            r = int(0x0a * (1-t))
            b = int(0x1e * (1-t) + 0x3a * t)
            g = int(0x0a * (1-t))
            color = f"#{r:02x}{g:02x}{b:02x}"
            y0 = int(SCREEN_H * i / steps)
            y1 = int(SCREEN_H * (i+1) / steps)
            canvas.create_rectangle(0, y0, SCREEN_W, y1, fill=color, outline="")

        # Time
        self.time_lbl = tk.Label(
            self.frame, text="",
            bg="#000000", fg="#ffffff",
            font=(FONT_UI, 56, "bold"),
        )
        self.time_lbl.place(relx=0.5, rely=0.28, anchor="center")
        self.date_lbl = tk.Label(
            self.frame, text="",
            bg="#000000", fg="#ffffff",
            font=(FONT_UI, 20),
        )
        self.date_lbl.place(relx=0.5, rely=0.37, anchor="center")
        self._tick()

        # User avatar
        av_canvas = tk.Canvas(self.frame, width=80, height=80,
                               bg="#000000", highlightthickness=0)
        av_canvas.place(relx=0.5, rely=0.55, anchor="center")
        av_canvas.create_oval(2, 2, 78, 78,
                               fill=self.wm.users.avatar_color(
                                   self.wm.current_user), outline="")
        av_canvas.create_text(40, 40,
                               text=self.wm.users.avatar(self.wm.current_user),
                               font=(FONT_EMOJI, 28))
        tk.Label(self.frame,
                 text=self.wm.users.display_name(self.wm.current_user),
                 bg="#000000", fg="#ffffff",
                 font=(FONT_UI, 15)).place(relx=0.5, rely=0.63, anchor="center")

        # Password
        pw_frame = tk.Frame(self.frame, bg="#000000")
        pw_frame.place(relx=0.5, rely=0.73, anchor="center")
        self._pw = tk.Entry(
            pw_frame, show="•",
            bg="#1c1c1e", fg="#ffffff",
            font=(FONT_UI, 16), relief="flat",
            highlightthickness=2,
            highlightbackground="#3a3a3c",
            highlightcolor="#0a84ff",
            width=20, justify="center",
        )
        self._pw.pack(side="left", ipady=8, padx=4)
        self._pw.bind("<Return>", lambda _: self._check())
        self._pw.focus_set()
        tk.Button(pw_frame, text="→",
                  bg="#0a84ff", fg="#ffffff",
                  font=(FONT_UI, 16), relief="flat",
                  padx=10, pady=6, cursor="hand2",
                  command=self._check).pack(side="left")

        self._err = tk.Label(self.frame, text="",
                              bg="#000000", fg="#ff453a",
                              font=(FONT_UI, 13))
        self._err.place(relx=0.5, rely=0.80, anchor="center")

    def _tick(self) -> None:
        if not self.frame.winfo_exists():
            return
        now = datetime.datetime.now()
        self.time_lbl.configure(text=now.strftime("%I:%M"))
        self.date_lbl.configure(text=now.strftime("%A, %B %d"))
        self.wm.root.after(1000, self._tick)

    def _check(self) -> None:
        pw = self._pw.get()
        if self.wm.users.authenticate(self.wm.current_user, pw):
            self.frame.destroy()
            self.on_unlock()
        else:
            self._err.configure(text="Incorrect password")
            self._pw.delete(0, "end")
            self.wm.root.after(2000, lambda: self._err.configure(text=""))


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 40 — WM OPEN METHODS (wire all apps to WM)
# ─────────────────────────────────────────────────────────────────────────────

def _wire_wm_openers(wm: "WM") -> None:
    """Attach open_* methods to the WM instance."""

    def _open(cls, *args, **kwargs):
        win = cls(wm, *args, **kwargs)
        return win

    wm.open_finder        = lambda: _open(FinderApp)
    wm.open_textedit      = lambda path=None: _open(TextEditApp, path)
    wm.open_terminal      = lambda: _open(TerminalApp)
    wm.open_safari        = lambda url=None: _open(SafariApp, url)
    wm.open_music         = lambda: _open(MusicApp)
    wm.open_preview       = lambda path=None: _open(PreviewApp, path)
    wm.open_calculator    = lambda: _open(CalculatorApp)
    wm.open_clock         = lambda: _open(ClockApp)
    wm.open_activity_monitor = lambda: _open(ActivityMonitorApp)
    wm.open_notes         = lambda: _open(NotesApp)
    wm.open_mail          = lambda: _open(MailApp)
    wm.open_keychain      = lambda: _open(KeychainApp)
    wm.open_numbers       = lambda path=None: _open(NumbersApp, path)
    wm.open_photos        = lambda: _open(PhotosApp)
    wm.open_disk_utility  = lambda: _open(DiskUtilityApp)
    wm.open_script_editor = lambda path=None: _open(ScriptEditorApp, path)
    wm.open_app_store     = lambda: _open(AppStoreApp)
    wm.open_preferences   = lambda panel=None: _open(SystemPreferencesApp, panel)
    wm.open_archive_utility = lambda: _open(ArchiveUtilityApp)
    wm.open_contacts      = lambda: _open(ContactsApp)

    # Also wire the dock and menubar app launchers
    _OPENERS = {
        "Finder":          wm.open_finder,
        "Notes":           wm.open_notes,
        "Safari":          wm.open_safari,
        "Mail":            wm.open_mail,
        "Music":           wm.open_music,
        "Preview":         wm.open_preview,
        "TextEdit":        wm.open_textedit,
        "Terminal":        wm.open_terminal,
        "Calculator":      wm.open_calculator,
        "Clock":           wm.open_clock,
        "Numbers":         wm.open_numbers,
        "Keychain Access": wm.open_keychain,
        "Photos":          wm.open_photos,
        "Disk Utility":    wm.open_disk_utility,
        "Script Editor":   wm.open_script_editor,
        "Activity Monitor":wm.open_activity_monitor,
        "App Store":       wm.open_app_store,
        "System Preferences": wm.open_preferences,
        "Archive Utility": wm.open_archive_utility,
        "Contacts":        wm.open_contacts,
    }
    wm._openers = _OPENERS


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 41 — GLOBAL KEYBOARD SHORTCUTS
# ─────────────────────────────────────────────────────────────────────────────

def _bind_global_shortcuts(wm: "WM") -> None:
    root = wm.root

    # ⌘Space  → Spotlight
    root.bind("<Control-space>", lambda _: wm.spotlight.toggle())
    # ⌘T      → New Terminal
    root.bind("<Control-t>",     lambda _: wm.open_terminal())
    # ⌘N      → New TextEdit
    root.bind("<Control-n>",     lambda _: wm.open_textedit())
    # ⌘L      → Lock Screen
    root.bind("<Control-l>",     lambda _: _lock(wm))
    # ⌘Q      → Quit focused window
    root.bind("<Control-q>",     lambda _: _quit_top(wm))
    # ⌘W      → Close focused window
    root.bind("<Control-w>",     lambda _: _quit_top(wm))
    # ⌘F      → Finder
    root.bind("<Control-f>",     lambda _: wm.open_finder())
    # ⌘P      → Preferences
    root.bind("<Control-p>",     lambda _: wm.open_preferences())
    # ⌘M      → Mail
    root.bind("<Control-m>",     lambda _: wm.open_mail())
    # F11     → Show Desktop
    root.bind("<F11>",           lambda _: _show_desktop(wm))
    # ⌘⇥     → Switch app (simple cycle)
    root.bind("<Control-Tab>",   lambda _: _cycle_windows(wm))


def _lock(wm: "WM") -> None:
    def on_unlock():
        pass  # Resume desktop
    LockScreen(wm, on_unlock)


def _quit_top(wm: "WM") -> None:
    wins = wm.all_wins()
    if wins:
        wins[-1].close()


def _show_desktop(wm: "WM") -> None:
    wins = wm.all_wins()
    if all(not w.frame.winfo_viewable() for w in wins):
        for w in wins:
            w.restore()
    else:
        for w in wins:
            w.minimise()


def _cycle_windows(wm: "WM") -> None:
    wins = wm.all_wins()
    if len(wins) < 2:
        return
    wins[-1].frame.lower()
    wins[0].frame.lift()
    wins[0].focus_set()


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 42 — USER MANAGER ADDITIONS
# ─────────────────────────────────────────────────────────────────────────────
# Patch UserManager to add avatar helpers if not already present

def _patch_user_manager() -> None:
    """Add helper methods to UserManager."""

    if not hasattr(UserManager, "display_name"):
        def display_name(self, username: Optional[str] = None) -> str:
            if username is None:
                username = getattr(self, "_current", "user")
            info = self._users.get(username, {})
            first = info.get("first_name", username.title())
            return first
        UserManager.display_name = display_name

    if not hasattr(UserManager, "avatar"):
        def avatar(self, username: str) -> str:
            avatars = {"user": "👤", "admin": "🛡️", "guest": "👥"}
            return avatars.get(username, "👤")
        UserManager.avatar = avatar

    if not hasattr(UserManager, "avatar_color"):
        def avatar_color(self, username: str) -> str:
            colors = {"user": "#007aff", "admin": "#5856d6", "guest": "#8e8e93"}
            return colors.get(username, "#007aff")
        UserManager.avatar_color = avatar_color

    if not hasattr(UserManager, "list_users"):
        def list_users(self) -> List[str]:
            return list(self._users.keys())
        UserManager.list_users = list_users

    if not hasattr(UserManager, "is_admin"):
        def is_admin(self, username: str) -> bool:
            return self._users.get(username, {}).get("group","staff") == "admin" \
                   or username == "admin"
        UserManager.is_admin = is_admin


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 43 — WM ADDITIONS (current_user, all_wins, lock)
# ─────────────────────────────────────────────────────────────────────────────

def _patch_wm() -> None:
    """Patch WM with helpers needed by new sections."""

    if not hasattr(WM, "all_wins"):
        def all_wins(self) -> List[BaseWin]:
            return list(self._windows)
        WM.all_wins = all_wins

    if not hasattr(WM, "lock"):
        def lock(self) -> None:
            _lock(self)
        WM.lock = lock

    if not hasattr(WM, "_draw_wallpaper"):
        def _draw_wallpaper(self) -> None:
            """Redraw the desktop wallpaper."""
            wp = self.settings.get("wallpaper", "gradient_blue")
            self._draw_desktop(wp)
        WM._draw_wallpaper = _draw_wallpaper

    if not hasattr(WM, "spotlight"):
        class _Spotlight:
            def __init__(self, wm):
                self._wm = wm
            def toggle(self):
                self._wm._toggle_spotlight()
        def _spotlight_prop(self) -> "_Spotlight":
            if not hasattr(self, "_spotlight_obj"):
                self._spotlight_obj = _Spotlight(self)
            return self._spotlight_obj
        WM.spotlight = property(_spotlight_prop)


# ─────────────────────────────────────────────────────────────────────────────
#  SECTION 44 — MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────


# authenticate / avatar_color already patched above

if not hasattr(UserManager, "current_user"):
    UserManager.current_user = "user"


# =============================================================================
#  FINAL MAIN  — boot → login → desktop
# =============================================================================

def main() -> None:
    """MacPyOS entry point."""
    # ── create subsystems ────────────────────────────────────────────────────
    vfs      = VFS()
    users    = UserManager()
    clip     = Clipboard()
    notifs   = NotificationManager()
    procs    = ProcessManager()
    settings = Settings()

    # ── create root window ───────────────────────────────────────────────────
    root = tk.Tk()
    root.title(f"MacPyOS {MACPYOS_VERSION} — {MACPYOS_CODENAME}")
    root.configure(bg="#000000")

    # Maximise to fill the screen on all platforms
    root.update_idletasks()
    try:
        root.state("zoomed")          # Windows
    except Exception:
        try:
            root.attributes("-zoomed", True)  # Linux
        except Exception:
            # Fallback: manually size to screen
            sw = root.winfo_screenwidth()
            sh = root.winfo_screenheight()
            root.geometry(f"{sw}x{sh}+0+0")

    root.resizable(True, True)
    root.update_idletasks()

    apply_theme("Monterey")

    # ── desktop launcher ─────────────────────────────────────────────────────
    def start_desktop(username: str) -> None:
        users.current_user = username
        wm = WM(root, vfs, users, procs, notifs, settings, clip)
        # Wire all app opener lambdas
        wm.open_clock            = lambda: ClockApp(wm)
        wm.open_activity_monitor = lambda: ActivityMonitorApp(wm)
        wm.open_notes            = lambda: NotesApp(wm)
        wm.open_mail             = lambda: MailApp(wm)
        wm.open_keychain         = lambda: KeychainApp(wm)
        wm.open_numbers          = lambda path=None: NumbersApp(wm, path)
        wm.open_photos           = lambda: PhotosApp(wm)
        wm.open_disk_utility     = lambda: DiskUtilityApp(wm)
        wm.open_script_editor    = lambda path=None: ScriptEditorApp(wm, path)
        wm.open_archive_utility  = lambda: ArchiveUtilityApp(wm)
        wm.open_contacts         = lambda: ContactsApp(wm)
        wm.open_app_store        = lambda: AppStoreApp(wm)
        wm.open_preferences      = lambda panel=None: SystemPreferencesApp(wm, panel)

        # Global shortcuts
        root.bind("<Control-space>", lambda _: wm.toggle_spotlight())
        root.bind("<Control-t>",     lambda _: wm.open_terminal())
        root.bind("<Control-n>",     lambda _: wm.open_notes())
        root.bind("<Control-l>",     lambda _: _do_lock(wm))
        root.bind("<Control-q>",     lambda _: _quit_top(wm))
        root.bind("<Control-Tab>",   lambda _: _cycle_windows(wm))

        root.after(800, lambda: notifs.send(
            "MacPyOS",
            f"Welcome, {users.display_name(username)}!",
            icon="\U0001f34e",
            duration=5.0,
        ))

    def _do_lock(wm):
        def on_unlock(): pass
        LockScreen(wm, on_unlock)

    def _quit_top(wm):
        wins = wm.all_wins()
        if wins:
            wins[-1].close()

    def _cycle_windows(wm):
        wins = wm.all_wins()
        if len(wins) >= 2:
            wins[-1].frame.lower()
            wins[0].frame.lift()

    # ── boot sequence ─────────────────────────────────────────────────────────
    def after_boot():
        LoginScreen(root, users, start_desktop)

    BootScreen(root, after_boot)
    root.mainloop()


if __name__ == "__main__":
    main()
