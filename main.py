
"""
三期決算図生成アプリケーション (Epic Financial Visualizer)
メインエントリーポイント
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from ui import MainWindow

def main():
    """アプリケーションのメインエントリーポイント"""
    app = QApplication(sys.argv)
    app.setApplicationName("Epic Financial Visualizer")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
