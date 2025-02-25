import telebot
import logging
from telebot import types
from requests.exceptions import ReadTimeout
from task_handlers.menu import list_menu
from task_handlers.add_task import add_task_menu
from task_handlers.list_tasks import display_tasks
from task_handlers.delete_pair import save_message_pair
from task_handlers.delete_pair import delete_all_message_pairs
from task_handlers.delete_pair import delete_previous_list_messages
from task_handlers.menu import service_menu
from task_handlers.menu import main_menu
from task_handlers.priority import change_priority_handler
from task_handlers.detail_tasks import details_handler
from task_handlers.comm import comment_handler
from task_handlers.delete_task import delete_task
from task_handlers.complete_task import complete_task
from task_handlers.create_kor import add_contractor_task_handler
from task_handlers.list_kor import contractor_task_list_handler
from task_handlers.adm import admin_menu
from conn.conn import get_db_connection
from conn.conn import bot
from sklad_config.conn_TG import bot_token
from sklad_config.conn_DB import connection_string
from sklad_handlers.add_handler import add_menu
from sklad_handlers.utill_handler import add_write_off
#from sklad_handlers.add_cell_handler import cell_menu
from sklad_handlers.delete_handler import delete_equipment
from sklad_handlers.search_handler import search_equipment
from sklad_handlers.inventory_handler import inventory_start
from sklad_handlers.add_asset_handler import add_asset
#from sklad_handlers.scan_qr_handler import request_photo
from sklad_config.conn_id import ADMIN_CHAT_ID
from tools import tools_menu_handler
import time
import traceback


conn = connection_string()




logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),  
        logging.StreamHandler()         
    ]
)


user_message_data = {}


def save_message_pair(chat_id, bot_message_id, user_message_id):
    user_message_data[chat_id] = {"bot_message_id": bot_message_id, "user_message_id": user_message_id}


def delete_previous_list_messages(chat_id):
    if chat_id in user_message_data:
        try:
            data = user_message_data.pop(chat_id)
            bot.delete_message(chat_id, data["bot_message_id"])
            bot.delete_message(chat_id, data["user_message_id"])
        except Exception:
            pass  


@bot.message_handler(commands=['start'])
def start_handler(message):
    delete_previous_list_messages(message.chat.id)

    
    main_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    main_keyboard.row("Склад", "Задачи", "Инструменты")

    sent_message = bot.send_message(
        message.chat.id,
        "Выберите раздел:",
        reply_markup=main_keyboard
    )
    save_message_pair(message.chat.id, sent_message.message_id, message.message_id)


@bot.message_handler(func=lambda message: message.text == "Склад")
def warehouse_menu(message):
    delete_previous_list_messages(message.chat.id)

    warehouse_keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    warehouse_keyboard.row("➕Добавить", "🔍 Поиск", "📦 Инвент")
    warehouse_keyboard.row("🆕 Ячейка", "❌Удалить", "♻️ Утиль")
    warehouse_keyboard.row("📤 Выдать", "📸 QR-код", "⬅️ Назад")

    sent_message = bot.send_message(
        message.chat.id,
        "Добро пожаловать на склад! Выберите действие:",
        reply_markup=warehouse_keyboard
    )
    save_message_pair(message.chat.id, sent_message.message_id, message.message_id)


@bot.message_handler(func=lambda message: message.text == "Задачи")
def tasks_menu(message):
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


@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def back_to_main_menu(message):
    start_handler(message)

def send_error_message(error_message):
    """
    Функция для отправки сообщения об ошибке администратору.
    """
    bot.send_message(ADMIN_CHAT_ID, error_message)

@bot.message_handler(commands=['a'])
def start(message):
    # Искусственная ошибка
    raise Exception("Тестовая ошибка для проверки функции отправки ошибок")


@bot.message_handler(func=lambda message: message.text == "📤 Выдать")
def start_add_process(message):
    add_asset(bot, None, message)
    #bot.send_message(message.chat.id, "НЕ ЛЕЗЬ СЮДА - КОМУ СКАЗАЛ БЛЯТБ")
@bot.message_handler(func=lambda message: message.text == "📸 QR-код")
def start_qr_scan_process(message):
    #request_photo(message, bot)
    bot.send_message(message.chat.id, "НЕ ЛЕЗЬ СЮДА - КОМУ СКАЗАЛ БЛЯТБ")

@bot.message_handler(func=lambda message: message.text == "➕Добавить")
def start_add_process(message):
#    add_menu(bot, conn, message)
    bot.send_message(message.chat.id, "НЕ ЛЕЗЬ СЮДА - КОМУ СКАЗАЛ БЛЯТБ")

@bot.message_handler(func=lambda message: message.text == "♻️ Утиль")
def start_write_off_process(message):
    add_write_off(bot, conn, message)


@bot.message_handler(func=lambda message: message.text == "🆕 Ячейка")
def start_add_cell_process(message):
#    cell_menu(bot, conn, message)
    bot.send_message(message.chat.id, "НЕ ЛЕЗЬ СЮДА - КОМУ СКАЗАЛ БЛЯТБ")

@bot.message_handler(func=lambda message: message.text == "❌Удалить")
def start_delete_process(message):
    delete_equipment(bot, conn, message)


@bot.message_handler(func=lambda message: message.text == "🔍 Поиск")
def start_search_process(message):
    search_equipment(bot, conn, message)


@bot.message_handler(func=lambda message: message.text == "📦 Инвент")
def start_inventory_process(message):
    inventory_start(bot, conn, message)


@bot.message_handler(commands=["t"])
def send_welcome(message):
    bot.reply_to(message, f"Ваш ID: {message.from_user.id}")
    print(f"ID бота: {bot.get_me().id}")

@bot.message_handler(commands=["del"])
def delete_messages(message):
    delete_all_message_pairs(message.chat.id)
    bot.send_message(message.chat.id, "✅ Все сообщения удалены.")
    main_menu(message)

@bot.message_handler(commands=["get_chat_id"])
def get_chat_id(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Chat ID: {chat_id}")

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == "➕ Добавить":
        add_task_menu(message)
    elif message.text == "📋 Списки":
        list_menu(message)
    elif message.text == "⚙️ Сервис":
        service_menu(message)
    elif message.text == "📌 Текущие":
        display_tasks(message, filter_type="Текущие")
    elif message.text == "📂 Проектные":
        display_tasks(message, filter_type="Проектные")
    elif message.text == "📊 Все задачи":
        display_tasks(message)
    elif message.text == "✅ Выполненные":
        display_tasks(message, filter_type="Выполненные")
    elif message.text == "✔️ Завершить":
        complete_task(message)
    elif message.text == "❌ Удалить":
        delete_task(message)
    elif message.text == "⚒️Королев":
        add_contractor_task_handler(message)
    elif message.text == "/del":
        delete_messages(message)
    elif message.text == "/adm":
        admin_menu(message)
    elif message.text == "📋 Детали":
        details_handler(message)
    elif message.text == "📊 Приоритет":
        change_priority_handler(message)
    elif message.text == "📑Королев":
        contractor_task_list_handler(message)
    elif message.text == "📝 Комментарий":
        comment_handler(message)
    elif message.text == "⚒️ Инструменты":
        tools_menu_handler(message)
    elif message.text == "⬅️ Назад":
        main_menu(message)
    else:
        pass



@bot.message_handler(func=lambda message: message.text == "📌 Текущие")
def show_current_tasks(message):
    
    delete_previous_list_messages(message.chat.id)
    display_tasks(message, filter_type="Текущие")

@bot.message_handler(func=lambda message: message.text == "📂 Проектные")
def show_project_tasks(message):
    delete_previous_list_messages(message.chat.id)
    display_tasks(message, filter_type="Проектные")


@bot.message_handler(func=lambda message: message.text == "✅ Выполненные")
def show_completed_tasks(message):
    delete_previous_list_messages(message.chat.id)
    display_tasks(message, filter_type="Выполненные")


@bot.message_handler(func=lambda message: message.text == "📊 Все задачи")
def show_all_tasks(message):
    delete_previous_list_messages(message.chat.id)
    display_tasks(message)

if __name__ == '__main__':
    logging.info("Бот запущен.")
    bot.polling(none_stop=True)
