"""
Тест двуязычного TTS
"""

import asyncio
from silero_tts import SileroTTS

async def test():
    tts = SileroTTS()
    
    print("\n" + "=" * 50)
    print("Тест русского и английского произношения")
    print("=" * 50)
    
    # Русский тест
    print("\n1. Русский текст (Чучу):")
    await tts.speak_chuchu("Привет! Это тестовая фраза про косплей и модель.")
    
    await asyncio.sleep(1)
    
    # Английский тест
    print("\n2. Английский текст:")
    await tts.speak_english("Hello! This is an English test phrase.")
    
    await asyncio.sleep(1)
    
    # Смешанный тест
    print("\n3. Смешанный текст (должна быть русская модель):")
    await tts.speak_chuchu("Я люблю косплей. And I love English too!")
    
    print("\n" + "=" * 50)
    print("✅ Тест завершён")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test())