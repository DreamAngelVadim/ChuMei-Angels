"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         UNDO HISTORY FOR CHUMEI ANGELS                       ║
║                                                                              ║
║   Система отмены/повтора действий                          ║
║   Хранит историю изменений текста в поле ввода                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from collections import deque


class UndoHistory:
    """
    Класс для управления историей изменений текста.
    Поддерживает: Ctrl+Z , Ctrl+Y 
    """
    
    def __init__:
        self.undo_stack = deque   # Стек отмены
        self.redo_stack = deque   # Стек повтора
        self.current_text = ""
        self.is_undoing = False
        self.is_redoing = False
    
    def push_state:
        """
        Сохраняет текущее состояние текста в историю.
        Вызывается перед каждым изменением текста.
        """
        if self.is_undoing or self.is_redoing:
            return
        
        if self.current_text != text:
            self.undo_stack.append
            self.redo_stack.clear
            self.current_text = text
    
    def undo:
        """
        Отменяет последнее действие 
        Возвращает предыдущий текст или None
        """
        if not self.undo_stack:
            return None
        
        self.is_undoing = True
        
        # Сохраняем текущее состояние для повтора
        self.redo_stack.append
        
        # Восстанавливаем предыдущее состояние
        previous_text = self.undo_stack.pop
        self.current_text = previous_text
        
        self.is_undoing = False
        return previous_text
    
    def redo:
        """
        Возвращает отменённое действие 
        Возвращает следующий текст или None
        """
        if not self.redo_stack:
            return None
        
        self.is_redoing = True
        
        # Сохраняем текущее состояние
        self.undo_stack.append
        
        # Восстанавливаем следующий текст
        next_text = self.redo_stack.pop
        self.current_text = next_text
        
        self.is_redoing = False
        return next_text
    
    def clear:
        """Очищает всю историю"""
        self.undo_stack.clear
        self.redo_stack.clear
        self.current_text = ""
    
    def has_undo:
        return len > 0
    
    def has_redo:
        return len > 0
