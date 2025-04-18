
"""
三期決算図生成アプリケーション (Epic Financial Visualizer)
財務計算モジュール - 財務データの処理と計算
"""

import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinanceCalculator:
    """財務データを処理し、分析用のデータフレームを生成するクラス"""
    
    def __init__(self):
        """初期化"""
        self.bs_items = [
            "流動資産合計",
            "現金・預金",
            "有形固定資産",
            "無形固定資産",
            "投資その他",
            "資産合計",
            "流動負債",
            "固定負債",
            "資本金",
            "利益剰余金"
        ]
        
        self.pl_items = [
            "売上高",
            "売上原価",
            "販売費及び一般管理費",
            "営業外収益",
            "営業外費用",
            "特別利益",
            "特別損失",
            "法人税"
        ]
    
    def process_data(self, extracted_data):
        """抽出されたデータを処理し、分析用のデータフレームを生成する
        
        Args:
            extracted_data: 各期のB/SとP/Lデータを含む辞書
                {期: {"bs": {...}, "pl": {...}}}
                
        Returns:
            dict: 処理済みの財務データ
        """
        logger.info("財務データの処理を開始します")
        
        periods = sorted(extracted_data.keys())
        logger.info(f"処理対象期: {periods}")
        
        bs_data = self._process_bs_data(extracted_data, periods)
        
        pl_data = self._process_pl_data(extracted_data, periods)
        
        result = {
            "periods": periods,
            "bs": bs_data,
            "pl": pl_data
        }
        
        logger.info("財務データの処理が完了しました")
        return result
    
    def _process_bs_data(self, extracted_data, periods):
        """B/Sデータを処理する
        
        Args:
            extracted_data: 抽出されたデータ
            periods: 期の一覧
            
        Returns:
            pandas.DataFrame: 処理済みのB/Sデータ
        """
        data = []
        
        for period in periods:
            period_data = extracted_data[period]["bs"]
            row = {"期": period}
            
            for item in self.bs_items:
                row[item] = period_data.get(item, 0)
            
            row["その他資産"] = (row["資産合計"] - 
                            (row["流動資産合計"] + row["有形固定資産"] + 
                             row["無形固定資産"] + row["投資その他"]))
            
            row["純資産合計"] = row["資本金"] + row["利益剰余金"]
            
            row["負債合計"] = row["流動負債"] + row["固定負債"]
            
            row["負債純資産合計"] = row["負債合計"] + row["純資産合計"]
            
            if row["資産合計"] != row["負債純資産合計"]:
                logger.warning(f"{period}期: B/Sのバランスが一致しません " +
                              f"(資産合計: {row['資産合計']}, 負債純資産合計: {row['負債純資産合計']})")
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        df["期"] = df["期"].astype(str)
        df.set_index("期", inplace=True)
        
        return df
    
    def _process_pl_data(self, extracted_data, periods):
        """P/Lデータを処理する
        
        Args:
            extracted_data: 抽出されたデータ
            periods: 期の一覧
            
        Returns:
            pandas.DataFrame: 処理済みのP/Lデータ
        """
        data = []
        
        for period in periods:
            period_data = extracted_data[period]["pl"]
            row = {"期": period}
            
            for item in self.pl_items:
                row[item] = period_data.get(item, 0)
            
            row["売上総利益"] = row["売上高"] - row["売上原価"]
            
            row["営業利益"] = row["売上総利益"] - row["販売費及び一般管理費"]
            
            row["経常利益"] = row["営業利益"] + row["営業外収益"] - row["営業外費用"]
            
            row["税引前当期純利益"] = row["経常利益"] + row["特別利益"] - row["特別損失"]
            
            row["当期純利益"] = row["税引前当期純利益"] - row["法人税"]
            
            data.append(row)
        
        df = pd.DataFrame(data)
        
        df["期"] = df["期"].astype(str)
        df.set_index("期", inplace=True)
        
        return df
