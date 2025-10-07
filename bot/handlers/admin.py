import os
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CallbackContext, CommandHandler, MessageHandler, filters

from bot.config import get_config
from bot.services.schedule_service import ScheduleService


def _is_admin(user_id: int) -> bool:
	return user_id in get_config().admin_ids


def register_admin_handlers(app: Application, schedule: ScheduleService) -> None:
	app.add_handler(CommandHandler("upload", lambda u, c: cmd_upload(u, c)))
	app.add_handler(MessageHandler(filters.Document.ALL, lambda u, c: on_document(u, c, schedule)))


async def cmd_upload(update: Update, context: CallbackContext):
	if not _is_admin(update.effective_user.id):
		await update.effective_chat.send_message("Siz admin emessiz.")
		return
	await update.effective_chat.send_message("Excel (.xlsx) faylin jiberiń.")


async def on_document(update: Update, context: CallbackContext, schedule: ScheduleService):
	if not _is_admin(update.effective_user.id):
		return
	if not update.message or not update.message.document:
		return
	doc = update.message.document
	if not doc.file_name.lower().endswith(".xlsx"):
		await update.effective_chat.send_message("Tek .xlsx fayl qabıl qılınadı.")
		return

	await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.UPLOAD_DOCUMENT)
	data_dir = Path(os.getcwd()) / "data" / "schedules"
	data_dir.mkdir(parents=True, exist_ok=True)
	stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
	local_path = data_dir / f"schedule_{stamp}.xlsx"

	file = await doc.get_file()
	await file.download_to_drive(custom_path=str(local_path))

	# Load schedule
	try:
		schedule.load_from_file(str(local_path))
		stats = schedule.stats()
		await update.effective_chat.send_message(
			f"Tablica jańalandı ✅\nGruppalar: {stats['groups']}\nMuǵallimler: {stats['teachers']}\nPánler: {stats['lessons']}"
		)
	except Exception as exc:
		await update.effective_chat.send_message(f"Júklewde qátelik: {exc}")
		# Keep file for debugging
		return


