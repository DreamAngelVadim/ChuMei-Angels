# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),           # Вся папка с видео, аватарками, фото
        ('Asian.ico', '.'),             # Иконка
        ('user_name.txt', '.'),         # Файл с именем (если есть)
    ],
    hiddenimports=[
        'omegaconf',
        'torch',
        'torchaudio',
        'scipy',
        'customtkinter',
        'cv2',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'pygame',
        'numpy',
        'speechrecognition',
        'pyaudio',
        'ollama',
        'transliterate',
        'pywinstyles',
        'silero_tts',
        'ai_brain',
        'microphone_input',
        'text_utils',
        'link_chat',
        'voice_id',
        'voice_recorder',
        'memory',
        'accent_helper',
        'punctuator',
        'replacements',
        'knowledge.cosplay',
        'knowledge.music',
        'knowledge.dialogues',
        'knowledge.personality',
        'knowledge.chains',
        'knowledge.story_arc',
        'photo_gallery',               # ← добавить фотоальбом
        'clipboard_helper',            # ← добавить буфер обмена
        'undo_history',                # ← добавить историю отмены
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ChuMei Angels',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # ← поставь True для отладки, потом False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['Asian.ico'],
)