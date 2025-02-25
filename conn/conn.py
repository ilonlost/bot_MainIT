import pyodbc
import logging
import telebot

# Лог файл для чтения ботом мониторинга
STATUS_FILE = "bot_status.txt"
# ID основного чата
chat_id = 
# ID тестового чата
GROUP_CHAT_ID = ''
# Инициализация бота
BOT_TOKEN = "token bot"
# Последнее закрепленное сообщение
last_pinned_message_id = None
# Словарь для записи сообщений отправленные ботом
sent_message_ids = {}
# Список для хранения пар (message_id бота, message_id пользователя)
message_pairs = []
# Обработчик команды /start для старта бота
bot = telebot.TeleBot(BOT_TOKEN)

# Логирование
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Конфигурация базы данных
DB_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': 'name server',
    'DATABASE': 'name database',
    'UID': 'login',
    'PWD': 'pwd'
}

def get_db_connection():
    """Подключение к базе данных"""
    return pyodbc.connect(
        f"DRIVER={DB_CONFIG['DRIVER']};"
        f"SERVER={DB_CONFIG['SERVER']};"
        f"DATABASE={DB_CONFIG['DATABASE']};"
        f"UID={DB_CONFIG['UID']};"
        f"PWD={DB_CONFIG['PWD']}"
    )


def get_user_by_telegram_id(telegram_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "telegram_id": row[1],
                "username": row[2],
                "group_access": row[3],
                "work_schedule": row[4]
            }
        return None
