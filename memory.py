"""
Система памяти для ChuMei Angels.
Хранит факты о пользователе, предпочтения и историю диалогов.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class Memory:
    """
    Класс для управления памятью и фактами о пользователе.
    """
    
    def __init__(self, memory_file: str = "memory.json"):
        """
        Инициализация системы памяти.
        
        Аргументы:
            memory_file: путь к файлу для сохранения памяти
        """
        self.memory_file = memory_file
        self.facts: Dict[str, List[str]] = {
            "chuchu": [],
            "mei": [],
            "hana": [],
            "ki": [],
            "simone": []
        }
        self.learning_mode: Dict[str, bool] = {
            "chuchu": False,
            "mei": False,
            "hana": False,
            "ki": False,
            "simone": False
        }
        self.conversation_history: List[Dict] = []
        self.user_preferences: Dict = {}
        
        # Создаём директорию для файла памяти, если нужно
        memory_dir = os.path.dirname(memory_file)
        if memory_dir:
            os.makedirs(memory_dir, exist_ok=True)
        
        self.load()
    
    def save_fact(self, girl_name: str, fact: str) -> bool:
        """
        Сохраняет факт о пользователе для конкретной девочки.
        
        Аргументы:
            girl_name: имя девочки (chuchu, mei, hana, ki, simone)
            fact: текст факта
        
        Возвращает:
            True если факт сохранён, иначе False
        """
        if girl_name not in self.facts:
            return False
        
        # Не добавляем дубликаты
        if fact not in self.facts[girl_name]:
            self.facts[girl_name].append(fact)
            # Ограничиваем количество фактов (не более 50)
            if len(self.facts[girl_name]) > 50:
                self.facts[girl_name] = self.facts[girl_name][-50:]
            self.save()
            print(f"💾 Сохранён факт для {girl_name}: {fact[:50]}...")
            return True
        return False
    
    def get_facts(self, girl_name: str, limit: int = 5) -> List[str]:
        """
        Возвращает список фактов для конкретной девочки.
        
        Аргументы:
            girl_name: имя девочки
            limit: максимальное количество фактов
        
        Возвращает:
            Список фактов
        """
        if girl_name not in self.facts:
            return []
        return self.facts[girl_name][-limit:]
    
    def delete_fact(self, girl_name: str, fact_index: int) -> bool:
        """
        Удаляет факт по индексу.
        
        Аргументы:
            girl_name: имя девочки
            fact_index: индекс факта в списке
        
        Возвращает:
            True если факт удалён, иначе False
        """
        if girl_name not in self.facts:
            return False
        if 0 <= fact_index < len(self.facts[girl_name]):
            deleted = self.facts[girl_name].pop(fact_index)
            self.save()
            print(f"🗑 Удалён факт для {girl_name}: {deleted[:50]}...")
            return True
        return False
    
    def clear_facts(self, girl_name: Optional[str] = None) -> bool:
        """
        Очищает факты для девочки или для всех.
        
        Аргументы:
            girl_name: имя девочки (если None — очищает всех)
        
        Возвращает:
            True если очищено, иначе False
        """
        if girl_name:
            if girl_name in self.facts:
                self.facts[girl_name] = []
                print(f"🗑 Очищены факты для {girl_name}")
        else:
            for girl in self.facts:
                self.facts[girl] = []
            print("🗑 Очищены факты для всех девочек")
        self.save()
        return True
    
    def set_learning_mode(self, girl_name: str, enabled: bool) -> bool:
        """
        Включает или выключает режим обучения для девочки.
        
        Аргументы:
            girl_name: имя девочки
            enabled: True — включить, False — выключить
        
        Возвращает:
            True если режим изменён, иначе False
        """
        if girl_name not in self.learning_mode:
            return False
        self.learning_mode[girl_name] = enabled
        print(f"📚 Режим обучения для {girl_name}: {'включён' if enabled else 'выключен'}")
        self.save()
        return True
    
    def is_learning_mode(self, girl_name: str) -> bool:
        """
        Проверяет, включён ли режим обучения для девочки.
        
        Аргументы:
            girl_name: имя девочки
        
        Возвращает:
            True если режим обучения включён
        """
        return self.learning_mode.get(girl_name, False)
    
    def add_to_conversation(self, role: str, content: str) -> None:
        """
        Добавляет сообщение в историю диалога.
        
        Аргументы:
            role: роль (user или assistant)
            content: текст сообщения
        """
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Ограничиваем историю 100 сообщениями
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        self.save()
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict]:
        """
        Возвращает последние сообщения из истории диалога.
        
        Аргументы:
            limit: количество сообщений
        
        Возвращает:
            Список сообщений
        """
        return self.conversation_history[-limit:]
    
    def clear_conversation_history(self) -> None:
        """Очищает историю диалогов"""
        self.conversation_history = []
        print("🗑 История диалогов очищена")
        self.save()
    
    def set_user_preference(self, key: str, value) -> None:
        """
        Сохраняет пользовательскую настройку.
        
        Аргументы:
            key: ключ настройки
            value: значение настройки
        """
        self.user_preferences[key] = value
        self.save()
    
    def get_user_preference(self, key: str, default=None):
        """
        Получает пользовательскую настройку.
        
        Аргументы:
            key: ключ настройки
            default: значение по умолчанию
        
        Возвращает:
            Значение настройки или default
        """
        return self.user_preferences.get(key, default)
    
    def save(self) -> None:
        """
        Сохраняет всю память в JSON файл.
        """
        try:
            data = {
                "facts": self.facts,
                "learning_mode": self.learning_mode,
                "conversation_history": self.conversation_history,
                "user_preferences": self.user_preferences,
                "saved_at": datetime.now().isoformat()
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"💾 Память сохранена в {self.memory_file}")
        except Exception as e:
            print(f"⚠️ Ошибка сохранения памяти: {e}")
    
    def load(self):
        """Загружает память из файла"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.short_term = data.get('short_term', [])
                    self.long_term = data.get('long_term', [])
                    self.learning_mode = data.get('learning_mode', False)
                    print(f"[MEMORY] Загружено из {self.memory_file}")
            except Exception as e:
                print(f"[MEMORY] Ошибка загрузки: {e}")
        else:
            print(f"[MEMORY] Файл {self.memory_file} не найден, создаю новый")
    
    def get_stats(self) -> Dict:
        """
        Возвращает статистику памяти.
        
        Возвращает:
            Словарь со статистикой
        """
        return {
            "total_facts": sum(len(facts) for facts in self.facts.values()),
            "facts_by_girl": {girl: len(facts) for girl, facts in self.facts.items()},
            "learning_mode": self.learning_mode.copy(),
            "conversation_length": len(self.conversation_history),
            "preferences_count": len(self.user_preferences)
        }