
"""
三期決算図生成アプリケーション (Epic Financial Visualizer)
コマンドラインインターフェース - GUIなしでの実行用
"""

import os
import sys
import argparse
import logging

from parser import PDFParser
from finance_calc import FinanceCalculator
from chart_generator import ChartGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """コマンドラインインターフェースのメインエントリーポイント"""
    parser = argparse.ArgumentParser(description="三期決算図生成アプリケーション - コマンドライン版")
    
    parser.add_argument("--pdf1", required=True, help="1期目のPDFファイルパス")
    parser.add_argument("--pdf2", required=True, help="2期目のPDFファイルパス")
    parser.add_argument("--pdf3", required=True, help="3期目のPDFファイルパス")
    parser.add_argument("--output", default="エピック_三期決算図.png", help="出力ファイルパス")
    parser.add_argument("--format", choices=["png", "pdf"], default="png", help="出力形式")
    
    args = parser.parse_args()
    
    pdf_files = [args.pdf1, args.pdf2, args.pdf3]
    for pdf_file in pdf_files:
        if not os.path.exists(pdf_file):
            logger.error(f"PDFファイルが見つかりません: {pdf_file}")
            return 1
    
    try:
        logger.info("PDFファイルを解析中...")
        parser = PDFParser()
        
        extracted_data = {}
        for i, pdf_file in enumerate(pdf_files):
            period = os.path.basename(pdf_file).split('_')[1].replace('期決算書', '').replace('.pdf', '')
            logger.info(f"{period}期のデータを抽出中...")
            extracted_data[period] = parser.extract_data(pdf_file)
        
        logger.info("財務データを計算中...")
        calculator = FinanceCalculator()
        financial_data = calculator.process_data(extracted_data)
        
        logger.info("グラフを生成中...")
        chart_generator = ChartGenerator()
        chart_path = chart_generator.generate_chart(financial_data)
        
        output_path = args.output
        if args.format == "pdf" and chart_path.endswith(".png"):
            output_path = output_path.replace(".png", ".pdf")
            logger.info(f"PDFに変換中: {output_path}")
            ChartGenerator.convert_to_pdf(chart_path, output_path)
        else:
            import shutil
            shutil.copy(chart_path, output_path)
        
        logger.info(f"処理が完了しました。出力ファイル: {output_path}")
        return 0
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
