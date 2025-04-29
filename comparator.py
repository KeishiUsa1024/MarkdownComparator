from typing import List, Tuple, Dict
from parser import normalize_text, align_row_to_header, parse_markdown_table

def parse_and_compare(md1: str, md2: str) -> Tuple[List[str], List[List[str]], List[str], List[List[str]], bool]:
    header1, rows1 = parse_markdown_table(md1)
    header2, rows2 = parse_markdown_table(md2)
    col_results = compare_tables(header1, rows1, header2, rows2)
    match_rate = sum(res['match_rate'] for res in col_results.values()) / len(col_results) if col_results else 0

    if match_rate == 0:
        print("⚠️ 表の一致率が0%のため、補完を実施します。")
        rows1 = [align_row_to_header(row, len(header1)) for row in rows1]
        rows2 = [align_row_to_header(row, len(header2)) for row in rows2]
        return header1, rows1, header2, rows2, True

    return header1, rows1, header2, rows2, False

def compare_tables(header1, rows1, header2, rows2):
    common_cols = [h for h in header1 if h in header2]
    col_indices1 = [header1.index(h) for h in common_cols]
    col_indices2 = [header2.index(h) for h in common_cols]
    min_rows = min(len(rows1), len(rows2))
    col_results = {}
    for i, h in enumerate(common_cols):
        match = 0
        diff = 0
        diffs = []
        for r in range(min_rows):
            cell1 = rows1[r][col_indices1[i]] if col_indices1[i] < len(rows1[r]) else ""
            cell2 = rows2[r][col_indices2[i]] if col_indices2[i] < len(rows2[r]) else ""
            if normalize_text(cell1) == normalize_text(cell2):
                match += 1
            else:
                diff += 1
                diffs.append((r+1, cell1, cell2))
        total = match + diff
        match_rate = match / total if total > 0 else 0.0
        col_results[h] = {
            "match": match,
            "diff": diff,
            "total": total,
            "match_rate": match_rate,
            "diff_examples": diffs[:3],
        }
    return col_results