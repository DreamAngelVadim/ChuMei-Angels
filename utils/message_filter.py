import re
from config import BANNED_WORDS_FILE

class MessageFilter:
    def __init__:
        self.bad_words = self._load_bad_words
        self.ignore_users = self._load_ignore_users
        print
        print

    def _load_bad_words:
        """Загружает плохие слова из файла или базы"""
        with open as f:
            words = f.read.split
        return words
    
    def _load_ignore_users:
        return []
    
    def should_ignore_message -> bool:
        """Расширенная проверка сообщения"""
        message_lower = message.lower.strip.split
        
        # Проверка плохих слов
        if any:
            print
            return True
        
        # Проверка пользователей в черном списке
        if username.lower in [user.lower for user in self.ignore_users]:
            pass 
        
        # Проверка на CAPS LOCK 
        if len > 10:
            pass 
        
        # Проверка на повторяющиеся символы 
        if re.search\1{5,}', message):  # 6+ одинаковых символов подряд
            pass 
        
        # Проверка длины сообщения
        if len > 250:
            print
            return True
        
        # Проверка на пустое сообщение
        if not message_lower:
            return True
        
        return False
 
    def add_ignore_user:
        pass 
