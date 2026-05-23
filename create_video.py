import cv2
import numpy as np
import os

# Создаём папку если нет
os.makedirs("assets/video", exist_ok=True)

def create_video(path, color, text, duration=5):
    fps = 30
    width, height = 400, 400
    total_frames = duration * fps
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(path, fourcc, fps, (width, height))
    
    for i in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = color
        
        # Пульсирующий эффект
        pulse = int(50 * np.sin(i * 0.1))
        frame = frame + pulse
        frame = np.clip(frame, 0, 255)
        
        # Текст
        cv2.putText(frame, text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (255, 255, 255), 2, cv2.LINE_AA)
        
        out.write(frame)
    
    out.release()
    print(f"✅ Создано: {path}")

# Проверяем установку OpenCV
try:
    create_video("assets/video/idle.mp4", (100, 100, 200), "ChuMei Angels", duration=10)
    create_video("assets/video/talking.mp4", (200, 100, 100), "Talking...", duration=5)
    print("\n✅ Видео успешно созданы!")
    print("   - assets/video/idle.mp4")
    print("   - assets/video/talking.mp4")
except ImportError:
    print("❌ OpenCV не установлен!")
    print("   Установите: pip install opencv-python")