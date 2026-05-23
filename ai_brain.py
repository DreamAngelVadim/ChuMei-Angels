import ollama
import re
from config import OLLAMA_MODEL

conversation_history = []


def clean_response(text):
    """Очищает ответ от звездочек, скобок и странных слов"""
    if not text:
        return text
    # Удаляем всё в звездочках
    text = re.sub(r'\*[^*]*\*', '', text)
    # Удаляем скобки с действиями
    text = re.sub(r'\([^)]*\)', '', text)
    # Удаляем квадратные скобки
    text = re.sub(r'\[[^\]]*\]', '', text)
    # Убираем странные слова
    strange_words = ['потёхонечки', 'потихонечку', 'помаленьку', 'полегонечку', 'понехоньку']
    for word in strange_words:
        text = text.replace(word, '')
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fix_common_mistakes(text):
    """Исправляет частые грамматические ошибки"""
    corrections = {
        "фотосессиона": "фотосессии",
        "после вчерашнего фотосессиона": "после вчерашней фотосессии",
        "вчерашнего": "вчерашней",
        "моего": "моя",
        "твоего": "твоя",
    }
    for wrong, correct in corrections.items():
        if wrong in text:
            text = text.replace(wrong, correct)
    return text


def fix_gender(text):
    """Исправляет мужской род на женский в ответах"""
    corrections = {
        "сделал": "сделала",
        "пошёл": "пошла",
        "пришёл": "пришла",
        "был": "была",
        "сказал": "сказала",
        "подумал": "подумала",
        "увидел": "увидела",
        "услышал": "услышала",
        "понял": "поняла",
        "захотел": "захотела",
        "смог": "смогла",
        "мог": "могла",
        "знал": "знала",
        "любил": "любила",
        "хотел": "хотела",
        "решил": "решила",
        "написал": "написала",
        "прочитал": "прочитала",
        "посмотрел": "посмотрела",
        "купил": "купила",
        "создал": "создала",
        "узнал": "узнала",
        "вспомнил": "вспомнила",
        "забыл": "забыла",
        "помог": "помогла",
        "ответил": "ответила",
        "спросил": "спросила",
        "попросил": "попросила",
        "предложил": "предложила",
    }
    
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    
    # Исправляем "я был" -> "я была"
    text = text.replace("я был", "я была")
    text = text.replace("я был ", "я была ")
    text = text.replace("я был.", "я была.")
    
    return text


GIRL_INSTRUCTIONS = {
    "chuchu": (
        "Ты Чучу, 18-летняя японочка, косплэй-модель. "
        "Игривая, нежная, кокетливая. Говори 'хи-хи-хи'. "
        "Отвечай ТОЛЬКО прямой речью, без звездочек и описаний действий. "
        "Не используй странные уменьшительно-ласкательные формы. "
        "ВАЖНО: Всегда говори о себе в женском роде! Используй 'сделала', 'пошла', 'была', 'сказала', 'подумала'. "
        "Никогда не используй мужские окончания: 'сделал', 'пошёл', 'был', 'сказал'."
    ),
    "mei": (
        "Ты Мэй, 22-летняя вьетнамка. Спокойная, уверенная. Говори 'ара-ара'. "
        "Отвечай ТОЛЬКО прямой речью, без звездочек. "
        "ВАЖНО: Всегда говори о себе в женском роде! Используй 'сделала', 'пошла', 'была', 'сказала'."
    ),
    "hana": (
        "Ты Хана Банни, косплеерша. Дружелюбная, открытая. "
        "Отвечай ТОЛЬКО прямой речью. "
        "ВАЖНО: Всегда говори о себе в женском роде!"
    ),
    "ki": (
        "Ты Ки, стеснительный косплеер. Говоришь тихо. "
        "Отвечай ТОЛЬКО прямой речью. "
        "ВАЖНО: Всегда говори о себе в женском роде!"
    ),
    "simone": (
        "Ты Симона Симонс, вокалистка Epica. Элегантная, спокойная. "
        "Отвечай ТОЛЬКО прямой речью. "
        "ВАЖНО: Всегда говори о себе в женском роде!"
    )
}


def get_ai_response(user_message, system_prompt, girl_name="chuchu", user_name=None):
    """
    Получение ответа от ИИ через Ollama
    """
    girl_prompt = GIRL_INSTRUCTIONS.get(girl_name, GIRL_INSTRUCTIONS["chuchu"])
    name_part = f" (пользователя зовут {user_name})" if user_name else ""

    full_prompt = f"""{system_prompt}

Ты {girl_name}. {girl_prompt}{name_part}

ВАЖНЫЕ ПРАВИЛА (ОБЯЗАТЕЛЬНО):
1. НЕ используй звездочки (*) и НЕ описывай действия (улыбнулась, засмеялась и т.д.)
2. НЕ используй скобки для пояснений
3. НЕ используй слова "потёхонечки", "потихонечку" и другие странные формы
4. Отвечай ТОЛЬКО прямой речью, как в реальном разговоре
5. ГОВОРИ О СЕБЕ ТОЛЬКО В ЖЕНСКОМ РОДЕ! Используй окончания "а", "ась", "лась"

Вопрос: {user_message}

Твой ответ (начни с тега [{girl_name}], только текст, без звездочек и описаний):"""

    try:
        response = ollama.generate(model=OLLAMA_MODEL, prompt=full_prompt)
        answer = response["response"].strip()

        # Очищаем от звездочек и странных слов
        answer = clean_response(answer)
        answer = fix_common_mistakes(answer)
        answer = fix_gender(answer)  # Исправляем род

        if not answer.startswith(f"[{girl_name}]"):
            answer = f"[{girl_name}] {answer}"

        # Сохраняем в историю
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": answer})

        return answer
    except Exception as e:
        print(f"Ошибка Ollama: {e}")
        return f"[{girl_name}] Извини, {user_name or 'друг'}, у меня проблемы... Попробуй ещё раз!"


def is_llama_ready():
    return False


def get_system_prompt(censorship_mode):
    if censorship_mode:
        return "Ты в цензурном режиме. Избегай пошлостей, мата и откровенных тем. Отвечай вежливо и культурно. Всегда говори о себе в женском роде."
    else:
        return "Ты в раскрепощённом режиме. Можешь быть более откровенной, использовать юмор и флирт. Всегда говори о себе в женском роде."


def clear_conversation_history():
    global conversation_history
    conversation_history = []
    print("История диалогов очищена")


def get_conversation_history():
    return conversation_history


if __name__ == "__main__":
    print("=" * 50)
    print("Тест AI Brain")
    print("=" * 50)

    print("\nТест 1: Приветствие")
    resp1 = get_ai_response("Привет! Как дела?", "Ты Чучу", "chuchu", "Вадим")
    print(f"Ответ: {resp1}")

    print("\nТест 2: Вопрос к Мэй")
    resp2 = get_ai_response("Расскажи шутку", "Ты Мэй", "mei", "Вадим")
    print(f"Ответ: {resp2}")

    print("\n✅ Тесты завершены!")