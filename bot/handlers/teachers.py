from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackContext, CommandHandler, CallbackQueryHandler
from datetime import datetime, timedelta

from bot.keyboards.menus import chunk_buttons
from bot.services.schedule_service import ScheduleService


def register_teacher_handlers(app: Application, schedule: ScheduleService) -> None:
	app.add_handler(CommandHandler("teacher", lambda u, c: start_teacher(u, c, schedule)))
	app.add_handler(CallbackQueryHandler(lambda u, c: on_teacher_selected(u, c, schedule), pattern=r"^tc_name:"))


async def start_teacher(update: Update, context: CallbackContext, schedule: ScheduleService):
	teachers = schedule.get_teachers()
	if not teachers:
		await update.effective_chat.send_message("Tablica ele júklenbegen.")
		return
	buttons = [[InlineKeyboardButton(text=t, callback_data=f"tc_name:{t}")] for t in teachers]
	markup = InlineKeyboardMarkup(chunk_buttons(buttons))
	await update.effective_chat.send_message("Muǵallimniń atın tańlań:", reply_markup=markup)


async def on_teacher_selected(update: Update, context: CallbackContext, schedule: ScheduleService):
	query = update.callback_query
	await query.answer()
	teacher = query.data.split(":", 1)[1]
	rows = schedule.get_teacher(teacher)
	if not rows:
		await query.edit_message_text(f"{teacher} ushın sabaqlar tabılmadı.")
		return

	# Localized day names order and map
	day_order = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
	localized = {
		"Mon": "Dúyshembi",
		"Tue": "Shiyshembi",
		"Wed": "Sárshembi",
		"Thu": "Piyshembi",
		"Fri": "Juma",
		"Sat": "Shembi",
	}

	# Compute current week's dates (Mon..Sat)
	now = datetime.now()
	start_of_week = now - timedelta(days=(now.weekday()))  # Monday
	day_to_date = {day_order[i]: (start_of_week + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(len(day_order))}

	# Group rows by day preserving input order
	by_day = {d: [] for d in day_order}
	for r in rows:
		if r.day in by_day:
			by_day[r.day].append(r)

	def parse_para_num(time_val: str | None) -> int | None:
		if not time_val:
			return None
		v = str(time_val).strip().upper()
		roman_map = {
			"I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6,
			"VII": 7, "VIII": 8, "IX": 9, "X": 10,
		}
		if v in roman_map:
			return roman_map[v]
		# If starts with digits, use that
		digits = ""
		for ch in v:
			if ch.isdigit():
				digits += ch
			else:
				break
		try:
			return int(digits) if digits else None
		except ValueError:
			return None

	lines = [f"<b>Muǵallim: {teacher}</b>", ""]
	for d in day_order:
		day_rows = [r for r in by_day[d] if r.subject and r.subject.strip()]
		if not day_rows:
			continue
		lines.append(f"<b>{localized.get(d, d)} ({day_to_date.get(d, '')}):</b>")
		# Merge consecutive rows that represent the same lesson ONLY when
		# subject, room, and para number match (same-time common subject across groups)
		merged = []  # each item: {time, para_num, subject, room, groups: [..]}
		for r in day_rows:
			key_time = r.time or ""
			subj = r.subject.strip()
			room = r.room or ""
			current_para = parse_para_num(key_time)
			if merged and merged[-1]["subject"] == subj and merged[-1]["room"] == room and merged[-1]["para_num"] == current_para:
				if r.group:
					merged[-1]["groups"].append(r.group)
			else:
				merged.append({
					"time": key_time,
					"para_num": current_para,
					"subject": subj,
					"room": room,
					"groups": [r.group] if r.group else []
				})
		for idx, item in enumerate(merged, 1):
			para_label = item["para_num"] if item["para_num"] is not None else idx
			lines.append(f"{para_label}-para. {item['subject']}")
			if item["groups"]:
				# unique groups, keep order, each on its own line
				seen = set()
				unique_groups = []
				for g in item["groups"]:
					if g and g not in seen:
						seen.add(g)
						unique_groups.append(g)
				for g in unique_groups:
					lines.append(f"              {g}")
			if item["room"]:
				lines.append(f"              [{item['room']} - auditoriya]")
			lines.append("")

	await query.edit_message_text("\n".join(lines), parse_mode='HTML')


