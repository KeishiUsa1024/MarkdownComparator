import os
import sys
from datetime import datetime
from typing import List, Dict
from parser import parse_markdown_table
from comparator import parse_and_compare, compare_tables
from reporter import generate_report, qualitative_diff

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
        report = generate_report(md1, md2, overview1, overview2, col_results, style_diff, cell_examples, fname, fname, completed, rows1, header1)
        # 出力先パス
        out_dir = os.path.join(result_dir, os.path.dirname(rel_path))
        os.makedirs(out_dir, exist_ok=True)
        outname = f"report_{os.path.splitext(fname)[0]}.md"
        outpath = os.path.join(out_dir, outname)
        if completed:
            completed_outname = f"completed_{os.path.splitext(fname)[0]}.md"
            completed_outpath = os.path.join(out_dir, completed_outname)
            with open(completed_outpath, "w", encoding="utf-8") as completed_outf:
                completed_outf.write("\n".join(["| " + " | ".join(row) + " |" for row in rows1]))
        with open(outpath, "w", encoding="utf-8") as outf:
            outf.write(report)
        print(f"レポート出力完了")

if __name__ == "__main__":
    main()