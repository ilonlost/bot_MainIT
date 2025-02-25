import logging
from telebot import types
from conn.conn import bot
from conn.conn import get_db_connection
from task_handlers.menu import main_menu





@bot.message_handler(func=lambda message: message.text == "📋 Детали")
def details_handler(message):
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, task_name FROM tasks")
        tasks = cursor.fetchall()

    if tasks:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for task in tasks:
            task_id, task_name = task
            markup.add(f"{task_id} - {task_name}")  # Кнопки с ID и названием задачи
        bot.send_message(message.chat.id, "Выберите задачу для получения подробной информации:", reply_markup=markup)
        bot.register_next_step_handler(message, show_task_details)
    else:
        bot.send_message(message.chat.id, "Нет доступных задач для отображения.")
        main_menu(message)


def show_task_details(message):
    task_id_and_name = message.text.strip()
    task_id = task_id_and_name.split(" ")[0]

    task_details = fetch_task_details(task_id)

    if task_details:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            
            cursor.execute("SELECT username FROM users WHERE telegram_id = ?", (task_details['creator'],))
            creator_username = cursor.fetchone()
            creator_text = creator_username[0] if creator_username else "Неизвестно"

            
            assignee_ids = task_details['assignee'].split(", ")
            cursor.execute(f"SELECT username FROM users WHERE telegram_id IN ({', '.join(['?'] * len(assignee_ids))})", assignee_ids)
            assignee_usernames = [row[0] for row in cursor.fetchall()]
            assignee_text = ", ".join(assignee_usernames) if assignee_usernames else "Не назначен"

        details_text = (
            f"📋 Детали задачи:\n"
            f"📝 Название: {task_details['task_name']}\n"
            f"📄 Описание: {task_details['task_description']}\n"
            f"🔑 Приоритет: {task_details['task_priority']}\n"
            f"🔖 Тип задачи: {task_details['task_type']}\n"
            f"⚙️ Статус: {task_details['task_status']}\n"
            f"👤 Создатель: {creator_text}\n"
            f"👥 Ответственные: {assignee_text}\n"
            f"💬 Комментарии:\n"
            f"1. {task_details['comment1']}\n"
            f"2. {task_details['comment2']}\n"
            f"3. {task_details['comment3']}\n"
        )
        bot.send_message(message.chat.id, details_text)
    else:
        bot.send_message(message.chat.id, "🚫 Задача с таким ID не найдена.")
    main_menu(message)


def fetch_task_details(task_id):
    try:
        task_id = int(task_id)
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT task_name, description, priority, type, status, creator, assignee, comment1, comment2, comment3
                FROM tasks WHERE id = ?
            """, (task_id,))
            task = cursor.fetchone()

            if task:
                return {
                    "task_name": task[0],
                    "task_description": task[1],
                    "task_priority": task[2],
                    "task_type": task[3],
                    "task_status": task[4],
                    "creator": task[5],
                    "assignee": task[6],
                    "comment1": task[7],
                    "comment2": task[8],
                    "comment3": task[9]
                }
            else:
                return None
    except ValueError:
        logging.error("Ошибка: Невозможно преобразовать ID в целое число")
        return None
    except Exception as e:
        logging.error(f"Ошибка при получении данных задачи: {str(e)}", exc_info=True)
        return None
