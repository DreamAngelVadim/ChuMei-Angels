"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CHUMEI ANGELS - UI DASHBOARD                         ║
║                                                                              ║
║   Интерфейс в стиле Windows 11 (тёмная тема, Mica, скруглённые углы)        ║
║   Отображает: состояние девочек, шкалу отношений, последние реплики         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
import threading
from datetime import datetime

# Настройка темы
ctk.set_appearance_mode("dark")  # Тёмная тема
ctk.set_default_color_theme("blue")  # Акцентный цвет Windows 11


class ChuMeiUI:
    def __init__(self, chumei_instance):
        """
        Параметры:
            chumei_instance: экземпляр класса ChuMei (для получения данных)
        """
        self.chumei = chumei_instance
        
        # Создание главного окна
        self.root = ctk.CTk()
        self.root.title("ChuMei Angels — виртуальный особняк в Сибуе")
        self.root.geometry("900x650")
        
        # Делаем окно полупрозрачным (эффект Mica в Windows 11)
        self.root.attributes('-alpha', 0.96)
        
        # Центрируем окно
        self.center_window()
        
        # Создаём интерфейс
        self.setup_ui()
        
        # Запускаем обновление данных (раз в секунду)
        self.update_loop()
    
    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Создаёт все элементы интерфейса"""
        
        # ========== ВЕРХНЯЯ ПАНЕЛЬ (заголовок) ==========
        self.header_frame = ctk.CTkFrame(self.root, height=60, corner_radius=0)
        self.header_frame.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🏠 ChuMei Angels — особняк в Сибуе, Токио",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.pack(side="left", padx=20, pady=15)
        
        # ========== ОСНОВНАЯ ОБЛАСТЬ (карточки девочек) ==========
        self.main_frame = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Создаём карточки для 5 девочек (в 2 ряда: 3 + 2)
        self.girl_frames = {}
        girls = ["chuchu", "mei", "hana", "ki", "simone"]
        
        # Первые 3 в верхнем ряду
        top_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=5)
        
        for i, girl in enumerate(girls[:3]):
            frame = ctk.CTkFrame(top_row, corner_radius=15, border_width=1, border_color="#2A2A2A")
            frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)
            self.girl_frames[girl] = frame
            self.create_girl_card(frame, girl)
        
        # Оставшиеся 2 в нижнем ряду
        bottom_row = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_row.pack(fill="x", pady=5)
        
        for i, girl in enumerate(girls[3:]):
            frame = ctk.CTkFrame(bottom_row, corner_radius=15, border_width=1, border_color="#2A2A2A")
            frame.pack(side="left", expand=True, fill="both", padx=5, pady=5)
            self.girl_frames[girl] = frame
            self.create_girl_card(frame, girl)
        
        # ========== НИЖНЯЯ ПАНЕЛЬ (статус и микрофон) ==========
        self.status_frame = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        self.status_frame.pack(fill="x", side="bottom", padx=0, pady=0)
        self.status_frame.pack_propagate(False)
        
        # Статус микрофона
        self.mic_status = ctk.CTkLabel(
            self.status_frame,
            text="🎤 Микрофон активен",
            font=ctk.CTkFont(size=14),
            text_color="#00FF00"
        )
        self.mic_status.pack(side="left", padx=20, pady=25)
        
        # Последняя реплика
        self.last_phrase_label = ctk.CTkLabel(
            self.status_frame,
            text="💬 Последняя реплика: —",
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        self.last_phrase_label.pack(side="left", padx=30, pady=25, fill="x", expand=True)
        
        # Кнопка выхода
        self.exit_button = ctk.CTkButton(
            self.status_frame,
            text="Выход",
            width=80,
            command=self.exit_app,
            fg_color="#D32F2F",
            hover_color="#B71C1C"
        )
        self.exit_button.pack(side="right", padx=20, pady=20)
    
    def create_girl_card(self, frame, girl_name):
        """Создаёт карточку для одной девочки"""
        # Имя и эмодзи
        names = {
            "chuchu": ("👧 Чучу", "Японочка, косплей-модель"),
            "mei": ("👩 Мэй", "Вьетнамка, крафтерша"),
            "hana": ("🐰 Хана Банни", "Модель, любит дошик"),
            "ki": ("🥔 Ки (Potato)", "Стеснительный косплеер"),
            "simone": ("🎤 Симона", "Вокалистка Epica")
        }
        
        name_text, subtitle = names.get(girl_name, (girl_name, ""))
        
        name_label = ctk.CTkLabel(
            frame,
            text=name_text,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        )
        name_label.pack(anchor="w", padx=15, pady=(10, 0))
        
        subtitle_label = ctk.CTkLabel(
            frame,
            text=subtitle,
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            anchor="w"
        )
        subtitle_label.pack(anchor="w", padx=15, pady=(0, 5))
        
        # Прогресс-бар отношений
        relation_label = ctk.CTkLabel(frame, text="❤️ Отношения:", font=ctk.CTkFont(size=12), anchor="w")
        relation_label.pack(anchor="w", padx=15, pady=(5, 0))
        
        progress = ctk.CTkProgressBar(frame, width=200, height=8, corner_radius=4)
        progress.pack(anchor="w", padx=15, pady=(2, 0))
        progress.set(0.5)  # Временное значение
        
        relation_value = ctk.CTkLabel(frame, text="50 / 100", font=ctk.CTkFont(size=10), text_color="#AAAAAA")
        relation_value.pack(anchor="w", padx=15, pady=(2, 5))
        
        # Этаж
        floor_label = ctk.CTkLabel(frame, text="🏢 Этаж: 1 (Холл)", font=ctk.CTkFont(size=12), anchor="w")
        floor_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Сохраняем ссылки на динамические элементы
        frame.progress = progress
        frame.relation_value = relation_value
        frame.floor_label = floor_label
        frame.girl_name = girl_name
    
    def update_loop(self):
        """Обновляет данные на экране раз в секунду"""
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.update_data()
            self.root.after(1000, self.update_loop)
    
    def update_data(self):
        """Обновляет данные для всех девочек"""
        # Временно — заглушка. Потом возьмёшь реальные данные из self.chumei
        for girl_name, frame in self.girl_frames.items():
            # Получаем уровень отношений (если есть)
            level = getattr(self.chumei, f"affection_{girl_name}", 50)
            frame.progress.set(level / 100)
            frame.relation_value.configure(text=f"{level} / 100")
            
            # Обновляем этаж (заглушка)
            floor_names = {0: "Холл", 1: "Гостиная", 2: "Комната", 3: "Спальня", 4: "Душа"}
            floor = level // 20
            frame.floor_label.configure(text=f"🏢 Этаж: {floor + 1} ({floor_names.get(floor, 'Холл')})")
        
        # Обновляем статус микрофона (если есть флаг)
        if hasattr(self.chumei, 'is_processing'):
            if self.chumei.is_processing:
                self.mic_status.configure(text="🟢 Микрофон активен", text_color="#00FF00")
            else:
                self.mic_status.configure(text="🔴 Микрофон слушает", text_color="#FFA500")
    
    def update_last_phrase(self, girl_name, text):
        """Обновляет последнюю реплику в интерфейсе"""
        names = {"chuchu": "Чучу", "mei": "Мэй", "hana": "Хана", "ki": "Ки", "simone": "Симона"}
        display_name = names.get(girl_name, girl_name)
        short_text = text[:80] + "..." if len(text) > 80 else text
        self.last_phrase_label.configure(text=f"💬 {display_name}: {short_text}")
    
    def exit_app(self):
        """Корректное завершение приложения"""
        self.root.destroy()
        self.chumei.running = False
    
    def run(self):
        """Запускает интерфейс в отдельном потоке"""
        self.root.mainloop()