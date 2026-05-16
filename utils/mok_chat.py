import asyncio
import os
from typing import Callable, Union

class MokChatBot:
    def __init__(self, path: str, message_callback: Callable[[str, str], None]):
        self.path = path
        self.message_callback = message_callback
        self.is_running = False
        self.last_mtime = 0
        self.processed_messages = set()

    def get_new_messages(self) -> list:
        """Читает новые сообщения из файла"""
        try:
            current_mtime = os.path.getmtime(self.path)
            
            if current_mtime <= self.last_mtime:
                return []
            
            self.last_mtime = current_mtime
            
            with open(self.path, 'r', encoding='utf-8') as file:
                all_messages = file.readlines()
            
            return [msg.strip() for msg in all_messages if msg.strip()]
            
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")
            return []

    async def process_messages(self, messages: list):
        """Асинхронно обрабатывает сообщения"""
        for message in messages:
            if message and not message.startswith('#'):
                msg_hash = hash(message)
                
                if msg_hash not in self.processed_messages:
                    self.processed_messages.add(msg_hash)
                    
                    if ':' in message:
                        username, text = message.split(':', 1)
                        username = username.strip()
                        text = text.strip()
                    else:
                        username = "user"
                        text = message
                    
                    if text:
                        print(f"💬 [{username}]: {text}")
                        # Асинхронный вызов callback
                        await self._call_callback(username, text)

    async def _call_callback(self, username: str, text: str):
        """Асинхронно вызывает callback"""
        try:
            # Проверяем является ли callback асинхронной функцией
            if asyncio.iscoroutinefunction(self.message_callback):
                await self.message_callback(username, text)
            else:
                # Если синхронная функция - запускаем в executor
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, self.message_callback, username, text
                )
        except Exception as e:
            print(f"❌ Ошибка в callback: {e}")

    async def start(self):
        """Запускает бота"""
        self.is_running = True
        if os.path.exists(self.path):
            os.remove(self.path)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write("# Файл чата\n# Формат: username: сообщение\n\n")
                
        print(f"📖 Мок-бот запущен. Чтение из: {self.path}")
        print("💡 Добавляйте сообщения в файл в реальном времени!")
        
        try:
            self.last_mtime = os.path.getmtime(self.path)
        except:
            self.last_mtime = 0
        
        try:
            while self.is_running:
                messages = self.get_new_messages()
                if messages:
                    await self.process_messages(messages)
                await asyncio.sleep(0.5)
        except KeyboardInterrupt:
            print("\n🛑 Остановка мок-бота...")
        except Exception as e:
            print(f"❌ Ошибка в мок-боте: {e}")
        finally:
            self.is_running = False

    def stop(self):
        """Останавливает бота"""
        self.is_running = False

async def start_mok_bot(message_callback: Callable[[str, str], None], path: str = 'chat.txt') -> MokChatBot:
    """
    Запускает мок-бота
    
    Args:
        message_callback: Функция для обработки сообщений (может быть async или sync)
        path: Путь к файлу с сообщениями
        
    Returns:
        MokChatBot instance
    """
    bot = MokChatBot(path, message_callback)
    return bot