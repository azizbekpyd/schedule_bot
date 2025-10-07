from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import re

from bot.excel_importer import load_schedule_from_excel, NormalizedRow


@dataclass
class ScheduleData:
	groups: List[str]
	teachers: List[str]
	by_group_day: Dict[Tuple[str, str], List[NormalizedRow]]
	by_teacher: Dict[str, List[NormalizedRow]]
	total_rows: int


class ScheduleService:
	def __init__(self) -> None:
		self._data: Optional[ScheduleData] = None
		self._source_path: Optional[str] = None

	def load_from_file(self, file_path: str) -> None:
		rows_raw = load_schedule_from_excel(file_path)

		def normalize_teacher(name: str) -> str:
			if not name:
				return ""
			# Drop anything in parentheses and trim
			clean = re.sub(r"\s*\(.*?\)\s*$", "", name).strip()
			# Collapse internal whitespace
			clean = re.sub(r"\s+", " ", clean)
			return clean

		# Normalize teacher names for menus and indexing (create new instances)
		rows = [
			NormalizedRow(
				group=r.group,
				day=r.day,
				time=r.time,
				subject=r.subject,
				teacher=normalize_teacher(r.teacher) if getattr(r, 'teacher', None) else "",
				room=r.room,
			)
			for r in rows_raw
		]

		groups: List[str] = sorted({r.group for r in rows})
		teachers: List[str] = sorted({r.teacher for r in rows if r.teacher})

		by_group_day: Dict[Tuple[str, str], List[NormalizedRow]] = {}
		for r in rows:
			by_group_day.setdefault((r.group, r.day), []).append(r)
		# Keep original order from Excel parsing (no sorting by time)

		by_teacher: Dict[str, List[NormalizedRow]] = {}
		for r in rows:
			if not r.teacher:
				continue
			by_teacher.setdefault(r.teacher, []).append(r)
		# Keep original Excel order for teacher listings as well (no sorting)

		self._data = ScheduleData(groups=groups, teachers=teachers, by_group_day=by_group_day, by_teacher=by_teacher, total_rows=len(rows))
		self._source_path = file_path

	def get_groups(self) -> List[str]:
		return list(self._data.groups) if self._data else []

	def get_teachers(self) -> List[str]:
		return list(self._data.teachers) if self._data else []

	def get_group_day(self, group: str, day: str) -> List[NormalizedRow]:
		if not self._data:
			return []
		return self._data.by_group_day.get((group, day), [])

	def get_teacher(self, teacher: str) -> List[NormalizedRow]:
		if not self._data:
			return []
		return self._data.by_teacher.get(teacher, [])

	def has_data(self) -> bool:
		return self._data is not None

	def source_path(self) -> Optional[str]:
		return self._source_path

	def stats(self) -> Dict[str, int]:
		if not self._data:
			return {"groups": 0, "teachers": 0, "lessons": 0}
		return {
			"groups": len(self._data.groups),
			"teachers": len(self._data.teachers),
			"lessons": self._data.total_rows,
		}


