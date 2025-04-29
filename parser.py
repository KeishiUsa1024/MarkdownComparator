import re
from typing import List, Tuple

def normalize_text(text: str) -> str:
    text = text.replace('\u3000', ' ')
    text = re.sub(r'[\r\n\t]+', ' ', text)
    text = re.sub(r'[ ]+', ' ', text)
    return text.strip()

def align_row_to_header(row: List[str], header_len: int) -> List[str]:
    if len(row) < header_len:
        return row + [''] * (header_len - len(row))
    else:
        return row[:header_len]

def parse_markdown_table(md: str) -> Tuple[List[str], List[List[str]]]:
    lines = [line.strip() for line in md.strip().splitlines() if line.strip() and not re.match(r"^\s*(#|<!--)", line)]
    header_idx = None
    for i, line in enumerate(lines):
        if re.match(r"^\s*\|.*\|\s*$", line):
            header_idx = i
            break

    if header_idx is None or header_idx + 1 >= len(lines):
        raise ValueError("有効なMarkdown表が見つかりません。")

    header = [h.strip() for h in lines[header_idx].strip('|').split('|')]
    delimiter_line = lines[header_idx + 1]
    if not re.match(r"^\s*\|[-| ]+\|\s*$", delimiter_line):
        raise ValueError("ヘッダー直後の区切り線が不正です。")

    data_lines = []
    expected_col_count = len(header)
    for i, line in enumerate(lines[header_idx + 2:], start=header_idx + 2):
        if re.match(r"^\s*\|.*\|\s*$", line):
            row = [c.strip() for c in line.split('|')]  # パイプで区切る
            row = row[:len(header)] + [''] * (len(header) - len(row))  # 列数のズレを許容
            row = align_row_to_header(row, len(header))
            if len(row) != expected_col_count:
                warnings.append(f"⚠️ 警告: {i+1}行目の列数がヘッダーと一致しません（{len(row)}列 vs {expected_col_count}列）")
            data_lines.append(row)

    return header, data_lines