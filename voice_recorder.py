"""
Запись голоса в WAV-файл для идентификации
"""
import sounddevice as sd
import numpy as np
import soundfile as sf
import tempfile
import os

def record_voice(duration: float = 3.0, sample_rate: int = 16000) -> str:
    """
    Записывает голос с микрофона и сохраняет в WAV-файл.
    
    Args:
        duration: длительность записи в секундах
        sample_rate: частота дискретизации
    
    Returns:
        путь к временному WAV-файлу
    """
    print(f"🎤 Запись голоса... Говорите {duration} секунд")
    
    try:
        # Записываем аудио
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Ждём окончания записи
        
        print("✅ Запись завершена")
        
        # Сохраняем во временный файл
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = temp_file.name
        temp_file.close()
        
        sf.write(temp_path, recording, sample_rate)
        print(f"💾 Аудио сохранено: {temp_path}")
        
        return temp_path
    
    except Exception as e:
        print(f"❌ Ошибка записи голоса: {e}")
        raise


def record_voice_interactive() -> str:
    """
    Интерактивная запись с обратным отсчётом
    """
    import time
    
    print("\n🎙️ Готовимся к записи голоса...")
    time.sleep(0.5)
    
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("🎤 ГОВОРИТЕ СЕЙЧАС!")
    return record_voice(duration=3.0)