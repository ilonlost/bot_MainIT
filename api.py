from flask import Flask, request, send_file
import subprocess
import os

app = Flask(__name__)

# Переменная для хранения процесса бота
bot_process = None

@app.route('/')
def index():
    return "API для управления ботом работает!", 200

@app.route('/start', methods=['POST'])
def start_bot():
    global bot_process
    if bot_process is None or bot_process.poll() is not None:
        bot_process = subprocess.Popen(["python", "bot.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "Бот запущен", 200
    else:
        return "Бот уже запущен", 400

@app.route('/stop', methods=['POST'])
def stop_bot():
    global bot_process
    if bot_process is not None and bot_process.poll() is None:
        bot_process.terminate()
        bot_process = None
        return "Бот остановлен", 200
    else:
        return "Бот не запущен", 400

@app.route('/restart', methods=['POST'])
def restart_bot():
    stop_bot()
    start_bot()
    return "Бот перезапущен", 200

@app.route('/logs', methods=['GET'])
def get_logs():
    if os.path.exists("logs.txt"):
        return send_file("logs.txt", as_attachment=True)
    else:
        return "Логи не найдены", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)