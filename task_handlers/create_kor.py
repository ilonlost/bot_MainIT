import logging
from _datetime import datetime
from conn.conn import bot
from conn.conn import get_db_connection
from task_handlers.menu import main_menu


@bot.message_handler(func=lambda message: message.text == "⚒️Королев")
def add_contractor_task_handler(message):
    bot.send_message(message.chat.id, "Введите наименование задачи:")
    bot.register_next_step_handler(message, get_task_name1)

def get_task_name1(message):
    task_name1 = message.text
    bot.send_message(message.chat.id, "Введите комментарий:")
    bot.register_next_step_handler(message, get_task_comment1, task_name1)

def get_task_comment1(message, task_name1):
    comment2 = message.text
    bot.send_message(message.chat.id, "Введите местоположение задачи:")
    bot.register_next_step_handler(message, get_task_location1, task_name1, comment2)

def get_task_location1(message, task_name1, comment2):
    location3 = message.text
    creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_contractor_task(task_name1, comment2, location3, creation_date)
    bot.send_message(message.chat.id, f"Задача '{task_name1}' добавлена!")
    main_menu(message)

def save_contractor_task(task_name1, comment2, location3, creation_date):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO contractor_tasks (task_name, comment, location, creation_date)
                VALUES (?, ?, ?, ?)
            """, (task_name1, comment2, location3, creation_date))
            conn.commit()
    except Exception as e:
        logging.error(f"Ошибка при добавлении задачи для подрядчика: {str(e)}", exc_info=True)
