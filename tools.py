import logging
import subprocess
import time
from task_conn.conn import bot
from telebot import types

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Список серверов фермы RDS
RDS_SERVERS = [
    "11-vm-rdcb01",  # Брокер 1
    "11-vm-rdcb02",  # Брокер 2
    "11-vm-rddb01",  # База данных
    "11-vm-rdfs01",  # Хранилище
    "11-vm-rds01",   # Терминальный сервер 1
    "11-vm-rds02",   # Терминальный сервер 2
    "11-vm-term01",  # Терминальный сервер 3
    "11-vm-term02",  # Терминальный сервер 4
    "11-vm-term03",  # Терминальный сервер 5
    "11-vm-term04",  # Терминальный сервер 6
    "11-vm-term05",  # Терминальный сервер 7
]

# Учетные данные для подключения к серверам
USERNAME = "agrohold.ru\\adm.kalinin"
PASSWORD = "Yfkbxybr6838#"
# Путь к файлу логов
LOG_FILE = "rds_logs.txt"



def get_server_status(server_name):
    """Проверяет доступность сервера."""
    try:
        command = [
            "powershell", "-Command",
            f"Test-NetConnection -ComputerName {server_name} -InformationLevel Quiet"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Ошибка при проверке доступности сервера {server_name}: {str(e)}", exc_info=True)
        return False

def log_message(message):
    """Записывает сообщение в лог."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def reboot_server(server_name):
    """Перезагружает указанный сервер."""
    try:
        command = [
            "powershell", "-Command",
            f"$Username = '{USERNAME}'; "
            f"$Password = '{PASSWORD}'; "
            f"$SecurePassword = ConvertTo-SecureString -AsPlainText $Password -Force; "
            f"$Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $Username, $SecurePassword; "
            f"Restart-Computer -ComputerName {server_name} -Force -Credential $Credential"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.returncode == 0, result.stderr
    except Exception as e:
        logging.error(f"Ошибка при перезагрузке сервера {server_name}: {str(e)}", exc_info=True)
        return False, str(e)

def get_connected_users():
    """Получает список подключенных пользователей."""
    try:
        command = [
            "powershell", "-Command",
            f"$Username = '{USERNAME}'; "
            f"$Password = '{PASSWORD}'; "
            f"$SecurePassword = ConvertTo-SecureString -AsPlainText $Password -Force; "
            f"$Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $Username, $SecurePassword; "
            f"Get-RDUserSession | Select-Object Username, HostServer, SessionId, ConnectionState"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        users = []
        for line in result.stdout.splitlines():
            if "Username" not in line:  # Пропускаем заголовок
                parts = line.split()
                if len(parts) >= 4:
                    users.append({
                        "username": parts[0],
                        "server": parts[1],
                        "session_id": parts[2],
                        "connection_state": parts[3]
                    })
        return users
    except Exception as e:
        logging.error(f"Ошибка при получении списка пользователей: {str(e)}", exc_info=True)
        return []

def get_server_status(server_name):
    """Проверяет доступность сервера."""
    try:
        command = [
            "powershell", "-Command",
            f"Test-NetConnection -ComputerName {server_name} -InformationLevel Quiet"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logging.error(f"Ошибка при проверке доступности сервера {server_name}: {str(e)}", exc_info=True)
        return False

def get_server_load(server_name):
    """Получает загрузку ЦП и ОЗУ сервера."""
    try:
        command = [
            "powershell", "-Command",
            f"$Username = '{USERNAME}'; "
            f"$Password = '{PASSWORD}'; "
            f"$SecurePassword = ConvertTo-SecureString -AsPlainText $Password -Force; "
            f"$Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $Username, $SecurePassword; "
            f"Invoke-Command -ComputerName {server_name} -Credential $Credential -ScriptBlock {{ "
            f"Get-Counter '\\Processor(_Total)\\% Processor Time' | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue; "
            f"Get-Counter '\\Memory\\Available MBytes' | Select-Object -ExpandProperty CounterSamples | Select-Object -ExpandProperty CookedValue "
            f"}}"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        cpu_usage, ram_available = result.stdout.strip().split()
        return float(cpu_usage), float(ram_available)
    except Exception as e:
        logging.error(f"Ошибка при получении нагрузки сервера {server_name}: {str(e)}", exc_info=True)
        return None, None

def is_host_in_farm(server_name):
    """Проверяет, находится ли хост в ферме."""
    try:
        command = [
            "powershell", "-Command",
            f"$Username = '{USERNAME}'; "
            f"$Password = '{PASSWORD}'; "
            f"$SecurePassword = ConvertTo-SecureString -AsPlainText $Password -Force; "
            f"$Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $Username, $SecurePassword; "
            f"Invoke-Command -ComputerName {server_name} -Credential $Credential -ScriptBlock {{ "
            f"(Get-RDServer -Role RDS-RD-SERVER).Server"
            f"}}"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        return server_name in result.stdout
    except Exception as e:
        logging.error(f"Ошибка при проверке хоста в ферме: {str(e)}", exc_info=True)
        return False

def get_user_count_per_server():
    """Возвращает количество пользователей на каждом терминальном сервере."""
    users = get_connected_users()
    user_count = {}
    for server in RDS_SERVERS:
        user_count[server] = 0
    for user in users:
        if user["server"] in user_count:
            user_count[user["server"]] += 1
    return user_count

def log_message(message):
    """Записывает сообщение в лог."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")


@bot.message_handler(func=lambda message: message.text == "Инструменты")
def tools_menu_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("RDS", "Назад")
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "RDS")
def rds_menu_handler(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Перезагрузка тестового сервера", "Перезагрузка фермы RDS", "Статистика RDS", "Пользователи", "Отключение пользователей", "Назад")
    bot.send_message(message.chat.id, "Управление RDS:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Перезагрузка тестового сервера")
def test_server_reboot_handler(message):
    try:
        # Отправка сообщения о начале перезагрузки
        bot.send_message(message.chat.id, "Начинаю перезагрузку тестового сервера 11-vm-DVLM01...")

        # Перезагрузка сервера
        success, error = reboot_server("11-vm-DVLM01")
        if success:
            bot.send_message(message.chat.id, "✅ Перезагрузка тестового сервера завершена успешно.")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка при перезагрузке тестового сервера:\n{error}")

        # Запись в лог
        log_message("Перезагрузка тестового сервера завершена.")
    except Exception as e:
        logging.error(f"Ошибка при перезагрузке тестового сервера: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось выполнить перезагрузку тестового сервера.")

@bot.message_handler(func=lambda message: message.text == "Перезагрузка фермы RDS")
def rds_reboot_handler(message):
    try:
        # Отправка сообщения о начале перезагрузки
        bot.send_message(message.chat.id, "Начинаю перезагрузку фермы RDS...")

        # Перезагрузка серверов
        servers = ["11-vm-rdcb01", "11-vm-rdcb02", "11-vm-rddb01", "11-vm-rdfs01", "11-vm-rds01", "11-vm-rds02", "11-vm-term01", "11-vm-term02", "11-vm-term03", "11-vm-term04" ,"11-vm-term05", "11-vm-ecoplan01"]
        for server in servers:
            success, error = reboot_server(server)
            if success:
                bot.send_message(message.chat.id, f"✅ Сервер {server} перезагружен.")
            else:
                bot.send_message(message.chat.id, f"❌ Ошибка при перезагрузке сервера {server}:\n{error}")

        # Запись в лог
        log_message("Перезагрузка фермы RDS завершена.")
        bot.send_message(message.chat.id, "✅ Перезагрузка фермы RDS завершена успешно.")
    except Exception as e:
        logging.error(f"Ошибка при перезагрузке фермы RDS: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось выполнить перезагрузку фермы RDS.")

@bot.message_handler(func=lambda message: message.text == "Статистика RDS")
def rds_stats_handler(message):
    try:
        # Формируем таблицу со статистикой
        stats_message = "📊 Статистика RDS:\n\n"
        stats_message += "| Сервер          | Статус   | ЦП (%) | ОЗУ (MB) | В ферме |\n"
        stats_message += "|-----------------|----------|--------|----------|---------|\n"
        for server in RDS_SERVERS:
            status = "🟢 Доступен" if get_server_status(server) else "🔴 Недоступен"
            cpu_usage, ram_available = get_server_load(server)
            in_farm = "❌" if is_host_in_farm(server) else "✅"
            if cpu_usage is not None and ram_available is not None:
                stats_message += f"| {server:15} | {status:8} | {cpu_usage:6.2f} | {ram_available:8.2f} | {in_farm:7} |\n"
            else:
                stats_message += f"| {server:15} | {status:8} |   N/A   |    N/A    | {in_farm:7} |\n"

        # Отправляем статистику
        bot.send_message(message.chat.id, f"```\n{stats_message}\n```", parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка при получении статистики RDS: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось получить статистику RDS.")

@bot.message_handler(func=lambda message: message.text == "Пользователи")
def users_handler(message):
    try:
        # Получаем количество пользователей на каждом сервере
        user_count = get_user_count_per_server()

        # Формируем список серверов для выбора
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for server, count in user_count.items():
            if count > 0:
                markup.add(f"{server} ({count} пользователей)")
        markup.add("Назад")
        msg = bot.send_message(message.chat.id, "Выберите сервер для просмотра пользователей:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_server_selection)
    except Exception as e:
        logging.error(f"Ошибка при получении списка пользователей: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось получить список пользователей.")

def process_server_selection(message):
    try:
        # Получаем имя сервера
        server_name = message.text.split(" (")[0]

        # Получаем список пользователей на сервере
        users = get_connected_users()
        server_users = [user for user in users if user["server"] == server_name]

        if not server_users:
            bot.send_message(message.chat.id, f"На сервере {server_name} нет подключенных пользователей.")
            return

        # Формируем список пользователей для выбора
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for user in server_users:
            markup.add(f"{user['username']} ({user['session_id']})")
        markup.add("Назад")
        msg = bot.send_message(message.chat.id, "Выберите пользователя для подробной информации:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_user_selection, server_name)
    except Exception as e:
        logging.error(f"Ошибка при выборе сервера: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось обработать выбор сервера.")

def process_user_selection(message, server_name):
    try:
        # Получаем имя пользователя и ID сессии
        user_info = message.text.split(" (")
        username = user_info[0]
        session_id = user_info[1].rstrip(")")

        # Получаем подробную информацию о пользователе
        users = get_connected_users()
        user = next((u for u in users if u["username"] == username and u["session_id"] == session_id), None)

        if user:
            user_message = f"👤 Подробная информация о пользователе:\n\n"
            user_message += f"Имя пользователя: {user['username']}\n"
            user_message += f"Сервер: {user['server']}\n"
            user_message += f"ID сессии: {user['session_id']}\n"
            user_message += f"Состояние подключения: {user['connection_state']}\n"
            bot.send_message(message.chat.id, user_message)
        else:
            bot.send_message(message.chat.id, "🚫 Пользователь не найден.")
    except Exception as e:
        logging.error(f"Ошибка при выборе пользователя: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось обработать выбор пользователя.")

@bot.message_handler(func=lambda message: message.text == "Отключение пользователей")
def disconnect_user_handler(message):
    try:
        # Получение списка пользователей
        users = get_connected_users()
        if not users:
            bot.send_message(message.chat.id, "Нет подключенных пользователей.")
            return

        # Формируем список пользователей для выбора
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for user in users:
            markup.add(f"{user['username']} ({user['server']})")
        markup.add("Назад")
        msg = bot.send_message(message.chat.id, "Выберите пользователя для отключения:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_disconnect_user)
    except Exception as e:
        logging.error(f"Ошибка при получении списка пользователей: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось получить список пользователей.")

def process_disconnect_user(message):
    try:
        # Получаем имя пользователя и сервер
        user_info = message.text.split(" (")
        username = user_info[0]
        server_name = user_info[1].rstrip(")")

        # Отключаем пользователя
        command = [
            "powershell", "-Command",
            f"$Username = '{USERNAME}'; "
            f"$Password = '{PASSWORD}'; "
            f"$SecurePassword = ConvertTo-SecureString -AsPlainText $Password -Force; "
            f"$Credential = New-Object -TypeName System.Management.Automation.PSCredential -ArgumentList $Username, $SecurePassword; "
            f"Invoke-Command -ComputerName {server_name} -Credential $Credential -ScriptBlock {{ "
            f"Invoke-RDUserLogoff -HostServer {server_name} -User {username} -Force "
            f"}}"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            bot.send_message(message.chat.id, f"✅ Пользователь {username} отключен от сервера {server_name}.")
        else:
            bot.send_message(message.chat.id, f"❌ Ошибка при отключении пользователя {username}:\n{result.stderr}")

        # Запись в лог
        log_message(f"Пользователь {username} отключен от сервера {server_name}.")
    except Exception as e:
        logging.error(f"Ошибка при отключении пользователя: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось отключить пользователя.")

@bot.message_handler(func=lambda message: message.text == "Назад")
def back_handler(message):
    main_menu(message)

def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Инструменты", "Задачи", "Склад")
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)

if __name__ == "__main__":
    logging.info("Бот запущен.")
    bot.polling(none_stop=True, timeout=30)
