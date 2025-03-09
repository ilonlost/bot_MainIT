import customtkinter as ctk
from tkinter import messagebox, scrolledtext, ttk
import requests
import subprocess
import os
import sys
import psutil

# Настройка темы и внешнего вида
ctk.set_appearance_mode("Dark")  # Темная тема по умолчанию
ctk.set_default_color_theme("blue")  # Цветовая тема

# Адрес API на удалённом сервере
API_URL = "http://10.10.66.70:5000"  # Укажите IP-адрес вашего сервера

class BotManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Управление ботами")
        self.geometry("800x600")  # Увеличим размер окна
        self.minsize(600, 400)  # Минимальный размер окна

        # Переменная для хранения состояния темы
        self.dark_mode = True

        # Создание интерфейса
        self.create_widgets()

    def create_widgets(self):
        """Создание элементов интерфейса."""
        # Верхняя панель (основное меню)
        self.top_menu_frame = ctk.CTkFrame(self, fg_color="#2E86C1")  # Синий фон
        self.top_menu_frame.pack(pady=10, padx=10, fill="x")

        # Кнопки основного меню
        self.it_fk_button = ctk.CTkButton(self.top_menu_frame, text="IT ФК", command=self.open_it_fk, height=40, fg_color="#3498DB", hover_color="#1B4F72")
        self.it_fk_button.pack(side="left", padx=5, fill="x", expand=True)

        self.notifications_button = ctk.CTkButton(self.top_menu_frame, text="Уведомления простои", command=self.open_notifications, height=40, fg_color="#3498DB", hover_color="#1B4F72")
        self.notifications_button.pack(side="left", padx=5, fill="x", expand=True)

        self.other_bots_button = ctk.CTkButton(self.top_menu_frame, text="Остальные боты", command=self.open_other_bots, height=40, fg_color="#3498DB", hover_color="#1B4F72")
        self.other_bots_button.pack(side="left", padx=5, fill="x", expand=True)

        # Верхняя панель (дополнительные функции)
        self.top_extra_frame = ctk.CTkFrame(self, fg_color="#34495E")  # Темно-серый фон
        self.top_extra_frame.pack(pady=10, padx=10, fill="x")

        # Кнопка переключения темы
        self.theme_button = ctk.CTkButton(self.top_extra_frame, text="🌙", command=self.toggle_theme, width=40,
                                          height=40)
        self.theme_button.pack(side="left", padx=5)

        # Кнопка настроек
        self.settings_button = ctk.CTkButton(self.top_extra_frame, text="⚙️", command=self.open_settings, width=40,
                                             height=40)
        self.settings_button.pack(side="right", padx=5)

    def open_it_fk(self):
        """Открывает окно управления IT ФК."""
        self.clear_window()
        self.it_fk_frame = ctk.CTkFrame(self)
        self.it_fk_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Статус
        self.status_label = ctk.CTkLabel(self.it_fk_frame, text="Статус: Ожидает команду")
        self.status_label.pack(pady=10)

        # Кнопки управления IT ФК
        self.start_button = ctk.CTkButton(self.it_fk_frame, text="Запустить", command=self.start_bot, height=40)
        self.start_button.pack(pady=10, padx=10, fill="x")

        self.stop_button = ctk.CTkButton(self.it_fk_frame, text="Остановить", command=self.stop_bot, height=40)
        self.stop_button.pack(pady=10, padx=10, fill="x")

        self.restart_button = ctk.CTkButton(self.it_fk_frame, text="Перезапустить", command=self.restart_bot, height=40)
        self.restart_button.pack(pady=10, padx=10, fill="x")

        self.log_button = ctk.CTkButton(self.it_fk_frame, text="Лог", command=self.show_logs, height=40)
        self.log_button.pack(pady=10, padx=10, fill="x")

    def open_notifications(self):
        """Открывает окно управления уведомлениями."""
        self.clear_window()
        self.it_fk_frame = ctk.CTkFrame(self)
        self.it_fk_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Статус
        self.status_label = ctk.CTkLabel(self.it_fk_frame, text="Статус: Ожидает команду")
        self.status_label.pack(pady=10)

        # Кнопки управления IT ФК
        self.start_button = ctk.CTkButton(self.it_fk_frame, text="Запустить", command=self.start_bot, height=40)
        self.start_button.pack(pady=10, padx=10, fill="x")

        self.stop_button = ctk.CTkButton(self.it_fk_frame, text="Остановить", command=self.stop_bot, height=40)
        self.stop_button.pack(pady=10, padx=10, fill="x")

        self.restart_button = ctk.CTkButton(self.it_fk_frame, text="Перезапустить", command=self.restart_bot, height=40)
        self.restart_button.pack(pady=10, padx=10, fill="x")

        self.log_button = ctk.CTkButton(self.it_fk_frame, text="Лог", command=self.show_logs, height=40)
        self.log_button.pack(pady=10, padx=10, fill="x")

    def open_other_bots(self):
        """Открывает окно с таблицей ботов"""
        self.clear_window()
        frame = ctk.CTkFrame(self)
        frame.pack(pady=10, padx=10, fill="both", expand=True)

        table = ttk.Treeview(frame, columns=("Имя", "Ссылка", "Описание"), show="headings")
        table.heading("Имя", text="Имя")
        table.heading("Ссылка", text="Ссылка")
        table.heading("Описание", text="Описание")

        table.pack(fill="both", expand=True)

        table.insert("", "end", values=("Бот1", "http://example.com", "Описание1"))
        table.insert("", "end", values=("Бот2", "http://example.com", "Описание2"))

    def open_settings(self):
        """Открывает окно настроек."""
        self.clear_window()
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Поле для заметок (примеры команд)
        self.notes_text = scrolledtext.ScrolledText(self.settings_frame, width=100, height=10, font=("Consolas", 12))
        self.notes_text.pack(pady=10, padx=10, fill="x")
        self.notes_text.insert("1.0", "Примеры команд:\n"
                                     "1. Вывод запущенных процессов Python: tasklist | findstr python\n"
                                     "2. Завершение всех процессов Python: taskkill /f /im python.exe\n"
                                     "3. Перезагрузка сервера: shutdown /r /t 0\n"
                                     "4. Проверка сети: ping 10.10.66.10\n")

        # Поле для ввода команд
        self.cmd_entry = ctk.CTkEntry(self.settings_frame, placeholder_text="Введите команду...", width=600)
        self.cmd_entry.pack(pady=10, padx=10, fill="x")

        # Кнопка для выполнения команд
        self.run_cmd_button = ctk.CTkButton(self.settings_frame, text="Выполнить команду", command=self.run_cmd, height=40)
        self.run_cmd_button.pack(pady=10, padx=10, fill="x")

        # Окно вывода CMD
        self.cmd_output_text = scrolledtext.ScrolledText(self.settings_frame, width=100, height=20, font=("Consolas", 12))
        self.cmd_output_text.pack(pady=10, padx=10, fill="both", expand=True)
        self.cmd_output_text.configure(state="disabled")  # Запрет редактирования

    def clear_window(self):
        """Очищает текущее окно."""
        for widget in self.winfo_children():
            if widget not in [self.top_menu_frame, self.top_extra_frame]:
                widget.destroy()

    def toggle_theme(self):
        """Переключает тему (темный/светлый режим)."""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            ctk.set_appearance_mode("Dark")
            self.theme_button.configure(text="Dark 🌙")
        else:
            ctk.set_appearance_mode("Light")
            self.theme_button.configure(text="Light ☀️")

    def start_bot(self):
        """Запуск бота через API."""
        try:
            response = requests.post(f"{API_URL}/start")
            messagebox.showinfo("Информация", response.text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить бота: {e}")

    def stop_bot(self):
        """Остановка бота через API."""
        try:
            response = requests.post(f"{API_URL}/stop")
            messagebox.showinfo("Информация", response.text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить бота: {e}")

    def restart_bot(self):
        """Перезапуск бота через API."""
        try:
            response = requests.post(f"{API_URL}/restart")
            messagebox.showinfo("Информация", response.text)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось перезапустить бота: {e}")

    def show_logs(self):
        """Показать лог бота."""
        try:
            log_file = "logs.txt"
            if os.path.exists(log_file):
                with open(log_file, "r") as file:
                    log_content = file.read()
                    messagebox.showinfo("Лог", log_content)
            else:
                messagebox.showwarning("Предупреждение", "Файл лога не найден.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть лог: {e}")

    def run_cmd(self):
        """Выполнить команду из поля ввода."""
        command = self.cmd_entry.get()
        if command:
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                self.cmd_output_text.configure(state="normal")
                self.cmd_output_text.delete("1.0", "end")
                self.cmd_output_text.insert("1.0", result.stdout)
                self.cmd_output_text.configure(state="disabled")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось выполнить команду: {e}")
        else:
            messagebox.showwarning("Предупреждение", "Введите команду.")

if __name__ == "__main__":
    app = BotManagerApp()
    app.mainloop()