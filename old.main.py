"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         ChuMei - Дуэт Чучу и Мэй                             ║
║                                                                              ║
║  Главный файл приложения. Управляет микрофоном, голосом, памятью и командами ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════
# 1. ИМПОРТЫ
# ═══════════════════════════════════════════════════════════════════════════════

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
from accent_helper import accent_helper  # <-- ДОБАВЛЕНО

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
# 2. ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ═══════════════════════════════════════════════════════════════════════════════

def clean_text(text):
    """Очищает текст от лишних символов, эмодзи и нормализует числа"""
    text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1 \2', text)
    for num, word in sorted(NUM_WORDS.items(), key=lambda x: -len(x[0])):
        text = re.sub(r'\b' + num + r'\b', word, text)
    # ... остальной код clean_text (оставь как было)
    return text


# ═══════════════════════════════════════════════════════════════════════════════
# 3. ОСНОВНОЙ КЛАСС ChuMei
# ═══════════════════════════════════════════════════════════════════════════════

class ChuMei:
    
    def __init__(self):
        """Инициализация всех систем"""
        print("=" * 60)
        print("ChuMei — дуэт Чучу и Мэй")
        print("=" * 60)
        
        self.avatar = AvatarVideo()
        self.link_chat = LinkChat()
        self.silero = SileroTTS()
        self.punctuator = RuPunctuator() if HAS_PUNCTUATOR else None
        self.censorship_mode = True
        self.sleep_mode = False
        self.is_processing = False
        self.running = True
        self.memory = Memory()
        self.user_name = None
        self.name_asked = False
        self.name_file = "user_name.txt"
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
        self.voice_file = "voice_sample.npy"
        self._load_voice_sample()
        
        
        
        
    def _load_user_name(self):
        if os.path.exists(self.name_file):
            with open(self.name_file, 'r', encoding='utf-8') as f:
                self.user_name = f.read().strip()
                if self.user_name:
                    self.name_asked = True
                    print(f"Загружено имя: {self.user_name}")
    
    def _load_voice_sample(self):
        if os.path.exists(self.voice_file):
            self.voice_embedding = np.load(self.voice_file)
            self.voice_enrolled = True
            print("Образец голоса загружен")
    
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
    
    
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ОСНОВНОЙ ЦИКЛ
    # ═══════════════════════════════════════════════════════════════════════════
    
    async def microphone_loop(self):
        print("\n🎤 Слушаю микрофон... Скажите что-нибудь!")
        print("   Обращения: Чучу, Мэй, девочки, девчата, сестрёнки")
        print("   Команды: режим обучения, запомни, напомни, свободна")
        print("   Для выхода: пока, выход, стоп\n")
        
        while self.running:
            if self.is_processing:
                await asyncio.sleep(0.1)
                continue
            
            await self._update_hunger()
            await self._update_toilet_needs()
            
            if time.time() - self.last_user_message_time > self.idle_chat_timeout:
                print("\n💬 Вы молчите, поболтаем...")
                await self._random_dialogue()
                self.last_user_message_time = time.time()
                continue
            
            text = await asyncio.to_thread(listen)
            print(f"🎤 РАСПОЗНАНО: '{text}'")
            
            # ═══════════════════════════════════════════════════════════════════
            # ПРЯМОЙ ПЕРЕХВАТ КОМАНД (БЕЗ АДАМЫ)
            # ═══════════════════════════════════════════════════════════════════
            if text:
                text_lower = text.lower()
                
                # ----- 1. РЕЖИМ ОБУЧЕНИЯ ДЛЯ ЧУЧУ -----
                if "чучу режим обучения" in text_lower or "чу режим обучения" in text_lower or "чу-чу режим обучения" in text_lower:
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
                
                # ----- 8.1 ПРЯМОЕ ЗАПОМИНАНИЕ ДЛЯ МЭЙ (без слова "запомни") -----
                # Проверяем, что Мэй в режиме обучения И фраза содержит описание внешности
                mei_learning = self.memory.get_learning_mode("mei")
                # Слова-маркеры, которые указывают на описание внешности
                description_keywords = ["ты красивая", "стройная", "шикарная", "сексуальная", 
                                       "у тебя", "твоя", "твои", "твоё", "твоя грудь", 
                                       "твои волосы", "твои глаза", "твоя фигура"]
                
                if mei_learning and ("мэй" in text_lower or "мея" in text_lower):
                    # Проверяем, есть ли в фразе слово-маркер описания
                    is_description = any(keyword in text_lower for keyword in description_keywords)
                    
                    # Исключаем команды
                    is_command = any(word in text_lower for word in ["режим", "свобод", "запомни", "напомни"])
                    
                    if is_description and not is_command:
                        # Убираем обращение
                        fact = re.sub(r'^(мэй|мея|mei)\s*', '', text_lower)
                        # Убираем вводные слова
                        fact = re.sub(r'^(ты |твоя |у тебя )', '', fact)
                        if fact and len(fact) > 5:
                            print(f"✅ ПЕРЕХВАТ: Мэй прямое запоминание '{fact}'")
                            self.memory.save_fact("mei", fact)
                            await self._speak("Запомнила про себя!", voice="mei")
                            self._reset_timers()
                            continue
                        
                # ----- 8.1 ПРЯМОЕ ЗАПОМИНАНИЕ ДЛЯ Ч (без слова "запомни") -----
                # Проверяем, что Мэй в режиме обучения
                mei_learning = self.memory.get_learning_mode("mei")
                if mei_learning and ("мэй" in text_lower or "мея" in text_lower or "mei" in text_lower):
                    # Убираем обращение
                    fact = re.sub(r'^(мэй|мея|mei)\s*', '', text_lower)
                    # Убираем слова-триггеры, если они есть в начале
                    fact = re.sub(r'^(ты |твоя |у тебя |ты, |твоя, |у тебя, )', '', fact)
                    if fact and len(fact) > 5 and not fact.startswith("режим") and not fact.startswith("свобод"):
                        print(f"✅ ПЕРЕХВАТ: Мэй прямое запоминание '{fact}'")
                        self.memory.save_fact("mei", fact)
                        await self._speak("Запомнила про себя!", voice="mei")
                        self._reset_timers()
                        continue        
                
                # ----- 9. ИЗМЕНИ ТЕЛО -----
                if "измени тело" in text_lower or "поменяй тело" in text_lower:
                    print("✅ ПЕРЕХВАТ: изменить тело")
                    await self._handle_change_body(text_lower)
                    self._reset_timers()
                    continue
                
                # ----- 10. РАСКРЕПОСТИСЬ -----
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
                
                # ----- 11. ЦЕНЗУРА -----
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
                
                    async def start(self):
        """Запуск бота после инициализации"""
        print("🔊 Тест голосов Ханы и Ки...")
        
        # Тест Ханы (быстро)
        await self.silero.speak("Меня зовут Ха на, я люблю дошик и деньги!", voice="hana")
        await asyncio.sleep(1)
        
        # Тест Ки (медленно)
        await self.silero.speak("Здравствуйте... я Ки. Я... стесняюсь.", voice="ki")
        
        print("✅ Тест завершён. Запускаю основной цикл...")
        
        # Запуск основного цикла (link_chat)
        await self.link_chat.start()
    # 🔼🔼🔼 КОНЕЦ МЕТОДА start() 🔼🔼🔼

async def main():
    app = ChuMei()
    await app.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
                
            # ═══════════════════════════════════════════════════════════════════
            # ОБЫЧНЫЙ ДИАЛОГ (через Адаму)
            # ═══════════════════════════════════════════════════════════════════
            if text:
                await self._process_normal(text)
            
            await asyncio.sleep(0.1)
    
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
    
    async def _process_normal(self, text):
        self.last_user_message_time = time.time()
        target, clean_text = self._parse_target(text)
        if not clean_text:
            return
        
        if any(word in clean_text.lower() for word in ["пока", "выход", "стоп", "завершить"]):
            await self._speak(f"До свидания, {self.user_name or 'Вадим'}! Мы будем ждать тебя!")
            self.running = False
            return
        
        print("\n🧠 Генерация ответа...")
        prompt = config.CHARACTER_PERSONALITY if not self.censorship_mode else config.CENSORED_PERSONALITY
        if self.user_name:
            prompt = f"Ты общаешься с пользователем по имени {self.user_name}. " + prompt
        
        response = get_ai_response(user_message=clean_text, system_prompt=prompt, girl_name=target if target in ["chuchu", "mei"] else "chuchu")
        if response:
            await self._play_response(response, target)
        
        self.last_response_time = time.time()
    
    def _parse_target(self, text):
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
        return target, text
    
    async def _play_response(self, response, target):
        await self.avatar.start_talking()
        parts = re.findall(r'\[(чучу|чу|мэй|мей|mei)\](.*?)(?:\[/|\[|$)', response, re.IGNORECASE | re.DOTALL)
        
        if parts:
            for speaker, line in parts:
                line = line.strip()
                if line:
                    clean_line = transliterate(clean_text(line))
                    if speaker.lower() in ["мэй", "мей", "mei"]:
                        await self.silero.speak(clean_line, voice="mei")
                    else:
                        await self.silero.speak(clean_line)
                    await asyncio.sleep(0.2)
        else:
            clean_response = transliterate(clean_text(response))
            if target == "mei":
                await self.silero.speak(clean_response, voice="mei")
            elif target == "both":
                await self.silero.speak_duet(clean_response)
            else:
                await self.silero.speak(clean_response)
        
        await self.avatar.stop_talking()
        print("✅ Ответ воспроизведён")
    
    async def _speak(self, text, voice=None, duet=False):
        # Расставляем ударения с помощью RUAccent
        try:
            text = accent_helper.process_for_tts(text)
        except Exception as e:
            print(f"⚠️ Ошибка расстановки ударений: {e}")
        
        print(f"🔊 Говорит {voice or 'chuchu'}: {text[:100]}...")
        await self.avatar.start_talking()
        if duet:
            await self.silero.speak_duet(text)
        elif voice == "mei":
            await self.silero.speak(text, voice="mei")
        else:
            await self.silero.speak(text)
        await self.avatar.stop_talking()
    
    def _reset_timers(self):
        self.last_response_time = time.time()
        self.last_user_message_time = time.time()
        self.is_processing = False
    
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
                await asyncio.sleep(0.05)
    
    async def _random_dialogue(self):
        if self.censorship_mode:
            scene = random.choice(DUET_IDLE_SAFE)
        else:
            scene = random.choice(DUET_IDLE_SAFE + DUET_IDLE_NSFW)
        await self._play_scene(scene)
    
    async def _update_hunger(self):
        pass
    
    async def _update_toilet_needs(self):
        pass
    
    async def _update_mood(self, who, change, reason=""):
        pass
    
    async def start(self):
        print("\n🚀 Запуск приложения...")
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.music.set_volume(0.7)
        
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
        await self.silero.speak_duet("Привет, Вадим! Это Чучу и Мэй, твои виртуальные помощницы! Хи-хи-хи!")
    
    async def cleanup(self):
        print("\n🧹 Очистка ресурсов...")
        self.running = False
        if self.avatar:
            await self.avatar.stop()
        if self.link_chat:
            self.link_chat.stop()
        print("✅ Завершено")


