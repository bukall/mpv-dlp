#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
编译脚本 - 将 batch_download_videos.py 编译为独立的可执行文件
需要安装 PyInstaller: pip install pyinstaller
"""

import os
import sys
import subprocess

def build_exe():
    # 源文件路径
    source_file = "batch_download_videos.py"

    # 检查源文件是否存在
    if not os.path.exists(source_file):
        print(f"错误: 找不到源文件 {source_file}")
        return False

    # 构建命令
    # --onefile: 打包成单个可执行文件
    # --console: 使用控制台窗口（适合命令行程序）
    # --name: 指定输出文件名
    # --clean: 清理临时文件
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--console",
        "--name", "batch_download_videos",
        "--clean",
        source_file
    ]

    print("开始编译...")
    print(f"执行命令: {' '.join(cmd)}")

    try:
        # 执行编译
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("\n✅ 编译成功!")
            print("\n输出文件: dist\\batch_download_videos.exe")
            print("你可以将此 exe 文件分发给其他人使用")
            return True
        else:
            print("\n❌ 编译失败!")
            print("\n错误输出:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"\n❌ 编译过程中出错: {e}")
        return False


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
