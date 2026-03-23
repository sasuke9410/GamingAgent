"""
tools/log_window.py

Real-time agent log window with wireframe button controller visualizer.
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
WIN_W = 720
WIN_H = 1000
CTRL_W = 700   # controller canvas width
CTRL_H = 320   # controller canvas height (320 for GBA L/R buttons)

# ── Palette ───────────────────────────────────────────────────────────────────
BG           = "#1a1b26"   # window background
PANEL_BG     = "#24253a"   # panel background
BORDER_COL   = "#414868"   # separator / border

# Wireframe button colors
WF_OUTLINE   = "#4a5568"   # normal outline color
WF_FILL      = "#1e2030"   # normal fill (nearly-transparent)
WF_TEXT      = "#7a8aaa"   # label text in normal state

DPAD_PRESS   = "#ffe033"   # D-pad pressed fill
DPAD_TEXT_P  = "#1a1b26"   # D-pad pressed label

AB_PRESS_A   = "#ff3344"   # A button pressed fill
AB_PRESS_B   = "#ff8844"   # B button pressed fill
AB_TEXT_P    = "#ffffff"

SS_PRESS     = "#8080ff"   # Start/Select pressed fill
SS_TEXT_P    = "#ffffff"

LR_PRESS     = "#44aaff"   # L/R shoulder button pressed fill

FG_DEFAULT   = "#c0caf5"
FG_ACCENT    = "#7aa2f7"
FG_ACTION    = "#9ece6a"
FG_THOUGHT   = "#e0af68"

FONT_UI      = ("Consolas", 12)
FONT_LABEL   = ("Consolas", 11, "bold")
FONT_HEADER  = ("Consolas", 14, "bold")
FONT_THOUGHT = ("Consolas", 13)
FONT_BTN     = ("Helvetica", 12, "bold")


# ── Helper ────────────────────────────────────────────────────────────────────

def _parse_button(action_str: str) -> str | None:
    """Extract button name from '(a, 1)' or 'a' or 'up' etc."""
    if not action_str:
        return None
    m = re.match(r'\(?(\w+)', action_str.strip())
    return m.group(1).lower() if m else None


def _rounded_rect(canvas, x0, y0, x1, y1, r=8, **kwargs) -> int:
    """Draw a rounded rectangle polygon; returns the canvas item id."""
    pts = [
        x0+r, y0,   x1-r, y0,
        x1,   y0+r, x1,   y1-r,
        x1-r, y1,   x0+r, y1,
        x0,   y1-r, x0,   y0+r,
    ]
    return canvas.create_polygon(pts, smooth=True, **kwargs)


# ── Wireframe controller widget ───────────────────────────────────────────────

# GBAモードを使うゲーム名のセット
GBA_GAMES = {"ace_attorney", "super_mario_bros"}


class GameBoyWidget:
    """
    Minimal wireframe controller: D-pad, A, B, START, SELECT.
    GBAモード時はLボタン・Rボタンも表示し、ラベルを日本語化する。
    Buttons are outlines only at rest; fill with accent color on press.
    Call highlight(button) to flash a button.
    """

    def __init__(self, parent, game_mode: str = "gb"):
        self.game_mode = game_mode
        self.canvas = tk.Canvas(
            parent,
            width=CTRL_W, height=CTRL_H,
            bg=BG, bd=0, highlightthickness=0
        )
        self.canvas.pack(pady=4)

        # button tag → list of canvas item ids
        self._btn_items:  dict[str, list[int]] = {}
        # button tag → (normal_fill, pressed_fill, normal_text, pressed_text)
        self._btn_colors: dict[str, tuple[str, str, str, str]] = {}
        # button tag → list of text item ids
        self._btn_texts:  dict[str, list[int]] = {}

        self._action_text_id: int = 0
        self._draw()

    # ── Public ────────────────────────────────────────────────────────────────

    def highlight(self, button: str | None) -> None:
        """Flash button for BUTTON_FLASH_MS ms."""
        if not button:
            return
        tag = button.lower()
        if tag not in self._btn_items:
            return
        nf, pf, nt, pt = self._btn_colors[tag]
        for item in self._btn_items[tag]:
            self.canvas.itemconfig(item, fill=pf, outline=pf)
        for item in self._btn_texts.get(tag, []):
            self.canvas.itemconfig(item, fill=pt)
        self.canvas.after(BUTTON_FLASH_MS, lambda: self._restore(tag))

    def show_action_label(self, action_str: str) -> None:
        self.canvas.itemconfig(self._action_text_id, text=action_str)

    # ── Private ───────────────────────────────────────────────────────────────

    def _restore(self, tag: str) -> None:
        if tag not in self._btn_items:
            return
        nf, pf, nt, pt = self._btn_colors[tag]
        for item in self._btn_items[tag]:
            self.canvas.itemconfig(item, fill=nf, outline=WF_OUTLINE)
        for item in self._btn_texts.get(tag, []):
            self.canvas.itemconfig(item, fill=nt)

    def _register(self, tag: str, shape_ids: list[int], text_ids: list[int],
                  pressed_fill: str, pressed_text: str = AB_TEXT_P) -> None:
        self._btn_items[tag] = shape_ids
        self._btn_texts[tag] = text_ids
        self._btn_colors[tag] = (WF_FILL, pressed_fill, WF_TEXT, pressed_text)

    def _draw(self) -> None:
        c = self.canvas
        is_gba = (self.game_mode == "gba")

        # ── Layout constants ─────────────────────────────────────────────────
        # GBAモード: LRボタン用に上部50pxを追加
        y_offset = 50 if is_gba else 0

        dpx, dpy = 175, 145 + y_offset   # D-pad center
        arm_hw = 28           # D-pad arm half-width (square arms)
        arm_len = 32          # D-pad arm length from center

        # ── Section label ────────────────────────────────────────────────────
        label_ctrl = "コントローラー" if is_gba else "CONTROLLER"
        c.create_text(CTRL_W // 2, 18 + y_offset, text=label_ctrl,
                      fill=BORDER_COL, font=("Consolas", 11, "bold"), anchor="center")

        # ── GBA: L / R shoulder buttons ──────────────────────────────────────
        if is_gba:
            c.create_text(CTRL_W // 2, 18, text="Lボタン / Rボタン",
                          fill=BORDER_COL, font=("Consolas", 10), anchor="center")

            def _shoulder_btn(tag, cx, cy, label):
                pw, ph = 80, 26
                pill = _rounded_rect(c, cx-pw//2, cy-ph//2, cx+pw//2, cy+ph//2,
                                     r=10, fill=WF_FILL, outline=WF_OUTLINE, width=2)
                txt = c.create_text(cx, cy, text=label, fill=WF_TEXT,
                                    font=("Consolas", 12, "bold"))
                self._register(tag, [pill], [txt], LR_PRESS, AB_TEXT_P)

            _shoulder_btn("l", 100, 36, "L")
            _shoulder_btn("r", 600, 36, "R")

        # ── D-pad ────────────────────────────────────────────────────────────
        label_dpad = "十字キー" if is_gba else "D-PAD"
        c.create_text(dpx, 36 + y_offset, text=label_dpad, fill=BORDER_COL,
                      font=("Consolas", 10), anchor="center")

        def _dpad_arm(tag, dx, dy, label):
            x0 = dpx + dx * arm_len - arm_hw
            y0 = dpy + dy * arm_len - arm_hw
            x1 = dpx + dx * arm_len + arm_hw
            y1 = dpy + dy * arm_len + arm_hw
            rect = _rounded_rect(c, x0, y0, x1, y1, r=5,
                                  fill=WF_FILL, outline=WF_OUTLINE, width=2)
            txt = c.create_text((x0+x1)//2, (y0+y1)//2,
                                 text=label, fill=WF_TEXT, font=FONT_BTN)
            self._register(tag, [rect], [txt], DPAD_PRESS, DPAD_TEXT_P)

        _dpad_arm("up",    0, -1, "▲")
        _dpad_arm("down",  0,  1, "▼")
        _dpad_arm("left", -1,  0, "◀")
        _dpad_arm("right", 1,  0, "▶")

        # D-pad center square (decoration, not interactive)
        c.create_rectangle(
            dpx - arm_hw, dpy - arm_hw,
            dpx + arm_hw, dpy + arm_hw,
            fill="#252638", outline=WF_OUTLINE, width=1
        )

        # ── A / B buttons ────────────────────────────────────────────────────
        r_ab = 30   # button radius
        # B: left-lower, A: right-upper (standard Game Boy layout)
        bx_b, by_b = 460, 155 + y_offset
        bx_a, by_a = 545, 120 + y_offset

        label_ab = "Aボタン / Bボタン" if is_gba else "A / B"
        c.create_text((bx_b + bx_a) // 2, 36 + y_offset, text=label_ab,
                      fill=BORDER_COL, font=("Consolas", 10), anchor="center")

        def _circle_btn(tag, cx, cy, label, pressed_color):
            oval = c.create_oval(cx-r_ab, cy-r_ab, cx+r_ab, cy+r_ab,
                                  fill=WF_FILL, outline=WF_OUTLINE, width=2)
            txt = c.create_text(cx, cy, text=label, fill=WF_TEXT, font=FONT_BTN)
            self._register(tag, [oval], [txt], pressed_color, AB_TEXT_P)

        _circle_btn("b", bx_b, by_b, "B", AB_PRESS_B)
        _circle_btn("a", bx_a, by_a, "A", AB_PRESS_A)

        # ── START / SELECT ────────────────────────────────────────────────────
        label_ss = "スタートボタン / セレクトボタン" if is_gba else "START / SELECT"
        c.create_text(CTRL_W // 2, 228 + y_offset, text=label_ss,
                      fill=BORDER_COL, font=("Consolas", 10), anchor="center")

        def _pill_btn(tag, cx, cy, label):
            pw, ph = 72, 22
            pill = _rounded_rect(c, cx-pw//2, cy-ph//2, cx+pw//2, cy+ph//2,
                                   r=8, fill=WF_FILL, outline=WF_OUTLINE, width=2)
            txt = c.create_text(cx, cy, text=label, fill=WF_TEXT,
                                 font=("Consolas", 11, "bold"))
            self._register(tag, [pill], [txt], SS_PRESS, SS_TEXT_P)

        _pill_btn("select", 270, 252 + y_offset, "SELECT")
        _pill_btn("start",  430, 252 + y_offset, "START")

        # ── Action label ─────────────────────────────────────────────────────
        self._action_text_id = c.create_text(
            CTRL_W // 2, CTRL_H - 12,
            text="", fill=FG_ACTION,
            font=("Consolas", 13, "bold"), anchor="center"
        )


# ── Main log window ───────────────────────────────────────────────────────────

class LogWindow:
    """
    Thread-safe real-time log window with wireframe controller visualizer.

    Usage (from main thread):
        win = LogWindow()
        win.start()
        win.log_step(step=1, elapsed_s=5.2, action="(a, 1)",
                     thought="...", game_state="...")
        win.close()
    """

    def __init__(self, title="Agent Log", x_offset=520, y_offset=0, game_name: str = ""):
        self._q: queue.Queue = queue.Queue()
        self._title    = title
        self._x_offset = x_offset
        self._y_offset = y_offset
        self._game_mode = "gba" if game_name in GBA_GAMES else "gb"
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

        self._sv_step   = tk.StringVar(value="ステップ: —")
        self._sv_time   = tk.StringVar(value="—")
        self._sv_reward = tk.StringVar(value="報酬: —")

        tk.Label(bar, textvariable=self._sv_step,   bg=PANEL_BG, fg=FG_ACCENT,
                 font=FONT_HEADER, width=14, anchor="w").pack(side=tk.LEFT, padx=8)
        tk.Label(bar, textvariable=self._sv_time,   bg=PANEL_BG, fg=FG_DEFAULT,
                 font=FONT_UI).pack(side=tk.LEFT, padx=4)
        tk.Label(bar, textvariable=self._sv_reward, bg=PANEL_BG, fg=FG_ACTION,
                 font=FONT_UI).pack(side=tk.RIGHT, padx=8)

        tk.Frame(root, bg=BORDER_COL, height=1).pack(fill=tk.X, padx=6, pady=2)

        # ── Wireframe controller ─────────────────────────────────────────────
        ctrl_frame = tk.Frame(root, bg=BG)
        ctrl_frame.pack(fill=tk.X, padx=6)
        self._gb = GameBoyWidget(ctrl_frame, game_mode=self._game_mode)

        tk.Frame(root, bg=BORDER_COL, height=1).pack(fill=tk.X, padx=6, pady=2)

        # ── Thought panel ────────────────────────────────────────────────────
        thought_frame = tk.Frame(root, bg=PANEL_BG)
        thought_frame.pack(fill=tk.X, padx=6, pady=2)
        tk.Label(thought_frame, text="思考プロセス", bg=PANEL_BG, fg=FG_ACCENT,
                 font=FONT_LABEL).pack(anchor="w", padx=6, pady=(4, 0))
        self._thought_box = tk.Text(
            thought_frame, bg="#1f2035", fg=FG_THOUGHT, font=FONT_THOUGHT,
            height=7, wrap=tk.WORD, relief=tk.FLAT, bd=0,
            padx=6, pady=4,
        )
        self._thought_box.pack(fill=tk.X, padx=4, pady=(2, 6))
        self._thought_box.config(state=tk.DISABLED)

        tk.Frame(root, bg=BORDER_COL, height=1).pack(fill=tk.X, padx=6, pady=2)

        # ── History ──────────────────────────────────────────────────────────
        tk.Label(root, text="履歴", bg=BG, fg=FG_ACCENT,
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
                try:
                    self._root.after_cancel(self._after_id)
                except Exception:
                    pass
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
        step    = msg["step"]
        elapsed = msg["elapsed_s"]
        action  = msg["action"]
        thought = msg["thought"]
        reward  = msg["reward"]
        ts      = msg["ts"]

        # Status bar
        mins, secs = divmod(int(elapsed), 60)
        self._sv_step.set(f"ステップ: {step}")
        self._sv_time.set(f"{mins:02d}:{secs:02d}  [{ts}]")
        self._sv_reward.set(f"報酬: {reward:+.2f}")

        # Controller
        btn = _parse_button(action)
        self._gb.highlight(btn)
        self._gb.show_action_label(action)

        # Thought box
        self._thought_box.config(state=tk.NORMAL)
        self._thought_box.delete("1.0", tk.END)
        self._thought_box.insert(tk.END, thought or "(思考なし)")
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
