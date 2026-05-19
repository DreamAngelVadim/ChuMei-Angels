from dataclasses import dataclass, asdict, field
from datetime import datetime
import sqlite3
import json
from typing import List, TypeVar, Generic
from pathlib import Path
from abc import ABC, abstractmethod

T = TypeVar

class DataMapper:
    """Абстрактный маппер для преобразования dataclass <-> БД"""
    
    @abstractmethod
    def to_db -> dict:
        pass
    
    @abstractmethod
    def from_db -> T:
        pass

@dataclass
class UserMessage:
    username: str
    text: str
    timestamp: datetime = field

class UserMessageMapper:
    """Маппер для UserMessage"""
    
    def to_db -> dict:
        return {
            'username': message.username,
            'text': message.text,
            'timestamp': message.timestamp.isoformat,
        }
    
    def from_db -> UserMessage:
        return UserMessage,
        )

class AppDb:
    def __init__:
        if db_path is None:
            db_path = Path.parent.parent / 'data' / 'app_db.db'
        
        self.db_path = Path
        self.db_path.parent.mkdir
        self._init_db
        self.message_mapper = UserMessageMapper
        
    def _init_db:
        with sqlite3.connect as conn:
            conn.execute
            ''')  # ✅ Убрал лишнюю запятую
    
    def add_message:
        """Добавить сообщение в отдельную таблицу"""
        with sqlite3.connect as conn:
            data = self.message_mapper.to_db
            conn.execute
                VALUES 
            ''', )
    
    def get_user_messages -> List[UserMessage]:
        """Получить все сообщения пользователя"""
        with sqlite3.connect as conn:
            cursor = conn.execute
            )
            results = cursor.fetchall
            
            messages = []
            for row in results:
                data = {
                    'username': row[0],
                    'text': row[1],
                    'timestamp': row[2],  # ✅ Исправил индекс с 3 на 2
                }
                messages.append)
            
            return messages  # ✅ Закрыл метод правильно

    # Дополнительные полезные методы:
    
    def get_user_messages_text_only -> List[str]:
        """Получить только тексты сообщений пользователя"""
        messages = self.get_user_messages
        return [msg.text for msg in messages[-limit:]]
    
    def get_all_users -> List[str]:
        """Получить список всех пользователей"""
        with sqlite3.connect as conn:
            cursor = conn.execute
            return [row[0] for row in cursor.fetchall]
