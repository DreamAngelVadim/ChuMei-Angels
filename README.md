[README.md](https://github.com/user-attachments/files/27905512/README.md)
# 🎀 ChuMei Angels

**Виртуальный особняк в Сибуе, Токио**  
5 девочек — Чучу, Мэй, Хана, Ки, Симона.  
Голосовое управление, ИИ (Ollama), видео-аватар, случайные цепочки, режим сна и цензуры.

---

## 📦 Требования

- **Python 3.10–3.13**
- **Git** (для клонирования)
- **Ollama** с моделью `llama3.1:8b` (или другой)
- **Микрофон** (для голосовых команд)
- **Web-камера** (необязательно, для видео-аватара)

---

## 🚀 Быстрый старт (для разработки)

 1. Клонируй репозиторий
git clone https://github.com/DreamAngelVadim/ChuMei-Angels.git
cd ChuMei-Angels

# 2. Создай виртуальное окружение (рекомендуется)
python -m venv venv
venv\Scripts\activate

# 3. Установи зависимости
pip install -r requirements.txt

# 4. Запусти приложение
python main.py


pip install pyinstaller


🛠 Сборка EXE (для распространения)
1. Установи PyInstaller


pip install pyinstaller

2. Собери приложение

pyinstaller --onefile --noconsole --name "ChuMei Angels" --icon="assets\Asian.ico" --add-data "assets;assets" --add-data "knowledge;knowledge" main.py



3. Параметр	Что делает
	--onefile	Один .exe файл
	--noconsole	Без консольного окна
	--icon="assets\Asian.ico"	Иконка программы
	--add-data "assets;assets"	Включает папку assets (видео)
	--add-data "knowledge;knowledge"	Включает папку knowledge (диалоги, цепочки)
	Важно: Папка assets должна содержать видео-файлы:
	
	avatar_idle_1.mp4
	
	avatar_talking.mp4
	
4. Результат
	Готовый ChuMei Angels.exe появится в папке dist/
	
	При первом запуске может потребоваться разрешение в брандмауэре
	
5. 📦 Создание установщика (Inno Setup)
	5.1. Скачай Inno Setup
	https://jrsoftware.org/isinfo.php (бесплатно)

	5.2. Создай скрипт .iss
	Скопируй содержимое ниже в файл ChuMei_Angels.iss:	

	[Setup]
	AppName=ChuMei Angels
	AppVersion=1.0
	DefaultDirName={pf}\ChuMei Angels
	DefaultGroupName=ChuMei Angels
	UninstallDisplayIcon={app}\ChuMei Angels.exe
	Compression=lzma2
	SolidCompression=yes
	OutputDir=installer
	OutputBaseFilename=ChuMei_Angels_Setup
	
	[Files]
	Source: "dist\ChuMei Angels.exe"; DestDir: "{app}"
	Source: "assets\*"; DestDir: "{app}\assets"; Flags: recursesubdirs
	Source: "knowledge\*"; DestDir: "{app}\knowledge"; Flags: recursesubdirs
	
	[Icons]
	Name: "{group}\ChuMei Angels"; Filename: "{app}\ChuMei Angels.exe"
	Name: "{group}\Uninstall ChuMei Angels"; Filename: "{uninstallexe}"
	Name: "{commondesktop}\ChuMei Angels"; Filename: "{app}\ChuMei Angels.exe"; Tasks: desktopicon
	
	[Tasks]
	Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"
	
	[Run]
	Filename: "{app}\ChuMei Angels.exe"; Description: "Launch ChuMei Angels"; Flags: postinstall nowait skipifsilent
	
6. Скомпилируй установщик
	Открой ChuMei_Angels.iss в Inno Setup
	
	Нажми Build → Compile (или Ctrl+F9)
	
	Установщик появится в папке installer/
	
7. 🎮 Голосовые команды
	Команда	Действие
	«Расскажи историю»	Полная история вечеринки
	«Скажи бака» / «Скажи кора»	Японские фразы (Чучу/Мэй)
	«Стриптиз за деньги»	Ночная цепочка
	«Спокойной ночи»	Девочки ложатся спать
	«Доброе утро»	Пробуждение
	«Раскрепостись»	NSFW-режим
	«Цензура»	SFW-режим	
	
	

	
