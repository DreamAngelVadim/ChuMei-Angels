"""
Модуль распознавания пользователя по голосу
"""
import os
import numpy as np
import torch
import torchaudio

_model = None

def _get_model():
    global _model
    if _model is None:
        print("🎤 Загружаю модель распознавания голоса...")
        try:
            from speechbrain.inference.speaker import SpeakerRecognition
            _model = SpeakerRecognition.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir="tmp_speechbrain"
            )
            print("✅ Модель голоса загружена")
        except Exception as e:
            print(f"⚠️ Ошибка загрузки модели: {e}")
            _model = None
    return _model


def get_voice_embedding(audio_path: str) -> np.ndarray:
    """Получает вектор голоса из аудиофайла."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Аудиофайл не найден: {audio_path}")
    
    model = _get_model()
    if model is None:
        raise RuntimeError("Модель распознавания не загружена")
    
    try:
        # Загружаем аудио
        signal, fs = torchaudio.load(audio_path)
        
        # Ресемплируем до 16kHz если нужно
        if fs != 16000:
            import torchaudio.transforms as T
            resampler = T.Resample(fs, 16000)
            signal = resampler(signal)
            fs = 16000
        
        # Получаем эмбеддинг
        embedding = model.encode_batch(signal)
        
        # Возвращаем как numpy array
        return embedding.squeeze().cpu().numpy()
    
    except Exception as e:
        print(f"⚠️ Ошибка получения эмбеддинга: {e}")
        raise


def compare_voices(audio_file: str, reference_file: str, threshold: float = 0.5) -> bool:
    """Сравнивает голос из файла с образцом."""
    try:
        emb1 = get_voice_embedding(audio_file)
        emb2 = get_voice_embedding(reference_file)
        similarity = compare_embeddings(emb1, emb2)
        print(f"🎤 Схожесть голосов: {similarity:.3f} (порог: {threshold})")
        return similarity >= threshold
    except Exception as e:
        print(f"⚠️ Ошибка сравнения голосов: {e}")
        return False


def compare_embeddings(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """Сравнивает два вектора голоса и возвращает косинусное расстояние."""
    # Нормализуем векторы
    emb1_norm = emb1 / np.linalg.norm(emb1)
    emb2_norm = emb2 / np.linalg.norm(emb2)
    
    # Косинусное сходство
    similarity = np.dot(emb1_norm, emb2_norm)
    
    # Преобразуем в расстояние (1 - similarity)
    distance = 1 - similarity
    
    return distance


def compare_embeddings_bool(emb1: np.ndarray, emb2: np.ndarray, threshold: float = 0.5) -> bool:
    """Сравнивает два вектора голоса и возвращает True/False."""
    distance = compare_embeddings(emb1, emb2)
    print(f"🎤 Distance: {distance:.3f} (порог: {threshold})")
    return distance < threshold