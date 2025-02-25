import logging
from task_handlers.delete_pair import delete_previous_interaction
from task_handlers.delete_pair import save_message_pair
from task_handlers.menu import back_menu_add
from conn.conn import bot
from conn.conn import get_db_connection
from conn.conn import get_user_by_telegram_id
from telebot import types


def add_task_menu(message):
    delete_previous_interaction(message.chat.id, message.message_id)

    sent_message = bot.send_message(message.chat.id, "Введите название задачи:")
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)
    bot.register_next_step_handler(sent_message, get_task_name, sent_message.message_id)


def get_task_name(message, previous_bot_message_id):
    delete_previous_interaction(message.chat.id, previous_bot_message_id)

    task_name = message.text
    sent_message = bot.send_message(message.chat.id, "Введите описание задачи:")
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)
    bot.register_next_step_handler(sent_message, get_task_description, sent_message.message_id, task_name)


def get_task_description(message, previous_bot_message_id, task_name):
    delete_previous_interaction(message.chat.id, previous_bot_message_id)

    description = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Текущая", "Проектная")
    sent_message = bot.send_message(message.chat.id, "Выберите тип задачи:", reply_markup=markup)
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)
    bot.register_next_step_handler(sent_message, get_task_type, sent_message.message_id, task_name, description)


def get_task_type(message, previous_bot_message_id, task_name, description):
    delete_previous_interaction(message.chat.id, previous_bot_message_id)

    task_type = message.text
    if task_type not in ["Текущая", "Проектная"]:
        sent_message = bot.send_message(message.chat.id, "Неверный тип задачи. Попробуйте снова.")
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)
        bot.register_next_step_handler(sent_message, get_task_type, sent_message.message_id, task_name, description)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔴 Высокий", "🟡 Средний", "🟢 Низкий")
    sent_message = bot.send_message(message.chat.id, "Выберите приоритет задачи:", reply_markup=markup)
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)
    bot.register_next_step_handler(sent_message, get_responsible_user, sent_message.message_id, task_name, description, task_type)


def get_responsible_user(message, previous_bot_message_id, task_name, description, task_type):
    delete_previous_interaction(message.chat.id, previous_bot_message_id)

    priority = message.text
    if priority not in ["🔴 Высокий", "🟡 Средний", "🟢 Низкий"]:
        sent_message = bot.send_message(message.chat.id, "Неверный приоритет. Попробуйте снова.")
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)
        bot.register_next_step_handler(sent_message, get_responsible_user, sent_message.message_id, task_name,
                                       description, task_type)
        return

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT telegram_id, username, group_access FROM users")
            users = cursor.fetchall()

        group_access = next((user[2] for user in users if user[0] == message.from_user.id), "user")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

        
        for user in users:
            markup.add(user[1])  

        markup.add("Готово")  
        sent_message = bot.send_message(message.chat.id, "Выберите ответственных (нажмите 'Готово', чтобы завершить):",
                                        reply_markup=markup)
        save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)

        #
        bot.register_next_step_handler(sent_message, collect_responsibles, task_name, description, task_type, priority,
                                       users, [])

    except Exception as e:
        logging.error(f"Ошибка при выборе ответственного: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Произошла ошибка. Попробуйте снова.")


def collect_responsibles(message, task_name, description, task_type, priority, users, selected_users):
    responsible_username = message.text.strip()

    if responsible_username == "Готово":
        if not selected_users:
            bot.send_message(message.chat.id, "Вы не выбрали ни одного ответственного. Попробуйте снова.")
            return
        save_task(message, None, task_name, description, task_type, priority, "admin", users, selected_users)
        return

    user = next((user for user in users if user[1] == responsible_username), None)
    if user and user[1] not in selected_users:
        selected_users.append(user[1])  
        bot.send_message(message.chat.id, f"Добавлено: {responsible_username}. Выберите еще или нажмите 'Готово'.")
    else:
        bot.send_message(message.chat.id, "Пользователь не найден или уже добавлен. Выберите другого.")

    bot.register_next_step_handler(message, collect_responsibles, task_name, description, task_type, priority, users, selected_users)


def save_task(message, previous_bot_message_id, task_name, description, task_type, priority, group_access, users, selected_usernames):
    responsible_ids = [user[0] for user in users if user[1] in selected_usernames]
    responsible_user_str = ", ".join(selected_usernames)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (task_name, description, priority, type, status, creator, assignee, comment1, comment2, comment3)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (task_name, description, priority, task_type, "⏳ В работе", message.from_user.id, ", ".join(map(str, responsible_ids)), "", "", ""))
            conn.commit()

            cursor.execute("SELECT SCOPE_IDENTITY()")
            task_id = cursor.fetchone()[0]

        notify_assignees(responsible_ids, task_name, description, priority, task_type, task_id)
       # bot.send_message(message.chat.id, "✅ Задача успешно добавлена!")
        back_menu_add(message)

    except Exception as e:
        logging.error(f"Ошибка при сохранении задачи: {str(e)}", exc_info=True)
        bot.send_message(message.chat.id, "🚫 Не удалось сохранить задачу. Попробуйте снова.")

def notify_assignees(assignee_ids, task_name, description, priority, task_type, task_id):
    """Уведомляет всех ответственных пользователей с деталями задачи."""
    for assignee_id in assignee_ids:
        try:
            task_details_text = (
                f"👥 Вам назначена новая задача:\n"
                f"📝 Название: {task_name}\n"
                f"📄 Описание: {description}\n"
                f"🔑 Приоритет: {priority}\n"
                f"🔖 Тип задачи: {task_type}\n"
                f"📋 ИДИ ДЕЛАТЬ"
            )
            bot.send_message(assignee_id, task_details_text)
        except Exception as e:
            logging.error(f"Не удалось отправить уведомление пользователю {assignee_id}: {str(e)}", exc_info=True)
