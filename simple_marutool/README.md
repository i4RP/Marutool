# シンプル三期決算図生成アプリケーション

PDFから貸借対照表データを抽出し、視覚化するシンプルなツールです。

## 機能
- 単一のPDFファイルから貸借対照表データを抽出
- 10項目の財務データを識別して表示
- 抽出したデータを円グラフ、棒グラフ、またはウォーターフォールチャートで可視化

## インストール方法

### 必要環境
- Python 3.12以上
- Tesseract OCR（OCR機能を使用する場合）
- Poppler（PDF処理に必要）

### Windowsの場合
1. [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) をインストール
2. [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) をインストール
3. 環境変数PATHにTesseractとPopplerのbinディレクトリを追加

### macOSの場合
```bash
brew install tesseract
brew install tesseract-lang  # 日本語OCRを含める場合
brew install poppler
```

### Poetryを使用したインストール
```bash
# Poetryのインストール（未インストールの場合）
pip install poetry

# 依存関係のインストール
poetry install
```

## 使用方法

### GUIアプリケーション
```bash
poetry run python simple_app.py
```

### コマンドライン版（パーサーのみ）
```bash
poetry run python simple_cli.py --pdf "エピック_6期決算書.pdf"
```

### コマンドライン版（可視化含む）
```bash
poetry run python simple_visualizer.py --pdf "エピック_6期決算書.pdf" --output "bs_chart.png" --type "pie"
```

## 抽出項目（10項目）
1. 流動資産合計
2. 現金・預金
3. 有形固定資産
4. 無形固定資産
5. 投資その他
6. 資産合計
7. 流動負債
8. 固定負債
9. 資本金
10. 利益剰余金

## 開発ロードマップ
1. ✅ 単一PDFからの貸借対照表データ抽出
2. ✅ 抽出データの可視化（円グラフ・棒グラフ）
3. ⬜ 複数PDFの処理と比較機能
4. ⬜ 損益計算書（P/L）データの抽出（8項目）
5. ⬜ 三期比較グラフの生成
6. ⬜ アプリケーションのパッケージング（.exe/.app）

## 技術詳細
- PDFテキスト抽出: pdfplumber, PyMuPDF
- OCR処理: pytesseract + pdf2image
- データ可視化: matplotlib
- GUI: PyQt5
