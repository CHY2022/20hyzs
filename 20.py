# -*- coding: utf-8 -*-
"""
20护眼小助手 v1.0 py：一哥陳
"""

import tkinter as tk
from tkinter import messagebox, ttk
import time
import threading
import io
import os
import sys
import json
import queue
import webbrowser
from urllib.parse import urljoin
from datetime import datetime, timedelta

# ==================== 可选依赖 ====================
try:
    from pynput import keyboard, mouse
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False
    print("提示: 未安装 pynput。请运行: pip install pynput")

try:
    import pystray
    from PIL import Image, ImageTk, ImageDraw
    HAS_TRAY = True
except ImportError:
    HAS_TRAY = False
    print("提示: 未安装 pystray/Pillow。请运行: pip install pystray Pillow")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("提示: 未安装 requests。请运行: pip install requests")

try:
    import pywinstyles
    HAS_WIN11 = True
except ImportError:
    HAS_WIN11 = False

try:
    import win_magnification as mag
    HAS_MAG = True
except ImportError:
    HAS_MAG = False


# ==================== 路径与配置 ====================
def get_resource_path(relative):
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


def get_user_data_path(filename):
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, filename)


CONFIG_FILE = get_user_data_path("eye_config.json")
STATS_FILE = get_user_data_path("eye_stats.json")
ICON_FILE = get_resource_path("favicon.ico")

DEFAULT_CONFIG = {
    "lock_idle_min": 5,
    "pause_idle_min": 2,
    "theme": "浅色",
    "opacity": 0.95,
    "autostart": False,
    "eye_mode": "原色",
    "blue_light_on": False,
    "blue_light_strength": 50,
    "tint_color": "淡黄",
    "eye_schedule_enabled": False,
    "eye_schedule_start": "20:00",
    "eye_schedule_end": "07:00",
}

TINT_COLORS = {
    "淡黄":   (255, 255, 220),
    "暖黄":   (255, 240, 200),
    "护眼绿": (200, 255, 200),
    "暖橙色": (255, 220, 180),
    "橙色":   (255, 200, 150),
    "薄荷绿": (200, 255, 230),
}

FONT_MAIN = "Microsoft YaHei"

HELP_TEXT = """⭐20-20-20护眼法则是眼科领域普遍推荐、操作门槛极低的间歇用眼护眼方法，核心作用是快速缓解长时间近距离用眼带来的视疲劳。

💡 具体操作方法
核心操作标准：每连续近距离用眼20分钟，抬头看向20英尺（约6米）以外的远处物体，至少停留观看20秒。
执行灵活度要求：不需要严格掐秒表精准计时，日常用眼过程中建立定时远眺的意识即可，比如学生写作业40分钟左右起身去窗边望一望，也符合该法则的护眼逻辑。
操作注意细节：远眺时不要只是闭眼休息，直接看窗外远处的树、楼房等物体，睫状肌放松的效果会比闭眼好很多。

🎓 背后的科学依据
①缓解睫状肌紧张：人长时间盯着近处物体时，眼部的睫状肌会一直处于收紧状态，时间久了就会僵硬酸痛，看向6米外的远处时，睫状肌会自然切换到完全放松的状态，相当于给眼睛做了一次短暂的拉伸运动。
②改善干眼问题：人在专注近距离用眼时，眨眼次数会从正常的每分钟15-20次大幅减少，容易导致泪膜破裂引发干眼症，定时远眺的动作可以强制打断专注状态，提醒人恢复正常眨眼频率，让泪液重新均匀涂抹在眼球表面。
③降低眼部调节负担：搭配视线向下倾斜30-45度的读写姿势，远眺动作还能帮助扩大眼睑覆盖眼球的面积，减慢泪液蒸发速度，进一步减少眼部干涩不适。

🏟️ 适用场景和实际效果
覆盖全场景近距离用眼：不仅适合长时间盯电脑屏幕的上班族，也适合长时间看书、画画、写作业的学生群体，所有需要连续近距离用眼的场景都可以使用该法则。
实际使用效果：该法则简单易执行，不需要额外复杂设备，坚持使用可以有效缓解视疲劳，降低长时间用眼带来的眼部酸胀、干涩、异物感等不适症状。
使用边界说明：它只是日常护眼的辅助技巧，并不是治愈眼病的灵丹妙药，也不能抵消长期不良用眼习惯带来的伤害，如果出现视力突然下降、视野缺损、剧烈眼痛等症状，必须第一时间前往正规医院眼科就诊。
特殊人群适配：学龄儿童使用该法则时，建议搭配每天累计2小时的日间户外活动，非学习目的的屏幕时间每天尽量控制在2小时以内，护眼效果会更好。

👁️ 核心原理
①放松睫状肌：看近处时睫状肌持续收缩，像手臂一直举着会酸。远眺6米外时，眼睛接近“无限远”状态，睫状肌几乎不用发力，得以松弛。
②恢复眨眼频率：盯着屏幕时眨眼次数会不自觉减少一半以上，导致泪膜蒸发过快、眼干。远眺时眨眼恢复，泪液重新均匀覆盖眼球表面。
③中断调节痉挛：长时间近距离用眼可能引发调节痉挛（假性近视），20秒的远眺能在疲劳累积前打断这一过程。

📋 权威认可与效果
该法则已获美国验光协会（AOA）和美国眼科学会（AAO）推荐，也纳入国家卫生健康委《近视防治指南（2024年版）》相关建议，是国内外广泛认可的护眼行为干预方法。

⚠️ 需要说明的边界
证据并非绝对一致：2026年一项针对30名年轻受试者的研究显示，每5、10或20分钟做一次20秒休息，在主观症状和阅读速度上未观察到显著改善，说明“最佳休息间隔和时长”仍需更多高质量研究验证。
不能治疗近视：该法则主要预防和缓解视疲劳，对已经形成的真性近视（眼轴变长）无逆转作用。
执行要点：远眺时要真正看向6米以外，持续至少20秒，只抬头看几秒效果会大打折扣。
"""


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            for k, v in DEFAULT_CONFIG.items():
                cfg.setdefault(k, v)
            return cfg
        except Exception:
            pass
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("配置保存失败:", e)


def load_stats():
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "records" in data:
                return data
        except Exception:
            pass
    return {"records": []}


def save_stats(data):
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("统计保存失败:", e)


# ==================== 滚动数字时钟 ====================
class ScrollClock(tk.Frame):
    DIGIT_W = 34
    DIGIT_H = 56
    FONT = ("Segoe UI", 36, "bold")
    GAP = 2

    def __init__(self, parent, text="20:00", bg="#1e1e1e", fg="#00d4ff", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.BG = bg
        self.COLOR = fg
        self._digits = []
        self._current = []
        self._animating = []
        self._build_columns(text)

    def _build_columns(self, text):
        for w in self.winfo_children():
            w.destroy()
        self._digits.clear()
        self._current.clear()
        self._animating.clear()
        for ch in text:
            if ch == ":":
                lbl = tk.Label(self, text=":", font=self.FONT,
                               fg=self.COLOR, bg=self.BG, width=1)
                lbl.pack(side=tk.LEFT)
                self._digits.append(None)
                self._current.append(":")
                self._animating.append(False)
            else:
                c = tk.Canvas(self, width=self.DIGIT_W, height=self.DIGIT_H,
                              bg=self.BG, highlightthickness=0)
                c.pack(side=tk.LEFT, padx=self.GAP)
                self._draw_digit(c, ch, 0)
                self._digits.append(c)
                self._current.append(ch)
                self._animating.append(False)

    def _draw_digit(self, canvas, char, offset_y):
        canvas.delete("all")
        canvas.create_text(self.DIGIT_W // 2, self.DIGIT_H // 2 + offset_y,
                           text=char, font=self.FONT, fill=self.COLOR)

    def set_text(self, text, animate=True):
        if len(text) != len(self._current):
            self._build_columns(text)
            return
        for i, (new_ch, old_ch) in enumerate(zip(text, self._current)):
            if new_ch == old_ch or self._digits[i] is None:
                continue
            if new_ch == ":" or old_ch == ":":
                continue
            self._current[i] = new_ch
            if animate:
                self._animate_digit(i, old_ch, new_ch)
            else:
                self._draw_digit(self._digits[i], new_ch, 0)

    def _animate_digit(self, idx, old_ch, new_ch):
        if self._animating[idx]:
            self._draw_digit(self._digits[idx], new_ch, 0)
            self._animating[idx] = False
            return
        self._animating[idx] = True
        canvas = self._digits[idx]
        steps = 6
        step_h = self.DIGIT_H // steps

        def frame(step):
            if not canvas.winfo_exists():
                return
            canvas.delete("all")
            offset = -step * step_h
            canvas.create_text(self.DIGIT_W // 2, self.DIGIT_H // 2 + offset,
                               text=old_ch, font=self.FONT, fill=self.COLOR)
            canvas.create_text(self.DIGIT_W // 2,
                               self.DIGIT_H // 2 + offset + self.DIGIT_H,
                               text=new_ch, font=self.FONT, fill=self.COLOR)
            if step < steps:
                canvas.after(16, lambda: frame(step + 1))
            else:
                self._draw_digit(canvas, new_ch, 0)
                self._animating[idx] = False
        frame(1)

    def set_colors(self, bg, fg):
        self.BG = bg
        self.COLOR = fg
        self.config(bg=bg)
        for w in self.winfo_children():
            if isinstance(w, tk.Canvas):
                w.config(bg=bg)
            elif isinstance(w, tk.Label):
                w.config(bg=bg, fg=fg)
        for i, ch in enumerate(self._current):
            if self._digits[i] is not None:
                self._draw_digit(self._digits[i], ch, 0)


# ==================== 主程序 ====================
class EyeCareApp:
    def __init__(self):
        self.config = load_config()
        self.stats = load_stats()
        self.root = tk.Tk()
        self.root.title("20护眼小助手 v1.0 py:一哥陳")
        
        # 核心修复：取消固定高度，改用自适应
        self.root.geometry("490x480")
        self.root.resizable(False, False)

        self.load_window_icon()

        # 状态
        self.work_seconds = 20 * 60
        self.remaining = self.work_seconds
        self.running = True
        self.resting = False
        self.idle_mode = False
        self.work_paused = False
        self.manual_paused = False
        self._hiding_to_tray = False
        self._drag_active = False
        self._work_timer_active = False
        self._last_state = "normal"

        # 休息
        self.rest_remaining = 20
        self.last_input_time = time.time()
        self.rest_timer = None

        # 空闲
        self.idle_check_timer = None

        # 锁屏
        self.wallpaper_urls = []
        self.wallpaper_index = 0
        self.wallpaper_timer = None
        self.lock_window = None
        self.leave_start_time = None

        # 统计会话
        self.work_session_start = None
        self.rest_session_start = None

        # 监听
        self.kb_listener = None
        self.mouse_listener = None

        # 托盘
        self.tray_icon = None
        self.ui_queue = queue.Queue()

        # 窗口
        self.settings_win = None
        self.stats_win = None
        self.help_win = None
        self.about_win = None
        self.float_window = None
        self.float_clock = None

        # 计算颜色变量并保存
        self._calculate_colors()
        
        self.build_ui()

        self.root.after(100, self.apply_win11_style)
        self.start_work_timer()
        self.setup_background_services()

        self.root.after(3000, self.apply_eye_filter)
        self.root.after(10000, self._schedule_check_loop)
        self.root.after(200, self._process_ui_queue)
        self.root.after(500, self._poll_window_state)

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def _calculate_colors(self):
        """根据当前主题计算所有颜色，确保字体与背景对比度清晰"""
        theme = self.config.get("theme", "浅色")
        
        # 基础默认（浅色）
        self.theme_bg = "#f3f3f3"
        self.card_bg = "#ffffff"
        self.theme_fg = "#1a1a1a"  # 深色字体
        self.sub_fg = "#666666"
        self.hover_bg = "#eef2f7"

        if theme == "深色":
            self.theme_bg = "#202124"
            self.card_bg = "#2a2d31"
            self.theme_fg = "#f0f0f0"  # 浅色字体
            self.sub_fg = "#aaaaaa"
            self.hover_bg = "#35393f"
        elif theme == "浅蓝色":
            self.theme_bg = "#e3f2fd"
            self.card_bg = "#ffffff"
            self.theme_fg = "#0d47a1"
            self.sub_fg = "#5c6bc0"
            self.hover_bg = "#bbdefb"
        elif theme == "浅绿色":
            self.theme_bg = "#e8f5e9"
            self.card_bg = "#ffffff"
            self.theme_fg = "#1b5e20"
            self.sub_fg = "#4caf50"
            self.hover_bg = "#c8e6c9"
        elif theme == "淡黄色":
            self.theme_bg = "#fffde7"
            self.card_bg = "#ffffff"
            self.theme_fg = "#f57f17"
            self.sub_fg = "#fbc02d"
            self.hover_bg = "#fff9c4"
        elif theme == "淡粉色":
            self.theme_bg = "#fce4ec"
            self.card_bg = "#ffffff"
            self.theme_fg = "#880e4f"
            self.sub_fg = "#f06292"
            self.hover_bg = "#f8bbd0"
        elif theme == "淡橙色":
            self.theme_bg = "#fff3e0"
            self.card_bg = "#ffffff"
            self.theme_fg = "#e65100"
            self.sub_fg = "#ff9800"
            self.hover_bg = "#ffe0b2"

    def _clock_fg(self):
        return "#00d4ff" if self.config.get("theme") == "深色" else "#0a84ff"

    def load_window_icon(self):
        if os.path.exists(ICON_FILE):
            try:
                self.root.iconbitmap(ICON_FILE)
            except Exception:
                pass

    def apply_win11_style(self):
        theme = self.config.get("theme", "浅色")
        style_map = {
            "深色": "dark",
            "浅色": "normal",
            "浅蓝色": "normal",
            "浅绿色": "normal",
            "淡黄色": "normal",
            "淡粉色": "normal",
            "淡橙色": "normal"
        }

        if HAS_WIN11:
            try:
                style = style_map.get(theme, "normal")
                done = threading.Event()

                def _apply():
                    try:
                        pywinstyles.apply_style(self.root, style)
                    except Exception:
                        pass
                    finally:
                        done.set()

                threading.Thread(target=_apply, daemon=True).start()
                done.wait(timeout=1.5)
            except Exception:
                pass

        self.root.config(bg=self.theme_bg)
        try:
            alpha = max(0.5, min(1.0, float(self.config.get("opacity", 0.95))))
            self.root.attributes("-alpha", alpha)
        except Exception:
            pass

    # ================= 主界面 =================
    def build_ui(self):
        header = tk.Frame(self.root, bg=self.theme_bg)
        header.pack(fill="x", padx=24, pady=(18, 0))
        tk.Label(header, text="20 护眼小助手", font=(FONT_MAIN, 12, "bold"),
                 bg=self.theme_bg, fg=self.theme_fg).pack(side=tk.LEFT)
        tk.Label(header, text="v1.0", font=(FONT_MAIN, 9),
                 bg=self.theme_bg, fg=self.sub_fg).pack(side=tk.LEFT, padx=6)

        card = tk.Frame(self.root, bg=self.card_bg, bd=0,
                        highlightthickness=1,
                        highlightbackground="#d0d0d0" if self.config.get("theme") != "深色" else "#3a3d42")
        card.pack(fill="x", padx=24, pady=10)

        self.status_label = tk.Label(
            card, text="工作中", font=(FONT_MAIN, 13),
            bg=self.card_bg, fg=self.theme_fg)
        self.status_label.pack(pady=(14, 4))

        self.clock = ScrollClock(card, text="20:00",
                                 bg=self.card_bg, fg=self._clock_fg())
        self.clock.pack(pady=6)

        self.sub_label = tk.Label(
            card, text="", font=(FONT_MAIN, 9),
            bg=self.card_bg, fg=self.sub_fg)
        self.sub_label.pack(pady=(0, 14))

        # 功能按钮区
        func_frame = tk.Frame(self.root, bg=self.theme_bg)
        func_frame.pack(fill="x", padx=24, pady=(4, 0))

        self.pause_btn = self._make_button(func_frame, "⏸ 暂停", self.toggle_manual_pause, False)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.leave_btn = self._make_button(func_frame, "🚪 离开一会", self.enter_leave_mode, False)
        self.leave_btn.pack(side=tk.LEFT, padx=6)

        self.stats_btn = self._make_button(func_frame, "📊 统计", self.open_stats, False)
        self.stats_btn.pack(side=tk.LEFT, padx=6)

        self.tray_btn = self._make_button(func_frame, "最小化到托盘", self.hide_to_tray, True)
        self.tray_btn.pack(side=tk.RIGHT, padx=(6, 0))

        # 底部说明
        bottom = tk.Frame(self.root, bg=self.theme_bg)
        bottom.pack(fill="x", padx=24, pady=(14, 16))

        explain = tk.Frame(bottom, bg=self.theme_bg)
        explain.pack(fill="x")
        tk.Label(
            explain,
            text="20-20-20护眼法则：每连续近距离用眼20分钟，抬头看向20英尺（约6米）以外的远处物体，至少停留观看20秒。",
            font=(FONT_MAIN, 8), bg=self.theme_bg, fg=self.sub_fg,
            justify="left", wraplength=340, anchor="w"
        ).pack(side=tk.LEFT, fill="x", expand=True)

        link = tk.Label(
            explain, text="详情", font=(FONT_MAIN, 8, "underline"),
            bg=self.theme_bg, fg="#0a84ff", cursor="hand2")
        link.pack(side=tk.LEFT, padx=(4, 0))
        link.bind("<Button-1>", lambda e: webbrowser.open(
            "https://www.baidu.com/s?wd=20-20-20护眼法则"))

        self._header = header
        self._header_label = header.winfo_children()[0]
        self._header_ver = header.winfo_children()[1]
        self._card = card
        self._func_frame = func_frame
        self._bottom = bottom
        self._explain = explain
        self._link = link

        self.update_work_display()

    def _make_button(self, parent, text, command, primary=False):
        bg = "#0a84ff" if primary else self.card_bg
        fg = "white" if primary else self.theme_fg
        btn = tk.Button(
            parent, text=text, command=command,
            font=(FONT_MAIN, 9), bg=bg, fg=fg,
            activebackground="#0066cc" if primary else self.hover_bg,
            activeforeground=fg, bd=0, relief="flat",
            padx=10, pady=7, cursor="hand2", width=10
        )
        return btn

    def update_work_display(self):
        if self.resting or self.idle_mode:
            return
        m, s = divmod(self.remaining, 60)
        time_str = f"{m:02d}:{s:02d}"
        
        if self.manual_paused:
            self.status_label.config(text="已手动暂停")
        else:
            self.status_label.config(text="工作中")
            
        self.clock.set_text(time_str)
        
        if self.float_clock and self.float_window and self.float_window.winfo_exists():
            self.float_clock.set_text(time_str)
            
        if self.manual_paused:
            self.sub_label.config(text="手动暂停中，点击「继续」恢复")
            self.pause_btn.config(text="▶ 继续")
        elif self.work_paused:
            self.sub_label.config(text="已空闲，工作计时已暂停")
        else:
            self.sub_label.config(text="每连续用眼 20 分钟，将强制休息 20 秒")
            self.pause_btn.config(text="⏸ 暂停")

    # ================= 手动暂停 / 继续 =================
    def toggle_manual_pause(self):
        if self.resting or self.idle_mode:
            return
        self.manual_paused = not self.manual_paused
        if self.manual_paused:
            self._end_work_session()
        else:
            self._start_work_session()
        self.update_work_display()

    # ================= 工作 / 休息 =================
    def start_work_timer(self):
        if self.resting or self.idle_mode or not self.running:
            return
        if self._work_timer_active:
            return
        self._work_timer_active = True
        self.root.after(1000, self._work_tick)

    def _work_tick(self):
        self._work_timer_active = False
        if not self.running or self.resting or self.idle_mode:
            return
        if self.work_paused or self.manual_paused:
            self.start_work_timer()
            return
        if self.remaining > 0:
            if self.remaining == self.work_seconds:
                self._start_work_session()
            self.remaining -= 1
            self.update_work_display()
            self.start_work_timer()
        else:
            self._end_work_session()
            self.start_rest()

    def start_rest(self):
        if self.idle_mode:
            return
        self.resting = True
        self.rest_remaining = 20
        self.rest_session_start = time.time()
        self.last_input_time = time.time()
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.config(bg="black")
        self.status_label.config(
            text="每近距离用眼20分钟，请远眺 20 英尺（约 6 米）外的物体\n至少 20 秒",
            bg="black", fg="white", font=(FONT_MAIN, 20))
        self.clock.set_colors(bg="black", fg="#00ff88")
        self.sub_label.config(bg="black", fg="lightgray", font=(FONT_MAIN, 13))
        self._func_frame.pack_forget()
        self._bottom.pack_forget()
        self.start_input_listeners()
        self.update_rest_display()
        self.rest_timer = self.root.after(1000, self.rest_countdown)

    def update_rest_display(self):
        self.clock.set_text(f"00:{self.rest_remaining:02d}")
        hint = "休息中..."
        if self.rest_remaining < 20:
            hint = "检测到操作，已重新计时！"
        self.sub_label.config(text=hint, fg="orange")

    def rest_countdown(self):
        if not self.resting:
            return
        elapsed = time.time() - self.last_input_time
        remain = 20 - int(elapsed)
        if remain > 0:
            self.rest_remaining = remain
            self.update_rest_display()
            self.rest_timer = self.root.after(1000, self.rest_countdown)
        else:
            self.end_rest()

    def end_rest(self):
        if self.rest_session_start:
            self._add_stat("rest", self.rest_session_start, time.time())
            self.rest_session_start = None
        self.resting = False
        self.stop_input_listeners()
        self.root.attributes("-fullscreen", False)
        self.root.attributes("-topmost", False)
        self.root.geometry("490x480")
        self.root.config(bg=self.theme_bg)
        self.status_label.config(
            text="工作中", bg=self.card_bg, fg=self.theme_fg,
            font=(FONT_MAIN, 13))
        self.clock.set_colors(bg=self.card_bg, fg=self._clock_fg())
        self.sub_label.config(bg=self.card_bg, fg=self.sub_fg, font=(FONT_MAIN, 9))
        
        self._func_frame.pack(fill="x", padx=24, pady=(4, 0))
        self._bottom.pack(fill="x", padx=24, pady=(14, 16))
        
        self.remaining = self.work_seconds
        self.update_work_display()
        self._work_timer_active = False
        self.start_work_timer()
        self.last_input_time = time.time()
        self.start_idle_check()

    # ================= 会话记录 =================
    def _start_work_session(self):
        if self.work_session_start is None:
            self.work_session_start = time.time()

    def _end_work_session(self):
        if self.work_session_start:
            self._add_stat("work", self.work_session_start, time.time())
            self.work_session_start = None

    def _add_stat(self, kind, start, end):
        if end <= start:
            return
        try:
            self.stats.setdefault("records", []).append({
                "type": kind,
                "start": int(start),
                "end": int(end),
            })
            cutoff = time.time() - 90 * 86400
            self.stats["records"] = [
                r for r in self.stats["records"] if r.get("end", 0) > cutoff
            ]
            save_stats(self.stats)
        except Exception as e:
            print("统计记录失败:", e)

    # ================= 离开一会 =================
    def enter_leave_mode(self):
        if self.resting or self.idle_mode:
            return
        self._end_work_session()
        self.leave_start_time = time.time()
        self.root.withdraw()
        self.show_lock_screen(leave_mode=True)

    # ================= 键鼠监听 =================
    def start_input_listeners(self):
        if not HAS_PYNPUT:
            return
        self.stop_input_listeners()
        try:
            self.kb_listener = keyboard.Listener(on_press=self.on_any_input)
            self.mouse_listener = mouse.Listener(
                on_move=self.on_any_input,
                on_click=self.on_any_input,
                on_scroll=self.on_any_input)
            self.kb_listener.start()
            self.mouse_listener.start()
        except Exception as e:
            print("监听启动失败:", e)

    def stop_input_listeners(self):
        for listener in (self.kb_listener, self.mouse_listener):
            if listener:
                try:
                    listener.stop()
                except Exception:
                    pass
        self.kb_listener = None
        self.mouse_listener = None

    def on_any_input(self, *args, **kwargs):
        self.last_input_time = time.time()
        if self.work_paused and not self.resting and not self.idle_mode:
            self.work_paused = False
            self.root.after(0, self.update_work_display)

    # ================= 空闲检测 =================
    def start_idle_check(self):
        if self.idle_check_timer:
            try:
                self.root.after_cancel(self.idle_check_timer)
            except Exception:
                pass
        if not self.resting and not self.idle_mode and self.running:
            self.idle_check_timer = self.root.after(3000, self.check_idle)

    def check_idle(self):
        if self.resting or self.idle_mode or not self.running:
            return
        idle_sec = time.time() - self.last_input_time
        lock_threshold = int(self.config.get("lock_idle_min", 5)) * 60
        pause_threshold = int(self.config.get("pause_idle_min", 2)) * 60
        if idle_sec > lock_threshold:
            self.prompt_idle_mode()
            return
        elif idle_sec > pause_threshold:
            if not self.work_paused:
                self.work_paused = True
                self._end_work_session()
                self.update_work_display()
        else:
            if self.work_paused:
                self.work_paused = False
                self.update_work_display()
        self.idle_check_timer = self.root.after(3000, self.check_idle)

    # ================= 待机 / 锁屏 =================
    def prompt_idle_mode(self):
        self.idle_prompt = tk.Toplevel(self.root)
        self.idle_prompt.title("待机确认")
        self.idle_prompt.geometry("340x170")
        self.idle_prompt.attributes("-topmost", True)
        self.idle_prompt.resizable(False, False)
        self.idle_prompt.config(bg=self.theme_bg)
        
        if os.path.exists(ICON_FILE):
            try:
                self.idle_prompt.iconbitmap(ICON_FILE)
            except Exception:
                pass
                
        tk.Label(self.idle_prompt,
                 text="检测到长时间无操作，\n是否进入待机模式（锁屏轮播壁纸）？",
                 font=(FONT_MAIN, 11), bg=self.theme_bg,
                 fg=self.theme_fg, justify="center").pack(pady=24)
        btn_frame = tk.Frame(self.idle_prompt, bg=self.theme_bg)
        btn_frame.pack()
        tk.Button(btn_frame, text="是 (20s)", width=8,
                  command=lambda: self.enter_idle_mode(True)).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="否", width=8,
                  command=lambda: self.enter_idle_mode(False)).pack(side=tk.LEFT, padx=10)
        self.prompt_countdown = 20
        self.prompt_label = tk.Label(self.idle_prompt,
                                     text=f"剩余 {self.prompt_countdown} 秒自动进入",
                                     fg="gray", bg=self.theme_bg)
        self.prompt_label.pack(pady=6)
        self.update_prompt_countdown()

    def update_prompt_countdown(self):
        if not hasattr(self, "idle_prompt") or not self.idle_prompt.winfo_exists():
            return
        self.prompt_countdown -= 1
        if self.prompt_countdown <= 0:
            self.idle_prompt.destroy()
            self.enter_idle_mode(True)
        else:
            self.prompt_label.config(text=f"剩余 {self.prompt_countdown} 秒自动进入")
            self.root.after(1000, self.update_prompt_countdown)

    def enter_idle_mode(self, enter):
        if hasattr(self, "idle_prompt") and self.idle_prompt.winfo_exists():
            self.idle_prompt.destroy()
        if enter:
            self.idle_mode = True
            self._end_work_session()
            self.leave_start_time = time.time()
            self.stop_input_listeners()
            self.root.withdraw()
            self.show_lock_screen(leave_mode=False)
        else:
            self.last_input_time = time.time()
            self.start_idle_check()

    # ================= 锁屏壁纸 =================
    def fetch_bing_wallpapers(self):
        if not HAS_REQUESTS:
            return []
        urls = []
        try:
            api_url = ("https://cn.bing.com/HPImageArchive.aspx"
                       "?format=js&idx=0&n=8&mkt=zh-CN")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            r = requests.get(api_url, headers=headers, timeout=10)
            r.raise_for_status()
            for img in r.json().get("images", []):
                urls.append(urljoin("https://cn.bing.com", img["url"]))
        except Exception as e:
            print("获取必应壁纸失败:", e)
        return urls

    def show_lock_screen(self, leave_mode=False):
        self.lock_window = tk.Toplevel()
        self.lock_window.attributes("-fullscreen", True)
        self.lock_window.attributes("-topmost", True)
        self.lock_window.config(bg="black", cursor="none")
        self.lock_window.bind("<Escape>", lambda e: self.exit_lock_screen(leave_mode))
        self.lock_label = tk.Label(self.lock_window, bg="black")
        self.lock_label.pack(expand=True, fill="both")
        tk.Label(self.lock_window, text="按 ESC 退出",
                 fg="gray", bg="black", font=(FONT_MAIN, 10)
                 ).place(relx=0.5, rely=0.95, anchor="s")

        def fetch():
            urls = self.fetch_bing_wallpapers()
            if urls:
                self.wallpaper_urls = urls
                self.root.after(0, self.start_wallpaper_slideshow)
            else:
                self.root.after(0, lambda: self.lock_label.config(
                    text="无法加载壁纸\n请按 ESC 退出", fg="white"))

        threading.Thread(target=fetch, daemon=True).start()

    def start_wallpaper_slideshow(self):
        if self.wallpaper_urls:
            self.show_wallpaper(0)

    def show_wallpaper(self, index):
        if not self.lock_window or not self.lock_window.winfo_exists():
            return
        if not self.wallpaper_urls:
            return
        url = self.wallpaper_urls[index % len(self.wallpaper_urls)]
        try:
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            resp.raise_for_status()
            pil_img = Image.open(io.BytesIO(resp.content))
            sw = self.lock_window.winfo_screenwidth()
            sh = self.lock_window.winfo_screenheight()
            pil_img = pil_img.resize((sw, sh), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_img)
            self.lock_label.config(image=photo)
            self.lock_label.image = photo
            self.wallpaper_index = (index + 1) % len(self.wallpaper_urls)
        except Exception as e:
            print("加载壁纸失败:", e)
            self.lock_label.config(text="壁纸加载失败", fg="white")
        self.wallpaper_timer = self.lock_window.after(
            20000, lambda: self.show_wallpaper(self.wallpaper_index))

    def exit_lock_screen(self, leave_mode=False):
        if self.wallpaper_timer:
            try:
                self.lock_window.after_cancel(self.wallpaper_timer)
            except Exception:
                pass
        if self.lock_window:
            self.lock_window.destroy()
            self.lock_window = None

        if self.leave_start_time:
            kind = "leave" if leave_mode else "leave"
            self._add_stat(kind, self.leave_start_time, time.time())
            self.leave_start_time = None

        if leave_mode:
            self.idle_mode = False
            self.root.deiconify()
            self.last_input_time = time.time()
            self.start_input_listeners()
            self.start_idle_check()
            self.update_work_display()
            self._work_timer_active = False
            self.start_work_timer()
        else:
            self.exit_idle_mode()

    def exit_idle_mode(self):
        self.idle_mode = False
        self.root.deiconify()
        self.last_input_time = time.time()
        self.start_input_listeners()
        self.start_idle_check()
        self.update_work_display()
        self._work_timer_active = False
        self.start_work_timer()

    # ================= 护眼模式（异步） =================
    def apply_eye_filter(self):
        if not HAS_MAG:
            return
        snapshot = {
            "eye_mode": self.config.get("eye_mode", "原色"),
            "blue_light_on": self.config.get("blue_light_on", False),
            "blue_light_strength": int(self.config.get("blue_light_strength", 50)),
            "tint_color": self.config.get("tint_color", "淡黄"),
            "schedule_enabled": self.config.get("eye_schedule_enabled", False),
            "schedule_start": self.config.get("eye_schedule_start", "20:00"),
            "schedule_end": self.config.get("eye_schedule_end", "07:00"),
        }
        threading.Thread(target=self._apply_eye_filter_worker,
                         args=(snapshot,), daemon=True).start()

    def _apply_eye_filter_worker(self, cfg):
        try:
            mode = cfg["eye_mode"]
            blue_on = cfg["blue_light_on"]
            if cfg["schedule_enabled"] and not self._in_eye_schedule_static(
                    cfg["schedule_start"], cfg["schedule_end"]):
                mode = "原色"
                blue_on = False
            try:
                mag.initialize()
            except Exception:
                pass
            if mode == "原色" and not blue_on:
                identity = (1, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                            0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1)
                mag.set_fullscreen_color_effect(identity)
                return
            if mode == "黑白":
                gray = (0.299, 0.587, 0.114, 0, 0,
                        0.299, 0.587, 0.114, 0, 0,
                        0.299, 0.587, 0.114, 0, 0,
                        0, 0, 0, 1, 0, 0, 0, 0, 0, 1)
                mag.set_fullscreen_color_effect(gray)
                return
            if mode == "蓝光过滤" or blue_on:
                tint = TINT_COLORS.get(cfg["tint_color"], (255, 255, 220))
                r_adj = tint[0] / 255.0
                g_adj = tint[1] / 255.0
                b_adj = tint[2] / 255.0
                if blue_on:
                    reduction = (cfg["blue_light_strength"] / 100.0) * 0.5
                    b_adj *= (1.0 - reduction)
                matrix = (r_adj, 0, 0, 0, 0, 0, g_adj, 0, 0, 0,
                          0, 0, b_adj, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1)
                mag.set_fullscreen_color_effect(matrix)
        except Exception as e:
            print("护眼滤镜应用失败:", e)

    @staticmethod
    def _in_eye_schedule_static(start_str, end_str):
        try:
            now = datetime.now().time()
            start = datetime.strptime(start_str, "%H:%M").time()
            end = datetime.strptime(end_str, "%H:%M").time()
            if start <= end:
                return start <= now <= end
            return now >= start or now <= end
        except Exception:
            return True

    def _schedule_check_loop(self):
        self.apply_eye_filter()
        self.root.after(60000, self._schedule_check_loop)

    # ================= 统计 =================
    def open_stats(self):
        if self.stats_win and self.stats_win.winfo_exists():
            self.stats_win.lift()
            return

        win = tk.Toplevel(self.root)
        self.stats_win = win
        win.title("使用统计")
        # 压缩高度，去除多余空白
        win.geometry("440x390")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.config(bg=self.theme_bg)
        
        if os.path.exists(ICON_FILE):
            try:
                win.iconbitmap(ICON_FILE)
            except Exception:
                pass

        tk.Label(win, text="📊 使用统计", font=(FONT_MAIN, 14, "bold"),
                 bg=self.theme_bg, fg=self.theme_fg).pack(pady=(16, 8))

        # 让 Notebook 融入当前主题色
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TNotebook", background=self.theme_bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.card_bg, foreground=self.theme_fg, padding=[10, 4])
        style.map("TNotebook.Tab", background=[("selected", self.theme_bg)])

        notebook = ttk.Notebook(win)
        notebook.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        for period in ("今日", "本周", "本月"):
            frame = tk.Frame(notebook, bg=self.theme_bg)
            notebook.add(frame, text=period)
            self._build_stats_content(frame, period)

    def _build_stats_content(self, parent, period):
        now = datetime.now()
        if period == "今日":
            start = datetime(now.year, now.month, now.day)
        elif period == "本周":
            start = now - timedelta(days=now.weekday())
            start = datetime(start.year, start.month, start.day)
        else: 
            start = datetime(now.year, now.month, 1)
        start_ts = start.timestamp()
        end_ts = time.time()

        summary = {"work": [0, 0], "rest": [0, 0], "leave": [0, 0]}
        
        for r in self.stats.get("records", []):
            if start_ts <= r.get("end", 0) <= end_ts:
                kind = r.get("type")
                dur = max(0, r.get("end", 0) - r.get("start", 0))
                if kind in summary:
                    summary[kind][0] += 1
                    summary[kind][1] += dur

        labels = {
            "work": ("💼 工作", "#0a84ff"),
            "rest": ("🌿 休息", "#28a745"),
            "leave": ("🚪 离开", "#ff9500"),
        }

        for kind in ("work", "rest", "leave"):
            name, color = labels[kind]
            count, seconds = summary[kind]
            minutes = seconds // 60
            sec = seconds % 60
            f = tk.Frame(parent, bg=self.theme_bg)
            f.pack(fill="x", pady=10, padx=8)
            tk.Label(f, text=name, font=(FONT_MAIN, 11, "bold"),
                     fg=color, bg=self.theme_bg, width=8, anchor="w").pack(side=tk.LEFT)
            tk.Label(f, text=f"{count} 次", font=(FONT_MAIN, 11),
                     bg=self.theme_bg, fg=self.theme_fg, width=8).pack(side=tk.LEFT)
            tk.Label(f, text=f"累计 {minutes} 分 {sec} 秒",
                     font=(FONT_MAIN, 11), bg=self.theme_bg,
                     fg=self.theme_fg).pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(parent, text=f"统计范围：{start.strftime('%Y-%m-%d')} 至今",
                 font=(FONT_MAIN, 8), bg=self.theme_bg, fg=self.sub_fg).pack(pady=8)

        tk.Button(parent, text="清空本周期统计", font=(FONT_MAIN, 9),
                  bg=self.card_bg, fg=self.theme_fg, bd=0,
                  command=lambda: self._clear_stats(start_ts, end_ts, parent)).pack(pady=6)

    def _clear_stats(self, start_ts, end_ts, parent):
        if not messagebox.askyesno("确认", "确定要清空本周期的统计数据吗？"):
            return
        self.stats["records"] = [
            r for r in self.stats.get("records", [])
            if not (start_ts <= r.get("end", 0) <= end_ts)
        ]
        save_stats(self.stats)
        for w in parent.winfo_children():
            w.destroy()
        self._build_stats_content(parent, "今日" if start_ts >= time.time() - 86400 else "本周")

    # ================= 编制说明 =================
    def open_help(self):
        if self.help_win and self.help_win.winfo_exists():
            self.help_win.lift()
            return
        win = tk.Toplevel(self.root)
        self.help_win = win
        win.title("软件编制说明 - 20-20-20护眼法则")
        win.geometry("620x680")
        win.attributes("-topmost", True)
        win.config(bg=self.theme_bg)
        
        if os.path.exists(ICON_FILE):
            try:
                win.iconbitmap(ICON_FILE)
            except Exception:
                pass

        # 修复右侧显示不全：创建一个包裹 Frame 来固定 Text 和 Scrollbar
        frame = tk.Frame(win, bg=self.theme_bg)
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        text = tk.Text(frame, wrap="word", font=(FONT_MAIN, 10),
                       bg=self.card_bg, fg=self.theme_fg,
                       padx=12, pady=12, bd=0, relief="flat",
                       highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)

        text.insert("1.0", HELP_TEXT)
        text.config(state="disabled")

    # ================= 软件说明 =================
    def open_about(self):
        if hasattr(self, "about_win") and self.about_win and self.about_win.winfo_exists():
            self.about_win.lift()
            return
            
        win = tk.Toplevel(self.root)
        self.about_win = win
        win.title("软件说明 - 20护眼小助手")
        win.geometry("480x460")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.config(bg=self.theme_bg)
        
        if os.path.exists(ICON_FILE):
            try:
                win.iconbitmap(ICON_FILE)
            except Exception:
                pass

        tk.Label(win, text="20护眼小助手 v1.0", font=(FONT_MAIN, 16, "bold"),
                 bg=self.theme_bg, fg=self.theme_fg).pack(pady=(20, 10))

        info_text = """“20护眼小助手” 是一款专为长时间面对电脑屏幕的人群（上班族、学生、程序员等）设计的 Windows 桌面护眼软件。它基于国际公认的“20-20-20护眼法则”开发，旨在通过强制提醒、时间统计、外观美化及全屏护眼滤镜等功能，帮助用户养成良好的用眼习惯，有效缓解视疲劳。

✨ 核心功能：
• 自动休息提醒：每连续用眼 20 分钟，强制全屏休息 20 秒，键鼠操作自动重置倒计时。
• 护眼滤镜：支持黑白模式、蓝光过滤，6种色温可选，支持护眼时间段设定。
• 离开与空闲检测：无操作自动暂停计时；超时进入待机，轮播必应高清壁纸。
• 多维统计：精准记录每日、每周、每月的工作、休息、离开时长与次数。
• 个性化体验：7种主题颜色，透明化调节，可拖动悬浮数字时钟，支持开机自启与最小化到托盘。

👨‍💻 作者信息：
作者：一哥陈
QQ：94754106
邮箱：c@2li.xyz
GitHub：https://github.com/CHY2022/20hyzs
"""
        
        frame = tk.Frame(win, bg=self.theme_bg)
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        text = tk.Text(frame, wrap="word", font=(FONT_MAIN, 9),
                       bg=self.card_bg, fg=self.theme_fg,
                       padx=12, pady=12, bd=0, relief="flat",
                       highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)

        text.insert("1.0", info_text)
        text.config(state="disabled")

        # 增加一行可点击的 GitHub 链接
        link_frame = tk.Frame(win, bg=self.theme_bg)
        link_frame.pack(pady=(0, 16))
        link = tk.Label(link_frame, text="访问 GitHub 项目主页", font=(FONT_MAIN, 9, "underline"),
                        bg=self.theme_bg, fg="#0a84ff", cursor="hand2")
        link.pack()
        link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/CHY2022/20hyzs"))

        tk.Button(win, text="关闭", font=(FONT_MAIN, 9), bg=self.card_bg, fg=self.theme_fg,
                  bd=0, relief="flat", padx=20, pady=5, cursor="hand2",
                  command=win.destroy).pack(pady=(0, 16))

    # ================= 设置窗口 =================
    def open_settings(self):
        if self.settings_win and self.settings_win.winfo_exists():
            self.settings_win.lift()
            return

        win = tk.Toplevel(self.root)
        self.settings_win = win
        win.title("设置")
        win.geometry("480x820")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.config(bg=self.theme_bg)
        
        if os.path.exists(ICON_FILE):
            try:
                win.iconbitmap(ICON_FILE)
            except Exception:
                pass

        canvas = tk.Canvas(win, bg=self.theme_bg, highlightthickness=0)
        scrollbar = ttk.Scrollbar(win, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=self.theme_bg)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", width=460)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        def section(title):
            lf = tk.LabelFrame(
                inner, text=f"  {title}  ", font=(FONT_MAIN, 10, "bold"),
                bg=self.theme_bg, fg=self.theme_fg,
                bd=1, relief="groove", padx=14, pady=10)
            lf.pack(fill="x", padx=16, pady=(12, 0))
            return lf

        def row(parent, label, widget_factory):
            f = tk.Frame(parent, bg=self.theme_bg)
            f.pack(fill="x", pady=5)
            tk.Label(f, text=label, font=(FONT_MAIN, 9),
                     bg=self.theme_bg, fg=self.theme_fg,
                     anchor="w", width=20).pack(side=tk.LEFT)
            widget_factory(f)

        sec1 = section("⏱  空闲检测")
        self.lock_idle_var = tk.IntVar(value=int(self.config.get("lock_idle_min", 5)))
        row(sec1, "锁屏空闲（分钟）",
            lambda p: tk.Spinbox(p, from_=1, to=60, width=8,
                                 textvariable=self.lock_idle_var).pack(side=tk.LEFT))
        self.pause_idle_var = tk.IntVar(value=int(self.config.get("pause_idle_min", 2)))
        row(sec1, "暂停空闲（分钟）",
            lambda p: tk.Spinbox(p, from_=1, to=30, width=8,
                                 textvariable=self.pause_idle_var).pack(side=tk.LEFT))

        sec2 = section("🎨  外观")
        self.theme_var = tk.StringVar(value=self.config.get("theme", "浅色"))
        row(sec2, "主题颜色",
            lambda p: tk.OptionMenu(p, self.theme_var, "浅色", "浅蓝色", "浅绿色", "淡黄色", "淡粉色", "淡橙色", "深色").pack(side=tk.LEFT))
        self.opacity_var = tk.DoubleVar(value=float(self.config.get("opacity", 0.95)))
        row(sec2, "透明度",
            lambda p: tk.Scale(p, from_=0.5, to=1.0, resolution=0.05,
                               orient=tk.HORIZONTAL, length=180,
                               variable=self.opacity_var, bg=self.theme_bg,
                               highlightthickness=0).pack(side=tk.LEFT))

        sec3 = section("🚀  启动")
        self.autostart_var = tk.BooleanVar(value=bool(self.config.get("autostart", False)))
        tk.Checkbutton(sec3, text="开机自启动", variable=self.autostart_var,
                       font=(FONT_MAIN, 9), bg=self.theme_bg, fg=self.theme_fg,
                       selectcolor=self.theme_bg,
                       activebackground=self.theme_bg).pack(anchor="w", pady=4)

        sec4 = section("👁  护眼模式")
        self.eye_mode_var = tk.StringVar(value=self.config.get("eye_mode", "原色"))
        row(sec4, "屏幕色彩",
            lambda p: tk.OptionMenu(p, self.eye_mode_var, "原色", "黑白", "蓝光过滤").pack(side=tk.LEFT))
        self.blue_on_var = tk.BooleanVar(value=bool(self.config.get("blue_light_on", False)))
        tk.Checkbutton(sec4, text="开启蓝光过滤", variable=self.blue_on_var,
                       font=(FONT_MAIN, 9), bg=self.theme_bg, fg=self.theme_fg,
                       selectcolor=self.theme_bg,
                       activebackground=self.theme_bg).pack(anchor="w", pady=4)
        self.blue_strength_var = tk.IntVar(value=int(self.config.get("blue_light_strength", 50)))
        row(sec4, "蓝光强度（0~100）",
            lambda p: tk.Scale(p, from_=0, to=100, orient=tk.HORIZONTAL,
                               length=180, variable=self.blue_strength_var,
                               bg=self.theme_bg, highlightthickness=0).pack(side=tk.LEFT))
        self.tint_var = tk.StringVar(value=self.config.get("tint_color", "淡黄"))
        row(sec4, "色温颜色",
            lambda p: tk.OptionMenu(p, self.tint_var, *TINT_COLORS.keys()).pack(side=tk.LEFT))

        sec5 = section("🕐  护眼时间段")
        self.schedule_on_var = tk.BooleanVar(
            value=bool(self.config.get("eye_schedule_enabled", False)))
        tk.Checkbutton(sec5, text="启用护眼时间段", variable=self.schedule_on_var,
                       font=(FONT_MAIN, 9), bg=self.theme_bg, fg=self.theme_fg,
                       selectcolor=self.theme_bg,
                       activebackground=self.theme_bg).pack(anchor="w", pady=4)
        tf = tk.Frame(sec5, bg=self.theme_bg)
        tf.pack(fill="x", pady=4)
        tk.Label(tf, text="从", font=(FONT_MAIN, 9),
                 bg=self.theme_bg, fg=self.theme_fg).pack(side=tk.LEFT)
        self.schedule_start_var = tk.StringVar(
            value=self.config.get("eye_schedule_start", "20:00"))
        tk.Entry(tf, textvariable=self.schedule_start_var, width=6).pack(
            side=tk.LEFT, padx=4)
        tk.Label(tf, text="到", font=(FONT_MAIN, 9),
                 bg=self.theme_bg, fg=self.theme_fg).pack(side=tk.LEFT)
        self.schedule_end_var = tk.StringVar(
            value=self.config.get("eye_schedule_end", "07:00"))
        tk.Entry(tf, textvariable=self.schedule_end_var, width=6).pack(
            side=tk.LEFT, padx=4)

        tk.Button(inner, text="保存并应用", font=(FONT_MAIN, 10, "bold"),
                  bg="#0a84ff", fg="white", bd=0, relief="flat",
                  padx=24, pady=8, cursor="hand2",
                  command=self.save_settings).pack(pady=24)

    def save_settings(self):
        self.config["lock_idle_min"] = max(1, self.lock_idle_var.get())
        self.config["pause_idle_min"] = max(1, self.pause_idle_var.get())
        self.config["theme"] = self.theme_var.get()
        self.config["opacity"] = round(self.opacity_var.get(), 2)
        self.config["autostart"] = bool(self.autostart_var.get())
        self.config["eye_mode"] = self.eye_mode_var.get()
        self.config["blue_light_on"] = bool(self.blue_on_var.get())
        self.config["blue_light_strength"] = int(self.blue_strength_var.get())
        self.config["tint_color"] = self.tint_var.get()
        self.config["eye_schedule_enabled"] = bool(self.schedule_on_var.get())
        self.config["eye_schedule_start"] = self.schedule_start_var.get().strip()
        self.config["eye_schedule_end"] = self.schedule_end_var.get().strip()
        save_config(self.config)
        
        # 根据新主题重新计算颜色变量
        self._calculate_colors()
        
        self.apply_win11_style()
        self.set_autostart(self.config["autostart"])
        self.apply_eye_filter()
        
        # 更新所有主界面部件的颜色
        self.root.config(bg=self.theme_bg)
        self._header.config(bg=self.theme_bg)
        self._header_label.config(bg=self.theme_bg, fg=self.theme_fg)
        self._header_ver.config(bg=self.theme_bg, fg=self.sub_fg)
        self._card.config(bg=self.card_bg, highlightbackground="#d0d0d0" if self.config.get("theme") != "深色" else "#3a3d42")
        self.status_label.config(bg=self.card_bg, fg=self.theme_fg)
        self.sub_label.config(bg=self.card_bg, fg=self.sub_fg)
        self.clock.set_colors(bg=self.card_bg, fg=self._clock_fg())
        self._func_frame.config(bg=self.theme_bg)
        self._bottom.config(bg=self.theme_bg)
        self._explain.config(bg=self.theme_bg, fg=self.sub_fg)
        self._link.config(bg=self.theme_bg)
        
        # 更新按钮颜色
        self.pause_btn.config(bg=self.card_bg, fg=self.theme_fg, activebackground=self.hover_bg)
        self.leave_btn.config(bg=self.card_bg, fg=self.theme_fg, activebackground=self.hover_bg)
        self.stats_btn.config(bg=self.card_bg, fg=self.theme_fg, activebackground=self.hover_bg)

        if self.settings_win and self.settings_win.winfo_exists():
            self.settings_win.destroy()
        messagebox.showinfo("设置", "设置已保存并应用。")

    def set_autostart(self, enable: bool):
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "EyeCare20"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0,
                                 winreg.KEY_SET_VALUE)
            if enable:
                exe_path = sys.executable if getattr(sys, "frozen", False) \
                    else os.path.abspath(__file__)
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print("自启动设置失败:", e)

    # ================= 窗口状态轮询 =================
    def _poll_window_state(self):
        try:
            state = self.root.state()
        except Exception:
            state = "normal"
        if state != self._last_state:
            if state == "iconic" and not self._hiding_to_tray:
                self.root.after(150, self.show_floating_clock)
            elif state == "normal":
                self.hide_floating_clock()
            self._last_state = state
        self.root.after(500, self._poll_window_state)

    # ================= 悬浮时钟 =================
    def show_floating_clock(self):
        if self.float_window and self.float_window.winfo_exists():
            return
        try:
            self.float_window = tk.Toplevel()
            self.float_window.overrideredirect(True)
            self.float_window.attributes("-topmost", True)
            self.float_window.attributes("-alpha", 0.88)
            self.float_window.config(bg="#1e1e1e")
            sw = self.float_window.winfo_screenwidth()
            sh = self.float_window.winfo_screenheight()
            self.float_window.geometry(f"200x100+{sw - 220}+{sh - 160}")
            self.float_clock = ScrollClock(self.float_window, text="20:00",
                                           bg="#1e1e1e", fg="#00d4ff")
            self.float_clock.pack(expand=True, fill="both", padx=5, pady=5)
            m, s = divmod(self.remaining, 60)
            self.float_clock.set_text(f"{m:02d}:{s:02d}", animate=False)
            self.float_window.bind("<ButtonPress-1>", self._start_move)
            self.float_window.bind("<B1-Motion>", self._do_move)
            self.float_window.bind("<ButtonRelease-1>", self._end_move)
            self.float_clock.bind("<ButtonPress-1>", self._start_move)
            self.float_clock.bind("<B1-Motion>", self._do_move)
            self.float_clock.bind("<ButtonRelease-1>", self._end_move)
            self.float_window.bind("<Double-Button-1>",
                                   lambda e: self._restore_from_float())
        except Exception as e:
            print("悬浮窗创建失败:", e)
            self.float_window = None
            self.float_clock = None

    def hide_floating_clock(self):
        if self.float_window and self.float_window.winfo_exists():
            self.float_window.destroy()
        self.float_window = None
        self.float_clock = None
        self._drag_active = False

    def _start_move(self, event):
        self._drag_active = True
        self._drag_x = event.x_root - self.float_window.winfo_x()
        self._drag_y = event.y_root - self.float_window.winfo_y()

    def _do_move(self, event):
        if not self._drag_active:
            return
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.float_window.geometry(f"+{x}+{y}")

    def _end_move(self, event):
        self._drag_active = False

    def _restore_from_float(self):
        self.hide_floating_clock()
        self.root.deiconify()

    # ================= 系统托盘 =================
    def setup_background_services(self):
        self.start_input_listeners()
        self.start_idle_check()
        if HAS_TRAY:
            self.setup_tray()

    def setup_tray(self):
        try:
            icon_image = self._load_tray_icon()
            if icon_image is None:
                return

            def open_website(icon, item):
                webbrowser.open("https://pan.2li.xyz")

            def show_window(icon, item):
                self.ui_queue.put("show")

            def open_settings(icon, item):
                self.ui_queue.put("settings")

            def open_stats(icon, item):
                self.ui_queue.put("stats")

            def open_help(icon, item):
                self.ui_queue.put("help")

            def open_about(icon, item):
                self.ui_queue.put("about")

            def quit_app(icon, item):
                self.ui_queue.put("quit")
                try:
                    icon.stop()
                except Exception:
                    pass

            menu = pystray.Menu(
                pystray.MenuItem("显示主窗口", show_window, default=True),
                pystray.MenuItem("统计", open_stats),
                pystray.MenuItem("设置", open_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("软件说明", open_about),
                pystray.MenuItem("软件编制说明（护眼知识）", open_help),
                pystray.MenuItem("打开官网", open_website),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("退出", quit_app),
            )
            self.tray_icon = pystray.Icon(
                "EyeCare20", icon_image, "20护眼小助手 v1.0", menu)
            self.tray_icon.on_click = lambda icon, item: self.ui_queue.put("show")
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            print("托盘已启动")
        except Exception as e:
            print("托盘初始化失败:", e)

    def _load_tray_icon(self):
        if not HAS_TRAY:
            return None
        if os.path.exists(ICON_FILE):
            try:
                return Image.open(ICON_FILE).convert("RGBA")
            except Exception:
                pass
        if HAS_REQUESTS:
            try:
                resp = requests.get("https://pan.2li.xyz/favicon.ico", timeout=8)
                resp.raise_for_status()
                return Image.open(io.BytesIO(resp.content)).convert("RGBA")
            except Exception:
                pass
        img = Image.new("RGBA", (64, 64), color=(30, 144, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((18, 14), "20", fill="white")
        return img

    def hide_to_tray(self):
        if self.tray_icon:
            self._hiding_to_tray = True
            try:
                self.root.withdraw()
            finally:
                self.root.after(1000, lambda: setattr(self, "_hiding_to_tray", False))
        else:
            self.root.iconify()
            messagebox.showinfo(
                "提示",
                "系统托盘不可用（pystray 未安装或初始化失败），\n"
                "已改为最小化窗口。")

    def _process_ui_queue(self):
        if not self.running:
            return
        try:
            while True:
                action = self.ui_queue.get_nowait()
                if action == "show":
                    self.root.deiconify()
                    self.root.lift()
                    self.root.focus_force()
                elif action == "settings":
                    self.root.deiconify()
                    self.root.lift()
                    self.root.focus_force()
                    self.root.after(200, self.open_settings)
                elif action == "stats":
                    self.root.deiconify()
                    self.root.lift()
                    self.root.focus_force()
                    self.root.after(200, self.open_stats)
                elif action == "help":
                    self.root.deiconify()
                    self.root.lift()
                    self.root.focus_force()
                    self.root.after(200, self.open_help)
                elif action == "about":
                    self.root.deiconify()
                    self.root.lift()
                    self.root.focus_force()
                    self.root.after(200, self.open_about)
                elif action == "quit":
                    self.quit_app()
                    return
        except queue.Empty:
            pass
        if self.running:
            self.root.after(150, self._process_ui_queue)

    def quit_app(self):
        self.running = False
        self._end_work_session()
        self.stop_input_listeners()
        if HAS_MAG:
            def _cleanup_mag():
                try:
                    mag.reset_fullscreen_color_effect()
                    mag.finalize()
                except Exception:
                    pass
            threading.Thread(target=_cleanup_mag, daemon=True).start()
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
            self.tray_icon = None
        for w in (self.lock_window, self.float_window):
            if w:
                try:
                    w.destroy()
                except Exception:
                    pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = EyeCareApp()
    app.run()