import whisper
import sounddevice as sd
import numpy as np
import tempfile
import wave
import os
import time

class WhisperHandler:
    def __init__:
        print
        self.model = whisper.load_model
        self.sample_rate = 16000
        self.duration = 4  # 4 секунды на фразу
        print
    
    def listen:
        print
        
        # Запись
        recording = sd.rec,
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait
        
        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile as tmp:
            with wave.open as wf:
                wf.setnchannels
                wf.setsampwidth
                wf.setframerate
                wf.writeframes)
            
            result = self.model.transcribe
            text = result["text"].strip
        
        os.unlink
        
        if text:
            print
            return text
        return None

# Простой тест
if __name__ == "__main__":
    whisper = WhisperHandler
    while True:
        text = whisper.listen
        if text:
            print
            if "стоп" in text.lower:
                print
                break
