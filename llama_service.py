"""
Сервис для работы с Q8_0 моделью через llama.cpp
"""

from llama_cpp import Llama
import os

print("Загрузка llama_service...")

class LlamaService:
    def __init__(self, model_path="models/llama.gguf"):
        self.llm = None
        self.model_path = model_path
        if os.path.exists(self.model_path):
            self._load_model()
        else:
            print(f"Модель не найдена: {self.model_path}")

    def _load_model(self):
        try:
            size_mb = os.path.getsize(self.model_path) / (1024 * 1024)
            print(f"Загрузка: {self.model_path} ({size_mb:.0f} MB)")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0,
                verbose=False
            )
            print("Модель загружена!")
        except Exception as e:
            print(f"Ошибка: {e}")

    def generate(self, prompt, max_tokens=150, temperature=0.7):
        if not self.llm:
            return None
        try:
            output = self.llm(prompt, max_tokens=max_tokens, temperature=temperature, echo=False)
            return output['choices'][0]['text'].strip()
        except Exception as e:
            print(f"Ошибка генерации: {e}")
            return None

    def is_ready(self):
        return self.llm is not None

print("Создаём экземпляр...")
llama_service = LlamaService()
print("Готово!")

if __name__ == "__main__":
    print("Тест:")
    if llama_service.is_ready():
        resp = llama_service.generate("Скажи Привет", max_tokens=5)
        print(f"Ответ: {resp}")
    else:
        print("Модель не загружена")
