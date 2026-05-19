import torch
import numpy as np
import scipy.io.wavfile as wav
import asyncio
import pygame
import tempfile
import os
import re

class SileroTTS:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        torch.set_num_threads(4)
        
        self.model, _ = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='ru',
            speaker='v5_4_ru'
        )
        self.model.to(self.device)
        self.sample_rate = 48000
        
        # ========== НАСТРОЙКА ВСЕХ 5 ГОЛОСОВ ==========
        self.VOICE_CONFIG = {
            "chuchu": {"speaker": "xenia", "rate": 1.0},
            "mei": {"speaker": "baya", "rate": 1.0},
            "hana": {"speaker": "xenia", "rate": 0.85},
            "ki": {"speaker": "baya", "rate": 0.77},
            "simone": {"speaker": "baya", "rate": 0.95},
        }
        
        self.max_chunk_size = 5000
        self.chunk_pause = 0.3
        
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
        self.audio_cache = {}
    
    def _transliterate_english(self, text):
        """Расширенная замена английских слов, имён и названий"""
        
        text = re.sub(r'\[[a-z]+\]', '', text)
        text = re.sub(r'\[/[a-z]+\]', '', text)
        text = re.sub(r'<[^>]+>', '', text)
        
        proper_names = {
            'Yaya Han': 'Яя Хан',
            'Yaya': 'Яя',
            'Han': 'Хан',
            'Kamui Cosplay': 'Камуи Косплей',
            'Kamui': 'Камуи',
            'Joe Cocker': 'Джо Кокер',
            'Joe': 'Джо',
            'Cocker': 'Кокер',
            'You Can Leave Your Hat On': 'Ю Кэн Лив Ёр Хэт Он',
            'Unchain My Heart': 'Анчейн Май Харт',
            'The Phantom Agony': 'Фантом Агони',
            'Phantom Agony': 'Фантом Агони',
            'ChuMei Distribution': 'Чумей Дистрибьюшн',
            'ChuMei': 'Чумей',
            'ChuMei Angels': 'Чумей Энджелс',
            'Yahoo Auctions Japan': 'Яху Окшнс Джапан',
            'Mercari': 'Меркари',
            'AllThingsWorn': 'Ол Синкс Уорн',
            'Hana Bunny x Yaya Han': 'Хана Банни энд Яя Хан',
            'SPF': 'Эс-Пи-Эф',
            'Vincent': 'Винсент',
            'Ilse': 'Ильзе',
            'Yaya Han x Hana Bunny': 'Яя Хан и Хана Банни',
            'Simons': 'Симонс',
            'Live in Seoul': 'Лайв ин Сеул',
            'Live': 'Лайв',
            'Seoul': 'Сеул',
        }
        
        for eng, rus in proper_names.items():
            text = text.replace(eng, rus)
        
        eng_words = {
            'Potato': 'Потейто',
            'potato': 'потейто',
            'Ki': 'Ки',
            'ki': 'ки',
            'Chu': 'Чу',
            'chu': 'чу',
            'Mei': 'Мэй',
            'mei': 'мэй',
            'Hana': 'Хана',
            'hana': 'хана',
            'Bunny': 'Банни',
            'bunny': 'банни',
            'Simone': 'Симона',
            'simone': 'симона',
            'Epica': 'Эпика',
            'epica': 'эпика',
        }
        
        for eng, rus in eng_words.items():
            text = text.replace(eng, rus)
        
        text = text.replace('«', '"').replace('»', '"')
        text = re.sub(r'\b[a-zA-Z]\b', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _number_to_words(self, num):
        """Преобразует число от 0 до 9999 в слова"""
        if num == 0:
            return "ноль"
        
        simple = {
            1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять",
            6: "шесть", 7: "семь", 8: "восемь", 9: "девять", 10: "десять",
            11: "одиннадцать", 12: "двенадцать", 13: "тринадцать", 14: "четырнадцать",
            15: "пятнадцать", 16: "шестнадцать", 17: "семнадцать", 18: "восемнадцать",
            19: "девятнадцать"
        }
        
        tens = {
            20: "двадцать", 30: "тридцать", 40: "сорок", 50: "пятьдесят",
            60: "шестьдесят", 70: "семьдесят", 80: "восемьдесят", 90: "девяносто"
        }
        
        hundreds = {
            100: "сто", 200: "двести", 300: "триста", 400: "четыреста",
            500: "пятьсот", 600: "шестьсот", 700: "семьсот", 800: "восемьсот", 900: "девятьсот"
        }
        
        thousands = {
            1: "одна тысяча", 2: "две тысячи", 3: "три тысячи", 4: "четыре тысячи",
            5: "пять тысяч", 6: "шесть тысяч", 7: "семь тысяч", 8: "восемь тысяч", 9: "девять тысяч"
        }
        
        if num in simple:
            return simple[num]
        
        if num < 100:
            tens_num = (num // 10) * 10
            units = num % 10
            result = tens[tens_num]
            if units > 0:
                result += " " + simple[units]
            return result
        
        if num < 1000:
            hundreds_num = (num // 100) * 100
            rest = num % 100
            result = hundreds[hundreds_num]
            if rest > 0:
                result += " " + self._number_to_words(rest)
            return result
        
        if num < 10000:
            thousands_num = num // 1000
            rest = num % 1000
            
            if thousands_num in thousands:
                result = thousands[thousands_num]
            else:
                result = self._number_to_words(thousands_num) + " тысяч"
            
            if rest > 0:
                result += " " + self._number_to_words(rest)
            return result
        
        return str(num)
    
    def _replace_numbers(self, text):
        """Заменяет все числа в тексте на слова"""
        
        special_cases = {
            '20двадцать13': 'две тысячи тринадцать',
            '20двадцать': 'двадцать',
            '4пятьсот': 'четыреста',
            'триста0': 'триста',
            '3000': 'три тысячи',
            '2500': 'две тысячи пятьсот',
            '2000': 'две тысячи',
            '1500': 'одна тысяча пятьсот',
            '1000': 'одна тысяча',
            '5000': 'пять тысяч',
            '10': 'десять',
        }
        
        for special, replacement in special_cases.items():
            text = text.replace(special, replacement)
        
        def replace_match(match):
            num_str = match.group()
            try:
                num = int(num_str)
                if 1 <= num <= 9999:
                    return self._number_to_words(num)
                return num_str
            except:
                return num_str
        
        pattern = r'\b\d{1,4}\b'
        text = re.sub(pattern, replace_match, text)
        
        pattern_attached = r'(\d{1,4})([а-яА-ЯёЁ]+)'
        text = re.sub(pattern_attached, lambda m: self._number_to_words(int(m.group(1))) + " " + m.group(2), text)
        
        pattern_mixed = r'([а-яА-ЯёЁ]+)(\d{1,4})'
        text = re.sub(pattern_mixed, lambda m: m.group(1) + " " + self._number_to_words(int(m.group(2))), text)
        
        return text
    
    def _split_into_sentences(self, text):
        """Разбивает текст на предложения"""
        sentences = re.split(r'(?<=[.!?;:…])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_into_chunks(self, text):
        """Разбивает длинный текст на части по предложениям"""
        if len(text) <= self.max_chunk_size:
            return [text]
        
        print(f"📖 Разбиваю длинный текст ({len(text)} символов) на части...")
        
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= self.max_chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        print(f"📖 Текст разбит на {len(chunks)} частей")
        return chunks
    
    def generate_audio(self, text, voice="chuchu"):
        """Генерирует аудио из текста"""
        cfg = self.VOICE_CONFIG.get(voice, self.VOICE_CONFIG["chuchu"])
        
        try:
            audio = self.model.apply_tts(
                text=text,
                speaker=cfg["speaker"],
                sample_rate=self.sample_rate,
                put_accent=True,
                put_yo=True,
                put_stress_homo=True,
                put_yo_homo=True
            )
            return audio.cpu().numpy()
        except Exception as e:
            print(f"⚠️ Ошибка синтеза: {e}")
            try:
                shorter_text = text[:300] if len(text) > 300 else text
                audio = self.model.apply_tts(
                    text=shorter_text,
                    speaker=cfg["speaker"],
                    sample_rate=self.sample_rate
                )
                return audio.cpu().numpy()
            except Exception as e2:
                print(f"❌ Критическая ошибка синтеза: {e2}")
                return np.zeros(16000)
    
    def save_to_wav(self, audio, filename):
        """Сохраняет аудио в WAV файл"""
        audio_int16 = (audio * 32767).astype(np.int16)
        wav.write(filename, self.sample_rate, audio_int16)
    
    def play_audio(self, audio):
        """Воспроизводит аудио через pygame"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            self.save_to_wav(audio, f.name)
            temp_file = f.name
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.wait(10)
        
        try:
            os.unlink(temp_file)
        except:
            pass
    
    async def speak(self, text, voice="chuchu"):
        """Основной метод для озвучивания текста"""
        if not text or not text.strip():
            return
        
        text = self._transliterate_english(text)
        text = self._replace_numbers(text)
        text = re.sub(r'[ \t]+', ' ', text).strip()
        text = re.sub(r'([.!?;:])([А-Яа-я])', r'\1 \2', text)
        
        chunks = self._split_into_chunks(text)
        
        if len(chunks) == 1:
            print(f"🎤 {voice}: {chunks[0][:100]}...")
            cache_key = f"{voice}:{chunks[0]}"
            if cache_key not in self.audio_cache:
                self.audio_cache[cache_key] = self.generate_audio(chunks[0], voice)
            await asyncio.to_thread(self.play_audio, self.audio_cache[cache_key])
        else:
            print(f"📖 Длинный рассказ ({len(chunks)} частей) от {voice}")
            for i, chunk in enumerate(chunks):
                print(f"  Часть {i+1}/{len(chunks)}: {chunk[:50]}...")
                cache_key = f"{voice}:{chunk}"
                if cache_key not in self.audio_cache:
                    self.audio_cache[cache_key] = self.generate_audio(chunk, voice)
                await asyncio.to_thread(self.play_audio, self.audio_cache[cache_key])
                if i < len(chunks) - 1:
                    await asyncio.sleep(self.chunk_pause)
    
    async def speak_story_alternating(self, story_text, voice1="chuchu", voice2="mei", pause_between=0.5):
        """Рассказывает историю с чередованием голосов"""
        if not story_text or not story_text.strip():
            return
        
        print(f"📖 Начинаем дуэтный рассказ: {voice1} + {voice2}")
        
        story_text = self._transliterate_english(story_text)
        story_text = self._replace_numbers(story_text)
        story_text = re.sub(r'[ \t]+', ' ', story_text).strip()
        
        sentences = self._split_into_sentences(story_text)
        
        if len(sentences) < 2:
            await self.speak(story_text, voice1)
            return
        
        voice1_turns = []
        voice2_turns = []
        
        for i in range(0, len(sentences), 4):
            voice1_part = " ".join(sentences[i:i+2])
            if voice1_part:
                voice1_turns.append(voice1_part)
            
            voice2_part = " ".join(sentences[i+2:i+4])
            if voice2_part:
                voice2_turns.append(voice2_part)
        
        max_turns = max(len(voice1_turns), len(voice2_turns))
        
        for i in range(max_turns):
            if i < len(voice1_turns):
                print(f"🎤 {voice1}: {voice1_turns[i][:80]}...")
                await self.speak(voice1_turns[i], voice1)
                await asyncio.sleep(pause_between)
            
            if i < len(voice2_turns):
                print(f"🎤 {voice2}: {voice2_turns[i][:80]}...")
                await self.speak(voice2_turns[i], voice2)
                if i < max_turns - 1:
                    await asyncio.sleep(pause_between)
        
        print("📖 Рассказ завершён")
    
    async def speak_duet(self, text, main_voice="chuchu"):
        """Озвучивает реплику дуэтом"""
        await self.speak(text, voice=main_voice)