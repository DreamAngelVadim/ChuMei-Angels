"""
Video Avatar — видео с рандомным выбором из нескольких вариантов
"""
import asyncio
import os
import glob
import random
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import config


class AvatarVideo:
    """Видео-аватар с рандомным выбором видео."""

    def __init__(self):
        self.root = None
        self.label = None
        self.idle_caps = []
        self.talking_caps = []
        self.current_cap = None
        self.is_talking = False
        self.running = False
        self.scale = 0.5
        self.width = 240
        self.height = 300
        self.after_id = None
        self.status_text = None

    def _find_videos(self, pattern):
        """Ищет видео по шаблону."""
        videos = glob.glob(os.path.join("assets", pattern))
        videos.sort()
        if not videos:
            fallback = pattern.replace("_*.mp4", ".mp4")
            fallback_path = os.path.join("assets", fallback)
            if os.path.exists(fallback_path):
                videos = [fallback_path]
        return videos

    def _open_videos(self, video_paths):
        """Открывает все видео и возвращает список caps."""
        caps = []
        for path in video_paths:
            cap = cv2.VideoCapture(path)
            if cap.isOpened():
                caps.append(cap)
        return caps

    async def start(self):
        self.running = True

        idle_paths = self._find_videos("avatar_idle_*.mp4")
        talking_paths = self._find_videos("avatar_talking_*.mp4")

        if not idle_paths:
            print("Видео не найдены! Положите avatar_idle_1.mp4 в папку assets/")
            return

        if not talking_paths:
            talking_paths = idle_paths.copy()

        print(f"Загрузка {len(idle_paths)} idle-видео...")
        self.idle_caps = self._open_videos(idle_paths)
        print(f"Загрузка {len(talking_paths)} talking-видео...")
        self.talking_caps = self._open_videos(talking_paths)

        self.current_cap = random.choice(self.idle_caps)

        original_width = int(self.current_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        original_height = int(self.current_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if original_width <= 0:
            original_width = 480
        if original_height <= 0:
            original_height = 600

        self.width = int(original_width * self.scale)
        self.height = int(original_height * self.scale)

        self.root = tk.Tk()
        self.root.title(f"{config.CHARACTER_NAME} — AI Ассистент")
        self.root.geometry(f"{self.width}x{self.height + 30}")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a0a1e")

        self.label = tk.Label(self.root, bg="#1a0a1e", bd=0)
        self.label.pack()

        self.status_text = tk.Label(self.root, text="Ожидаю...",
                                    fg="#e0c0ff", bg="#1a0a1e", font=("Arial", 11))
        self.status_text.pack(pady=3)

        print(f"Видео-аватар запущен")
        self._update_frame()

        while self.running:
            try:
                if self.root:
                    self.root.update()
            except:
                pass
            await asyncio.sleep(0.03)

    def _update_frame(self):
        if not self.running or self.current_cap is None:
            return
        try:
            if self.root is None:
                return
            ret, frame = self.current_cap.read()
            if not ret:
                self.current_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.current_cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_resized = cv2.resize(frame_rgb, (self.width, self.height))
                img = Image.fromarray(frame_resized)
                imgtk = ImageTk.PhotoImage(image=img)
                if self.label:
                    self.label.imgtk = imgtk
                    self.label.configure(image=imgtk)
            if self.running and self.root:
                self.after_id = self.root.after(30, self._update_frame)
        except:
            pass

    async def start_talking(self):
        self.is_talking = True
        if self.talking_caps:
            self.current_cap = random.choice(self.talking_caps)
            self.current_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        try:
            if self.label:
                self.label.configure(highlightbackground="#ff00ff", highlightcolor="#ff00ff", highlightthickness=4)
        except:
            pass
        try:
            if self.status_text:
                self.status_text.config(text="Говорю...", fg="#ff00ff")
        except:
            pass

    async def stop_talking(self):
        self.is_talking = False
        if self.idle_caps:
            self.current_cap = random.choice(self.idle_caps)
            self.current_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        try:
            if self.label:
                self.label.configure(highlightbackground="#1a0a1e", highlightcolor="#1a0a1e", highlightthickness=0)
        except:
            pass
        try:
            if self.status_text:
                self.status_text.config(text="Ожидаю...", fg="#e0c0ff")
        except:
            pass

    async def stop(self):
        self.running = False
        if self.after_id:
            try:
                self.root.after_cancel(self.after_id)
            except:
                pass
        for cap in self.idle_caps + self.talking_caps:
            try:
                cap.release()
            except:
                pass
        if self.root:
            try:
                self.root.destroy()
            except:
                pass