import telebot
import pyodbc
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


API_TOKEN = '7810424702:AAHq18mDh-9i-DaYS2DuEhiIbxfj8lCBplo'


bot = telebot.TeleBot(API_TOKEN)


DB_CONFIG = {
    'DRIVER': '{ODBC Driver 17 for SQL Server}',
    'SERVER': '11-VM-DWH01',
    'DATABASE': 'Telegram_DB',
    'UID': 'asutp',
    'PWD': 'Miratorg1'
}

def get_db_connection():
    """Подключение к базе данных"""
    try:
        conn_str = (
            f"DRIVER={DB_CONFIG['DRIVER']};"
            f"SERVER={DB_CONFIG['SERVER']};"
            f"DATABASE={DB_CONFIG['DATABASE']};"
        )
        if DB_CONFIG['UID'] and DB_CONFIG['PWD']:
            conn_str += f"UID={DB_CONFIG['UID']};PWD={DB_CONFIG['PWD']};"
        else:
            conn_str += "Trusted_Connection=yes;"

        conn = pyodbc.connect(conn_str)
        logger.info("Подключение к базе данных успешно")
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return None


selected_hashtag = {}

def send_hashtag_list(chat_id):
    """Отправляет список хештегов в виде инлайн-кнопок"""
    try:

        conn = get_db_connection()
        if conn is None:
            bot.send_message(chat_id, "Ошибка подключения к базе данных.")
            return

        cursor = conn.cursor()


        cursor.execute("SELECT id, hashtag FROM hashtags")
        hashtags = cursor.fetchall()

        if hashtags:

            markup = telebot.types.InlineKeyboardMarkup()
            for tag in hashtags:
                button = telebot.types.InlineKeyboardButton(text=tag[1], callback_data=f"hashtag_{tag[0]}")
                markup.add(button)


            bot.send_message(chat_id, "Выберите хештег:", reply_markup=markup)
        else:
            bot.send_message(chat_id, "Нет доступных хештегов.")


        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка при отправке списка хештегов: {e}")
        bot.send_message(chat_id, "Произошла ошибка. Попробуйте позже.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('hashtag_'))
def handle_hashtag_selection(call):
    """Обработчик выбора хештега"""
    try:

        hashtag_id = int(call.data.split('_')[1])


        selected_hashtag[call.message.chat.id] = hashtag_id


        bot.send_message(call.message.chat.id, "Введите username пользователя в формате @username:")
    except Exception as e:
        logger.error(f"Ошибка при обработке выбора хештега: {e}")
        bot.send_message(call.message.chat.id, "Произошла ошибка. Попробуйте позже.")

def add_user_to_hashtag(message):
    """Добавляет пользователя в выбранный хештег"""
    try:

        username = message.text.strip().lower()


        if not username.startswith("@"):
            username = f"@{username}"


        chat_id = message.chat.id
        if chat_id not in selected_hashtag:
            bot.send_message(chat_id, "Ошибка: хештег не выбран.")
            return

        hashtag_id = selected_hashtag[chat_id]


        conn = get_db_connection()
        if conn is None:
            bot.send_message(chat_id, "Ошибка подключения к базе данных.")
            return

        cursor = conn.cursor()


        cursor.execute("INSERT INTO hashtag_users (hashtag_id, username) VALUES (?, ?)", (hashtag_id, username))
        conn.commit()


        bot.send_message(chat_id, f"Пользователь {username} добавлен в хештег.")


        del selected_hashtag[chat_id]


        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка добавления пользователя в хештег: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте снова.")

@bot.message_handler(func=lambda message: message.chat.id in selected_hashtag)
def handle_username_input(message):
    """Обработчик ввода username пользователя"""
    add_user_to_hashtag(message)

@bot.message_handler(commands=['starts'])
def start_command(message):
    """Обработчик команды /start"""
    try:
        bot.send_message(message.chat.id, "Привет! Я бот для уведомлений. Используй /admin для управления.")
        logger.info(f"Пользователь {message.from_user.username} вызвал команду /start")
    except Exception as e:
        logger.error(f"Ошибка в команде /start: {e}")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    """Обработчик команды /admin"""
    logger.info(f"Пользователь {message.from_user.username} вызвал команду /admin")
    try:

        conn = get_db_connection()
        if conn is None:
            bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
            return

        cursor = conn.cursor()


        cursor.execute("SELECT id FROM users WHERE telegram_id = ? AND group_access = 'admin'", (message.from_user.id,))
        admin = cursor.fetchone()

        if admin:

            markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
            itembtn1 = telebot.types.KeyboardButton('Добавить хештег')
            itembtn2 = telebot.types.KeyboardButton('Добавить пользователя в хештег')
            markup.add(itembtn1, itembtn2)
            bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "У вас нет прав администратора.")


        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка админской панели: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")

@bot.message_handler(func=lambda message: message.text == 'Добавить хештег')
def handle_add_hashtag(message):
    """Обработчик выбора 'Добавить хештег'"""
    try:

        msg = bot.send_message(message.chat.id, "Введите название нового хештега (начинается с #):")
        bot.register_next_step_handler(msg, add_hashtag)
    except Exception as e:
        logger.error(f"Ошибка при запросе названия хештега: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")

def add_hashtag(message):
    """Добавляет новый хештег в базу данных"""
    try:
        hashtag = message.text.strip().lower()


        if not hashtag.startswith("#"):
            hashtag = f"#{hashtag}"


        conn = get_db_connection()
        if conn is None:
            bot.send_message(message.chat.id, "Ошибка подключения к базе данных.")
            return

        cursor = conn.cursor()


        cursor.execute("SELECT id FROM hashtags WHERE hashtag = ?", (hashtag,))
        existing_hashtag = cursor.fetchone()

        if existing_hashtag:
            bot.send_message(message.chat.id, f"Хештег {hashtag} уже существует.")
        else:

            cursor.execute("INSERT INTO hashtags (hashtag) VALUES (?)", (hashtag,))
            conn.commit()
            bot.send_message(message.chat.id, f"Хештег {hashtag} успешно добавлен.")


        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка добавления хештега: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте снова.")

@bot.message_handler(func=lambda message: message.text == 'Добавить пользователя в хештег')
def handle_add_user_to_hashtag(message):
    """Обработчик выбора 'Добавить пользователя в хештег'"""
    send_hashtag_list(message.chat.id)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обработчик новых сообщений"""
    logger.info(f"Получено сообщение: {message.text} от пользователя {message.from_user.username}")
    try:
        text = message.text.lower()


        conn = get_db_connection()
        if conn is None:
            logger.error("Ошибка подключения к базе данных")
            return

        cursor = conn.cursor()


        cursor.execute("SELECT id, hashtag FROM hashtags")
        hashtags = cursor.fetchall()


        for tag in hashtags:
            if tag[1] in text:

                cursor.execute("""
                    SELECT username 
                    FROM hashtag_users
                    WHERE hashtag_id = ?
                """, tag[0])
                users = cursor.fetchall()
                users = [user[0] for user in users]


                send_notification(message.chat.id, tag[1], users)
                break


        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")

def send_notification(chat_id, tag, users):
    """Отправка уведомления пользователям"""
    try:
        if users:

            notification_text = f"Упоминание хештега #{tag} для {', '.join(users)}."

            bot.send_message(chat_id, notification_text)
            logger.info(f"Уведомление отправлено: {notification_text}")
        else:
            logger.info("Нет пользователей для уведомления")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")


if __name__ == "__main__":
    try:
        logger.info("Бот запущен")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")