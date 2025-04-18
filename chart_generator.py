
"""
三期決算図生成アプリケーション (Epic Financial Visualizer)
グラフ生成モジュール - 財務データの可視化
"""

import os
import tempfile
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import logging
from matplotlib.backends.backend_pdf import PdfPages

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChartGenerator:
    """財務データからグラフを生成するクラス"""
    
    def __init__(self):
        """初期化"""
        self.output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
        os.makedirs(self.output_dir, exist_ok=True)
        
        self._setup_japanese_font()
        
        plt.style.use('ggplot')
    
    def _setup_japanese_font(self):
        """日本語フォントの設定"""
        try:
            jp_fonts = [f.name for f in fm.fontManager.ttflist if 'JP' in f.name or 'Gothic' in f.name or 'Mincho' in f.name]
            
            if jp_fonts:
                plt.rcParams['font.family'] = jp_fonts[0]
                logger.info(f"日本語フォントを設定しました: {jp_fonts[0]}")
            else:
                logger.warning("日本語フォントが見つかりませんでした。デフォルトフォントを使用します。")
        except Exception as e:
            logger.warning(f"フォント設定中にエラーが発生しました: {e}")
    
    def generate_chart(self, financial_data):
        """財務データからグラフを生成する
        
        Args:
            financial_data: 財務データ（B/SとP/L）
                {"periods": [...], "bs": DataFrame, "pl": DataFrame}
                
        Returns:
            str: 生成されたグラフのファイルパス
        """
        logger.info("グラフの生成を開始します")
        
        periods = financial_data["periods"]
        bs_data = financial_data["bs"]
        pl_data = financial_data["pl"]
        
        temp_file = os.path.join(self.output_dir, "エピック_三期決算図.png")
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 16), dpi=100)
        
        self._create_pl_chart(ax1, pl_data, periods)
        
        self._create_bs_chart(ax2, bs_data, periods)
        
        fig.suptitle("三期決算図 - エピック", fontsize=20, y=0.98)
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        plt.savefig(temp_file, bbox_inches='tight')
        plt.close()
        
        logger.info(f"グラフを保存しました: {temp_file}")
        return temp_file
    
    def _create_pl_chart(self, ax, pl_data, periods):
        """P/L構成図を作成する
        
        Args:
            ax: matplotlib Axes オブジェクト
            pl_data: P/Lデータ
            periods: 期の一覧
        """
        items = ["売上高", "売上原価", "販売費及び一般管理費", "営業利益", "経常利益", "当期純利益"]
        
        bar_width = 0.15
        
        x = np.arange(len(items))
        
        for i, period in enumerate(periods):
            values = [pl_data.loc[period, item] for item in items]
            ax.bar(x + i*bar_width, values, width=bar_width, label=f"{period}期")
        
        ax.set_title("損益計算書（P/L）構成", fontsize=16)
        ax.set_xticks(x + bar_width * (len(periods) - 1) / 2)
        ax.set_xticklabels(items, rotation=45, ha='right')
        ax.legend()
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{int(x):,}"))
        
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        ax.set_ylabel("金額（円）")
    
    def _create_bs_chart(self, ax, bs_data, periods):
        """B/S構成図を作成する
        
        Args:
            ax: matplotlib Axes オブジェクト
            bs_data: B/Sデータ
            periods: 期の一覧
        """
        asset_items = ["流動資産合計", "有形固定資産", "無形固定資産", "投資その他", "その他資産"]
        liability_equity_items = ["流動負債", "固定負債", "資本金", "利益剰余金"]
        
        bar_width = 0.35
        
        x = np.arange(len(periods))
        
        bottom = np.zeros(len(periods))
        for item in asset_items:
            values = [bs_data.loc[period, item] for period in periods]
            ax.bar(x - bar_width/2, values, bottom=bottom, width=bar_width, label=f"資産: {item}")
            bottom += values
        
        bottom = np.zeros(len(periods))
        for item in liability_equity_items:
            values = [bs_data.loc[period, item] for period in periods]
            ax.bar(x + bar_width/2, values, bottom=bottom, width=bar_width, label=f"負債・純資産: {item}")
            bottom += values
        
        ax.set_title("貸借対照表（B/S）構成", fontsize=16)
        ax.set_xticks(x)
        ax.set_xticklabels([f"{period}期" for period in periods])
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: f"{int(x):,}"))
        
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)
        
        ax.set_ylabel("金額（円）")
    
    @staticmethod
    def convert_to_pdf(png_path, pdf_path):
        """PNGをPDFに変換する
        
        Args:
            png_path: PNGファイルのパス
            pdf_path: 出力PDFファイルのパス
            
        Returns:
            bool: 変換が成功した場合はTrue
        """
        try:
            img = plt.imread(png_path)
            
            with PdfPages(pdf_path) as pdf:
                plt.figure(figsize=(12, 16))
                plt.imshow(img)
                plt.axis('off')  # 軸を非表示
                pdf.savefig(bbox_inches='tight')
                plt.close()
            
            logger.info(f"PDFに変換しました: {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF変換中にエラーが発生しました: {e}")
            return False
