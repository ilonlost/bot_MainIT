import logging
from telebot import types
from conn.conn import bot
from conn.conn import get_db_connection
from task_handlers.delete_pair import delete_expired_message_pairs
from task_handlers.delete_pair import delete_all_message_pairs
from task_handlers.delete_pair import save_message_pair
from task_handlers.menu import main_menu


def add_comment(task_id, comment, comment_column):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = f"UPDATE tasks SET {comment_column} = ? WHERE id = ?"
            cursor.execute(query, (comment, task_id))
            conn.commit()
        return True
    except Exception as e:
        logging.error(f"Ошибка при добавлении комментария: {str(e)}", exc_info=True)
        return False

@bot.message_handler(func=lambda message: message.text == "📝 Комментарий")
def comment_handler(message):
    
    delete_expired_message_pairs(message.chat.id)

    
    delete_all_message_pairs(message.chat.id)

    
    save_message_pair(message.chat.id, user_message_id=message.message_id)

    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task_name FROM tasks")
        tasks = cursor.fetchall()

    if tasks:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for task in tasks:
            task_id, task_name = task
            markup.add(f"{task_id} - {task_name}")  
        sent_message = bot.send_message(message.chat.id, "Выберите задачу, к которой хотите добавить комментарий:", reply_markup=markup)
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
        bot.register_next_step_handler(message, choose_comment_column)
    else:
        sent_message = bot.send_message(message.chat.id, "Нет доступных задач для добавления комментария.")
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
        main_menu(message)


def choose_comment_column(message):
    
    delete_expired_message_pairs(message.chat.id)
    
    save_message_pair(message.chat.id, user_message_id=message.message_id)

    task_id_and_name = message.text
    task_id = task_id_and_name.split(" ")[0]  
    sent_message = bot.send_message(message.chat.id, "Введите текст комментария:")
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
    bot.register_next_step_handler(message, handle_comment, task_id)


def handle_comment(message, task_id):
    
    delete_expired_message_pairs(message.chat.id)
    
    save_message_pair(message.chat.id, user_message_id=message.message_id)

    comment_text = message.text
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("1", "2", "3")  
    sent_message = bot.send_message(message.chat.id, "Выберите номер комментария (1, 2 или 3):", reply_markup=markup)
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
    bot.register_next_step_handler(message, save_comment, task_id, comment_text)


def save_comment(message, task_id, comment_text):
    
    delete_expired_message_pairs(message.chat.id)
    
    save_message_pair(message.chat.id, user_message_id=message.message_id)

    comment_number = message.text
    if comment_number == "1":
        comment_column = "comment1"
    elif comment_number == "2":
        comment_column = "comment2"
    elif comment_number == "3":
        comment_column = "comment3"
    else:
        sent_message = bot.send_message(message.chat.id, "❌ Неверный номер комментария. Попробуйте снова.")
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
        return

    
    if add_comment(task_id, comment_text, comment_column):
        sent_message = bot.send_message(message.chat.id, f"✅ Комментарий добавлен в столбец {comment_number}.")
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
    else:
        sent_message = bot.send_message(message.chat.id, "🚫 Не удалось добавить комментарий.")
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)

    
    main_menu(message)
