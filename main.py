"""
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                     CHUMEI ANGELS                                            ║
║                                                                                              ║
║   ГЛАВНЫЙ ФАЙЛ ПРИЛОЖЕНИЯ                                                                    ║
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
║   📝 ВЕРСИЯ: 3.1 (исправленная)                                                             ║
║   📅 ДАТА: 2026-05-24                                                                       ║
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
import logging
import traceback
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path

import pygame
import numpy as np

from avatar_video import AvatarVideo

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chumei.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def resource_path(relative_path: str) -> str:
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
from ai_brain import get_ai_response, is_llama_ready, get_system_prompt
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
# 4. МАППИНГ ГОЛОСОВ
# ══════════════════════════════════════════════════════════════════════════════════════════════

VOICE_MAPPING = {
    "chuchu": "baya",
    "mei": "xenia",
    "hana": "xenia",
    "ki": "baya",
    "simone": "baya",
}

DISPLAY_NAMES = {
    "chuchu": "Чучу",
    "mei": "Мэй",
    "hana": "Хана",
    "ki": "Ки",
    "simone": "Симона"
}


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 5. ЯПОНСКИЕ ФРАЗЫ
# ══════════════════════════════════════════════════════════════════════════════════════════════

JP_TRIGGERS = {
    ("скажи бака", "скажи baka"): ("chuchu", "Бака! Ты дурак, да? Хи-хи-хи!"),
    ("скажи кора", "скажи kora"): ("mei", "Кора, яро? Эй ты, сволочь? Ара-ара..."),
    ("скажи кусо", "скажи kuso"): ("hana", "Кусо! Дерьмо! Дошик кончился..."),
    ("скажи докэ", "скажи doke"): ("ki", "Докэ... отойди, пожалуйста..."),
    ("скажи бусу", "скажи busu"): ("simone", "Бусу. Уродина. Холодно."),
}


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 6. ОСНОВНОЙ КЛАСС CHUMEI
# ══════════════════════════════════════════════════════════════════════════════════════════════

class ChuMei:
    """ГЛАВНЫЙ КЛАСС ПРИЛОЖЕНИЯ CHUMEI ANGELS."""

    def __init__(self):
        logger.info("=" * 60)
        logger.info("ChuMei Angels — виртуальный особняк в Сибуе")
        logger.info("=" * 60)

        self.story_playing = False
        self.story_chain = []
        self.story_index = 0
        self.story_total = 0
        self.censorship_mode = True
        self.sleep_mode = False
        self.is_processing = False
        self.running = True

        self.affection_chuchu = 50
        self.affection_mei = 50
        self.affection_hana = 50
        self.affection_ki = 50
        self.affection_simone = 50

        self.link_chat = LinkChat()
        self.silero = SileroTTS()
        self.punctuator = RuPunctuator() if HAS_PUNCTUATOR else None
        self.memory = Memory()
        self.avatar = AvatarVideo()

        self.user_name = None
        self.name_asked = False
        self.name_file = resource_path("user_name.txt")
        self._load_user_name()

        self.last_response_time = 0
        self.last_user_message_time = time.time()
        self.idle_chat_timeout = 30

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

        self._init_search_sites()
        self._init_app_commands()
        self._init_volume_commands()

        self.voice_enrolled = False
        self.voice_embedding = None
        self.voice_file = resource_path("voice_sample.npy")
        self._load_voice_sample()

        self.bedtime_hour = 4
        self.wakeup_hour = 7
        self.all_girls = ["chuchu", "mei", "hana", "ki", "simone"]
        self.force_awake_until = 0

    def _load_user_name(self):
        if os.path.exists(self.name_file):
            try:
                with open(self.name_file, 'r', encoding='utf-8') as f:
                    self.user_name = f.read().strip()
                    if self.user_name:
                        self.name_asked = True
                        logger.info(f"📛 Загружено имя: {self.user_name}")
            except Exception as e:
                logger.error(f"Ошибка загрузки имени: {e}")

    def _load_voice_sample(self):
        if os.path.exists(self.voice_file):
            try:
                self.voice_embedding = np.load(self.voice_file)
                self.voice_enrolled = True
                logger.info("🔊 Образец голоса загружен")
            except Exception as e:
                logger.error(f"Ошибка загрузки голоса: {e}")

    def _init_search_sites(self):
        self.search_sites = {
            "ютуб": ["https://youtube.com", "https://www.youtube.com/results?search_query={query}"],
            "гугл": ["https://google.com", "https://www.google.com/search?q={query}"],
            "яндекс": ["https://ya.ru", "https://yandex.ru/search/?text={query}"],
            "википедия": ["https://wikipedia.org", "https://ru.wikipedia.org/wiki/{query}"],
        }
        self.search_triggers = ["открой", "запусти", "покажи", "найди", "поищи"]
        self.auto_sites = {"видео": "ютуб", "музыку": "ютуб", "погоду": "гугл"}

    def _init_app_commands(self):
        self.app_commands = {
            "блокнот": "notepad.exe",
            "калькулятор": "calc.exe",
            "проводник": "explorer.exe",
        }

    def _init_volume_commands(self):
        self.volume_commands = {
            "up": ["погромче", "громче", "громкость вверх"],
            "down": ["потише", "тише", "громкость вниз"],
            "mute": ["молча", "замолчи", "тишина"],
            "max": ["звук 100", "громкость 100", "максимум"],
        }

    def _reset_timers(self):
        self.last_response_time = time.time()
        self.last_user_message_time = time.time()
        self.is_processing = False

    def _get_real_voice(self, voice: str) -> str:
        return VOICE_MAPPING.get(voice, "xenia")

    def _is_english_text(self, text: str) -> bool:
        """Определяет, является ли текст английским (нет русских букв)"""
        # Проверяем наличие русских букв
        for c in text:
            if 'а' <= c <= 'я' or 'А' <= c <= 'Я' or c in 'ёЁ':
                return False
        # Если нет русских букв и есть хотя бы одна латинская - английский
        for c in text:
            if 'a' <= c <= 'z' or 'A' <= c <= 'Z':
                return True
        return False

    def add_chat_message(self, speaker: str, text: str, is_user: bool = False):
        if hasattr(self, 'ui'):
            self.ui.add_chat_message(speaker, text, is_user=is_user)

    async def _speak(self, text: str, voice: str = None, duet: bool = False):
        """
        Озвучивает текст целиком, определяя язык по наличию кириллицы.
        """
        if not text or not text.strip():
            return

        # Добавляем в чат
        if hasattr(self, 'ui'):
            speaker_name = voice or "chuchu"
            display_name = DISPLAY_NAMES.get(speaker_name, speaker_name)
            self.ui.add_chat_message(display_name, text, is_user=False)

        # Проверка режима сна
        sleep_phrases = ["спокойной ночи", "доброе утро", "пора спать", "баю-бай", "спать"]
        if self.sleep_mode and not any(phrase in text.lower() for phrase in sleep_phrases):
            logger.info(f"😴 {voice or 'chuchu'} спит, не отвечает...")
            return

        logger.info(f"🔊 Говорит {voice or 'chuchu'}: {text[:100]}...")

        # Анимация речи
        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
            await self.avatar.start_talking()

        # Определяем язык текста
        is_english = self._is_english_text(text)

        # Подготовка текста
        processed = normalize_text_for_tts(text)

        try:
            if is_english:
                await self.silero.speak_english(processed)
            else:
                tts_voice = self._get_real_voice(voice) if voice else "xenia"
                await self.silero.speak(processed, voice=tts_voice)
        except Exception as e:
            logger.error(f"Ошибка озвучивания: {e}")

        # Останавливаем анимацию речи
        if hasattr(self, 'avatar') and hasattr(self.avatar, 'running') and self.avatar.running:
            await self.avatar.stop_talking()

    async def _play_scene(self, scene: List[Tuple[str, str]]):
        for item in scene:
            if isinstance(item, tuple):
                speaker, line = item
                try:
                    await self._speak(line, voice=speaker)
                except Exception as e:
                    logger.error(f"Ошибка воспроизведения сцены: {e}")
                await asyncio.sleep(0.01)

    async def _random_dialogue(self):
        """Запускает случайный диалог между девочками"""
        if self.story_playing or self.sleep_mode or self.is_processing:
            logger.debug("Диалог заблокирован")
            return
        
        try:
            from knowledge.dialogues import DUET_IDLE_SAFE, DUET_IDLE_NSFW
            
            if self.censorship_mode:
                scenes = DUET_IDLE_SAFE
            else:
                scenes = DUET_IDLE_SAFE + DUET_IDLE_NSFW
            
            if not scenes:
                logger.warning("Нет доступных диалогов")
                return
            
            scene = random.choice(scenes)
            logger.info(f"💬 Запуск случайного диалога: {scene[0][:30]}...")
            
            # Воспроизводим каждую реплику в сцене
            for line in scene:
                if isinstance(line, str) and ': ' in line:
                    # Разбираем "Имя: текст"
                    name, text = line.split(': ', 1)
                    
                    # Определяем speaker
                    if name in ["Чучу", "Велма", "Девочки"]:
                        speaker = "chuchu"
                    elif name in ["Мэй", "Дафна", "Ресторан"]:
                        speaker = "mei"
                    else:
                        speaker = "chuchu"
                    
                    logger.info(f"   {name} → {speaker}: {text[:50]}")
                    await self._speak(text, voice=speaker)
                    await asyncio.sleep(0.5)  # Пауза между репликами
                else:
                    logger.warning(f"Неизвестный формат реплики: {line}")
                    
        except ImportError as e:
            logger.error(f"Не удалось загрузить диалоги: {e}")
        except Exception as e:
            logger.error(f"Ошибка в случайном диалоге: {e}")

    # ───────────────────────────────────────────────────────────────────────────────────────────
    # ИДЕНТИФИКАЦИЯ
    # ───────────────────────────────────────────────────────────────────────────────────────────

    async def identify_user(self):
        logger.info("\n🎤 Идентификация пользователя (упрощённая)...")

        if self.user_name:
            await self._speak(f"Привет, {self.user_name}! Я скучала!", voice="chuchu")
            self.censorship_mode = False
            logger.info(f"✅ Приветствуем: {self.user_name}, цензура выключена")
            return

        await self._enroll_new_user()

    async def _enroll_new_user(self):
        await self._speak("Привет! Давай познакомимся! Как тебя зовут?", voice="chuchu")

        for i in range(3):
            text = await self.listen_with_timeout(5)
            logger.info(f"🔍 Распознанный текст: '{text}'")

            if text and text.strip():
                self.user_name = text.strip().capitalize()
                logger.info(f"📛 Сохраняю имя: {self.user_name}")
                try:
                    with open(self.name_file, 'w', encoding='utf-8') as f:
                        f.write(self.user_name)
                except Exception as e:
                    logger.error(f"Ошибка сохранения имени: {e}")
                await self._speak(f"Приятно познакомиться, {self.user_name}!", voice="chuchu")
                await self._speak("А теперь... выключаю цензуру! Мы же друзья!", voice="mei")
                self.censorship_mode = False
                return
            else:
                if i < 2:
                    await self._speak("Не расслышала, повторите пожалуйста...", voice="mei")
                else:
                    self.user_name = "Гость"
                    await self._speak("Хорошо, буду называть вас Гость!", voice="chuchu")
                    self.censorship_mode = True

    async def _ask_new_user_name(self):
        await self._enroll_new_user()

    # ───────────────────────────────────────────────────────────────────────────────────────────
    # МЕТОДЫ ДЛЯ РАБОТЫ С ИИ
    # ───────────────────────────────────────────────────────────────────────────────────────────

    def _parse_target(self, text: str) -> Tuple[str, str]:
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
                    logger.info(f"🎯 Распознано обращение: {target_type}")
                    return target, clean_text
        return target, clean_text

    async def _play_response(self, response: str, target: str):
        response = re.sub(r'\[/?[а-яА-Яa-z]+\]', '', response)
        response = re.sub(r'\s+', ' ', response).strip()

        if not response:
            response = f"Привет, {self.user_name}! Чем могу помочь?"

        display_name = DISPLAY_NAMES.get(target, target.capitalize())
        if hasattr(self, 'ui'):
            self.ui.add_chat_message(display_name, response, is_user=False)

        logger.info(f"💬 {display_name}: {response[:100]}...")
        await self._speak(response, voice=target)

    async def _process_normal(self, text: str):
        if hasattr(self, 'ui') and text:
            self.ui.add_chat_message("Вы", text, is_user=True)

        if self.story_playing or self.sleep_mode:
            logger.info("⏸️ Занято (история или сон), диалог отложен.")
            return

        self.last_user_message_time = time.time()
        target, clean_text = self._parse_target(text)
        if not clean_text:
            return

        words = clean_text.lower().split()
        if "выход" in words or "завершить" in words or (words == ["пока"]):
            name = self.user_name if self.user_name else "Вадим"
            await self._speak(f"До свидания, {name}! Мы будем ждать тебя!", voice="chuchu")
            self.running = False
            return

        logger.info("\n🧠 Генерация ответа...")
        from ai_brain import get_system_prompt
        prompt = get_system_prompt(self.censorship_mode)
        if self.user_name:
            prompt = f"Ты общаешься с пользователем по имени {self.user_name}. " + prompt

        allowed_girls = ["chuchu", "mei", "hana", "ki", "simone", "both"]
        girl_for_ai = target if target in allowed_girls else "chuchu"

        try:
            response = get_ai_response(
                user_message=clean_text,
                system_prompt=prompt,
                girl_name=girl_for_ai,
                user_name=self.user_name
            )
        except Exception as e:
            logger.error(f"Ошибка получения ответа от ИИ: {e}")
            response = f"Извини, {self.user_name}, у меня что-то пошло не так. Попробуй ещё раз!"

        if response:
            response = re.sub(r'\[/?[а-яА-Яa-z]+\]', '', response)
            response = re.sub(r'\s+', ' ', response).strip()
            if not response:
                response = f"Привет, {self.user_name}! Чем могу помочь?"

        if response:
            await self._play_response(response, target)

        self.last_response_time = time.time()

    async def process_text_command(self, text: str):
        logger.info(f"📝 Текстовая команда: {text}")
        await self._process_normal(text)

    # ───────────────────────────────────────────────────────────────────────────────────────────
    # ОБРАБОТЧИКИ КОМАНД
    # ───────────────────────────────────────────────────────────────────────────────────────────

    async def _handle_japanese_phrase(self, text_lower: str) -> bool:
        for triggers, (voice, phrase) in JP_TRIGGERS.items():
            if any(trigger in text_lower for trigger in triggers):
                await self._speak(phrase, voice=voice)
                return True
        await self._speak("Не поняла, какую фразу сказать. Попробуй: скажи бака, скажи кора, скажи кусо, скажи докэ", voice="chuchu")
        return True

    # ───────────────────────────────────────────────────────────────────────────────────────────
    # РАССКАЗ ИСТОРИИ
    # ───────────────────────────────────────────────────────────────────────────────────────────

    async def tell_full_story(self):
        try:
            from knowledge.story_arc import FULL_STORY_ARC_FINAL
        except ImportError:
            await self._speak("История пока не загружена.", voice="chuchu")
            return

        if self.story_playing or self.sleep_mode:
            await self._speak("История уже рассказывается или мы спим.", voice="chuchu")
            return

        self.story_chain = FULL_STORY_ARC_FINAL
        self.story_total = len(self.story_chain)
        self.story_index = 0
        self.story_playing = True
        asyncio.create_task(self._play_story())

    async def _play_story(self):
        self.is_processing = True

        name_map = {
            "chuchu": "Чучу",
            "mei": "Мэй",
            "hana": "Хана",
            "ki": "Ки",
            "potato": "Ки",
            "simone": "Симона",
        }

        while self.story_playing and self.story_index < self.story_total:
            speaker, text = self.story_chain[self.story_index]
            self.story_index += 1

            if hasattr(self, 'ui'):
                display_name = name_map.get(speaker, speaker.capitalize())
                self.ui.add_chat_message(display_name, text, is_user=False)

            await self._speak(text, voice=speaker)
            await asyncio.sleep(0.3)

        self.story_playing = False
        self.is_processing = False

        end_text = "Вот и вся история. Надеюсь, тебе понравилось!"
        if hasattr(self, 'ui'):
            self.ui.add_chat_message("Чучу", end_text, is_user=False)
        await self._speak(end_text, voice="chuchu")

    # ───────────────────────────────────────────────────────────────────────────────────────────
    # РЕЖИМ СНА
    # ───────────────────────────────────────────────────────────────────────────────────────────

    async def _go_to_sleep(self):
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
        if hasattr(self, 'force_awake_until') and time.time() < self.force_awake_until:
            if self.sleep_mode:
                await self._wake_up()
            return False

        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute
        bedtime_minutes = 4 * 60
        wakeup_minutes = 7 * 60 + 40
        is_sleep_time = bedtime_minutes <= current_minutes < wakeup_minutes

        if is_sleep_time:
            if not self.sleep_mode:
                logger.info(f"😴 Время спать ({now.hour:02d}:{now.minute:02d})")
                await self._go_to_sleep()
            return True
        else:
            if self.sleep_mode:
                logger.info(f"🌞 Время просыпаться ({now.hour:02d}:{now.minute:02d})")
                await self._wake_up()
            return False

    # ───────────────────────────────────────────────────────────────────────────────────────────
    # МИКРОФОН
    # ───────────────────────────────────────────────────────────────────────────────────────────

    async def listen_with_timeout(self, timeout: int = 5) -> str:
        try:
            loop = asyncio.get_event_loop()
            text = await asyncio.wait_for(
                loop.run_in_executor(None, listen),
                timeout=timeout
            )
            logger.info(f"🎤 listen_with_timeout вернула: '{text}'")
            return text if text else ""
        except asyncio.TimeoutError:
            return ""
        except Exception as e:
            logger.error(f"⚠️ Ошибка распознавания: {e}")
            return ""

    async def microphone_loop(self):
        logger.info("\n🎤 Слушаю микрофон... Скажите что-нибудь!")
        
        last_idle_time = time.time()
        idle_interval = 30  # 30 секунд тишины
    
        while self.running:
            if self.is_processing:
                await asyncio.sleep(0.5)
                continue
    
            await self._check_sleep_time()
    
            try:
                text, was_activity = await asyncio.to_thread(listen, timeout=3)
            except Exception as e:
                logger.error(f"Ошибка в listen: {e}")
                await asyncio.sleep(1)
                continue
    
            if was_activity:
                # Была активность (пользователь что-то говорил или был звук)
                last_idle_time = time.time()
                logger.debug(f"Активность detected, idle таймер сброшен")
                
                if text and len(text.strip()) >= 3:
                    # Обработка распознанного текста
                    text_lower = text.lower()
                    echo_phrases = ["не расслышала", "повторите", "как вас зовут", "скажите что-нибудь"]
                    if any(phrase in text_lower for phrase in echo_phrases):
                        continue
    
                    if self.sleep_mode:
                        continue
    
                    if any(word in text_lower for word in ["скажи бака", "скажи baka", "скажи кора", "скажи kora"]):
                        await self._handle_japanese_phrase(text_lower)
                        continue
    
                    if "расскажи историю" in text_lower:
                        await self.tell_full_story()
                        continue
    
                    await self._process_normal(text)
            else:
                # Тишина - проверяем idle таймер
                time_since_activity = time.time() - last_idle_time
                logger.debug(f"Тишина: {time_since_activity:.1f} сек / {idle_interval} сек")
                
                if not self.story_playing and not self.sleep_mode and not self.is_processing:
                    if time_since_activity >= idle_interval:
                        logger.info(f"💬 {idle_interval} секунд тишины, запускаю idle диалог")
                        await self._random_dialogue()
                        last_idle_time = time.time()  # Сбрасываем после запуска
    
            await asyncio.sleep(0.2)

    # ───────────────────────────────────────────────────────────────────────────────────────────
    # ЦЕПОЧКИ
    # ───────────────────────────────────────────────────────────────────────────────────────────

    async def try_random_chain(self):
        try:
            from knowledge.chains import DAY_CHAINS, NIGHT_CHAINS, RARE_CHAINS
        except ImportError:
            return

        if self.story_playing or self.is_processing or self.sleep_mode:
            return

        current_hour = datetime.now().hour
        is_night = current_hour < 6 or current_hour > 21
        is_day = not is_night

        chain = None
        if random.random() < 0.1:
            chain = random.choice(RARE_CHAINS)
        elif is_night and random.random() < 0.3:
            chain = random.choice(NIGHT_CHAINS)
        elif is_day and random.random() < 0.4:
            chain = random.choice(DAY_CHAINS)

        if chain:
            await self._play_chain(chain)

    async def _play_chain(self, chain: Dict[str, Any]):
        self.is_processing = True
        steps = chain["steps"]

        for speaker, text in steps:
            if hasattr(self, 'ui'):
                display_name = DISPLAY_NAMES.get(speaker, speaker.capitalize())
                self.ui.add_chat_message(display_name, text, is_user=False)

            await self._speak(text, voice=speaker)
            await asyncio.sleep(0.5)

        self.is_processing = False

    # ───────────────────────────────────────────────────────────────────────────────────────────
    # СОСТОЯНИЯ ТЕЛА
    # ───────────────────────────────────────────────────────────────────────────────────────────

    async def _update_hunger(self):
        current_time = time.time()
        if current_time - self.hunger_timer > self.hunger_interval:
            self.hunger_chuchu = max(0, self.hunger_chuchu - self.hunger_decay_rate)
            self.hunger_mei = max(0, self.hunger_mei - self.hunger_decay_rate)
            self.hunger_timer = current_time

            if self.hunger_chuchu < 20:
                await self._speak("Я голодная... Может, перекусим?", voice="chuchu")
            if self.hunger_mei < 20:
                await self._speak("Ара-ара... Не пора ли нам поесть?", voice="mei")

    async def _update_toilet_needs(self):
        current_time = time.time()
        if current_time - self.last_toilet_time > 120:
            self.bladder_chuchu = max(0, self.bladder_chuchu - 5)
            self.bladder_mei = max(0, self.bladder_mei - 5)

            if self.bladder_chuchu < 30:
                await self._speak("Ой... Кажется, мне нужно...", voice="chuchu")
            if self.bladder_mei < 30:
                await self._speak("Извините... Я скоро вернусь.", voice="mei")

    # ───────────────────────────────────────────────────────────────────────────────────────────
    # ЗАПУСК
    # ───────────────────────────────────────────────────────────────────────────────────────────

    def run_microphone_sync(self):
        asyncio.run(self.microphone_loop())

    async def _background_init(self):
        self.link_chat.start()
        await asyncio.sleep(1)

        logger.info("\n" + "=" * 60)
        logger.info("✅ ВСЁ ГОТОВО!")
        logger.info(f"📝 Персонаж: {config.CHARACTER_NAME}")
        logger.info(f"🧠 Модель ИИ: {config.OLLAMA_MODEL}")
        logger.info("=" * 60 + "\n")

    async def start(self):
        logger.info("\n🚀 Запуск приложения...")
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
        logger.info("\n🧹 Очистка ресурсов...")
        self.running = False

        if hasattr(self, 'avatar'):
            await self.avatar.stop()

        if hasattr(self, 'link_chat'):
            self.link_chat.stop()

        if hasattr(self, 'ui') and hasattr(self.ui, 'root'):
            try:
                self.ui.root.quit()
                self.ui.root.destroy()
            except:
                pass

        logger.info("✅ Завершено")


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 7. ТОЧКА ВХОДА
# ══════════════════════════════════════════════════════════════════════════════════════════════

async def main():
    app = ChuMei()
    try:
        await app.start()
    except KeyboardInterrupt:
        logger.info("\n👋 До свидания!")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}\n{traceback.format_exc()}")
    finally:
        await app.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Принудительное завершение!")
    except Exception as e:
        logger.error(f"Фатальная ошибка: {e}")