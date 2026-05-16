import torch

model, _ = torch.hub.load('snakers4/silero-models', 'silero_tts', language='ru', speaker='v5_4_ru')
print("Доступные голоса:", model.speakers)