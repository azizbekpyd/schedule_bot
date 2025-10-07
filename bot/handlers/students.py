from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackContext, CommandHandler, CallbackQueryHandler

from bot.keyboards.menus import chunk_buttons
from bot.services.schedule_service import ScheduleService


DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

DAY_NAMES = {
    "Mon": "Dúyshembi",
    "Tue": "Shiyshembi", 
    "Wed": "Sárshembi",
    "Thu": "Piyshembi",
    "Fri": "Juma",
    "Sat": "Shembi"
}


def register_student_handlers(app: Application, schedule: ScheduleService) -> None:
	app.add_handler(CommandHandler("student", lambda u, c: start_student(u, c, schedule)))
	app.add_handler(CallbackQueryHandler(lambda u, c: on_group_selected(u, c, schedule), pattern=r"^st_group:"))
	app.add_handler(CallbackQueryHandler(lambda u, c: on_day_selected(u, c, schedule), pattern=r"^st_day:"))


async def start_student(update: Update, context: CallbackContext, schedule: ScheduleService):
	groups = schedule.get_groups()
	if not groups:
		await update.effective_chat.send_message("Tablica ele júklenbegen.")
		return

	buttons = [[InlineKeyboardButton(text=g, callback_data=f"st_group:{g}")] for g in groups]
	markup = InlineKeyboardMarkup(chunk_buttons(buttons))
	await update.effective_chat.send_message("Gruppanı tańlań:", reply_markup=markup)


async def on_group_selected(update: Update, context: CallbackContext, schedule: ScheduleService):
	query = update.callback_query
	await query.answer()
	group = query.data.split(":", 1)[1]
	# Ask for day
	buttons = [[InlineKeyboardButton(text=day, callback_data=f"st_day:{group}:{day}")] for day in DAYS]
	markup = InlineKeyboardMarkup(chunk_buttons(buttons, row_size=3))
	await query.edit_message_text(f"Gruppa: {group}.\nKundi tańlań:", reply_markup=markup)


async def on_day_selected(update: Update, context: CallbackContext, schedule: ScheduleService):
	query = update.callback_query
	await query.answer()
	_, group, day = query.data.split(":", 2)
	rows = schedule.get_group_day(group, day)
	if not rows:
		await query.edit_message_text(f"{group} gruppasında {day} kúni sabaq joq.")
		return

	day_name = DAY_NAMES.get(day, day)
	lines = [f"<b>{group} — {day_name} ({day})</b>", ""]  # Bold group name + empty line
	
	# Filter out rows that are just teacher names (no subject)
	valid_rows = [r for r in rows if r.subject and r.subject.strip()]
	
	for i, r in enumerate(valid_rows, 1):
		lines.append(f"{i}. Pán: {r.subject}")
		if r.teacher:
			lines.append(f"   Muǵallim: {r.teacher}")
		if r.room:
			lines.append(f"   [{r.room}-auditoriya]")
		lines.append("")  # Empty line between subjects

	await query.edit_message_text("\n".join(lines), parse_mode='HTML')


