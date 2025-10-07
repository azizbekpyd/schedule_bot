## Schedule Bot

Telegram bot that lets students view timetable by group and day, and teachers view their lessons by name. Admins can upload an Excel file which the bot parses automatically.

### Setup
- Create and activate a Python 3.12+ venv
- Install requirements: `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and set `BOT_TOKEN` and `ADMIN_IDS`

### Excel Format
Provide an `.xlsx` file with a single sheet containing these columns (header names can be case-insensitive):
- `group` — group name (e.g. IS-21, 401-20)
- `day` — day of week (Mon, Tue, Wed, Thu, Fri, Sat; Uzbek or Russian also supported: Dushanba/Pon)
- `time` — lesson time (e.g. 08:30-10:00)
- `subject` — subject name
- `teacher` — teacher full name
- `room` — optional room/audience

Example rows:

```
group,day,time,subject,teacher,room
IS-21,Mon,08:30-10:00,Math,Aliyev A.,B-201
IS-21,Mon,10:10-11:40,Physics,Karimova N.,B-105
CS-20,Tue,12:00-13:30,Programming,Rustamov B.,Lab-2
```

### Run
`python -m main`

Commands:
- `/start` — main menu
- `/student` — student flow: choose group, then day
- `/teacher` — teacher flow: choose teacher, then day (optional)
- `/upload` — admin only: send an `.xlsx` document to reload schedule

### Notes
- Parsing implemented with `openpyxl`, no external build tools required.
- Teacher names and groups are extracted from the Excel file; nothing is hard-coded.

