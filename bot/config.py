import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Config:
	bot_token: str
	admin_ids: set[int]
	database_path: str


def get_config() -> Config:
	bot_token = os.getenv("BOT_TOKEN", "")
	admins_raw = os.getenv("ADMIN_IDS", "")
	admin_ids: set[int] = set()
	for part in admins_raw.replace(";", ",").split(","):
		part = part.strip()
		if not part:
			continue
		try:
			admin_ids.add(int(part))
		except ValueError:
			continue

	database_path = os.getenv("DATABASE_PATH", os.path.join(os.getcwd(), "schedule.db"))

	return Config(
		bot_token=bot_token,
		admin_ids=admin_ids,
		database_path=database_path,
	)
