"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         UNDO HISTORY FOR CHUMEI ANGELS                       ║
║                                                                              ║
║   Система отмены/повтора действий (Ctrl+Z / Ctrl+Y)                         ║
║   Хранит историю изменений текста в поле ввода                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from collections import deque


class UndoHistory:
    """
    Класс для управления историей изменений текста.
    Поддерживает: Ctrl+Z (отмена), Ctrl+Y (повтор)
    """
    
    def __init__(self, max_history=50):
        self.undo_stack = deque(maxlen=max_history)   # Стек отмены
        self.redo_stack = deque(maxlen=max_history)   # Стек повтора
        self.current_text = ""
        self.is_undoing = False
        self.is_redoing = False
    
    def push_state(self, text):
        """
        Сохраняет текущее состояние текста в историю.
        Вызывается перед каждым изменением текста.
        """
        if self.is_undoing or self.is_redoing:
            return
        
        if self.current_text != text:
            self.undo_stack.append(self.current_text)
            self.redo_stack.clear()
            self.current_text = text
    
    def undo(self, current_text):
        """
        Отменяет последнее действие (Ctrl+Z)
        Возвращает предыдущий текст или None
        """
        if not self.undo_stack:
            return None
        
        self.is_undoing = True
        
        # Сохраняем текущее состояние для повтора
        self.redo_stack.append(current_text)
        
        # Восстанавливаем предыдущее состояние
        previous_text = self.undo_stack.pop()
        self.current_text = previous_text
        
        self.is_undoing = False
        return previous_text
    
    def redo(self, current_text):
        """
        Возвращает отменённое действие (Ctrl+Y)
        Возвращает следующий текст или None
        """
        if not self.redo_stack:
            return None
        
        self.is_redoing = True
        
        # Сохраняем текущее состояние
        self.undo_stack.append(current_text)
        
        # Восстанавливаем следующий текст
        next_text = self.redo_stack.pop()
        self.current_text = next_text
        
        self.is_redoing = False
        return next_text
    
    def clear(self):
        """Очищает всю историю"""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.current_text = ""
    
    def has_undo(self):
        return len(self.undo_stack) > 0
    
    def has_redo(self):
        return len(self.redo_stack) > 0