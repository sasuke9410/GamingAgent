"""
tools/log_window.py

Real-time agent log window with Game Boy controller visualizer.
Runs in a daemon thread. Thread-safe updates via queue.Queue.
"""
import queue
import re
import threading
import time
import tkinter as tk
from tkinter import scrolledtext
import datetime


# ── Timing ────────────────────────────────────────────────────────────────────
POLL_MS = 100          # queue poll interval
BUTTON_FLASH_MS = 250  # how long a pressed button stays lit

# ── Window geometry ───────────────────────────────────────────────────────────
WIN_W = 480
WIN_H = 780
GB_W  = 380   # Game Boy canvas width
GB_H  = 400   # Game Boy canvas height

# ── Palette (DMG-inspired) ────────────────────────────────────────────────────
BG            = "#1a1b26"   # window background
PANEL_BG      = "#24253a"   # panel background
BORDER_COL    = "#414868"   # separator / border

GB_BODY       = "#c0c0b8"   # classic light gray body
GB_BODY_SHAD  = "#8a8a82"   # body shadow / bottom edge
GB_VENT       = "#a0a09a"   # speaker vent lines
SCREEN_FRAME  = "#505048"   # screen bezel
SCREEN_BG     = "#0f380f"   # classic GB screen green-off
SCREEN_GLARE  = "#1a5f1a"   # very faint inner highlight

DPAD_NORMAL   = "#2a2a2a"   # D-pad cross normal
DPAD_PRESSED  = "#ffe033"   # D-pad pressed  (bright yellow)
DPAD_CENTER   = "#1a1a1a"   # D-pad center pip

AB_BODY       = "#8b1a2c"   # A/B button maroon
AB_PRESSED    = "#ff3344"   # A/B pressed (bright red)
AB_SHINE      = "#d04060"   # A/B highlight arc

SS_BODY       = "#3a3a3a"   # Start/Select pill normal
SS_PRESSED    = "#8080ff"   # Start/Select pressed

LABEL_FG      = "#a0a098"   # small button labels
FG_DEFAULT    = "#c0caf5"   # general text
FG_ACCENT     = "#7aa2f7"   # accent / header
FG_ACTION     = "#9ece6a"   # action text
FG_THOUGHT    = "#e0af68"   # thought text

FONT_UI       = ("Consolas", 9)
FONT_LABEL    = ("Consolas", 8, "bold")
FONT_HEADER   = ("Consolas", 11, "bold")
FONT_THOUGHT  = ("Consolas", 10)


# ── Helper ────────────────────────────────────────────────────────────────────

def _parse_button(action_str: str) -> str | None:
    """Extract button name from '(a, 1)' or 'a' or 'up' etc."""
    if not action_str:
        return None
    m = re.match(r'\(?(\w+)', action_str.strip())
    return m.group(1).lower() if m else None


# ── Game Boy Canvas ───────────────────────────────────────────────────────────

class GameBoyWidget:
    """
    Draws a DMG-style Game Boy on a tk.Canvas.
    Call highlight(button) to flash a button, reset() to clear.
    """

    def __init__(self, parent):
        self.canvas = tk.Canvas(
            parent,
            width=GB_W, height=GB_H,
            bg=BG, bd=0, highlightthickness=0
        )
        self.canvas.pack(pady=4)

        # button tag → canvas item id(s)
        self._btn_items: dict[str, list[int]] = {}
        self._btn_colors: dict[str, tuple[str, str]] = {}  # tag → (normal, pressed)

        self._draw()

    # ── Public ────────────────────────────────────────────────────────────────

    def highlight(self, button: str | None) -> None:
        """Flash button for BUTTON_FLASH_MS ms."""
        if not button:
            return
        tag = button.lower()
        items = self._btn_items.get(tag)
        colors = self._btn_colors.get(tag)
        if not items or not colors:
            return
        # light up
        for item in items:
            self.canvas.itemconfig(item, fill=colors[1])
        # schedule restore
        self.canvas.after(BUTTON_FLASH_MS, lambda: self._restore(tag))

    def _restore(self, tag: str) -> None:
        items = self._btn_items.get(tag)
        colors = self._btn_colors.get(tag)
        if items and colors:
            for item in items:
                self.canvas.itemconfig(item, fill=colors[0])

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _register(self, tag: str, item_id: int, normal: str, pressed: str):
        self._btn_items.setdefault(tag, []).append(item_id)
        self._btn_colors[tag] = (normal, pressed)

    def _draw(self):
        c = self.canvas

        # ── Body shell ──────────────────────────────────────────────────────
        bx0, by0, bx1, by1 = 30, 8, GB_W - 30, GB_H - 8
        # shadow
        c.create_rounded_rect = _rounded_rect
        _rounded_rect(c, bx0+4, by0+4, bx1+4, by1+4, r=28, fill=GB_BODY_SHAD, outline="")
        # body
        _rounded_rect(c, bx0, by0, bx1, by1, r=28, fill=GB_BODY, outline=GB_BODY_SHAD, width=2)

        # top-right angled cut (characteristic DMG shape)
        cut_size = 50
        c.create_polygon(
            bx1 - cut_size, by0,
            bx1, by0 + cut_size,
            bx1, by0,
            fill=BG, outline=""
        )
        # redraw that corner with body color + shaped notch
        c.create_polygon(
            bx1 - cut_size + 2, by0 + 2,
            bx1 - 2, by0 + cut_size - 2,
            bx1 - 2, by0 + 2,
            fill=GB_BODY, outline=GB_BODY_SHAD
        )

        # ── GAME BOY logo ────────────────────────────────────────────────────
        c.create_text(
            (bx0 + bx1) // 2, by0 + 14,
            text="GAME BOY™", fill="#1a1a1a",
            font=("Helvetica", 8, "bold"), anchor="center"
        )
        c.create_text(
            (bx0 + bx1) // 2 - 2, by0 + 26,
            text="NINTENDO", fill="#4a4a4a",
            font=("Helvetica", 6), anchor="center"
        )

        # ── Screen bezel ────────────────────────────────────────────────────
        sx0, sy0 = bx0 + 42, by0 + 44
        sx1, sy1 = bx0 + 218, by0 + 148
        _rounded_rect(c, sx0, sy0, sx1, sy1, r=10, fill=SCREEN_FRAME, outline="#1a1a1a", width=2)
        # inner screen
        _rounded_rect(c, sx0+8, sy0+8, sx1-8, sy1-8, r=4, fill=SCREEN_BG, outline="")
        # power LED dot
        c.create_oval(sx0 + 8, sy1 + 8, sx0 + 16, sy1 + 16, fill="#00cc44", outline="")
        c.create_text(sx0 + 26, sy1 + 12, text="BATTERY", fill=LABEL_FG, font=("Helvetica", 6), anchor="w")

        # ── Speaker vents (right side) ───────────────────────────────────────
        vx = bx1 - 50
        for i in range(6):
            vy = by0 + 230 + i * 18
            _rounded_rect(c, vx, vy, vx + 34, vy + 8, r=4, fill=GB_VENT, outline=GB_BODY_SHAD)

        # ── D-pad ────────────────────────────────────────────────────────────
        dpx, dpy = bx0 + 75, by0 + 215   # center of D-pad
        arm = 22   # arm half-width
        pad = 20   # arm length

        def _dpad_arm(dx, dy, tag_name, label):
            x0 = dpx + dx * pad - arm
            y0 = dpy + dy * pad - arm
            x1 = dpx + dx * pad + arm
            y1 = dpy + dy * pad + arm
            item = _rounded_rect(c, x0, y0, x1, y1, r=5,
                                  fill=DPAD_NORMAL, outline="#111111", width=1)
            self._register(tag_name, item, DPAD_NORMAL, DPAD_PRESSED)
            c.create_text(
                (x0+x1)//2, (y0+y1)//2,
                text=label, fill=LABEL_FG, font=("Helvetica", 10, "bold")
            )

        _dpad_arm(0, -1, "up",    "▲")
        _dpad_arm(0,  1, "down",  "▼")
        _dpad_arm(-1, 0, "left",  "◀")
        _dpad_arm( 1, 0, "right", "▶")

        # center cap
        cx0, cy0 = dpx - arm, dpy - arm
        item = c.create_rectangle(cx0, cy0, dpx+arm, dpy+arm, fill=DPAD_CENTER, outline="")
        # (center pip is not interactive — just visual)

        # ── A and B buttons ──────────────────────────────────────────────────
        # B: lower-left, A: upper-right (DMG layout)
        abr = 18   # radius
        bx_b, by_b = bx1 - 110, by0 + 230   # B center
        bx_a, by_a = bx1 - 68,  by0 + 205   # A center (upper-right of B)

        def _ab_button(cx, cy, tag_name, label):
            # shadow
            c.create_oval(cx-abr+2, cy-abr+2, cx+abr+2, cy+abr+2,
                           fill="#4a0010", outline="")
            # body
            item = c.create_oval(cx-abr, cy-abr, cx+abr, cy+abr,
                                   fill=AB_BODY, outline="#1a0008", width=1)
            self._register(tag_name, item, AB_BODY, AB_PRESSED)
            # shine arc
            c.create_arc(cx-abr+4, cy-abr+3, cx+abr-6, cy-4,
                          start=30, extent=120, fill=AB_SHINE, outline="")
            c.create_text(cx, cy, text=label, fill="white",
                           font=("Helvetica", 10, "bold"))

        _ab_button(bx_b, by_b, "b", "B")
        _ab_button(bx_a, by_a, "a", "A")

        # ── Start / Select ───────────────────────────────────────────────────
        def _ss_button(cx, cy, tag_name, label):
            pw, ph = 36, 12
            item = _rounded_rect(c, cx-pw//2, cy-ph//2, cx+pw//2, cy+ph//2,
                                   r=5, fill=SS_BODY, outline="#111111")
            self._register(tag_name, item, SS_BODY, SS_PRESSED)
            c.create_text(cx, cy + ph + 6, text=label, fill=LABEL_FG,
                           font=("Helvetica", 7))

        mid_x = (bx0 + bx1) // 2
        _ss_button(mid_x - 32, by0 + 262, "select", "SELECT")
        _ss_button(mid_x + 32, by0 + 262, "start",  "START")

        # ── Action label (shows last button) ─────────────────────────────────
        self._action_text_id = c.create_text(
            (bx0 + bx1) // 2, by0 + 310,
            text="", fill=FG_ACTION,
            font=("Consolas", 11, "bold"), anchor="center"
        )

    def show_action_label(self, action_str: str) -> None:
        self.canvas.itemconfig(self._action_text_id, text=action_str)


# ── Rounded rectangle helper ──────────────────────────────────────────────────

def _rounded_rect(canvas, x0, y0, x1, y1, r=10, **kwargs) -> int:
    """Draw a rounded rectangle; returns the canvas item id of the last segment."""
    pts = [
        x0+r, y0,   x1-r, y0,
        x1,   y0+r, x1,   y1-r,
        x1-r, y1,   x0+r, y1,
        x0,   y1-r, x0,   y0+r,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


# ── Main log window ───────────────────────────────────────────────────────────

class LogWindow:
    """
    Thread-safe real-time log window with Game Boy controller visualizer.

    Usage (from main thread):
        win = LogWindow()
        win.start()
        win.log_step(step=1, elapsed_s=5.2, action="(a, 1)",
                     thought="...", game_state="...")
        win.close()
    """

    def __init__(self, title="Agent Log", x_offset=520, y_offset=0):
        self._q: queue.Queue = queue.Queue()
        self._title    = title
        self._x_offset = x_offset
        self._y_offset = y_offset
        self._thread: threading.Thread | None = None
        self._ready    = threading.Event()

    # ── Public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        self._thread = threading.Thread(
            target=self._run, daemon=True, name="LogWindowThread"
        )
        self._thread.start()
        self._ready.wait(timeout=6.0)

    def log_step(self, step: int, elapsed_s: float, action: str,
                 thought: str, game_state: str, reward: float = 0.0) -> None:
        self._q.put(dict(
            type="step", step=step, elapsed_s=elapsed_s,
            action=action, thought=thought or "",
            game_state=game_state or "", reward=reward,
            ts=datetime.datetime.now().strftime("%H:%M:%S"),
        ))

    def log_message(self, text: str) -> None:
        self._q.put(dict(type="msg", text=text))

    def close(self) -> None:
        self._q.put(dict(type="quit"))

    # ── Internals ─────────────────────────────────────────────────────────────

    def _run(self) -> None:
        root = tk.Tk()
        root.title(self._title)
        root.configure(bg=BG)
        root.geometry(f"{WIN_W}x{WIN_H}+{self._x_offset}+{self._y_offset}")
        root.resizable(True, True)
        self._build(root)
        self._ready.set()
        self._after_id = root.after(POLL_MS, self._poll)
        try:
            root.mainloop()
        except Exception:
            pass

    def _build(self, root: tk.Tk) -> None:
        self._root = root

        # ── Status bar ───────────────────────────────────────────────────────
        bar = tk.Frame(root, bg=PANEL_BG, pady=4)
        bar.pack(fill=tk.X, padx=6, pady=(6, 2))

        self._sv_step    = tk.StringVar(value="Step: —")
        self._sv_time    = tk.StringVar(value="—")
        self._sv_reward  = tk.StringVar(value="Reward: —")

        tk.Label(bar, textvariable=self._sv_step,   bg=PANEL_BG, fg=FG_ACCENT,
                 font=FONT_HEADER, width=10, anchor="w").pack(side=tk.LEFT, padx=8)
        tk.Label(bar, textvariable=self._sv_time,   bg=PANEL_BG, fg=FG_DEFAULT,
                 font=FONT_UI).pack(side=tk.LEFT, padx=4)
        tk.Label(bar, textvariable=self._sv_reward, bg=PANEL_BG, fg=FG_ACTION,
                 font=FONT_UI).pack(side=tk.RIGHT, padx=8)

        tk.Frame(root, bg=BORDER_COL, height=1).pack(fill=tk.X, padx=6, pady=2)

        # ── Game Boy controller ──────────────────────────────────────────────
        gb_frame = tk.Frame(root, bg=BG)
        gb_frame.pack(fill=tk.X, padx=6)
        self._gb = GameBoyWidget(gb_frame)

        tk.Frame(root, bg=BORDER_COL, height=1).pack(fill=tk.X, padx=6, pady=2)

        # ── Thought panel ────────────────────────────────────────────────────
        thought_frame = tk.Frame(root, bg=PANEL_BG)
        thought_frame.pack(fill=tk.X, padx=6, pady=2)
        tk.Label(thought_frame, text="💭 Thought", bg=PANEL_BG, fg=FG_ACCENT,
                 font=FONT_LABEL).pack(anchor="w", padx=6, pady=(4,0))
        self._thought_box = tk.Text(
            thought_frame, bg="#1f2035", fg=FG_THOUGHT, font=FONT_THOUGHT,
            height=5, wrap=tk.WORD, relief=tk.FLAT, bd=0,
            padx=6, pady=4,
        )
        self._thought_box.pack(fill=tk.X, padx=4, pady=(2,6))
        self._thought_box.config(state=tk.DISABLED)

        tk.Frame(root, bg=BORDER_COL, height=1).pack(fill=tk.X, padx=6, pady=2)

        # ── History ──────────────────────────────────────────────────────────
        tk.Label(root, text="📜 History", bg=BG, fg=FG_ACCENT,
                 font=FONT_LABEL).pack(anchor="w", padx=12)

        self._history = scrolledtext.ScrolledText(
            root, bg="#131421", fg=FG_DEFAULT, font=FONT_UI,
            wrap=tk.WORD, relief=tk.FLAT, bd=0, padx=6, pady=4,
            state=tk.DISABLED,
        )
        self._history.pack(fill=tk.BOTH, expand=True, padx=6, pady=(0, 6))

        for tag, col in [
            ("header",  FG_ACCENT),
            ("action",  FG_ACTION),
            ("thought", FG_THOUGHT),
            ("info",    "#565f89"),
        ]:
            self._history.tag_configure(tag, foreground=col)

    # ── Queue polling ─────────────────────────────────────────────────────────

    def _poll(self) -> None:
        try:
            while True:
                self._handle(self._q.get_nowait())
        except queue.Empty:
            pass
        if self._root:
            self._after_id = self._root.after(POLL_MS, self._poll)

    def _handle(self, msg: dict) -> None:
        t = msg.get("type")
        if t == "quit":
            if self._root:
                # Cancel pending after() callbacks to avoid Tcl async handler warnings
                try:
                    self._root.after_cancel(self._after_id)
                except Exception:
                    pass
                # Delete StringVar references before destroy to avoid GC warnings
                for attr in ("_sv_step", "_sv_time", "_sv_reward"):
                    try:
                        sv = getattr(self, attr, None)
                        if sv is not None:
                            sv.set("")
                    except Exception:
                        pass
                self._root.quit()
                self._root.destroy()
                self._root = None
        elif t == "step":
            self._update_step(msg)
        elif t == "msg":
            self._append(msg["text"] + "\n", "info")

    def _update_step(self, msg: dict) -> None:
        step     = msg["step"]
        elapsed  = msg["elapsed_s"]
        action   = msg["action"]
        thought  = msg["thought"]
        state    = msg["game_state"]
        reward   = msg["reward"]
        ts       = msg["ts"]

        # Status bar
        mins, secs = divmod(int(elapsed), 60)
        self._sv_step.set(f"Step: {step}")
        self._sv_time.set(f"{mins:02d}:{secs:02d}  [{ts}]")
        self._sv_reward.set(f"Reward: {reward:+.2f}")

        # Controller
        btn = _parse_button(action)
        self._gb.highlight(btn)
        self._gb.show_action_label(action)

        # Thought box
        self._thought_box.config(state=tk.NORMAL)
        self._thought_box.delete("1.0", tk.END)
        self._thought_box.insert(tk.END, thought or "(no thought)")
        self._thought_box.config(state=tk.DISABLED)

        # History
        short_t = (thought[:160] + "…") if len(thought) > 160 else thought
        self._append(f"S{step:04d} [{ts}]  {action}\n", "header")
        if short_t:
            self._append(f"  → {short_t}\n", "thought")

    def _append(self, text: str, tag: str = "") -> None:
        self._history.config(state=tk.NORMAL)
        if tag:
            self._history.insert(tk.END, text, tag)
        else:
            self._history.insert(tk.END, text)
        self._history.see(tk.END)
        self._history.config(state=tk.DISABLED)
