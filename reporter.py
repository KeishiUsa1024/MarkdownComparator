from typing import List, Dict

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

def generate_report(md1, md2, overview1, overview2, col_results, style_diff, cell_examples, file1, file2, completed, rows1, header1):
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
    if completed:
        report.append("\n## 補完内容")
        report.append("以下の表は補完されました。")
        report.append(f"- ファイル名: {file1}")
        report.append(f"- 補完後の行数: {len(rows1)}")
        report.append(f"- 補完後の列数: {len(header1)}")
    return "\n".join(report)