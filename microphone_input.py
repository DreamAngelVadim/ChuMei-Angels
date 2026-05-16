"""
Модуль захвата речи с микрофона (улучшенный v2)
"""
import speech_recognition as sr


def listen():
    """Слушает микрофон и возвращает распознанный текст."""
    r = sr.Recognizer()
    
    # Настройки
    r.pause_threshold = 2.0       # 2 секунды тишины — конец фразы
    r.phrase_threshold = 0.2      # Низкий порог начала речи
    r.non_speaking_duration = 0.8 # Терпим паузы внутри фразы
    r.energy_threshold = 150      # Чувствительность
    r.dynamic_energy_threshold = True  # Автоподстройка
    
    with sr.Microphone() as source:
        # Быстрая адаптация — всего 1 секунда
        r.adjust_for_ambient_noise(source, duration=1)
        
        try:
            # Слушаем фразу
            audio = r.listen(source, timeout=8, phrase_time_limit=20)
            text = r.recognize_google(audio, language="ru-RU")
            print(f"Вы: {text}")
            return text.lower()
            
        except sr.UnknownValueError:
            print("Не расслышала...")
            return None
        except sr.RequestError:
            print("Нет интернета для распознавания речи")
            return None
        except sr.WaitTimeoutError:
            print("Слишком долго тишины...")
            return None
        except Exception as e:
            print(f"Ошибка записи: {e}")
            return None