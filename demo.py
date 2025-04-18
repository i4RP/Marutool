
"""
三期決算図生成アプリケーション (Epic Financial Visualizer)
デモスクリプト - サンプルデータを使用したデモンストレーション
"""

import os
import sys
import logging
from finance_calc import FinanceCalculator
from chart_generator import ChartGenerator
from sample_data.sample_financial_data import get_sample_data

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """デモスクリプトのメインエントリーポイント"""
    print("三期決算図生成アプリケーション - デモ")
    print("-" * 50)
    
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("サンプルデータを読み込み中...")
    sample_data = get_sample_data()
    
    logger.info("財務データを計算中...")
    calculator = FinanceCalculator()
    financial_data = calculator.process_data(sample_data)
    
    logger.info("グラフを生成中...")
    chart_generator = ChartGenerator()
    chart_path = chart_generator.generate_chart(financial_data)
    
    pdf_path = os.path.join(output_dir, "エピック_三期決算図_サンプル.pdf")
    logger.info(f"PDFに変換中: {pdf_path}")
    ChartGenerator.convert_to_pdf(chart_path, pdf_path)
    
    logger.info(f"処理が完了しました。")
    logger.info(f"PNG出力: {chart_path}")
    logger.info(f"PDF出力: {pdf_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
