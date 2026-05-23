import asyncio
from silero_tts import SileroTTS

async def test_eng_voices():
    tts = SileroTTS()
    # Проверьте несколько голосов из списка en_0 ... en_117
    test_voices = ['en_0', 'en_1', 'en_5', 'en_12', 'en_24']
    
    print("Тестирование английских голосов...")
    for voice in test_voices:
        print(f"\n--- Голос: {voice} ---")
        # Используем метод speak_english для генерации
        await tts.speak_english("Hello! This is an English test phrase.", voice=voice)
        await asyncio.sleep(1) # Небольшая пауза между голосами

if __name__ == "__main__":
    asyncio.run(test_eng_voices())