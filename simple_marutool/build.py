"""
シンプル三期決算図生成アプリケーション - ビルドスクリプト
"""

import os
import sys
import platform
import subprocess
import logging
import shutil
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """依存関係をチェック"""
    logger.info("依存関係のチェックを開始します...")
    
    try:
        import PyInstaller
        logger.info(f"PyInstallerが見つかりました: {PyInstaller.__version__}")
    except ImportError:
        logger.warning("PyInstallerが見つかりません。インストールします...")
        try:
            subprocess.run(
                ["pip", "install", "pyinstaller"], 
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            logger.info("PyInstallerのインストールが完了しました")
        except subprocess.CalledProcessError as e:
            logger.error(f"PyInstallerのインストールに失敗しました: {e}")
            logger.error(f"エラー出力: {e.stderr}")
            return False
    
    return True

def build_application():
    """アプリケーションをビルド"""
    logger.info("アプリケーションのビルドを開始します...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    app_name = "SimpleMaru"
    main_script = os.path.join(current_dir, "simple_app.py")
    
    if platform.system() == "Windows":
        icon_path = os.path.join(current_dir, "assets", "icon.ico") if os.path.exists(os.path.join(current_dir, "assets", "icon.ico")) else None
        icon_option = f"--icon={icon_path}" if icon_path else ""
        
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            f"--name={app_name}",
            icon_option,
            main_script
        ]
        
        if not icon_option:
            cmd.remove(icon_option)
        
    elif platform.system() == "Darwin":  # macOS
        icon_path = os.path.join(current_dir, "assets", "icon.icns") if os.path.exists(os.path.join(current_dir, "assets", "icon.icns")) else None
        icon_option = f"--icon={icon_path}" if icon_path else ""
        
        cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            f"--name={app_name}",
            icon_option,
            main_script
        ]
        
        if not icon_option:
            cmd.remove(icon_option)
        
    else:  # Linux
        cmd = [
            "pyinstaller",
            "--onefile",
            f"--name={app_name}",
            main_script
        ]
    
    cmd = [c for c in cmd if c]
    
    logger.info(f"ビルドコマンド: {' '.join(cmd)}")
    
    try:
        subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=current_dir
        )
        
        dist_dir = os.path.join(current_dir, "dist")
        if os.path.exists(dist_dir):
            files = os.listdir(dist_dir)
            if files:
                logger.info(f"ビルドが完了しました。出力ファイル: {', '.join(files)}")
                
                executable_path = os.path.join(dist_dir, files[0])
                logger.info(f"実行可能ファイル: {executable_path}")
                
                return True
            else:
                logger.error("ビルドは成功しましたが、出力ファイルが見つかりません")
                return False
        else:
            logger.error("ビルドは成功しましたが、distディレクトリが見つかりません")
            return False
        
    except subprocess.CalledProcessError as e:
        logger.error(f"ビルドに失敗しました: {e}")
        logger.error(f"エラー出力: {e.stderr}")
        return False

def copy_sample_files():
    """サンプルファイルをdistディレクトリにコピー"""
    logger.info("サンプルファイルをコピーします...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(current_dir, "dist")
    
    if not os.path.exists(dist_dir):
        logger.error("distディレクトリが見つかりません")
        return False
    
    sample_files = []
    for file in os.listdir(current_dir):
        if file.endswith(".pdf"):
            sample_files.append(file)
    
    if not sample_files:
        logger.warning("サンプルPDFファイルが見つかりません")
        return True
    
    for file in sample_files:
        src = os.path.join(current_dir, file)
        dst = os.path.join(dist_dir, file)
        try:
            shutil.copy2(src, dst)
            logger.info(f"コピー完了: {file}")
        except Exception as e:
            logger.error(f"ファイルのコピーに失敗しました: {e}")
    
    return True

def main():
    """メインエントリーポイント"""
    logger.info("シンプル三期決算図生成アプリケーションのビルドを開始します...")
    
    if not check_dependencies():
        logger.error("依存関係のチェックに失敗しました")
        return 1
    
    if not build_application():
        logger.error("アプリケーションのビルドに失敗しました")
        return 1
    
    if not copy_sample_files():
        logger.warning("サンプルファイルのコピーに失敗しました")
    
    logger.info("ビルドプロセスが完了しました")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(current_dir, "dist")
    
    if platform.system() == "Windows":
        logger.info("アプリケーションを実行するには:")
        logger.info(f"{dist_dir}\\SimpleMaru.exe をダブルクリックしてください")
    elif platform.system() == "Darwin":  # macOS
        logger.info("アプリケーションを実行するには:")
        logger.info(f"Finderで {dist_dir}/SimpleMaru.app を開いてください")
    else:  # Linux
        logger.info("アプリケーションを実行するには:")
        logger.info(f"{dist_dir}/SimpleMaru を実行してください")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
