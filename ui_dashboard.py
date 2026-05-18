"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CHUMEI ANGELS - UI DASHBOARD                         ║
║                                                                              ║
║   ✅ Современный дизайн с градиентами и тенями                               ║
║   ✅ Увеличенные аватарки (80x80)                                            ║
║   ✅ Плавные анимации при наведении                                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from datetime import datetime
import os
import asyncio
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox

# ========== НАСТРОЙКА СТИЛЯ ==========
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
    
    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#2D2D2D", foreground="#FFFFFF",
                         relief="flat", borderwidth=1,
                         font=("Segoe UI", 10, "normal"))
        label.pack()
    
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None


class ChuMeiUI:
    def __init__(self, chumei_instance):
        self.chumei = chumei_instance
        
        # История для undo/redo
        self.undo_stack = []
        self.redo_stack = []
        self.current_text = ""
        
        self.root = ctk.CTk()
        self.root.title("ChuMei Angels — виртуальный особняк в Сибуе")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        # Установка иконки окна (если есть)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        self.setup_ui()
        self.setup_hotkeys()
        self.update_loop()
        self.center_window()
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    # ========== UNDO/REDO ==========
    
    def save_state(self):
        current = self.input_entry.get()
        if current != self.current_text:
            self.undo_stack.append(self.current_text)
            self.current_text = current
            self.redo_stack.clear()
            if len(self.undo_stack) > 50:
                self.undo_stack.pop(0)
    
    def undo(self, event=None):
        if self.undo_stack:
            self.redo_stack.append(self.current_text)
            prev_text = self.undo_stack.pop()
            self.current_text = prev_text
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, prev_text or "")
            print("↩️ Отмена")
        return "break"
    
    def redo(self, event=None):
        if self.redo_stack:
            self.undo_stack.append(self.current_text)
            next_text = self.redo_stack.pop()
            self.current_text = next_text
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, next_text or "")
            print("↪️ Возврат")
        return "break"
    
    # ========== ГОРЯЧИЕ КЛАВИШИ ==========
    
    def setup_hotkeys(self):
        self.input_entry.bind("<Control-c>", self.copy_text)
        self.input_entry.bind("<Control-v>", self.paste_text)
        self.input_entry.bind("<Control-x>", self.cut_text)
        self.input_entry.bind("<Control-a>", self.select_all)
        self.input_entry.bind("<Control-z>", self.undo)
        self.input_entry.bind("<Control-y>", self.redo)
    
    def copy_text(self, event=None):
        try:
            selected = self.input_entry.selection_get()
            if selected:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected)
                print(f"📋 Скопировано: {selected[:50]}...")
        except:
            pass
        return "break"
    
    def paste_text(self, event=None):
        try:
            text = self.root.clipboard_get()
            if text:
                self.save_state()
                cursor = self.input_entry.index("insert")
                current = self.input_entry.get()
                new = current[:cursor] + text + current[cursor:]
                self.input_entry.delete(0, "end")
                self.input_entry.insert(0, new)
                self.input_entry.icursor(cursor + len(text))
                self.current_text = new
                print(f"📋 Вставлено: {text[:50]}...")
        except:
            pass
        return "break"
    
    def cut_text(self, event=None):
        try:
            selected = self.input_entry.selection_get()
            if selected:
                self.save_state()
                self.root.clipboard_clear()
                self.root.clipboard_append(selected)
                start = self.input_entry.index("sel.first")
                end = self.input_entry.index("sel.last")
                current = self.input_entry.get()
                new = current[:start] + current[end:]
                self.input_entry.delete(0, "end")
                self.input_entry.insert(0, new)
                self.input_entry.icursor(start)
                self.current_text = new
                print(f"📋 Вырезано: {selected[:50]}...")
        except:
            pass
        return "break"
    
    def select_all(self, event=None):
        self.input_entry.select_range(0, "end")
        self.input_entry.icursor("end")
        return "break"
    
    def show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg="#2D2D2D", fg="white", activebackground="#0078D4", activeforeground="white")
        menu.add_command(label="Копировать (Ctrl+C)", command=lambda: self.copy_text())
        menu.add_command(label="Вырезать (Ctrl+X)", command=lambda: self.cut_text())
        menu.add_command(label="Вставить (Ctrl+V)", command=lambda: self.paste_text())
        menu.add_separator()
        menu.add_command(label="Отменить (Ctrl+Z)", command=lambda: self.undo())
        menu.add_command(label="Повторить (Ctrl+Y)", command=lambda: self.redo())
        menu.add_separator()
        menu.add_command(label="Выделить всё (Ctrl+A)", command=lambda: self.select_all())
        menu.add_command(label="Очистить", command=lambda: self.input_entry.delete(0, "end"))
        menu.post(event.x_root, event.y_root)
    
    # ========== ПОСТРОЕНИЕ ИНТЕРФЕЙСА ==========
    
    def setup_ui(self):
        # Главный контейнер
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ========== ЛЕВАЯ ПАНЕЛЬ (видео) ==========
        self.left_frame = ctk.CTkFrame(self.main_container, width=300, corner_radius=15, 
                                       fg_color="#1E1E1E", border_width=1, border_color="#3D3D3D")
        self.left_frame.pack(side="left", fill="y", padx=(0, 10))
        self.left_frame.pack_propagate(False)
        
        # Заголовок панели
        panel_title = ctk.CTkLabel(self.left_frame, text="🎬 Видео-аватар", 
                                   font=ctk.CTkFont(size=12, weight="bold"), text_color="#0078D4")
        panel_title.pack(pady=(10, 5))
        
        self.video_label = tk.Label(
            self.left_frame, 
            text="Загрузка видео...", 
            bg="#1E1E1E", 
            fg="#A0A0A0",
            font=("Segoe UI", 11)
        )
        self.video_label.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        self.video_status = ctk.CTkLabel(self.left_frame, text="🟢 Аватар активен", 
                                         font=ctk.CTkFont(size=10), text_color="#00FF00")
        self.video_status.pack(side="bottom", pady=10)
        
        # ========== ЦЕНТРАЛЬНАЯ ПАНЕЛЬ (карточки) ==========
        self.center_frame = ctk.CTkFrame(self.main_container, corner_radius=15, fg_color="transparent")
        self.center_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Заголовок центральной панели
        self.header_frame = ctk.CTkFrame(self.center_frame, height=40, corner_radius=12, fg_color="#252526")
        self.header_frame.pack(fill="x", pady=(0, 10))
        self.header_frame.pack_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🏠 ChuMei Angels — особняк в Сибуе | 5 уникальных помощниц",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#FFFFFF"
        )
        self.title_label.pack(expand=True)
        
        # Скроллируемая область
        self.cards_frame = ctk.CTkScrollableFrame(self.center_frame, fg_color="transparent")
        self.cards_frame.pack(fill="both", expand=True)
        
        self.girl_frames = {}
        girls = ["chuchu", "mei", "hana", "ki", "simone"]
        
        for girl in girls:
            frame = ctk.CTkFrame(self.cards_frame, corner_radius=12, border_width=1, border_color="#3D3D3D",
                                fg_color="#252526")
            frame.pack(fill="x", padx=5, pady=5)
            self.girl_frames[girl] = frame
            self.create_girl_card(frame, girl)
        
        # ========== ПРАВАЯ ПАНЕЛЬ (ЧАТ) ==========
        self.chat_frame = ctk.CTkFrame(self.main_container, width=380, corner_radius=15, fg_color="#1E1E1E")
        self.chat_frame.pack(side="right", fill="y", expand=False)
        self.chat_frame.pack_propagate(False)
        
        # Заголовок чата
        self.chat_header = ctk.CTkFrame(self.chat_frame, height=40, corner_radius=12, fg_color="#252526")
        self.chat_header.pack(fill="x", pady=(0, 10))
        self.chat_header.pack_propagate(False)
        
        self.chat_title = ctk.CTkLabel(
            self.chat_header,
            text="💬 История диалогов",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFFFFF"
        )
        self.chat_title.pack(expand=True)
        
        self.chat_text = ctk.CTkTextbox(self.chat_frame, wrap="word", font=ctk.CTkFont(size=11),
                                       fg_color="#2D2D2D", border_width=0)
        self.chat_text.pack(fill="both", expand=True, pady=(0, 10))
        self.chat_text.configure(state="disabled")
        
        # ========== ПОЛЕ ВВОДА ==========
        self.input_frame = ctk.CTkFrame(self.chat_frame, height=45, corner_radius=12, fg_color="#252526")
        self.input_frame.pack(fill="x", pady=(0, 10))
        self.input_frame.pack_propagate(False)
        
        self.input_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="💬 Введите сообщение... (Ctrl+Z/Y - отмена/повтор)", 
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            border_width=0
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=8)
        self.input_entry.bind("<Return>", lambda e: self.send_text_command())
        self.input_entry.bind("<Button-3>", self.show_context_menu)
        self.input_entry.bind("<KeyRelease>", lambda e: self.save_state())
        
        self.send_button = ctk.CTkButton(
            self.input_frame, text="📤", width=40, height=32,
            command=self.send_text_command, 
            fg_color="#0078D4", hover_color="#106EBE",
            corner_radius=10
        )
        self.send_button.pack(side="right", padx=(0, 10), pady=6)
        
        # ========== КНОПКИ УПРАВЛЕНИЯ ==========
        bottom_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=(0, 10))
        
        btn_style = {"width": 45, "height": 32, "corner_radius": 8}
        
        self.clear_chat_btn = ctk.CTkButton(bottom_frame, text="🗑", command=self.clear_chat, 
                                           fg_color="#555555", hover_color="#777777", **btn_style)
        self.clear_chat_btn.pack(side="left", padx=5, expand=True, fill="x")
        
        self.reset_button = ctk.CTkButton(bottom_frame, text="🔄", command=self.reset_bot, 
                                         fg_color="#555555", hover_color="#777777", **btn_style)
        self.reset_button.pack(side="left", padx=5, expand=True, fill="x")
        
        self.exit_button = ctk.CTkButton(bottom_frame, text="✖", command=self.exit_app, 
                                        fg_color="#D32F2F", hover_color="#B71C1C", **btn_style)
        self.exit_button.pack(side="left", padx=5, expand=True, fill="x")
        
        # ========== ЗАПУСК ВИДЕО ==========
        if hasattr(self, 'chumei') and hasattr(self.chumei, 'avatar'):
            print("🎬 Запускаем видео из UI...")
            self.chumei.avatar.set_label(self.video_label)
            self.chumei.avatar.start()
    
    def create_girl_card(self, frame, girl_name):
        girls_data = {
            "chuchu": ("👧 Чучу", "Японочка, косплей-модель", "icon_chuchu.png"),
            "mei": ("👩 Мэй", "Вьетнамка, крафтерша", "icon_mei.png"),
            "hana": ("🐰 Хана Банни", "Модель, любит дошик", "icon_hana.png"),
            "ki": ("🥔 Ки (Potato)", "Стеснительный косплеер", "icon_ki.png"),
            "simone": ("🎤 Симона", "Вокалистка Epica", "icon_simone.png")
        }
        name_text, subtitle, icon_file = girls_data.get(girl_name, (girl_name, "", ""))
        
        frame.grid_columnconfigure(1, weight=1)
        
        # Аватар 80x80
        icon_path = os.path.join("assets", "Avatars pic", icon_file)
        if os.path.exists(icon_path):
            try:
                original = Image.open(icon_path)
                original.thumbnail((80, 80), Image.Resampling.LANCZOS)
                avatar_img = ctk.CTkImage(light_image=original, dark_image=original, size=(original.width, original.height))
                avatar_label = ctk.CTkLabel(frame, image=avatar_img, text="")
                avatar_label.grid(row=0, column=0, padx=(12, 8), pady=12, rowspan=2)
                avatar_label.bind("<Button-1>", lambda e, name=girl_name: self.open_gallery(name))
            except:
                avatar_label = ctk.CTkLabel(frame, text=name_text[:2], font=ctk.CTkFont(size=36))
                avatar_label.grid(row=0, column=0, padx=(12, 8), pady=12, rowspan=2)
        else:
            avatar_label = ctk.CTkLabel(frame, text=name_text[:2], font=ctk.CTkFont(size=36))
            avatar_label.grid(row=0, column=0, padx=(12, 8), pady=12, rowspan=2)
        
        name_label = ctk.CTkLabel(frame, text=name_text, font=ctk.CTkFont(size=13, weight="bold"))
        name_label.grid(row=0, column=1, sticky="w", padx=(0, 5), pady=(12, 0))
        
        subtitle_label = ctk.CTkLabel(frame, text=subtitle, font=ctk.CTkFont(size=10), text_color="#888888")
        subtitle_label.grid(row=1, column=1, sticky="w", padx=(0, 5))
        
        # Прогресс-бар
        progress = ctk.CTkProgressBar(frame, width=130, height=6, corner_radius=3)
        progress.grid(row=0, column=2, padx=5, pady=12)
        progress.set(0.5)
        
        val = ctk.CTkLabel(frame, text="50", font=ctk.CTkFont(size=11), width=35)
        val.grid(row=0, column=3, padx=5)
        
        floor_label = ctk.CTkLabel(frame, text="🏢🏢", font=ctk.CTkFont(size=14), width=40)
        floor_label.grid(row=0, column=4, padx=5)
        
        frame.progress = progress
        frame.relation_value = val
        frame.floor_label = floor_label
        frame.girl_name = girl_name
    
    def open_gallery(self, girl_name):
        base_path = os.path.join("assets", "girls", girl_name)
        image_paths = []
        if os.path.exists(base_path):
            image_paths = [os.path.join(base_path, f) for f in os.listdir(base_path) 
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if image_paths:
            try:
                from photo_gallery import GirlGallery
                gallery = GirlGallery(self.root, girl_name, image_paths)
            except ImportError:
                messagebox.showinfo("Фотоальбом", f"Для {girl_name} найдено {len(image_paths)} фото")
        else:
            messagebox.showinfo("Нет фото", f"📸 Для {girl_name} пока нет фото")
    
    # ========== ПОТОКОБЕЗОПАСНЫЕ МЕТОДЫ ==========
    
    def add_chat_message(self, speaker, text, is_user=False):
        def _add():
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                if is_user:
                    line = f"[{timestamp}] 👤 {speaker}: {text}\n"
                else:
                    line = f"[{timestamp}] 💬 {speaker}: {text}\n"
                self.chat_text.configure(state="normal")
                self.chat_text.insert("end", line)
                self.chat_text.see("end")
                self.chat_text.configure(state="disabled")
            except Exception as e:
                print(f"⚠️ Ошибка: {e}")
        
        if self.root and self.root.winfo_exists():
            self.root.after(0, _add)
    
    def update_data(self):
        def _update():
            try:
                for girl, frame in self.girl_frames.items():
                    level = getattr(self.chumei, f"affection_{girl}", 50)
                    frame.progress.set(level / 100)
                    frame.relation_value.configure(text=str(level))
                    floor = level // 20
                    frame.floor_label.configure(text="🏢" * (floor + 1))
            except Exception as e:
                print(f"⚠️ Ошибка обновления: {e}")
        
        if self.root and self.root.winfo_exists():
            self.root.after(0, _update)
    
    def clear_chat(self):
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        self.chat_text.configure(state="disabled")
        print("🗑 Чат очищен")
    
    def send_text_command(self):
        text = self.input_entry.get().strip()
        if not text:
            return
        self.save_state()
        self.input_entry.delete(0, "end")
        self.current_text = ""
        self.add_chat_message("Вы", text, is_user=True)
        if hasattr(self, 'chumei'):
            asyncio.create_task(self.chumei.process_text_command(text))
    
    def update_loop(self):
        if self.root.winfo_exists():
            self.update_data()
            self.root.after(1000, self.update_loop)
    
    def reset_bot(self):
        self.chumei.story_playing = False
        self.chumei.sleep_mode = False
        self.chumei.is_processing = False
        self.chumei.censorship_mode = True
        self.chumei.story_index = 0
        print("🔄 Бот сброшен")
    
    def exit_app(self):
        print("👋 Закрытие...")
        if hasattr(self.chumei, 'avatar'):
            self.chumei.avatar.stop()
        self.chumei.running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        self.root.mainloop()