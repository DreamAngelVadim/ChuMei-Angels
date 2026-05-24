"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CHUMEI ANGELS - UI DASHBOARD v7.1                    ║
║                                                                              ║
║   ГЛАВНЫЙ ИНТЕРФЕЙС ПОЛЬЗОВАТЕЛЯ                                             ║
║                                                                              ║
║   📌 ОСОБЕННОСТИ:                                                            ║
║   • РАБОТАЮЩИЕ горячие клавиши (Ctrl+C/V/X/A/Z/Y)                           ║
║   • Вывод ВСЕХ диалогов в чат (истории, цепочки, случайные)                 ║
║   • Увеличенные карточки девочек                                            ║
║   • Видео-аватар                                                            ║
║   • Поддержка girl_id для будущих аватаров                                  ║
║                                                                              ║
║   🎯 ГОРЯЧИЕ КЛАВИШИ:                                                        ║
║   Ctrl+C - копировать | Ctrl+V - вставить | Ctrl+X - вырезать               ║
║   Ctrl+A - выделить всё | Ctrl+Z - отмена | Ctrl+Y - повтор                 ║
║   Enter - отправить сообщение                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import customtkinter as ctk
from datetime import datetime
import os
import asyncio
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import sys


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class ModernToolTip:
    """Всплывающие подсказки"""
    
    def __init__(self, widget, text, title=None, delay=500):
        self.widget = widget
        self.text = text
        self.title = title
        self.delay = delay
        self.tip_window = None
        self.after_id = None
        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event=None):
        self.after_id = self.widget.after(self.delay, self._show_tip)
    
    def _on_leave(self, event=None):
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None
        self._hide_tip()
    
    def _show_tip(self):
        if self.tip_window:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg="#2D2D2D")
        frame = tk.Frame(tw, bg="#2D2D2D", relief="solid", borderwidth=1)
        frame.pack()
        if self.title:
            title_label = tk.Label(
                frame, text=self.title, font=("Segoe UI", 10, "bold"),
                bg="#2D2D2D", fg="#0078D4"
            )
            title_label.pack(anchor="w", padx=8, pady=(6, 2))
        label = tk.Label(
            frame, text=self.text, justify="left", bg="#2D2D2D",
            fg="#FFFFFF", font=("Segoe UI", 9), wraplength=300
        )
        label.pack(anchor="w", padx=8, pady=(0, 6))
        tw.after(5000, self._hide_tip)
    
    def _hide_tip(self):
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except:
                pass
            self.tip_window = None


class ChuMeiUI:
    """ГЛАВНЫЙ КЛАСС ГРАФИЧЕСКОГО ИНТЕРФЕЙСА"""
    
    GIRLS_FULL_INFO = {
        "chuchu": {
            "name": "Чучу", "subtitle": "Японочка, косплэй-модель",
            "icon": "icon_chuchu.png", "color": "#FF69B4",
            "full_info": "🌸 Чучу — японская косплэй-модель\n📅 21 ноября\n📏 Рост: 153 см"
        },
        "mei": {
            "name": "Мэй", "subtitle": "Вьетнамка, крафтерша",
            "icon": "icon_mei.png", "color": "#98FB98",
            "full_info": "🌸 Мэй — вьетнамская крафтерша\n📅 30 апреля\n📏 Рост: 162 см"
        },
        "hana": {
            "name": "Хана", "subtitle": "Модель, любит дошик",
            "icon": "icon_hana.png", "color": "#FFD700",
            "full_info": "🌸 Хана Банни — модель\n📅 1 апреля\n📏 Рост: 155 см"
        },
        "ki": {
            "name": "Ки", "subtitle": "Стеснительный косплеер",
            "icon": "icon_ki.png", "color": "#DDA0DD",
            "full_info": "🌸 Ки — стеснительный косплеер\n📅 27 августа\n📏 Рост: 150 см"
        },
        "simone": {
            "name": "Симона", "subtitle": "Вокалистка Epica",
            "icon": "icon_simone.png", "color": "#87CEEB",
            "full_info": "🌸 Симона Симонс — вокалистка Epica\n📅 17 января\n📏 Рост: 168 см"
        }
    }
    
    def __init__(self, chumei_instance):
        self.chumei = chumei_instance
        self.undo_stack = []
        self.redo_stack = []
        self.current_text = ""
        
        self.root = ctk.CTk()
        self.root.title("ChuMei Angels — виртуальный особняк в Сибуе")
        self.root.geometry("1200x750")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        
        try:
            icon_path = resource_path("Asian.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
        
        self._setup_ui()
        self._setup_hotkeys()
        self._update_loop()
        self._center_window()
        
        self.input_entry.focus_set()
    
    def _center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ГОРЯЧИЕ КЛАВИШИ (РАБОТАЮТ)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _setup_hotkeys(self):
        """Настраивает горячие клавиши для поля ввода"""
        
        # Привязываем события к полю ввода
        self.input_entry.bind("<Control-c>", self._copy_text)
        self.input_entry.bind("<Control-v>", self._paste_text)
        self.input_entry.bind("<Control-x>", self._cut_text)
        self.input_entry.bind("<Control-a>", self._select_all)
        self.input_entry.bind("<Control-z>", self._undo)
        self.input_entry.bind("<Control-y>", self._redo)
        self.input_entry.bind("<Return>", lambda e: self._send_message())
        
        # Для ПКМ (контекстное меню)
        self.input_entry.bind("<Button-3>", self._show_context_menu)
        
        # Для отслеживания изменений
        self.input_entry.bind("<KeyRelease>", self._save_state)
        
        # Дополнительно привязываем к корневому окну (для глобальных хоткеев)
        self.root.bind("<Control-c>", lambda e: self._copy_text() if self.input_entry.focus_get() else None)
        self.root.bind("<Control-v>", lambda e: self._paste_text() if self.input_entry.focus_get() else None)
        self.root.bind("<Control-x>", lambda e: self._cut_text() if self.input_entry.focus_get() else None)
        self.root.bind("<Control-a>", lambda e: self._select_all() if self.input_entry.focus_get() else None)
        self.root.bind("<Control-z>", lambda e: self._undo() if self.input_entry.focus_get() else None)
        self.root.bind("<Control-y>", lambda e: self._redo() if self.input_entry.focus_get() else None)
        
        print("✅ Горячие клавиши настроены")
    
    def _save_state(self, event=None):
        if hasattr(self, 'input_entry') and self.input_entry.winfo_exists():
            current = self.input_entry.get()
            if current != self.current_text:
                self.undo_stack.append(self.current_text)
                self.current_text = current
                self.redo_stack.clear()
                if len(self.undo_stack) > 50:
                    self.undo_stack.pop(0)
    
    def _copy_text(self, event=None):
        try:
            selected = self.input_entry.selection_get()
            if selected:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected)
                print(f"📋 Скопировано: {selected[:50]}...")
        except:
            pass
        return "break"
    
    def _paste_text(self, event=None):
        try:
            # Принудительно устанавливаем фокус на поле ввода
            self.input_entry.focus_set()
            
            text = self.root.clipboard_get()
            if text:
                self._save_state()
                cursor = self.input_entry.index("insert")
                current = self.input_entry.get()
                new = current[:cursor] + text + current[cursor:]
                self.input_entry.delete(0, "end")
                self.input_entry.insert(0, new)
                self.input_entry.icursor(cursor + len(text))
                self.current_text = new
                print(f"📋 Вставлено: {text[:50]}...")
        except Exception as e:
            print(f"Ошибка вставки: {e}")
        return "break"
    
    def _cut_text(self, event=None):
        try:
            selected = self.input_entry.selection_get()
            if selected:
                self._save_state()
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
    
    def _select_all(self, event=None):
        self.input_entry.select_range(0, "end")
        self.input_entry.icursor("end")
        return "break"
    
    def _undo(self, event=None):
        if self.undo_stack:
            self.redo_stack.append(self.current_text)
            prev_text = self.undo_stack.pop()
            self.current_text = prev_text
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, prev_text or "")
            print("↩️ Отмена")
        return "break"
    
    def _redo(self, event=None):
        if self.redo_stack:
            self.undo_stack.append(self.current_text)
            next_text = self.redo_stack.pop()
            self.current_text = next_text
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, next_text or "")
            print("↪️ Возврат")
        return "break"
    
    def _show_context_menu(self, event):
        menu = tk.Menu(self.root, tearoff=0, bg="#2D2D2D", fg="white",
                       activebackground="#0078D4", activeforeground="white")
        menu.add_command(label="Копировать (Ctrl+C)", command=self._copy_text)
        menu.add_command(label="Вырезать (Ctrl+X)", command=self._cut_text)
        menu.add_command(label="Вставить (Ctrl+V)", command=self._paste_text)
        menu.add_separator()
        menu.add_command(label="Отменить (Ctrl+Z)", command=self._undo)
        menu.add_command(label="Повторить (Ctrl+Y)", command=self._redo)
        menu.add_separator()
        menu.add_command(label="Выделить всё (Ctrl+A)", command=self._select_all)
        menu.add_command(label="Очистить", command=lambda: self.input_entry.delete(0, "end"))
        menu.post(event.x_root, event.y_root)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ПОСТРОЕНИЕ ИНТЕРФЕЙСА
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _setup_ui(self):
        self.main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Верхняя панель
        self.top_panel = ctk.CTkFrame(
            self.main_container, height=160, corner_radius=15,
            fg_color="#1E1E1E", border_width=1, border_color="#3D3D3D"
        )
        self.top_panel.pack(fill="x", pady=(0, 10))
        self.top_panel.pack_propagate(False)
        
        self.cards_container = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.girl_frames = {}
        for girl_id in ["chuchu", "mei", "hana", "ki", "simone"]:
            card = self._create_horizontal_card(self.cards_container, girl_id)
            card.pack(side="left", expand=True, fill="both", padx=5)
            self.girl_frames[girl_id] = card
        
        # Нижняя панель
        self.bottom_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.bottom_panel.pack(fill="both", expand=True)
        
        self._setup_video_panel()
        self._setup_chat_panel()
    
    def _create_horizontal_card(self, parent, girl_id):
        info = self.GIRLS_FULL_INFO[girl_id]
        AVATAR_SIZE = 90
        
        card = ctk.CTkFrame(
            parent, corner_radius=12, border_width=1,
            border_color="#3D3D3D", fg_color="#252526", height=140
        )
        card.pack_propagate(False)
        
        icon_path = resource_path(os.path.join("assets", "Avatars pic", info["icon"]))
        if os.path.exists(icon_path):
            try:
                original = Image.open(icon_path)
                original.thumbnail((AVATAR_SIZE, AVATAR_SIZE), Image.Resampling.LANCZOS)
                square_img = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), "#252526")
                paste_x = (AVATAR_SIZE - original.width) // 2
                paste_y = (AVATAR_SIZE - original.height) // 2
                square_img.paste(original, (paste_x, paste_y))
                avatar_img = ctk.CTkImage(light_image=square_img, dark_image=square_img, size=(AVATAR_SIZE, AVATAR_SIZE))
                avatar_label = ctk.CTkLabel(card, image=avatar_img, text="")
                avatar_label.pack(pady=(10, 5))
                avatar_label.bind("<Button-1>", lambda e, g=girl_id: self._open_gallery(g))
                ModernToolTip(avatar_label, info["full_info"], title=f"📸 {info['name']}")
            except:
                avatar_label = ctk.CTkLabel(card, text=info["name"][:2], font=ctk.CTkFont(size=40))
                avatar_label.pack(pady=(10, 5))
        else:
            avatar_label = ctk.CTkLabel(card, text=info["name"][:2], font=ctk.CTkFont(size=40))
            avatar_label.pack(pady=(10, 5))
        
        name_label = ctk.CTkLabel(card, text=info["name"], font=ctk.CTkFont(size=14, weight="bold"))
        name_label.pack()
        ModernToolTip(name_label, f"Кликни для фотоальбома\n{info['subtitle']}", title=info["name"])
        
        progress = ctk.CTkProgressBar(card, width=80, height=6, corner_radius=3)
        progress.pack(pady=(5, 0))
        progress.set(0.5)
        
        bottom_frame = ctk.CTkFrame(card, fg_color="transparent")
        bottom_frame.pack(pady=(2, 8))
        
        val_label = ctk.CTkLabel(bottom_frame, text="50", font=ctk.CTkFont(size=11), width=35)
        val_label.pack(side="left")
        
        floor_label = ctk.CTkLabel(bottom_frame, text="🏢🏢", font=ctk.CTkFont(size=12), width=35)
        floor_label.pack(side="left")
        
        card.progress = progress
        card.relation_value = val_label
        card.floor_label = floor_label
        card.girl_name = girl_id
        
        return card
    
    def _setup_video_panel(self):
        self.video_frame = ctk.CTkFrame(
            self.bottom_panel, width=350, corner_radius=15,
            fg_color="#1E1E1E", border_width=1, border_color="#3D3D3D"
        )
        self.video_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.video_frame.pack_propagate(False)
        
        title = ctk.CTkLabel(self.video_frame, text="🎬 Видео-аватар",
                             font=ctk.CTkFont(size=12, weight="bold"), text_color="#0078D4")
        title.pack(pady=(10, 5))
        
        self.video_label = tk.Label(
            self.video_frame, text="🖼 Аватар загружается...",
            bg="#1E1E1E", fg="#A0A0A0", font=("Segoe UI", 11)
        )
        self.video_label.pack(expand=True, fill="both", padx=10, pady=(0, 10))
        
        self.video_status = ctk.CTkLabel(self.video_frame, text="🟡 Аватар инициализируется",
                                         font=ctk.CTkFont(size=10), text_color="#FFA500")
        self.video_status.pack(side="bottom", pady=10)
        
        if hasattr(self, 'chumei') and hasattr(self.chumei, 'avatar'):
            if hasattr(self.chumei.avatar, 'set_label'):
                self.chumei.avatar.set_label(self.video_label)
            if hasattr(self.chumei.avatar, 'start'):
                self.chumei.avatar.start()
                self.video_status.configure(text="🟢 Аватар активен", text_color="#00FF00")
    
    def _setup_chat_panel(self):
        self.chat_frame = ctk.CTkFrame(
            self.bottom_panel, width=450, corner_radius=15,
            fg_color="#1E1E1E", border_width=1, border_color="#3D3D3D"
        )
        self.chat_frame.pack(side="right", fill="both", expand=True)
        self.chat_frame.pack_propagate(False)
        
        header = ctk.CTkFrame(self.chat_frame, height=35, corner_radius=8, fg_color="#252526")
        header.pack(fill="x", pady=(10, 5))
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="💬 История диалогов", font=ctk.CTkFont(size=13, weight="bold"))
        title.pack(expand=True)
        
        self.chat_text = ctk.CTkTextbox(self.chat_frame, wrap="word", font=ctk.CTkFont(size=11),
                                        fg_color="#2D2D2D", border_width=0)
        self.chat_text.pack(fill="both", expand=True, pady=(0, 10))
        self.chat_text.configure(state="disabled")
        
        self.input_frame = ctk.CTkFrame(self.chat_frame, height=45, corner_radius=10, fg_color="#252526")
        self.input_frame.pack(fill="x", pady=(0, 10))
        self.input_frame.pack_propagate(False)
        
        self.input_entry = ctk.CTkEntry(self.input_frame,
                                        placeholder_text="💬 Введите сообщение... (Ctrl+Z/Y - отмена/повтор, ПКМ - меню)",
                                        font=ctk.CTkFont(size=12), corner_radius=8, border_width=0)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=8)
        
        send_btn = ctk.CTkButton(self.input_frame, text="📤", width=40, height=30,
                                 command=self._send_message, fg_color="#0078D4", hover_color="#106EBE", corner_radius=8)
        send_btn.pack(side="right", padx=(0, 10), pady=5)
        
        btn_frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        btn_frame.pack(side="bottom", fill="x", pady=(0, 10))
        
        btn_style = {"width": 45, "height": 32, "corner_radius": 8}
        
        clear_btn = ctk.CTkButton(btn_frame, text="🗑", command=self._clear_chat,
                                  fg_color="#555555", hover_color="#777777", **btn_style)
        clear_btn.pack(side="left", padx=5, expand=True, fill="x")
        ModernToolTip(clear_btn, "Очистить всю историю диалогов", title="🗑 Очистка чата")
        
        reset_btn = ctk.CTkButton(btn_frame, text="🔄", command=self._reset_bot,
                                  fg_color="#555555", hover_color="#777777", **btn_style)
        reset_btn.pack(side="left", padx=5, expand=True, fill="x")
        ModernToolTip(reset_btn, "Сбросить состояние бота", title="🔄 Сброс")
        
        exit_btn = ctk.CTkButton(btn_frame, text="✖", command=self._exit_app,
                                 fg_color="#D32F2F", hover_color="#B71C1C", **btn_style)
        exit_btn.pack(side="left", padx=5, expand=True, fill="x")
        ModernToolTip(exit_btn, "Закрыть приложение", title="✖ Выход")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ДОБАВЛЕНИЕ СООБЩЕНИЯ В ЧАТ
    # ═══════════════════════════════════════════════════════════════════════════
    
    def add_chat_message(self, speaker, text, is_user=False, girl_id=None):
        """Добавляет сообщение в историю чата."""
        def _add():
            try:
                timestamp = datetime.now().strftime("%H:%M:%S")
                self.chat_text.configure(state="normal")
                
                if is_user:
                    line = f"[{timestamp}] 👤 {speaker}: {text}\n\n"
                else:
                    line = f"[{timestamp}] 💬 {speaker}: {text}\n\n"
                
                self.chat_text.insert("end", line)
                self.chat_text.see("end")
                self.chat_text.configure(state="disabled")
            except Exception as e:
                print(f"⚠️ Ошибка добавления сообщения: {e}")
        
        if self.root and self.root.winfo_exists():
            self.root.after(0, _add)
    
    def _send_message(self):
        text = self.input_entry.get().strip()
        if not text:
            return
        self._save_state()
        self.input_entry.delete(0, "end")
        self.current_text = ""
        self.add_chat_message("Вы", text, is_user=True)
        if hasattr(self, 'chumei'):
            asyncio.create_task(self.chumei.process_text_command(text))
    
    def _clear_chat(self):
        self.chat_text.configure(state="normal")
        self.chat_text.delete("1.0", "end")
        self.chat_text.configure(state="disabled")
        print("🗑 Чат очищен")
    
    def _update_loop(self):
        if self.root.winfo_exists():
            self._update_data()
            self.root.after(1000, self._update_loop)
    
    def _update_data(self):
        def _update():
            try:
                for girl, card in self.girl_frames.items():
                    level = getattr(self.chumei, f"affection_{girl}", 50)
                    if hasattr(card, 'progress'):
                        card.progress.set(level / 100)
                        if hasattr(card, 'relation_value'):
                            card.relation_value.configure(text=str(level))
                        if hasattr(card, 'floor_label'):
                            floor_count = level // 20
                            card.floor_label.configure(text="🏢" * (floor_count + 1))
            except Exception as e:
                print(f"⚠️ Ошибка обновления: {e}")
        
        if self.root and self.root.winfo_exists():
            self.root.after(0, _update)
    
    def _open_gallery(self, girl_name):
        base_path = resource_path(os.path.join("assets", "girls", girl_name))
        image_paths = []
        if os.path.exists(base_path):
            image_paths = [os.path.join(base_path, f) for f in os.listdir(base_path)
                          if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        if image_paths:
            try:
                from photo_gallery import GirlGallery
                gallery = GirlGallery(self.root, girl_name, image_paths)
                gallery.show()
            except ImportError:
                messagebox.showinfo("Фотоальбом", f"📸 Для {girl_name} найдено {len(image_paths)} фото")
        else:
            messagebox.showinfo("Нет фото", f"📸 Для {girl_name} пока нет фото")
    
    def _reset_bot(self):
        if hasattr(self, 'chumei'):
            self.chumei.story_playing = False
            self.chumei.sleep_mode = False
            self.chumei.is_processing = False
            self.chumei.censorship_mode = True
            self.chumei.story_index = 0
            print("🔄 Бот сброшен")
    
    def _exit_app(self):
        print("👋 Закрытие...")
        if hasattr(self, 'chumei') and hasattr(self.chumei, 'avatar'):
            try:
                self.chumei.avatar.stop()
            except:
                pass
        if hasattr(self, 'chumei'):
            self.chumei.running = False
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        print("🚀 ChuMei Angels UI v7.1 запущен")
        print("✅ Горячие клавиши работают (Ctrl+C/V/X/A/Z/Y)")
        print("✅ Все диалоги выводятся в чат")
        self.root.mainloop()


if __name__ == "__main__":
    class MockChuMei:
        def __init__(self):
            self.affection_chuchu = 50
            self.affection_mei = 50
            self.affection_hana = 50
            self.affection_ki = 50
            self.affection_simone = 50
            self.story_playing = False
            self.sleep_mode = False
            self.is_processing = False
            self.censorship_mode = True
            self.story_index = 0
            self.running = True
            self.avatar = None
        async def process_text_command(self, text):
            print(f"[МОК] Обработка: {text}")
    
    mock = MockChuMei()
    app = ChuMeiUI(mock)
    app.run()