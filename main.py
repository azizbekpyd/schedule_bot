import asyncio
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from bot.config import get_config
from bot.handlers.admin import register_admin_handlers
from bot.handlers.students import register_student_handlers
from bot.handlers.teachers import register_teacher_handlers
from bot.handlers.start import register_start_handlers
from bot.services.schedule_service import ScheduleService

from telegram.ext import Application, ApplicationBuilder


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    config = get_config()

    if not config.bot_token:
        raise RuntimeError("BOT_TOKEN is not configured. Set it in .env")

    # Ensure data dir exists
    data_dir = Path(os.getcwd()) / "data" / "schedules"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Initialize schedule service
    schedule_service = ScheduleService()
    # Attempt to load last schedule if exists (skip temp files)
    excel_files = [f for f in data_dir.glob(
        "*.xlsx") if not f.name.startswith("~$")]
    latest = next(iter(sorted(excel_files, reverse=True)), None)
    if latest is not None:
        try:
            schedule_service.load_from_file(str(latest))
            logging.info("Loaded schedule from %s", latest)
        except Exception as exc:
            logging.exception("Failed to load existing schedule: %s", exc)

    application: Application = ApplicationBuilder().token(config.bot_token).build()

    # Register handlers
    register_start_handlers(application, schedule_service)
    register_student_handlers(application, schedule_service)
    register_teacher_handlers(application, schedule_service)
    register_admin_handlers(application, schedule_service)

    await application.initialize()
    await application.start()
    logging.info("Bot started")
    try:
        await application.updater.start_polling()
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except:
        KeyboardInterrupt()
