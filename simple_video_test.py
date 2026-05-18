import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import random
import asyncio


class AvatarVideo:
    def __init__(self):
        self.video_label = None
        self.cap = None
        self.running = False
        self.after_id = None
        self.idle_videos = []
        self.talking_videos = []
        self.current_video_type = "idle"
    
    def set_label(self, label_widget):
        self.video_label = label_widget
        print("🎬 Видео-виджет привязан")
        
        # Ищем видео
        import glob
        all_videos = glob.glob(os.path.join("assets", "*.mp4"))
        print(f"🔍 Найдено видео: {len(all_videos)}")
        
        for path in all_videos:
            name = os.path.basename(path).lower()
            if "talking" in name:
                self.talking_videos.append(path)
                print(f"  ✅ Talking: {name}")
            else:
                self.idle_videos.append(path)
                print(f"  ✅ Idle: {name}")
    
    async def start(self):
        if not self.video_label or not self.idle_videos:
            print("⚠️ Нет видео для проигрывания")
            return
        
        self.running = True
        self._load_video("idle")
        self._update_frame()
        
        while self.running:
            await asyncio.sleep(0.03)
    
    def _load_video(self, video_type):
        if video_type == "talking" and self.talking_videos:
            path = random.choice(self.talking_videos)
        else:
            path = random.choice(self.idle_videos)
        
        if self.cap:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(path)
        print(f"🎬 Загружено видео: {os.path.basename(path)}")
    
    def _update_frame(self):
        if not self.running or not self.cap:
            return
        
        try:
            if not self.video_label.winfo_exists():
                self.running = False
                return
        except:
            self.running = False
            return
        
        ret, frame = self.cap.read()
        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
        
        if ret:
            # Получаем размеры виджета
            width = self.video_label.winfo_width()
            height = self.video_label.winfo_height()
            if width < 10:
                width = 280
            if height < 10:
                height = 350
            
            frame_resized = cv2.resize(frame, (width, height))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk, text="")
        
        if self.running:
            self.after_id = self.video_label.after(30, self._update_frame)
    
    async def start_talking(self):
        if self.talking_videos:
            self._load_video("talking")
            print("🎤 Аватар говорит")
    
    async def stop_talking(self):
        if self.idle_videos:
            self._load_video("idle")
            print("🎤 Аватар замолк")
    
    async def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        if self.after_id and self.video_label:
            try:
                self.video_label.after_cancel(self.after_id)
            except:
                pass