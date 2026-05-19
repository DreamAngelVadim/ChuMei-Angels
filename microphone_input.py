"""
Модуль захвата речи с микрофона
"""

import speech_recognition as sr


def listen(timeout=5):
    """
    Слушает микрофон и возвращает распознанный текст.
    
    Аргументы:
        timeout: максимальное время ожидания речи (секунды)
    
    Возвращает:
        Распознанный текст или пустую строку
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 500
    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold = 1.0
    
    try:
        with sr.Microphone() as source:
            print("🎤 Слушаю...", end=" ", flush=True)
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
                print("✅")
                
                try:
                    text = recognizer.recognize_google(audio, language="ru-RU")
                    return text.lower()
                except sr.UnknownValueError:
                    print("❌ Не распознано")
                    return ""
                except sr.RequestError as e:
                    print(f"❌ Ошибка сервиса: {e}")
                    return ""
                    
            except sr.WaitTimeoutError:
                print("⌛ Таймаут")
                return ""
                
    except Exception as e:
        print(f"❌ Ошибка микрофона: {e}")
        return ""


def listen_with_timeout(timeout=5):
    """
    Обёртка для listen с таймаутом (для совместимости).
    
    Аргументы:
        timeout: максимальное время ожидания речи (секунды)
    
    Возвращает:
        Распознанный текст или пустую строку
    """
    return listen(timeout=timeout)