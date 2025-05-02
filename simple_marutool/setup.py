"""
シンプル三期決算図生成アプリケーション - セットアップスクリプト
"""

import os
import sys
import platform
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_tesseract():
    """Tesseract OCRがインストールされているか確認"""
    try:
        result = subprocess.run(
            ["tesseract", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            logger.info(f"Tesseract OCRが見つかりました: {result.stdout.splitlines()[0]}")
            return True
        else:
            logger.warning("Tesseract OCRが見つかりません")
            return False
    except FileNotFoundError:
        logger.warning("Tesseract OCRが見つかりません")
        return False

def check_poppler():
    """Popplerがインストールされているか確認"""
    try:
        if platform.system() == "Windows":
            from pdf2image.exceptions import PDFInfoNotInstalledError
            try:
                from pdf2image import pdfinfo_from_path
                logger.info("Popplerが見つかりました")
                return True
            except PDFInfoNotInstalledError:
                logger.warning("Popplerが見つかりません")
                return False
        else:
            result = subprocess.run(
                ["pdfinfo", "-v"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                logger.info("Popplerが見つかりました")
                return True
            else:
                logger.warning("Popplerが見つかりません")
                return False
    except (FileNotFoundError, ImportError):
        logger.warning("Popplerが見つかりません")
        return False

def check_dependencies():
    """依存関係をチェック"""
    logger.info("依存関係のチェックを開始します...")
    
    tesseract_ok = check_tesseract()
    poppler_ok = check_poppler()
    
    if not tesseract_ok:
        if platform.system() == "Windows":
            logger.info("Tesseract OCRのインストール方法（Windows）:")
            logger.info("1. https://github.com/tesseract-ocr/tesseract からインストーラーをダウンロード")
            logger.info("2. インストール時に「Additional language data」で日本語を選択")
            logger.info("3. 環境変数PATHにTesseractのインストールディレクトリを追加")
        else:
            logger.info("Tesseract OCRのインストール方法（macOS）:")
            logger.info("brew install tesseract")
            logger.info("brew install tesseract-lang")
    
    if not poppler_ok:
        if platform.system() == "Windows":
            logger.info("Popplerのインストール方法（Windows）:")
            logger.info("1. https://github.com/oschwartz10612/poppler-windows/releases/ からダウンロード")
            logger.info("2. 解凍したフォルダを任意の場所に配置")
            logger.info("3. 環境変数PATHにPopplerのbinディレクトリを追加")
        else:
            logger.info("Popplerのインストール方法（macOS）:")
            logger.info("brew install poppler")
    
    return tesseract_ok and poppler_ok

def setup_poetry():
    """Poetryの依存関係をインストール"""
    logger.info("Poetryの依存関係をインストールします...")
    
    try:
        subprocess.run(
            ["poetry", "install"], 
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info("Poetryの依存関係のインストールが完了しました")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Poetryの依存関係のインストールに失敗しました: {e}")
        logger.error(f"エラー出力: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error("Poetryが見つかりません。インストールしてください:")
        logger.error("pip install poetry")
        return False

def main():
    """セットアップのメインエントリーポイント"""
    logger.info("シンプル三期決算図生成アプリケーションのセットアップを開始します...")
    
    deps_ok = check_dependencies()
    
    poetry_ok = setup_poetry()
    
    if deps_ok and poetry_ok:
        logger.info("セットアップが完了しました！")
        logger.info("アプリケーションを起動するには:")
        logger.info("poetry run python simple_app.py")
        return 0
    else:
        logger.warning("セットアップが完了しましたが、一部の依存関係が不足しています。")
        logger.warning("上記のインストール手順に従って必要なソフトウェアをインストールしてください。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
