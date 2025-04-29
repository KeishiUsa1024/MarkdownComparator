# MarkdownComparator

MarkdownComparatorは、2つのMarkdownファイルを比較し、表の差分をレポートとして生成するツールです。

## 機能
- 2つのMarkdownファイルの表を比較
- 定量的および定性的な差分をレポートとして出力

## インストール
1. リポジトリをクローンします。
   ```bash
   git clone https://github.com/yourusername/MarkdownComparator.git
   ```
2. 必要な依存関係をインストールします。
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法
1. `main.py`を実行して、比較を開始します。
   ```bash
   python main.py
   ```
2. 結果は`result`ディレクトリに出力されます。

## ファイル構成
- `comparator.py`: 比較ロジックを実装
- `main.py`: エントリーポイント
- `markdown_table_diff.py`: Markdownの表の差分を計算
- `parser.py`: Markdownファイルの解析
- `reporter.py`: レポートの生成