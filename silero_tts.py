import torch
import numpy as np
import scipy.io.wavfile as wav
import asyncio
import pygame
import tempfile
import os

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
            "hana": {"speaker": "xenia", "rate": 1.18},
            "ki": {"speaker": "baya", "rate": 0.87},
            "simone": {"speaker": "baya", "rate": 0.95},
        }
        
        # Инициализация pygame для воспроизведения
        pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
        
        # Кэш для аудио
        self.audio_cache = {}
    
    def generate_audio(self, text, voice="chuchu"):
        """Генерирует аудио из текста"""
        cfg = self.VOICE_CONFIG.get(voice, self.VOICE_CONFIG["chuchu"])
        
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
            audio = self.model.apply_tts(
                text=text,
                speaker=cfg["speaker"],
                sample_rate=self.sample_rate
            )
            return audio.cpu().numpy()
    
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