"""
Запись голоса в WAV-файл для идентификации
"""
import sounddevice as sd
import numpy as np
import soundfile as sf


def record_voice(duration: int = 5, sample_rate: int = 16000) -> str:
    """
    Записывает голос с микрофона и сохраняет в WAV-файл.
    Возвращает путь к файлу.
    """
    import tempfile
    
    print(f"Запись {duration} секунд... Говорите!")
    
    # Записываем аудио
    recording = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    # Сохраняем во временный файл
    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
    sf.write(temp_path, recording.flatten(), sample_rate)
    
    print(f"Запись сохранена: {temp_path}")
    return temp_path