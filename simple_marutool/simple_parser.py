"""
シンプルPDFパーサー - 貸借対照表データ抽出
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

class SimpleParser:
    """PDFから貸借対照表データを抽出するシンプルなクラス"""
    
    def __init__(self):
        """初期化"""
        self.ocr_lang = "jpn"  # 日本語OCR
        
        self.bs_patterns = {
            "流動資産合計": r"流動資産.*?合計|流動資産.*?計",
            "現金・預金": r"現金及び預金|現金・預金",
            "有形固定資産": r"有形固定資産",
            "無形固定資産": r"無形固定資産",
            "投資その他": r"投資その他の資産|投資.*?その他",
            "資産合計": r"資産.*?合計|資産.*?計",
            "流動負債": r"流動負債.*?合計|流動負債.*?計",
            "固定負債": r"固定負債.*?合計|固定負債.*?計",
            "資本金": r"資本金",
            "利益剰余金": r"利益剰余金"
        }
    
    def extract_bs_data(self, pdf_path):
        """PDFから貸借対照表データを抽出する
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            dict: 抽出されたB/Sデータ
        """
        logger.info(f"PDFファイルの解析を開始: {pdf_path}")
        
        text = self._extract_text_from_pdf(pdf_path)
        
        if not text or len(text.strip()) < 100:
            logger.info("テキスト抽出が不十分なため、OCRを使用します")
            text = self._perform_ocr(pdf_path)
        
        logger.info(f"抽出されたテキスト長: {len(text)} 文字")
        
        if text:
            preview = text[:500] + "..." if len(text) > 500 else text
            logger.info(f"テキストプレビュー: {preview}")
        
        bs_data = self._extract_bs_items(text)
        
        logger.info(f"抽出されたB/Sデータ: {bs_data}")
        return bs_data
    
    def _extract_text_from_pdf(self, pdf_path):
        """PDFからテキストを抽出する（複数の方法を試みる）
        
        Args:
            pdf_path: PDFファイルのパス
            
        Returns:
            str: 抽出されたテキスト
        """
        text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text() or ""
                    text += page_text + "\n\n"
            
            if text.strip():
                logger.info("pdfplumberでテキスト抽出成功")
                return text
        except Exception as e:
            logger.warning(f"pdfplumberでのテキスト抽出に失敗: {e}")
        
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                page_text = page.get_text() or ""
                text += page_text + "\n\n"
            doc.close()
            
            if text.strip():
                logger.info("PyMuPDFでテキスト抽出成功")
                return text
        except Exception as e:
            logger.warning(f"PyMuPDFでのテキスト抽出に失敗: {e}")
        
        logger.warning("テキスト抽出に失敗しました")
        return ""
    
    def _extract_bs_items(self, text):
        """テキストから貸借対照表項目を抽出する
        
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
                logger.info(f"項目「{key}」: {value:,}円")
            else:
                logger.warning(f"項目「{key}」が見つかりませんでした")
                bs_data[key] = 0  # デフォルト値
        
        return bs_data
    
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
                logger.info("PDFを画像に変換中...")
                images = convert_from_path(pdf_path, output_folder=temp_dir)
                
                text = ""
                for i, image in enumerate(images):
                    logger.info(f"ページ {i+1}/{len(images)} のOCR処理中...")
                    
                    img_processed = self._preprocess_image(image)
                    
                    page_text = pytesseract.image_to_string(img_processed, lang=self.ocr_lang)
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
        
    def _find_financial_value(self, text, pattern):
        """テキストから財務項目の値を抽出する
        
        Args:
            text: 抽出されたテキスト
            pattern: 検索パターン
            
        Returns:
            int: 抽出された数値（見つからない場合はNone）
        """
        try:
            matches_context = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches_context:
                start_pos = max(0, match.start() - 10)
                end_pos = min(len(text), match.end() + 300)
                context = text[start_pos:end_pos]
                
                item_value_pattern = rf'{pattern}[^\d]*?([\d,\s]+)'
                item_value_matches = re.findall(item_value_pattern, context, re.IGNORECASE)
                
                if item_value_matches:
                    for value_str in item_value_matches:
                        cleaned_value = re.sub(r'[,\s]', '', value_str)
                        try:
                            value = int(cleaned_value)
                            if value >= 10000:
                                logger.info(f"「{pattern}」の値を抽出: {value_str} -> {value:,}円")
                                return value
                        except ValueError:
                            continue
                
                value_patterns = [
                    r'([0-9]{1,3}(?:,\s*[0-9]{3})+)',  # 58, 894, 722 形式
                    r'([0-9]{1,3}(?:,[0-9]{3})+)',      # 58,894,722 形式
                    r'([0-9]+\s*[0-9]{3}\s*[0-9]{3})',  # 58 894 722 形式
                ]
                
                for value_pattern in value_patterns:
                    value_matches = re.findall(value_pattern, context)
                    if value_matches:
                        for value_str in value_matches:
                            cleaned_value = re.sub(r'[,\s]', '', value_str)
                            try:
                                value = int(cleaned_value)
                                if value >= 10000:
                                    logger.info(f"「{pattern}」の値を抽出: {value_str} -> {value:,}円")
                                    return value
                            except ValueError:
                                continue
            
            logger.warning(f"「{pattern}」に対応する値が見つかりませんでした")
            return None
            
        except Exception as e:
            logger.error(f"値の抽出中にエラーが発生しました: {e}")
            return None

if __name__ == "__main__":
    pdf_path = "エピック_6期決算書.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"PDFファイルが見つかりません: {pdf_path}")
    else:
        parser = SimpleParser()
        bs_data = parser.extract_bs_data(pdf_path)
        
        print("\n===== 貸借対照表データ =====")
        for key, value in bs_data.items():
            print(f"{key}: {value:,}円")
