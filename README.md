# bot_MainIT
Описание проекта
Проект представляет собой Telegram-бота, разработанного с использованием библиотеки telebot и подключенного к базе данных MSSQL через pyodbc. Бот предназначен для управления задачами, пользователями и оборудованием, а также для выполнения различных операций, связанных с базой данных. Бот поддерживает функции создания, обновления и удаления записей в таблицах, а также предоставляет информацию о текущих задачах и пользователях.

Команды для установки библиотек
Для установки необходимых библиотек выполните следующие команды:

bash
Copy
pip install logging
pip install time
pip install pyTelegramBotAPI
pip install datetime
pip install schedule
pip install os-sys
pip install pywin32
pip install python-docx
pip install qrcode[pil]
pip install pyzbar
pip install pillow
pip install subprocess.run
pip install pyodbc
Логика установки Python
Установка Python:

Скачайте Python с официального сайта: python.org.

Убедитесь, что во время установки выбрана опция "Add Python to PATH".

Создание виртуального окружения (опционально, но рекомендуется):

Перейдите в директорию вашего проекта.

Создайте виртуальное окружение:

bash
Copy
python -m venv venv
Активируйте виртуальное окружение:

На Windows:

bash
Copy
venv\Scripts\activate
На macOS/Linux:

bash
Copy
source venv/bin/activate
Установка библиотек:

Установите необходимые библиотеки, используя команды, приведенные выше.

SQL-запросы
Вот примеры SQL-запросов, которые могут быть использованы в вашем проекте:

Получение всех ячеек:

sql
Copy
SELECT cell_number, description, short_name FROM dbo.Cells;
Получение всех задач:

sql
Copy
SELECT id, task_name, description, priority, type, status, created_at, updated_at, creator, assignee FROM dbo.tasks;
Добавление новой задачи:

sql
Copy
INSERT INTO dbo.tasks (task_name, description, priority, type, status, created_at, updated_at, creator, assignee)
VALUES ('Новая задача', 'Описание задачи', 'Высокий', 'Тип задачи', 'Новая', GETDATE(), GETDATE(), 'Создатель', 'Исполнитель');
Обновление статуса задачи:

sql
Copy
UPDATE dbo.tasks SET status = 'В процессе' WHERE id = 1;
Получение информации о пользователе:

sql
Copy
SELECT username, group_access, work_schedule FROM dbo.users WHERE telogram_id = 123456789;
Логика работы бота
Инициализация бота:

Бот инициализируется с использованием токена, полученного от BotFather.

Подключение к базе данных MSSQL осуществляется через pyodbc.

Команды бота:

/start - Приветственное сообщение и краткая информация о боте.

/tasks - Получение списка всех задач.

/addtask - Добавление новой задачи.

/updatetask - Обновление статуса задачи.

/users - Получение информации о пользователях.

Логирование:

Все действия бота логируются с использованием библиотеки logging.

Расписание:

Для выполнения периодических задач используется библиотека schedule.

Заключение
Этот проект демонстрирует, как можно создать Telegram-бота для управления задачами и пользователями с использованием MSSQL и Python. Бот поддерживает основные CRUD-операции и предоставляет удобный интерфейс для взаимодействия с базой данных через Telegram.

Если у вас есть дополнительные вопросы или требуется больше информации, не стесняйтесь спрашивать!
