"""
シンプル三期決算図生成アプリケーション - 統合アプリケーション
"""

import os
import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QGroupBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QSplitter, QFrame, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

from simple_parser import SimpleParser
from simple_visualizer import SimpleVisualizer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """メインウィンドウ"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("シンプル三期決算図生成アプリケーション")
        self.setMinimumSize(1000, 700)
        
        self.pdf_path = None
        self.bs_data = None
        self.chart_path = None
        self.chart_type = "pie"  # デフォルトは円グラフ
        
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
        
        chart_type_group = QGroupBox("グラフタイプ")
        chart_type_layout = QHBoxLayout()
        
        self.chart_type_group = QButtonGroup()
        
        pie_radio = QRadioButton("円グラフ")
        pie_radio.setChecked(True)
        pie_radio.toggled.connect(lambda: self.set_chart_type("pie"))
        self.chart_type_group.addButton(pie_radio)
        chart_type_layout.addWidget(pie_radio)
        
        bar_radio = QRadioButton("棒グラフ")
        bar_radio.toggled.connect(lambda: self.set_chart_type("bar"))
        self.chart_type_group.addButton(bar_radio)
        chart_type_layout.addWidget(bar_radio)
        
        waterfall_radio = QRadioButton("ウォーターフォール")
        waterfall_radio.toggled.connect(lambda: self.set_chart_type("waterfall"))
        self.chart_type_group.addButton(waterfall_radio)
        chart_type_layout.addWidget(waterfall_radio)
        
        chart_type_group.setLayout(chart_type_layout)
        main_layout.addWidget(chart_type_group)
        
        process_button = QPushButton("処理開始")
        process_button.setMinimumHeight(40)
        process_button.clicked.connect(self.process_pdf)
        main_layout.addWidget(process_button)
        
        splitter = QSplitter(Qt.Horizontal)
        
        result_frame = QFrame()
        result_layout = QVBoxLayout(result_frame)
        
        result_label = QLabel("抽出結果:")
        result_layout.addWidget(result_label)
        
        self.result_table = QTableWidget(0, 2)
        self.result_table.setHorizontalHeaderLabels(["項目", "金額"])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        result_layout.addWidget(self.result_table)
        
        splitter.addWidget(result_frame)
        
        chart_frame = QFrame()
        chart_layout = QVBoxLayout(chart_frame)
        
        chart_label = QLabel("グラフ:")
        chart_layout.addWidget(chart_label)
        
        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setStyleSheet("background-color: #f0f0f0;")
        self.chart_label.setMinimumSize(400, 300)
        chart_layout.addWidget(self.chart_label)
        
        splitter.addWidget(chart_frame)
        
        splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter, 1)  # 1は伸縮係数
        
        log_label = QLabel("ログ:")
        main_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        main_layout.addWidget(self.log_text)
    
    def set_chart_type(self, chart_type):
        """グラフタイプを設定"""
        self.chart_type = chart_type
        self.log_message(f"グラフタイプを変更: {chart_type}")
    
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
            
            self.generate_chart()
            
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
    
    def generate_chart(self):
        """グラフを生成"""
        if not self.bs_data:
            return
        
        self.chart_path = "temp_chart.png"
        
        visualizer = SimpleVisualizer()
        
        if self.chart_type == "pie":
            visualizer.create_bs_chart(self.bs_data, self.chart_path)
        elif self.chart_type == "bar":
            visualizer.create_bs_bar_chart(self.bs_data, self.chart_path)
        elif self.chart_type == "waterfall":
            filename = os.path.basename(self.pdf_path)
            period_name = f"第{filename.split('_')[1].split('期')[0]}期" if '_' in filename and '期' in filename else "第6期"
            period_date = "令和3年4月1日～令和4年3月31日"  # デフォルト値
            
            visualizer.create_waterfall_chart(self.bs_data, period_name, period_date, self.chart_path)
        
        self.display_chart()
    
    def display_chart(self):
        """グラフを表示"""
        if not self.chart_path or not os.path.exists(self.chart_path):
            return
        
        pixmap = QPixmap(self.chart_path)
        self.chart_label.setPixmap(pixmap.scaled(
            self.chart_label.width(), 
            self.chart_label.height(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))
    
    def log_message(self, message, error=False):
        """ログメッセージを表示"""
        if error:
            message = f"<span style='color:red;'>{message}</span>"
        else:
            message = f"<span>{message}</span>"
        
        self.log_text.append(message)
        logger.info(message.replace("<span>", "").replace("</span>", ""))
    
    def resizeEvent(self, event):
        """ウィンドウサイズ変更時にグラフをリサイズ"""
        super().resizeEvent(event)
        if hasattr(self, 'chart_label') and self.chart_path:
            self.display_chart()

def main():
    """アプリケーションのメインエントリーポイント"""
    if "DISPLAY" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    app = QApplication(sys.argv)
    app.setApplicationName("シンプル三期決算図生成アプリケーション")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
