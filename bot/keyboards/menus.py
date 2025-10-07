from typing import List


def chunk_buttons(buttons: List[List[object]], row_size: int = 2) -> List[List[object]]:
	chunked: List[List[object]] = []
	row: List[object] = []
	for btn_row in buttons:
		for btn in btn_row:
			row.append(btn)
			if len(row) >= row_size:
				chunked.append(row)
				row = []
	if row:
		chunked.append(row)
	return chunked


