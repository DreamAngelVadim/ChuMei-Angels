"""
Тест произношения слов "тестовая" и "косплей" через TTS
"""

import asyncio
from silero_tts import SileroTTS
from accent_helper import accent_helper

async def test_pronunciation():
    print("=" * 60)
    print("Тест произношения через TTS")
    print("=" * 60)
    
    tts = SileroTTS()
    
    # Список тестовых фраз
    test_phrases = [
        "тестовая фраза",
        "это тестовая проверка",
        "Я люблю косплей",
        "косплей и модель",
        "Привет, это тестовая фраза про косплей",
    ]
    
    print("\n🔊 Озвучиваю тестовые фразы:\n")
    
    for phrase in test_phrases:
        # Обрабатываем ударения
        processed = accent_helper.process(phrase)
        print(f"📝 Текст: {phrase}")
        print(f"📊 С ударениями: {processed}")
        print(f"🔊 Озвучивание: ", end="", flush=True)
        
        # Озвучиваем
        await tts.speak(phrase, voice="xenia")
        print(" ✅")
        print("-" * 40)
        await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ Тест завершён")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_pronunciation())