"""
シンプル三期決算図生成アプリケーション - GUI
"""

import os
import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QGroupBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from simple_parser import SimpleParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("シンプル三期決算図生成アプリケーション")
        self.setMinimumSize(800, 600)
        
        self.pdf_path = None
        self.bs_data = None
        
        self.init_ui()
    
    def init_ui(self):
        """UIの初期化"""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        
        file_group = QGroupBox("PDFファイル選択")
        file_layout = QVBoxLayout()
        
        file_row = QHBoxLayout()
        self.file_label = QLabel("ファイルが選択されていません")
        self.file_label.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        file_row.addWidget(QLabel("決算書PDF:"))
        file_row.addWidget(self.file_label, 1)
        
        select_button = QPushButton("ファイル選択")
        select_button.clicked.connect(self.select_file)
        file_row.addWidget(select_button)
        
        file_layout.addLayout(file_row)
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        process_button = QPushButton("処理開始")
        process_button.setMinimumHeight(40)
        process_button.clicked.connect(self.process_pdf)
        main_layout.addWidget(process_button)
        
        result_group = QGroupBox("抽出結果")
        result_layout = QVBoxLayout()
        
        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["項目", "金額"])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        result_layout.addWidget(self.result_table)
        
        log_label = QLabel("ログ:")
        result_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        result_layout.addWidget(self.log_text)
        
        result_group.setLayout(result_layout)
        main_layout.addWidget(result_group)
    
    def select_file(self):
        """PDFファイルを選択"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "決算書PDFを選択", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            self.pdf_path = file_path
            self.file_label.setText(os.path.basename(file_path))
            self.log_message(f"ファイルを選択しました: {os.path.basename(file_path)}")
    
    def process_pdf(self):
        """PDFを処理"""
        if not self.pdf_path:
            self.log_message("エラー: PDFファイルが選択されていません", error=True)
            return
        
        self.log_message(f"PDFの処理を開始します: {os.path.basename(self.pdf_path)}")
        
        try:
            parser = SimpleParser()
            self.bs_data = parser.extract_bs_data(self.pdf_path)
            
            self.display_results()
            
            self.log_message("処理が完了しました")
            
        except Exception as e:
            self.log_message(f"エラーが発生しました: {e}", error=True)
    
    def display_results(self):
        """結果をテーブルに表示"""
        if not self.bs_data:
            return
        
        self.result_table.setRowCount(0)
        
        for i, (key, value) in enumerate(self.bs_data.items()):
            self.result_table.insertRow(i)
            
            item_name = QTableWidgetItem(key)
            self.result_table.setItem(i, 0, item_name)
            
            value_str = f"{value:,}円" if value else "0円"
            item_value = QTableWidgetItem(value_str)
            item_value.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.result_table.setItem(i, 1, item_value)
    
    def log_message(self, message, error=False):
        """ログメッセージを表示"""
        if error:
            message = f"<span style='color:red;'>{message}</span>"
        else:
            message = f"<span>{message}</span>"
        
        self.log_text.append(message)
        logger.info(message.replace("<span>", "").replace("</span>", ""))

def main():
    """アプリケーションのメインエントリーポイント"""
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    app = QApplication(sys.argv)
    app.setApplicationName("シンプル三期決算図生成アプリケーション")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
