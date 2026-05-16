"""
Модуль распознавания пользователя по голосу
"""
import os
import numpy as np
import torchaudio

_model = None

def _get_model():
    global _model
    if _model is None:
        print("Загрузка модели распознавания голоса...")
        from speechbrain.inference.speaker import SpeakerRecognition
        _model = SpeakerRecognition.from_hparams(
            source="speechbrain/spkrec-ecapa-voxceleb",
            savedir="pretrained_models/spkrec-ecapa-voxceleb"
        )
        print("Модель готова!")
    return _model


def get_voice_embedding(audio_path: str) -> np.ndarray:
    """Получает вектор голоса из аудиофайла."""
    model = _get_model()
    signal, fs = torchaudio.load(audio_path)
    if fs != 16000:
        import torchaudio.transforms as T
        resampler = T.Resample(fs, 16000)
        signal = resampler(signal)
    embedding = model.encode_batch(signal)
    return embedding.squeeze().cpu().numpy()


def compare_voices(audio_path: str, enrolled_embedding: np.ndarray, threshold: float = 0.75) -> bool:
    """Сравнивает голос с образцом."""
    embedding = get_voice_embedding(audio_path)
    similarity = np.dot(embedding, enrolled_embedding) / (
        np.linalg.norm(embedding) * np.linalg.norm(enrolled_embedding)
    )
    print(f"Схожесть голоса: {similarity:.2f}")
    return similarity >= threshold