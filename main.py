from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# isort: off
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# isort: on
from src import settings
from src.enums import Command
from src.logger import logger
from src.sheets_client import sheet
from src.translation import get_translator


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    IMAGE_CAPTION_TEXT = (
        "🇬🇧 EN: Thanks for being with us this week. Please give us the feedback so we can improve the camp for the next year!\n"
        "🇺🇦 UA: Дякую, що провели з нами цей тиждень. Це було незабутньо. Заповніть, будь ласка, форму, щоб ми могли покращити табір наступного року!"
    )
    with open(settings.SRC_FOLDER / "images" / "intro.jpg", "rb") as photo:
        await update.message.reply_photo(photo=photo, caption=IMAGE_CAPTION_TEXT)

    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    REPLY_TEXT = "🇬🇧 EN: Please choose a language:\n🇺🇦 UA: Оберіть, будь ласка, мову:"
    await update.message.reply_text(REPLY_TEXT, reply_markup=reply_markup)
    return Command.LANGUAGE_SELECTION


async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang_code = query.data.replace("lang_", "")
    _ = get_translator(lang_code).gettext
    context.user_data["_"] = _
    context.user_data["answers"] = []
    context.user_data["question_index"] = 0

    question_text = _("question1")
    await query.message.reply_text(question_text)
    context.user_data["question_index"] = 1
    return Command.ASK_QUESTION


async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ = context.user_data["_"]
    index = context.user_data.get("question_index", 0)
    context.user_data["answers"].append(update.message.text)
    if index == settings.TOTAL_QUESTIONS:
        await update.message.reply_text("Thank you for your feedback!")
        sheet.append_row(context.user_data["answers"])
        return ConversationHandler.END

    next_question = _(settings.QUESTION_KEYS[index])
    await update.message.reply_text(next_question)
    context.user_data["question_index"] = index + 1
    return Command.ASK_QUESTION


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Command.LANGUAGE_SELECTION: [
                CallbackQueryHandler(handle_language_selection, pattern=r"^lang_")
            ],
            Command.ASK_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)
            ],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.run_polling()
