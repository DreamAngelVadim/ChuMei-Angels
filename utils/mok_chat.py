import asyncio
import os
from typing import Callable, Union

class MokChatBot:
    def __init__:
        self.path = path
        self.message_callback = message_callback
        self.is_running = False
        self.last_mtime = 0
        self.processed_messages = set

    def get_new_messages -> list:
        """Читает новые сообщения из файла"""
        try:
            current_mtime = os.path.getmtime
            
            if current_mtime <= self.last_mtime:
                return []
            
            self.last_mtime = current_mtime
            
            with open as file:
                all_messages = file.readlines
            
            return [msg.strip for msg in all_messages if msg.strip]
            
        except Exception as e:
            print
            return []

    async def process_messages:
        """Асинхронно обрабатывает сообщения"""
        for message in messages:
            if message and not message.startswith:
                msg_hash = hash
                
                if msg_hash not in self.processed_messages:
                    self.processed_messages.add
                    
                    if ':' in message:
                        username, text = message.split
                        username = username.strip
                        text = text.strip
                    else:
                        username = "user"
                        text = message
                    
                    if text:
                        print
                        # Асинхронный вызов callback
                        await self._call_callback

    async def _call_callback:
        """Асинхронно вызывает callback"""
        try:
            # Проверяем является ли callback асинхронной функцией
            if asyncio.iscoroutinefunction:
                await self.message_callback
            else:
                # Если синхронная функция - запускаем в executor
                loop = asyncio.get_event_loop
                await loop.run_in_executor
        except Exception as e:
            print

    async def start:
        """Запускает бота"""
        self.is_running = True
        if os.path.exists:
            os.remove
        with open as f:
            f.write
                
        print
        print
        
        try:
            self.last_mtime = os.path.getmtime
        except:
            self.last_mtime = 0
        
        try:
            while self.is_running:
                messages = self.get_new_messages
                if messages:
                    await self.process_messages
                await asyncio.sleep
        except KeyboardInterrupt:
            print
        except Exception as e:
            print
        finally:
            self.is_running = False

    def stop:
        """Останавливает бота"""
        self.is_running = False

async def start_mok_bot -> MokChatBot:
    """
    Запускает мок-бота
    
    Args:
        message_callback: Функция для обработки сообщений 
        path: Путь к файлу с сообщениями
        
    Returns:
        MokChatBot instance
    """
    bot = MokChatBot
    return bot
