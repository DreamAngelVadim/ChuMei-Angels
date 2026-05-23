"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         RUACCENT HELPER                                      ║
║                    Автоматическая расстановка ударений                        ║
║                    + пользовательский словарь для проблемных слов            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from ruaccent import RUAccent
import sys
import os

# Добавляем путь к папке knowledge для импорта
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'knowledge'))

try:
    from custom_stress import CUSTOM_STRESS
    print(f"📚 Загружено {len(CUSTOM_STRESS)} пользовательских исключений")
except ImportError:
    CUSTOM_STRESS = {}
    print("⚠️ Файл custom_stress.py не найден, использую только стандартный словарь")

class AccentHelper:
    def __init__(self):
        """Инициализация расстановщика ударений"""
        print("🎯 Загружаем модуль расстановки ударений...")
        self.accentizer = RUAccent()
        self.accentizer.load(
            use_dictionary=True,
            tiny_mode=False
        )
        print("✅ Ударения готовы")
    
    def process(self, text: str) -> str:
        """Расставляет ударения в тексте с учётом пользовательского словаря"""
        if not text:
            return text
        try:
            # 1. Сначала применяем стандартный алгоритм
            processed = self.accentizer.process_all(text)
            
            # 2. Затем применяем пользовательские замены (только для проблемных слов)
            for word, stressed_word in CUSTOM_STRESS.items():
                if word in processed:
                    processed = processed.replace(word, stressed_word)
            
            return processed
        except Exception as e:
            print(f"⚠️ Ошибка расстановки ударений: {e}")
            return text
    
    def process_for_tts(self, text: str) -> str:
        """Расставляет ударения и добавляет пометки для TTS"""
        if not text:
            return text
        try:
            # Применяем стандартную обработку
            processed = self.process(text)
            
            # Дополнительные замены для конкретных имён (на всякий случай)
            extra_replacements = {
                "Велма": "Вэ+лма",
                "велма": "вэ+лма",
                "Дафна": "Да+фна",
                "дафна": "да+фна",
                "Симона": "Сим+она",
                "симона": "сим+она",
            }
            for wrong, correct in extra_replacements.items():
                processed = processed.replace(wrong, correct)
            
            return processed
        except Exception as e:
            print(f"⚠️ Ошибка в process_for_tts: {e}")
            return text

# Создаём глобальный экземпляр
accent_helper = AccentHelper()