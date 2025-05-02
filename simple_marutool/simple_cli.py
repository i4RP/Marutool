"""
シンプル三期決算図生成アプリケーション - CLI版
"""

import os
import sys
import argparse
import logging
from simple_parser import SimpleParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """CLIアプリケーションのメインエントリーポイント"""
    parser = argparse.ArgumentParser(description="シンプル三期決算図生成アプリケーション - CLI版")
    parser.add_argument("--pdf", required=True, help="解析するPDFファイルのパス")
    args = parser.parse_args()
    
    pdf_path = args.pdf
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDFファイルが見つかりません: {pdf_path}")
        return 1
    
    logger.info(f"PDFファイルの処理を開始: {pdf_path}")
    
    try:
        parser = SimpleParser()
        bs_data = parser.extract_bs_data(pdf_path)
        
        print("\n===== 貸借対照表データ =====")
        for key, value in bs_data.items():
            print(f"{key}: {value:,}円")
        
        logger.info("処理が完了しました")
        return 0
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
