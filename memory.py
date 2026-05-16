import json
import os
from datetime import datetime

class Memory:
    def __init__(self, knowledge_dir="knowledge/girls"):
        self.knowledge_dir = knowledge_dir
        os.makedirs(knowledge_dir, exist_ok=True)
    
    def _get_file_path(self, girl_name, file_type):
        return f"{self.knowledge_dir}/{girl_name}/{file_type}.json"
    
    def _ensure_valid_file(self, path, girl_name):
        """Проверяет, что файл существует и содержит валидный JSON"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
                    return data
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Создаём новый валидный файл
        data = {
            "name": girl_name,
            "created": datetime.now().isoformat(),
            "learning_mode": False,
            "facts": []
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return data
    
    def save_fact(self, girl_name, fact):
        path = self._get_file_path(girl_name, "brain")
        data = self._ensure_valid_file(path, girl_name)
        
        data["facts"].append({
            "id": len(data["facts"]) + 1,
            "text": fact,
            "timestamp": datetime.now().isoformat(),
            "source": "user"
        })
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
    
    def get_facts(self, girl_name, limit=10):
        path = self._get_file_path(girl_name, "brain")
        data = self._ensure_valid_file(path, girl_name)
        facts = [f["text"] for f in data.get("facts", [])[-limit:]]
        return facts
    
    def set_learning_mode(self, girl_name, enabled):
        path = self._get_file_path(girl_name, "brain")
        data = self._ensure_valid_file(path, girl_name)
        data["learning_mode"] = enabled
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return enabled
    
    def get_learning_mode(self, girl_name):
        path = self._get_file_path(girl_name, "brain")
        data = self._ensure_valid_file(path, girl_name)
        return data.get("learning_mode", False)