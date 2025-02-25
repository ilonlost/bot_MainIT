from conn.conn import get_db_connection
from conn.conn import bot
from datetime import datetime
import logging
import schedule
import time


def delete_main_menu_message(chat_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
           
            cursor.execute("SELECT bot_message_id FROM message_pairs WHERE chat_id = ? ORDER BY timestamp DESC LIMIT 1", (chat_id,))
            result = cursor.fetchone()
            if result:
                bot_message_id = result[0]
                
                bot.delete_message(chat_id, bot_message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщения из главного меню: {str(e)}", exc_info=True)

def delete_previous_service_message(chat_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT bot_message_id FROM message_pairs 
                WHERE chat_id = ? AND bot_message_id IS NOT NULL 
                ORDER BY timestamp DESC LIMIT 1
            """, (chat_id,))
            result = cursor.fetchone()
            if result:
                bot_message_id = result[0]
                
                bot.delete_message(chat_id, bot_message_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении старого сообщения в сервисе: {str(e)}", exc_info=True)


def delete_previous_interaction(chat_id, previous_bot_message_id):
    try:
        
        bot.delete_message(chat_id, previous_bot_message_id)

        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_message_id FROM message_pairs 
                WHERE chat_id = ? AND bot_message_id = ? 
                LIMIT 1
            """, (chat_id, previous_bot_message_id))
            user_message_id = cursor.fetchone()
            if user_message_id:
                bot.delete_message(chat_id, user_message_id[0])
                
                cursor.execute("""
                    DELETE FROM message_pairs 
                    WHERE chat_id = ? AND (bot_message_id = ? OR user_message_id = ?)
                """, (chat_id, previous_bot_message_id, user_message_id[0]))
                conn.commit()
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщений: {str(e)}")

def save_message_pair(chat_id, bot_message_id=None, user_message_id=None):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO message_pairs (chat_id, bot_message_id, user_message_id, timestamp)
                VALUES (?, ?, ?, ?)
            """, (chat_id, bot_message_id, user_message_id, datetime.now()))
            conn.commit()
    except Exception as e:
        logging.error(f"Ошибка при сохранении пар сообщений: {str(e)}", exc_info=True)

def delete_old_messages():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT chat_id FROM message_pairs")
            chat_ids = cursor.fetchall()
            for (chat_id,) in chat_ids:
                delete_expired_message_pairs(chat_id)
    except Exception as e:
        logging.error(f"Ошибка при удалении старых сообщений: {str(e)}")

def delete_previous_list_messages(chat_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            
            cursor.execute("""
                SELECT bot_message_id, user_message_id 
                FROM message_pairs 
                WHERE chat_id = ?
            """, (chat_id,))
            previous_messages = cursor.fetchall()

            
            for bot_message_id, user_message_id in previous_messages:
                try:
                    if user_message_id:
                        bot.delete_message(chat_id, user_message_id)
                    if bot_message_id:
                        bot.delete_message(chat_id, bot_message_id)
                except Exception as e:
                    logging.error(f"Ошибка при удалении сообщения из Telegram: {str(e)}")

            
            cursor.execute("""
                DELETE FROM message_pairs 
                WHERE chat_id = ?
            """, (chat_id,))
            conn.commit()

            print(f"Удалены старые сообщения для чата {chat_id}.")
    except Exception as e:
        logging.error(f"Ошибка при удалении предыдущих сообщений: {str(e)}", exc_info=True)


def delete_session_messages(chat_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT user_message_id, bot_message_id FROM message_pairs WHERE chat_id = ?", (chat_id,))
            messages = cursor.fetchall()

            for user_message_id, bot_message_id in messages:
                try:
                    if user_message_id:
                        bot.delete_message(chat_id, user_message_id)  
                    if bot_message_id:
                        bot.delete_message(chat_id, bot_message_id)  
                except Exception as e:
                    logging.warning(f"Не удалось удалить сообщение: {str(e)}")

            
            cursor.execute("DELETE FROM message_pairs WHERE chat_id = ?", (chat_id,))
            conn.commit()
    except Exception as e:
        logging.error(f"Ошибка при удалении сообщений сессии: {str(e)}", exc_info=True)

def delete_expired_message_pairs(chat_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            
            cursor.execute("""
                SELECT bot_message_id, user_message_id 
                FROM message_pairs 
                WHERE chat_id = ? AND timestamp < DATEADD(MINUTE, -1, GETDATE())
            """, (chat_id,))
            expired_messages = cursor.fetchall()

            
            for bot_message_id, user_message_id in expired_messages:
                try:
                    if user_message_id:
                        bot.delete_message(chat_id, user_message_id)
                    if bot_message_id:
                        bot.delete_message(chat_id, bot_message_id)
                except Exception as e:
                    logging.error(f"Ошибка при удалении сообщения из Telegram: {str(e)}")

            
            cursor.execute("""
                DELETE FROM message_pairs 
                WHERE chat_id = ? AND timestamp < DATEADD(MINUTE, -1, GETDATE())
            """, (chat_id,))
            conn.commit()

            print(f"Удалены устаревшие сообщения для чата {chat_id}.")
    except Exception as e:
        logging.error(f"Ошибка при удалении устаревших пар сообщений: {str(e)}", exc_info=True)

def delete_all_message_pairs(chat_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT bot_message_id, user_message_id FROM message_pairs WHERE chat_id = ?", (chat_id,))
            rows = cursor.fetchall()

            
            for bot_message_id, user_message_id in rows:
                try:
                    if bot_message_id:
                        bot.delete_message(chat_id, bot_message_id)
                except Exception as e:
                    logging.error(f"Ошибка при удалении сообщения бота {bot_message_id}: {e}")

                try:
                    if user_message_id:
                        bot.delete_message(chat_id, user_message_id)
                except Exception as e:
                    logging.error(f"Ошибка при удалении сообщения пользователя {user_message_id}: {e}")

            
            cursor.execute("DELETE FROM message_pairs WHERE chat_id = ?", (chat_id,))
            conn.commit()

    except Exception as e:
        logging.error(f"Ошибка при удалении записей из базы данных: {e}")




