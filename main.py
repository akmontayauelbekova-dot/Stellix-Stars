import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO)

WELCOME = (
    "✦ STELLIX STARS ✦\n\n"
    "Добро пожаловать в наш цифровой магазин!\n"
    "Выберите интересующий вас раздел ниже."
)

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐ Telegram Stars", callback_data="stars")],
        [InlineKeyboardButton("👑 Telegram Premium", callback_data="premium")],
        [InlineKeyboardButton("🛍 Мои заявки", callback_data="orders")],
        [InlineKeyboardButton("💬 Поддержка", callback_data="support")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        WELCOME,
        reply_markup=main_menu()
    )

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "stars":
        keyboard = [
            [InlineKeyboardButton("⭐ 50 Stars", callback_data="50")],
            [InlineKeyboardButton("⭐ 100 Stars", callback_data="100")],
            [InlineKeyboardButton("⭐ 250 Stars", callback_data="250")],
            [InlineKeyboardButton("⭐ 500 Stars", callback_data="500")],
            [InlineKeyboardButton("⭐ 1000 Stars", callback_data="1000")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="home")]
        ]
        await query.edit_message_text(
            "⭐ TELEGRAM STARS\n\n"
            "Выберите количество, чтобы узнать подробности.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "premium":
        await query.edit_message_text(
            "👑 TELEGRAM PREMIUM\n\n"
            "Узнать информацию о доступных вариантах можно через поддержку.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("💬 Поддержка", callback_data="support")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="home")]
            ])
        )

    elif query.data in ["50", "100", "250", "500", "1000"]:
        context.user_data["selected"] = query.data
        context.user_data["waiting"] = True

        await query.edit_message_text(
            f"⭐ Вы выбрали {query.data} Stars.\n\n"
            "Напишите ваш Telegram username (@username), "
            "чтобы отправить запрос на уточнение стоимости.\n\n"
            "Это пока только заявка, не оплата."
        )

    elif query.data == "orders":
        await query.edit_message_text(
            "🛍 Ваши заявки\n\n"
            "Для просмотра статуса обратитесь в поддержку.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="home")]
            ])
        )

    elif query.data == "support":
        await query.edit_message_text(
            "💬 Поддержка STELLIX STARS\n\n"
            "По вопросам обращайтесь к администратору магазина.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Назад", callback_data="home")]
            ])
        )

    elif query.data == "home":
        await query.edit_message_text(
            WELCOME,
            reply_markup=main_menu()
        )

async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting"):
        return

    username = update.message.text.strip()

    if len(username) > 100:
        await update.message.reply_text("Слишком длинный текст. Попробуйте ещё раз.")
        return

    selected = context.user_data.get("selected", "не указано")
    user = update.effective_user

    admin_id = ADMIN_ID

    if admin_id:
        try:
            await context.bot.send_message(
                chat_id=int(admin_id),
                text=(
                    "✦ НОВАЯ ЗАЯВКА STELLIX STARS\n\n"
                    f"Товар: {selected} Stars\n"
                    f"Получатель: {username}\n"
                    f"Покупатель: @{user.username or 'без username'}\n"
                    f"ID: {user.id}"
                )
            )
        except Exception:
            logging.exception("Не удалось отправить заявку администратору")

    context.user_data["waiting"] = False

    await update.message.reply_text(
        "✦ Ваша заявка принята!\n\n"
        "Администратор сможет связаться с вами после проверки.",
        reply_markup=main_menu()
    )

def main():
    if not TOKEN:
        raise RuntimeError("Не задан BOT_TOKEN")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)
    )

    print("STELLIX STARS is running!")
    app.run_polling()

if __name__ == "__main__":
    main()


