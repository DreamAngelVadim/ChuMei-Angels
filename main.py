"""
╔══════════════════════════════════════════════════════════════════════════════════════════════╗
║                                     CHUMEI ANGELS                                            ║
║                                                                                              ║
║   Главный файл приложения. Управляет микрофоном, голосом, памятью и командами               ║
║                                                                                              ║
║   🏠 ОСОБНЯК: Токио, Сибуя, район Хироо, улица Сакура, дом 4                                 ║
║   👧 ДЕВОЧКИ: Чучу, Мэй, Хана, Ки, Симона                                                    ║
║   🎮 УПРАВЛЕНИЕ: Голосовые команды, триггеры, режимы                                          ║
║                                                                                              ║
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
import pygame
import numpy as np
from datetime import datetime
import threading

# Мои модули
import config
from ai_brain import get_ai_response
from avatar_video import AvatarVideo
from microphone_input import listen
from silero_tts import SileroTTS
from text_utils import clean_text, convert_number_to_words, normalize_text_for_tts
from ui_dashboard import ChuMeiUI

# Временно отключаем replacements.py, если указано в config
if hasattr(config, 'USE_REPLACEMENTS') and config.USE_REPLACEMENTS:
    from replacements import NUM_WORDS, GENDER_FIXES, REPLACEMENTS
else:
    NUM_WORDS = {}
    GENDER_FIXES = {}
    REPLACEMENTS = {}

from transliterate import transliterate
from link_chat import LinkChat
from voice_id import get_voice_embedding, compare_voices
from voice_recorder import record_voice
from memory import Memory

# accent_helper (заглушка, если нет)
try:
    from accent_helper import accent_helper
except ImportError:
    accent_helper = None

# Знания
from knowledge.cosplay import *
from knowledge.music import *
from knowledge.dialogues import *
from knowledge.personality import DUO_NAMES

# Пунктуатор (опционально)
try:
    from punctuator import RuPunctuator
    HAS_PUNCTUATOR = True
except ImportError:
    HAS_PUNCTUATOR = False


# ═══════════════════════════════════════════════════════════════════════════════
# 2. ЯПОНСКИЕ ФРАЗЫ (человеческие триггеры)
# ═══════════════════════════════════════════════════════════════════════════════

JP_TRIGGERS = {
    ("скажи бака", "скажи baka"): ("chuchu", "Бака! Ты дурак, да? Хи-хи-хи!"),
    ("скажи кора", "скажи kora"): ("mei", "Кора, яро? Эй ты, сволочь? Ара-ара..."),
    ("скажи кусо", "скажи kuso"): ("hana", "Кусо! Дерьмо! Дошик кончился..."),
    ("скажи докэ", "скажи doke"): ("ki", "Докэ... отойди, пожалуйста..."),
    ("скажи бусу", "скажи busu"): ("simone", "Бусу. Уродина. Холодно."),
}


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 3. ОСНОВНОЙ КЛАСС CHUMEI
# ══════════════════════════════════════════════════════════════════════════════════════════════

class ChuMei:
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.1 КОНСТРУКТОР
    # ═══════════════════════════════════════════════════════════════════════════
    
    def __init__(self):
        print("=" * 60)
        print("ChuMei Angels — виртуальный особняк в Сибуе")
        print("=" * 60)
        
        # ----- ФЛАГИ СОСТОЯНИЯ -----
        self.story_playing = False      # Идёт ли рассказ истории
        self.story_chain = []           # Массив с историей
        self.story_index = 0            # Текущая позиция в истории
        self.story_total = 0            # Всего реплик в истории
        self.censorship_mode = True     # Режим цензуры (True = скромно)
        self.sleep_mode = False         # Режим сна
        self.is_processing = False      # Бот занят обработкой
        self.running = True             # Основной цикл активен
        
        # ----- ОСНОВНЫЕ СИСТЕМЫ -----
        self.avatar = AvatarVideo()     # Видео-аватар
        self.link_chat = LinkChat()     # Текстовый чат
        self.silero = SileroTTS()       # Голосовой синтез (5 девочек)
        self.punctuator = RuPunctuator() if HAS_PUNCTUATOR else None
        self.memory = Memory()          # Долговременная память (JSON)
        
        # ----- ПАРАМЕТРЫ ПОЛЬЗОВАТЕЛЯ -----
        self.user_name = None
        self.name_asked = False
        self.name_file = "user_name.txt"
        self._load_user_name()
        
        # ----- ТАЙМЕРЫ -----
        self.last_response_time = 0
        self.last_user_message_time = time.time()
        self.idle_chat_timeout = 30     # 30 секунд бездействия → случайный диалог
        
        # ----- ПОТРЕБНОСТИ ДЕВОЧЕК -----
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
        
        # ----- КОМАНДЫ И ТРИГГЕРЫ -----
        self._init_search_sites()       # Поисковые сайты
        self._init_app_commands()       # Запуск приложений
        self._init_volume_commands()    # Управление громкостью
        
        # ----- РАСПОЗНАВАНИЕ ГОЛОСА -----
        self.voice_enrolled = False
        self.voice_embedding = None
        self.voice_file = "voice_sample.npy"
        self._load_voice_sample()
        
        # ----- РЕЖИМ СНА -----
        self.bedtime_hour = 23          # 11 вечера
        self.wakeup_hour = 8            # 8 утра
        self.all_girls = ["chuchu", "mei", "hana", "ki", "simone"]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.2 ПРИВАТНЫЕ МЕТОДЫ (загрузка данных, инициализация подсистем)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _load_user_name(self):
        if os.path.exists(self.name_file):
            with open(self.name_file, 'r', encoding='utf-8') as f:
                self.user_name = f.read().strip()
                if self.user_name:
                    self.name_asked = True
                    print(f"📛 Загружено имя: {self.user_name}")
    
    def _load_voice_sample(self):
        if os.path.exists(self.voice_file):
            self.voice_embedding = np.load(self.voice_file)
            self.voice_enrolled = True
            print("🔊 Образец голоса загружен")
    
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
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.3 МЕТОДЫ ДЛЯ РАБОТЫ С ГОЛОСОМ
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _speak(self, text, voice=None, duet=False):
        sleep_phrases = ["спокойной ночи", "доброе утро", "пора спать", "баю-бай", "спать", "укладываемся", "просыпаемся"]
        if self.sleep_mode and not any(phrase in text.lower() for phrase in sleep_phrases):
            print(f"😴 {voice or 'chuchu'} спит, не отвечает...")
            return
        
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
        await self.avatar.start_talking()
        
        if duet:
            await self.silero.speak_duet(text)
        elif voice == "mei":
            await self.silero.speak(text, voice="mei")
        else:
            await self.silero.speak(text, voice=voice or "chuchu")
        
        await self.avatar.stop_talking()
    
    async def _play_scene(self, scene):
        for item in scene:
            if isinstance(item, tuple):
                speaker, line = item
                if speaker == "chuchu":
                    await self.silero.speak(line, voice="chuchu")
                elif speaker == "mei":
                    await self.silero.speak(line, voice="mei")
                elif speaker == "both":
                    await self.silero.speak_duet(line)
                await asyncio.sleep(0.05)
    
    async def _random_dialogue(self):
        if self.story_playing or self.sleep_mode:
            return
        if self.censorship_mode:
            scene = random.choice(DUET_IDLE_SAFE)
        else:
            scene = random.choice(DUET_IDLE_SAFE + DUET_IDLE_NSFW)
        await self._play_scene(scene)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.4 МЕТОДЫ ДЛЯ РАБОТЫ С ИИ И ОБРАЩЕНИЯМИ
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _parse_target(self, text):
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
        await self.avatar.start_talking()
        
        response = response.replace("[chuchu]", "[чучу]").replace("[/chuchu]", "[/чучу]")
        response = response.replace("[mei]", "[мэй]").replace("[/mei]", "[/мэй]")
        response = response.replace("[hana]", "[хана]").replace("[/hana]", "[/хана]")
        response = response.replace("[ki]", "[ки]").replace("[/ki]", "[/ки]")
        response = response.replace("[simone]", "[симона]").replace("[/simone]", "[/симона]")
        response = response.replace("[chu]", "[чучу]").replace("[/chu]", "[/чучу]")
        
        parts = re.findall(r'\[(чучу|чу|мэй|мей|mei|хана|hana|ки|ki|симона|simone)\](.*?)(?:\[/|$)', response, re.IGNORECASE | re.DOTALL)
        
        if parts:
            for speaker, line in parts:
                line = line.strip()
                if line:
                    clean_line = transliterate(clean_text(line))
                    if speaker.lower() in ["мэй", "мей", "mei"]:
                        await self.silero.speak(clean_line, voice="mei")
                    elif speaker.lower() in ["хана", "hana"]:
                        await self.silero.speak(clean_line, voice="hana")
                    elif speaker.lower() in ["ки", "ki"]:
                        await self.silero.speak(clean_line, voice="ki")
                    elif speaker.lower() in ["симона", "simone"]:
                        await self.silero.speak(clean_line, voice="simone")
                    else:
                        await self.silero.speak(clean_line, voice="chuchu")
                    await asyncio.sleep(0.2)
        else:
            clean_response = transliterate(clean_text(response))
            if target == "mei":
                await self.silero.speak(clean_response, voice="mei")
            elif target == "hana":
                await self.silero.speak(clean_response, voice="hana")
            elif target == "ki":
                await self.silero.speak(clean_response, voice="ki")
            elif target == "simone":
                await self.silero.speak(clean_response, voice="simone")
            elif target == "both":
                await self.silero.speak_duet(clean_response)
            else:
                await self.silero.speak(clean_response, voice="chuchu")
        
        await self.avatar.stop_talking()
        print("✅ Ответ воспроизведён")
    
    async def _process_normal(self, text):
        if self.story_playing or self.sleep_mode:
            print("⏸️ Занято (история или сон), диалог отложен.")
            return
        
        self.last_user_message_time = time.time()
        target, clean_text = self._parse_target(text)
        if not clean_text:
            return
        
        words = clean_text.lower().split()
        if "выход" in words or "завершить" in words or (words == ["пока"]):
            await self._speak(f"До свидания, {self.user_name or 'Вадим'}! Мы будем ждать тебя!")
            self.running = False
            return
        
        print("\n🧠 Генерация ответа...")
        prompt = config.CHARACTER_PERSONALITY if not self.censorship_mode else config.CENSORED_PERSONALITY
        if self.user_name:
            prompt = f"Ты общаешься с пользователем по имени {self.user_name}. " + prompt
        
        allowed_girls = ["chuchu", "mei", "hana", "ki", "simone", "both"]
        girl_for_ai = target if target in allowed_girls else "chuchu"
        response = get_ai_response(user_message=clean_text, system_prompt=prompt, girl_name=girl_for_ai)
        if response:
            await self._play_response(response, target)
        
        self.last_response_time = time.time()
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.5 ЯПОНСКИЕ ФРАЗЫ И КОМАНДЫ
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _handle_japanese_phrase(self, text_lower):
        for triggers, (voice, phrase) in JP_TRIGGERS.items():
            if any(trigger in text_lower for trigger in triggers):
                await self._speak(phrase, voice=voice)
                return True
        await self._speak("Не поняла, какую фразу сказать. Попробуй: скажи бака, скажи кора, скажи кусо, скажи докэ")
        return True
    
    async def _handle_change_body(self, text_lower):
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
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.6 ИСТОРИЯ ВЕЧЕРИНКИ
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def tell_full_story(self):
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
        self.is_processing = True
        await self.avatar.start_talking()
        while self.story_playing and self.story_index < self.story_total:
            speaker, text = self.story_chain[self.story_index]
            self.story_index += 1
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
        await self.avatar.stop_talking()
        self.story_playing = False
        self.is_processing = False
        await self._speak("Вот и вся история. Надеюсь, тебе понравилось!")
    
    async def continue_story(self):
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
        if self.story_playing:
            self.story_playing = False
            self.is_processing = False
            await self._speak("Останавливаю рассказ.")
        else:
            await self._speak("История и не рассказывалась.")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.7 ПОТРЕБНОСТИ (заглушки)
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _update_hunger(self):
        pass
    
    async def _update_toilet_needs(self):
        pass
    
    async def _update_mood(self, who, change, reason=""):
        pass
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.8 РЕЖИМ СНА
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def _check_sleep_time(self):
        current_hour = datetime.now().hour
        
        if current_hour >= self.bedtime_hour or current_hour < self.wakeup_hour:
            if not self.sleep_mode:
                self.sleep_mode = True
                for girl in self.all_girls:
                    if girl == "chuchu":
                        await self._speak("Спокойной ночи, Вадим... Сладких снов...", voice=girl)
                    elif girl == "mei":
                        await self._speak("Ара-ара... Увидимся утром...", voice=girl)
                    elif girl == "hana":
                        await self._speak("Надеюсь, мне приснится дошик...", voice=girl)
                    elif girl == "ki":
                        await self._speak("Спокойной... ночи... (зевает)", voice=girl)
                    elif girl == "simone":
                        await self._speak("Спокойной ночи, Вадим. Пусть тебе приснится что-то хорошее.", voice=girl)
                    await asyncio.sleep(0.5)
            return True
        else:
            if self.sleep_mode:
                self.sleep_mode = False
                for girl in self.all_girls:
                    if girl == "chuchu":
                        await self._speak("Доброе утро, Вадим! Хи-хи-хи!", voice=girl)
                    elif girl == "mei":
                        await self._speak("Ара-ара... Кто хочет кофе?", voice=girl)
                    elif girl == "hana":
                        await self._speak("Утро... Дошик бы...", voice=girl)
                    elif girl == "ki":
                        await self._speak("Здравствуйте... я выспалась...", voice=girl)
                    elif girl == "simone":
                        await self._speak("Доброе утро. Хорошего дня.", voice=girl)
                    await asyncio.sleep(0.5)
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.9 МИКРОФОН
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def microphone_loop(self):
        """Главный цикл: слушает микрофон, распознаёт речь, выполняет команды"""
        print("\n🎤 Слушаю микрофон... Скажите что-нибудь!")
        print("   Обращения: Чучу, Мэй, девочки, девчата, сестрёнки")
        print("   Команды: режим обучения, запомни, напомни, свободна")
        print("   Для выхода: пока, выход, стоп\n")
        
        while self.running:
            if self.is_processing:
                await asyncio.sleep(0.1)
                continue
            
            await self._check_sleep_time()
            
            if self.sleep_mode:
                await asyncio.sleep(10)
                continue
            
            await self._update_hunger()
            await self._update_toilet_needs()
            
            if not self.story_playing and time.time() - self.last_user_message_time > self.idle_chat_timeout:
                print("\n💬 Вы молчите, пробуем запустить цепочку...")
                await self.try_random_chain()
                if not self.is_processing and random.random() < 0.25:
                    await self._random_dialogue()
                self.last_user_message_time = time.time()
                continue
            
            text = await asyncio.to_thread(listen)
            print(f"🎤 РАСПОЗНАНО: '{text}'")
            
            if text:
                text_lower = text.lower()
                
                # ----- ТРИГГЕРЫ -----
                
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
                
                if any(word in text_lower for word in ["раскрепостись", "гости ушли", "мы одни"]):
                    if self.censorship_mode:
                        self.censorship_mode = False
                        await self.avatar.start_talking()
                        await self.silero.speak("Уф, наконец-то! Я снова стала собой!")
                        await asyncio.sleep(0.2)
                        await self.silero.speak("О да! Теперь можно и без трусиков походить!", voice="mei")
                        await self.avatar.stop_talking()
                    else:
                        await self._speak("Мы уже раскрепощённые, Вадим!")
                    self._reset_timers()
                    continue
                
                if any(word in text_lower for word in ["цензура", "режим цензуры", "у нас гости"]):
                    if not self.censorship_mode:
                        self.censorship_mode = True
                        await self.avatar.start_talking()
                        await self.silero.speak("Поняла, Вадим. Режим цензуры включён.")
                        await self.avatar.stop_talking()
                    else:
                        await self._speak("Цензура уже включена, Вадим!")
                    self._reset_timers()
                    continue
                
                if "перезагрузи компьютер" in text_lower or "перезагрузка" in text_lower:
                    await self.silero.speak("Перезагружаю компьютер. Сейчас вернусь!")
                    os.system("shutdown /r /t 30")
                    self._reset_timers()
                    continue
                
                if "выключи компьютер" in text_lower or "выключение" in text_lower:
                    await self.silero.speak("Выключаю компьютер. Сладких снов, Вадим!")
                    os.system("shutdown /s /t 30")
                    self._reset_timers()
                    continue
                
                if any(word in text_lower for word in ["отмена", "отмени"]):
                    if "компьютер" in text_lower or "перезагрузк" in text_lower:
                        os.system("shutdown /a")
                        await self.silero.speak("Отменила. Работаем дальше!")
                        self._reset_timers()
                        continue
                
                if "расскажи историю" in text_lower or "про вечеринку" in text_lower:
                    await self.tell_full_story()
                    self._reset_timers()
                    continue
                
                if "баю-бай" in text_lower or "укладываемся" in text_lower or ("спать" in text_lower and ("девочки" in text_lower or "все" in text_lower)):
                    print("✅ ПЕРЕХВАТ: уложить спать")
                    self.sleep_mode = True
                    for girl in self.all_girls:
                        if girl == "chuchu":
                            await self._speak("Спокойной ночи, Вадим...", voice=girl)
                        elif girl == "mei":
                            await self._speak("Ара-ара... Увидимся утром...", voice=girl)
                        elif girl == "hana":
                            await self._speak("Не подглядывай...", voice=girl)
                        elif girl == "ki":
                            await self._speak("Спокойной... ночи...", voice=girl)
                        elif girl == "simone":
                            await self._speak("Сладких снов.", voice=girl)
                        await asyncio.sleep(0.5)
                    self._reset_timers()
                    continue
                
                if any(word in text_lower for word in ["скажи бака", "скажи baka", "скажи кора", "скажи kora", "скажи кусо", "скажи kuso", "скажи докэ", "скажи doke", "скажи бусу", "скажи busu"]):
                    await self._handle_japanese_phrase(text_lower)
                    self._reset_timers()
                    continue
                
                if "стриптиз за деньги" in text_lower or "станцуем за деньги" in text_lower:
                    print("✅ ПЕРЕХВАТ: стриптиз за деньги")
                    from knowledge.chains import NIGHT_CHAINS
                    await self._play_chain(NIGHT_CHAINS[0])
                    self._reset_timers()
                    continue
                
                if "доброе утро" in text_lower or "просыпайтесь" in text_lower or "подъём" in text_lower:
                    print("✅ ПЕРЕХВАТ: пробуждение")
                    if self.sleep_mode:
                        self.sleep_mode = False
                        for girl in self.all_girls:
                            if girl == "chuchu":
                                await self._speak("Доброе утро, Вадим! Хи-хи-хи!", voice=girl)
                            elif girl == "mei":
                                await self._speak("Ара-ара... Кто хочет кофе?", voice=girl)
                            elif girl == "hana":
                                await self._speak("Утро... Дошик бы...", voice=girl)
                            elif girl == "ki":
                                await self._speak("Здравствуйте... я выспалась...", voice=girl)
                            elif girl == "simone":
                                await self._speak("Доброе утро. Хорошего дня.", voice=girl)
                            await asyncio.sleep(0.5)
                    else:
                        await self._speak("Мы уже не спим, Вадим! Доброе утро!")
                    self._reset_timers()
                    continue
                
                await self._process_normal(text)
            
            await asyncio.sleep(0.1)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.10 СЛУЧАЙНЫЕ ЦЕПОЧКИ
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def try_random_chain(self):
        from knowledge.chains import DAY_CHAINS, NIGHT_CHAINS, RARE_CHAINS, CRIME_CHAIN
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
        self.is_processing = True
        steps = chain["steps"]
        step_index = 0
        while step_index < len(steps) and self.running:
            speaker, text = steps[step_index]
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
    
    # ═══════════════════════════════════════════════════════════════════════════
    # 3.11 ЗАПУСК И ОСТАНОВКА
    # ═══════════════════════════════════════════════════════════════════════════
    
    def run_microphone_sync(self):
        """Запускает микрофон в синхронном режиме (для отдельного потока)"""
        asyncio.run(self.microphone_loop())
    
    async def start(self):
        print("\n🚀 Запуск приложения...")
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.music.set_volume(0.7)
        
        print("🔊 Тест голосов Ханы и Ки...")
        await self.silero.speak("Привет, меня зовут Хана, я люблю дошик и деньги!", voice="hana")
        await asyncio.sleep(1)
        await self.silero.speak("Здравствуйте... я Ки. Я... стесняюсь.", voice="ki")
        print("✅ Тест голосов завершён")
        
        asyncio.create_task(self.avatar.start())
        self.link_chat.start()
        
        await asyncio.sleep(2)
        await self._perform_intro_duet()
        
        print("\n" + "=" * 60)
        print("✅ ВСЁ ГОТОВО!")
        print(f"📝 Персонаж: {config.CHARACTER_NAME}")
        print(f"🧠 Модель ИИ: {config.OLLAMA_MODEL}")
        print("=" * 60 + "\n")
        
        # Запускаем интерфейс в главном потоке
        self.ui = ChuMeiUI(self)
        
        # Запускаем микрофон в отдельном потоке
        mic_thread = threading.Thread(target=self.run_microphone_sync, daemon=True)
        mic_thread.start()
        
        # Запускаем главный цикл интерфейса
        self.ui.run()
    
    async def _perform_intro_duet(self):
        await self.silero.speak_duet("Привет, Вадим! Это Чучу и Мэй, твои виртуальные помощницы! Хи-хи-хи!")
    
    async def cleanup(self):
        print("\n🧹 Очистка ресурсов...")
        self.running = False
        if self.avatar:
            await self.avatar.stop()
        if self.link_chat:
            self.link_chat.stop()
        print("✅ Завершено")


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 4. ТОЧКА ВХОДА
# ══════════════════════════════════════════════════════════════════════════════════════════════

async def main():
    app = ChuMei()
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")