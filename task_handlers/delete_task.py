import logging
from conn.conn import bot
from conn.conn import get_db_connection
from task_handlers.menu import main_menu
from telebot import types



def delete_task(message):
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task_name FROM tasks")
        tasks = cursor.fetchall()

    if tasks:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for task in tasks:
            task_id, task_name = task
            markup.add(f"{task_id} - {task_name}")  
        bot.send_message(message.chat.id, "Выберите задачу для удаления:", reply_markup=markup)
        bot.register_next_step_handler(message, remove_task)
    else:
        bot.send_message(message.chat.id, "Нет доступных задач для удаления.")
        main_menu(message)

def remove_task(message):
    task_id_and_name = message.text
    task_id = task_id_and_name.split(" ")[0]  
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
        bot.send_message(message.chat.id, f"✅ Задача с ID {task_id} удалена.")
        main_menu(message)  
    except Exception as e:
        logging.error(f"Ошибка при удалении задачи: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось удалить задачу.")
        main_menu(message)  
