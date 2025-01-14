from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Токен от BotFather
TOKEN = "7428205184:AAHKGl0ek2ZwMgZtz4WGO0sTJX6z927xvVM"

# Главное меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Составить меню", callback_data="menu")],
        [InlineKeyboardButton("Составить список покупок по меню", callback_data="shopping_list")],
        [InlineKeyboardButton("Книга рецептов по меню", callback_data="recipe_book")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Привет! Выбери, что ты хочешь от меню-конструктора (ткни в нужную кнопку)", reply_markup=reply_markup)

# Обработка нажатий в меню
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu":
        keyboard = [
            [InlineKeyboardButton("Составить рандомное меню (не хочу думать и выбирать)", callback_data="random_menu")],
            [InlineKeyboardButton("Составить меню самостоятельно", callback_data="manual_menu")],
            [InlineKeyboardButton("Посмотреть всё меню целиком", callback_data="view_menu")],
            [InlineKeyboardButton("Вернуться в главное меню", callback_data="main_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Чтобы составить меню, выбери из трёх вариантов, которые подойдут для тебя", reply_markup=reply_markup)

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
            [InlineKeyboardButton("Посмотреть меню по приему пищи", callback_data="menu_by_meal")],
            [InlineKeyboardButton("Посмотреть всё меню целиком", callback_data="full_menu")],
            [InlineKeyboardButton("Вернуться в меню выбора", callback_data="menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Выбери тип меню", reply_markup=reply_markup)

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
