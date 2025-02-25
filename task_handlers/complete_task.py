import logging
from telebot import types
from conn.conn import bot
from conn.conn import get_db_connection
from task_handlers.menu import main_menu



def complete_task(message):
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task_name FROM tasks WHERE status != '✅ Завершено'")
        tasks = cursor.fetchall()

    if tasks:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for task in tasks:
            task_id, task_name = task
            markup.add(f"{task_id} - {task_name}")  #
        bot.send_message(message.chat.id, "Выберите задачу для завершения:", reply_markup=markup)
        bot.register_next_step_handler(message, finish_task)
    else:
        bot.send_message(message.chat.id, "Нет доступных задач для завершения.")
        main_menu(message)

def finish_task(message):
    task_id_and_name = message.text
    task_id = task_id_and_name.split(" ")[0]  
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET status = '✅ Завершено' WHERE id = ?", (task_id,))
            conn.commit()
        bot.send_message(message.chat.id, f"✅ Задача с ID {task_id} завершена.")
        main_menu(message)  
    except Exception as e:
        logging.error(f"Ошибка при завершении задачи: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось завершить задачу.")
        main_menu(message)  
