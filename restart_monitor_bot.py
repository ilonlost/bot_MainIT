import time
import subprocess

MONITOR_BOT_SCRIPT = "monitor_bot.py"  # Имя скрипта бота-монитора
RESTART_INTERVAL = 120  # Интервал перезапуска в секундах (2 минуты)

def run_monitor_bot():
    """Функция запускает скрипт бота-монитора."""
    while True:
        try:
            print(f"Запуск {MONITOR_BOT_SCRIPT}")
            process = subprocess.Popen(["python", MONITOR_BOT_SCRIPT])
            time.sleep(RESTART_INTERVAL)  # Ждём 2 минуты перед перезапуском
            print("Перезапуск бота-монитора...")
            process.terminate()  # Завершаем текущий процесс бота
            process.wait()  # Дожидаемся завершения процесса
        except Exception as e:
            print(f"Ошибка при запуске {MONITOR_BOT_SCRIPT}: {str(e)}")
            time.sleep(10)  # Ожидание перед повторной попыткой в случае ошибки

if __name__ == "__main__":
    run_monitor_bot()