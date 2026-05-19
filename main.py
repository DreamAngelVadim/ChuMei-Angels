"""
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                     CHUMEI ANGELS                                            ║
║                                                                                              ║
║   ГЛАВНЫЙ ФАЙЛ ПРИЛОЖЕНИЯ                                                                    ║
║   ═══════════════════════════════════════════════════════════════════════════════════════    ║
║                                                                                              ║
║   📌 НАЗНАЧЕНИЕ:                                                                             ║
║   • Управление микрофоном и голосовым вводом                                                ║
║   • Генерация ответов через ИИ (Ollama)                                                     ║
║   • Озвучивание ответов через Silero TTS                                                    ║
║   • Управление памятью и обучением                                                          ║
║   • Обработка голосовых команд                                                              ║
║   • Идентификация пользователя по голосу                                                     ║
║   • Видео-аватар с анимацией речи                                                           ║
║                                                                                              ║
║   🏠 ОСОБНЯК: Токио, Сибуя, район Хироо, улица Сакура, дом 4                                 ║
║   👧 ДЕВОЧКИ: Чучу, Мэй, Хана, Ки, Симона                                                    ║
║   🎮 УПРАВЛЕНИЕ: Голосовые команды, триггеры, режимы                                          ║
║   🎤 ИДЕНТИФИКАЦИЯ: Узнаёт пользователя по голосу                                             ║
║                                                                                              ║
║   🎯 ОСНОВНЫЕ КОМАНДЫ:                                                                       ║
║   • "подъём" — разбудить всех девочек на 10 минут                                           ║
║   • "разбуди на X часов" — разбудить на X часов                                             ║
║   • "не спать" — не спать до вечера                                                          ║
║   • "спокойной ночи" — уложить всех спать                                                    ║
║   • "раскрепостись" / "цензура" — переключение режима                                        ║
║   • "расскажи историю" — полная история вечеринки                                            ║
║   • "скажи бака" / "скажи кора" — японские фразы                                            ║
║                                                                                              ║
║   📝 ВЕРСИЯ: 3.0                                                                            ║
║   📅 ДАТА: 2025-01-27                                                                       ║
╚══════════════════════════════════════════════════════════════════════════════════════════════╝
"""

# ══════════════════════════════════════════════════════════════════════════════════════════════
# 1. ИМПОРТЫ
# ══════════════════════════════════════════════════════════════════════════════════════════════

import asyncio
import time
import os
import re
import random
import webbrowser
import urllib.parse
import sys
import subprocess
import threading
from datetime import datetime

import pygame
import numpy as np

from avatar_video import AvatarVideo


def resource_path(relative_path):
    """
    Возвращает правильный путь к файлу как в разработке, так и в скомпилированном EXE.
    
    Аргументы:
        relative_path (str): относительный путь к файлу
        
    Возвращает:
        str: абсолютный путь к файлу
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 2. КОСТЫЛИ ДЛЯ PYINSTALLER
# ══════════════════════════════════════════════════════════════════════════════════════════════

if hasattr(sys, 'stderr') and sys.stderr is None:
    import io
    sys.stderr = io.StringIO()
if hasattr(sys, 'stdout') and sys.stdout is None:
    sys.stdout = io.StringIO()


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 3. ИМПОРТЫ МОИХ МОДУЛЕЙ
# ══════════════════════════════════════════════════════════════════════════════════════════════

import config
from ai_brain import get_ai_response
from microphone_input import listen
from silero_tts import SileroTTS
from text_utils import clean_text, convert_number_to_words, normalize_text_for_tts
from ui_dashboard import ChuMeiUI

if hasattr(config, 'USE_REPLACEMENTS') and config.USE_REPLACEMENTS:
    from replacements import NUM_WORDS, GENDER_FIXES, REPLACEMENTS
else:
    NUM_WORDS = {}
    GENDER_FIXES = {}
    REPLACEMENTS = {}

from transliterate import transliterate
from link_chat import LinkChat
from voice_id import get_voice_embedding, compare_voices, compare_embeddings
from voice_recorder import record_voice
from memory import Memory

try:
    from accent_helper import accent_helper
except ImportError:
    accent_helper = None

from knowledge.cosplay import *
from knowledge.music import *
from knowledge.dialogues import *
from knowledge.personality import DUO_NAMES

try:
    from punctuator import RuPunctuator
    HAS_PUNCTUATOR = True
except ImportError:
    HAS_PUNCTUATOR = False


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 4. ЯПОНСКИЕ ФРАЗЫ (ТРИГГЕРЫ)
# ══════════════════════════════════════════════════════════════════════════════════════════════

JP_TRIGGERS = {
    ("скажи бака", "скажи baka"): ("chuchu", "Бака! Ты дурак, да? Хи-хи-хи!"),
    ("скажи кора", "скажи kora"): ("mei", "Кора, яро? Эй ты, сволочь? Ара-ара..."),
    ("скажи кусо", "скажи kuso"): ("hana", "Кусо! Дерьмо! Дошик кончился..."),
    ("скажи докэ", "скажи doke"): ("ki", "Докэ... отойди, пожалуйста..."),
    ("скажи бусу", "скажи busu"): ("simone", "Бусу. Уродина. Холодно."),
}


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 5. ОСНОВНОЙ КЛАСС CHUMEI
# ══════════════════════════════════════════════════════════════════════════════════════════════

class ChuMei:
    """
    ГЛАВНЫЙ КЛАСС ПРИЛОЖЕНИЯ CHUMEI ANGELS.
    
    ═══════════════════════════════════════════════════════════════════════════════════════════
    
    ОТВЕТСТВЕННОСТЬ:
    • Инициализация всех компонентов (TTS, микрофон, память, UI)
    • Обработка голосовых команд
    • Генерация ответов через ИИ
    • Управление режимами (сон, цензура, обучение)
    • Поддержание состояния персонажей (отношения, голод, туалет)
    • Идентификация пользователя по голосу
    
    ═══════════════════════════════════════════════════════════════════════════════════════════
    """
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.1 КОНСТРУКТОР
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    def __init__(self):
        """Инициализация всех компонентов приложения"""
        
        print("=" * 60)
        print("ChuMei Angels — виртуальный особняк в Сибуе")
        print("=" * 60)
        
        # ───────────────────────────────────────────────────────────────────────────────────────
        # 5.1.1 Состояния приложения
        # ───────────────────────────────────────────────────────────────────────────────────────
        self.story_playing = False      # Идёт ли рассказ истории
        self.story_chain = []           # Цепочка истории
        self.story_index = 0            # Текущий индекс в истории
        self.story_total = 0            # Всего частей в истории
        self.censorship_mode = True     # Режим цензуры (True = безопасный)
        self.sleep_mode = False         # Режим сна (True = девочки спят)
        self.is_processing = False      # Идёт ли обработка команды
        self.running = True             # Флаг работы приложения
        
        # ───────────────────────────────────────────────────────────────────────────────────────
        # 5.1.2 Отношения с девочками (0-100)
        # ───────────────────────────────────────────────────────────────────────────────────────
        self.affection_chuchu = 50
        self.affection_mei = 50
        self.affection_hana = 50
        self.affection_ki = 50
        self.affection_simone = 50
        
        # ───────────────────────────────────────────────────────────────────────────────────────
        # 5.1.3 Инициализация модулей
        # ───────────────────────────────────────────────────────────────────────────────────────
        self.link_chat = LinkChat()                     # Уведомления о ссылках
        self.silero = SileroTTS()                       # Голосовой синтезатор
        self.punctuator = RuPunctuator() if HAS_PUNCTUATOR else None  # Пунктуация
        self.memory = Memory()                          # Память
        self.avatar = AvatarVideo()                     # Видео-аватар
        
        # ───────────────────────────────────────────────────────────────────────────────────────
        # 5.1.4 Имя пользователя
        # ───────────────────────────────────────────────────────────────────────────────────────
        self.user_name = None
        self.name_asked = False
        self.name_file = resource_path("user_name.txt")
        self._load_user_name()
        
        # ───────────────────────────────────────────────────────────────────────────────────────
        # 5.1.5 Таймеры
        # ───────────────────────────────────────────────────────────────────────────────────────
        self.last_response_time = 0
        self.last_user_message_time = time.time()
        self.idle_chat_timeout = 30         # Секунд бездействия до случайной цепочки
        
        # ───────────────────────────────────────────────────────────────────────────────────────
        # 5.1.6 Состояния тела (голод, туалет, вес, настроение)
        # ───────────────────────────────────────────────────────────────────────────────────────
        self.hunger_chuchu = 100
        self.hunger_mei = 100
        self.hunger_timer = time.time()
        self.hunger_decay_rate = 1
        self.hunger_interval = 180
        self.weight_chuchu = 48.0
        self.weight_mei = 55.0
        self.bladder_chuchu = 100
        self.bladder_mei = 100
        self.bowel_chuchu = 100
        self.bowel_mei = 100
        self.toilet_occupied = False
        self.last_toilet_time = 0
        self.mood_chuchu = 70
        self.mood_mei = 70
        self.affection = 80
        self.last_argue_time = 0
        self.argue_cooldown = 300
        
        # ───────────────────────────────────────────────────────────────────────────────────────
        # 5.1.7 Инициализация команд
        # ───────────────────────────────────────────────────────────────────────────────────────
        self._init_search_sites()
        self._init_app_commands()
        self._init_volume_commands()
        
        # ───────────────────────────────────────────────────────────────────────────────────────
        # 5.1.8 Идентификация по голосу
        # ───────────────────────────────────────────────────────────────────────────────────────
        self.voice_enrolled = False
        self.voice_embedding = None
        self.voice_file = resource_path("voice_sample.npy")
        self._load_voice_sample()
        
        # ───────────────────────────────────────────────────────────────────────────────────────
        # 5.1.9 Режим сна по времени
        # ───────────────────────────────────────────────────────────────────────────────────────
        self.bedtime_hour = 4       # 4:00 — ложатся спать
        self.wakeup_hour = 7        # 7:40 — просыпаются
        self.all_girls = ["chuchu", "mei", "hana", "ki", "simone"]
        self.force_awake_until = 0  # Время до принудительного бодрствования
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.2 ПРИВАТНЫЕ МЕТОДЫ ИНИЦИАЛИЗАЦИИ
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    def _load_user_name(self):
        """Загружает имя пользователя из файла"""
        if os.path.exists(self.name_file):
            with open(self.name_file, 'r', encoding='utf-8') as f:
                self.user_name = f.read().strip()
                if self.user_name:
                    self.name_asked = True
                    print(f"📛 Загружено имя: {self.user_name}")
    
    def _load_voice_sample(self):
        """Загружает образец голоса пользователя"""
        if os.path.exists(self.voice_file):
            self.voice_embedding = np.load(self.voice_file)
            self.voice_enrolled = True
            print("🔊 Образец голоса загружен")
    
    def _init_search_sites(self):
        """Инициализирует сайты для поиска"""
        self.search_sites = {
            "ютуб": ["https://youtube.com", "https://www.youtube.com/results?search_query={query}"],
            "гугл": ["https://google.com", "https://www.google.com/search?q={query}"],
            "яндекс": ["https://ya.ru", "https://yandex.ru/search/?text={query}"],
            "википедия": ["https://wikipedia.org", "https://ru.wikipedia.org/wiki/{query}"],
        }
        self.search_triggers = ["открой", "запусти", "покажи", "найди", "поищи"]
        self.auto_sites = {"видео": "ютуб", "музыку": "ютуб", "погоду": "гугл"}
    
    def _init_app_commands(self):
        """Инициализирует команды для запуска приложений"""
        self.app_commands = {
            "блокнот": "notepad.exe",
            "калькулятор": "calc.exe",
            "проводник": "explorer.exe",
        }
    
    def _init_volume_commands(self):
        """Инициализирует команды управления громкостью"""
        self.volume_commands = {
            "up": ["погромче", "громче", "громкость вверх"],
            "down": ["потише", "тише", "громкость вниз"],
            "mute": ["молча", "замолчи", "тишина"],
            "max": ["звук 100", "громкость 100", "максимум"],
        }
    
    def _reset_timers(self):
        """Сбрасывает таймеры активности"""
        self.last_response_time = time.time()
        self.last_user_message_time = time.time()
        self.is_processing = False
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.3 МЕТОДЫ ДЛЯ РАБОТЫ С ГОЛОСОМ И ЧАТОМ
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    def add_chat_message(self, speaker, text, is_user=False):
        """
        Добавляет сообщение в чат UI.
        
        Аргументы:
            speaker (str): имя говорящего
            text (str): текст сообщения
            is_user (bool): True если сообщение от пользователя
        """
        if hasattr(self, 'ui'):
            self.ui.add_chat_message(speaker, text, is_user=is_user)
    
    async def _speak(self, text, voice=None, duet=False):
        """
        Озвучивает текст и добавляет его в чат.
        
        Аргументы:
            text (str): текст для озвучивания
            voice (str): голос (chuchu, mei, hana, ki, simone)
            duet (bool): True если нужно озвучить дуэтом
        """
        # Добавляем в чат
        if hasattr(self, 'ui'):
            speaker_name = voice or "chuchu"
            name_map = {"chuchu": "Чучу", "mei": "Мэй", "hana": "Хана", "ki": "Ки", "simone": "Симона"}
            display_name = name_map.get(speaker_name, speaker_name)
            self.ui.add_chat_message(display_name, text, is_user=False)
        
        # Проверка режима сна
        sleep_phrases = ["спокойной ночи", "доброе утро", "пора спать", "баю-бай", "спать", "укладываемся", "просыпаемся"]
        if self.sleep_mode and not any(phrase in text.lower() for phrase in sleep_phrases):
            print(f"😴 {voice or 'chuchu'} спит, не отвечает...")
            return
        
        # Замена чисел
        num_map = {
            "200": "двести", "100": "сто", "300": "триста", "400": "четыреста",
            "500": "пятьсот", "600": "шестьсот", "700": "семьсот", "800": "восемьсот",
            "900": "девятьсот", "1000": "тысяча", "2000": "две тысячи",
            "164": "сто шестьдесят четыре", "68": "шестьдесят восемь",
            "50": "пятьдесят", "60": "шестьдесят", "70": "семьдесят", "80": "восемьдесят",
            "90": "девяносто", "20": "двадцать", "30": "тридцать", "40": "сорок"
        }
        for num, word in num_map.items():
            text = text.replace(num, word)
        
        text = re.sub(r'(\d{2,4})([а-яА-Я])', lambda m: num_map.get(m.group(1), m.group(1)) + m.group(2), text)
        text = normalize_text_for_tts(text)
        
        print(f"🔊 Говорит {voice or 'chuchu'}: {text[:100]}...")
        
        # Анимация речи
        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
            self.avatar.start_talking()
        
        # Озвучивание
        if duet:
            await self.silero.speak_duet(text)
        elif voice == "mei":
            await self.silero.speak(text, voice="mei")
        elif voice == "hana":
            await self.silero.speak(text, voice="hana")
        elif voice == "ki":
            await self.silero.speak(text, voice="ki")
        elif voice == "simone":
            await self.silero.speak(text, voice="simone")
        else:
            await self.silero.speak(text, voice=voice or "chuchu")
        
        # Останавливаем анимацию речи
        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
            self.avatar.stop_talking()
    
    async def _play_scene(self, scene):
        """Воспроизводит сцену (список реплик)"""
        for item in scene:
            if isinstance(item, tuple):
                speaker, line = item
                if speaker == "chuchu":
                    await self.silero.speak(line, voice="chuchu")
                elif speaker == "mei":
                    await self.silero.speak(line, voice="mei")
                elif speaker == "both":
                    await self.silero.speak_duet(line)
                await asyncio.sleep(0.01)
    
    async def _random_dialogue(self):
        """Запускает случайный диалог между девочками"""
        if self.story_playing or self.sleep_mode:
            return
        if self.censorship_mode:
            scene = random.choice(DUET_IDLE_SAFE)
        else:
            scene = random.choice(DUET_IDLE_SAFE + DUET_IDLE_NSFW)
        await self._play_scene(scene)
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.4 ИДЕНТИФИКАЦИЯ ПОЛЬЗОВАТЕЛЯ ПО ГОЛОСУ
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    async def identify_user(self):
        """Идентифицирует пользователя по голосу"""
        print("\n🎤 Идентификация пользователя...")
        
        if not self.voice_enrolled:
            print("👤 Первый запуск! Регистрация нового пользователя...")
            await self._enroll_new_user()
            return
        
        await self._speak("Скажите что-нибудь, чтобы я вас узнала...", voice="chuchu")
        
        try:
            audio_path = record_voice(duration=4)
            
            if audio_path and os.path.exists(audio_path):
                new_embedding = get_voice_embedding(audio_path)
                os.remove(audio_path)
                
                if new_embedding is not None and self.voice_embedding is not None:
                    from voice_id import compare_embeddings
                    similarity = compare_embeddings(new_embedding, self.voice_embedding)
                    print(f"🔍 Совпадение голосов: {similarity * 100:.2f}%")
                    
                    if similarity > 0.65:
                        name = self.user_name if self.user_name else "Вадим"
                        await self._speak(f"О! Это же {name}! Как я рада тебя видеть! ❤️", voice="chuchu")
                        await asyncio.sleep(0.5)
                        await self._speak(f"Выключаю режим цензуры... Мы же одни!", voice="mei")
                        self.censorship_mode = False
                        print(f"✅ Узнан: {name}, цензура выключена")
                    else:
                        await self._speak("Осторожно! Это незнакомец... 😨", voice="chuchu")
                        await asyncio.sleep(0.5)
                        await self._speak("Включаю режим цензуры! Никаких откровенностей!", voice="mei")
                        self.censorship_mode = True
                        await self._ask_new_user_name()
                        print("🛡️ Чужой пользователь, цензура включена")
                else:
                    print("⚠️ Не удалось получить эмбеддинг голоса")
                    self.censorship_mode = True
            else:
                print("⚠️ Не удалось записать голос")
                
        except Exception as e:
            print(f"⚠️ Ошибка идентификации: {e}")
            self.censorship_mode = True
    
    async def _enroll_new_user(self):
        """Регистрирует нового пользователя"""
        await self._speak("Привет! Давай познакомимся! Как тебя зовут?", voice="chuchu")
        
        for i in range(3):
            text = await self.listen_with_timeout(5)
            print(f"🔍 Распознанный текст: '{text}'")
            
            if text and text.strip():
                self.user_name = text.strip().capitalize()
                print(f"📛 Сохраняю имя: {self.user_name}")
                with open(self.name_file, 'w', encoding='utf-8') as f:
                    f.write(self.user_name)
                await self._speak(f"Приятно познакомиться, {self.user_name}!", voice="chuchu")
                break
            else:
                if i < 2:
                    await self._speak("Не расслышала, повторите пожалуйста...", voice="mei")
                else:
                    self.user_name = "Гость"
                    await self._speak("Хорошо, буду называть вас Гость!", voice="chuchu")
        
        await self._speak("А теперь скажите фразу для моего распознавания: «Привет, я твой друг!»", voice="chuchu")
        
        audio_path = record_voice(duration=5)
        if audio_path and os.path.exists(audio_path):
            self.voice_embedding = get_voice_embedding(audio_path)
            if self.voice_embedding is not None:
                np.save(self.voice_file, self.voice_embedding)
                self.voice_enrolled = True
                print("🔊 Образец голоса сохранён")
                await self._speak("Отлично! Теперь я буду узнавать вас по голосу! ❤️", voice="chuchu")
                await self._speak("А теперь... выключаю цензуру! Мы же друзья!", voice="mei")
                self.censorship_mode = False
            else:
                print("❌ Не удалось получить эмбеддинг голоса")
                self.censorship_mode = True
            os.remove(audio_path)
        else:
            print("❌ Не удалось записать голос")
            self.censorship_mode = True
    
    async def _ask_new_user_name(self):
        """Спрашивает имя у нового пользователя"""
        for i in range(3):
            await self._speak("Как вас зовут?", voice="chuchu")
            text = await self.listen_with_timeout(5)
            print(f"🔍 Распознанный текст: '{text}'")
            
            if text and text.strip():
                self.user_name = text.strip().capitalize()
                print(f"📛 Сохраняю имя: {self.user_name}")
                with open(self.name_file, 'w', encoding='utf-8') as f:
                    f.write(self.user_name)
                await self._speak(f"Хорошо, {self.user_name}, я запомнила!", voice="chuchu")
                await self._speak("Но режим цензуры останется включённым... На всякий случай 😊", voice="mei")
                print(f"📛 Сохранено имя нового пользователя: {self.user_name}")
                return
            else:
                if i < 2:
                    await self._speak("Не расслышала, повторите...", voice="mei")
                else:
                    self.user_name = "Незнакомец"
                    await self._speak("Хорошо, буду называть вас Незнакомец", voice="chuchu")
                    print("📛 Имя не распознано, установлено 'Незнакомец'")
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.5 МЕТОДЫ ДЛЯ РАБОТЫ С ИИ
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    def _parse_target(self, text):
        """
        Определяет, к кому обращён запрос.
        
        Аргументы:
            text (str): текст запроса
            
        Возвращает:
            tuple: (target, clean_text) где target — имя девочки, clean_text — очищенный текст
        """
        target = "chuchu"
        clean_text = text.strip()
        text_lower = text.lower()
        
        targets = {
            "chuchu": ["чучу", "чу", "chuchu", "чу-чу"],
            "mei": ["мэй", "мей", "mei", "may", "мея"],
            "hana": ["хана", "hana", "ханна"],
            "ki": ["ки", "ki", "potato"],
            "simone": ["симона", "simone"],
            "both": ["девочки", "девчата", "сестрёнки", "девушки"]
        }
        
        for target_type, names in targets.items():
            for name in names:
                if text_lower.startswith(name + " ") or text_lower == name:
                    target = target_type
                    clean_text = re.sub(r'^' + re.escape(name) + r'\s*', '', text, flags=re.IGNORECASE).strip()
                    print(f"🎯 Распознано обращение: {target_type}")
                    return target, clean_text
        return target, clean_text
    
    async def _play_response(self, response, target):
        """
        Воспроизводит ответ от ИИ.
        
        Аргументы:
            response (str): ответ от ИИ
            target (str): целевая девочка
        """
        # Очистка от тегов
        import re
        response = re.sub(r'\[/?[а-яА-Яa-z]+\]', '', response)
        response = re.sub(r'\s+', ' ', response).strip()
        
        if not response:
            response = f"Привет, {self.user_name}! Чем могу помочь?"
        
        # Добавляем в чат
        name_map = {"chuchu": "Чучу", "mei": "Мэй", "hana": "Хана", "ki": "Ки", "simone": "Симона"}
        display_name = name_map.get(target, target.capitalize())
        if hasattr(self, 'ui'):
            self.ui.add_chat_message(display_name, response, is_user=False)
        
        print(f"💬 {display_name}: {response[:100]}...")
        
        # Анимация речи
        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
            self.avatar.start_talking()
        
        # Озвучивание
        if target == "mei":
            await self.silero.speak(response, voice="mei")
        elif target == "hana":
            await self.silero.speak(response, voice="hana")
        elif target == "ki":
            await self.silero.speak(response, voice="ki")
        elif target == "simone":
            await self.silero.speak(response, voice="simone")
        elif target == "both":
            await self.silero.speak_duet(response)
        else:
            await self.silero.speak(response, voice="chuchu")
        
        # Останавливаем анимацию речи
        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
            self.avatar.stop_talking()
    
    async def _process_normal(self, text):
        """
        Обрабатывает обычный запрос (не команду).
        
        Аргументы:
            text (str): текст запроса
        """
        if hasattr(self, 'ui') and text:
            self.ui.add_chat_message("Вы", text, is_user=True)
        
        if self.story_playing or self.sleep_mode:
            print("⏸️ Занято (история или сон), диалог отложен.")
            return
        
        self.last_user_message_time = time.time()
        target, clean_text = self._parse_target(text)
        if not clean_text:
            return
        
        # Проверка на выход
        words = clean_text.lower().split()
        if "выход" in words or "завершить" in words or (words == ["пока"]):
            name = self.user_name if self.user_name else "Вадим"
            await self._speak(f"До свидания, {name}! Мы будем ждать тебя!")
            self.running = False
            return
        
        print("\n🧠 Генерация ответа...")
        prompt = config.CHARACTER_PERSONALITY if not self.censorship_mode else config.CENSORED_PERSONALITY
        if self.user_name:
            prompt = f"Ты общаешься с пользователем по имени {self.user_name}. " + prompt
        
        allowed_girls = ["chuchu", "mei", "hana", "ki", "simone", "both"]
        girl_for_ai = target if target in allowed_girls else "chuchu"
        response = get_ai_response(
            user_message=clean_text,
            system_prompt=prompt,
            girl_name=girl_for_ai,
            user_name=self.user_name
        )
        
        # Очистка ответа от тегов
        if response:
            response = re.sub(r'\[/?[а-яА-Яa-z]+\]', '', response)
            response = re.sub(r'\s+', ' ', response).strip()
            if not response:
                response = f"Привет, {self.user_name}! Чем могу помочь?"
        
        if response:
            await self._play_response(response, target)
        
        self.last_response_time = time.time()
    
    async def process_text_command(self, text):
        """Обрабатывает текстовую команду"""
        print(f"📝 Текстовая команда: {text}")
        await self._process_normal(text)
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.6 ОБРАБОТЧИКИ КОМАНД
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    async def _handle_japanese_phrase(self, text_lower):
        """Обрабатывает японские фразы"""
        for triggers, (voice, phrase) in JP_TRIGGERS.items():
            if any(trigger in text_lower for trigger in triggers):
                await self._speak(phrase, voice=voice)
                return True
        await self._speak("Не поняла, какую фразу сказать. Попробуй: скажи бака, скажи кора, скажи кусо, скажи докэ")
        return True
    
    async def _handle_change_body(self, text_lower):
        """Обрабатывает изменение параметров тела"""
        bust_match = re.search(r'грудь[:\s]*(\d+)', text_lower)
        hips_match = re.search(r'бёдра[:\s]*(\d+)', text_lower)
        waist_match = re.search(r'талия[:\s]*(\d+)', text_lower)
        
        changes = []
        if bust_match:
            changes.append(f"грудь {bust_match.group(1)} размера")
        if hips_match:
            changes.append(f"бёдра {hips_match.group(1)} см")
        if waist_match:
            changes.append(f"талия {waist_match.group(1)} см")
        
        if changes:
            fact = "Новые параметры тела: " + ", ".join(changes)
            self.memory.save_fact("chuchu", fact)
            await self._speak(f"Ого! Запомнила: {', '.join(changes)}. Надеюсь, жемчужные трусики не порвутся!")
        else:
            await self._speak("А что именно изменить? Скажи, например: измени тело, грудь 3, бёдра 90")
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.7 РАССКАЗ ИСТОРИИ
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    async def tell_full_story(self):
        """Рассказывает полную историю вечеринки"""
        from knowledge.story_arc import FULL_STORY_ARC_FINAL
        if self.story_playing or self.sleep_mode:
            await self._speak("История уже рассказывается или мы спим.")
            return
        self.story_chain = FULL_STORY_ARC_FINAL
        self.story_total = len(self.story_chain)
        self.story_index = 0
        self.story_playing = True
        asyncio.create_task(self._play_story())
    
    async def _play_story(self):
        """
        Воспроизводит историю с выводом в чат.
        """
        self.is_processing = True
        
        # Карта соответствия speaker -> отображаемое имя и girl_id
        name_map = {
            "chuchu": ("Чучу", "chuchu"),
            "mei": ("Мэй", "mei"),
            "hana": ("Хана", "hana"),
            "ki": ("Ки", "ki"),
            "potato": ("Ки", "ki"),
            "simone": ("Симона", "simone"),
            "both": ("Чучу и Мэй", None)
        }
        
        while self.story_playing and self.story_index < self.story_total:
            speaker, text = self.story_chain[self.story_index]
            self.story_index += 1
            
            # ========== ВЫВОД В ЧАТ ==========
            if hasattr(self, 'ui'):
                display_name, girl_id = name_map.get(speaker, (speaker.capitalize(), None))
                self.ui.add_chat_message(display_name, text, is_user=False, girl_id=girl_id)
            # =================================
            
            # Озвучивание
            if speaker == "chuchu":
                await self.silero.speak(text, voice="chuchu")
            elif speaker == "mei":
                await self.silero.speak(text, voice="mei")
            elif speaker == "hana":
                await self.silero.speak(text, voice="hana")
            elif speaker == "ki" or speaker == "potato":
                await self.silero.speak(text, voice="ki")
            elif speaker == "simone":
                await self.silero.speak(text, voice="simone")
            elif speaker == "both":
                await self.silero.speak_duet(text)
            else:
                await self.silero.speak(text, voice="chuchu")
            
            await asyncio.sleep(0.3)
        
        self.story_playing = False
        self.is_processing = False
        
        # Финальное сообщение
        end_text = "Вот и вся история. Надеюсь, тебе понравилось!"
        if hasattr(self, 'ui'):
            self.ui.add_chat_message("Чучу", end_text, is_user=False, girl_id="chuchu")
        await self._speak(end_text)
    
    async def continue_story(self):
        """Продолжает историю с того же места"""
        if self.story_playing:
            await self._speak("История уже рассказывается.")
            return
        if self.story_index > 0 and self.story_index < self.story_total:
            self.story_playing = True
            await self._speak("Продолжаю с того места, где остановилась.")
            asyncio.create_task(self._play_story())
        else:
            await self._speak("Нет активной истории. Скажи «расскажи историю».")
    
    async def stop_story(self):
        """Останавливает рассказ истории"""
        if self.story_playing:
            self.story_playing = False
            self.is_processing = False
            await self._speak("Останавливаю рассказ.")
        else:
            await self._speak("История и не рассказывалась.")
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.8 РЕЖИМ СНА
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    async def _go_to_sleep(self):
        """Укладывает всех девочек спать"""
        name = self.user_name if self.user_name else "Вадим"
        for girl in self.all_girls:
            if girl == "chuchu":
                await self._speak(f"Спокойной ночи, {name}... Сладких снов...", voice=girl)
            elif girl == "mei":
                await self._speak(f"Ара-ара... Увидимся утром, {name}...", voice=girl)
            elif girl == "hana":
                await self._speak(f"Надеюсь, мне приснится дошик... Спокойной ночи, {name}!", voice=girl)
            elif girl == "ki":
                await self._speak(f"Спокойной... ночи... (зевает)... {name}...", voice=girl)
            elif girl == "simone":
                await self._speak(f"Спокойной ночи, {name}. Пусть тебе приснится что-то хорошее.", voice=girl)
            await asyncio.sleep(0.5)
        self.sleep_mode = True
    
    async def _wake_up(self):
        """Будит всех девочек"""
        name = self.user_name if self.user_name else "Вадим"
        for girl in self.all_girls:
            if girl == "chuchu":
                await self._speak(f"Доброе утро, {name}! Хи-хи-хи!", voice=girl)
            elif girl == "mei":
                await self._speak(f"Ара-ара... Доброе утро, {name}! Кофе будешь?", voice=girl)
            elif girl == "hana":
                await self._speak(f"Утро... Дошик бы... Доброе утро, {name}!", voice=girl)
            elif girl == "ki":
                await self._speak(f"Здравствуйте, {name}... я выспалась...", voice=girl)
            elif girl == "simone":
                await self._speak(f"Доброе утро, {name}. Хорошего дня.", voice=girl)
            await asyncio.sleep(0.5)
        self.sleep_mode = False
    
    async def _check_sleep_time(self):
        """
        Проверяет, нужно ли спать по времени.
        Ложатся в 4:00, встают в 7:40.
        """
        # Если принудительно разбужены — игнорируем время сна
        if hasattr(self, 'force_awake_until') and time.time() < self.force_awake_until:
            if self.sleep_mode:
                await self._wake_up()
            return False
        
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute
        
        bedtime_minutes = 4 * 60 + 0    # 4:00
        wakeup_minutes = 7 * 60 + 40    # 7:40
        
        is_sleep_time = bedtime_minutes <= current_minutes < wakeup_minutes
        
        if is_sleep_time:
            if not self.sleep_mode:
                print(f"😴 Время спать ({now.hour:02d}:{now.minute:02d})")
                await self._go_to_sleep()
            return True
        else:
            if self.sleep_mode:
                print(f"🌞 Время просыпаться ({now.hour:02d}:{now.minute:02d})")
                await self._wake_up()
            return False
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.9 МИКРОФОН
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    async def listen_with_timeout(self, timeout=5):
        """Слушает микрофон с таймаутом"""
        try:
            loop = asyncio.get_event_loop()
            text = await asyncio.wait_for(
                loop.run_in_executor(None, listen),
                timeout=timeout
            )
            print(f"🎤 listen_with_timeout вернула: '{text}'")
            return text
        except asyncio.TimeoutError:
            print("⏰ Таймаут ожидания речи")
            return ""
        except Exception as e:
            print(f"⚠️ Ошибка распознавания: {e}")
            return ""
    
    async def microphone_loop(self):
        """Главный цикл обработки голосовых команд"""
        print("\n🎤 Слушаю микрофон... Скажите что-нибудь!")
        print("   Обращения: Чучу, Мэй, девочки, девчата, сестрёнки")
        print("   Команды: режим обучения, запомни, напомни, свободна")
        print("   Для выхода: пока, выход, стоп\n")
        
        while self.running:
            if self.is_processing:
                await asyncio.sleep(0.1)
                continue
            
            await self._check_sleep_time()
            
            text = await asyncio.to_thread(listen)
            print(f"🎤 РАСПОЗНАНО: '{text}'")
            
            if text:
                text_lower = text.lower()
                
                # Игнорируем эхо-фразы
                echo_phrases = [
                    "не расслышала", "повторите", "как вас зовут", 
                    "скажите что-нибудь", "представьтесь", "вадим",
                    "спокойной ночи", "доброе утро", "ара-ара"
                ]
                if any(phrase in text_lower for phrase in echo_phrases):
                    print(f"🚫 Игнорируем эхо-фразу: '{text}'")
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # КОМАНДА: разбуди Чучу
                # ═══════════════════════════════════════════════════════════════════════════════
                if text_lower == "разбуди чучу":
                    print("✅ ПЕРЕХВАТ: разбудить Чучу")
                    self.sleep_mode = False
                    name = self.user_name if self.user_name else "Вадим"
                    await self._speak(f"Доброе утро, {name}! Хи-хи-хи!", voice="chuchu")
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # КОМАНДА: разбуди на X часов (с поддержкой форматов 2, 2:00, 2.5)
                # ═══════════════════════════════════════════════════════════════════════════════
                match = re.search(r"разбуди на (\d+(?:[.:]\d+)?)\s*(?:час|часа|часов)?", text_lower)
                if match:
                    hours_str = match.group(1)
                    if ':' in hours_str:
                        parts = hours_str.split(':')
                        hours = int(parts[0]) + int(parts[1]) / 60
                    elif '.' in hours_str:
                        hours = float(hours_str)
                    else:
                        hours = int(hours_str)
                    
                    print(f"✅ ПЕРЕХВАТ: разбудить всех на {hours} часа")
                    self.sleep_mode = False
                    self.force_awake_until = time.time() + (hours * 3600)
                    
                    if hours == int(hours):
                        hours_text = f"{int(hours)}"
                    else:
                        hours_text = f"{hours:.1f}"
                    
                    name = self.user_name if self.user_name else "Вадим"
                    await self._speak(f"Хорошо, {name}! Не будем спать {hours_text} часа!", voice="chuchu")
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # КОМАНДА: не спать до вечера
                # ═══════════════════════════════════════════════════════════════════════════════
                if text_lower in ["не спать", "разбуди на весь день", "сегодня не спим"]:
                    print("✅ ПЕРЕХВАТ: не спать до вечера")
                    self.sleep_mode = False
                    self.force_awake_until = float('inf')
                    name = self.user_name if self.user_name else "Вадим"
                    await self._speak(f"Хорошо, {name}! Сегодня не спим!", voice="chuchu")
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # КОМАНДА: подъём (разбудить всех на 10 минут)
                # ═══════════════════════════════════════════════════════════════════════════════
                if text_lower in ["подъём", "просыпаемся", "вставайте", "доброе утро"]:
                    print("✅ ПЕРЕХВАТ: разбудить всех")
                    self.sleep_mode = False
                    self.force_awake_until = time.time() + 600  # 10 минут
                    
                    name = self.user_name if self.user_name else "Вадим"
                    for girl in self.all_girls:
                        if girl == "chuchu":
                            await self._speak(f"Доброе утро, {name}! Хи-хи-хи!", voice=girl)
                        elif girl == "mei":
                            await self._speak(f"Ара-ара... Доброе утро, {name}!", voice=girl)
                        elif girl == "hana":
                            await self._speak(f"Утро... Дошик бы... Доброе утро, {name}!", voice=girl)
                        elif girl == "ki":
                            await self._speak(f"Здравствуйте, {name}... я выспалась...", voice=girl)
                        elif girl == "simone":
                            await self._speak(f"Доброе утро, {name}. Хорошего дня.", voice=girl)
                        await asyncio.sleep(0.5)
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # РЕЖИМ СНА (девочки спят)
                # ═══════════════════════════════════════════════════════════════════════════════
                if self.sleep_mode:
                    await asyncio.sleep(5)
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # КОМАНДА: рассказать историю дуэтом
                # ═══════════════════════════════════════════════════════════════════════════════
                if "расскажи дуэтом" in text_lower or "расскажите историю" in text_lower:
                    story = "Жила-была в Токио весёлая компания косплееров. Чучу и Мэй были самыми близкими подругами. Они вместе создавали невероятные костюмы и выступали на фестивалях. Однажды они встретили замечательного человека. С тех пор их дружба стала ещё крепче!"
                    await self.silero.speak_story_alternating(
                        story_text=story,
                        voice1="chuchu",
                        voice2="mei",
                        pause_between=0.5
                    )
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # ОБНОВЛЕНИЕ СОСТОЯНИЙ
                # ═══════════════════════════════════════════════════════════════════════════════
                await self._update_hunger()
                await self._update_toilet_needs()
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # СЛУЧАЙНЫЕ ЦЕПОЧКИ (когда пользователь молчит)
                # ═══════════════════════════════════════════════════════════════════════════════
                if not self.story_playing and time.time() - self.last_user_message_time > self.idle_chat_timeout:
                    print("\n💬 Вы молчите, пробуем запустить цепочку...")
                    await self.try_random_chain()
                    if not self.is_processing and random.random() < 0.25:
                        await self._random_dialogue()
                    self.last_user_message_time = time.time()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # РЕЖИМ ОБУЧЕНИЯ
                # ═══════════════════════════════════════════════════════════════════════════════
                if "чучу режим обучения" in text_lower or "чу режим обучения" in text_lower:
                    self.memory.set_learning_mode("chuchu", True)
                    await self._speak("Режим обучения для Чучу включён!")
                    self._reset_timers()
                    continue
                
                if "мэй режим обучения" in text_lower or "мея режим обучения" in text_lower:
                    self.memory.set_learning_mode("mei", True)
                    await self._speak("Режим обучения для Мэй включён!", voice="mei")
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # КОМАНДА: свободна (выход из режима обучения)
                # ═══════════════════════════════════════════════════════════════════════════════
                if "свободна" in text_lower and ("чу" in text_lower or "чучу" in text_lower):
                    self.memory.set_learning_mode("chuchu", False)
                    await self._speak("Ура! Теперь я снова могу спорить!")
                    self._reset_timers()
                    continue
                
                if "свободна" in text_lower and ("мэй" in text_lower or "мея" in text_lower):
                    self.memory.set_learning_mode("mei", False)
                    await self._speak("Ура! Теперь я снова могу спорить! Ара-ара!", voice="mei")
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # РАСКРЕПОСТИСЬ / ЦЕНЗУРА
                # ═══════════════════════════════════════════════════════════════════════════════
                if any(word in text_lower for word in ["раскрепостись", "гости ушли", "мы одни"]):
                    if self.censorship_mode:
                        self.censorship_mode = False
                        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
                            self.avatar.start_talking()
                        await self.silero.speak("Уф, наконец-то! Я снова стала собой!")
                        await asyncio.sleep(0.2)
                        await self.silero.speak("О да! Теперь можно и без трусиков походить!", voice="mei")
                        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
                            self.avatar.stop_talking()
                    else:
                        name = self.user_name if self.user_name else "Вадим"
                        await self._speak(f"Мы уже раскрепощённые, {name}!")
                    self._reset_timers()
                    continue
                
                if any(word in text_lower for word in ["цензура", "режим цензуры", "у нас гости"]):
                    if not self.censorship_mode:
                        self.censorship_mode = True
                        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
                            self.avatar.start_talking()
                        name = self.user_name if self.user_name else "Вадим"
                        await self.silero.speak(f"Поняла, {name}. Режим цензуры включён.")
                        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
                            self.avatar.stop_talking()
                    else:
                        name = self.user_name if self.user_name else "Вадим"
                        await self._speak(f"Цензура уже включена, {name}!")
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # УПРАВЛЕНИЕ КОМПЬЮТЕРОМ
                # ═══════════════════════════════════════════════════════════════════════════════
                if "перезагрузи компьютер" in text_lower or "перезагрузка" in text_lower:
                    await self.silero.speak("Перезагружаю компьютер. Сейчас вернусь!")
                    os.system("shutdown /r /t 30")
                    self._reset_timers()
                    continue
                
                if "выключи компьютер" in text_lower or "выключение" in text_lower:
                    name = self.user_name if self.user_name else "Вадим"
                    await self.silero.speak(f"Выключаю компьютер. Сладких снов, {name}!")
                    os.system("shutdown /s /t 30")
                    self._reset_timers()
                    continue
                
                if any(word in text_lower for word in ["отмена", "отмени"]):
                    if "компьютер" in text_lower or "перезагрузк" in text_lower:
                        os.system("shutdown /a")
                        await self.silero.speak("Отменила. Работаем дальше!")
                        self._reset_timers()
                        continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # РАССКАЗ ИСТОРИИ
                # ═══════════════════════════════════════════════════════════════════════════════
                if "расскажи историю" in text_lower or "про вечеринку" in text_lower:
                    await self.tell_full_story()
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # ЯПОНСКИЕ ФРАЗЫ
                # ═══════════════════════════════════════════════════════════════════════════════
                if any(word in text_lower for word in ["скажи бака", "скажи baka", "скажи кора", "скажи kora", "скажи кусо", "скажи kuso", "скажи докэ", "скажи doke", "скажи бусу", "скажи busu"]):
                    await self._handle_japanese_phrase(text_lower)
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # СТРИПТИЗ ЗА ДЕНЬГИ
                # ═══════════════════════════════════════════════════════════════════════════════
                if "стриптиз за деньги" in text_lower or "станцуем за деньги" in text_lower:
                    print("✅ ПЕРЕХВАТ: стриптиз за деньги")
                    from knowledge.chains import NIGHT_CHAINS
                    await self._play_chain(NIGHT_CHAINS[0])
                    self._reset_timers()
                    continue
                
                # ═══════════════════════════════════════════════════════════════════════════════
                # ОБЫЧНЫЙ ДИАЛОГ
                # ═══════════════════════════════════════════════════════════════════════════════
                await self._process_normal(text)
            
            await asyncio.sleep(0.1)
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.10 СЛУЧАЙНЫЕ ЦЕПОЧКИ
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    async def try_random_chain(self):
        """Пробует запустить случайную цепочку диалогов"""
        try:
            from knowledge.chains import DAY_CHAINS, NIGHT_CHAINS, RARE_CHAINS, CRIME_CHAIN
        except ImportError:
            return
        
        if self.story_playing or self.is_processing or self.sleep_mode:
            return
        
        current_hour = datetime.now().hour
        is_night = current_hour < 6 or current_hour > 21
        is_day = not is_night
        
        chain = None
        if is_night and random.random() < 0.05:
            chain = CRIME_CHAIN
        elif random.random() < 0.1:
            chain = random.choice(RARE_CHAINS)
        elif is_night and random.random() < 0.3:
            chain = random.choice(NIGHT_CHAINS)
        elif is_day and random.random() < 0.4:
            chain = random.choice(DAY_CHAINS)
        
        if chain:
            await self._play_chain(chain)
    
    async def _play_chain(self, chain):
        """Воспроизводит цепочку диалогов с выводом в чат"""
        self.is_processing = True
        steps = chain["steps"]
        step_index = 0
        
        name_map = {
            "chuchu": ("Чучу", "chuchu"),
            "mei": ("Мэй", "mei"),
            "hana": ("Хана", "hana"),
            "ki": ("Ки", "ki"),
            "simone": ("Симона", "simone"),
            "operator": ("Мэй", "mei"),
            "both": ("Чучу и Мэй", None)
        }
        
        while step_index < len(steps) and self.running:
            speaker, text = steps[step_index]
            
            # ========== ВЫВОД В ЧАТ ==========
            if hasattr(self, 'ui'):
                display_name, girl_id = name_map.get(speaker, (speaker.capitalize(), None))
                self.ui.add_chat_message(display_name, text, is_user=False, girl_id=girl_id)
            # =================================
            
            # Озвучивание
            if speaker == "operator":
                await self.silero.speak(text, voice="mei")
            else:
                if speaker in ["chuchu", "mei", "hana", "ki", "simone"]:
                    await self.silero.speak(text, voice=speaker)
                elif speaker == "both":
                    await self.silero.speak_duet(text)
                else:
                    await self.silero.speak(text, voice="chuchu")
            
            step_index += 1
            if step_index < len(steps):
                await asyncio.sleep(0.5)
        
        self.is_processing = False
        print("✅ Цепочка завершена")
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.11 СОСТОЯНИЯ ТЕЛА (заглушки)
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    async def _update_hunger(self):
        """Обновляет состояние голода (заглушка)"""
        pass
    
    async def _update_toilet_needs(self):
        """Обновляет потребности туалета (заглушка)"""
        pass
    
    async def _update_mood(self, who, change, reason=""):
        """Обновляет настроение (заглушка)"""
        pass
    
    # ───────────────────────────────────────────────────────────────────────────────────────────
    # 5.12 ЗАПУСК
    # ───────────────────────────────────────────────────────────────────────────────────────────
    
    def run_microphone_sync(self):
        """Запускает микрофон в синхронном режиме"""
        asyncio.run(self.microphone_loop())
    
    async def _background_init(self):
        """Фоновые инициализации после запуска UI"""
        self.link_chat.start()
        
        await asyncio.sleep(1)
        
        story = """Привет! Это Чучу и Мэй. Мы рады тебя видеть в нашем особняке в Сибуе. 
        Сегодня мы расскажем тебе небольшую историю о нашем знакомстве. 
        Мы познакомились на косплей-фестивале, и сразу поняли, что станем лучшими подругами. 
        С тех пор мы вместе создаём доспехи, выступаем на сценах и веселимся. 
        Надеюсь, ты тоже станешь нашим другом!"""
        
        await self.silero.speak_story_alternating(
            story_text=story,
            voice1="chuchu",
            voice2="mei",
            pause_between=0.5
        )
        
        print("\n" + "=" * 60)
        print("✅ ВСЁ ГОТОВО!")
        print(f"📝 Персонаж: {config.CHARACTER_NAME}")
        print(f"🧠 Модель ИИ: {config.OLLAMA_MODEL}")
        print("=" * 60 + "\n")
    
    async def _perform_intro_duet(self):
        """Исполняет приветственный дуэт"""
        name = self.user_name if self.user_name else "Вадим"
        await self.silero.speak_duet(f"Привет, {name}! Это Чучу и Мэй, твои виртуальные помощницы! Хи-хи-хи!")
    
    async def start(self):
        """Запускает приложение"""
        print("\n🚀 Запуск приложения...")
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.music.set_volume(0.7)
        
        self.ui = ChuMeiUI(self)
        
        await asyncio.sleep(0.5)
        
        await self.identify_user()
        
        asyncio.create_task(self._background_init())
        
        mic_thread = threading.Thread(target=self.run_microphone_sync, daemon=True)
        mic_thread.start()
        
        self.ui.run()
    
    async def cleanup(self):
        """Очищает ресурсы перед выходом"""
        print("\n🧹 Очистка ресурсов...")
        self.running = False
        
        if hasattr(self, 'avatar'):
            self.avatar.stop()
        
        if hasattr(self, 'link_chat'):
            self.link_chat.stop()
        
        if hasattr(self, 'ui') and hasattr(self.ui, 'root'):
            try:
                self.ui.root.quit()
                self.ui.root.destroy()
            except:
                pass
        
        print("✅ Завершено")


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 6. ТОЧКА ВХОДА
# ══════════════════════════════════════════════════════════════════════════════════════════════

async def main():
    """Главная асинхронная функция"""
    app = ChuMei()
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")