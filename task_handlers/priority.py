from telebot import types
from conn.conn import bot
from conn.conn import get_db_connection
from task_handlers.delete_pair import save_message_pair
from task_handlers.delete_pair import delete_previous_interaction
from task_handlers.delete_pair import delete_all_message_pairs
from task_handlers.menu import main_menu
from task_handlers.menu import main_menu1


@bot.message_handler(func=lambda message: message.text == "📊 Приоритет")
def change_priority_handler(message):
    
    delete_previous_interaction(message.chat.id, message.message_id)

    
    sent_message = bot.send_message(message.chat.id, "Загрузка списка задач...")
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)

    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task_name FROM tasks")
        tasks = cursor.fetchall()

    if tasks:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for task in tasks:
            task_id, task_name = task
            markup.add(f"{task_id} - {task_name}")
        sent_message = bot.send_message(message.chat.id, "Выберите задачу для изменения приоритета:", reply_markup=markup)
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
        bot.register_next_step_handler(message, ask_for_priority)
    else:
        sent_message = bot.send_message(message.chat.id, "Задачи не найдены.")
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
        main_menu(message)

def ask_for_priority(message):
    
    delete_previous_interaction(message.chat.id, message.message_id)

    task_id_and_name = message.text
    task_id = task_id_and_name.split(" ")[0]

    sent_message = bot.send_message(
        message.chat.id,
        f"Вы выбрали задачу с ID: {task_id}. Теперь выберите новый приоритет:",
        reply_markup=get_priority_markup()
    )
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
    bot.register_next_step_handler(message, update_priority, task_id)


def get_priority_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("🔴 Высокий", "🟡 Средний", "🟢 Низкий")
    return markup

def update_priority(message, task_id):
    
    delete_previous_interaction(message.chat.id, message.message_id)

    priority = message.text
    if priority not in ["🔴 Высокий", "🟡 Средний", "🟢 Низкий"]:
        sent_message = bot.send_message(message.chat.id, "Неизвестный приоритет. Попробуйте снова.")
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
        main_menu(message)
        return

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET priority = ? WHERE id = ?", (priority, task_id))
            conn.commit()

        sent_message = bot.send_message(
            message.chat.id,
            f"Приоритет задачи с ID {task_id} успешно обновлён."
        )
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)
    except Exception as e:
        sent_message = bot.send_message(
            message.chat.id,
            f"Ошибка при обновлении приоритета: {str(e)}"
        )
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)

    
    delete_all_message_pairs(message.chat.id)

    
    main_menu(message)


