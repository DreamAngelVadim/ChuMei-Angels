import re
from config import BANNED_WORDS_FILE

class MessageFilter:
    def __init__(self):
        self.bad_words = self._load_bad_words()
        self.ignore_users = self._load_ignore_users()
        print(self.bad_words)
        print(BANNED_WORDS_FILE)

    def _load_bad_words(self):
        """Загружает плохие слова из файла или базы"""
        with open(BANNED_WORDS_FILE, 'r', encoding='utf-8') as f:
            words = f.read().split(' ')
        return words
    
    def _load_ignore_users(self):
        return []
    
    def should_ignore_message(self, username: str, message: str) -> bool:
        """Расширенная проверка сообщения"""
        message_lower = message.lower().strip().split(' ')
        
        # Проверка плохих слов
        if any(bad_word in message_lower for bad_word in self.bad_words):
            print(f"🚫 Фильтр: плохое слово от {username}")
            return True
        
        # Проверка пользователей в черном списке
        if username.lower() in [user.lower() for user in self.ignore_users]:
            pass 
        
        # Проверка на CAPS LOCK (более 70% заглавных букв)
        if len(message) > 10:
            pass 
        
        # Проверка на повторяющиеся символы (спам)
        if re.search(r'(.)\1{5,}', message):  # 6+ одинаковых символов подряд
            pass 
        
        # Проверка длины сообщения
        if len(message) > 250:
            print(f"🚫 Фильтр: слишком длинное сообщение от {username}")
            return True
        
        # Проверка на пустое сообщение
        if not message_lower:
            return True
        
        return False
 
    def add_ignore_user(self, username: str):
        pass 