from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackContext, CommandHandler, CallbackQueryHandler

from bot.services.schedule_service import ScheduleService
from bot.handlers.students import start_student
from bot.handlers.teachers import start_teacher


def register_start_handlers(app: Application, schedule: ScheduleService) -> None:
    app.add_handler(CommandHandler("start", on_start))
    app.add_handler(CallbackQueryHandler(lambda u, c: on_menu_click(u, c, schedule), pattern=r"^menu:") )


async def on_start(update: Update, context: CallbackContext):
    buttons = [
        [InlineKeyboardButton(text="🎓 Student", callback_data="menu:student"), InlineKeyboardButton(text="👨‍🏫 Teacher", callback_data="menu:teacher")],
    ]
    await update.effective_chat.send_message("Assalawma aleykum! Kerekli bólimdi tańlań:", reply_markup=InlineKeyboardMarkup(buttons))


async def on_menu_click(update: Update, context: CallbackContext, schedule: ScheduleService):
    q = update.callback_query
    await q.answer()
    if q.data == "menu:student":
        await start_student(update, context, schedule)
    elif q.data == "menu:teacher":
        await start_teacher(update, context, schedule)


