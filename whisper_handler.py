import whisper
import sounddevice as sd
import numpy as np
import tempfile
import wave
import os
import time

class WhisperHandler:
    def __init__(self, model_size="base"):
        print(f"🔄 Загрузка Whisper {model_size}...")
        self.model = whisper.load_model(model_size)
        self.sample_rate = 16000
        self.duration = 4  # 4 секунды на фразу
        print(f"✅ Whisper готов!")
    
    def listen(self):
        print("🎤 Слушаю...")
        
        # Запись
        recording = sd.rec(
            int(self.duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()
        
        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            with wave.open(tmp.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(recording.tobytes())
            
            result = self.model.transcribe(tmp.name, language="ru")
            text = result["text"].strip()
        
        os.unlink(tmp.name)
        
        if text:
            print(f"📝 Распознано: {text}")
            return text
        return None

# Простой тест
if __name__ == "__main__":
    whisper = WhisperHandler()
    while True:
        text = whisper.listen()
        if text:
            print(f"Результат: {text}")
            if "стоп" in text.lower():
                print("Выход...")
                break