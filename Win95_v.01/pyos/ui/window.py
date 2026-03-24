"""
Tkinter desktop window for the simulator.

After sign-in, the user sees a Windows 95-inspired desktop shell built entirely
with Python's standard library:
    - My Computer: browse the virtual filesystem
    - Notepad: edit a text file inside the virtual filesystem
    - MS-DOS Prompt: run shell commands
    - Program Manager: launch and inspect simulated programs
    - System Monitor: inspect virtual memory and screen output

Example usage:
    from pyos.ui.window import run_gui
    run_gui()
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from pyos.services.auth import AuthError, AuthService
from pyos.ui.shell import Shell
from pyos.services.kernel import Kernel


DESKTOP_BG = "#008080"
TASKBAR_BG = "#c0c0c0"
CARD_BG = "#c0c0c0"
ACCENT = "#000080"
WINDOW_BG = "#c0c0c0"
TITLE_BG = "#000080"
TITLE_FG = "#ffffff"
TEXT_DARK = "#000000"
TEXT_LIGHT = "#ffffff"
PANEL_LIGHT = "#dfdfdf"
PANEL_DARK = "#808080"


class SimulatorWindow:
    """Desktop GUI wrapper around the simulator shell."""

    def __init__(self) -> None:
        self.auth = AuthService()
        self.current_user: str | None = None
        self.root = tk.Tk()
        self.root.title("Pyos_v0.1")
        self.root.geometry("1280x820")
        self.root.minsize(1100, 720)
        self.root.configure(bg=DESKTOP_BG)

        self.shell: Shell | None = None
        self.desktop_frame: tk.Frame | None = None
        self.wallpaper_canvas: tk.Canvas | None = None
        self.start_menu: tk.Frame | None = None
        self.signup_dialog: tk.Toplevel | None = None
        self.splash_dialog: tk.Toplevel | None = None
        self.shutdown_dialog: tk.Toplevel | None = None
        self.clock_label: tk.Label | None = None
        self.taskbar_label: tk.Label | None = None
        self.open_windows: dict[str, tk.Toplevel] = {}
        self.window_positions: dict[str, tuple[int, int]] = {}
        self.signin_entry_widgets: list[tk.Widget] = []
        self.signup_entry_widgets: list[tk.Widget] = []

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.signup_username_var = tk.StringVar()
        self.signup_password_var = tk.StringVar()
        self.signup_confirm_var = tk.StringVar()
        self.command_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Welcome to Pyos_v0.1.")
        self.cwd_var = tk.StringVar(value="/")
        self.user_var = tk.StringVar(value="Not signed in")

        self.file_path_var = tk.StringVar(value=".")
        self.files_status_var = tk.StringVar(value="Browse drives and folders in the virtual filesystem.")
        self.notes_path_var = tk.StringVar(value="C:/USER/NOTES.txt")
        self.process_status_var = tk.StringVar(value="Launch programs and inspect the scheduler.")
        self.memory_status_var = tk.StringVar(value="Inspect RAM, screen output, and keyboard I/O.")
        self.browser_url_var = tk.StringVar(value="pyos://home")
        self.browser_status_var = tk.StringVar(value="Welcome to The Internet.")
        self.music_status_var = tk.StringVar(value="Choose a track from the playlist.")
        self.settings_status_var = tk.StringVar(value="Tune the desktop appearance and shell behavior.")
        self.clock_status_var = tk.StringVar(value="Local time, analog clock, and a simple timer.")
        self.paint_status_var = tk.StringVar(value="Sketch on the canvas with the current color.")
        self.timer_seconds_var = tk.StringVar(value="60")
        self.accent_choice_var = tk.StringVar(value=ACCENT)
        self.wallpaper_choice_var = tk.StringVar(value="Teal")
        self.title_bar_color = ACCENT

        self.console_widgets: dict[str, object] = {}
        self.files_widgets: dict[str, object] = {}
        self.notes_widgets: dict[str, object] = {}
        self.process_widgets: dict[str, object] = {}
        self.memory_widgets: dict[str, object] = {}
        self.browser_widgets: dict[str, object] = {}
        self.music_widgets: dict[str, object] = {}
        self.paint_widgets: dict[str, object] = {}
        self.settings_widgets: dict[str, object] = {}
        self.clock_widgets: dict[str, object] = {}
        self.file_details_var = tk.StringVar(value="Select an item to view details.")
        self.control_panel_selection_var = tk.StringVar(value="Desktop")
        self.music_tracks = [
            ("Startup Theme", "Classic boot music for entering the desktop"),
            ("Drive A", "A bright loop for browsing your virtual files"),
            ("Kernel Clock", "Minimal electronic beat with system ticks"),
            ("After Hours", "Soft keys for late-night simulator sessions"),
        ]
        self.current_track_index = 0
        self.music_progress = 0
        self.music_is_playing = False
        self.paint_current_color = "#7cc7ff"
        self.paint_brush_size = 4
        self.timer_running = False
        self.timer_remaining = 0

        self._configure_style()
        self._build_auth_view()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("Auth.TFrame", background=DESKTOP_BG)
        style.configure("Title.TLabel", font=("Tahoma", 18, "bold"), background=DESKTOP_BG, foreground=TEXT_LIGHT)
        style.configure("Subtitle.TLabel", font=("Tahoma", 9), background=DESKTOP_BG, foreground="#e6ffff")
        style.configure("CardTitle.TLabel", font=("Tahoma", 10, "bold"), background=CARD_BG, foreground=TEXT_DARK)
        style.configure("Info.TLabel", font=("Tahoma", 8), background=CARD_BG, foreground=TEXT_DARK)
        style.configure("Status.TLabel", font=("Tahoma", 8, "bold"), background=DESKTOP_BG, foreground=TEXT_LIGHT)
        style.configure("Accent.TButton", font=("Tahoma", 10, "bold"))
        style.configure("TEntry", fieldbackground="#ffffff", foreground=TEXT_DARK)

    def _clear_root(self) -> None:
        for child in self.root.winfo_children():
            child.destroy()

    def _build_auth_view(self) -> None:
        self._clear_root()
        self.signin_entry_widgets = []
        self.signup_entry_widgets = []
        outer = tk.Frame(self.root, bg=DESKTOP_BG)
        outer.pack(fill="both", expand=True)
        self._build_auth_wallpaper(outer)

        dialog = tk.Frame(outer, bg=CARD_BG, bd=2, relief="raised")
        dialog.place(relx=0.5, rely=0.48, anchor="center", width=430, height=230)

        title_bar = tk.Frame(dialog, bg=self.title_bar_color, height=24)
        title_bar.pack(fill="x", side="top")
        title_bar.pack_propagate(False)
        tk.Label(
            title_bar,
            text="Enter Network Password",
            bg=self.title_bar_color,
            fg=TEXT_LIGHT,
            font=("Tahoma", 8, "bold"),
        ).pack(side="left", padx=6, pady=4)
        tk.Button(
            title_bar,
            text="X",
            bg=TASKBAR_BG,
            fg=TEXT_DARK,
            relief="raised",
            font=("Tahoma", 8, "bold"),
            width=3,
            command=self.root.destroy,
        ).pack(side="right", padx=3, pady=2)

        body = tk.Frame(dialog, bg=CARD_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)
        body.columnconfigure(1, weight=1)

        icon_box = tk.Canvas(body, width=44, height=44, bg=CARD_BG, highlightthickness=0)
        icon_box.grid(row=0, column=0, rowspan=4, sticky="nw", padx=(0, 10))
        icon_box.create_rectangle(7, 8, 36, 30, fill="#ffffff", outline="#000000")
        icon_box.create_rectangle(12, 13, 31, 25, fill="#000080", outline="")
        icon_box.create_rectangle(16, 31, 27, 36, fill="#808080", outline="#000000")

        tk.Label(
            body,
            text="Type a user name and password to log on to Pyos_v0.1.",
            bg=CARD_BG,
            fg=TEXT_DARK,
            font=("Tahoma", 8),
            justify="left",
        ).grid(row=0, column=1, columnspan=2, sticky="w")
        tk.Label(body, text="User name:", bg=CARD_BG, fg=TEXT_DARK, font=("Tahoma", 8)).grid(
            row=1, column=1, sticky="w", pady=(12, 2)
        )
        sign_in_username = tk.Entry(body, textvariable=self.username_var, width=28, relief="sunken", bd=2, font=("Tahoma", 9))
        sign_in_username.grid(row=1, column=2, sticky="ew", pady=(12, 2))
        tk.Label(body, text="Password:", bg=CARD_BG, fg=TEXT_DARK, font=("Tahoma", 8)).grid(
            row=2, column=1, sticky="w", pady=2
        )
        sign_in_password = tk.Entry(body, textvariable=self.password_var, show="*", width=28, relief="sunken", bd=2, font=("Tahoma", 9))
        sign_in_password.grid(row=2, column=2, sticky="ew", pady=2)
        self.signin_entry_widgets.extend([sign_in_username, sign_in_password])

        buttons = tk.Frame(body, bg=CARD_BG)
        buttons.grid(row=3, column=1, columnspan=2, sticky="e", pady=(16, 0))
        tk.Button(buttons, text="OK", command=self._handle_sign_in, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=10, font=("Tahoma", 8)).pack(side="left")
        tk.Button(buttons, text="Cancel", command=self.root.destroy, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=10, font=("Tahoma", 8)).pack(side="left", padx=(6, 0))
        tk.Button(buttons, text="New User...", command=self._open_signup_dialog, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=12, font=("Tahoma", 8)).pack(side="left", padx=(6, 0))

        footer = tk.Frame(dialog, bg=CARD_BG, bd=2, relief="sunken")
        footer.pack(fill="x", side="bottom", padx=12, pady=(0, 12))
        tk.Label(footer, textvariable=self.status_var, bg=CARD_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(anchor="w", padx=8, pady=4)

        sign_in_username.focus_set()

        self.root.bind("<Return>", self._auth_enter_pressed)

    def _build_auth_wallpaper(self, parent: tk.Frame) -> None:
        wallpaper = tk.Canvas(parent, bg=DESKTOP_BG, highlightthickness=0)
        wallpaper.pack(fill="both", expand=True)
        wallpaper.create_text(
            28,
            28,
            anchor="nw",
            text="Pyos_v0.1",
            fill=TEXT_LIGHT,
            font=("Tahoma", 18, "bold"),
        )
        wallpaper.create_text(
            30,
            56,
            anchor="nw",
            text="Windows 95 style shell",
            fill=TEXT_LIGHT,
            font=("Tahoma", 8),
        )

    def _show_splash_dialog(self) -> None:
        if self.splash_dialog is not None and self.splash_dialog.winfo_exists():
            self.splash_dialog.destroy()
        splash = tk.Toplevel(self.root)
        splash.overrideredirect(True)
        splash.geometry("420x180+430+250")
        splash.configure(bg=CARD_BG, bd=2, relief="raised")
        splash.transient(self.root)
        self.splash_dialog = splash

        body = tk.Frame(splash, bg=CARD_BG, bd=2, relief="sunken")
        body.pack(fill="both", expand=True, padx=3, pady=3)
        tk.Label(body, text="Starting Pyos_v0.1...", bg=CARD_BG, fg=TEXT_DARK, font=("Tahoma", 14, "bold")).pack(
            anchor="w", padx=18, pady=(18, 4)
        )
        tk.Label(body, text="Please wait while the desktop is prepared.", bg=CARD_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(
            anchor="w", padx=18
        )
        progress_frame = tk.Frame(body, bg=TASKBAR_BG, bd=2, relief="sunken", height=22)
        progress_frame.pack(fill="x", padx=18, pady=(24, 8))
        progress_frame.pack_propagate(False)
        progress = tk.Frame(progress_frame, bg=self.title_bar_color, width=0)
        progress.place(x=0, y=0, relheight=1.0, width=0)
        tk.Label(body, text="Windows 95 style environment", bg=CARD_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(
            anchor="w", padx=18
        )

        self._animate_splash(progress, 0)

    def _animate_splash(self, bar: tk.Frame, step: int) -> None:
        if self.splash_dialog is None or not self.splash_dialog.winfo_exists():
            return
        width = 300
        bar.place_configure(width=int(width * (step / 10)))
        if step >= 10:
            self.splash_dialog.destroy()
            self.splash_dialog = None
            self._open_desktop()
            return
        self.root.after(70, lambda: self._animate_splash(bar, step + 1))

    def _open_signup_dialog(self) -> None:
        if self.signup_dialog is not None and self.signup_dialog.winfo_exists():
            self.signup_dialog.lift()
            self.signup_dialog.focus_force()
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("New User")
        dialog.geometry("360x220+470+260")
        dialog.resizable(False, False)
        dialog.configure(bg=CARD_BG, bd=2, relief="raised")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", self._close_signup_dialog)
        self.signup_dialog = dialog
        self.signup_entry_widgets = []

        title_bar = tk.Frame(dialog, bg=self.title_bar_color, height=24)
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)
        tk.Label(title_bar, text="Create New User", bg=self.title_bar_color, fg=TEXT_LIGHT, font=("Tahoma", 8, "bold")).pack(
            side="left", padx=6, pady=4
        )

        body = tk.Frame(dialog, bg=CARD_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)
        body.columnconfigure(1, weight=1)

        fields = [
            ("User name:", self.signup_username_var),
            ("Password:", self.signup_password_var),
            ("Confirm:", self.signup_confirm_var),
        ]
        created_entries: list[tk.Entry] = []
        for row, (label, variable) in enumerate(fields):
            tk.Label(body, text=label, bg=CARD_BG, fg=TEXT_DARK, font=("Tahoma", 8)).grid(row=row, column=0, sticky="w", pady=4)
            entry = tk.Entry(
                body,
                textvariable=variable,
                show="*" if row > 0 else "",
                width=24,
                relief="sunken",
                bd=2,
                font=("Tahoma", 9),
            )
            entry.grid(row=row, column=1, sticky="ew", pady=4)
            created_entries.append(entry)

        button_row = tk.Frame(body, bg=CARD_BG)
        button_row.grid(row=3, column=0, columnspan=2, sticky="e", pady=(14, 0))
        tk.Button(button_row, text="Create", command=self._handle_sign_up, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=10, font=("Tahoma", 8)).pack(side="left")
        tk.Button(button_row, text="Cancel", command=self._close_signup_dialog, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=10, font=("Tahoma", 8)).pack(side="left", padx=(6, 0))

        self.signup_entry_widgets.extend(created_entries)
        created_entries[0].focus_set()

    def _close_signup_dialog(self) -> None:
        if self.signup_dialog is not None and self.signup_dialog.winfo_exists():
            try:
                self.signup_dialog.grab_release()
            except tk.TclError:
                pass
            self.signup_dialog.destroy()
        self.signup_dialog = None

    def _auth_enter_pressed(self, event: tk.Event) -> None:
        widget = self.root.focus_get()
        if widget is None:
            return
        if widget in self.signup_entry_widgets:
            self._handle_sign_up()
            return
        if widget in self.signin_entry_widgets:
            self._handle_sign_in()

    def _handle_sign_up(self) -> None:
        username = self.signup_username_var.get()
        password = self.signup_password_var.get()
        confirm = self.signup_confirm_var.get()
        if password != confirm:
            self.status_var.set("Passwords do not match.")
            return
        try:
            account = self.auth.sign_up(username, password)
        except AuthError as exc:
            self.status_var.set(str(exc))
            return

        self.status_var.set(f"User {account['username']} created. You can log on now.")
        self.username_var.set(account["username"])
        self.password_var.set("")
        self.signup_username_var.set("")
        self.signup_password_var.set("")
        self.signup_confirm_var.set("")
        self._close_signup_dialog()
        if self.signin_entry_widgets:
            self.signin_entry_widgets[0].focus_set()

    def _handle_sign_in(self) -> None:
        try:
            account = self.auth.sign_in(self.username_var.get(), self.password_var.get())
        except AuthError as exc:
            self.status_var.set(str(exc))
            return
        self.current_user = account["username"]
        self._show_splash_dialog()

    def _open_desktop(self) -> None:
        self.root.unbind("<Return>")
        self._clear_root()
        self.open_windows = {}
        self.shell = Shell(Kernel())
        self.user_var.set(self.current_user or "USER")
        self.cwd_var.set(self.shell.kernel.pwd())
        self.file_path_var.set(self.shell.kernel.pwd())

        desktop = tk.Frame(self.root, bg=DESKTOP_BG)
        desktop.pack(fill="both", expand=True)
        self.desktop_frame = desktop

        wallpaper = tk.Canvas(desktop, bg="#57a8ff", highlightthickness=0)
        wallpaper.pack(fill="both", expand=True)
        wallpaper.bind("<Configure>", self._paint_wallpaper)
        self.wallpaper_canvas = wallpaper

        self._build_taskbar(desktop)
        desktop_icons = [
            ("My Computer", self._open_files_app, "computer"),
            ("My Documents", self._open_notes_app, "docs"),
            ("Network Neighborhood", self._open_browser_app, "network"),
            ("MS-DOS Prompt", self._open_terminal_app, "terminal"),
            ("Paint", self._open_paint_app, "paint"),
            ("Recycle Bin", self._open_memory_app, "bin"),
        ]
        positions = [(34, 34), (34, 118), (34, 202), (34, 286), (34, 370), (34, 454)]
        for (label, action, kind), (x, y) in zip(desktop_icons, positions):
            icon = self._create_desktop_icon(wallpaper, label, action, kind)
            wallpaper.create_window(x, y, anchor="nw", window=icon)
        self._seed_default_apps()
        self._refresh_all_apps()
        self._tick_clock()

    def _create_desktop_icon(self, parent: tk.Canvas, label: str, action, kind: str) -> tk.Frame:
        frame = tk.Frame(parent, bg=DESKTOP_BG)
        icon = tk.Canvas(frame, width=40, height=34, bg=DESKTOP_BG, highlightthickness=0)
        icon.pack()
        self._draw_desktop_icon(icon, kind)
        button = tk.Button(
            frame,
            text=label,
            command=action,
            bg=DESKTOP_BG,
            fg=TEXT_LIGHT,
            activebackground=DESKTOP_BG,
            activeforeground=TEXT_LIGHT,
            relief="flat",
            wraplength=78,
            justify="center",
            font=("Tahoma", 8),
            padx=1,
            pady=1,
        )
        button.pack()
        return frame

    def _draw_desktop_icon(self, canvas: tk.Canvas, kind: str) -> None:
        if kind == "computer":
            canvas.create_rectangle(8, 6, 32, 21, fill="#dcdcdc", outline="#000000")
            canvas.create_rectangle(11, 9, 29, 18, fill="#000080", outline="")
            canvas.create_rectangle(15, 23, 25, 28, fill="#808080", outline="#000000")
            return
        if kind == "docs":
            canvas.create_rectangle(11, 5, 30, 29, fill="#ffffff", outline="#000000")
            canvas.create_polygon(24, 5, 30, 5, 30, 11, fill="#dfdfdf", outline="#000000")
            canvas.create_line(14, 14, 27, 14, fill="#000080")
            canvas.create_line(14, 18, 27, 18, fill="#000080")
            canvas.create_line(14, 22, 24, 22, fill="#000080")
            return
        if kind == "network":
            canvas.create_rectangle(6, 16, 16, 25, fill="#dcdcdc", outline="#000000")
            canvas.create_rectangle(24, 16, 34, 25, fill="#dcdcdc", outline="#000000")
            canvas.create_rectangle(15, 5, 25, 14, fill="#dcdcdc", outline="#000000")
            canvas.create_line(20, 14, 11, 16, fill="#000000")
            canvas.create_line(20, 14, 29, 16, fill="#000000")
            return
        if kind == "terminal":
            canvas.create_rectangle(7, 6, 33, 27, fill="#000000", outline="#ffffff")
            canvas.create_text(20, 16, text="C:>", fill="#ffffff", font=("Courier New", 7, "bold"))
            return
        if kind == "paint":
            canvas.create_rectangle(8, 7, 31, 27, fill="#ffffff", outline="#000000")
            canvas.create_line(10, 24, 18, 10, fill="#ff0000", width=2)
            canvas.create_line(18, 10, 27, 22, fill="#0000ff", width=2)
            return
        canvas.create_rectangle(10, 8, 29, 27, fill="#ffffff", outline="#000000")
        canvas.create_rectangle(7, 24, 32, 29, fill="#808080", outline="#000000")
        canvas.create_line(13, 11, 26, 24, fill="#000000")
        canvas.create_line(13, 24, 26, 11, fill="#000000")

    def _paint_wallpaper(self, event: tk.Event) -> None:
        canvas = event.widget
        if not isinstance(canvas, tk.Canvas):
            return
        self._draw_current_wallpaper(canvas)

    def _draw_current_wallpaper(self, canvas: tk.Canvas) -> None:
        if not canvas.winfo_exists():
            return

        width = max(canvas.winfo_width(), 1)
        height = max(canvas.winfo_height(), 1)
        horizon = int(height * 0.58)

        canvas.delete("wallpaper")
        theme = self.wallpaper_choice_var.get()
        if theme == "Clouds":
            self._draw_clouds_wallpaper(canvas, width, height, horizon)
        elif theme == "Teal":
            self._draw_teal_wallpaper(canvas, width, height)
        else:
            self._draw_bliss_wallpaper(canvas, width, height, horizon)

        canvas.create_text(
            width - 30,
            height - 28,
            text="Pyos_v0.1",
            anchor="se",
            fill="#e6f3ff",
            font=("Tahoma", 16, "bold"),
            tags="wallpaper",
        )
        canvas.tag_lower("wallpaper")

    def _draw_bliss_wallpaper(self, canvas: tk.Canvas, width: int, height: int, horizon: int) -> None:
        for band in range(14):
            y0 = int(horizon * band / 14)
            y1 = int(horizon * (band + 1) / 14)
            blue = 185 + band * 4
            green = 145 + band * 5
            color = f"#5a{green:02x}{blue:02x}"
            canvas.create_rectangle(0, y0, width, y1, fill=color, outline="", tags="wallpaper")

        sun_x = width * 0.82
        sun_y = height * 0.18
        for radius, color in [(92, "#fff2b8"), (68, "#ffe87c"), (46, "#ffe14a")]:
            canvas.create_oval(
                sun_x - radius,
                sun_y - radius,
                sun_x + radius,
                sun_y + radius,
                fill=color,
                outline="",
                tags="wallpaper",
            )

        for start_x, start_y, span_x, span_y in [
            (0.12, 0.12, 0.12, 0.04),
            (0.34, 0.18, 0.15, 0.05),
            (0.62, 0.13, 0.13, 0.04),
            (0.78, 0.24, 0.12, 0.04),
        ]:
            self._draw_cloud_cluster(canvas, width * start_x, height * start_y, width * span_x, height * span_y)

        back_hill = [
            (0, height),
            (0, horizon + 70),
            (width * 0.18, horizon + 10),
            (width * 0.38, horizon + 54),
            (width * 0.58, horizon - 8),
            (width * 0.76, horizon + 48),
            (width, horizon + 8),
            (width, height),
        ]
        canvas.create_polygon(back_hill, fill="#61aa48", outline="", smooth=True, tags="wallpaper")

        front_hill = [
            (0, height),
            (0, horizon + 38),
            (width * 0.12, horizon - 24),
            (width * 0.28, horizon + 8),
            (width * 0.47, horizon - 44),
            (width * 0.69, horizon + 10),
            (width * 0.86, horizon - 18),
            (width, horizon + 24),
            (width, height),
        ]
        canvas.create_polygon(front_hill, fill="#3d8d35", outline="", smooth=True, tags="wallpaper")

        path_points = [
            (width * 0.56, horizon + 60),
            (width * 0.61, horizon + 74),
            (width * 0.66, horizon + 110),
            (width * 0.7, height),
            (width * 0.53, height),
            (width * 0.49, horizon + 96),
            (width * 0.5, horizon + 70),
        ]
        canvas.create_polygon(path_points, fill="#d8cb8d", outline="", smooth=True, tags="wallpaper")

    def _draw_clouds_wallpaper(self, canvas: tk.Canvas, width: int, height: int, horizon: int) -> None:
        canvas.create_rectangle(0, 0, width, height, fill="#78b7ff", outline="", tags="wallpaper")
        for stripe in range(12):
            y = int(height * stripe / 12)
            shade = 180 + stripe * 4
            canvas.create_rectangle(
                0,
                y,
                width,
                y + int(height / 12) + 2,
                fill=f"#{shade:02x}{shade:02x}ff",
                outline="",
                tags="wallpaper",
            )
        for index in range(8):
            x = width * (0.08 + index * 0.12)
            y = height * (0.1 + (index % 3) * 0.12)
            self._draw_cloud_cluster(canvas, x, y, width * 0.14, height * 0.05)
        canvas.create_rectangle(0, horizon, width, height, fill="#6aa84f", outline="", tags="wallpaper")

    def _draw_teal_wallpaper(self, canvas: tk.Canvas, width: int, height: int) -> None:
        canvas.create_rectangle(0, 0, width, height, fill="#008080", outline="", tags="wallpaper")
        step = 32
        for x in range(0, width + step, step):
            canvas.create_line(x, 0, x, height, fill="#0d9a9a", tags="wallpaper")
        for y in range(0, height + step, step):
            canvas.create_line(0, y, width, y, fill="#0d9a9a", tags="wallpaper")
        for x in range(0, width + step, step * 2):
            for y in range(0, height + step, step * 2):
                canvas.create_rectangle(x, y, x + step, y + step, outline="#38b6b6", tags="wallpaper")

    def _draw_cloud_cluster(self, canvas: tk.Canvas, x: float, y: float, width: float, height: float) -> None:
        for dx, dy, scale in [(-0.24, 0.08, 0.72), (0.0, 0.0, 1.0), (0.25, 0.06, 0.78)]:
            half_w = width * scale / 2
            half_h = height * scale / 2
            cx = x + width * dx
            cy = y + height * dy
            canvas.create_oval(
                cx - half_w,
                cy - half_h,
                cx + half_w,
                cy + half_h,
                fill="#f8fdff",
                outline="",
                tags="wallpaper",
            )

    def _repaint_wallpaper(self) -> None:
        if self.wallpaper_canvas is None or not self.wallpaper_canvas.winfo_exists():
            return
        self._draw_current_wallpaper(self.wallpaper_canvas)

    def _build_menu_bar(self, parent: tk.Frame) -> None:
        menu = tk.Frame(parent, bg=TASKBAR_BG, height=28, bd=2, relief="raised")
        menu.pack(fill="x", side="top")
        menu.pack_propagate(False)

        left = tk.Frame(menu, bg=TASKBAR_BG)
        left.pack(side="left", padx=10)
        for label in ["File", "Edit", "View", "Tools", "Help"]:
            tk.Label(
                left,
                text=label,
                bg=TASKBAR_BG,
                fg=TEXT_DARK,
                font=("Tahoma", 9),
            ).pack(side="left", padx=8)

        right = tk.Frame(menu, bg=TASKBAR_BG)
        right.pack(side="right", padx=10)
        tk.Label(
            right,
            text="Pyos_v0.1",
            bg=TASKBAR_BG,
            fg=TEXT_DARK,
            font=("Tahoma", 9, "bold"),
        ).pack(side="left", padx=(0, 14))
        self.clock_label = tk.Label(
            right,
            text="",
            bg=TASKBAR_BG,
            fg=TEXT_DARK,
            font=("Tahoma", 9, "bold"),
        )
        self.clock_label.pack(side="left")

    def _build_taskbar(self, parent: tk.Frame) -> None:
        taskbar = tk.Frame(parent, bg=TASKBAR_BG, height=42, bd=2, relief="raised")
        taskbar.pack(fill="x", side="bottom")
        taskbar.pack_propagate(False)

        tk.Button(
            taskbar,
            text="Start",
            command=self._toggle_start_menu,
            bg=TASKBAR_BG,
            fg=TEXT_DARK,
            relief="raised",
            font=("Tahoma", 10, "bold"),
            padx=16,
        ).pack(side="left", padx=(6, 8), pady=5)

        dock = tk.Frame(taskbar, bg=TASKBAR_BG)
        dock.pack(side="left", fill="x", expand=True, pady=5)

        for label, action in [
            ("My Computer", self._open_files_app),
            ("Notepad", self._open_notes_app),
            ("MS-DOS Prompt", self._open_terminal_app),
            ("Online", self._open_browser_app),
            ("Media", self._open_music_app),
            ("Tasks", self._open_process_app),
            ("System", self._open_memory_app),
            ("Paint", self._open_paint_app),
            ("Clock", self._open_clock_app),
            ("Control Panel", self._open_settings_app),
            ("Calc", self._open_calculator_app),
        ]:
            tk.Button(
                dock,
                text=label,
                command=action,
                bg=TASKBAR_BG,
                fg=TEXT_DARK,
                relief="raised",
                activebackground=PANEL_LIGHT,
                font=("Tahoma", 8),
                padx=10,
                pady=4,
            ).pack(side="left", padx=6)

        clock_frame = tk.Frame(taskbar, bg=TASKBAR_BG, bd=2, relief="sunken")
        clock_frame.pack(side="right", padx=6, pady=5)
        tk.Label(clock_frame, textvariable=self.user_var, bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(
            side="left", padx=(8, 6)
        )
        self.taskbar_label = tk.Label(clock_frame, text="", bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8, "bold"))
        self.taskbar_label.pack(side="left", padx=(0, 8))

    def _toggle_start_menu(self) -> None:
        if self.start_menu is not None and self.start_menu.winfo_exists():
            self.start_menu.destroy()
            self.start_menu = None
            return

        menu = tk.Frame(self.root, bg=TASKBAR_BG, bd=2, relief="raised")
        menu.place(x=3, rely=1.0, y=-42, width=232, height=286, anchor="sw")
        self.start_menu = menu

        banner = tk.Frame(menu, bg=self.title_bar_color, width=34)
        banner.pack(side="left", fill="y")
        tk.Label(
            banner,
            text="Pyos_v0.1",
            bg=self.title_bar_color,
            fg=TEXT_LIGHT,
            font=("Tahoma", 12, "bold"),
        ).place(relx=0.5, rely=0.5, anchor="center")

        grid = tk.Frame(menu, bg=TASKBAR_BG)
        grid.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        apps = [
            ("Programs", self._open_process_app),
            ("Documents", self._open_notes_app),
            ("Settings", self._open_settings_app),
            ("Find", self._open_files_app),
            ("Help", self._open_browser_app),
            ("Run...", self._open_terminal_app),
            ("Shut Down...", self._open_shutdown_dialog),
        ]
        for index, (label, action) in enumerate(apps):
            row = index
            tk.Button(
                grid,
                text=label,
                command=lambda fn=action: self._run_start_action(fn),
                bg=TASKBAR_BG,
                fg=TEXT_DARK,
                relief="flat",
                activebackground=self.title_bar_color,
                activeforeground=TEXT_LIGHT,
                anchor="w",
                font=("Tahoma", 8),
                width=22,
                padx=10,
                pady=5,
            ).grid(row=row, column=0, sticky="ew")
        grid.columnconfigure(0, weight=1)

    def _run_start_action(self, action) -> None:
        if self.start_menu is not None and self.start_menu.winfo_exists():
            self.start_menu.destroy()
            self.start_menu = None
        action()

    def _seed_default_apps(self) -> None:
        self._open_files_app()
        self._open_terminal_app()
        self._open_notes_app()

    def _create_window(self, key: str, title: str, size: str, position: tuple[int, int]) -> tk.Toplevel:
        existing = self.open_windows.get(key)
        if existing is not None and existing.winfo_exists():
            existing.deiconify()
            existing.lift()
            existing.focus_force()
            return existing

        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry(f"{size}+{position[0]}+{position[1]}")
        window.overrideredirect(True)
        window.configure(bg=WINDOW_BG, bd=2, relief="raised")
        window.transient(self.root)
        window.protocol("WM_DELETE_WINDOW", lambda k=key: self._close_window(k))
        window._pyos_key = key
        self.window_positions[key] = position
        self.open_windows[key] = window
        return window

    def _close_window(self, key: str) -> None:
        window = self.open_windows.pop(key, None)
        self.window_positions.pop(key, None)
        if window is not None and window.winfo_exists():
            window.destroy()

    def _window_shell(self, window: tk.Toplevel, title: str, subtitle: str) -> tk.Frame:
        frame = tk.Frame(window, bg=WINDOW_BG)
        frame.pack(fill="both", expand=True)

        header = tk.Frame(frame, bg=self.title_bar_color, height=26, bd=2, relief="raised")
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text=title, bg=self.title_bar_color, fg=TITLE_FG, font=("Tahoma", 8, "bold")).pack(
            side="left", padx=6, pady=4
        )
        header.bind("<Button-1>", lambda event, win=window: self._begin_window_drag(event, win))
        header.bind("<B1-Motion>", lambda event, win=window: self._drag_window(event, win))
        tk.Button(
            header,
            text="X",
            command=lambda win=window: self._close_window(getattr(win, "_pyos_key", "")),
            bg=TASKBAR_BG,
            fg=TEXT_DARK,
            relief="raised",
            font=("Tahoma", 8, "bold"),
            width=3,
        ).pack(side="right", padx=3, pady=2)

        body = tk.Frame(frame, bg=WINDOW_BG, bd=2, relief="sunken")
        body.pack(fill="both", expand=True, padx=3, pady=3)
        content = tk.Frame(body, bg=WINDOW_BG)
        content.pack(fill="both", expand=True, padx=4, pady=4)
        return content

    def _begin_window_drag(self, event: tk.Event, window: tk.Toplevel) -> None:
        window._drag_origin = (event.x_root, event.y_root, window.winfo_x(), window.winfo_y())

    def _drag_window(self, event: tk.Event, window: tk.Toplevel) -> None:
        origin = getattr(window, "_drag_origin", None)
        if origin is None:
            return
        start_x, start_y, win_x, win_y = origin
        dx = event.x_root - start_x
        dy = event.y_root - start_y
        window.geometry(f"+{win_x + dx}+{win_y + dy}")

    def _open_terminal_app(self) -> None:
        window = self._create_window("terminal", "Pyos_v0.1 MS-DOS Prompt", "640x420", (300, 120))
        body = self._window_shell(window, "MS-DOS Prompt", "Run shell commands inside the simulator.")
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)

        quick = tk.Frame(body, bg=TASKBAR_BG, bd=2, relief="raised")
        quick.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        for label in ["File", "Edit", "View", "Help"]:
            tk.Label(quick, text=label, bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(side="left", padx=6, pady=2)

        console = ScrolledText(
            body,
            wrap="word",
            font=("Courier New", 10),
            bg="#000000",
            fg="#c0c0c0",
            insertbackground="#c0c0c0",
            bd=0,
        )
        console.grid(row=1, column=0, sticky="nsew")

        bottom = tk.Frame(body, bg=WINDOW_BG)
        bottom.grid(row=2, column=0, sticky="ew", pady=(2, 0))
        bottom.columnconfigure(1, weight=1)
        tk.Label(bottom, text="C:\\>", bg=WINDOW_BG, fg=TEXT_DARK, font=("Courier New", 9)).grid(row=0, column=0, sticky="w")
        entry = tk.Entry(bottom, textvariable=self.command_var, relief="sunken", bd=2, font=("Courier New", 9))
        entry.grid(row=0, column=1, sticky="ew", padx=(4, 4))
        tk.Button(bottom, text="OK", command=self._run_from_terminal_entry, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=8, font=("Tahoma", 8)).grid(
            row=0, column=2
        )

        self.console_widgets = {"window": window, "console": console, "entry": entry}
        self._append_console(self.shell.kernel.boot_report() if self.shell else "MS-DOS Prompt ready.")
        entry.focus_set()

    def _open_files_app(self) -> None:
        window = self._create_window("files", "Pyos_v0.1 My Computer", "680x430", (70, 110))
        body = self._window_shell(window, "My Computer", "Browse drive C and manage your files.")
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=2)

        toolbar = tk.Frame(body, bg=TASKBAR_BG, bd=2, relief="raised")
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 2))
        toolbar.columnconfigure(1, weight=1)
        tk.Label(toolbar, text="Address", bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8)).grid(
            row=0, column=0, sticky="w", padx=(4, 4), pady=2
        )
        tk.Entry(toolbar, textvariable=self.file_path_var, relief="sunken", bd=2, font=("Tahoma", 8)).grid(row=0, column=1, sticky="ew", pady=2)
        tk.Button(toolbar, text="Open", command=self._refresh_files_app, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", font=("Tahoma", 8), width=7).grid(row=0, column=2, padx=(4, 0), pady=2)
        tk.Button(toolbar, text="Up", command=self._files_go_up, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", font=("Tahoma", 8), width=5).grid(row=0, column=3, padx=(4, 0), pady=2)

        sidebar = tk.Frame(body, bg=WINDOW_BG, bd=2, relief="sunken")
        sidebar.grid(row=1, column=0, sticky="nsew", padx=(0, 3))
        tk.Label(sidebar, text="Folders", bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8, "bold"), bd=2, relief="raised").pack(fill="x")
        places = tk.Listbox(sidebar, font=("Tahoma", 8), activestyle="none", bg="#ffffff", fg=TEXT_DARK)
        places.pack(fill="both", expand=True, padx=2, pady=2)
        for item in ["C:/", "C:/USER", "C:/USER/DESKTOP", "C:/USER/DOCUMENTS", "C:/WINDOWS", "C:/PROGRAM FILES"]:
            places.insert("end", item)
        places.bind("<<ListboxSelect>>", lambda _event: self._files_select_place(places))

        right_pane = tk.Frame(body, bg=WINDOW_BG)
        right_pane.grid(row=1, column=1, sticky="nsew", padx=(3, 0))
        right_pane.rowconfigure(1, weight=1)
        right_pane.columnconfigure(0, weight=1)

        tk.Label(right_pane, text="Contents", bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8, "bold"), bd=2, relief="raised").grid(row=0, column=0, sticky="ew")
        listing = tk.Listbox(
            right_pane,
            font=("Tahoma", 8),
            activestyle="none",
            bg="#ffffff",
            fg=TEXT_DARK,
            selectbackground="#000080",
            selectforeground="#ffffff",
        )
        listing.grid(row=1, column=0, sticky="nsew")
        listing.bind("<Double-1>", self._files_open_selected)
        listing.bind("<<ListboxSelect>>", self._files_preview_selected)

        details = tk.Frame(right_pane, bg=TASKBAR_BG, bd=2, relief="sunken")
        details.grid(row=2, column=0, sticky="ew", pady=(2, 0))
        tk.Label(details, textvariable=self.file_details_var, anchor="w", justify="left", bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(fill="x", padx=4, pady=3)

        status = tk.Label(body, textvariable=self.files_status_var, anchor="w", bg=TASKBAR_BG, fg=TEXT_DARK, bd=2, relief="sunken", font=("Tahoma", 8))
        status.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(2, 0))

        self.files_widgets = {"window": window, "list": listing, "places": places, "status": status}
        self._refresh_files_app()

    def _open_notes_app(self) -> None:
        window = self._create_window("notes", "Pyos_v0.1 Notepad", "560x420", (450, 170))
        body = self._window_shell(window, "Notepad", "Edit text files stored under C:/USER.")
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)

        top = tk.Frame(body, bg=TASKBAR_BG, bd=2, relief="raised")
        top.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        for label in ["File", "Edit", "Search", "Help"]:
            tk.Label(top, text=label, bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(side="left", padx=6, pady=2)

        editor = ScrolledText(body, wrap="word", font=("Courier New", 10), bg="#ffffff", fg="#000000", insertbackground="#000000", bd=0)
        editor.grid(row=1, column=0, sticky="nsew")

        status = tk.Frame(body, bg=TASKBAR_BG, bd=2, relief="sunken")
        status.grid(row=2, column=0, sticky="ew", pady=(2, 0))
        tk.Label(status, textvariable=self.notes_path_var, anchor="w", bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(side="left", fill="x", expand=True, padx=4, pady=2)
        tk.Button(status, text="Open", command=self._load_notes, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=8, font=("Tahoma", 8)).pack(side="right", padx=(2, 4), pady=2)
        tk.Button(status, text="Save", command=self._save_notes, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=8, font=("Tahoma", 8)).pack(side="right", pady=2)

        self.notes_widgets = {"window": window, "editor": editor, "status": status}
        self._load_notes()

    def _open_process_app(self) -> None:
        window = self._create_window("process", "Pyos_v0.1 Program Manager", "820x580", (180, 220))
        body = self._window_shell(window, "Program Manager", "Launch demo apps and watch the scheduler.")
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        controls = tk.Frame(body, bg=WINDOW_BG)
        controls.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        for index, program in enumerate(["clock", "editor", "calc", "backup", "typewriter"]):
            tk.Button(
                controls,
                text=f"Run {program}",
                command=lambda name=program: self._launch_program(name),
                bg="#22304a",
                fg="#eef7ff",
                relief="flat",
                padx=10,
            ).grid(row=0, column=index, padx=(0, 8))
        ttk.Button(controls, text="Tick", command=lambda: self._tick_scheduler(1)).grid(row=0, column=6, padx=(8, 0))
        ttk.Button(controls, text="Tick x5", command=lambda: self._tick_scheduler(5)).grid(row=0, column=7, padx=(8, 0))

        process_text = ScrolledText(body, wrap="word", font=("Consolas", 10), bg="#0d1420", fg="#f0f6ff")
        process_text.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        right = tk.Frame(body, bg=WINDOW_BG)
        right.grid(row=1, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        actions = tk.Frame(right, bg=WINDOW_BG)
        actions.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ttk.Button(actions, text="Inspect Latest PID", command=self._inspect_latest_process).pack(side="left")
        ttk.Button(actions, text="Kill Latest PID", command=self._kill_latest_process).pack(side="left", padx=(8, 0))

        info = ScrolledText(right, wrap="word", font=("Consolas", 10), bg="#0d1420", fg="#f0f6ff")
        info.grid(row=1, column=0, sticky="nsew")

        status = tk.Label(body, textvariable=self.process_status_var, anchor="w", bg=WINDOW_BG, fg="#9fc7ff")
        status.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.process_widgets = {"window": window, "table": process_text, "info": info}
        self._refresh_process_app()

    def _open_memory_app(self) -> None:
        window = self._create_window("memory", "Pyos_v0.1 Console", "780x560", (500, 100))
        body = self._window_shell(window, "Console", "Inspect RAM, screen output, and keyboard I/O.")
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)

        top = tk.Frame(body, bg=WINDOW_BG)
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Button(top, text="Refresh", command=self._refresh_memory_app).pack(side="left")
        ttk.Button(top, text="Feed Keyboard", command=self._feed_keyboard_demo).pack(side="left", padx=(8, 0))
        ttk.Button(top, text="Read Keyboard", command=self._read_keyboard_demo).pack(side="left", padx=(8, 0))

        mem_text = ScrolledText(body, wrap="word", font=("Consolas", 10), bg="#0d1420", fg="#f0f6ff")
        mem_text.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        screen_text = ScrolledText(body, wrap="word", font=("Consolas", 10), bg="#0d1420", fg="#f0f6ff")
        screen_text.grid(row=1, column=1, sticky="nsew")

        status = tk.Label(body, textvariable=self.memory_status_var, anchor="w", bg=WINDOW_BG, fg="#9fc7ff")
        status.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.memory_widgets = {"window": window, "mem": mem_text, "screen": screen_text}
        self._refresh_memory_app()

    def _open_calculator_app(self) -> None:
        window = self._create_window("calculator", "Pyos_v0.1 Calculator", "262x308", (880, 180))
        body = self._window_shell(window, "Calculator", "A simple desktop app for quick arithmetic.")
        body.columnconfigure(0, weight=1)
        display_var = tk.StringVar(value="0")

        menu = tk.Frame(body, bg=TASKBAR_BG, bd=2, relief="raised")
        menu.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 2))
        for label in ["Edit", "View", "Help"]:
            tk.Label(menu, text=label, bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(side="left", padx=6, pady=2)

        entry = tk.Entry(body, textvariable=display_var, justify="right", font=("Tahoma", 16), relief="sunken", bd=2, bg="#ffffff")
        entry.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(0, 4), padx=2, ipady=4)

        buttons = [
            "7", "8", "9", "/",
            "4", "5", "6", "*",
            "1", "2", "3", "-",
            "0", ".", "=", "+",
        ]
        for index, token in enumerate(buttons):
            row = 2 + index // 4
            col = index % 4
            tk.Button(
                body,
                text=token,
                command=lambda value=token: self._calculator_press(display_var, value),
                bg=TASKBAR_BG,
                fg=TEXT_DARK,
                relief="raised",
                font=("Tahoma", 8),
                pady=5,
            ).grid(row=row, column=col, sticky="nsew", padx=2, pady=2)
            body.rowconfigure(row, weight=1)
            body.columnconfigure(col, weight=1)

        tk.Button(
            body,
            text="Clear",
            command=lambda: display_var.set("0"),
            bg=TASKBAR_BG,
            fg=TEXT_DARK,
            relief="raised",
            font=("Tahoma", 8),
        ).grid(row=6, column=0, columnspan=4, sticky="ew", padx=2, pady=(2, 0))

    def _calculator_press(self, display_var: tk.StringVar, token: str) -> None:
        current = display_var.get()
        if token == "=":
            try:
                value = str(eval(current, {"__builtins__": {}}, {}))
            except Exception:
                value = "Error"
            display_var.set(value)
            return
        if current in {"0", "Error"} and token not in {".", "+", "-", "*", "/"}:
            display_var.set(token)
        else:
            display_var.set(current + token)

    def _run_from_terminal_entry(self) -> None:
        command = self.command_var.get().strip()
        if not command:
            return
        self.command_var.set("")
        self._run_terminal_command(command)

    def _run_terminal_command(self, command: str) -> None:
        if self.shell is None:
            return
        if command == "calc":
            self._open_calculator_app()
            self._append_console("Opened Calculator app.")
            return
        self._append_console(f"{self.shell.prompt()}{command}")
        output = self.shell.onecmd(command)
        if output:
            self._append_console(output)
        elif command.startswith("cd "):
            self._append_console("Directory changed.")
        elif command == "clear":
            self._append_console("Screen buffer cleared.")
        self.cwd_var.set(self.shell.kernel.pwd())
        self.file_path_var.set(self.shell.kernel.pwd())
        self._refresh_all_apps()

    def _append_console(self, text: str) -> None:
        console = self.console_widgets.get("console")
        if not isinstance(console, ScrolledText):
            return
        console.configure(state="normal")
        console.insert("end", text + "\n\n")
        console.see("end")
        console.configure(state="disabled")

    def _set_text(self, widget: object, text: str) -> None:
        if not isinstance(widget, ScrolledText):
            return
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _refresh_all_apps(self) -> None:
        self._refresh_files_app()
        self._refresh_process_app()
        self._refresh_memory_app()

    def _refresh_files_app(self) -> None:
        if self.shell is None:
            return
        listing = self.files_widgets.get("list")
        if not isinstance(listing, tk.Listbox):
            return
        path = self.file_path_var.get().strip() or "."
        listing.delete(0, "end")
        try:
            nodes = self.shell.kernel.fs.scandir(path)
        except Exception:
            self.files_status_var.set("Could not open that path.")
            self.file_details_var.set("Could not open that path.")
            return
        for node in nodes:
            prefix = "<DIR>" if node.is_dir() else "     "
            size = "" if node.is_dir() else f"{getattr(node, 'size', 0)} bytes"
            listing.insert("end", f"{prefix:>5}  {node.name:<24} {size}")
        self.files_status_var.set(f"{len(nodes)} item(s) in {path}")
        self.file_details_var.set(f"Path: {path}")

    def _files_go_up(self) -> None:
        path = self.file_path_var.get().strip() or "."
        normalized = path.replace("\\", "/")
        if normalized in {".", "/", "C:/", "C:"}:
            self.file_path_var.set("C:/")
        else:
            parts = [part for part in normalized.split("/") if part]
            if len(parts) <= 1:
                self.file_path_var.set("C:/")
            elif len(parts) == 2 and parts[0].endswith(":"):
                self.file_path_var.set(f"{parts[0]}/")
            else:
                self.file_path_var.set("/".join(parts[:-1]))
        self._refresh_files_app()

    def _files_open_selected(self, event: tk.Event) -> None:
        if self.shell is None:
            return
        listing = self.files_widgets.get("list")
        if not isinstance(listing, tk.Listbox):
            return
        selection = listing.curselection()
        if not selection:
            return
        raw = listing.get(selection[0])
        name = raw[7:31].strip()
        base = self.file_path_var.get().strip() or "."
        if base == "/":
            target = f"/{name}"
        elif base == ".":
            target = name
        else:
            target = f"{base.rstrip('/')}/{name}"
        if raw.startswith("<DIR>"):
            self.file_path_var.set(target)
            self._refresh_files_app()
            return
        result = self.shell.kernel.cat(target)
        self.files_status_var.set(target)
        self.file_details_var.set(result.message if result.ok else f"error: {result.message}")

    def _files_preview_selected(self, event: tk.Event) -> None:
        if self.shell is None:
            return
        listing = self.files_widgets.get("list")
        if not isinstance(listing, tk.Listbox):
            return
        selection = listing.curselection()
        if not selection:
            return
        raw = listing.get(selection[0])
        name = raw[7:31].strip()
        base = self.file_path_var.get().strip() or "."
        target = name if base == "." else f"{base.rstrip('/')}/{name}" if not base.endswith("/") else f"{base}{name}"
        result = self.shell.kernel.stat(target)
        self.file_details_var.set(result.message if result.ok else target)

    def _files_select_place(self, places: tk.Listbox) -> None:
        selection = places.curselection()
        if not selection:
            return
        self.file_path_var.set(places.get(selection[0]))
        self._refresh_files_app()

    def _files_new_folder(self) -> None:
        if self.shell is None:
            return
        path = self.file_path_var.get().strip() or "."
        base = "/" if path == "/" else path.rstrip("/")
        target = f"{base}/new_folder" if base not in {"", "/"} else "/new_folder"
        result = self.shell.kernel.mkdir(target)
        self.files_status_var.set(result.message if result.ok else f"error: {result.message}")
        self._refresh_files_app()

    def _files_new_file(self) -> None:
        if self.shell is None:
            return
        path = self.file_path_var.get().strip() or "."
        base = "/" if path == "/" else path.rstrip("/")
        target = f"{base}/new_file.txt" if base not in {"", "/"} else "/new_file.txt"
        result = self.shell.kernel.write(target, "New file inside Pyos_v0.1.")
        self.files_status_var.set(result.message if result.ok else f"error: {result.message}")
        self._refresh_files_app()

    def _load_notes(self) -> None:
        if self.shell is None:
            return
        editor = self.notes_widgets.get("editor")
        if not isinstance(editor, ScrolledText):
            return
        path = self.notes_path_var.get().strip() or "C:/USER/NOTES.txt"
        result = self.shell.kernel.cat(path)
        editor.delete("1.0", "end")
        if result.ok:
            editor.insert("1.0", result.message)
            self.notes_path_var.set(path)
        else:
            self.shell.kernel.write(path, "")
            self.notes_path_var.set(path)

    def _save_notes(self) -> None:
        if self.shell is None:
            return
        editor = self.notes_widgets.get("editor")
        if not isinstance(editor, ScrolledText):
            return
        path = self.notes_path_var.get().strip() or "C:/USER/NOTES.txt"
        content = editor.get("1.0", "end").rstrip()
        result = self.shell.kernel.write(path, content)
        self.notes_path_var.set(path if result.ok else f"error: {result.message}")
        self._refresh_files_app()

    def _launch_program(self, name: str) -> None:
        if self.shell is None:
            return
        result = self.shell.kernel.launch_program(name)
        self.process_status_var.set(result.message if result.ok else f"error: {result.message}")
        self._append_console(result.message)
        self._refresh_all_apps()

    def _tick_scheduler(self, count: int) -> None:
        if self.shell is None:
            return
        result = self.shell.kernel.tick(count)
        self.process_status_var.set(result.message.splitlines()[-1] if result.message else "Scheduler updated.")
        self._append_console(result.message)
        self._refresh_all_apps()

    def _latest_pid(self) -> int | None:
        if self.shell is None:
            return None
        processes = self.shell.kernel.processes.list_processes()
        return processes[-1].pid if processes else None

    def _inspect_latest_process(self) -> None:
        if self.shell is None:
            return
        info = self.process_widgets.get("info")
        if not isinstance(info, ScrolledText):
            return
        pid = self._latest_pid()
        if pid is None:
            self._set_text(info, "No processes yet.")
            return
        result = self.shell.kernel.procinfo(pid)
        self._set_text(info, result.message)

    def _kill_latest_process(self) -> None:
        if self.shell is None:
            return
        pid = self._latest_pid()
        if pid is None:
            self.process_status_var.set("No process available to kill.")
            return
        result = self.shell.kernel.kill(pid)
        self.process_status_var.set(result.message if result.ok else f"error: {result.message}")
        self._append_console(result.message)
        self._refresh_all_apps()

    def _refresh_process_app(self) -> None:
        if self.shell is None:
            return
        table = self.process_widgets.get("table")
        if isinstance(table, ScrolledText):
            self._set_text(table, self.shell.kernel.ps().message)
        self._inspect_latest_process()

    def _feed_keyboard_demo(self) -> None:
        if self.shell is None:
            return
        result = self.shell.kernel.keyboard_feed("hello from the desktop app")
        self.memory_status_var.set(result.message)
        self._refresh_memory_app()

    def _read_keyboard_demo(self) -> None:
        if self.shell is None:
            return
        result = self.shell.kernel.keyboard_read()
        self.memory_status_var.set(result.message if result.ok else f"error: {result.message}")
        self._append_console(result.message)
        self._refresh_memory_app()

    def _refresh_memory_app(self) -> None:
        if self.shell is None:
            return
        mem = self.memory_widgets.get("mem")
        screen = self.memory_widgets.get("screen")
        if isinstance(mem, ScrolledText):
            text = self.shell.kernel.mem().message + "\n\n" + self.shell.kernel.memmap().message
            self._set_text(mem, text)
        if isinstance(screen, ScrolledText):
            self._set_text(screen, self.shell.kernel.screen_dump(20).message)

    def _open_browser_app(self) -> None:
        window = self._create_window("browser", "Pyos_v0.1 The Internet", "900x620", (150, 90))
        body = self._window_shell(window, "The Internet", "A local browser-style app for docs, apps, and system views.")
        body.rowconfigure(2, weight=1)
        body.columnconfigure(1, weight=1)

        toolbar = tk.Frame(body, bg=WINDOW_BG)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        for label, url in [
            ("Home", "pyos://home"),
            ("Apps", "pyos://apps"),
            ("Docs", "pyos://docs"),
            ("System", "pyos://system"),
        ]:
            tk.Button(
                toolbar,
                text=label,
                command=lambda value=url: self._browser_open(value),
                bg="#22304a",
                fg="#eef7ff",
                relief="flat",
                padx=10,
            ).pack(side="left", padx=(0, 8))
        ttk.Entry(toolbar, textvariable=self.browser_url_var).pack(side="left", fill="x", expand=True, padx=(8, 8))
        ttk.Button(toolbar, text="Go", command=lambda: self._browser_open(self.browser_url_var.get())).pack(side="left")

        sidebar = tk.Frame(body, bg="#121a26")
        sidebar.grid(row=2, column=0, sticky="nsew", padx=(0, 10))
        sidebar.rowconfigure(2, weight=1)
        tk.Label(sidebar, text="Favorites", bg="#121a26", fg="#eef7ff", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=12, pady=(12, 8)
        )
        bookmarks = tk.Listbox(sidebar, bg="#0d1420", fg="#eef7ff", activestyle="none", height=8)
        bookmarks.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        for item in ["pyos://home", "pyos://apps", "pyos://docs", "pyos://system", "pyos://notes"]:
            bookmarks.insert("end", item)
        bookmarks.bind("<<ListboxSelect>>", lambda _e: self._browser_select_bookmark(bookmarks))

        content = ScrolledText(body, wrap="word", font=("Consolas", 10), bg="#0d1420", fg="#eef7ff")
        content.grid(row=2, column=1, sticky="nsew")

        status = tk.Label(body, textvariable=self.browser_status_var, anchor="w", bg=WINDOW_BG, fg="#9fc7ff")
        status.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.browser_widgets = {"window": window, "content": content, "bookmarks": bookmarks}
        self._browser_open(self.browser_url_var.get())

    def _browser_select_bookmark(self, bookmarks: tk.Listbox) -> None:
        selection = bookmarks.curselection()
        if not selection:
            return
        self._browser_open(bookmarks.get(selection[0]))

    def _browser_open(self, url: str) -> None:
        if self.shell is None:
            return
        content = self.browser_widgets.get("content")
        if not isinstance(content, ScrolledText):
            return
        normalized = (url or "pyos://home").strip()
        self.browser_url_var.set(normalized)
        page = self._browser_page(normalized)
        self.browser_status_var.set(f"Opened {normalized}")
        self._set_text(content, page)

    def _browser_page(self, url: str) -> str:
        if self.shell is None:
            return "Browser unavailable."
        if url == "pyos://home":
            return (
                "Pyos_v0.1 Online Services\n"
                "===============\n\n"
                "Welcome to the desktop online shell.\n\n"
                "Drive layout:\n"
                "- C:/WINDOWS\n"
                "- C:/PROGRAM FILES\n"
                "- C:/USER\n"
                "- C:/TEMP\n\n"
                "Quick links:\n"
                "- pyos://apps\n"
                "- pyos://docs\n"
                "- pyos://system\n"
                "- pyos://notes\n"
            )
        if url == "pyos://apps":
            return (
                "Installed Apps\n"
                "--------------\n"
                "My Computer\nNotepad\nMS-DOS Prompt\nOnline Services\nMedia Player\nPaint\n"
                "Program Manager\nSystem Monitor\nClock\nControl Panel\nCalculator\n"
            )
        if url == "pyos://docs":
            return (
                "Pyos_v0.1 Docs\n"
                "---------\n"
                "This educational OS simulates:\n"
                "- a Windows-style in-memory C drive\n"
                "- process scheduling\n"
                "- virtual memory tracking\n"
                "- keyboard and screen I/O\n"
                "- a desktop shell with multiple apps\n"
            )
        if url == "pyos://system":
            ps = self.shell.kernel.ps().message
            mem = self.shell.kernel.mem().message
            return f"System Snapshot\n---------------\n\n{ps}\n\n{mem}"
        if url == "pyos://notes":
            result = self.shell.kernel.cat(self.notes_path_var.get())
            return result.message if result.ok else f"error: {result.message}"
        return f"Could not find {url}\n\nTry pyos://home"

    def _open_music_app(self) -> None:
        window = self._create_window("music", "Pyos_v0.1 Media Player", "520x500", (860, 120))
        body = self._window_shell(window, "Media Player", "A simple player for built-in desktop tracks.")
        body.rowconfigure(2, weight=1)
        body.columnconfigure(0, weight=1)

        now_playing = tk.Label(body, text="Now Playing", bg=WINDOW_BG, fg="#eef7ff", font=("Segoe UI", 14, "bold"))
        now_playing.grid(row=0, column=0, sticky="w")
        status = tk.Label(body, textvariable=self.music_status_var, bg=WINDOW_BG, fg="#9fc7ff", anchor="w")
        status.grid(row=1, column=0, sticky="ew", pady=(6, 10))

        playlist = tk.Listbox(body, bg="#0d1420", fg="#eef7ff", activestyle="none")
        playlist.grid(row=2, column=0, sticky="nsew")
        for name, description in self.music_tracks:
            playlist.insert("end", f"{name}  -  {description}")
        playlist.bind("<Double-1>", lambda _e: self._music_select_track(playlist))

        controls = tk.Frame(body, bg=WINDOW_BG)
        controls.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(controls, text="Play", command=self._music_play).pack(side="left")
        ttk.Button(controls, text="Pause", command=self._music_pause).pack(side="left", padx=(8, 0))
        ttk.Button(controls, text="Next", command=self._music_next).pack(side="left", padx=(8, 0))

        progress = ttk.Progressbar(body, mode="determinate", maximum=100)
        progress.grid(row=4, column=0, sticky="ew", pady=(12, 0))

        self.music_widgets = {"window": window, "playlist": playlist, "progress": progress}
        self._refresh_music_status()

    def _music_select_track(self, playlist: tk.Listbox) -> None:
        selection = playlist.curselection()
        if not selection:
            return
        self.current_track_index = selection[0]
        self.music_progress = 0
        self._refresh_music_status()

    def _refresh_music_status(self) -> None:
        name, description = self.music_tracks[self.current_track_index]
        state = "Playing" if self.music_is_playing else "Paused"
        self.music_status_var.set(f"{state}: {name} | {description}")
        progress = self.music_widgets.get("progress")
        if isinstance(progress, ttk.Progressbar):
            progress["value"] = self.music_progress

    def _music_play(self) -> None:
        self.music_is_playing = True
        self._refresh_music_status()
        self._music_tick()

    def _music_pause(self) -> None:
        self.music_is_playing = False
        self._refresh_music_status()

    def _music_next(self) -> None:
        self.current_track_index = (self.current_track_index + 1) % len(self.music_tracks)
        self.music_progress = 0
        self._refresh_music_status()

    def _music_tick(self) -> None:
        if not self.music_is_playing:
            return
        self.music_progress += 3
        if self.music_progress >= 100:
            self._music_next_internal()
        else:
            self._refresh_music_status()
        self.root.after(500, self._music_tick)

    def _music_next_internal(self) -> None:
        self.current_track_index = (self.current_track_index + 1) % len(self.music_tracks)
        self.music_progress = 0
        self._refresh_music_status()

    def _open_paint_app(self) -> None:
        window = self._create_window("paint", "Pyos_v0.1 Paint", "760x560", (620, 160))
        body = self._window_shell(window, "Paint", "Sketch, annotate, and doodle inside the desktop.")
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)

        toolbar = tk.Frame(body, bg=WINDOW_BG)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        for color in ["#7cc7ff", "#ff8c82", "#ffe082", "#80e27e", "#ffffff"]:
            tk.Button(
                toolbar,
                bg=color,
                width=3,
                command=lambda value=color: self._set_paint_color(value),
                relief="flat",
            ).pack(side="left", padx=(0, 6))
        ttk.Button(toolbar, text="Brush +", command=lambda: self._change_brush_size(2)).pack(side="left", padx=(12, 0))
        ttk.Button(toolbar, text="Brush -", command=lambda: self._change_brush_size(-2)).pack(side="left", padx=(8, 0))
        ttk.Button(toolbar, text="Clear", command=self._clear_paint_canvas).pack(side="left", padx=(8, 0))

        canvas = tk.Canvas(body, bg="#f7fbff", highlightthickness=0)
        canvas.grid(row=1, column=0, sticky="nsew")
        canvas.bind("<B1-Motion>", self._paint_drag)

        status = tk.Label(body, textvariable=self.paint_status_var, anchor="w", bg=WINDOW_BG, fg="#9fc7ff")
        status.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self.paint_widgets = {"window": window, "canvas": canvas}

    def _set_paint_color(self, color: str) -> None:
        self.paint_current_color = color
        self.paint_status_var.set(f"Brush color set to {color}.")

    def _change_brush_size(self, delta: int) -> None:
        self.paint_brush_size = max(2, self.paint_brush_size + delta)
        self.paint_status_var.set(f"Brush size: {self.paint_brush_size}")

    def _paint_drag(self, event: tk.Event) -> None:
        canvas = self.paint_widgets.get("canvas")
        if not isinstance(canvas, tk.Canvas):
            return
        size = self.paint_brush_size
        canvas.create_oval(
            event.x - size,
            event.y - size,
            event.x + size,
            event.y + size,
            fill=self.paint_current_color,
            outline=self.paint_current_color,
        )

    def _clear_paint_canvas(self) -> None:
        canvas = self.paint_widgets.get("canvas")
        if isinstance(canvas, tk.Canvas):
            canvas.delete("all")
        self.paint_status_var.set("Canvas cleared.")

    def _open_settings_app(self) -> None:
        window = self._create_window("settings", "Pyos_v0.1 Control Panel", "620x420", (760, 220))
        body = self._window_shell(window, "Control Panel", "Adjust system settings, colors, and wallpaper.")
        body.rowconfigure(1, weight=1)
        body.columnconfigure(1, weight=1)

        categories_frame = tk.Frame(body, bg=WINDOW_BG, bd=2, relief="sunken")
        categories_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 3))
        tk.Label(categories_frame, text="Settings", bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8, "bold"), bd=2, relief="raised").pack(fill="x")
        categories = tk.Listbox(categories_frame, font=("Tahoma", 8), activestyle="none", bg="#ffffff", fg=TEXT_DARK, exportselection=False)
        categories.pack(fill="both", expand=True, padx=2, pady=2)
        for item in ["Desktop", "Colors", "System", "Mouse", "Keyboard"]:
            categories.insert("end", item)
        categories.bind("<<ListboxSelect>>", lambda _event: self._select_control_panel_category(categories))
        categories.selection_set(0)

        details = tk.Frame(body, bg=WINDOW_BG, bd=2, relief="sunken")
        details.grid(row=0, column=1, sticky="nsew")
        details.columnconfigure(0, weight=1)
        tk.Label(details, textvariable=self.control_panel_selection_var, bg=TASKBAR_BG, fg=TEXT_DARK, font=("Tahoma", 8, "bold"), bd=2, relief="raised").grid(row=0, column=0, sticky="ew")

        section = tk.Frame(details, bg=WINDOW_BG)
        section.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

        tk.Label(section, text="Accent Color", bg=WINDOW_BG, fg=TEXT_DARK, font=("Tahoma", 8, "bold")).pack(anchor="w")
        accent_row = tk.Frame(section, bg=WINDOW_BG)
        accent_row.pack(anchor="w", pady=(4, 10))
        for color in ["#000080", "#800000", "#008000", "#808000", "#008080"]:
            tk.Radiobutton(
                accent_row,
                text=color,
                value=color,
                variable=self.accent_choice_var,
                command=self._apply_accent_color,
                bg=WINDOW_BG,
                fg=TEXT_DARK,
                selectcolor=PANEL_LIGHT,
                activebackground=WINDOW_BG,
                activeforeground=TEXT_DARK,
                font=("Tahoma", 8),
            ).pack(anchor="w")

        tk.Label(section, text="Wallpaper", bg=WINDOW_BG, fg=TEXT_DARK, font=("Tahoma", 8, "bold")).pack(anchor="w")
        wallpaper_row = tk.Frame(section, bg=WINDOW_BG)
        wallpaper_row.pack(anchor="w", pady=(4, 10))
        for wallpaper in ["Bliss", "Clouds", "Teal"]:
            tk.Radiobutton(
                wallpaper_row,
                text=wallpaper,
                value=wallpaper,
                variable=self.wallpaper_choice_var,
                command=self._apply_wallpaper,
                bg=WINDOW_BG,
                fg=TEXT_DARK,
                selectcolor=PANEL_LIGHT,
                activebackground=WINDOW_BG,
                activeforeground=TEXT_DARK,
                font=("Tahoma", 8),
            ).pack(anchor="w")

        info = tk.Label(
            section,
            text=(
                "Current shell: Pyos_v0.1\n"
                "Filesystem: C:/USER\n"
                "Window style: custom Win95 frames\n"
                "Wallpaper engine: pure Tkinter canvas"
            ),
            justify="left",
            anchor="w",
            bg=WINDOW_BG,
            fg=TEXT_DARK,
            font=("Tahoma", 8),
        )
        info.pack(fill="x", pady=(8, 0))

        status = tk.Label(body, textvariable=self.settings_status_var, anchor="w", bg=TASKBAR_BG, fg=TEXT_DARK, bd=2, relief="sunken", font=("Tahoma", 8))
        status.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(2, 0))
        self.settings_widgets = {"window": window, "info": info, "categories": categories}

    def _select_control_panel_category(self, categories: tk.Listbox) -> None:
        selection = categories.curselection()
        if not selection:
            return
        self.control_panel_selection_var.set(categories.get(selection[0]))

    def _apply_accent_color(self) -> None:
        color = self.accent_choice_var.get()
        self.title_bar_color = color
        self.settings_status_var.set(f"Accent color changed to {color}.")
        self.paint_current_color = color

    def _apply_wallpaper(self) -> None:
        wallpaper = self.wallpaper_choice_var.get()
        self._repaint_wallpaper()
        self.settings_status_var.set(f"Wallpaper changed to {wallpaper}.")

    def _open_shutdown_dialog(self) -> None:
        if self.shutdown_dialog is not None and self.shutdown_dialog.winfo_exists():
            self.shutdown_dialog.lift()
            self.shutdown_dialog.focus_force()
            return
        dialog = tk.Toplevel(self.root)
        dialog.overrideredirect(True)
        dialog.geometry("330x170+470+300")
        dialog.configure(bg=CARD_BG, bd=2, relief="raised")
        dialog.transient(self.root)
        dialog.grab_set()
        self.shutdown_dialog = dialog

        title = tk.Frame(dialog, bg=self.title_bar_color, height=24)
        title.pack(fill="x")
        title.pack_propagate(False)
        tk.Label(title, text="Shut Down Windows", bg=self.title_bar_color, fg=TEXT_LIGHT, font=("Tahoma", 8, "bold")).pack(side="left", padx=6, pady=4)

        body = tk.Frame(dialog, bg=CARD_BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)
        tk.Label(body, text="What do you want the computer to do?", bg=CARD_BG, fg=TEXT_DARK, font=("Tahoma", 8)).pack(anchor="w")
        choice = tk.StringVar(value="shutdown")
        for value, label in [("shutdown", "Shut down"), ("restart", "Restart"), ("logoff", "Close all programs and log on as a different user")]:
            tk.Radiobutton(body, text=label, value=value, variable=choice, bg=CARD_BG, fg=TEXT_DARK, selectcolor=PANEL_LIGHT, activebackground=CARD_BG, activeforeground=TEXT_DARK, font=("Tahoma", 8)).pack(anchor="w", pady=(6, 0))

        buttons = tk.Frame(body, bg=CARD_BG)
        buttons.pack(anchor="e", pady=(14, 0))
        tk.Button(buttons, text="Yes", command=lambda: self._confirm_shutdown(choice.get()), bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=8, font=("Tahoma", 8)).pack(side="left")
        tk.Button(buttons, text="No", command=self._close_shutdown_dialog, bg=TASKBAR_BG, fg=TEXT_DARK, relief="raised", width=8, font=("Tahoma", 8)).pack(side="left", padx=(6, 0))

    def _close_shutdown_dialog(self) -> None:
        if self.shutdown_dialog is not None and self.shutdown_dialog.winfo_exists():
            try:
                self.shutdown_dialog.grab_release()
            except tk.TclError:
                pass
            self.shutdown_dialog.destroy()
        self.shutdown_dialog = None

    def _confirm_shutdown(self, action: str) -> None:
        self._close_shutdown_dialog()
        splash = tk.Toplevel(self.root)
        splash.overrideredirect(True)
        splash.geometry("360x140+450+300")
        splash.configure(bg=CARD_BG, bd=2, relief="raised")
        message = "It is now safe to turn off your computer." if action == "shutdown" else "Preparing desktop..."
        body = tk.Frame(splash, bg=CARD_BG, bd=2, relief="sunken")
        body.pack(fill="both", expand=True, padx=3, pady=3)
        tk.Label(body, text=message, bg=CARD_BG, fg=TEXT_DARK, font=("Tahoma", 10, "bold")).pack(expand=True)

        def finish() -> None:
            if splash.winfo_exists():
                splash.destroy()
            if action == "shutdown":
                self._log_out("Windows is shutting down.")
            elif action == "restart":
                self._log_out("Windows restarted.")
            else:
                self._log_out("You may now log on again.")

        self.root.after(700, finish)

    def _open_clock_app(self) -> None:
        window = self._create_window("clock", "Pyos_v0.1 Clock", "520x540", (940, 180))
        body = self._window_shell(window, "Clock", "Local time, analog face, and countdown timer.")
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)

        digital = tk.Label(body, text="", bg=WINDOW_BG, fg="#eef7ff", font=("Consolas", 24, "bold"))
        digital.grid(row=0, column=0, sticky="ew")

        canvas = tk.Canvas(body, width=260, height=260, bg="#0d1420", highlightthickness=0)
        canvas.grid(row=1, column=0, pady=(12, 12))

        timer_row = tk.Frame(body, bg=WINDOW_BG)
        timer_row.grid(row=2, column=0, sticky="ew")
        ttk.Entry(timer_row, textvariable=self.timer_seconds_var, width=10).pack(side="left")
        ttk.Button(timer_row, text="Start Timer", command=self._start_timer).pack(side="left", padx=(8, 0))
        ttk.Button(timer_row, text="Stop", command=self._stop_timer).pack(side="left", padx=(8, 0))

        status = tk.Label(body, textvariable=self.clock_status_var, anchor="w", bg=WINDOW_BG, fg="#9fc7ff")
        status.grid(row=3, column=0, sticky="ew", pady=(12, 0))

        self.clock_widgets = {"window": window, "digital": digital, "canvas": canvas}
        self._draw_clock_face()

    def _draw_clock_face(self) -> None:
        from datetime import datetime

        digital = self.clock_widgets.get("digital")
        canvas = self.clock_widgets.get("canvas")
        if isinstance(digital, tk.Label):
            digital.config(text=datetime.now().strftime("%I:%M:%S %p"))
        if isinstance(canvas, tk.Canvas):
            canvas.delete("all")
            center_x = 130
            center_y = 130
            radius = 100
            canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="#7cc7ff", width=3)
            for hour in range(12):
                angle = math.radians(hour * 30 - 90)
                x1 = center_x + math.cos(angle) * 78
                y1 = center_y + math.sin(angle) * 78
                x2 = center_x + math.cos(angle) * 92
                y2 = center_y + math.sin(angle) * 92
                canvas.create_line(x1, y1, x2, y2, fill="#eef7ff", width=2)

            now = datetime.now()
            minute_angle = math.radians(now.minute * 6 - 90)
            hour_angle = math.radians(((now.hour % 12) + now.minute / 60) * 30 - 90)
            second_angle = math.radians(now.second * 6 - 90)
            canvas.create_line(center_x, center_y, center_x + math.cos(hour_angle) * 52, center_y + math.sin(hour_angle) * 52, fill="#eef7ff", width=4)
            canvas.create_line(center_x, center_y, center_x + math.cos(minute_angle) * 72, center_y + math.sin(minute_angle) * 72, fill="#7cc7ff", width=3)
            canvas.create_line(center_x, center_y, center_x + math.cos(second_angle) * 84, center_y + math.sin(second_angle) * 84, fill="#ff8c82", width=2)
            canvas.create_oval(center_x - 4, center_y - 4, center_x + 4, center_y + 4, fill="#eef7ff", outline="")
        self.root.after(1000, self._draw_clock_face)

    def _start_timer(self) -> None:
        try:
            self.timer_remaining = max(1, int(self.timer_seconds_var.get()))
        except ValueError:
            self.clock_status_var.set("Timer must be an integer number of seconds.")
            return
        self.timer_running = True
        self.clock_status_var.set(f"Timer running: {self.timer_remaining} seconds remaining.")
        self._timer_tick()

    def _stop_timer(self) -> None:
        self.timer_running = False
        self.clock_status_var.set("Timer stopped.")

    def _timer_tick(self) -> None:
        if not self.timer_running:
            return
        if self.timer_remaining <= 0:
            self.timer_running = False
            self.clock_status_var.set("Timer complete.")
            return
        self.clock_status_var.set(f"Timer running: {self.timer_remaining} seconds remaining.")
        self.timer_remaining -= 1
        self.root.after(1000, self._timer_tick)

    def _tick_clock(self) -> None:
        from datetime import datetime

        if self.clock_label is not None:
            self.clock_label.config(text=datetime.now().strftime("%I:%M %p"))
        if self.taskbar_label is not None:
            self.taskbar_label.config(text=datetime.now().strftime("%I:%M %p"))
        self.root.after(1000, self._tick_clock)

    def _log_out(self, message: str = "Signed out.") -> None:
        for key in list(self.open_windows):
            self._close_window(key)
        self._close_signup_dialog()
        self._close_shutdown_dialog()
        self.current_user = None
        self.username_var.set("")
        self.password_var.set("")
        self.command_var.set("")
        self.status_var.set(message)
        self._build_auth_view()

    def run(self) -> None:
        self.root.mainloop()


def run_gui() -> None:
    """Launch the desktop simulator window."""

    SimulatorWindow().run()
