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
# 1. ИМПОРТЫ (подключаем внешние и внутренние модули)
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

# Мои модули
import config
from ai_brain import get_ai_response
from avatar_video import AvatarVideo
from microphone_input import listen
from silero_tts import SileroTTS
from replacements import NUM_WORDS, GENDER_FIXES, REPLACEMENTS
from transliterate import transliterate
from link_chat import LinkChat
from voice_id import get_voice_embedding, compare_voices
from voice_recorder import record_voice
from memory import Memory
from accent_helper import accent_helper

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


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (работа с текстом, цифрами, английскими буквами)
# ══════════════════════════════════════════════════════════════════════════════════════════════

def clean_text(text):
    """Очищает текст от лишних символов, эмодзи и нормализует числа"""
    text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1 \2', text)
    for num, word in sorted(NUM_WORDS.items(), key=lambda x: -len(x[0])):
        text = re.sub(r'\b' + num + r'\b', word, text)
    return text


def convert_number_to_words(num):
    """Преобразует число в слова (поддержка до 9999)"""
    if num < 10:
        return ['ноль','один','два','три','четыре','пять','шесть','семь','восемь','девять'][num]
    elif num < 20:
        teens = ['десять','одиннадцать','двенадцать','тринадцать','четырнадцать','пятнадцать',
                 'шестнадцать','семнадцать','восемнадцать','девятнадцать']
        return teens[num - 10]
    elif num < 100:
        tens = ['','десять','двадцать','тридцать','сорок','пятьдесят','шестьдесят',
                'семьдесят','восемьдесят','девяносто']
        t = tens[num // 10]
        u = convert_number_to_words(num % 10) if num % 10 != 0 else ''
        return f"{t} {u}".strip()
    elif num < 1000:
        hundreds = ['','сто','двести','триста','четыреста','пятьсот','шестьсот','семьсот','восемьсот','девятьсот']
        h = hundreds[num // 100]
        rest = convert_number_to_words(num % 100) if num % 100 != 0 else ''
        return f"{h} {rest}".strip()
    elif num < 10000:
        thousands = ['','одна тысяча','две тысячи','три тысячи','четыре тысячи','пять тысяч','шесть тысяч','семь тысяч','восемь тысяч','девять тысяч']
        t = thousands[num // 1000]
        rest = convert_number_to_words(num % 1000) if num % 1000 != 0 else ''
        return f"{t} {rest}".strip()
    else:
        return str(num)


def normalize_text_for_tts(text):
    """Заменяет все цифры на слова, английские буквы на русские"""
    
    # Специальные словари для частых чисел
    number_words = {
        "100": "сто", "200": "двести", "300": "триста", "400": "четыреста",
        "500": "пятьсот", "600": "шестьсот", "700": "семьсот", "800": "восемьсот",
        "900": "девятьсот",
        "1000": "тысяча", "2000": "две тысячи", "3000": "три тысячи",
    }
    
    # Прямая замена частых чисел (самый надёжный способ)
    for num, word in number_words.items():
        text = text.replace(num, word)
    
    # Замена диапазонов типа "52-54"
    text = re.sub(r'(\d+)-(\d+)', lambda m: f"{convert_number_to_words(int(m.group(1)))} {convert_number_to_words(int(m.group(2)))}", text)
    
    # Замена всех остальных чисел (от 10 до 9999)
    def replace_number(match):
        num_str = match.group(0)
        try:
            num = int(num_str)
            return convert_number_to_words(num)
        except:
            return num_str
    
    # Ищем любые числа от 10 до 9999 (не заменяем уже заменённые слова)
    text = re.sub(r'\b(?!сто|двести|триста|четыреста|пятьсот|шестьсот|семьсот|восемьсот|девятьсот|тысяча)\d{2,4}\b', replace_number, text)
    
    # Отдельные цифры 0-9
    digit_map = {
        '0': 'ноль', '1': 'один', '2': 'два', '3': 'три', '4': 'четыре',
        '5': 'пять', '6': 'шесть', '7': 'семь', '8': 'восемь', '9': 'девять'
    }
    for digit, word in digit_map.items():
        text = text.replace(digit, word)
    
    # Замена английских букв на русские
    eng_to_rus = {
        'a': 'эй', 'b': 'би', 'c': 'си', 'd': 'ди', 'e': 'и',
        'f': 'эф', 'g': 'джи', 'h': 'эйч', 'i': 'ай', 'j': 'джей',
        'k': 'кей', 'l': 'эл', 'm': 'эм', 'n': 'эн', 'o': 'оу',
        'p': 'пи', 'q': 'кью', 'r': 'ар', 's': 'эс', 't': 'ти',
        'u': 'ю', 'v': 'ви', 'w': 'дабл-ю', 'x': 'экс', 'y': 'уай', 'z': 'зет'
    }
    
    for eng, rus in eng_to_rus.items():
        text = re.sub(r'\b' + eng + r'\b', rus, text, flags=re.IGNORECASE)
        text = re.sub(r'([а-яА-Я])' + eng + r'([а-яА-Я])', r'\1' + rus + r'\2', text, flags=re.IGNORECASE)
    
    return text


# ═══════════════════════════════════════════════════════════════════════════════
# ЯПОНСКИЕ ФРАЗЫ (человеческие триггеры)
# ═══════════════════════════════════════════════════════════════════════════════

JP_TRIGGERS = {
    # Чучу
    ("скажи бака", "скажи baka"): ("chuchu", "Бака! Ты дурак, да? Хи-хи-хи!"),
    ("скажи шиматта", "скажи shimatta"): ("chuchu", "Шиматта! Вот чёрт! Трусики жалко!"),
    ("скажи урусай", "скажи urusai"): ("chuchu", "Урусай ва! Заткнись уже, надоел!"),
    
    # Мэй
    ("скажи кора", "скажи kora"): ("mei", "Кора, яро? Эй ты, сволочь? Ара-ара..."),
    ("скажи чикусё", "скажи chikusho"): ("mei", "Чикусё! Сука! Сейчас догоню!"),
    ("скажи дамарэ", "скажи damare"): ("mei", "Дамарэ! Заткнись быстро! А то хуже будет!"),
    
    # Хана
    ("скажи кусо", "скажи kuso"): ("hana", "Кусо! Дерьмо! Дошик кончился..."),
    ("скажи удзай", "скажи uzai"): ("hana", "Удзай! Задолбал! Дай денег лучше!"),
    ("скажи синдзимаэ", "скажи shinjimae"): ("hana", "Синдзимаэ! Убирайся к чёрту! Не мешай!"),
    
    # Ки
    ("скажи бака ки", "скажи baka ki"): ("ki", "Бака... (краснеет, отворачивается) Не называйте меня так..."),
    ("скажи чикусё ки", "скажи chikusho ki"): ("ki", "Чикусё... (тихо, всхлипывая) Я не плачу..."),
    ("скажи докэ", "скажи doke"): ("ki", "Докэ... отойди, пожалуйста... мне неловко..."),
    
    # Симона
    ("скажи бусу", "скажи busu"): ("simone", "Бусу. Уродина. (холодно) Не обижайся, это правда."),
    ("скажи онорэ", "скажи onore"): ("simone", "Онорэ. Мразь. (ледяным тоном) Убирайся с глаз моих."),
}


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 3. ОСНОВНОЙ КЛАСС CHUMEI (вся логика бота)
# ══════════════════════════════════════════════════════════════════════════════════════════════

class ChuMei:
    """
    Главный класс приложения ChuMei Angels.
    
    ОТВЕЧАЕТ ЗА:
    - Инициализацию всех систем (голос, видео, память, чат)
    - Обработку голосовых команд и триггеров
    - Рассказывание историй (карусель без обрывов)
    - Случайные диалоги в idle-режиме
    - Управление потребностями девочек
    """
    
    # ══════════════════════════════════════════════════════════════════════════════════════════
    # 3.1 КОНСТРУКТОР (инициализация всех переменных и систем)
    # ══════════════════════════════════════════════════════════════════════════════════════════
    
    def __init__(self):
        """Инициализация всех систем при запуске бота"""
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
        self.punctuator = RuPunctuator() if HAS_PUNCTUATOR else None  # Расстановка знаков
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
        
        # ----- ПОТРЕБНОСТИ ДЕВОЧЕК (позже расширим на всех) -----
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
    
    # ══════════════════════════════════════════════════════════════════════════════════════════
    # 3.2 ПРИВАТНЫЕ МЕТОДЫ (загрузка данных, инициализация подсистем)
    # ══════════════════════════════════════════════════════════════════════════════════════════
    
    def _load_user_name(self):
        """Загружает имя пользователя из файла (если есть)"""
        if os.path.exists(self.name_file):
            with open(self.name_file, 'r', encoding='utf-8') as f:
                self.user_name = f.read().strip()
                if self.user_name:
                    self.name_asked = True
                    print(f"📛 Загружено имя: {self.user_name}")
    
    def _load_voice_sample(self):
        """Загружает образец голоса для идентификации (если есть)"""
        if os.path.exists(self.voice_file):
            self.voice_embedding = np.load(self.voice_file)
            self.voice_enrolled = True
            print("🔊 Образец голоса загружен")
    
    def _init_search_sites(self):
        """Инициализация поисковых сайтов для команды 'открой ютуб'"""
        self.search_sites = {
            "ютуб": ["https://youtube.com", "https://www.youtube.com/results?search_query={query}"],
            "гугл": ["https://google.com", "https://www.google.com/search?q={query}"],
            "яндекс": ["https://ya.ru", "https://yandex.ru/search/?text={query}"],
            "википедия": ["https://wikipedia.org", "https://ru.wikipedia.org/wiki/{query}"],
        }
        self.search_triggers = ["открой", "запусти", "покажи", "найди", "поищи"]
        self.auto_sites = {"видео": "ютуб", "музыку": "ютуб", "погоду": "гугл"}
    
    def _init_app_commands(self):
        """Инициализация команд для запуска приложений Windows"""
        self.app_commands = {
            "блокнот": "notepad.exe",
            "калькулятор": "calc.exe",
            "проводник": "explorer.exe",
        }
    
    def _init_volume_commands(self):
        """Инициализация команд для управления громкостью"""
        self.volume_commands = {
            "up": ["погромче", "громче", "громкость вверх"],
            "down": ["потише", "тише", "громкость вниз"],
            "mute": ["молча", "замолчи", "тишина"],
            "max": ["звук 100", "громкость 100", "максимум"],
        }
    
    def _reset_timers(self):
        """Сбрасывает таймеры после обработки команды"""
        self.last_response_time = time.time()
        self.last_user_message_time = time.time()
        self.is_processing = False
    
    # ══════════════════════════════════════════════════════════════════════════════════════════
    # 3.3 МЕТОДЫ ДЛЯ РАБОТЫ С ГОЛОСОМ
    # ══════════════════════════════════════════════════════════════════════════════════════════
    
    async def _speak(self, text, voice=None, duet=False):
        # ОТЛАДКА: выводим исходный текст
        print(f"🐛 ИСХОДНЫЙ ТЕКСТ: {text}")
        
        # Нормализуем текст (цифры, английские буквы)
        text = normalize_text_for_tts(text)
        
        # ОТЛАДКА: выводим после нормализации
        print(f"🐛 ПОСЛЕ НОРМАЛИЗАЦИИ: {text}")
        
        # Расставляем ударения с помощью RUAccent
        try:
            text = accent_helper.process_for_tts(text)
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"⚠️ Ошибка расстановки ударений: {e}")
        
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
        """Проигрывает сцену из нескольких реплик (для случайных диалогов)"""
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
        """Запускает случайный диалог, когда пользователь молчит (idle)"""
        if self.story_playing:
            return  # Не болтаем во время истории
        
        if self.censorship_mode:
            scene = random.choice(DUET_IDLE_SAFE)
        else:
            scene = random.choice(DUET_IDLE_SAFE + DUET_IDLE_NSFW)
        await self._play_scene(scene)
    
    # ══════════════════════════════════════════════════════════════════════════════════════════
    # 3.4 МЕТОДЫ ДЛЯ РАБОТЫ С ИИ И ОТВЕТАМИ
    # ══════════════════════════════════════════════════════════════════════════════════════════
    
    def _parse_target(self, text):
        """
        Определяет, к кому обращаются.
        Возвращает: target (chuchu/mei/hana/ki/simone/both) и очищенный текст
        """
        target = "chuchu"  # по умолчанию Чучу
        clean_text = text.strip()
        text_lower = text.lower()
        
        # Словарь обращений для каждой девочки
        targets = {
            "chuchu": ["чучу", "чу", "chuchu", "чу-чу"],
            "mei": ["мэй", "мей", "mei", "may", "мея"],
            "hana": ["хана", "hana", "ханна", "хана банни"],
            "ki": ["ки", "ki", "potato", "потато", "potato godzilla"],
            "simone": ["симона", "simone", "симонa", "simona", "миссис симонс"],
            "both": ["девочки", "девчата", "сестрёнки", "девушки", "все девочки"]
        }
        
        # Проверяем начало фразы (обращение + пробел или точное совпадение)
        for target_type, names in targets.items():
            for name in names:
                if text_lower.startswith(name + " ") or text_lower == name:
                    target = target_type
                    # Убираем обращение из текста
                    clean_text = re.sub(r'^' + re.escape(name) + r'\s*', '', text, flags=re.IGNORECASE).strip()
                    print(f"🎯 Распознано обращение: {target_type} ({name})")  # для отладки
                    return target, clean_text
        
        # Если обращения нет — возвращаем исходный текст и Чучу по умолчанию
        return target, clean_text
    
    async def _play_response(self, response, target):
        """Воспроизводит ответ от ИИ с определением голоса по тегу или контексту"""
        await self.avatar.start_talking()
        
        # Пробуем найти теги [имя]...[/имя] или [имя]...
        # Поддерживаем: чучу, чу, мэй, мей, mei, хана, hana, ки, ki, симона, simone
        parts = re.findall(r'\[(чучу|чу|мэй|мей|mei|хана|hana|ки|ki|симона|simone)\](.*?)(?:\[/|$)', response, re.IGNORECASE | re.DOTALL)
        
        if parts:
            for speaker, line in parts:
                line = line.strip()
                if line:
                    clean_line = transliterate(clean_text(line))
                    speaker_lower = speaker.lower()
                    
                    if speaker_lower in ["мэй", "мей", "mei"]:
                        await self.silero.speak(clean_line, voice="mei")
                    elif speaker_lower in ["хана", "hana"]:
                        await self.silero.speak(clean_line, voice="hana")
                    elif speaker_lower in ["ки", "ki"]:
                        await self.silero.speak(clean_line, voice="ki")
                    elif speaker_lower in ["симона", "simone"]:
                        await self.silero.speak(clean_line, voice="simone")
                    else:
                        await self.silero.speak(clean_line, voice="chuchu")
                    await asyncio.sleep(0.2)
        else:
            # Если тегов нет — используем target и удаляем возможное имя из начала
            clean_response = transliterate(clean_text(response))
            
            # Убираем возможное "Чучу:" или "Мэй:" из начала
            clean_response = re.sub(r'^(Чучу|Мэй|Хана|Ки|Симона):\s*', '', clean_response, flags=re.IGNORECASE)
            
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
        """
        Обычный диалог через ИИ (llama3.1:8b).
        Вызывается, когда не сработал ни один триггер.
        """
        # Если рассказывается история — игнорируем обычный диалог
        if self.story_playing:
            print("⏸️ История рассказывается, обычный диалог отложен.")
            return
        
        self.last_user_message_time = time.time()
        target, clean_text = self._parse_target(text)
        if not clean_text:
            return
        
        # Команды выхода
        if any(word in clean_text.lower() for word in ["пока", "выход", "стоп", "завершить"]):
            await self._speak(f"До свидания, {self.user_name or 'Вадим'}! Мы будем ждать тебя!")
            self.running = False
            return
        
        print("\n🧠 Генерация ответа...")
        prompt = config.CHARACTER_PERSONALITY if not self.censorship_mode else config.CENSORED_PERSONALITY
        if self.user_name:
            prompt = f"Ты общаешься с пользователем по имени {self.user_name}. " + prompt
        
        # Разрешаем всех 5 девочек для ИИ
        allowed_girls = ["chuchu", "mei", "hana", "ki", "simone", "both"]
        girl_for_ai = target if target in allowed_girls else "chuchu"
        response = get_ai_response(user_message=clean_text, system_prompt=prompt, girl_name=girl_for_ai)
        if response:
            await self._play_response(response, target)
        
        self.last_response_time = time.time()
    
    
    async def _handle_japanese_phrase(self, text_lower):
        """Обрабатывает команды типа 'скажи бака'"""
        
        # Чучу
        if "скажи бака" in text_lower or "скажи baka" in text_lower:
            await self._speak("Бака! Ты дурак, да? Хи-хи-хи!", voice="chuchu")
            return True
        
        if "скажи шиматта" in text_lower or "скажи shimatta" in text_lower:
            await self._speak("Шиматта! Вот чёрт! Трусики жалко!", voice="chuchu")
            return True
        
        if "скажи урусай" in text_lower or "скажи urusai" in text_lower:
            await self._speak("Урусай ва! Заткнись уже, надоел!", voice="chuchu")
            return True
        
        # Мэй
        if "скажи кора" in text_lower or "скажи kora" in text_lower:
            await self._speak("Кора, яро? Эй ты, сволочь? Ара-ара...", voice="mei")
            return True
        
        if "скажи чикусё" in text_lower or "скажи chikusho" in text_lower:
            await self._speak("Чикусё! Сука! Сейчас догоню!", voice="mei")
            return True
        
        if "скажи дамарэ" in text_lower or "скажи damare" in text_lower:
            await self._speak("Дамарэ! Заткнись быстро! А то хуже будет!", voice="mei")
            return True
        
        # Хана
        if "скажи кусо" in text_lower or "скажи kuso" in text_lower:
            await self._speak("Кусо! Дерьмо! Дошик кончился...", voice="hana")
            return True
        
        if "скажи удзай" in text_lower or "скажи uzai" in text_lower:
            await self._speak("Удзай! Задолбал! Дай денег лучше!", voice="hana")
            return True
        
        # Ки
        if "скажи докэ" in text_lower or "скажи doke" in text_lower:
            await self._speak("Докэ... отойди, пожалуйста... мне неловко...", voice="ki")
            return True
        
        if "скажи бака ки" in text_lower or "скажи baka ki" in text_lower:
            await self._speak("Бака... (краснеет, отворачивается) Не называйте меня так...", voice="ki")
            return True
        
        # Симона
        if "скажи бусу" in text_lower or "скажи busu" in text_lower:
            await self._speak("Бусу. Уродина. Холодно. Не обижайся, это правда.", voice="simone")
            return True
        
        await self._speak("Не поняла, какую фразу сказать. Попробуй: скажи бака, скажи кора, скажи кусо, скажи докэ")
        return True
    
    async def _handle_change_body(self, text_lower):
        """Обрабатывает команду 'измени тело' (грудь, бёдра, талия)"""
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
    
    # ══════════════════════════════════════════════════════════════════════════════════════════
    # 3.5 ИСТОРИЯ ВЕЧЕРИНКИ (карусель без обрывов)
    # ══════════════════════════════════════════════════════════════════════════════════════════
    
    async def tell_full_story(self):
        """Запускает полную историю вечеринки с начала"""
        from knowledge.story_arc import FULL_STORY_ARC_FINAL
        
        if self.story_playing:
            await self._speak("История уже рассказывается. Дай мне закончить.")
            return
        
        self.story_chain = FULL_STORY_ARC_FINAL
        self.story_total = len(self.story_chain)
        self.story_index = 0
        self.story_playing = True
        
        # Запускаем в отдельной задаче, чтобы не блокировать основной цикл
        asyncio.create_task(self._play_story())
    
    async def _play_story(self):
        """Внутренний метод для проигрывания истории (непрерывно, до конца)"""
        # Блокируем микрофон на время рассказа
        self.is_processing = True
        await self.avatar.start_talking()
        
        while self.story_playing and self.story_index < self.story_total:
            speaker, text = self.story_chain[self.story_index]
            self.story_index += 1
            
            # Определяем голос для каждой реплики
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
            
            await asyncio.sleep(0.3)  # Пауза между репликами
        
        await self.avatar.stop_talking()
        self.story_playing = False
        self.is_processing = False
        await self._speak("Вот и вся история. Надеюсь, тебе понравилось!")
    
    async def continue_story(self):
        """Продолжает прерванную историю с того же места"""
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
        """Останавливает текущую историю"""
        if self.story_playing:
            self.story_playing = False
            self.is_processing = False
            await self._speak("Останавливаю рассказ.")
        else:
            await self._speak("История и не рассказывалась.")
    
    # ══════════════════════════════════════════════════════════════════════════════════════════
    # 3.6 ПОТРЕБНОСТИ (заглушки, будут расширены позже)
    # ══════════════════════════════════════════════════════════════════════════════════════════
    
    async def _update_hunger(self):
        """Обновление уровня голода (заглушка)"""
        pass
    
    async def _update_toilet_needs(self):
        """Обновление потребности в туалете (заглушка)"""
        pass
    
    async def _update_mood(self, who, change, reason=""):
        """Обновление настроения (заглушка)"""
        pass
    
    # ══════════════════════════════════════════════════════════════════════════════════════════
    # 3.7 ОСНОВНОЙ ЦИКЛ МИКРОФОНА (обработка голосовых команд)
    # ══════════════════════════════════════════════════════════════════════════════════════════
    
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
            
            # Обновление потребностей
            await self._update_hunger()
            await self._update_toilet_needs()
            
            # Idle диалоги если долго молчим (НО НЕ ВО ВРЕМЯ ИСТОРИИ)
            if not self.story_playing and time.time() - self.last_user_message_time > self.idle_chat_timeout:
                print("\n💬 Вы молчите, пробуем запустить цепочку...")
                # Пытаемся запустить случайную цепочку
                await self.try_random_chain()
                # Если цепочка не запустилась — обычный диалог
                if not self.is_processing:
                    await self._random_dialogue()
                self.last_user_message_time = time.time()
                continue
            
            text = await asyncio.to_thread(listen)
            print(f"🎤 РАСПОЗНАНО: '{text}'")
            
            if text:
                text_lower = text.lower()
                
                # ========== БЛОК ТРИГГЕРОВ (перехват команд) ==========
                
                # ----- 1. РЕЖИМ ОБУЧЕНИЯ ДЛЯ ЧУЧУ -----
                if "чучу режим обучения" in text_lower or "чу режим обучения" in text_lower:
                    print("✅ ПЕРЕХВАТ: режим обучения для Чучу")
                    self.memory.set_learning_mode("chuchu", True)
                    await self._speak("Режим обучения для Чучу включён. Слушаю и запоминаю!")
                    self._reset_timers()
                    continue
                
                # ----- 2. РЕЖИМ ОБУЧЕНИЯ ДЛЯ МЭЙ -----
                if "мэй режим обучения" in text_lower or "мея режим обучения" in text_lower or "mei режим обучения" in text_lower:
                    print("✅ ПЕРЕХВАТ: режим обучения для Мэй")
                    self.memory.set_learning_mode("mei", True)
                    await self._speak("Режим обучения для Мэй включён. Слушаю и запоминаю!", voice="mei")
                    self._reset_timers()
                    continue
                
                # ----- 3. ЗАПОМНИ ДЛЯ ЧУЧУ -----
                if "запомни" in text_lower and ("чу" in text_lower or "чучу" in text_lower):
                    match = re.search(r'запомни[:\s]+(.+)', text_lower)
                    if match:
                        fact = match.group(1).strip()
                        if fact:
                            print(f"✅ ПЕРЕХВАТ: Чучу запомни '{fact}'")
                            self.memory.save_fact("chuchu", fact)
                            await self._speak("Запомнила!")
                            self._reset_timers()
                            continue
                
                # ----- 4. ЗАПОМНИ ДЛЯ МЭЙ -----
                if "запомни" in text_lower and ("мэй" in text_lower or "мея" in text_lower or "mei" in text_lower):
                    match = re.search(r'запомни[:\s]+(.+)', text_lower)
                    if match:
                        fact = match.group(1).strip()
                        if fact:
                            print(f"✅ ПЕРЕХВАТ: Мэй запомни '{fact}'")
                            self.memory.save_fact("mei", fact)
                            await self._speak("Запомнила!", voice="mei")
                            self._reset_timers()
                            continue
                
                # ----- 5. НАПОМНИ ДЛЯ ЧУЧУ -----
                if "напомни" in text_lower and ("чу" in text_lower or "чучу" in text_lower):
                    print("✅ ПЕРЕХВАТ: Чучу напомни")
                    facts = self.memory.get_facts("chuchu", limit=5)
                    if facts:
                        await self._speak("Вот что я помню: " + ", ".join(facts))
                    else:
                        await self._speak("Я пока ничего не запомнила!")
                    self._reset_timers()
                    continue
                
                # ----- 6. НАПОМНИ ДЛЯ МЭЙ -----
                if "напомни" in text_lower and ("мэй" in text_lower or "мея" in text_lower or "mei" in text_lower):
                    print("✅ ПЕРЕХВАТ: Мэй напомни")
                    facts = self.memory.get_facts("mei", limit=5)
                    if facts:
                        await self._speak("Вот что я помню: " + ", ".join(facts), voice="mei")
                    else:
                        await self._speak("Я пока ничего не запомнила!", voice="mei")
                    self._reset_timers()
                    continue
                
                # ----- 7. СВОБОДНА ДЛЯ ЧУЧУ -----
                if "свободна" in text_lower and ("чу" in text_lower or "чучу" in text_lower):
                    print("✅ ПЕРЕХВАТ: Чучу свободна")
                    self.memory.set_learning_mode("chuchu", False)
                    await self._speak("Ура! Теперь я снова могу спорить! Хи-хи-хи!")
                    self._reset_timers()
                    continue
                
                # ----- 8. СВОБОДНА ДЛЯ МЭЙ -----
                if "свободна" in text_lower and ("мэй" in text_lower or "мея" in text_lower or "mei" in text_lower):
                    print("✅ ПЕРЕХВАТ: Мэй свободна")
                    self.memory.set_learning_mode("mei", False)
                    await self._speak("Ура! Теперь я снова могу спорить! Ара-ара!", voice="mei")
                    self._reset_timers()
                    continue
                
                # ----- 9. ИЗМЕНИ ТЕЛО -----
                if "измени тело" in text_lower or "поменяй тело" in text_lower:
                    print("✅ ПЕРЕХВАТ: изменить тело")
                    await self._handle_change_body(text_lower)
                    self._reset_timers()
                    continue
                
                # ----- 10. РАСКРЕПОСТИСЬ (NSFW) -----
                if any(word in text_lower for word in ["раскрепостись", "раскрепостить", "раскрепостите", "отбой", "гости ушли", "мы одни", "отключи цензуру"]):
                    print("✅ ПЕРЕХВАТ: раскрепоститься")
                    if self.censorship_mode:
                        self.censorship_mode = False
                        await self.avatar.start_talking()
                        await self.silero.speak("Уф, наконец-то! Я снова стала собой!")
                        await asyncio.sleep(0.2)
                        await self.silero.speak("О да! Теперь можно и без трусиков походить!", voice="mei")
                        await asyncio.sleep(0.1)
                        await self.silero.speak("Мэй! Ну ты сразу о своём!")
                        await self.silero.speak("А что? Ты же тоже об этом думала!", voice="mei")
                        await self.silero.speak_duet("Хи-хи-хи!")
                        await self.avatar.stop_talking()
                    else:
                        await self._speak("Мы уже раскрепощённые, Вадим! Хи-хи-хи!")
                    self._reset_timers()
                    continue
                
                # ----- 11. ЦЕНЗУРА (SFW) -----
                if any(word in text_lower for word in ["цензура", "режим цензуры", "у нас гости", "гости"]):
                    print("✅ ПЕРЕХВАТ: включить цензуру")
                    if not self.censorship_mode:
                        self.censorship_mode = True
                        await self.avatar.start_talking()
                        await self.silero.speak("Поняла, Вадим. Режим цензуры включён. Мы скромные девочки.")
                        await asyncio.sleep(0.2)
                        await self.silero.speak("Да, теперь только скромные разговоры. Никаких трусиков.", voice="mei")
                        await self.silero.speak("Мэй! Ты опять!")
                        await self.silero.speak_duet("Хи-хи-хи!")
                        await self.avatar.stop_talking()
                    else:
                        await self._speak("Цензура уже включена, Вадим!")
                    self._reset_timers()
                    continue
                
                # ----- 12. ПЕРЕЗАГРУЗКА КОМПЬЮТЕРА -----
                if any(word in text_lower for word in ["перезагрузи компьютер", "перезагрузка", "ребут компьютер"]):
                    print("✅ ПЕРЕХВАТ: перезагрузка компьютера")
                    await self.silero.speak("Перезагружаю компьютер. Сейчас вернусь!")
                    await asyncio.sleep(0.2)
                    await self.silero.speak("Сохрани всё, что не сохранено!", voice="mei")
                    os.system("shutdown /r /t 30")
                    self._reset_timers()
                    continue
                
                # ----- 13. ВЫКЛЮЧЕНИЕ КОМПЬЮТЕРА -----
                if any(word in text_lower for word in ["выключи компьютер", "выключение", "шатдаун"]):
                    print("✅ ПЕРЕХВАТ: выключение компьютера")
                    await self.silero.speak("Выключаю компьютер. Сладких снов, Вадим!")
                    await asyncio.sleep(0.2)
                    await self.silero.speak("Пусть тебе приснится что-нибудь... горячее!", voice="mei")
                    os.system("shutdown /s /t 30")
                    self._reset_timers()
                    continue
                
                # ----- 14. ОТМЕНА -----
                if any(word in text_lower for word in ["отмена", "отмени", "не надо"]):
                    if "компьютер" in text_lower or "перезагрузк" in text_lower:
                        print("✅ ПЕРЕХВАТ: отмена перезагрузки")
                        os.system("shutdown /a")
                        await self.silero.speak("Отменила. Работаем дальше!")
                        await asyncio.sleep(0.2)
                        await self.silero.speak("Фух, а я уже испугалась!", voice="mei")
                        self._reset_timers()
                        continue
                
                # ----- 15. ПЕРЕЗАПУСК ПРИЛОЖЕНИЯ -----
                if any(word in text_lower for word in ["перезапустись", "перезагрузись", "рестарт", "ребутнись", "перезагрузи приложение"]):
                    print("✅ ПЕРЕХВАТ: перезапуск")
                    await self.avatar.start_talking()
                    await self.silero.speak("Перезагружаюсь! Сейчас вернусь!")
                    await asyncio.sleep(0.3)
                    await self.silero.speak("И я тоже! Не скучай без нас!", voice="mei")
                    await self.avatar.stop_talking()
                    await asyncio.sleep(0.5)
                    os.execv(sys.executable, ['python'] + sys.argv)
                    return
                
                # ----- 16. РАССКАЖИ ИСТОРИЮ -----
                if any(word in text_lower for word in ["расскажи историю", "про вечеринку", "историю про вечеринку"]):
                    print("✅ ПЕРЕХВАТ: расскажи историю")
                    await self.tell_full_story()
                    self._reset_timers()
                    continue
                
                # ----- 17. ПРОДОЛЖИ ИСТОРИЮ -----
                if not self.story_playing and any(word in text_lower for word in ["продолжи", "дальше", "ещё"]):
                    print("✅ ПЕРЕХВАТ: продолжить историю")
                    await self.continue_story()
                    self._reset_timers()
                    continue
                
                # ----- 18. СТОП ИСТОРИЯ -----
                if any(word in text_lower for word in ["стоп история", "хватит", "замолчи", "прекрати"]):
                    print("✅ ПЕРЕХВАТ: остановить историю")
                    await self.stop_story()
                    self._reset_timers()
                    continue
                
                
                # ----- 19. ЯПОНСКИЕ ФРАЗЫ (скажи бака, скажи кора и т.д.) -----
                if any(word in text_lower for word in ["скажи бака", "скажи baka", "скажи кора", "скажи kora", "скажи кусо", "скажи kuso", "скажи чикусё", "скажи chikusho", "скажи удзай", "скажи uzai", "скажи докэ", "скажи doke"]):
                    print("✅ ПЕРЕХВАТ: японская фраза")
                    await self._handle_japanese_phrase(text_lower)
                    self._reset_timers()
                    continue
                
                
                # ========== ОБЫЧНЫЙ ДИАЛОГ ==========
                await self._process_normal(text)
            
            await asyncio.sleep(0.1)
    
    # ══════════════════════════════════════════════════════════════════════════════════════════
    # 3.8 ПУСК И ОСТАНОВКА
    # ══════════════════════════════════════════════════════════════════════════════════════════
    
    async def start(self):
        """Запуск бота: инициализация, тест голосов, старт микрофона"""
        print("\n🚀 Запуск приложения...")
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.music.set_volume(0.7)
        
        # Тест голосов Ханы и Ки
        print("🔊 Тест голосов Ханы и Ки...")
        await self.silero.speak("Привет дорогой, меня зовут Ха на, я люблю дошик и деньги!", voice="hana")
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
        
        await self.microphone_loop()
        await self.cleanup()
    
    async def _perform_intro_duet(self):
        """Приветственное сообщение при запуске"""
        await self.silero.speak_duet("Привет, Вадим! Это Чучу и Мэй, твои виртуальные помощницы! Хи-хи-хи!")
    
    async def cleanup(self):
        """Очистка ресурсов при завершении"""
        print("\n🧹 Очистка ресурсов...")
        self.running = False
        if self.avatar:
            await self.avatar.stop()
        if self.link_chat:
            self.link_chat.stop()
        print("✅ Завершено")

    # ══════════════════════════════════════════════════════════════════════════════════════════
    # 3.9 СЛУЧАЙНЫЕ ЦЕПОЧКИ
    # ══════════════════════════════════════════════════════════════════════════════════════════
    
    async def try_random_chain(self):
        """Пытается запустить случайную цепочку (если условия подходят)"""
        from knowledge.chains import DAY_CHAINS, NIGHT_CHAINS, RARE_CHAINS, CRIME_CHAIN
        
        # Не запускаем, если уже что-то идёт
        if self.story_playing or self.is_processing:
            return
        
        current_hour = datetime.now().hour
        is_night = current_hour < 6 or current_hour > 21
        is_day = not is_night
        
        # Выбираем тип цепочки
        chain = None
        
        # Криминальная цепочка (5% шанс, только ночью)
        if is_night and random.random() < 0.05:
            chain = CRIME_CHAIN
            print(f"🌙 Запущена криминальная цепочка: {chain['name']}")
        
        # Редкая цепочка (10% шанс)
        elif random.random() < 0.1:
            chain = random.choice(RARE_CHAINS)
            print(f"✨ Запущена редкая цепочка: {chain['name']}")
        
        # Ночная цепочка (30% шанс)
        elif is_night and random.random() < 0.3:
            chain = random.choice(NIGHT_CHAINS)
            print(f"🌙 Запущена ночная цепочка: {chain['name']}")
        
        # Дневная цепочка (40% шанс)
        elif is_day and random.random() < 0.4:
            chain = random.choice(DAY_CHAINS)
            print(f"☀️ Запущена дневная цепочка: {chain['name']}")
        
        if chain:
            await self._play_chain(chain)
    
    async def _play_chain(self, chain):
        """Проигрывает цепочку шаг за шагом (50% шанс на каждый следующий шаг)"""
        self.is_processing = True
        steps = chain["steps"]
        step_index = 0
        
        while step_index < len(steps) and self.running:
            speaker, text = steps[step_index]
            # Дополнительный параметр для "operator" (голос диктора)
            if speaker == "operator":
                await self.silero.speak(text, voice="mei")  # временно голосом Мэй
            else:
                # Определяем голос
                if speaker in ["chuchu", "mei", "hana", "ki", "simone"]:
                    await self.silero.speak(text, voice=speaker)
                elif speaker == "both":
                    await self.silero.speak_duet(text)
                else:
                    await self.silero.speak(text, voice="chuchu")
            
            step_index += 1
            
            # 50% шанс продолжить, если не конец цепочки
            if step_index < len(steps) and random.random() < 0.5:
                await asyncio.sleep(0.5)  # пауза перед следующим шагом
            else:
                break  # цепочка прервалась
        
        self.is_processing = False
        print("✅ Цепочка завершена")


# ══════════════════════════════════════════════════════════════════════════════════════════════
# 4. ТОЧКА ВХОДА
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