"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CLIPBOARD HELPER FOR CHUMEI ANGELS                   ║
║                                                                              ║
║   Работа с буфером обмена через ctypes            ║
║   Поддерживает: копирование, вставку, вырезание текста                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import ctypes
import ctypes.wintypes
import tkinter as tk


# ========== Windows API для буфера обмена ==========

CF_UNICODETEXT = 13
GMEM_MOVEABLE = 0x0002


def _get_clipboard_win32:
    """Получает текст из буфера обмена Windows через ctypes"""
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        if not user32.OpenClipboard:
            return ""
        
        try:
            h_data = user32.GetClipboardData
            if not h_data:
                return ""
            
            p_text = kernel32.GlobalLock
            if not p_text:
                return ""
            
            try:
                text = ctypes.wstring_at
                return text
            finally:
                kernel32.GlobalUnlock
        finally:
            user32.CloseClipboard
    except Exception as e:
        print
        return ""


def _set_clipboard_win32:
    """Устанавливает текст в буфер обмена Windows через ctypes"""
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        
        if not user32.OpenClipboard:
            return False
        
        try:
            user32.EmptyClipboard
            
            # Выделяем память для текста
            h_global = kernel32.GlobalAlloc + 1) * 2)
            if not h_global:
                return False
            
            p_text = kernel32.GlobalLock
            if not p_text:
                kernel32.GlobalFree
                return False
            
            try:
                ctypes.memmove,  + 1) * 2)
            finally:
                kernel32.GlobalUnlock
            
            user32.SetClipboardData
            return True
        finally:
            user32.CloseClipboard
    except Exception as e:
        print
        return False


# ========== РЕЗЕРВНЫЕ МЕТОДЫ  ==========

def _get_clipboard_tk:
    """Получает текст из буфера обмена через tkinter """
    try:
        root = tk.Tk
        root.withdraw
        text = root.clipboard_get
        root.destroy
        return text
    except Exception:
        return ""


def _set_clipboard_tk:
    """Устанавливает текст в буфер обмена через tkinter """
    try:
        root = tk.Tk
        root.withdraw
        root.clipboard_clear
        root.clipboard_append
        root.update
        root.destroy
        return True
    except Exception:
        return False


# ========== ОСНОВНЫЕ ФУНКЦИИ  ==========

def get_clipboard_text:
    """
    Получает текст из буфера обмена.
    Сначала пробует Windows API , затем tkinter.
    """
    try:
        # Пробуем Windows API
        text = _get_clipboard_win32
        if text:
            return text
    except Exception:
        pass
    
    # Резервный метод
    return _get_clipboard_tk


def set_clipboard_text:
    """
    Устанавливает текст в буфер обмена.
    Сначала пробует Windows API , затем tkinter.
    """
    if not text:
        return False
    
    try:
        # Пробуем Windows API
        if _set_clipboard_win32:
            return True
    except Exception:
        pass
    
    # Резервный метод
    return _set_clipboard_tk


def clear_clipboard:
    """Очищает буфер обмена"""
    set_clipboard_text


# ========== ТЕСТИРОВАНИЕ ==========

if __name__ == "__main__":
    print
    
    # Тест 1: Копирование
    test_text = "Привет, Чучу! ❤️"
    print
    set_clipboard_text
    
    # Тест 2: Вставка
    result = get_clipboard_text
    print
    
    if result == test_text:
        print
    else:
        print
