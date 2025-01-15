import sqlite3
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

import os
import psycopg2

# Получаем URL базы данных из переменной окружения
DATABASE_URL = os.getenv("DATABASE_URL")

# Подключаемся к базе данных
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()


# Токен вашего бота
TOKEN = "7428205184:AAHKGl0ek2ZwMgZtz4WGO0sTJX6z927xvVM"

# Этапы диалога
CALORIES, PROTEINS, FATS, CARBS = range(4)

# Функция инициализации базы данных
def init_db():
    conn = sqlite3.connect("nutrition.db")  # Подключение к базе данных
    cursor = conn.cursor()

    # Таблица для хранения данных пользователя
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id INTEGER PRIMARY KEY,
            calories REAL,
            proteins REAL,
            fats REAL,
            carbs REAL
        )
    """)

    # Таблица с блюдами
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_type TEXT,
            category TEXT,
            name TEXT,
            calories REAL,
            proteins REAL,
            fats REAL,
            carbs REAL,
            serving_weight REAL
        )
    """)
    conn.commit()
    conn.close()

# Начало диалога
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Чтобы начать, мне нужно узнать ваши потребности. "
        "Сколько калорий вам нужно в день? (введите число)"
    )
    return CALORIES

# Сохранение калорий и переход к белкам
def set_calories(update: Update, context: CallbackContext):
    try:
        context.user_data['calories'] = float(update.message.text)
        update.message.reply_text("Сколько белков вам нужно в день? (в граммах)")
        return PROTEINS
    except ValueError:
        update.message.reply_text("Пожалуйста, введите корректное число.")
        return CALORIES

# Сохранение белков и переход к жирам
def set_proteins(update: Update, context: CallbackContext):
    try:
        context.user_data['proteins'] = float(update.message.text)
        update.message.reply_text("Сколько жиров вам нужно в день? (в граммах)")
        return FATS
    except ValueError:
        update.message.reply_text("Пожалуйста, введите корректное число.")
        return PROTEINS

# Сохранение жиров и переход к углеводам
def set_fats(update: Update, context: CallbackContext):
    try:
        context.user_data['fats'] = float(update.message.text)
        update.message.reply_text("Сколько углеводов вам нужно в день? (в граммах)")
        return CARBS
    except ValueError:
        update.message.reply_text("Пожалуйста, введите корректное число.")
        return FATS

# Сохранение углеводов и завершение диалога
def set_carbs(update: Update, context: CallbackContext):
    try:
        context.user_data['carbs'] = float(update.message.text)

        # Сохранение данных в базу
        user_id = update.effective_user.id
        conn = sqlite3.connect("nutrition.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_data (user_id, calories, proteins, fats, carbs)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, context.user_data['calories'], context.user_data['proteins'], context.user_data['fats'], context.user_data['carbs']))
        conn.commit()
        conn.close()

        update.message.reply_text(
            "Спасибо! Ваши данные сохранены. Теперь я составлю для вас меню. "
        )
        return suggest_menu(update, context)
    except ValueError:
        update.message.reply_text("Пожалуйста, введите корректное число.")
        return CARBS

# Функция составления меню
def suggest_menu(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    conn = sqlite3.connect("nutrition.db")
    cursor = conn.cursor()

    # Получение данных пользователя
    cursor.execute("SELECT calories, proteins, fats, carbs FROM user_data WHERE user_id = ?", (user_id,))
    user_data = cursor.fetchone()

    if not user_data:
        update.message.reply_text("Ваши данные не найдены. Пожалуйста, начните с команды /start.")
        return ConversationHandler.END

    # Подбор блюд
    cursor.execute("""
        SELECT name, serving_weight, calories, proteins, fats, carbs 
        FROM meals
        LIMIT 5
    """)  # Условие подбора можно усложнить в зависимости от потребностей
    meals = cursor.fetchall()

    conn.close()

    # Формирование ответа
    if meals:
        response = "Вот примерное меню для вас:\n"
        for meal in meals:
            response += (f"- {meal[0]}: {meal[1]} г, "
                         f"{meal[2]} ккал, {meal[3]} г белков, {meal[4]} г жиров, {meal[5]} г углеводов\n")
        update.message.reply_text(response)
    else:
        update.message.reply_text("В базе данных пока нет блюд для составления меню.")
    
    return ConversationHandler.END

# Завершение диалога
def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Диалог отменен.")
    return ConversationHandler.END

# Главный обработчик
def main():
    init_db()  # Инициализация базы данных

    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Диалог для сбора данных пользователя
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CALORIES: [MessageHandler(Filters.text & ~Filters.command, set_calories)],
            PROTEINS: [MessageHandler(Filters.text & ~Filters.command, set_proteins)],
            FATS: [MessageHandler(Filters.text & ~Filters.command, set_fats)],
            CARBS: [MessageHandler(Filters.text & ~Filters.command, set_carbs)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()

# Основной блок
if __name__ == "__main__":
    main()
