"""
Модуль расстановки запятых по правилам русского языка
"""
import re


class RuPunctuator:
    def __init__(self):
        print("Модуль пунктуации готов!")

    def add_punctuation(self, text: str) -> str:
        """Базовая расстановка запятых."""
        if not text or not text.strip():
            return text

        # Запятая перед союзами
        text = re.sub(
            r'\s+(что|чтобы|если|когда|потому что|так как|поскольку|хотя|пока|как|где|куда|откуда|зачем|почему|чей|кто)\s+',
            r', \1 ', text, flags=re.IGNORECASE
        )

        # Запятая перед "а", "но", "да", "однако", "зато"
        text = re.sub(
            r'\s+(а|но|да|однако|зато)\s+',
            r', \1 ', text, flags=re.IGNORECASE
        )

        # Запятая перед "который", "которая", "которое", "которые"
        text = re.sub(
            r'\s+(который|которая|которое|которые|которых|которым|которыми)\s+',
            r', \1 ', text, flags=re.IGNORECASE
        )

        # Убираем двойные запятые
        text = re.sub(r',\s*,', ',', text)
        # Убираем запятую в начале строки
        text = re.sub(r'^,\s*', '', text)

        return text