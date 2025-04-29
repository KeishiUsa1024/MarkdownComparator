from typing import List, Dict
from dataclasses import dataclass

@dataclass
class ReportData:
    md1: str
    md2: str
    overview1: Dict
    overview2: Dict
    col_results: Dict
    style_diff: List[str]
    cell_examples: List[str]
    file1: str
    file2: str
    completed: bool
    rows1: List[List[str]]
    header1: List[str]

# 2つのMarkdown表を定性的に比較する関数
# 引数:
#   md1, md2: 比較するMarkdownコンテンツ
#   header1, header2: 各表のヘッダー
#   rows1, rows2: 各表の行データ
#   col_results: 列ごとの比較結果
# 戻り値:
#   スタイルの違いとセルの例を含むタプル
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

# 2つの表を比較したMarkdownレポートを生成する関数
# 引数:
#   data: レポート生成に必要なデータを含むReportDataオブジェクト
# 戻り値:
#   生成されたMarkdownレポートの文字列
def generate_report(data: ReportData):
    report = []
    report.append(f"# Markdown表比較レポート: {data.file1} vs {data.file2}\n")
    report.append("## 表1 概要")
    report.append(f"- 文字数: {data.overview1['char_count']}")
    report.append(f"- 列数: {data.overview1['header_count']} ({', '.join(data.overview1['col_names'])})")
    report.append(f"- 行数: {data.overview1['row_count']}")
    report.append(f"- 要素数: {data.overview1['element_count']}\n")
    report.append("## 表2 概要")
    report.append(f"- 文字数: {data.overview2['char_count']}")
    report.append(f"- 列数: {data.overview2['header_count']} ({', '.join(data.overview2['col_names'])})")
    report.append(f"- 行数: {data.overview2['row_count']}")
    report.append(f"- 要素数: {data.overview2['element_count']}\n")
    report.append("## 定量的な比較")
    report.append("| 列名 | 一致 | 差分 | 一致率 |")
    report.append("|------|------|------|--------|")
    for col, res in data.col_results.items():
        report.append(f"| {col} | {res['match']} | {res['diff']} | {res['match_rate']*100:.1f}% |")
    report.append("\n## 定性的な差分")
    if data.style_diff:
        report.append("### Markdown記法の違い")
        for s in data.style_diff:
            report.append(f"- {s}")
    if data.cell_examples:
        report.append("### 差分セルの例")
        for ex in data.cell_examples:
            report.append(ex)
    if data.completed:
        report.append("\n## 補完内容")
        report.append("以下の表は補完されました。")
        report.append(f"- ファイル名: {data.file1}")
        report.append(f"- 補完後の行数: {len(data.rows1)}")
        report.append(f"- 補完後の列数: {len(data.header1)}")
    return "\n".join(report)