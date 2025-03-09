import os
import subprocess
import telebot

MONITOR_BOT_TOKEN = "7945717506:AAFmFd6n1ozmM16RYOEpFTMHJMkrS-WWPbQ"
STATUS_FILE = "bot_status.txt"
MAIN_BOT_SCRIPT = "start_main_bot.py"
NOTIF_BOT_SCRIPT = "start_notif_bot.py"

bot_monitor = telebot.TeleBot(MONITOR_BOT_TOKEN)

# /status — Проверка статуса основного бота
@bot_monitor.message_handler(commands=["status"])
def check_status(message):
    try:
        with open(STATUS_FILE, "r") as file:
            status = file.read().strip()
        bot_monitor.send_message(message.chat.id, f"Статус основного бота: {status}")
    except FileNotFoundError:
        bot_monitor.send_message(message.chat.id, "Статус неизвестен. Возможно, бот еще не запущен.")


# /error — Получение последней ошибки
@bot_monitor.message_handler(commands=["error"])
def get_last_error(message):
    try:
        with open(STATUS_FILE, "r") as file:
            status = file.read().strip()
        if "error" in status:
            bot_monitor.send_message(message.chat.id, f"Последняя ошибка основного бота:\n{status}")
        else:
            bot_monitor.send_message(message.chat.id, "Ошибок не найдено.")
    except FileNotFoundError:
        bot_monitor.send_message(message.chat.id, "Файл статуса отсутствует.")

# /restart — Перезапуск основного бота
@bot_monitor.message_handler(commands=["restart"])
def restart_bot(message):
    try:
        bot_monitor.send_message(message.chat.id, "Перезапускаю основной бот...")
        subprocess.Popen(["python", MAIN_BOT_SCRIPT])
        bot_monitor.send_message(message.chat.id, "Основной бот успешно перезапущен.")
    except Exception as e:
        bot_monitor.send_message(message.chat.id, f"Ошибка при перезапуске: {str(e)}")
# /restart — Перезапуск основного бота
@bot_monitor.message_handler(commands=["restarts"])
def restart_bot(message):
    try:
        bot_monitor.send_message(message.chat.id, "Перезапускаю notif бот...")
        subprocess.Popen(["python", NOTIF_BOT_SCRIPT])
        bot_monitor.send_message(message.chat.id, "Notif бот успешно перезапущен.")
    except Exception as e:
        bot_monitor.send_message(message.chat.id, f"Ошибка при перезапуске: {str(e)}")
# Запуск бота-монитора
if __name__ == "__main__":
    bot_monitor.polling(none_stop=True)