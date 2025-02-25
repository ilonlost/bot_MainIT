import logging
from task_handlers.delete_pair import delete_expired_message_pairs
from task_handlers.delete_pair import delete_previous_list_messages
from task_handlers.delete_pair import save_message_pair
from conn.conn import get_db_connection
from conn.conn import bot
from telebot import types




def display_tasks(message, filter_type=None):
    try:
        
        delete_expired_message_pairs(message.chat.id)

        
        delete_previous_list_messages(message.chat.id)

        with get_db_connection() as conn:
            cursor = conn.cursor()

            
            if filter_type == "Текущие":
                cursor.execute(
                    "SELECT id, task_name, type, priority, status FROM tasks WHERE type = 'Текущая' AND status != '✅ Завершено'")
            elif filter_type == "Проектные":
                cursor.execute(
                    "SELECT id, task_name, type, priority, status FROM tasks WHERE type = 'Проектная' AND status != '✅ Завершено'")
            elif filter_type == "Выполненные":
                cursor.execute("SELECT id, task_name, type, priority, status FROM tasks WHERE status = '✅ Завершено'")
            else:
                cursor.execute("SELECT id, task_name, type, priority, status FROM tasks")

            tasks = cursor.fetchall()

            
            if tasks:
                project_tasks = []
                current_tasks = []
                completed_tasks = []

                for task in tasks:
                    task_id, task_name, task_type, task_priority, status = task
                    formatted_priority = format_priority(task_priority)

                    task_text = f"- {formatted_priority} ID: {task_id} Задача: {task_name} "

                    if "Завершено" in status:
                        completed_tasks.append(task_text)
                    elif task_type.lower() == "проектная":
                        project_tasks.append(task_text)
                    elif task_type.lower() == "текущая":
                        current_tasks.append(task_text)

                
                task_list_message = "📋 Список ваших задач:\n\n"

                if project_tasks:
                    task_list_message += "         Проектные задачи:\n"
                    task_list_message += "\n".join(project_tasks) + "\n\n"

                if current_tasks:
                    task_list_message += "         Текущие задачи:\n"
                    task_list_message += "\n".join(current_tasks) + "\n\n"


                
                sent_message = bot.send_message(message.chat.id, task_list_message)
                save_message_pair(message.chat.id, bot_message_id=sent_message.message_id,
                                  user_message_id=message.message_id)
            else:
                sent_message = bot.send_message(message.chat.id, "❌ Задач не найдено.")
                save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)
    except Exception as e:
        logging.error(f"Ошибка при отображении задач: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось загрузить задачи. Попробуйте снова.")

    
    prompt_main_menu(message)



def prompt_main_menu(message):
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Добавить", "📋 Списки", "⚙️ Сервис", "⬅️ Назад")

    
    sent_message = bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)



def handle_repeated_selection(chat_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bot_message_id FROM message_pairs
                WHERE chat_id = ? AND bot_message_id IS NOT NULL
                ORDER BY id DESC LIMIT 1
            """, (chat_id,))
            last_message = cursor.fetchone()

            if last_message:
                bot.delete_message(chat_id, last_message[0])
                cursor.execute("""
                    DELETE FROM message_pairs
                    WHERE chat_id = ? AND bot_message_id = ?
                """, (chat_id, last_message[0]))
                conn.commit()
    except Exception as e:
        logging.error(f"Ошибка при удалении предыдущего списка: {str(e)}")



def format_priority(priority):
    if priority == "🔴 Высокий":
        return "🔴"
    elif priority == "🟡 Средний":
        return "🟡"
    else:
        return "🟢"
