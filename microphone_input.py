"""
Модуль захвата речи с микрофона
Оптимизирован для распознавания только человеческой речи
"""

import speech_recognition as sr
import time
import logging
import numpy as np

logger = logging.getLogger(__name__)


class SpeechListener:
    """Класс для управления микрофоном с умной активацией"""
    
    def __init__(self):
        self.microphone = None
        self.recognizer = None
        self.is_listening = False
        
        # Настройки для распознавания речи
        self.energy_threshold = 300
        self.dynamic_energy_threshold = True
        self.dynamic_energy_adjustment_damping = 0.15
        self.dynamic_energy_ratio = 1.5
        self.pause_threshold = 0.8
        self.phrase_threshold = 0.3
        self.non_speaking_duration = 0.5
        
        # Минимальная длина фразы для распознавания
        self.min_phrase_length = 3  # минимум 3 символа
        
        # Калибровка шума (один раз при запуске)
        self.calibrated = False
    
    def _ensure_microphone(self):
        """Подключает микрофон и калибрует шум"""
        if self.microphone is None:
            try:
                self.microphone = sr.Microphone()
                self.recognizer = sr.Recognizer()
                
                # Настройки
                self.recognizer.energy_threshold = self.energy_threshold
                self.recognizer.dynamic_energy_threshold = self.dynamic_energy_threshold
                self.recognizer.dynamic_energy_adjustment_damping = self.dynamic_energy_adjustment_damping
                self.recognizer.dynamic_energy_ratio = self.dynamic_energy_ratio
                self.recognizer.pause_threshold = self.pause_threshold
                self.recognizer.phrase_threshold = self.phrase_threshold
                self.recognizer.non_speaking_duration = self.non_speaking_duration
                
                # Калибровка шума (важно!)
                if not self.calibrated:
                    print("🎤 Калибровка микрофона... Говорите в обычном темпе")
                    with self.microphone as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=2)
                        self.energy_threshold = self.recognizer.energy_threshold
                        print(f"   Порог шума: {self.energy_threshold}")
                        self.calibrated = True
                
                print("🎤 Микрофон готов")
            except Exception as e:
                print(f"❌ Ошибка микрофона: {e}")
                self.microphone = None
                self.recognizer = None
    
    def _is_speech_likely(self, audio_data) -> bool:
        """
        Анализирует аудио и определяет, похоже ли оно на речь
        Использует простые эвристики: энергия, длительность, частота
        """
        try:
            # Конвертируем в numpy массив для анализа
            audio_np = np.frombuffer(audio_data.get_wav_data(), dtype=np.int16)
            
            # Вычисляем RMS (среднеквадратичное значение)
            rms = np.sqrt(np.mean(audio_np.astype(np.float32)**2))
            
            # Речь обычно имеет RMS > 500
            if rms < 500:
                return False
            
            # Проверяем длительность (речь обычно длится > 0.5 сек)
            duration = len(audio_np) / 16000  # sample_rate=16000
            if duration < 0.5:
                return False
            
            return True
        except:
            return True  # Если не можем проанализировать, считаем речью
    
    def listen(self, timeout=5):
        """
        Слушает микрофон.
        Возвращает: (текст, была_активность)
        """
        self._ensure_microphone()
        
        if self.microphone is None:
            return "", False
        
        try:
            with self.microphone as source:
                # Короткая адаптация к текущему шуму
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                print("🎤 Слушаю...", end=" ", flush=True)
                
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
                    
                    # Проверяем, похоже ли на речь
                    if not self._is_speech_likely(audio):
                        print("🔇")
                        return "", False
                    
                    print("🎧", end=" ", flush=True)
                    
                    try:
                        text = self.recognizer.recognize_google(audio, language="ru-RU")
                        
                        # Проверяем длину распознанного текста
                        if len(text.strip()) < self.min_phrase_length:
                            print(f"📝 '{text}' (слишком коротко)")
                            return "", True
                        
                        print(f"📝 {text}")
                        return text.lower(), True
                        
                    except sr.UnknownValueError:
                        print("❌ Не разобрал")
                        return "", True  # Активность была, но не распознали
                        
                    except sr.RequestError as e:
                        print(f"❌ Ошибка сервиса: {e}")
                        return "", True
                        
                except sr.WaitTimeoutError:
                    print("⌛", end=" ", flush=True)
                    return "", False  # Тишина
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return "", False


# Глобальный экземпляр
_listener = SpeechListener()


def listen(timeout=5):
    """Возвращает (текст, была_активность)"""
    return _listener.listen(timeout=timeout)