"""
Silero TTS v5 с поддержкой русского и английского языков
Автоматическое переключение между моделями в зависимости от текста
"""

import torch
import numpy as np
import scipy.io.wavfile as wav
import pygame
import tempfile
import os
import re
import asyncio
import logging

logger = logging.getLogger(__name__)


class SileroTTS:
    """Улучшенный TTS с поддержкой русского и английского языков"""
    
    def __init__(self):
        print("🎤 Загрузка Silero TTS (русская + английская модели)...")
        
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"   Device: {self.device}")
        
        # ---------- РУССКАЯ МОДЕЛЬ (v5_4_ru) ----------
        print("   📚 Загрузка русской модели (v5_4_ru)...")
        self.model_ru, _ = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='ru',
            speaker='v5_4_ru'
        )
        self.model_ru.to(self.device)
        
        # ---------- АНГЛИЙСКАЯ МОДЕЛЬ (v3_en) ----------
        print("   📚 Загрузка английской модели (v3_en)...")
        self.model_en, _ = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='en',
            speaker='v3_en'
        )
        self.model_en.to(self.device)
        
        self.sample_rate = 48000
        
        # Флаги для русской модели
        self.put_accent = True
        self.put_yo = True
        self.put_stress_homo = True
        self.put_yo_homo = True
        self.intensity = 3
        
        # Настройки для предотвращения обрыва фраз
        self.add_final_punctuation = True
        self.add_silence_buffer = True
        self.silence_buffer_ms = 300
        self.add_final_word = False
        
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
        print("✅ TTS готов (русский + английский)")
    
    def _transliterate_english(self, text: str) -> str:
        """Заменяет английские слова русским произношением"""
        translit_map = {
            # Игры
            "Genshin Impact": "Гэньшин Импакт",
            "Genshin": "Гэньшин",
            "Impact": "Импакт",
            "Blue Archive": "Блю Аркайв",
            "Needy Girl Overdose": "Ниди Гёрл Овэрдоус",
            "Zenless Zone Zero": "Зэнлесс Зоун Зиро",
            "D.Va": "ДиВа",
            "Raiden Shogun": "Райдэн Шогун",
            
            # Платформы
            "Instagram": "Инстаграм",
            "TikTok": "ТикТок",
            "OnlyFans": "ОнлиФанс",
            "YouTube": "Ютуб",
            "Twitter": "Твиттер",
            "Facebook": "Фейсбук",
            "Twitch": "Твич",
            "Discord": "Дискорд",
            "Telegram": "Телеграм",
            
            # Слова
            "cosplay": "косплэй",
            "Cosplay": "Косплэй",
            "online": "онлайн",
            "stream": "стрим",
            "Stream": "Стрим",
            "anime": "аниме",
            "Anime": "Аниме",
            "manga": "манга",
            "Manga": "Манга",
            "kawaii": "кавайи",
            "Kawaii": "Кавайи",
            
            # Имена брендов
            "Epica": "Эпика",
            "Kamelot": "Кэмелот",
            "Nightwish": "Найтвиш",
            "Rammstein": "Рамштайн",
            
            # Другое
            "Online": "Онлайн",
            "Only": "Онли",
            "Fans": "Фанс",
        }
        
        for eng, rus in translit_map.items():
            text = text.replace(eng, rus)
        
        return text
    
    def _select_model(self, text: str):
        """
        Выбирает модель в зависимости от языка текста
        - Если есть русские буквы -> русская модель
        - Если только латиница -> английская модель
        """
        cyrillic = any('а' <= char <= 'я' or 'А' <= char <= 'Я' or char == 'ё' or char == 'Ё' for char in text)
        
        if cyrillic:
            print(f"   🟢 Выбрана русская модель (есть кириллица)")
            return self.model_ru, 'ru'
        else:
            print(f"   🔵 Выбрана английская модель (только латиница)")
            return self.model_en, 'en'
    
    def _fix_russian_e(self, text: str) -> str:
        """Заменяет 'е' на 'э' в русских словах"""
        replacements = {
            'тест': 'тэст', 'Тест': 'Тэст',
            'теста': 'тэста', 'тесту': 'тэсту',
            'тестом': 'тэстом', 'тесте': 'тэсте',
            'тесты': 'тэсты', 'тестов': 'тэстов',
            'тестовая': 'тэстовая', 'тестовое': 'тэстовое',
            'тестовый': 'тэстовый', 'тестовые': 'тэстовые',
            'косплей': 'косплэй', 'Косплей': 'Косплэй',
            'косплея': 'косплэя', 'косплею': 'косплэю',
            'косплеем': 'косплэем', 'косплее': 'косплэе',
            'косплеер': 'косплэер', 'косплеера': 'косплэера',
            'модель': 'модэль', 'Модель': 'Модэль',
            'модели': 'модэли', 'моделью': 'модэлью',
            'моделей': 'модэлей',
            'тренд': 'трэнд', 'бренд': 'брэнд',
        }
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result
    
    def _fix_ending(self, text: str) -> str:
        """Исправляет окончание фразы для предотвращения обрыва"""
        if not text:
            return text
        
        text = text.strip()
        
        if self.add_final_punctuation:
            if text and text[-1] not in '.!?;:':
                text += '.'
        
        if self.add_final_word:
            text += " мм"
        
        return text
    
    def _add_silence_to_audio(self, audio: np.ndarray) -> np.ndarray:
        """Добавляет буфер тишины в конец аудио"""
        if not self.add_silence_buffer:
            return audio
        
        silence_duration = self.silence_buffer_ms / 1000.0
        silence_samples = int(self.sample_rate * silence_duration)
        silence = np.zeros(silence_samples, dtype=audio.dtype)
        
        return np.concatenate([audio, silence])
    
    def _prepare_text(self, text: str) -> str:
        """Подготовка текста: числа → слова"""
        if not text:
            return text
        
        if any('а' <= char <= 'я' for char in text.lower()):
            num_words = {
                '0': 'ноль', '1': 'один', '2': 'два', '3': 'три', '4': 'четыре',
                '5': 'пять', '6': 'шесть', '7': 'семь', '8': 'восемь', '9': 'девять',
                '10': 'десять', '100': 'сто', '1000': 'тысяча'
            }
            for num, word in num_words.items():
                text = text.replace(num, word)
        
        return text
    
    def _split_into_sentences(self, text: str) -> list:
        """Разбивает текст на предложения"""
        sentences = re.split(r'(?<=[.!?;:])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _mark_question_center(self, text: str) -> str:
        """Размечает вопросительные интонации (только для русского)"""
        if '?' not in text or '*' in text:
            return text
        
        words = text.replace('?', '').split()
        if not words:
            return text
        
        question_words = {'кто', 'что', 'где', 'когда', 'куда', 'откуда', 
                          'почему', 'зачем', 'как', 'сколько', 'какой', 'чей'}
        
        if any(w.lower() in question_words for w in words):
            return text
        
        excluded = question_words | {'и', 'в', 'на', 'с', 'по', 'у', 'к', 'от', 'до'}
        
        for i, word in enumerate(reversed(words)):
            clean = word.strip('.,!?')
            if len(clean) > 2 and clean.lower() not in excluded:
                words[-i-1] = f"*{clean}*"
                break
        
        if not any('*' in w for w in words):
            words[-1] = f"*{words[-1]}*"
        
        return ' '.join(words) + '?'
    
    async def speak(self, text: str, voice: str = None):
        """Озвучивание текста с автоматическим выбором языка"""
        if not text or not text.strip():
            return
        
        # 0. Транслитерация английских слов (перед определением языка)
        text = self._transliterate_english(text)
        
        # 1. Подготовка текста
        text = self._prepare_text(text)
        
        # 2. Определяем язык и выбираем модель
        active_model, lang = self._select_model(text)
        
        # 3. Применяем русские обработки только для русского текста
        if lang == 'ru':
            text = self._fix_russian_e(text)
            text = self._mark_question_center(text)
            final_voice = voice if voice and voice != 'en_24' else 'xenia'
        else:
            final_voice = 'en_24'
        
        # 4. Разбиваем на предложения
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            if not sentence:
                continue
            
            processed = self._fix_ending(sentence)
            print(f"🔊 {final_voice}: {processed[:100]}...")
            
            try:
                if lang == 'ru':
                    audio = active_model.apply_tts(
                        text=processed,
                        speaker=final_voice,
                        sample_rate=self.sample_rate,
                        put_accent=self.put_accent,
                        put_yo=self.put_yo,
                        put_stress_homo=self.put_stress_homo,
                        put_yo_homo=self.put_yo_homo,
                        intensity=self.intensity
                    )
                else:
                    audio = active_model.apply_tts(
                        text=processed,
                        speaker='en_24',
                        sample_rate=self.sample_rate
                    )
                
                audio_np = audio.cpu().numpy()
                audio_np = self._add_silence_to_audio(audio_np)
                
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    audio_int16 = (audio_np * 32767).astype(np.int16)
                    wav.write(f.name, self.sample_rate, audio_int16)
                    temp_file = f.name
                
                pygame.mixer.music.load(temp_file)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.05)
                
                for _ in range(3):
                    try:
                        os.unlink(temp_file)
                        break
                    except PermissionError:
                        await asyncio.sleep(0.2)
                        
            except Exception as e:
                logger.error(f"Ошибка TTS: {e}")
            
            await asyncio.sleep(0.1)
    
    async def speak_chuchu(self, text: str):
        """Чучу (русский голос xenia)"""
        await self.speak(text, voice="xenia")
    
    async def speak_mei(self, text: str):
        """Мэй (русский голос baya)"""
        await self.speak(text, voice="baya")
    
    async def speak_english(self, text: str, voice: str = "en_24"):
        """Английский текст (голос en_24 - подобран под xenia)"""
        await self.speak(text, voice=voice)
    
    async def speak_duet(self, text: str, main_voice: str = "xenia"):
        await self.speak(text, voice=main_voice)
    
    async def speak_story_alternating(self, story_text: str, voice1: str = "xenia",
                                       voice2: str = "baya", pause_between: float = 0.5):
        """Рассказ истории с чередованием голосов (только русский)"""
        if not story_text:
            return
        
        sentences = self._split_into_sentences(story_text)
        
        if len(sentences) < 2:
            await self.speak(story_text, voice=voice1)
            return
        
        for i, sentence in enumerate(sentences):
            voice = voice1 if i % 2 == 0 else voice2
            await self.speak(sentence, voice=voice)
            await asyncio.sleep(pause_between)


# Упрощённая версия для обратной совместимости
class SimpleSileroTTS:
    def __init__(self):
        self.tts = SileroTTS()
    
    async def speak(self, text: str, voice: str = "xenia"):
        await self.tts.speak(text, voice=voice)
    
    async def speak_duet(self, text: str):
        await self.tts.speak(text, voice="xenia")
    
    async def speak_story_alternating(self, story_text: str, voice1: str = "xenia",
                                       voice2: str = "baya", pause_between: float = 0.5):
        await self.tts.speak_story_alternating(story_text, voice1, voice2, pause_between)