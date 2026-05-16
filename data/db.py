from dataclasses import dataclass, asdict, field
from datetime import datetime
import sqlite3
import json
from typing import List, TypeVar, Generic
from pathlib import Path
from abc import ABC, abstractmethod

T = TypeVar('T')

class DataMapper(ABC, Generic[T]):
    """Абстрактный маппер для преобразования dataclass <-> БД"""
    
    @abstractmethod
    def to_db(self, obj: T) -> dict:
        pass
    
    @abstractmethod
    def from_db(self, data: dict) -> T:
        pass

@dataclass
class UserMessage:
    username: str
    text: str
    timestamp: datetime = field(default_factory=datetime.now)

class UserMessageMapper(DataMapper[UserMessage]):
    """Маппер для UserMessage"""
    
    def to_db(self, message: UserMessage) -> dict:
        return {
            'username': message.username,
            'text': message.text,
            'timestamp': message.timestamp.isoformat(),
        }
    
    def from_db(self, data: dict) -> UserMessage:
        return UserMessage(
            username=data['username'],
            text=data['text'],
            timestamp=datetime.fromisoformat(data['timestamp']),
        )

class AppDb:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / 'data' / 'app_db.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.message_mapper = UserMessageMapper()
        
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_messages (
                    username TEXT,
                    message_text TEXT,
                    timestamp TEXT
                )
            ''')  # ✅ Убрал лишнюю запятую
    
    def add_message(self, message: UserMessage):
        """Добавить сообщение в отдельную таблицу"""
        with sqlite3.connect(self.db_path) as conn:
            data = self.message_mapper.to_db(message)
            conn.execute('''
                INSERT INTO user_messages (username, message_text, timestamp)
                VALUES (?, ?, ?)
            ''', (data['username'], data['text'], data['timestamp']))
    
    def get_user_messages(self, username: str) -> List[UserMessage]:
        """Получить все сообщения пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT username, message_text, timestamp FROM user_messages WHERE username = ? ORDER BY timestamp',  # ✅ Убрал лишнюю запятую
                (username,)
            )
            results = cursor.fetchall()
            
            messages = []
            for row in results:
                data = {
                    'username': row[0],
                    'text': row[1],
                    'timestamp': row[2],  # ✅ Исправил индекс с 3 на 2
                }
                messages.append(self.message_mapper.from_db(data))
            
            return messages  # ✅ Закрыл метод правильно

    # Дополнительные полезные методы:
    
    def get_user_messages_text_only(self, username: str, limit: int = 10) -> List[str]:
        """Получить только тексты сообщений пользователя"""
        messages = self.get_user_messages(username)
        return [msg.text for msg in messages[-limit:]]
    
    def get_all_users(self) -> List[str]:
        """Получить список всех пользователей"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT DISTINCT username FROM user_messages')
            return [row[0] for row in cursor.fetchall()]