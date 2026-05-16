"""
Окно уведомлений — исправленная версия
"""
import tkinter as tk
import webbrowser


class LinkChat:
    """Всплывающие уведомления для ссылок."""

    def __init__(self):
        self.notification = None
        self.hide_after = 10000

    def start(self):
        """Ничего не делает, всё в add_link."""
        print("Уведомления готовы")

    def add_link(self, text: str, url: str):
        """Показывает всплывающее уведомление."""
        print(f"Показываю уведомление: {text}")

        if self.notification:
            try:
                self.notification.destroy()
            except:
                pass

        self.notification = tk.Toplevel()
        self.notification.title("Ссылка от Лизы")
        self.notification.geometry("380x140+{}+{}".format(
            self.notification.winfo_screenwidth() - 400,
            self.notification.winfo_screenheight() - 180
        ))
        self.notification.attributes('-topmost', True)
        self.notification.configure(bg="#2d0a3d")

        # Заголовок
        header = tk.Label(self.notification, text="Чучу отправила ссылку",
                          fg="#e0c0ff", bg="#2d0a3d", font=("Arial", 12, "bold"))
        header.pack(pady=8)

        # Текст
        tk.Label(self.notification, text=text,
                 fg="#e0c0ff", bg="#2d0a3d", font=("Arial", 10)).pack()

        # Ссылка
        link_btn = tk.Label(self.notification, text=url,
                            fg="#ff66ff", bg="#2d0a3d",
                            font=("Consolas", 9, "underline"), cursor="hand2")
        link_btn.pack(pady=5)
        link_btn.bind("<Button-1>", lambda e: webbrowser.open(url))

        # Автоскрытие
        self.notification.after(self.hide_after, self._hide)

        # Принудительно обновляем
        self.notification.update()
        self.notification.deiconify()

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