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
        
        # Загружаем v5_4_ru
        self.model, _ = torch.hub.load(
            repo_or_dir='snakers4/silero-models',
            model='silero_tts',
            language='ru',
            speaker='v5_4_ru'
        )
        self.model.to(self.device)
        self.sample_rate = 48000
        
        # Настройки голосов
        self.VOICE_CONFIG = {
            "chuchu": {"speaker": "xenia", "rate": 1.0},
            "mei": {"speaker": "baya", "rate": 1.0},
            "hana": {"speaker": "xenia", "rate": 0.7},
            "ki": {"speaker": "baya", "rate": 0.77},
            "simone": {"speaker": "baya", "rate": 0.95},
        }
        
        # Инициализация pygame для воспроизведения
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
        
        # Кэш для аудио
        self.audio_cache = {}
    
    def _truncate_text(self, text, max_len=400):
        """Обрезает текст до максимальной длины, сохраняя последнее предложение"""
        if len(text) <= max_len:
            return text
        
        print(f"⚠️ Текст слишком длинный ({len(text)} символов), обрезаю до {max_len}")
        
        # Обрезаем до max_len
        truncated = text[:max_len]
        
        # Ищем последнюю точку, вопросительный или восклицательный знак
        last_punct = max(
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?'),
            truncated.rfind('\n')
        )
        
        if last_punct > max_len // 2:
            truncated = truncated[:last_punct + 1]
        else:
            # Если нет хорошей границы, обрезаем по пробелу
            last_space = truncated.rfind(' ')
            if last_space > max_len // 2:
                truncated = truncated[:last_space]
        
        return truncated + " ..."
    
    def generate_audio(self, text, voice="chuchu"):
        """Генерирует аудио из текста"""
        cfg = self.VOICE_CONFIG.get(voice, self.VOICE_CONFIG["chuchu"])
        
        # Обрезаем длинный текст
        text = self._truncate_text(text, max_len=400)
        
        # Обычный синтез с ударениями
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
            print(f"Ошибка синтеза: {e}")
            # Пробуем без ударений
            try:
                shorter_text = self._truncate_text(text, max_len=300)
                audio = self.model.apply_tts(
                    text=shorter_text,
                    speaker=cfg["speaker"],
                    sample_rate=self.sample_rate
                )
                return audio.cpu().numpy()
            except Exception as e2:
                print(f"Критическая ошибка синтеза: {e2}")
                # Возвращаем тишину вместо падения
                return np.zeros(16000)
    
    def save_to_wav(self, audio, filename):
        """Сохраняет аудио в WAV файл"""
        audio_int16 = (audio * 32767).astype(np.int16)
        wav.write(filename, self.sample_rate, audio_int16)
    
    def play_audio(self, audio):
        """Воспроизводит аудио через pygame"""
        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            self.save_to_wav(audio, f.name)
            temp_file = f.name
        
        # Воспроизводим
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # Ждём окончания
        while pygame.mixer.music.get_busy():
            pygame.time.wait(10)
        
        # Удаляем временный файл
        try:
            os.unlink(temp_file)
        except:
            pass
    
    async def speak(self, text, voice="chuchu"):
        """Основной метод для озвучивания текста"""
        # ПРЯМАЯ ЗАМЕНА ЧИСЕЛ (в самом последнем моменте)
        text = text.replace("200", "двести")
        text = text.replace("100", "сто")
        text = text.replace("300", "триста")
        text = text.replace("400", "четыреста")
        text = text.replace("500", "пятьсот")
        text = text.replace("600", "шестьсот")
        text = text.replace("700", "семьсот")
        text = text.replace("800", "восемьсот")
        text = text.replace("900", "девятьсот")
        text = text.replace("164", "сто шестьдесят четыре")
        text = text.replace("68", "шестьдесят восемь")
        text = text.replace("2000", "две тысячи")
        text = text.replace("3000", "три тысячи")
        text = text.replace("50", "пятьдесят")
        text = text.replace("60", "шестьдесят")
        text = text.replace("70", "семьдесят")
        text = text.replace("80", "восемьдесят")
        text = text.replace("90", "девяносто")
        text = text.replace("20", "двадцать")
        text = text.replace("30", "тридцать")
        text = text.replace("40", "сорок")
        
        # Замена чисел, прилипших к словам (200долларов → двестидолларов)
        text = re.sub(r'(\d{2,4})([а-яА-Я])', lambda m: {
            "200": "двести", "100": "сто", "300": "триста", "400": "четыреста",
            "500": "пятьсот", "600": "шестьсот", "700": "семьсот", "800": "восемьсот",
            "900": "девятьсот", "164": "сто шестьдесят четыре", "68": "шестьдесят восемь"
        }.get(m.group(1), m.group(1)) + m.group(2), text)
        
        print(f"🎤 {voice}: {text[:100]}...")
        
        # Генерируем аудио (с кэшированием для повторяющихся фраз)
        cache_key = f"{voice}:{text}"
        if cache_key not in self.audio_cache:
            self.audio_cache[cache_key] = self.generate_audio(text, voice)
        
        audio = self.audio_cache[cache_key]
        
        # Воспроизводим в отдельном потоке, чтобы не блокировать асинхронность
        await asyncio.to_thread(self.play_audio, audio)
    
    async def speak_duet(self, text, main_voice="chuchu"):
        """Озвучивает реплику дуэтом (чередуя голоса)"""
        await self.speak(text, voice=main_voice)