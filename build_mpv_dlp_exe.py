#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编译脚本 - 将 main.py 和 mpv_download.py 编译为独立的可执行文件
需要安装 PyInstaller: pip install pyinstaller
"""

import os
import sys
import subprocess

def build_exe():
    # 源文件路径
    main_file = "main.py"

    # 检查源文件是否存在
    if not os.path.exists(main_file):
        print(f"错误: 找不到源文件 {main_file}")
        return False

    # 为 main.py 构建命令
    cmd_main = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--name", "mpv-dlp",
        "--clean",
        main_file
    ]

    print("开始编译 mpv-dlp...")
    print(f"执行命令: {' '.join(cmd_main)}")

    try:
        # 执行 main.py 编译
        result = subprocess.run(cmd_main, capture_output=True, text=True)

        if result.returncode == 0:
            print("\n✅ mpv-dlp 编译成功!")
            print("输出文件: dist\\mpv-dlp.exe")
        else:
            print("\n❌ mpv-dlp 编译失败!")
            print("\n错误输出:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"\n❌ mpv-dlp 编译过程中发生错误: {e}")
        return False

def main():
    print("Python 编译为 exe 脚本")
    print("=" * 50)

    # 检查是否安装了 PyInstaller
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("请先运行: pip install pyinstaller")
        return

    # 开始编译
    build_exe()

if __name__ == "__main__":
    main()
