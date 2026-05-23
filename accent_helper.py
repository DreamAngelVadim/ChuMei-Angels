"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         RUACCENT HELPER                                      ║
║                    Автоматическая расстановка ударений                        ║
║                    + пользовательский словарь для проблемных слов            ║
║                    + поддержка вопросительных интонаций                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from ruaccent import RUAccent
import sys
import os
import re

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
            # Сначала применяем пользовательские замены (ДО стандартного алгоритма)
            # Это важно для слов с "е" -> "э"
            processed = text
            for word, stressed_word in CUSTOM_STRESS.items():
                if word in processed:
                    processed = processed.replace(word, stressed_word)
            
            # Затем применяем стандартный алгоритм ruaccent
            processed = self.accentizer.process_all(processed)
            
            return processed
        except Exception as e:
            print(f"⚠️ Ошибка расстановки ударений: {e}")
            return text
    
    def _mark_question_center(self, text: str) -> str:
        """
        Размечает интонационный центр для вопросов
        Поддержка 4 типов вопросов из Silero TTS v5:
        - Общие вопросы (выделяем звёздочками)
        - Специальные вопросы (с вопросительным словом)
        - Альтернативные вопросы (с "или")
        - Вопросы-хвостики (с "не так ли", "правда", "да")
        """
        if '?' not in text or '*' in text:
            return text
        
        text_without_q = text.replace('?', '').strip()
        words = text_without_q.split()
        
        if not words:
            return text
        
        # Список вопросительных слов для специальных вопросов
        question_words = {'кто', 'что', 'где', 'когда', 'куда', 'откуда', 
                          'почему', 'зачем', 'как', 'сколько', 'какой', 'чей',
                          'какая', 'какое', 'какие', 'чьи', 'чья', 'чьё'}
        
        # 1. Проверка на альтернативный вопрос (с "или")
        if ' или ' in text_without_q:
            parts = text_without_q.split(' или ')
            if len(parts) >= 2:
                # Выделяем ключевые слова из обеих частей
                first_words = parts[0].split()
                second_words = parts[1].split()
                if first_words:
                    text_without_q = text_without_q.replace(first_words[-1], f"*{first_words[-1]}*", 1)
                if second_words:
                    text_without_q = text_without_q.replace(second_words[-1], f"*{second_words[-1]}*", 1)
                return text_without_q + '?'
        
        # 2. Проверка на вопрос-хвостик
        tail_markers = ['не так ли', 'правда', 'ведь', 'не правда ли', 'да', 'не']
        for marker in tail_markers:
            if marker in text_without_q.lower():
                main_part = text_without_q.lower().split(marker)[0].strip()
                if main_part:
                    main_words = main_part.split()
                    if main_words:
                        key_word = main_words[-1]
                        text_without_q = text_without_q.replace(key_word, f"*{key_word}*", 1)
                return text_without_q + '?'
        
        # 3. Проверка на специальный вопрос (с вопросительным словом)
        has_question_word = any(word.lower() in question_words for word in words)
        
        if has_question_word:
            # Для специальных вопросов выделяем вопросительное слово
            for i, word in enumerate(words):
                if word.lower() in question_words:
                    words[i] = f"*{word}*"
                    break
            return ' '.join(words) + '?'
        
        # 4. Общий вопрос (без вопросительного слова)
        # Исключаем предлоги и союзы из выделения
        excluded_words = question_words | {'и', 'в', 'на', 'с', 'по', 'у', 'к', 'от', 'до', 
                                           'за', 'над', 'под', 'о', 'об', 'без', 'для', 'через'}
        
        # Ищем слово для выделения (с конца предложения)
        marked = False
        for i, word in enumerate(reversed(words)):
            word_clean = word.strip('.,!?')
            if len(word_clean) > 2 and word_clean.lower() not in excluded_words:
                words[-i-1] = f"*{word_clean}*"
                marked = True
                break
        
        # Если не нашли подходящее слово, выделяем последнее
        if not marked:
            last_clean = words[-1].strip('.,!?')
            words[-1] = f"*{last_clean}*"
        
        return ' '.join(words) + '?'
    
    def _add_ssml_markup(self, text: str, rate: str = "medium") -> str:
        """
        Добавляет базовую SSML разметку для улучшения интонации
        rate: x-slow, slow, medium, fast, x-fast
        """
        # Не применяем SSML если текст короткий
        if len(text) < 50:
            return text
        
        # Добавляем паузы после знаков препинания
        text = re.sub(r'([.!?;:])\s+', r'\1<break time="150ms"/> ', text)
        
        # Оборачиваем в prosody для контроля скорости
        return f'<speak><prosody rate="{rate}">{text}</prosody></speak>'
    
    def process_for_tts(self, text: str, use_ssml: bool = False, rate: str = "medium") -> str:
        """
        Расставляет ударения и размечает вопросы для TTS
        
        Аргументы:
            text: исходный текст
            use_ssml: использовать SSML разметку (для сложных случаев)
            rate: скорость речи (x-slow, slow, medium, fast, x-fast)
        
        Возвращает:
            текст с ударениями и разметкой вопросов
        """
        if not text:
            return text
        
        try:
            # 1. Стандартная обработка ударений
            processed = self.process(text)
            
            # 2. Разметка вопросительных интонаций (только для обычных текстов, не SSML)
            if not use_ssml:
                processed = self._mark_question_center(processed)
            
            # 3. Опционально: SSML разметка
            if use_ssml:
                processed = self._add_ssml_markup(processed, rate)
            
            return processed
            
        except Exception as e:
            print(f"⚠️ Ошибка в process_for_tts: {e}")
            return text


# Создаём глобальный экземпляр
accent_helper = AccentHelper()


# Функция для быстрого тестирования
def test_accent_helper():
    """Тестовая функция для проверки работы ударений и вопросов"""
    test_phrases = [
        "Привет, Чучу и Мэй!",
        "Ты любишь косплей?",
        "Кто пришёл на вечеринку?",
        "Ты пойдёшь гулять или останешься дома?",
        "Хорошая погода, не так ли?",
        "Он пришёл сегодня?",
        "Ты действительно хочешь это сделать?",
        "Я люблю косплей и модель",
    ]
    
    print("\n" + "=" * 60)
    print("Тест акцент-хелпера (ударения + вопросы)")
    print("=" * 60)
    
    for phrase in test_phrases:
        result = accent_helper.process_for_tts(phrase)
        print(f"\n📝 Исходный: {phrase}")
        print(f"🎯 Результат: {result}")
    
    print("\n" + "=" * 60)
    print("✅ Тест завершён")
    print("=" * 60)


if __name__ == "__main__":
    test_accent_helper()