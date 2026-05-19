"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         RUACCENT HELPER                                       ║
║                    Автоматическая расстановка ударений                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from ruaccent import RUAccent

class AccentHelper:
    def __init__(self):
        """Инициализация расстановщика ударений"""
        print("🎯 Загружаем модуль расстановки ударений...")
        self.accentizer = RUAccent()
        # Используем turbo3.1 - хороший баланс скорости и качества
        # use_dictionary=True - используем словарь для точности
        # tiny_mode=False - полная версия
        self.accentizer.load(
            use_dictionary=True,              # используем словарь
            tiny_mode=False                   # полная версия
        )
        print("✅ Ударения готовы")
    
    def process(self, text: str) -> str:
        """Расставляет ударения в тексте"""
        if not text:
            return text
        try:
            # process_all обрабатывает весь текст целиком
            return self.accentizer.process_all(text)
        except Exception as e:
            print(f"⚠️ Ошибка расстановки ударений: {e}")
            return text
    
    def process_for_tts(self, text: str) -> str:
        """Расставляет ударения и добавляет пометки для TTS"""
        if not text:
            return text
        try:
            # Можно добавить замену проблемных слов вручную
            replacements = {
                "Велма": "Вэ́лма",
                "велма": "вэ́лма",
                "Дафна": "Да́фна",
                "дафна": "да́фна",
                "Симона": "Симо́на",
                "симона": "симо́на",
            }
            for wrong, correct in replacements.items():
                text = text.replace(wrong, correct)
            
            return self.accentizer.process_all(text)
        except Exception as e:
            print(f"⚠️ Ошибка в process_for_tts: {e}")
            return text

# Создаём глобальный экземпляр
accent_helper = AccentHelper()