import re

def clean_text(text):
    """Базовая очистка текста"""
    if not text:
        return ""
    text = re.sub(r'\[[a-z]+\]', '', text)
    text = re.sub(r'\[/[a-z]+\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def convert_number_to_words(num):
    """Число в слова (0-9999)"""
    if num == 0:
        return "ноль"
    
    simple = {
        1: "один", 2: "два", 3: "три", 4: "четыре", 5: "пять",
        6: "шесть", 7: "семь", 8: "восемь", 9: "девять", 10: "десять",
        11: "одиннадцать", 12: "двенадцать", 13: "тринадцать", 14: "четырнадцать",
        15: "пятнадцать", 16: "шестнадцать", 17: "семнадцать", 18: "восемнадцать",
        19: "девятнадцать"
    }
    
    tens = {
        20: "двадцать", 30: "тридцать", 40: "сорок", 50: "пятьдесят",
        60: "шестьдесят", 70: "семьдесят", 80: "восемьдесят", 90: "девяносто"
    }
    
    hundreds = {
        100: "сто", 200: "двести", 300: "триста", 400: "четыреста",
        500: "пятьсот", 600: "шестьсот", 700: "семьсот", 800: "восемьсот", 900: "девятьсот"
    }
    
    thousands = {
        1: "одна тысяча", 2: "две тысячи", 3: "три тысячи", 4: "четыре тысячи",
        5: "пять тысяч", 6: "шесть тысяч", 7: "семь тысяч", 8: "восемь тысяч", 9: "девять тысяч"
    }
    
    if num in simple:
        return simple[num]
    
    if num < 100:
        t = (num // 10) * 10
        u = num % 10
        result = tens[t]
        if u > 0:
            result += " " + simple[u]
        return result
    
    if num < 1000:
        h = (num // 100) * 100
        r = num % 100
        result = hundreds[h]
        if r > 0:
            result += " " + convert_number_to_words(r)
        return result
    
    if num < 10000:
        th = num // 1000
        r = num % 1000
        if th in thousands:
            result = thousands[th]
        else:
            result = convert_number_to_words(th) + " тысяч"
        if r > 0:
            result += " " + convert_number_to_words(r)
        return result
    
    return str(num)

def normalize_text_for_tts(text):
    """Подготовка текста для TTS"""
    if not text:
        return ""
    text = clean_text(text)
    
    # Замена чисел
    def replace_num(m):
        try:
            return convert_number_to_words(int(m.group()))
        except:
            return m.group()
    
    text = re.sub(r'\b\d{1,4}\b', replace_num, text)
    
    # Базовые замены имён
    names = {
        'Chu': 'Чу', 'chu': 'чу',
        'Mei': 'Мэй', 'mei': 'мэй',
        'Hana': 'Хана', 'hana': 'хана',
        'Ki': 'Ки', 'ki': 'ки',
        'Simone': 'Симона', 'simone': 'симона'
    }
    
    for eng, rus in names.items():
        text = text.replace(eng, rus)
    
    return text