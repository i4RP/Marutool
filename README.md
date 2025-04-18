# 三期決算図生成アプリケーション (Epic Financial Visualizer)

財務諸表PDFから18項目を抽出し、3期分の財務データを視覚化するアプリケーションです。

## 機能
- 3期分のPDFファイルから財務データを抽出
- OCR機能によるスキャンPDFの対応
- 貸借対照表(B/S)と損益計算書(P/L)の視覚的な比較図の生成
- PNG/PDF形式での出力

## 使用方法
1. アプリケーションを起動
2. 3期分のPDFファイルを選択
3. 処理が完了すると三期決算図が表示されます
4. 出力形式を選択して保存

## 必要環境
- Windows または macOS
- Tesseract OCR (OCR機能を使用する場合)
- Poppler (PDF処理に必要)

## インストール方法

### Windows
1. [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) をインストール
2. [Poppler for Windows](https://github.com/oschwartz10612/poppler-windows/releases/) をインストール
3. 環境変数PATHにTesseractとPopplerのbinディレクトリを追加

### macOS
```bash
brew install tesseract
brew install tesseract-lang
brew install poppler
```

## 実行方法

### GUIアプリケーション
```bash
poetry run python main.py
```

### コマンドライン版
```bash
poetry run python cli.py --pdf1 path/to/first.pdf --pdf2 path/to/second.pdf --pdf3 path/to/third.pdf --output output.png --format png
```

### デモ（サンプルデータ）
```bash
poetry run python demo.py
```

## ビルド方法
```bash
poetry run python build.py
```

## 抽出項目（18項目）
### 貸借対照表（B/S）- 10項目
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

### 損益計算書（P/L）- 8項目
1. 売上高
2. 売上原価
3. 販売費及び一般管理費
4. 営業外収益
5. 営業外費用
6. 特別利益
7. 特別損失
8. 法人税
