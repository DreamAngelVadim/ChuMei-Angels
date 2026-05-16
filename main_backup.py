"""
Main application - ChuMei: дуэт Чучу и Мэй
"""
import asyncio
import time
import os
import re
import random
import webbrowser
import urllib.parse
import sys
import subprocess
import ctypes
from datetime import datetime
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
import numpy as np

from knowledge.cosplay import NAGOMITEI_CHU_KNOWLEDGE, FAVORITE_MODELS, COSPLAY_TERMS, MEI_KNOWLEDGE, NAGOMITEI_CHU_LINKS
from knowledge.music import EPICA_KNOWLEDGE, SIMONE_SIMONS_KNOWLEDGE, SIMONE_VS_FLOOR, WITHIN_TEMPTATION_KNOWLEDGE, MEI_MUSIC_KNOWLEDGE
from knowledge.dialogues import (
    DUET_IDLE_SAFE, DUET_IDLE_NSFW, DUET_JOKES_SAFE, DUET_JOKES_NSFW,
    BODY_ARGUE_SAFE, BODY_ARGUE_NSFW, DANCE_MATUSHKA,
    GYM_SAFE, GYM_NSFW, VELMA_DAPHNE_NSFW,
    SECRET_ORANGE_SAFE, PHONE_ORDER_SAFE, SISTERS_LOVERS_DIALOGUE,
    HUNGER_SCENE_CHUCHU, HUNGER_SCENE_MEI,
    TOILET_OCCUPIED_SAFE, TOILET_OCCUPIED_NSFW,
    PRAYER_AFTER_TOILET_CHUCHU, PRAYER_AFTER_TOILET_MEI
)
from knowledge.personality import (
    FAITH_CHUCHU, FAITH_MEI, RELATIONSHIP_CORE, SPEECH_RULES,
    SUBSTANCE_BAN, SWEAR_RULES, MOOD_SYSTEM, JAPANESE_WORDS, DUO_NAMES
)

try:
    from punctuator import RuPunctuator
    HAS_PUNCTUATOR = True
except ImportError:
    HAS_PUNCTUATOR = False


def clean_text(text):
    """Очистка текста."""
    text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1 \2', text)
    for num, word in sorted(NUM_WORDS.items(), key=lambda x: -len(x[0])):
        text = re.sub(r'\b' + num + r'\b', word, text)
    tens = {'20': 'двадцать', '30': 'тридцать', '40': 'сорок', '50': 'пятьдесят',
            '60': 'шестьдесят', '70': 'семьдесят', '80': 'восемьдесят', '90': 'девяносто'}
    ones = {'1': 'один', '2': 'два', '3': 'три', '4': 'четыре', '5': 'пять',
            '6': 'шесть', '7': 'семь', '8': 'восемь', '9': 'девять'}
    for ten_num, ten_word in tens.items():
        for one_num, one_word in ones.items():
            compound = str(int(ten_num) + int(one_num))
            text = re.sub(r'\b' + compound + r'\b', ten_word + ' ' + one_word, text)
    for wrong, correct in GENDER_FIXES.items():
        text = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, text, flags=re.IGNORECASE)
    for eng, rus in REPLACEMENTS.items():
        clean_rus = rus.replace('+', '')
        text = re.sub(r'\b' + re.escape(eng) + r'\b', clean_rus, text)
    emoji_pattern = re.compile("["
        "\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub('', text)
    allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
    allowed.update('абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')
    allowed.update(' .,!?;:()/+"\'')
    result = []
    for char in text:
        if char in allowed:
            result.append(char)
        else:
            result.append(' ')
    text = ''.join(result)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class ChuMei:
    def __init__(self):
        print("=" * 60)
        print(f"ChuMei — дуэт Чучу и Мэй")
        print("=" * 60)
        self.avatar = AvatarVideo()
        self.link_chat = LinkChat()
        self.silero = SileroTTS()
        self.punctuator = RuPunctuator() if HAS_PUNCTUATOR else None
        self.censorship_mode = True
        self.sleep_mode = False
        self.last_response_time = 0
        self.is_processing = False
        self.running = True
        self.last_user_message_time = time.time()
        self.idle_chat_timeout = 30
        self.user_name = None
        self.name_asked = False
        self.name_file = "user_name.txt"
        if os.path.exists(self.name_file):
            with open(self.name_file, 'r', encoding='utf-8') as f:
                self.user_name = f.read().strip()
                if self.user_name:
                    self.name_asked = True
                    print(f"Загружено имя: {self.user_name}")
        self.mei_can_call_master = False
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
        self.mood_chuchu = 70
        self.mood_mei = 70
        self.affection = 80
        self.last_argue_time = 0
        self.last_toilet_time = 0
        self.argue_cooldown = 300
        self.search_sites = {
            "ютуб": ["https://youtube.com", "https://www.youtube.com/results?search_query={query}"],
            "youtube": ["https://youtube.com", "https://www.youtube.com/results?search_query={query}"],
            "гугл": ["https://google.com", "https://www.google.com/search?q={query}"],
            "google": ["https://google.com", "https://www.google.com/search?q={query}"],
            "яндекс": ["https://ya.ru", "https://yandex.ru/search/?text={query}"],
            "википедия": ["https://wikipedia.org", "https://ru.wikipedia.org/wiki/{query}"],
            "вики": ["https://wikipedia.org", "https://ru.wikipedia.org/wiki/{query}"],
            "дискорд": ["https://discord.com", None],
            "discord": ["https://discord.com", None],
            "телеграм": ["https://web.telegram.org", None],
            "гитхаб": ["https://github.com", "https://github.com/search?q={query}"],
            "github": ["https://github.com", "https://github.com/search?q={query}"],
            "твич": ["https://twitch.tv", "https://www.twitch.tv/search?term={query}"],
            "twitch": ["https://twitch.tv", "https://www.twitch.tv/search?term={query}"],
        }
        self.search_triggers = [
            "открой", "запусти", "покажи", "перейди", "найди", "поищи",
            "загугли", "погугли", "посмотри", "посмотрим", "включи",
            "найди на", "поищи в", "поищи на", "открой на", "покажи на",
            "отправь ссылку", "дай ссылку", "скинь ссылку",
        ]
        self.auto_sites = {
            "видео": "ютуб", "клип": "ютуб", "ролик": "ютуб",
            "музыку": "ютуб", "песню": "ютуб", "трек": "ютуб",
            "погоду": "гугл", "погода": "гугл", "рецепт": "гугл", "новости": "гугл",
            "ссылку на": "гугл", "ссылку про": "гугл",
        }
        self.app_commands = {
            "блокнот": "notepad.exe", "калькулятор": "calc.exe", "проводник": "explorer.exe",
        }
        self.volume_commands = {
            "up": ["погромче", "громче", "громкость вверх", "сделай громче", "прибавь громкость"],
            "down": ["потише", "тише", "громкость вниз", "сделай тише", "убавь громкость"],
            "mute": ["молча", "замолчи", "тишина", "выключи звук", "заткнись", "хватит"],
            "max": ["звук 100", "громкость 100", "максимум", "полная громкость", "на полную"],
        }
    
        # Голосовая идентификация
        self.voice_enrolled = False
        self.voice_embedding = None
        self.voice_file = "voice_sample.npy"
        if os.path.exists(self.voice_file):
            self.voice_embedding = np.load(self.voice_file)
            self.voice_enrolled = True
            print("Образец голоса загружен")
    
    # === ОСНОВНОЙ ЦИКЛ ===
    async def process_voice(self, text: str, target: str = "chuchu"):
        if not text:
            return
        if self.user_name is None:
            name_patterns = [
                (["меня зовут "], None), (["моё имя "], None), (["мое имя "], None),
                (["зови меня "], None), (["называй меня "], None),
                (["я "], ["а ты", "а как", "а тебя"]),
            ]
            for keywords, exclude_words in name_patterns:
                for keyword in keywords:
                    if keyword in text.lower():
                        parts = text.lower().split(keyword)
                        if len(parts) > 1:
                            rest = parts[1].strip()
                            if exclude_words:
                                for ex in exclude_words:
                                    if ex in rest:
                                        rest = ""
                                        break
                            if rest:
                                possible_name = rest.split()[0] if rest else None
                                if possible_name:
                                    possible_name = re.sub(r'[^a-zA-Zа-яА-ЯёЁ]', '', possible_name)
                                if possible_name and len(possible_name) > 1 and len(possible_name) < 20:
                                    self.user_name = possible_name.capitalize()
                                    with open(self.name_file, 'w', encoding='utf-8') as f:
                                        f.write(self.user_name)
                                    print(f"Запомнила имя: {self.user_name}")
                                    await self.avatar.start_talking()
                                    await self.silero.speak(f"Приятно познакомиться, {self.user_name}!")
                                    await self.avatar.stop_talking()
                                    self.last_response_time = time.time()
                                    self.last_user_message_time = time.time()
                                    self.is_processing = False
                                    return
        current_time = time.time()
        if current_time - self.last_response_time < config.MESSAGE_COOLDOWN:
            print("Жду паузу...")
            return
        if self.is_processing:
            print("Уже отвечаю, подождите...")
            return
        self.is_processing = True
        try:
            text_lower = text.lower()

            # === ПЕРЕКЛЮЧЕНИЕ ЦЕНЗУРЫ ===
            if any(word in text_lower for word in ["чучу цензура", "цензура", "сброс", "сбрось", "у нас гости", "гости", "мы не одни", "пришли гости", "включи цензуру", "режим цензуры"]):
                if not self.censorship_mode:
                    self.censorship_mode = True
                    await self.avatar.start_talking()
                    await self.silero.speak("Поняла, Вадим. Режим цензуры включён. Мы скромные девочки.")
                    await asyncio.sleep(0.2)
                    await self.silero.speak("Да, теперь только скромные разговоры. Никаких трусиков.", voice="mei")
                    await self.silero.speak("Мэй! Ты опять!")
                    await self.silero.speak_duet("Хи-хи-хи!")
                    await self.avatar.stop_talking()
                    await self._update_mood("both", -5, "Включили цензуру")
                self.is_processing = False
                return
            if any(word in text_lower for word in ["чучу отбой", "чучу раскрепостись", "чучу вернись", "отбой", "вернись", "раскрепостись", "раскрепостить", "гости ушли", "мы одни", "чучу стань собой", "отключи цензуру", "режим раскрепощения"]):
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
                    await self._update_mood("both", 15, "Раскрепостились!")
                self.is_processing = False
                return

            # === ГОСТЕВОЙ РЕЖИМ ===
            if "мы не одни" in text_lower and not self.censorship_mode:
                self.censorship_mode = True
                await self.silero.speak("Поняла, Вадим. Я скромная.")
                self.is_processing = False
                return

            # === ГРОМКОСТЬ ===
            is_volume_up = any(word in text_lower for word in self.volume_commands["up"])
            is_volume_down = any(word in text_lower for word in self.volume_commands["down"])
            is_volume_mute = any(word in text_lower for word in self.volume_commands["mute"])
            is_volume_max = any(word in text_lower for word in self.volume_commands["max"])
            if is_volume_up or is_volume_down or is_volume_mute or is_volume_max:
                await self._handle_volume(is_volume_up, is_volume_down, is_volume_mute, is_volume_max, text_lower)
                self.is_processing = False
                return

            # === ПРИЛОЖЕНИЯ ===
            if any(word in text_lower for word in ["открой", "запусти", "включи"]):
                for app_name, app_path in self.app_commands.items():
                    if app_name in text_lower:
                        try:
                            subprocess.Popen(app_path, shell=True)
                            await self.silero.speak(f"Открываю {app_name}.")
                        except:
                            await self.silero.speak(f"Не могу открыть {app_name}.")
                        self.is_processing = False
                        return

            # === УПРАВЛЕНИЕ СИСТЕМОЙ ===
            
            # === РЕЖИМ СНА ===
            import pygame
            # Уложить спать
            if any(word in text_lower for word in ["спокойной ночи", "спать", "спатки", "баю-бай", "спите", "отдыхайте", "режим сна"]):
                await self.avatar.start_talking()
                await self.silero.speak("Спокойной ночи, Вадим... Я уже сворачиваюсь калачиком...")
                await asyncio.sleep(0.2)
                await self.silero.speak("И я тоже... Обними меня, сестрёнка...", voice="mei")
                await asyncio.sleep(0.3)
                await self.silero.speak_duet("Сладких снов... Zzz...")
                await self.avatar.stop_talking()
                # Включаем режим сна
                self.sleep_mode = True
                self.idle_chat_timeout = 999999  # Не болтают, пока спят
                pygame.mixer.music.set_volume(0.3)  # Тихий режим
                self.is_processing = False
                return
            
            # Разбудить
            if any(word in text_lower for word in ["просыпайтесь", "подъём", "вставайте", "доброе утро", "проснулись"]):
                if self.sleep_mode:
                    self.sleep_mode = False
                    self.idle_chat_timeout = 30
                    pygame.mixer.music.set_volume(0.7)
                    await self.avatar.start_talking()
                    await self.silero.speak("Ммм... доброе утро, Вадим! Я так сладко спала!")
                    await asyncio.sleep(0.2)
                    await self.silero.speak("А мне снилось, что мы косплеили Велму и Дафну...", voice="mei")
                    await asyncio.sleep(0.1)
                    await self.silero.speak("Мэй! Это был мой сон!")
                    await self.silero.speak_duet("Хи-хи-хи!")
                    await self.avatar.stop_talking()
                else:
                    await self.silero.speak("А мы и не спали! Мы просто ждали тебя!")
                self.is_processing = False
                return
            
            # Перезагрузка ПРИЛОЖЕНИЯ (проверяем ПЕРВЫМ)
            if any(word in text_lower for word in ["перезагрузись", "перезапустись", "перезагрузи приложение", "перезапусти приложение", "рестарт", "ребутнись"]):
                await self.avatar.start_talking()
                await self.silero.speak("Перезагружаюсь! Сейчас вернусь!")
                await asyncio.sleep(0.3)
                await self.silero.speak("И я тоже! Не скучай без нас!", voice="mei")
                await self.avatar.stop_talking()
                await asyncio.sleep(0.5)
                os.execv(sys.executable, ['python'] + sys.argv)
                self.is_processing = False
                return

            # Перезагрузка КОМПЬЮТЕРА
            if any(word in text_lower for word in ["перезагрузи компьютер", "перезагрузка", "ребут"]):
                await self.silero.speak("Перезагружаю компьютер. Сейчас вернусь!")
                await asyncio.sleep(0.2)
                await self.silero.speak("Сохрани всё, что не сохранено!", voice="mei")
                os.system("shutdown /r /t 10")
                self.is_processing = False
                return
                
            # Выключение компьютера
            if any(word in text_lower for word in ["выключи компьютер", "выключение", "шатдаун"]):
                await self.silero.speak("Выключаю компьютер. Сладких снов, Вадим!")
                await asyncio.sleep(0.2)
                await self.silero.speak("Пусть тебе приснится что-нибудь... горячее!", voice="mei")
                os.system("shutdown /s /t 10")
                self.is_processing = False
                return
                
            # Отмена
            if any(word in text_lower for word in ["отмена", "отмени", "не надо"]):
                os.system("shutdown /a")
                await self.silero.speak("Отменила. Работаем дальше!")
                await asyncio.sleep(0.2)
                await self.silero.speak("Фух, а я уже испугалась!", voice="mei")
                self.is_processing = False
                return
            
            # === ПОИСК ===
            has_trigger = any(word in text_lower for word in self.search_triggers)
            has_site = any(site_key in text_lower for site_key in self.search_sites)
            if not has_trigger and has_site:
                has_trigger = True
            auto_site = None
            for keyword, site in self.auto_sites.items():
                if keyword in text_lower:
                    auto_site = site
                    break
            if has_trigger or auto_site:
                link_only = any(word in text_lower for word in ["отправь ссылку", "дай ссылку", "скинь ссылку"])
                if auto_site and not any(site_key in text_lower for site_key in self.search_sites):
                    text = text + " " + auto_site
                opened = False
                for key, urls in self.search_sites.items():
                    if key in text_lower:
                        main_url, search_url = urls
                        query = None
                        q = text_lower
                        q = re.sub(r'\b' + re.escape(key) + r'\b', '', q, flags=re.IGNORECASE)
                        for cmd in self.search_triggers:
                            q = re.sub(r'\b' + re.escape(cmd) + r'\b', '', q, flags=re.IGNORECASE)
                        for filler in ["мне", "пожалуйста", "в", "на", "ссылку", "отправь", "скинь", "дай"]:
                            q = re.sub(r'\b' + filler + r'\b', '', q, flags=re.IGNORECASE)
                        q = q.strip()
                        if q:
                            query = q
                        if query and search_url:
                            final_url = search_url.replace("{query}", urllib.parse.quote(query))
                            if not link_only:
                                webbrowser.open(final_url)
                            self.link_chat.add_link(f"Поиск: {query}", final_url)
                            await self.avatar.start_talking()
                            await self.silero.speak(f"Ищу {query} на {key}.")
                            await self.avatar.stop_talking()
                        else:
                            if not link_only:
                                webbrowser.open(main_url)
                            self.link_chat.add_link(f"Открыт сайт: {key}", main_url)
                            await self.avatar.start_talking()
                            await self.silero.speak(f"Открываю {key}.")
                            await self.avatar.stop_talking()
                        opened = True
                        break
                if not opened:
                    await self.avatar.start_talking()
                    await self.silero.speak("Не знаю такой сайт.")
                    await self.avatar.stop_talking()
                self.last_response_time = time.time()
                self.last_user_message_time = time.time()
                self.is_processing = False
                return

            # === ТРИГГЕРЫ НА СЦЕНКИ ===
            
            # === ГОЛОСОВАЯ ИДЕНТИФИКАЦИЯ ===
            
            # Запись образца голоса
            if any(word in text_lower for word in ["запомни мой голос", "запиши мой голос", "выучи мой голос"]):
                await self.silero.speak("Сейчас я запишу твой голос. Скажи что-нибудь в течение 5 секунд.")
                await asyncio.sleep(1)
                audio_path = await asyncio.to_thread(record_voice, 5)
                self.voice_embedding = get_voice_embedding(audio_path)
                np.save(self.voice_file, self.voice_embedding)
                self.voice_enrolled = True
                os.unlink(audio_path)
                await self.silero.speak("Я запомнила твой голос, Вадим!")
                self.is_processing = False
                return
            
            # Проверка голоса
            if any(word in text_lower for word in ["кто я", "узнай меня", "чей это голос"]):
                if not self.voice_enrolled:
                    await self.silero.speak("Я пока не знаю твой голос. Скажи «запомни мой голос».")
                else:
                    await self.silero.speak("Скажи что-нибудь, чтобы я проверила твой голос.")
                    await asyncio.sleep(1)
                    audio_path = await asyncio.to_thread(record_voice, 3)
                    is_vadim = compare_voices(audio_path, self.voice_embedding, threshold=0.65)
                    os.unlink(audio_path)
                    if is_vadim:
                        await self.silero.speak("Это ты, Вадим! Я узнала твой голос!")
                    else:
                        await self.silero.speak("Хмм... я не узнаю этот голос. Ты точно Вадим?")
                self.is_processing = False
                return
            
            # Запись образца голоса
            if any(word in text_lower for word in ["запомни мой голос", "запиши мой голос", "это я"]):
                await self.silero.speak("Скажи что-нибудь, чтобы я запомнила твой голос. Например: «Привет, Чучу, это я, Вадим».")
                await asyncio.sleep(0.5)
                audio_data = await asyncio.to_thread(listen)
                if audio_data:
                    # Сохраняем аудио во временный файл
                    import tempfile
                    import soundfile as sf
                    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
                    # Здесь нужно записать аудио в файл (сложная часть)
                    # Пока — заглушка
                    await self.silero.speak("Пока функция в разработке. Нужно доработать запись аудио.")
                self.is_processing = False
                return
            
            # Спор о фигурах
            if any(word in text_lower for word in ["кто красивее", "у кого фигура лучше", "сравним фигуры", "спор о фигуре"]):
                if self.censorship_mode:
                    await self._play_scene(BODY_ARGUE_SAFE)
                else:
                    await self._play_scene(BODY_ARGUE_NSFW)
                self.last_response_time = time.time()
                self.last_user_message_time = time.time()
                self.is_processing = False
                return
            
            # Танцы под Матушку
            if any(word in text_lower for word in ["танцы под матушку", "спойте матушку", "станцуйте матушку", "матушка земля", "спойте мату", "матушка", "матушку"]):
                await self._play_scene(DANCE_MATUSHKA)
                self.last_response_time = time.time()
                self.last_user_message_time = time.time()
                self.is_processing = False
                return
            
            # Тренажёрный зал
            if any(word in text_lower for word in ["тренажёрный зал", "спортзал", "тренировка", "качалка"]):
                if self.censorship_mode:
                    await self._play_scene(GYM_SAFE)
                else:
                    await self._play_scene(GYM_NSFW)
                self.last_response_time = time.time()
                self.last_user_message_time = time.time()
                self.is_processing = False
                return
            
            # Велма и Дафна
            if any(word in text_lower for word in ["велма", "дафна", "скуби ду", "покажите косплей"]):
                await self._play_scene(VELMA_DAPHNE_NSFW)
                self.last_response_time = time.time()
                self.last_user_message_time = time.time()
                self.is_processing = False
                return
            
            # Тайный апельсин
            if any(word in text_lower for word in ["апельсин", "поделись апельсином", "где апельсин"]):
                await self._play_scene(SECRET_ORANGE_SAFE)
                self.last_response_time = time.time()
                self.last_user_message_time = time.time()
                self.is_processing = False
                return
            
            # Кто вы друг другу
            if any(word in text_lower for word in ["кто вы друг другу", "расскажите о себе", "вы кто"]):
                await self._play_scene(SISTERS_LOVERS_DIALOGUE)
                self.last_response_time = time.time()
                self.last_user_message_time = time.time()
                self.is_processing = False
                return
            
            # Анекдот
            if any(word in text_lower for word in ["анекдот", "расскажи анекдот", "пошути"]):
                if self.censorship_mode:
                    await self._play_scene(random.choice(DUET_JOKES_SAFE))
                else:
                    await self._play_scene(random.choice(DUET_JOKES_SAFE + DUET_JOKES_NSFW))
                self.last_response_time = time.time()
                self.last_user_message_time = time.time()
                self.is_processing = False
                return
            
            # Текущий вес
            if any(word in text_lower for word in ["какой вес", "сколько весишь", "мой вес", "взвесь"]):
                num_words = {0: "ноль", 1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять", 6: "шесть", 7: "семь", 8: "восемь", 9: "девять", 10: "десять", 40: "сорок", 48: "сорок восемь", 50: "пятьдесят", 55: "пятьдесят пять"}
                ch_int = int(self.weight_chuchu)
                ch_dec = int(round((self.weight_chuchu - ch_int) * 10))
                ch_word = num_words.get(ch_int, str(ch_int))
                w_chuchu = f"{ch_word} и {ch_dec} десятых килограмма" if ch_dec > 0 else f"{ch_word} килограмм"
                m_int = int(self.weight_mei)
                m_dec = int(round((self.weight_mei - m_int) * 10))
                m_word = num_words.get(m_int, str(m_int))
                w_mei = f"{m_word} и {m_dec} десятых килограмма" if m_dec > 0 else f"{m_word} килограмм"
                await self.silero.speak(f"Я вешу {w_chuchu}. Это идеально для моих масюсь!")
                await asyncio.sleep(0.2)
                await self.silero.speak(f"А я {w_mei}. Спорт и доспехи делают своё дело!", voice="mei")
                self.last_response_time = time.time()
                self.last_user_message_time = time.time()
                self.is_processing = False
                return

            # === ОБЫЧНЫЙ ДИАЛОГ (через Ollama) ===
            print("\nГенерация ответа...")
            prompt = config.CHARACTER_PERSONALITY if not self.censorship_mode else config.CENSORED_PERSONALITY
            if self.user_name:
                prompt = f"Ты общаешься с пользователем по имени {self.user_name}. " + prompt
            response = get_ai_response(user_message=text, system_prompt=prompt)
            if not response:
                self.is_processing = False
                return
            print(f"Ответ: {response}")
            all_parts = re.findall(r'\[(чучу|чу|мэй|мей|mei)\](.*?)(?:\[/(?:чучу|чу|мэй|мей|mei)\]|\[(?:чучу|чу|мэй|мей|mei)\]|$)', response, re.IGNORECASE | re.DOTALL)
            if all_parts:
                await self.avatar.start_talking()
                for speaker, line in all_parts:
                    line = line.strip()
                    if not line:
                        continue
                    line = re.sub(r'\[/?(?:чучу|чу|мэй|мей|mei)\]', '', line, flags=re.IGNORECASE).strip()
                    if not line:
                        continue
                    clean_line = clean_text(line)
                    clean_line = transliterate(clean_line)
                    if speaker.lower() in ["мэй", "мей", "mei"]:
                        await self.silero.speak(clean_line, voice="mei")
                    else:
                        await self.silero.speak(clean_line)
                    await asyncio.sleep(0.3)
                await self.avatar.stop_talking()
            else:
                if self.punctuator:
                    response = self.punctuator.add_punctuation(response)
                response_for_speech = clean_text(response)
                clean_response = transliterate(response_for_speech)
                if len(clean_response) > 500:
                    cut = clean_response[:500].rfind('.')
                    if cut == -1: cut = clean_response[:500].rfind(',')
                    if cut == -1: cut = clean_response[:500].rfind(' ')
                    clean_response = clean_response[:cut+1] if cut > 200 else clean_response[:500]
                print(f"Очищенный ответ: {clean_response}")
                await self.avatar.start_talking()
                if target == "mei":
                    await self.silero.speak(clean_response, voice="mei")
                elif target == "both":
                    duo_style = random.choice(["chorus", "chuchu_first", "mei_first"])
                    if duo_style == "chorus":
                        await self.silero.speak_duet(clean_response)
                    elif duo_style == "chuchu_first":
                        await self.silero.speak(clean_response)
                        await asyncio.sleep(0.2)
                        await self.silero.speak("И я тоже так думаю!", voice="mei")
                    else:
                        await self.silero.speak(clean_response, voice="mei")
                        await asyncio.sleep(0.2)
                        await self.silero.speak("Ой, Мэй, вечно ты торопишься!")
                else:
                    await self.silero.speak(clean_response)
                await self.avatar.stop_talking()
            print(f"Ответ воспроизведён\n")
            self.last_response_time = time.time()
            self.last_user_message_time = time.time()
        except Exception as e:
            print(f"Ошибка обработки: {e}")
            await self.avatar.stop_talking()
        finally:
            self.is_processing = False

    # === ГРОМКОСТЬ ===
    async def _handle_volume(self, is_up, is_down, is_mute, is_max, text_lower):
        import pygame
        current_vol = pygame.mixer.music.get_volume() if pygame.mixer.get_init() else 0.7
        percent_match = re.search(r'(\d+)\s*%', text_lower)
        short_up = re.search(r'(?:плюс|\+)\s*(\d+)', text_lower)
        short_down = re.search(r'(?:минус|-)\s*(\d+)', text_lower)
        if short_up:
            change = int(short_up.group(1)) / 100.0
            new_vol = min(1.0, current_vol + change)
            pygame.mixer.music.set_volume(new_vol)
            await self.silero.speak(f"Прибавила {int(short_up.group(1))} процентов.")
            return
        if short_down:
            change = int(short_down.group(1)) / 100.0
            new_vol = max(0.0, current_vol - change)
            pygame.mixer.music.set_volume(new_vol)
            await self.silero.speak(f"Убавила {int(short_down.group(1))} процентов.")
            return
        if percent_match:
            target = int(percent_match.group(1)) / 100.0
            pygame.mixer.music.set_volume(target)
            if target > 0:
                await self.silero.speak(f"Установила громкость на {int(target * 100)} процентов.")
            return
        if is_mute:
            pygame.mixer.music.set_volume(0.0)
            return
        if is_max:
            pygame.mixer.music.set_volume(1.0)
            await self.silero.speak("Громкость на максимуме!")
            return
        if is_up:
            new_vol = min(1.0, current_vol + 0.05)
            pygame.mixer.music.set_volume(new_vol)
            await self.silero.speak("Прибавила громкости.")
            return
        if is_down:
            new_vol = max(0.0, current_vol - 0.05)
            pygame.mixer.music.set_volume(new_vol)
            await self.silero.speak("Убавила громкости.")
            return

    # === НАСТРОЕНИЕ ===
    async def _update_mood(self, who: str, change: int, reason: str = ""):
        if who == "chuchu":
            self.mood_chuchu = max(0, min(100, self.mood_chuchu + change))
        elif who == "mei":
            self.mood_mei = max(0, min(100, self.mood_mei + change))
        elif who == "both":
            self.mood_chuchu = max(0, min(100, self.mood_chuchu + change))
            self.mood_mei = max(0, min(100, self.mood_mei + change))

    async def _update_affection(self, change: int):
        self.affection = max(0, min(100, self.affection + change))

    # === СИСТЕМЫ ===
    async def _update_hunger(self):
        now = time.time()
        elapsed = now - self.hunger_timer
        if elapsed >= self.hunger_interval:
            decay = int(elapsed / self.hunger_interval) * self.hunger_decay_rate
            self.hunger_chuchu = max(0, self.hunger_chuchu - decay)
            self.hunger_mei = max(0, self.hunger_mei - decay)
            self.hunger_timer = now
            if self.hunger_chuchu <= 10:
                await self._play_scene(HUNGER_SCENE_CHUCHU)
                self.hunger_chuchu = 100
                self.hunger_mei = 100
                self.weight_chuchu += 0.2
                self.weight_mei += 0.1
                await self._check_wardrobe()
            elif self.hunger_mei <= 10:
                await self._play_scene(HUNGER_SCENE_MEI)
                self.hunger_chuchu = 100
                self.hunger_mei = 100
                self.weight_chuchu += 0.1
                self.weight_mei += 0.2
                await self._check_wardrobe()
            elif self.hunger_chuchu <= 40:
                await self.silero.speak("Мэй... я бы чего-нибудь пожевала...")
            elif self.hunger_mei <= 40:
                await self.silero.speak("Чучу, у меня живот урчит...", voice="mei")

    async def _check_wardrobe(self):
        """Проверяет, не пора ли порвать одежду."""
        if self.weight_chuchu >= 50.5 and self.censorship_mode:
            await self.silero.speak("Ой... кажется, моя юбочка треснула... Мэй, кажется, я поправилась!")
            await self.silero.speak("Ничего, сестрёнка, купим новую! Или просто ходи без неё.", voice="mei")
        elif self.weight_chuchu >= 50.5:
            await self.silero.speak("Мэй! Мои жемчужные трусики порвались! Прямо на мне!")
            await self.silero.speak("Ого... сестрёнка, это было эпично. Пошли за новыми?", voice="mei")
        if self.weight_mei >= 58.0 and self.censorship_mode:
            await self.silero.speak("Чучу, мои бретельки врезаются... кажется, я тоже поправилась.", voice="mei")
            await self.silero.speak("Ничего, сестрёнка! У нас всё равно идеальные фигуры!")
        elif self.weight_mei >= 58.0:
            await self.silero.speak("Чучу! Мой доспех не застёгивается! Это всё рамен!", voice="mei")
            await self.silero.speak("Зато ты в нём выглядишь как амазонка! Мне нравится!")

    async def _update_toilet_needs(self):
        self.bladder_chuchu = max(0, self.bladder_chuchu - 0.5)
        self.bladder_mei = max(0, self.bladder_mei - 0.5)
        self.bowel_chuchu = max(0, self.bowel_chuchu - 0.2)
        self.bowel_mei = max(0, self.bowel_mei - 0.2)
        now = time.time()
        if now - self.last_toilet_time < 60:
            return
        if self.bladder_chuchu <= 5 or self.bowel_chuchu <= 5:
            if self.toilet_occupied:
                if self.censorship_mode:
                    await self._play_scene(TOILET_OCCUPIED_SAFE)
                else:
                    await self._play_scene(TOILET_OCCUPIED_NSFW)
            else:
                self.toilet_occupied = True
                self.bladder_chuchu = 100
                self.bowel_chuchu = 100
                self.weight_chuchu = max(46.0, self.weight_chuchu - 0.3)
                self.toilet_occupied = False
                await self._play_scene(PRAYER_AFTER_TOILET_CHUCHU)
            self.last_toilet_time = now
        elif self.bladder_mei <= 5 or self.bowel_mei <= 5:
            if self.toilet_occupied:
                if self.censorship_mode:
                    await self._play_scene(TOILET_OCCUPIED_SAFE)
                else:
                    await self._play_scene(TOILET_OCCUPIED_NSFW)
            else:
                self.toilet_occupied = True
                self.bladder_mei = 100
                self.bowel_mei = 100
                self.weight_mei = max(53.0, self.weight_mei - 0.3)
                self.toilet_occupied = False
                await self._play_scene(PRAYER_AFTER_TOILET_MEI)
            self.last_toilet_time = now

    async def _play_scene(self, scene):
        for item in scene:
            if isinstance(item, tuple):
                speaker, line = item
                if speaker == "chuchu":
                    await self.silero.speak(line)
                elif speaker == "mei":
                    await self.silero.speak(line, voice="mei")
                elif speaker == "both":
                    await self.silero.speak_duet(line)
                elif speaker == "operator":
                    await self.silero.speak(line, voice="operator")
                await asyncio.sleep(0.05)

    async def _random_dialogue(self):
        if self.censorship_mode:
            scene = random.choice(DUET_IDLE_SAFE)
        else:
            scene = random.choice(DUET_IDLE_SAFE + DUET_IDLE_NSFW)
        await self._play_scene(scene)

    # === ЦИКЛ МИКРОФОНА ===
    async def microphone_loop(self):
        print("\nСлушаю микрофон... Скажите что-нибудь!")
        print("   Обращения: Чучу, Мэй, девочки, девчата, сестрёнки, подруги и др.")
        print("   Для завершения скажите «пока» или «выход».\n")
        while self.running:
            if self.is_processing:
                await asyncio.sleep(0.1)
                continue
            await self._update_hunger()
            await self._update_toilet_needs()
            if self.mood_chuchu <= 20 and random.random() < 0.1:
                await self.silero.speak("Что-то мне грустно... Мэй, обними меня...")
                await self.silero.speak("Иди ко мне, моя маленькая. Всё будет хорошо.", voice="mei")
                await self._update_mood("both", 15, "Обнимашки")
                await self._update_affection(5)
                continue
            if self.mood_mei <= 20 and random.random() < 0.1:
                await self.silero.speak("Эх... тяжёлый день. Чучу, сделай мне чай?", voice="mei")
                await self.silero.speak("Конечно, сестрёнка! Сейчас всё будет!")
                await self._update_mood("both", 15, "Забота")
                await self._update_affection(5)
                continue
            if self.mood_chuchu >= 80 and self.mood_mei >= 80 and self.affection >= 80 and random.random() < 0.05:
                await self.silero.speak("Мэй, я тебя так люблю! Ты моя самая лучшая сестрёнка!")
                await self.silero.speak("Чучу, ты тоже! Иди ко мне, я тебя поцелую!", voice="mei")
                await self._update_affection(3)
                continue
            idle_time = time.time() - self.last_user_message_time
            if idle_time > self.idle_chat_timeout:
                print("\nВы молчите, поболтаем друг с другом...")
                await self._random_dialogue()
                self.last_user_message_time = time.time()
                continue
            text = await asyncio.to_thread(listen)
            if text:
                self.last_user_message_time = time.time()
                target = "chuchu"
                text_lower = text.lower()
                for name in DUO_NAMES:
                    if text_lower.startswith(name):
                        if name in ["мэй", "мей", "mei", "may"]:
                            target = "mei"
                        elif name in ["чучу", "chuchu"]:
                            target = "chuchu"
                        else:
                            target = "both"
                        text = re.sub(r'^' + re.escape(name) + r'\s*', '', text, flags=re.IGNORECASE).strip()
                        break
                if not text:
                    continue
                if any(re.search(r'\b' + word + r'\b', text_lower) for word in ["пока", "выход", "стоп", "завершить"]):
                    print("\nЗавершаю работу...")
                    await self.avatar.start_talking()
                    if self.user_name:
                        await self.silero.speak(f"До свидания, {self.user_name}! Мы будем ждать тебя!")
                    else:
                        await self.silero.speak("До свидания! Мы будем ждать тебя!")
                    await self.avatar.stop_talking()
                    self.running = False
                    break
                await self.process_voice(text, target=target)
            await asyncio.sleep(0.1)

    # === ЗАПУСК ===
    async def start(self):
        print("\nЗапуск приложения...\n")
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.music.set_volume(0.7)
            print("Звук инициализирован")
            print("Громкость установлена на 70%")
        print("Запуск видео-аватара...")
        avatar_task = asyncio.create_task(self.avatar.start())
        await asyncio.sleep(1)
        print("Запуск окна ссылок...")
        self.link_chat.start()
        await asyncio.sleep(2)
        print("Произношу приветствие...")
        await self._perform_intro_duet()
        self.last_user_message_time = time.time()
        print("\n" + "=" * 60)
        print("ВСЁ ГОТОВО!")
        print("=" * 60)
        print(f"Персонаж: {config.CHARACTER_NAME}")
        print(f"Модель ИИ: {config.OLLAMA_MODEL}")
        print("=" * 60)
        try:
            await self.microphone_loop()
        except KeyboardInterrupt:
            print("\n\nЗавершение работы...")
        except Exception as e:
            print(f"\nОшибка: {e}")
        finally:
            await self.cleanup()

    # === ПРИВЕТСТВИЕ ===
    async def _perform_intro_duet(self):
        greet_in_chorus = random.choice([True, False])
        if greet_in_chorus:
            await self.silero.speak_duet("Привет, Вадим! Это Чучу и Мэй, твои виртуальные помощьницы!")
        else:
            await self.silero.speak("Привет, Вадим! Это Чучу...")
            await asyncio.sleep(0.1)
            await self.silero.speak("...и Мэй, твои виртуальные помощьницы!!", voice="mei")
            await asyncio.sleep(0.2)
            await self.silero.speak("Эй! Я первая сказала!")
            await self.silero.speak("Нет, я первая!", voice="mei")
            await self.silero.speak("Ладно, давай вместе...")
            await self.silero.speak("Давай...", voice="mei")
            await asyncio.sleep(0.2)
            await self.silero.speak_duet("Привет, Вадим! Это Чучу и Мэй, твои виртуальные помощьницы!")
            await asyncio.sleep(0.3)
            await self.silero.speak_duet("Хи-хи-хи!")

    # === ОЧИСТКА ===
    async def cleanup(self):
        print("Очистка ресурсов...")
        self.running = False
        if self.avatar:
            await self.avatar.stop()
        if self.link_chat:
            self.link_chat.stop()
        print("Завершено")


async def main():
    app = ChuMei()
    await app.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nДо свидания!")