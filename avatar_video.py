import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import os
import asyncio

class AvatarVideo:
    def __init__(self):
        self.video_label = None
        self.cap = None
        self.running = False
        self.after_id = None
        self.current_video_type = "idle"
        self.idle_path = "assets/video/idle.mp4"
        self.talking_path = "assets/video/talking.mp4"
        self.is_talking = False
    
    def set_label(self, label_widget):
        self.video_label = label_widget
        print("🎬 Видео-виджет привязан")
        
        if os.path.exists(self.idle_path):
            print(f"   ✅ Idle видео: {self.idle_path}")
        else:
            print(f"   ❌ Idle видео не найдено: {self.idle_path}")
        
        if os.path.exists(self.talking_path):
            print(f"   ✅ Talking видео: {self.talking_path}")
        else:
            print(f"   ❌ Talking видео не найдено: {self.talking_path}")
    
    def _load_video(self, video_path):
        if self.cap:
            self.cap.release()
        
        if os.path.exists(video_path):
            self.cap = cv2.VideoCapture(video_path)
            if self.cap.isOpened():
                print(f"   🎬 Загружено видео: {os.path.basename(video_path)}")
                return True
        return False
    
    def _update_frame(self):
        if not self.running:
            return
        if not self.cap:
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
            try:
                # Получаем размеры виджета
                label_width = self.video_label.winfo_width()
                label_height = self.video_label.winfo_height()
                if label_width < 10:
                    label_width = 280
                if label_height < 10:
                    label_height = 350
                
                # Получаем размеры видео
                video_height, video_width = frame.shape[:2]
                video_aspect = video_width / video_height
                label_aspect = label_width / label_height
                
                # Вычисляем размеры с сохранением пропорций
                if video_aspect > label_aspect:
                    # Видео шире - подгоняем по ширине
                    new_width = label_width
                    new_height = int(label_width / video_aspect)
                else:
                    # Видео выше - подгоняем по высоте
                    new_height = label_height
                    new_width = int(label_height * video_aspect)
                
                # Ресайзим кадр
                frame_resized = cv2.resize(frame, (new_width, new_height))
                
                # Создаём чёрный фон и центрируем видео
                if new_width < label_width or new_height < label_height:
                    bg = np.zeros((label_height, label_width, 3), dtype=np.uint8)
                    x_offset = (label_width - new_width) // 2
                    y_offset = (label_height - new_height) // 2
                    bg[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = frame_resized
                    frame_rgb = cv2.cvtColor(bg, cv2.COLOR_BGR2RGB)
                else:
                    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
                
                img = Image.fromarray(frame_rgb)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.video_label.imgtk = imgtk
                self.video_label.config(image=imgtk)
            except Exception as e:
                print(f"Ошибка обновления кадра: {e}")
        
        if self.running:
            self.after_id = self.video_label.after(33, self._update_frame)
    
    def start(self):
        print("🎬 AvatarVideo.start() вызван")
        if not self.video_label:
            print("⚠️ Нет video_label!")
            return
        
        if not os.path.exists(self.idle_path):
            print(f"⚠️ Нет idle видео: {self.idle_path}")
            return
        
        self.running = True
        if self._load_video(self.idle_path):
            self._update_frame()
            print("🎬 Видео запущено")
        else:
            print("❌ Не удалось загрузить видео")
    
    async def start_talking(self):
        if not self.running:
            return
        if not self.is_talking:
            self.is_talking = True
            if self._load_video(self.talking_path):
                print("🎤 Аватар говорит")
            await asyncio.sleep(0.01)
    
    async def stop_talking(self):
        if not self.running:
            return
        if self.is_talking:
            self.is_talking = False
            if self._load_video(self.idle_path):
                print("🎤 Аватар замолк")
            await asyncio.sleep(0.01)
    
    def stop(self):
        print("🎬 Остановка аватара...")
        self.running = False
        if self.cap:
            self.cap.release()
        if self.after_id and self.video_label:
            try:
                self.video_label.after_cancel(self.after_id)
            except:
                pass