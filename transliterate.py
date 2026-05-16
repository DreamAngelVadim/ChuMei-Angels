"""
Автоматическая транслитерация английских слов в русскую транскрипцию
"""
import re


# Таблица транслитерации
TRANSLIT_TABLE = {
    'a': 'э', 'b': 'б', 'c': 'к', 'd': 'д', 'e': 'е', 'f': 'ф',
    'g': 'г', 'h': 'х', 'i': 'и', 'j': 'дж', 'k': 'к', 'l': 'л',
    'm': 'м', 'n': 'н', 'o': 'о', 'p': 'п', 'q': 'к', 'r': 'р',
    's': 'с', 't': 'т', 'u': 'у', 'v': 'в', 'w': 'в', 'x': 'кс',
    'y': 'и', 'z': 'з',
    'A': 'Э', 'B': 'Б', 'C': 'К', 'D': 'Д', 'E': 'Е', 'F': 'Ф',
    'G': 'Г', 'H': 'Х', 'I': 'И', 'J': 'Дж', 'K': 'К', 'L': 'Л',
    'M': 'М', 'N': 'Н', 'O': 'О', 'P': 'П', 'Q': 'К', 'R': 'Р',
    'S': 'С', 'T': 'Т', 'U': 'У', 'V': 'В', 'W': 'В', 'X': 'Кс',
    'Y': 'И', 'Z': 'З',
}

# Особые сочетания
SPECIAL_COMBOS = {
    'sh': 'ш', 'ch': 'ч', 'th': 'з', 'ph': 'ф', 'wh': 'в',
    'ck': 'к', 'gh': '', 'ng': 'нг', 'qu': 'кв',
    'ee': 'и', 'oo': 'у', 'ea': 'и', 'ou': 'ау', 'ow': 'оу',
    'ay': 'эй', 'ey': 'ей', 'oy': 'ой', 'aw': 'о',
    'tion': 'шн', 'sion': 'жн',
    'Sh': 'Ш', 'Ch': 'Ч', 'Th': 'З', 'Ph': 'Ф', 'Wh': 'В',
    'Ck': 'К', 'Gh': '', 'Ng': 'Нг', 'Qu': 'Кв',
    'Ee': 'И', 'Oo': 'У', 'Ea': 'И', 'Ou': 'Ау', 'Ow': 'Оу',
    'Ay': 'Эй', 'Ey': 'Ей', 'Oy': 'Ой', 'Aw': 'О',
    'Tion': 'Шн', 'Sion': 'Жн',
}


def transliterate(text: str) -> str:
    """Переводит английские слова в русскую транскрипцию."""
    # Находим английские слова (латиница)
    def replace_english(match):
        word = match.group(0)
        # Если слово короткое (предлог, артикль) — пропускаем
        if len(word) <= 2 and word.lower() in ['a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'by', 'is', 'it']:
            return word
        
        # Применяем особые сочетания сначала
        for combo, replacement in sorted(SPECIAL_COMBOS.items(), key=lambda x: -len(x[0])):
            word = word.replace(combo, replacement)
        
        # Применяем побуквенную транслитерацию
        result = []
        for char in word:
            if char in TRANSLIT_TABLE:
                result.append(TRANSLIT_TABLE[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    # Заменяем все английские слова
    text = re.sub(r'[a-zA-Z]{2,}', replace_english, text)
    
    return text