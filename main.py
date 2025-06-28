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
from src.sheets_client import feedback_sheet, questions_sheet
from src.translation import get_translator


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command = update.message.text.split()[0]

    if command == "/feedback":
        IMAGE_CAPTION_TEXT = (
            "🇬🇧 EN: Thanks for being with us this week. Please give us the feedback so we can improve the camp for the next year!\n"
            "🇺🇦 UA: Дякую, що провели з нами цей тиждень. Це було незабутньо. Заповніть, будь ласка, форму, щоб ми могли покращити табір наступного року!"
        )
        with open(settings.SRC_FOLDER / "images" / "intro.jpg", "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=IMAGE_CAPTION_TEXT)

        context.user_data["next_state"] = Command.ANSWER_QUESTION
    else:
        context.user_data["next_state"] = Command.ASK_QUESTION

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
    lang_code = query.data.lstrip("lang_")
    _ = get_translator(lang_code).gettext
    context.user_data["_"] = _

    next_state = context.user_data.get("next_state")

    if next_state == Command.ASK_QUESTION:
        await query.message.reply_text(_("What's your question?"))
        return Command.ASK_QUESTION
    else:
        context.user_data["answers"] = []
        context.user_data["question_index"] = 2
        await query.message.reply_text(_("question1"))

        return Command.ANSWER_QUESTION


async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _ = context.user_data["_"]
    index = context.user_data.get("question_index", 1)
    context.user_data["answers"].append(update.message.text)
    if index > settings.TOTAL_QUESTIONS:
        await update.message.reply_text(_("Thank you for your feedback!"))
        feedback_sheet.append_row(context.user_data["answers"])
        return ConversationHandler.END

    next_question = _(f"question{index}")
    await update.message.reply_text(next_question)
    context.user_data["question_index"] = index + 1
    return Command.ANSWER_QUESTION


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions_sheet.append_row([update.message.text])
    _ = context.user_data["_"]
    await update.message.reply_text(_("Good question, thanks!"))
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("feedback", start),
            CommandHandler("question", start),
        ],
        states={
            Command.LANGUAGE_SELECTION: [
                CallbackQueryHandler(handle_language_selection, pattern=r"^lang_")
            ],
            Command.ANSWER_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)
            ],
            Command.ASK_QUESTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()
