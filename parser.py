
"""
三期決算図生成アプリケーション (Epic Financial Visualizer)
PDFパーサーモジュール - テキスト抽出とOCR処理
"""

import os
import re
import tempfile
import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFParser:
    """PDFからテキストを抽出し、必要に応じてOCR処理を行うクラス"""
    
    def __init__(self):
        """初期化"""
        self.ocr_lang = "jpn"
        
        self.bs_patterns = {
            "流動資産合計": r"流動資産[合計|計]",
            "現金・預金": r"現金及び預金|現金・預金",
            "有形固定資産": r"有形固定資産",
            "無形固定資産": r"無形固定資産",
            "投資その他": r"投資その他の資産",
            "資産合計": r"資産[合計|計]",
            "流動負債": r"流動負債[合計|計]",
            "固定負債": r"固定負債[合計|計]",
            "資本金": r"資本金",
            "利益剰余金": r"利益剰余金"
        }
        
        self.pl_patterns = {
            "売上高": r"売上高",
            "売上原価": r"売上原価",
            "販売費及び一般管理費": r"販売費及び一般管理費",
            "営業外収益": r"営業外収益",
            "営業外費用": r"営業外費用",
            "特別利益": r"特別利益",
            "特別損失": r"特別損失",
            "法人税": r"法人税"
        }
    
    def extract_data(self, pdf_path):
        """PDFからデータを抽出する
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            dict: 抽出されたデータ（B/SとP/L）
        """
        logger.info(f"PDFファイルの解析を開始: {pdf_path}")
        
        text = self._extract_text_from_pdf(pdf_path)
        
        if not self._is_text_sufficient(text):
            logger.info("テキスト抽出が不十分なため、OCRを使用します")
            text = self._perform_ocr(pdf_path)
        
        bs_data = self._extract_bs_data(text)
        pl_data = self._extract_pl_data(text)
        
        result = {
            "bs": bs_data,
            "pl": pl_data
        }
        
        logger.info(f"データ抽出完了: {len(bs_data)} B/S項目, {len(pl_data)} P/L項目")
        return result
    
    def _extract_text_from_pdf(self, pdf_path):
        """PDFからテキストを抽出する（複数の方法を試みる）
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            str: 抽出されたテキスト
        """
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            
            if text.strip():
                logger.info("pdfplumberでテキスト抽出成功")
                return text
        except Exception as e:
            logger.warning(f"pdfplumberでのテキスト抽出に失敗: {e}")
        
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text() or ""
            doc.close()
            
            if text.strip():
                logger.info("PyMuPDFでテキスト抽出成功")
                return text
        except Exception as e:
            logger.warning(f"PyMuPDFでのテキスト抽出に失敗: {e}")
        
        logger.warning("テキスト抽出に失敗しました")
        return ""
    
    def _is_text_sufficient(self, text):
        """抽出されたテキストが十分かどうかを判断する
        
        Args:
            text: 抽出されたテキスト
            
        Returns:
            bool: テキストが十分な場合はTrue
        """
        if not text.strip():
            return False
        
        key_terms = ["資産", "負債", "純資産", "売上", "損益"]
        found_terms = sum(1 for term in key_terms if term in text)
        
        return found_terms >= 3
    
    def _perform_ocr(self, pdf_path):
        """PDFをOCR処理してテキストを抽出する
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            str: OCRで抽出されたテキスト
        """
        logger.info("OCR処理を開始します")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                images = convert_from_path(pdf_path, output_folder=temp_dir)
                
                text = ""
                for i, image in enumerate(images):
                    logger.info(f"ページ {i+1}/{len(images)} のOCR処理中...")
                    
                    
                    page_text = pytesseract.image_to_string(image, lang=self.ocr_lang)
                    text += page_text + "\n\n"
                
                logger.info("OCR処理が完了しました")
                return text
                
            except Exception as e:
                logger.error(f"OCR処理中にエラーが発生しました: {e}")
                return ""
    
    def _preprocess_image(self, image):
        """OCRの精度向上のための画像前処理
        
        Args:
            image: PIL Image オブジェクト
            
        Returns:
            PIL Image: 処理後の画像
        """
        image = image.convert('L')
        
        
        return image
    
    def _extract_bs_data(self, text):
        """テキストから貸借対照表(B/S)のデータを抽出する
        
        Args:
            text: 抽出されたテキスト
            
        Returns:
            dict: 抽出されたB/Sデータ
        """
        bs_data = {}
        
        for key, pattern in self.bs_patterns.items():
            value = self._find_financial_value(text, pattern)
            if value is not None:
                bs_data[key] = value
            else:
                logger.warning(f"B/S項目「{key}」が見つかりませんでした")
                bs_data[key] = 0  # デフォルト値
        
        return bs_data
    
    def _extract_pl_data(self, text):
        """テキストから損益計算書(P/L)のデータを抽出する
        
        Args:
            text: 抽出されたテキスト
            
        Returns:
            dict: 抽出されたP/Lデータ
        """
        pl_data = {}
        
        for key, pattern in self.pl_patterns.items():
            value = self._find_financial_value(text, pattern)
            if value is not None:
                pl_data[key] = value
            else:
                logger.warning(f"P/L項目「{key}」が見つかりませんでした")
                pl_data[key] = 0  # デフォルト値
        
        return pl_data
    
    def _find_financial_value(self, text, pattern):
        """テキストから財務項目の値を抽出する
        
        Args:
            text: 抽出されたテキスト
            pattern: 検索パターン
            
        Returns:
            int: 抽出された数値（見つからない場合はNone）
        """
        regex = re.compile(f".*{pattern}.*?([0-9,]+).*")
        matches = regex.findall(text)
        
        if matches:
            value_str = matches[0].replace(",", "")
            try:
                return int(value_str)
            except ValueError:
                logger.warning(f"数値変換に失敗: {value_str}")
                return None
        
        return None
