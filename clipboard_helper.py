"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CLIPBOARD HELPER FOR CHUMEI ANGELS                   ║
║                                                                              ║
║   Работа с буфером обмена через ctypes (без внешних зависимостей)           ║
║   Поддерживает: копирование, вставку, вырезание текста                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import ctypes
import ctypes.wintypes
import tkinter as tk


# ========== Windows API для буфера обмена ==========

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


def _get_clipboard_win32():
    """Получает текст из буфера обмена Windows через ctypes"""
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        if not user32.OpenClipboard(0):
            return ""
        
        try:
            h_data = user32.GetClipboardData(CF_UNICODETEXT)
            if not h_data:
                return ""
            
            p_text = kernel32.GlobalLock(h_data)
            if not p_text:
                return ""
            
            try:
                text = ctypes.wstring_at(p_text)
                return text
            finally:
                kernel32.GlobalUnlock(h_data)
        finally:
            user32.CloseClipboard()
    except Exception as e:
        print(f"⚠️ Ошибка чтения буфера обмена: {e}")
        return ""


def _set_clipboard_win32(text):
    """Устанавливает текст в буфер обмена Windows через ctypes"""
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        if not user32.OpenClipboard(0):
            return False
        
        try:
            user32.EmptyClipboard()
            
            # Выделяем память для текста
            h_global = kernel32.GlobalAlloc(GMEM_MOVEABLE, (len(text) + 1) * 2)
            if not h_global:
                return False
            
            p_text = kernel32.GlobalLock(h_global)
            if not p_text:
                kernel32.GlobalFree(h_global)
                return False
            
            try:
                ctypes.memmove(p_text, text.encode('utf-16le'), (len(text) + 1) * 2)
            finally:
                kernel32.GlobalUnlock(h_global)
            
            user32.SetClipboardData(CF_UNICODETEXT, h_global)
            return True
        finally:
            user32.CloseClipboard()
    except Exception as e:
        print(f"⚠️ Ошибка записи в буфер обмена: {e}")
        return False


# ========== РЕЗЕРВНЫЕ МЕТОДЫ (через tkinter) ==========

def _get_clipboard_tk():
    """Получает текст из буфера обмена через tkinter (резервный метод)"""
    try:
        root = tk.Tk()
        root.withdraw()
        text = root.clipboard_get()
        root.destroy()
        return text
    except Exception:
        return ""


def _set_clipboard_tk(text):
    """Устанавливает текст в буфер обмена через tkinter (резервный метод)"""
    try:
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        return True
    except Exception:
        return False


# ========== ОСНОВНЫЕ ФУНКЦИИ (автоматический выбор метода) ==========

def get_clipboard_text():
    """
    Получает текст из буфера обмена.
    Сначала пробует Windows API (быстрее), затем tkinter.
    """
    try:
        # Пробуем Windows API
        text = _get_clipboard_win32()
        if text:
            return text
    except Exception:
        pass
    
    # Резервный метод
    return _get_clipboard_tk()


def set_clipboard_text(text):
    """
    Устанавливает текст в буфер обмена.
    Сначала пробует Windows API (быстрее), затем tkinter.
    """
    if not text:
        return False
    
    try:
        # Пробуем Windows API
        if _set_clipboard_win32(text):
            return True
    except Exception:
        pass
    
    # Резервный метод
    return _set_clipboard_tk(text)


def clear_clipboard():
    """Очищает буфер обмена"""
    set_clipboard_text("")


# ========== ТЕСТИРОВАНИЕ ==========

if __name__ == "__main__":
    print("🧪 Тестирование clipboard_helper\n")
    
    # Тест 1: Копирование
    test_text = "Привет, Чучу! ❤️"
    print(f"📝 Копируем: {test_text}")
    set_clipboard_text(test_text)
    
    # Тест 2: Вставка
    result = get_clipboard_text()
    print(f"📋 Вставляем: {result}")
    
    if result == test_text:
        print("✅ Тест пройден!")
    else:
        print("❌ Тест не пройден")