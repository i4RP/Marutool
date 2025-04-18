
"""
三期決算図生成アプリケーション (Epic Financial Visualizer)
GUI実装
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QProgressBar,
                            QMessageBox, QComboBox, QGroupBox, QRadioButton,
                            QButtonGroup, QSplitter, QScrollArea)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from parser import PDFParser
from finance_calc import FinanceCalculator
from chart_generator import ChartGenerator

class WorkerThread(QThread):
    """バックグラウンド処理用のワーカースレッド"""
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(dict, str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, pdf_files):
        super().__init__()
        self.pdf_files = pdf_files
        
    def run(self):
        try:
            self.progress_signal.emit(10, "PDFファイルを解析中...")
            parser = PDFParser()
            
            extracted_data = {}
            for i, pdf_file in enumerate(self.pdf_files):
                period = os.path.basename(pdf_file).split('_')[1].replace('期決算書', '').replace('.pdf', '')
                self.progress_signal.emit(20 + i*20, f"{period}期のデータを抽出中...")
                extracted_data[period] = parser.extract_data(pdf_file)
            
            self.progress_signal.emit(70, "財務データを計算中...")
            calculator = FinanceCalculator()
            financial_data = calculator.process_data(extracted_data)
            
            self.progress_signal.emit(90, "グラフを生成中...")
            chart_generator = ChartGenerator()
            chart_path = chart_generator.generate_chart(financial_data)
            
            self.progress_signal.emit(100, "完了")
            self.finished_signal.emit(financial_data, chart_path)
            
        except Exception as e:
            self.error_signal.emit(f"エラーが発生しました: {str(e)}")

class MainWindow(QMainWindow):
    """メインウィンドウクラス"""
    
    def __init__(self):
        super().__init__()
        
        self.pdf_files = []
        self.chart_path = None
        self.financial_data = None
        
        self.init_ui()
        
    def init_ui(self):
        """UIの初期化"""
        self.setWindowTitle("三期決算図生成アプリケーション")
        self.setMinimumSize(800, 600)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        file_group = QGroupBox("PDFファイル選択")
        file_layout = QVBoxLayout()
        
        for i in range(3):
            file_row = QHBoxLayout()
            label = QLabel(f"{i+1}期目:")
            self.file_labels = []
            file_label = QLabel("ファイルが選択されていません")
            file_label.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
            self.file_labels.append(file_label)
            
            select_btn = QPushButton("選択...")
            select_btn.clicked.connect(lambda checked, idx=i: self.select_file(idx))
            
            file_row.addWidget(label)
            file_row.addWidget(file_label, 1)
            file_row.addWidget(select_btn)
            file_layout.addLayout(file_row)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        process_group = QGroupBox("処理")
        process_layout = QVBoxLayout()
        
        format_layout = QHBoxLayout()
        format_label = QLabel("出力形式:")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "PDF"])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch(1)
        
        process_layout.addLayout(format_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_label = QLabel("準備完了")
        
        process_layout.addWidget(self.progress_bar)
        process_layout.addWidget(self.progress_label)
        
        button_layout = QHBoxLayout()
        self.process_btn = QPushButton("処理開始")
        self.process_btn.clicked.connect(self.start_processing)
        self.process_btn.setEnabled(False)
        
        self.save_btn = QPushButton("保存...")
        self.save_btn.clicked.connect(self.save_chart)
        self.save_btn.setEnabled(False)
        
        button_layout.addWidget(self.process_btn)
        button_layout.addWidget(self.save_btn)
        
        process_layout.addLayout(button_layout)
        process_group.setLayout(process_layout)
        main_layout.addWidget(process_group)
        
        preview_group = QGroupBox("プレビュー")
        preview_layout = QVBoxLayout()
        
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_label = QLabel("処理を実行すると、ここにプレビューが表示されます")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0;")
        self.preview_scroll.setWidget(self.preview_label)
        
        preview_layout.addWidget(self.preview_scroll)
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group, 1)
        
    def select_file(self, index):
        """PDFファイルの選択"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "PDFファイルを選択", "", "PDF Files (*.pdf)"
        )
        
        if file_path:
            file_name = os.path.basename(file_path)
            self.file_labels[index].setText(file_name)
            
            if index >= len(self.pdf_files):
                self.pdf_files.append(file_path)
            else:
                self.pdf_files[index] = file_path
            
            if len(self.pdf_files) == 3 and all(self.pdf_files):
                self.process_btn.setEnabled(True)
            else:
                self.process_btn.setEnabled(False)
    
    def start_processing(self):
        """処理を開始"""
        if len(self.pdf_files) != 3:
            QMessageBox.warning(self, "警告", "3つのPDFファイルを選択してください")
            return
        
        self.process_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_label.setText("処理を開始します...")
        
        self.worker = WorkerThread(self.pdf_files)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.processing_finished)
        self.worker.error_signal.connect(self.processing_error)
        self.worker.start()
    
    def update_progress(self, value, message):
        """進捗の更新"""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
    
    def processing_finished(self, financial_data, chart_path):
        """処理完了時の処理"""
        self.financial_data = financial_data
        self.chart_path = chart_path
        
        pixmap = QPixmap(chart_path)
        self.preview_label = QLabel()
        self.preview_label.setPixmap(pixmap)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_scroll.setWidget(self.preview_label)
        
        self.save_btn.setEnabled(True)
        self.process_btn.setEnabled(True)
        self.progress_label.setText("処理が完了しました。保存ボタンで画像を保存できます。")
    
    def processing_error(self, error_message):
        """エラー発生時の処理"""
        QMessageBox.critical(self, "エラー", error_message)
        self.process_btn.setEnabled(True)
        self.progress_label.setText("エラーが発生しました。")
    
    def save_chart(self):
        """グラフの保存"""
        if not self.chart_path:
            QMessageBox.warning(self, "警告", "保存するグラフがありません")
            return
        
        output_format = self.format_combo.currentText().lower()
        
        default_name = f"エピック_三期決算図.{output_format}"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "グラフを保存", default_name, 
            f"{output_format.upper()} Files (*.{output_format})"
        )
        
        if file_path:
            if not file_path.lower().endswith(f".{output_format}"):
                file_path += f".{output_format}"
            
            if output_format == "png" and self.chart_path.endswith(".png"):
                import shutil
                shutil.copy(self.chart_path, file_path)
            elif output_format == "pdf":
                from chart_generator import ChartGenerator
                ChartGenerator.convert_to_pdf(self.chart_path, file_path)
            
            QMessageBox.information(self, "保存完了", f"グラフを保存しました:\n{file_path}")
