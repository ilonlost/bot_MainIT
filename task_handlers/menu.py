from conn.conn import bot
from task_handlers.delete_pair import delete_previous_list_messages
from task_handlers.delete_pair import save_message_pair
from task_handlers.delete_pair import delete_expired_message_pairs
from task_handlers.delete_pair import delete_previous_service_message
from task_handlers.delete_pair import delete_previous_interaction
from telebot import types
import telebot


def main_menu(message):
    delete_previous_list_messages(message.chat.id)

    tasks_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    tasks_keyboard.row("➕ Добавить", "📋 Списки", "⚙️ Сервис")
    tasks_keyboard.row("⬅️ Назад")

    sent_message = bot.send_message(
        message.chat.id,
        "Добро пожаловать в меню задач! Выберите действие:",
        reply_markup=tasks_keyboard
    )
    save_message_pair(message.chat.id, sent_message.message_id, message.message_id)



def service_menu(message):

    delete_expired_message_pairs(message.chat.id)

    delete_previous_list_messages(message.chat.id)
    delete_previous_service_message(message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✔️ Завершить", "❌ Удалить", "📝 Комментарий", "📊 Приоритет", "📋 Детали", "⚒️Королев", "⬅️ Назад")
    sent_message = bot.send_message(message.chat.id, "Выберите сервисную функцию:", reply_markup=markup)

    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id)


def back_menu_add(message):

    delete_previous_list_messages(message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Добавить", "📋 Списки", "⚙️ Сервис", "⬅️ Назад")


    sent_message = bot.send_message(message.chat.id, "✅ Задача успешно добавлена!", reply_markup=markup)

    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)


def list_menu(message):
    
    delete_expired_message_pairs(message.chat.id)

    
    delete_previous_list_messages(message.chat.id)

    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📌 Текущие", "📂 Проектные", "📊 Все задачи", "✅ Выполненные", "📑Королев", "⬅️ Назад")

    
    sent_message = bot.send_message(message.chat.id, "Выберите желаемый список:", reply_markup=markup)
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)

def main_menu1(message):
    
    delete_previous_interaction(message.chat.id, message.message_id)

    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Добавить", "📋 Списки", "⚙️ Сервис")

   
    sent_message = bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    save_message_pair(message.chat.id, bot_message_id=sent_message.message_id, user_message_id=message.message_id)
