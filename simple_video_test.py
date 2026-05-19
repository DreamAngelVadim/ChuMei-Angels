import cv2
import tkinter as tk
from PIL import Image, ImageTk
import os
import random
import asyncio


class AvatarVideo:
    def __init__:
        self.video_label = None
        self.cap = None
        self.running = False
        self.after_id = None
        self.idle_videos = []
        self.talking_videos = []
        self.current_video_type = "idle"
    
    def set_label:
        self.video_label = label_widget
        print
        
        # Ищем видео
        import glob
        all_videos = glob.glob)
        print}")
        
        for path in all_videos:
            name = os.path.basename.lower
            if "talking" in name:
                self.talking_videos.append
                print
            else:
                self.idle_videos.append
                print
    
    async def start:
        if not self.video_label or not self.idle_videos:
            print
            return
        
        self.running = True
        self._load_video
        self._update_frame
        
        while self.running:
            await asyncio.sleep
    
    def _load_video:
        if video_type == "talking" and self.talking_videos:
            path = random.choice
        else:
            path = random.choice
        
        if self.cap:
            self.cap.release
        
        self.cap = cv2.VideoCapture
        print}")
    
    def _update_frame:
        if not self.running or not self.cap:
            return
        
        try:
            if not self.video_label.winfo_exists:
                self.running = False
                return
        except:
            self.running = False
            return
        
        ret, frame = self.cap.read
        if not ret:
            self.cap.set
            ret, frame = self.cap.read
        
        if ret:
            # Получаем размеры виджета
            width = self.video_label.winfo_width
            height = self.video_label.winfo_height
            if width < 10:
                width = 280
            if height < 10:
                height = 350
            
            frame_resized = cv2.resize)
            frame_rgb = cv2.cvtColor
            img = Image.fromarray
            imgtk = ImageTk.PhotoImage
            
            self.video_label.imgtk = imgtk
            self.video_label.configure
        
        if self.running:
            self.after_id = self.video_label.after
    
    async def start_talking:
        if self.talking_videos:
            self._load_video
            print
    
    async def stop_talking:
        if self.idle_videos:
            self._load_video
            print
    
    async def stop:
        self.running = False
        if self.cap:
            self.cap.release
        if self.after_id and self.video_label:
            try:
                self.video_label.after_cancel
            except:
                pass
