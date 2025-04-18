
"""
三期決算図生成アプリケーション (Epic Financial Visualizer)
ビルドスクリプト - Windows/macOS用の実行ファイルを生成
"""

import os
import sys
import platform
import subprocess
import shutil

def main():
    """ビルドプロセスのメインエントリーポイント"""
    print("三期決算図生成アプリケーション - ビルドスクリプト")
    print("-" * 50)
    
    current_os = platform.system()
    print(f"現在のOS: {current_os}")
    
    app_name = "Marutool"
    main_script = "main.py"
    
    cmd = [
        "poetry", "run", "pyinstaller",
        main_script,
        "--name", app_name,
        "--add-data", "assets/*:assets",
    ]
    
    if current_os == "Windows":
        print("Windows用のビルドを実行します...")
        icon_path = "assets/icon.ico" if os.path.exists("assets/icon.ico") else None
        cmd.extend(["--onefile", "--windowed"])
        if icon_path:
            cmd.extend(["--icon", icon_path])
    elif current_os == "Darwin":  # macOS
        print("macOS用のビルドを実行します...")
        icon_path = "assets/icon.icns" if os.path.exists("assets/icon.icns") else None
        cmd.extend(["--windowed"])
        if icon_path:
            cmd.extend(["--icon", icon_path])
    else:
        print(f"警告: {current_os}はサポートされていません。Linuxとして続行します。")
        cmd.extend([
            "--onefile",
            "--windowed",
        ])
    
    cmd = [item for item in cmd if item is not None]
    
    print("実行コマンド:")
    print(" ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("\nビルドが完了しました！")
        
        if current_os == "Windows":
            output_path = os.path.join("dist", f"{app_name}.exe")
        elif current_os == "Darwin":
            output_path = os.path.join("dist", f"{app_name}.app")
        else:
            output_path = os.path.join("dist", app_name)
        
        print(f"出力ファイル: {os.path.abspath(output_path)}")
        
    except subprocess.CalledProcessError as e:
        print(f"\nエラー: ビルド中にエラーが発生しました。\n{e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
