"""
Photo Gallery — фотоальбом с личным делом для ChuMei Angels
Стиль Windows 11 Dark Theme
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class GirlGallery:
    """Фотоальбом с личным делом для каждой девочки в стиле Windows 11"""
    
    # Цветовая схема Windows 11 Dark
    COLORS = {
        "bg_dark": "#1C1C1C",      # основной фон
        "bg_light": "#2D2D2D",      # светлый фон для карточек
        "bg_hover": "#3D3D3D",      # при наведении
        "accent": "#0078D4",        # акцентный синий
        "accent_hover": "#106EBE",  # акцент при наведении
        "text_primary": "#FFFFFF",   # основной текст
        "text_secondary": "#A0A0A0", # второстепенный текст
        "border": "#404040",         # границы
        "success": "#6B8C42",        # зелёный
        "warning": "#C42B1C",        # красный
    }
    
    # Личные дела девочек
    PERSONAL_FILES = {
        "chuchu": {
            "name": "Чучу",
            "full_name": "Чучу (ChuChu)",
            "age": "19 лет",
            "birthday": "14 февраля",
            "sign": "Водолей",
            "height": "158 см",
            "weight": "48 кг",
            "hobby": "Косплей, аниме, танцы",
            "likes": "Косплей, сладости, рамен, Pokémon",
            "dislikes": "Одиночество, грубость",
            "personality": "Весёлая, энергичная, немного капризная, обожает внимание",
            "dream": "Стать известной косплей-моделью и объездить весь мир",
            "quote": "Бака! Ты дурак, да? Хи-хи-хи!",
            "voice": "Xenia (Silero TTS)",
            "color": "#FF69B4"
        },
        "mei": {
            "name": "Мэй",
            "full_name": "Мэй Нгуен (Mei Nguyen)",
            "age": "21 год",
            "birthday": "30 апреля",
            "sign": "Телец",
            "height": "162 см",
            "weight": "55 кг",
            "hobby": "Крафт, DIY, рисование",
            "likes": "Рукоделие, чай с жасмином, вьетнамская кухня",
            "dislikes": "Хаос, беспорядок",
            "personality": "Спокойная, рассудительная, заботливая, любит порядок",
            "dream": "Открыть свою мастерскую авторских украшений",
            "quote": "Ара-ара... У тебя золотые руки!",
            "voice": "Baya (Silero TTS)",
            "color": "#98FB98"
        },
        "hana": {
            "name": "Хана",
            "full_name": "Хана Банни (Hana Bunny)",
            "age": "20 лет",
            "birthday": "1 апреля",
            "sign": "Овен",
            "height": "155 см",
            "weight": "47 кг",
            "hobby": "Еда, прыжки, косплей",
            "likes": "Дошик, деньги, зайки, сладкое",
            "dislikes": "Голод, скуку",
            "personality": "Энергичная, жизнерадостная, немного наивная, обожает покушать",
            "dream": "Открыть свой ресторан лапши",
            "quote": "Банихоп-хоп! Дошик — это жизнь!",
            "voice": "Hana (Silero TTS)",
            "color": "#FFD700"
        },
        "ki": {
            "name": "Ки",
            "full_name": "Ки (Potato)",
            "age": "18 лет",
            "birthday": "27 августа",
            "sign": "Дева",
            "height": "150 см",
            "weight": "42 кг",
            "hobby": "Рисование, чтение, косплей",
            "likes": "Тишина, уют, картошка, одиночество",
            "dislikes": "Шумные компании, внимание к себе",
            "personality": "Стеснительная, тихая, застенчивая, очень добрая",
            "dream": "Нарисовать свою мангу",
            "quote": "Извините... я картошка...",
            "voice": "Potato (Silero TTS)",
            "color": "#DDA0DD"
        },
        "simone": {
            "name": "Симона",
            "full_name": "Симона Симонс (Simone Simons)",
            "age": "24 года",
            "birthday": "17 января",
            "sign": "Козерог",
            "height": "168 см",
            "weight": "58 кг",
            "hobby": "Музыка, пение, опера",
            "likes": "Металл, классическая музыка, Epica, кошки",
            "dislikes": "Фальшь, неискренность",
            "personality": "Страстная, артистичная, вдохновляющая, харизматичная",
            "dream": "Покорить мировую сцену с Epica",
            "quote": "Музыка — это любовь!",
            "voice": "Kseniya (Silero TTS)",
            "color": "#87CEEB"
        }
    }
    
    def __init__(self, parent, girl_name, image_paths):
        self.parent = parent
        self.girl_name = girl_name
        self.image_paths = image_paths
        self.current_index = 0
        self.zoom_window = None
        self.slideshow_running = False
        self.slideshow_id = None
        
        self.personal = self.PERSONAL_FILES.get(girl_name, {})
        self.display_name = self.personal.get("name", girl_name.capitalize())
        
        # Создаём окно в стиле Windows 11
        self.window = tk.Toplevel(parent)
        self.window.title(f"📸 {self.display_name} — ChuMei Angels")
        self.window.geometry("950x700")
        self.window.configure(bg=self.COLORS["bg_dark"])
        
        # Убираем стандартные границы и добавляем свой заголовок
        self.window.overrideredirect(True)
        self.setup_custom_titlebar()
        
        # Создаём вкладки
        self.setup_notebook()
        
        self.center_window()
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def setup_custom_titlebar(self):
        """Создаёт кастомный заголовок в стиле Windows 11"""
        self.titlebar = tk.Frame(self.window, bg=self.COLORS["bg_light"], height=32)
        self.titlebar.pack(fill="x", side="top")
        self.titlebar.pack_propagate(False)
        
        # Иконка и заголовок
        title_text = f"ChuMei Angels — {self.display_name}"
        title_label = tk.Label(
            self.titlebar, 
            text=title_text,
            font=("Segoe UI", 11),
            bg=self.COLORS["bg_light"],
            fg=self.COLORS["text_primary"]
        )
        title_label.pack(side="left", padx=12, pady=6)
        
        # Кнопка закрытия
        close_btn = tk.Button(
            self.titlebar,
            text="✖",
            font=("Segoe UI", 10),
            bg=self.COLORS["bg_light"],
            fg=self.COLORS["text_primary"],
            relief="flat",
            activebackground=self.COLORS["warning"],
            activeforeground="white",
            cursor="hand2",
            command=self.close
        )
        close_btn.pack(side="right", padx=8, pady=4)
        
        # Возможность перетаскивать окно
        self.titlebar.bind("<Button-1>", self.start_move)
        self.titlebar.bind("<B1-Motion>", self.on_move)
        title_label.bind("<Button-1>", self.start_move)
        title_label.bind("<B1-Motion>", self.on_move)
    
    def start_move(self, event):
        self.x = event.x
        self.y = event.y
    
    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.window.winfo_x() + deltax
        y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{x}+{y}")
    
    def setup_notebook(self):
        """Создаёт стилизованные вкладки"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Стиль для вкладок
        style.configure("Custom.TNotebook", background=self.COLORS["bg_dark"], borderwidth=0)
        style.configure("Custom.TNotebook.Tab", 
                       background=self.COLORS["bg_light"],
                       foreground=self.COLORS["text_secondary"],
                       padding=[20, 8],
                       font=("Segoe UI", 10))
        style.map("Custom.TNotebook.Tab",
                 background=[("selected", self.COLORS["accent"])],
                 foreground=[("selected", "white")])
        
        self.notebook = ttk.Notebook(self.window, style="Custom.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Вкладка с фото
        self.setup_photo_tab()
        
        # Вкладка с личным делом
        self.setup_profile_tab()
    
    def setup_photo_tab(self):
        """Вкладка с фотоальбомом"""
        self.photo_frame = tk.Frame(self.notebook, bg=self.COLORS["bg_dark"])
        self.notebook.add(self.photo_frame, text="📸 Фотоальбом")
        
        # Верхняя панель с информацией
        info_frame = tk.Frame(self.photo_frame, bg=self.COLORS["bg_dark"])
        info_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        self.counter_label = tk.Label(
            info_frame,
            text=f"📷 Фото {self.current_index + 1} из {len(self.image_paths)}" if self.image_paths else "Нет фото",
            font=("Segoe UI", 12),
            bg=self.COLORS["bg_dark"],
            fg=self.COLORS["text_secondary"]
        )
        self.counter_label.pack(side="left")
        
        # Панель управления
        control_frame = tk.Frame(self.photo_frame, bg=self.COLORS["bg_dark"])
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # Стилизованные кнопки
        btn_style = {
            "font": ("Segoe UI", 11),
            "bg": self.COLORS["bg_light"],
            "fg": self.COLORS["text_primary"],
            "relief": "flat",
            "cursor": "hand2",
            "padx": 15,
            "pady": 6
        }
        
        self.prev_btn = tk.Button(
            control_frame,
            text="◀ Назад",
            command=self.prev_image,
            **btn_style
        )
        self.prev_btn.pack(side="left", padx=5)
        self.prev_btn.bind("<Enter>", lambda e: self.prev_btn.configure(bg=self.COLORS["bg_hover"]))
        self.prev_btn.bind("<Leave>", lambda e: self.prev_btn.configure(bg=self.COLORS["bg_light"]))
        
        self.slideshow_btn = tk.Button(
            control_frame,
            text="▶ Слайд-шоу",
            command=self.toggle_slideshow,
            **btn_style
        )
        self.slideshow_btn.pack(side="left", padx=5)
        self.slideshow_btn.bind("<Enter>", lambda e: self.slideshow_btn.configure(bg=self.COLORS["bg_hover"]))
        self.slideshow_btn.bind("<Leave>", lambda e: self.slideshow_btn.configure(bg=self.COLORS["bg_light"]))
        
        self.next_btn = tk.Button(
            control_frame,
            text="Вперед ▶",
            command=self.next_image,
            **btn_style
        )
        self.next_btn.pack(side="left", padx=5)
        self.next_btn.bind("<Enter>", lambda e: self.next_btn.configure(bg=self.COLORS["bg_hover"]))
        self.next_btn.bind("<Leave>", lambda e: self.next_btn.configure(bg=self.COLORS["bg_light"]))
        
        # Область для фото
        self.image_container = tk.Frame(self.photo_frame, bg=self.COLORS["bg_dark"])
        self.image_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.image_label = tk.Label(
            self.image_container,
            bg=self.COLORS["bg_dark"],
            cursor="hand2"
        )
        self.image_label.pack(expand=True)
        self.image_label.bind("<Button-1>", self.zoom_image)
        
        # Загружаем первое фото
        if self.image_paths:
            self.load_image()
        else:
            self.image_label.config(text="📸 Нет фото", font=("Segoe UI", 16), fg=self.COLORS["text_secondary"])
    
    def setup_profile_tab(self):
        """Вкладка с личным делом"""
        self.profile_frame = tk.Frame(self.notebook, bg=self.COLORS["bg_dark"])
        self.notebook.add(self.profile_frame, text="📋 Личное дело")
        
        if not self.personal:
            no_data = tk.Label(
                self.profile_frame,
                text="Информация о персонаже в разработке",
                font=("Segoe UI", 14),
                bg=self.COLORS["bg_dark"],
                fg=self.COLORS["text_secondary"]
            )
            no_data.pack(expand=True)
            return
        
        # Canvas для скроллинга
        canvas = tk.Canvas(self.profile_frame, bg=self.COLORS["bg_dark"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.profile_frame, orient="vertical", command=canvas.yview, 
                                 bg=self.COLORS["bg_light"], troughcolor=self.COLORS["bg_dark"])
        scrollable_frame = tk.Frame(canvas, bg=self.COLORS["bg_dark"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Аватар и имя
        color = self.personal.get("color", self.COLORS["accent"])
        
        header_frame = tk.Frame(scrollable_frame, bg=self.COLORS["bg_dark"])
        header_frame.pack(fill="x", pady=(20, 10))
        
        # Заголовок с именем
        name_label = tk.Label(
            header_frame,
            text=f"📋 {self.personal.get('name', '')}",
            font=("Segoe UI", 22, "bold"),
            bg=self.COLORS["bg_dark"],
            fg=color
        )
        name_label.pack()
        
        # Полное имя
        tk.Label(
            header_frame,
            text=self.personal.get("full_name", "—"),
            font=("Segoe UI", 12),
            bg=self.COLORS["bg_dark"],
            fg=self.COLORS["text_secondary"]
        ).pack()
        
        # Разделитель
        separator = tk.Frame(scrollable_frame, height=2, bg=self.COLORS["border"])
        separator.pack(fill="x", padx=40, pady=15)
        
        # Основная информация
        info_frame = tk.Frame(scrollable_frame, bg=self.COLORS["bg_dark"])
        info_frame.pack(fill="x", padx=40, pady=5)
        
        # Возраст, день рождения, знак
        self._add_info_card(info_frame, "🎂 Возраст", self.personal.get("age", "—"))
        self._add_info_card(info_frame, "📅 День рождения", self.personal.get("birthday", "—"))
        self._add_info_card(info_frame, "⭐ Знак зодиака", self.personal.get("sign", "—"))
        
        # Параметры
        params_frame = tk.Frame(scrollable_frame, bg=self.COLORS["bg_dark"])
        params_frame.pack(fill="x", padx=40, pady=5)
        
        self._add_info_card(params_frame, "📏 Рост", self.personal.get("height", "—"))
        self._add_info_card(params_frame, "⚖️ Вес", self.personal.get("weight", "—"))
        
        # Разделитель
        separator2 = tk.Frame(scrollable_frame, height=2, bg=self.COLORS["border"])
        separator2.pack(fill="x", padx=40, pady=15)
        
        # Хобби, интересы, характер
        self._add_section(scrollable_frame, "🎯 Хобби", self.personal.get("hobby", "—"))
        self._add_section(scrollable_frame, "❤️ Любит", self.personal.get("likes", "—"))
        self._add_section(scrollable_frame, "💔 Не любит", self.personal.get("dislikes", "—"))
        self._add_section(scrollable_frame, "🎭 Характер", self.personal.get("personality", "—"))
        self._add_section(scrollable_frame, "✨ Мечта", self.personal.get("dream", "—"))
        
        # Любимая фраза
        phrase = self.personal.get("quote", "—")
        quote_frame = tk.Frame(scrollable_frame, bg=self.COLORS["bg_light"], relief="flat", bd=1)
        quote_frame.pack(fill="x", padx=40, pady=15)
        
        tk.Label(
            quote_frame,
            text=f"«{phrase}»",
            font=("Segoe UI", 11, "italic"),
            bg=self.COLORS["bg_light"],
            fg=color,
            wraplength=700
        ).pack(pady=15, padx=20)
        
        # Голос
        voice_frame = tk.Frame(scrollable_frame, bg=self.COLORS["bg_dark"])
        voice_frame.pack(fill="x", padx=40, pady=10)
        
        tk.Label(
            voice_frame,
            text="🎤 Голос:",
            font=("Segoe UI", 11, "bold"),
            bg=self.COLORS["bg_dark"],
            fg=self.COLORS["text_primary"]
        ).pack(side="left")
        tk.Label(
            voice_frame,
            text=self.personal.get("voice", "—"),
            font=("Segoe UI", 11),
            bg=self.COLORS["bg_dark"],
            fg=self.COLORS["text_secondary"]
        ).pack(side="left", padx=10)
    
    def _add_info_card(self, parent, label, value):
        """Добавляет карточку с информацией"""
        card = tk.Frame(parent, bg=self.COLORS["bg_light"], relief="flat", bd=0)
        card.pack(side="left", expand=True, fill="x", padx=5, pady=5)
        
        tk.Label(
            card,
            text=label,
            font=("Segoe UI", 10),
            bg=self.COLORS["bg_light"],
            fg=self.COLORS["text_secondary"]
        ).pack(pady=(8, 0))
        tk.Label(
            card,
            text=value,
            font=("Segoe UI", 13, "bold"),
            bg=self.COLORS["bg_light"],
            fg=self.COLORS["text_primary"]
        ).pack(pady=(0, 8))
    
    def _add_section(self, parent, title, content):
        """Добавляет секцию с заголовком и содержимым"""
        frame = tk.Frame(parent, bg=self.COLORS["bg_dark"])
        frame.pack(fill="x", padx=40, pady=8)
        
        # Заголовок
        title_frame = tk.Frame(frame, bg=self.COLORS["bg_dark"])
        title_frame.pack(fill="x")
        
        tk.Label(
            title_frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            bg=self.COLORS["bg_dark"],
            fg=self.COLORS["accent"]
        ).pack(anchor="w")
        
        # Содержимое
        tk.Label(
            frame,
            text=content,
            font=("Segoe UI", 11),
            bg=self.COLORS["bg_dark"],
            fg=self.COLORS["text_primary"],
            wraplength=750,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(5, 0))
    
    def center_window(self):
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_image(self):
        if not self.image_paths:
            return
        
        path = self.image_paths[self.current_index]
        try:
            img = Image.open(path)
            img.thumbnail((650, 500), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
            self.counter_label.configure(text=f"📷 Фото {self.current_index + 1} из {len(self.image_paths)}")
        except Exception as e:
            self.image_label.configure(text=f"Ошибка загрузки: {e}", image="")
    
    def prev_image(self):
        if self.image_paths:
            self.current_index = (self.current_index - 1) % len(self.image_paths)
            self.load_image()
    
    def next_image(self):
        if self.image_paths:
            self.current_index = (self.current_index + 1) % len(self.image_paths)
            self.load_image()
    
    def zoom_image(self, event=None):
        if not self.image_paths:
            return
        
        path = self.image_paths[self.current_index]
        try:
            img = Image.open(path)
            zoom = tk.Toplevel(self.window)
            zoom.title("Просмотр фото — ChuMei Angels")
            zoom.configure(bg=self.COLORS["bg_dark"])
            
            screen_width = zoom.winfo_screenwidth()
            screen_height = zoom.winfo_screenheight()
            
            img.thumbnail((screen_width - 100, screen_height - 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            label = tk.Label(zoom, image=photo, bg=self.COLORS["bg_dark"])
            label.image = photo
            label.pack(padx=20, pady=20)
            
            close_btn = tk.Button(
                zoom,
                text="Закрыть",
                font=("Segoe UI", 11),
                bg=self.COLORS["accent"],
                fg="white",
                relief="flat",
                cursor="hand2",
                command=zoom.destroy
            )
            close_btn.pack(pady=10)
            
            zoom.update_idletasks()
            w, h = zoom.winfo_width(), zoom.winfo_height()
            x = (screen_width - w) // 2
            y = (screen_height - h) // 2
            zoom.geometry(f"+{x}+{y}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть фото: {e}")
    
    def toggle_slideshow(self):
        if self.slideshow_running:
            self.stop_slideshow()
        else:
            self.start_slideshow()
    
    def start_slideshow(self):
        self.slideshow_running = True
        self.slideshow_btn.configure(text="⏸ Стоп", bg=self.COLORS["warning"])
        self._slideshow_step()
    
    def stop_slideshow(self):
        self.slideshow_running = False
        self.slideshow_btn.configure(text="▶ Слайд-шоу", bg=self.COLORS["bg_light"])
        if self.slideshow_id:
            self.window.after_cancel(self.slideshow_id)
            self.slideshow_id = None
    
    def _slideshow_step(self):
        if self.slideshow_running:
            self.next_image()
            self.slideshow_id = self.window.after(3000, self._slideshow_step)
    
    def close(self):
        self.stop_slideshow()
        self.window.destroy()