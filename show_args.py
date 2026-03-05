#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
显示所有传入的命令行参数
当其他程序调用此脚本时，会打印所有传递的参数
"""

import sys
import os
import time
from datetime import datetime

def get_log_file_path():
    """获取日志文件的完整路径（与脚本同目录）"""
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    # 组合日志文件路径
    return os.path.join(script_dir, "show_args.log")

def write_to_log(content):
    """将内容追加写入日志文件"""
    log_file = get_log_file_path()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_content = f"[{timestamp}] {content}\n"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_content)

def write_parameters():
    """只记录参数信息到日志"""
    # 记录完整命令行
    write_to_log(f"完整命令行: {' '.join(sys.argv)}")

    # 记录参数列表
    if len(sys.argv) > 1:
        for i, arg in enumerate(sys.argv[1:], start=1):
            write_to_log(f"参数 {i}: {arg}")
    else:
        write_to_log("没有传入任何参数")

    write_to_log("")

def main():
    # 获取脚本名称
    script_name = os.path.basename(sys.argv[0])

    # 打印基本信息
    print(f"脚本名称: {script_name}")
    print(f"参数个数: {len(sys.argv) - 1}")  # 减去脚本名

    # 打印所有参数
    if len(sys.argv) > 1:
        print("\n传入的参数列表:")
        for i, arg in enumerate(sys.argv[1:], start=1):
            print(f"  参数 {i}: {arg}")
    else:
        print("\n没有传入任何参数")

    # 打印完整命令行
    print(f"\n完整命令行: {' '.join(sys.argv)}")

    # 将参数信息写入日志
    write_parameters()

    # 等待用户按下 Ctrl+C
    print("\n按 Ctrl+C 退出...")
    try:
        # 使用一个无限循环来保持程序运行
        # 使用 time.sleep() 而不是 signal.pause() 以保持跨平台兼容性
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n收到中断信号，程序退出")

if __name__ == "__main__":
    main()
