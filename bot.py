from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка подключения к базе данных в коде

import psycopg2

DATABASE_URL = "postgresql://eat_and_be_slim_db_user:RhQNjgwp1gLy5pgDKdla1ekWtcoy8xr2@dpg-cu3417hopnds7381ndq0-a/eat_and_be_slim_db"  # Замените на URL вашей базы данных

# Установить подключение
def connect_to_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print("Успешное подключение к базе данных")
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None

# Создание таблицы для хранения данных о блюдах

def create_table():
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS meals (
                        id SERIAL PRIMARY KEY,
                        meal_type VARCHAR(50),
                        category VARCHAR(100),
                        name VARCHAR(255),
                        calories FLOAT,
                        proteins FLOAT,
                        fats FLOAT,
                        carbs FLOAT,
                        serving_weight FLOAT
                    );
                """)
                conn.commit()
                print("Таблица успешно создана или уже существует")
        except Exception as e:
            print(f"Ошибка при создании таблицы: {e}")
        finally:
            conn.close()


#Загрузка данных в базу

import pandas as pd

def upload_data(file_path):
    conn = connect_to_db()
    if conn:
        try:
            data = pd.read_excel(file_path)
            with conn.cursor() as cur:
                for _, row in data.iterrows():
                    cur.execute("""
                        INSERT INTO meals (meal_type, category, name, calories, proteins, fats, carbs, serving_weight)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """, (row['meal_type'], row['category'], row['name'], row['calories'],
                          row['proteins'], row['fats'], row['carbs'], row['serving_weight']))
                conn.commit()
                print("Данные успешно загружены в базу")
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")
        finally:
            conn.close()



# Токен от BotFather
TOKEN = "7428205184:AAHKGl0ek2ZwMgZtz4WGO0sTJX6z927xvVM"

# Главное меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("1. Составить меню", callback_data="menu")],
        [InlineKeyboardButton("2. Составить список покупок по меню", callback_data="shopping_list")],
        [InlineKeyboardButton("3. Книга рецептов по меню", callback_data="recipe_book")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выберите действие:", reply_markup=reply_markup)

# Обработка нажатий в меню
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu":
        keyboard = [
            [InlineKeyboardButton("1.1. Составить рандомное меню", callback_data="random_menu")],
            [InlineKeyboardButton("1.2. Составить меню самостоятельно", callback_data="manual_menu")],
            [InlineKeyboardButton("1.3. Посмотреть всё меню", callback_data="view_menu")],
            [InlineKeyboardButton("Вернуться в главное меню", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите действие:", reply_markup=reply_markup)

    elif query.data == "random_menu":
        await query.edit_message_text("Функция для генерации случайного меню в разработке.")

    elif query.data == "manual_menu":
        keyboard = [
            [InlineKeyboardButton("Завтрак", callback_data="breakfast")],
            [InlineKeyboardButton("Обед", callback_data="lunch")],
            [InlineKeyboardButton("Перекус", callback_data="snack")],
            [InlineKeyboardButton("Ужин", callback_data="dinner")],
            [InlineKeyboardButton("Десерт", callback_data="dessert")],
            [InlineKeyboardButton("Вернуться в меню выбора", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выберите прием пищи:", reply_markup=reply_markup)

    elif query.data == "view_menu":
        keyboard = [
            [InlineKeyboardButton("1.3.1. Посмотреть меню по приему пищи", callback_data="menu_by_meal")],
            [InlineKeyboardButton("1.3.2. Посмотреть меню целиком", callback_data="full_menu")],
            [InlineKeyboardButton("Вернуться в меню выбора", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Как вы хотите просмотреть меню?", reply_markup=reply_markup)

    elif query.data == "shopping_list":
        await query.edit_message_text("Функция для составления списка покупок в разработке.")

    elif query.data == "recipe_book":
        await query.edit_message_text("Функция для создания книги рецептов в разработке.")

    elif query.data == "main_menu":
        await start(update, context)

# Главный обработчик
def main():
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(menu_handler))

    # Запуск бота
    application.run_polling()

if __name__ == "__main__":
    main()
