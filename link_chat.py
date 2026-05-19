"""
Окно уведомлений для ссылок
"""
import tkinter as tk
import webbrowser


class LinkChat:
    """Всплывающие уведомления для ссылок."""

    def __init__(self):
        self.notification = None
        self.hide_after = 10000  # мс

    def start(self):
        """Ничего не делает, всё в add_link."""
        pass

    def add_link(self, url="https://t.me/chumei_ai", text="✨ Присоединяйся к нашему чатику! ✨"):
        """Показывает всплывающее уведомление."""
        print(f"🔗 Показываю уведомление: {text}")

        if self.notification:
            try:
                self.notification.destroy()
            except:
                pass

        self.notification = tk.Toplevel()
        self.notification.title("ChuMei Angels — Приглашение")
        self.notification.geometry(f"400x120+{self.notification.winfo_screenwidth() - 420}+{self.notification.winfo_screenheight() - 200}")
        self.notification.attributes("-topmost", True)
        self.notification.configure(bg="#1e1e2e")

        # Заголовок
        header = tk.Label(
            self.notification,
            text="🌸 ChuMei Angels 🌸",
            font=("Arial", 12, "bold"),
            fg="#ffb6c1",
            bg="#1e1e2e"
        )
        header.pack(pady=(10, 5))

        # Текст
        label = tk.Label(
            self.notification,
            text=text,
            font=("Arial", 10),
            fg="#ffffff",
            bg="#1e1e2e"
        )
        label.pack(pady=5)

        # Ссылка (кликабельная)
        link_btn = tk.Label(
            self.notification,
            text=url,
            font=("Arial", 9, "underline"),
            fg="#89b4fa",
            bg="#1e1e2e",
            cursor="hand2"
        )
        link_btn.pack(pady=5)
        link_btn.bind("<Button-1>", lambda e: self._open_url(url))

        # Кнопка закрытия
        close_btn = tk.Button(
            self.notification,
            text="✖",
            font=("Arial", 8),
            bg="#1e1e2e",
            fg="#ffffff",
            bd=0,
            command=self._hide
        )
        close_btn.place(x=370, y=5)

        # Автоскрытие
        self.notification.after(self.hide_after, self._hide)

        # Принудительно обновляем
        self.notification.update()
        self.notification.deiconify()

    def _open_url(self, url):
        webbrowser.open(url)
        self._hide()

    def _hide(self):
        if self.notification:
            try:
                self.notification.destroy()
            except:
                pass
            self.notification = None

    def update(self):
        pass

    def stop(self):
        self._hide()