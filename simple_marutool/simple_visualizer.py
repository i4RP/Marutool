"""
シンプル三期決算図生成アプリケーション - データ可視化
"""

import os
import sys
import argparse
import logging
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from simple_parser import SimpleParser

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Noto Sans CJK JP', 'IPAGothic', 'VL Gothic', 'Yu Gothic', 'Hiragino Sans']

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleVisualizer:
    """財務データの可視化クラス"""
    
    def __init__(self):
        """初期化"""
        pass
    
    def create_bs_chart(self, bs_data, output_path=None):
        """貸借対照表データのチャートを作成
        
        Args:
            bs_data: 貸借対照表データ
            output_path: 出力ファイルパス（Noneの場合は表示のみ）
        """
        asset_items = [
            '現金・預金', 
            '有形固定資産', 
            '無形固定資産', 
            '投資その他'
        ]
        
        liability_equity_items = [
            '流動負債', 
            '固定負債', 
            '資本金', 
            '利益剰余金'
        ]
        
        asset_values = [bs_data.get(item, 0) for item in asset_items]
        liability_equity_values = [bs_data.get(item, 0) for item in liability_equity_items]
        
        total_assets = sum(asset_values)
        total_liabilities_equity = sum(liability_equity_values)
        
        if bs_data.get('資産合計', 0) == 0:
            bs_data['資産合計'] = total_assets
            logger.info(f"資産合計を計算: {total_assets:,}円")
        
        if bs_data.get('流動資産合計', 0) == 0:
            bs_data['流動資産合計'] = bs_data.get('現金・預金', 0)
            logger.info(f"流動資産合計を推定: {bs_data['流動資産合計']:,}円")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
        
        asset_labels = asset_items
        asset_sizes = asset_values
        
        asset_colors = ['#3498db', '#2ecc71', '#9b59b6', '#e67e22']
        
        if sum(asset_sizes) > 0:  # ゼロ除算を防ぐ
            ax1.pie(asset_sizes, labels=asset_labels, autopct='%1.1f%%', startangle=90, colors=asset_colors)
            ax1.set_title('資産構成', fontsize=14)
        else:
            ax1.text(0.5, 0.5, 'データなし', horizontalalignment='center', verticalalignment='center', fontsize=14)
            ax1.set_title('資産構成', fontsize=14)
        
        liability_equity_labels = liability_equity_items
        liability_equity_sizes = liability_equity_values
        
        liability_equity_colors = ['#e74c3c', '#f39c12', '#1abc9c', '#34495e']
        
        if sum(liability_equity_sizes) > 0:  # ゼロ除算を防ぐ
            ax2.pie(liability_equity_sizes, labels=liability_equity_labels, autopct='%1.1f%%', startangle=90, colors=liability_equity_colors)
            ax2.set_title('負債・純資産構成', fontsize=14)
        else:
            ax2.text(0.5, 0.5, 'データなし', horizontalalignment='center', verticalalignment='center', fontsize=14)
            ax2.set_title('負債・純資産構成', fontsize=14)
        
        plt.suptitle('貸借対照表分析', fontsize=16)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            logger.info(f"チャートを保存しました: {output_path}")
        else:
            plt.show()
        
        return fig
    
    def create_bs_bar_chart(self, bs_data, output_path=None):
        """貸借対照表データの棒グラフを作成
        
        Args:
            bs_data: 貸借対照表データ
            output_path: 出力ファイルパス（Noneの場合は表示のみ）
        """
        items = [
            '流動資産合計',
            '現金・預金', 
            '有形固定資産', 
            '無形固定資産', 
            '投資その他',
            '資産合計',
            '流動負債', 
            '固定負債', 
            '資本金', 
            '利益剰余金'
        ]
        
        values = [bs_data.get(item, 0) for item in items]
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        bars = ax.bar(items, values, color='#3498db')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{height:,.0f}',
                    ha='center', va='bottom', rotation=45)
        
        ax.set_title('貸借対照表項目', fontsize=16)
        ax.set_ylabel('金額（円）', fontsize=12)
        
        plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path)
            logger.info(f"棒グラフを保存しました: {output_path}")
        else:
            plt.show()
        
        return fig

def main():
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(description="シンプル三期決算図生成アプリケーション - データ可視化")
    parser.add_argument("--pdf", required=True, help="解析するPDFファイルのパス")
    parser.add_argument("--output", help="出力ファイルパス（デフォルト: bs_chart.png）", default="bs_chart.png")
    parser.add_argument("--type", help="グラフタイプ（pie または bar）", default="pie")
    args = parser.parse_args()
    
    pdf_path = args.pdf
    output_path = args.output
    chart_type = args.type
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDFファイルが見つかりません: {pdf_path}")
        return 1
    
    logger.info(f"PDFファイルの処理を開始: {pdf_path}")
    
    try:
        parser = SimpleParser()
        bs_data = parser.extract_bs_data(pdf_path)
        
        visualizer = SimpleVisualizer()
        
        if chart_type == "pie":
            visualizer.create_bs_chart(bs_data, output_path)
        else:
            visualizer.create_bs_bar_chart(bs_data, output_path)
        
        logger.info("処理が完了しました")
        return 0
        
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
