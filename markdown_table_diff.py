"""
使い方:
    python markdown_table_diff.py

このスクリプトは
- base フォルダ内のmdファイルを基準として
- input フォルダ配下（サブディレクトリ含む）のmdファイルと同名ファイルがbaseにあれば比較し
- result フォルダにinputと同じディレクトリ構造で比較レポートを出力します
"""

import re
from datetime import datetime
import sys
import argparse
import os
from typing import List, Tuple, Dict

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
    lines = [line.strip() for line in md.strip().splitlines() if line.strip()]
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
            row = [c.strip() for c in line.split('|')]
            row = align_row_to_header(row, len(header))
            if len(row) != expected_col_count:
                print(f"⚠️ 警告: {i+1}行目の列数がヘッダーと一致しません（{len(row)}列 vs {expected_col_count}列）")
            data_lines.append(row)

    return header, data_lines

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

def table_overview(md: str, header: List[str], rows: List[List[str]]) -> Dict:
    char_count = len(md)
    element_count = sum(len(row) for row in rows)
    return {
        "char_count": char_count,
        "header_count": len(header),
        "element_count": element_count,
        "row_count": len(rows),
        "col_names": header,
    }

    

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

def qualitative_diff(md1: str, md2: str, header1, header2, rows1, rows2, col_results):
    style_diff = []
    if md1.count('---') != md2.count('---'):
        style_diff.append("区切り線（'---'）の数が異なります。")
    if len(header1) != len(header2):
        style_diff.append("ヘッダーの列数が異なります。")
    if len(rows1) != len(rows2):
        style_diff.append("データ行数が異なります。")
    cell_examples = []
    for col, res in col_results.items():
        for row_idx, cell1, cell2 in res["diff_examples"]:
            cell_examples.append(f"- 列「{col}」{row_idx}行目: '{cell1}' vs '{cell2}'")
    return style_diff, cell_examples

def generate_report(md1, md2, overview1, overview2, col_results, style_diff, cell_examples, file1, file2):
    report = []
    report.append(f"# Markdown表比較レポート: {file1} vs {file2}\n")
    report.append("## 表1 概要")
    report.append(f"- 文字数: {overview1['char_count']}")
    report.append(f"- 列数: {overview1['header_count']} ({', '.join(overview1['col_names'])})")
    report.append(f"- 行数: {overview1['row_count']}")
    report.append(f"- 要素数: {overview1['element_count']}\n")
    report.append("## 表2 概要")
    report.append(f"- 文字数: {overview2['char_count']}")
    report.append(f"- 列数: {overview2['header_count']} ({', '.join(overview2['col_names'])})")
    report.append(f"- 行数: {overview2['row_count']}")
    report.append(f"- 要素数: {overview2['element_count']}\n")
    report.append("## 定量的な比較")
    report.append("| 列名 | 一致 | 差分 | 一致率 |")
    report.append("|------|------|------|--------|")
    for col, res in col_results.items():
        report.append(f"| {col} | {res['match']} | {res['diff']} | {res['match_rate']*100:.1f}% |")
    report.append("\n## 定性的な差分")
    if style_diff:
        report.append("### Markdown記法の違い")
        for s in style_diff:
            report.append(f"- {s}")
    if cell_examples:
        report.append("### 差分セルの例")
        for ex in cell_examples:
            report.append(ex)
    return "\n".join(report)

def find_md_files_recursive(root):
    md_files = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith('.md'):
                rel_dir = os.path.relpath(dirpath, root)
                rel_path = os.path.join(rel_dir, f) if rel_dir != '.' else f
                md_files.append(rel_path)
    return md_files

def main():
    base_dir = os.path.join(os.path.dirname(__file__), "base")
    input_dir = os.path.join(os.path.dirname(__file__), "input")
    result_dir = os.path.join(os.path.dirname(__file__), "result")
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not os.path.isdir(base_dir) or not os.path.isdir(input_dir) or not os.path.isdir(result_dir):
        print("base, input, result の3つのディレクトリが必要です。")
        sys.exit(1)

    result_dir = os.path.join(result_dir, current_time)
    print(f"Base directory: {os.path.relpath(base_dir)}")
    print(f"Input directory: {os.path.relpath(input_dir)}")
    print(f"Result directory: {os.path.relpath(result_dir)}")

    base_files = {os.path.basename(f): os.path.join(base_dir, f)
                  for f in os.listdir(base_dir) if f.endswith('.md')}
    input_files = find_md_files_recursive(input_dir)

    for rel_path in input_files:
        input_path = os.path.join(input_dir, rel_path)
        fname = os.path.basename(rel_path)
        if fname not in base_files:
            continue
        base_path = base_files[fname]
        try:
            with open(base_path, encoding="utf-8") as f1, open(input_path, encoding="utf-8") as f2:
                md1 = f1.read()
                md2 = f2.read()
            header1, rows1, header2, rows2, completed = parse_and_compare(md1, md2)
        except Exception as e:
            print(f"{rel_path} の比較に失敗: {e}")
            continue
        overview1 = table_overview(md1, header1, rows1)
        overview2 = table_overview(md2, header2, rows2)
        if completed:
            print(f"⚠️ {rel_path} の表が補完されました。")

        col_results = compare_tables(header1, rows1, header2, rows2)
        style_diff, cell_examples = qualitative_diff(md1, md2, header1, header2, rows1, rows2, col_results)
        report = generate_report(md1, md2, overview1, overview2, col_results, style_diff, cell_examples, fname, fname)
        # 出力先パス
        out_dir = os.path.join(result_dir, os.path.dirname(rel_path))
        os.makedirs(out_dir, exist_ok=True)
        outname = f"report_{os.path.splitext(fname)[0]}.md"
        outpath = os.path.join(out_dir, outname)
        with open(outpath, "w", encoding="utf-8") as outf:
            outf.write(report)
        print(f"レポート出力完了")

if __name__ == "__main__":
    main()