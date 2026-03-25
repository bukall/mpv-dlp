#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载视频脚本
从 CSV 文件读取视频链接和标题，逐个下载到本地
CSV 格式: 第一列为链接，第二列为标题（作为文件名）
"""

import sys
import os
import csv
import time
from pathlib import Path
from typing import List, Tuple

# 导入 mpv_download 模块
from mpv_download import download_video


def get_csv_file_from_args() -> str:
    """
    从命令行参数获取 CSV 文件路径
    
    返回值:
        CSV 文件的完整路径，如果没有参数则返回 None
    """
    if len(sys.argv) > 1:
        csv_path = sys.argv[1].strip()
        # 移除引号（如果有）
        csv_path = csv_path.strip('"\'')
        
        if os.path.exists(csv_path) and csv_path.lower().endswith('.csv'):
            return csv_path
    
    return None


def get_csv_file_from_user() -> str:
    """
    从用户输入获取 CSV 文件路径
    
    返回值:
        CSV 文件的完整路径
    """
    while True:
        csv_path = input("\n请输入 CSV 文件路径: ").strip()
        
        if not csv_path:
            print("❌ 路径不能为空，请重新输入")
            continue
        
        # 移除引号（如果有）
        csv_path = csv_path.strip('"\'')
        
        if not os.path.exists(csv_path):
            print(f"❌ 文件不存在: {csv_path}")
            continue
        
        if not csv_path.lower().endswith('.csv'):
            print("❌ 请提供 .csv 文件")
            continue
        
        return csv_path


def read_csv_file(csv_path: str) -> List[Tuple[str, str]]:
    """
    读取 CSV 文件并提取链接和标题
    
    参数:
        csv_path: CSV 文件路径
    
    返回值:
        [(链接, 标题), ...] 列表
    """
    videos = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # 跳过标题行
            header = next(reader, None)
            
            for row_num, row in enumerate(reader, start=2):
                if len(row) < 2:
                    print(f"⚠️  第 {row_num} 行数据不足，跳过")
                    continue
                
                url, title = row[0].strip(), row[1].strip()
                
                if not url:
                    print(f"⚠️  第 {row_num} 行链接为空，跳过")
                    continue
                
                if not title:
                    print(f"⚠️  第 {row_num} 行标题为空，使用链接作为文件名")
                    title = url.split('/')[-1].split('?')[0] or "video"
                
                videos.append((url, title))
    
    except Exception as e:
        print(f"❌ 读取 CSV 文件失败: {e}")
        return []
    
    return videos


def confirm_download(videos: List[Tuple[str, str]]) -> bool:
    """
    显示将要下载的视频列表，询问用户确认
    
    参数:
        videos: [(链接, 标题), ...] 列表
    
    返回值:
        True 确认下载，False 取消
    """
    print("\n" + "=" * 70)
    print(f"📋 将要下载 {len(videos)} 个视频:")
    print("=" * 70)
    
    for i, (url, title) in enumerate(videos, 1):
        print(f"{i}. 文件名: {title}")
        print(f"   URL: {url[:80]}{'...' if len(url) > 80 else ''}")
        print()
    
    print("=" * 70)
    
    while True:
        choice = input("确认开始下载? (Y/n): ").strip().lower()
        if choice in ('y', 'yes', '是', '确认', ''):
            return True
        elif choice in ('n', 'no', '否', '取消'):
            return False
        else:
            print("❌ 请输入 y 或 n，或直接按回车确认")


def download_videos(videos: List[Tuple[str, str]], wait_seconds: int = 5) -> None:
    """
    逐个下载视频，每个下载完成后等待指定秒数
    
    参数:
        videos: [(链接, 标题), ...] 列表
        wait_seconds: 每个下载完成后等待的秒数（默认 5）
    """
    total = len(videos)
    
    for i, (url, title) in enumerate(videos, 1):
        print("\n" + "=" * 70)
        print(f"📥 [{i}/{total}] 正在下载: {title}")
        print("=" * 70)
        
        try:
            # 调用 mpv_download.py 的下载函数
            # 只传入链接和文件名，其余参数使用默认值
            success = download_video(
                url=url,
                output_filename=title
            )
            
            if success:
                print(f"✅ [{i}/{total}] 下载完成: {title}")
            else:
                print(f"❌ [{i}/{total}] 下载失败: {title}")
        
        except Exception as e:
            print(f"❌ [{i}/{total}] 下载出错: {e}")
        
        # 如果不是最后一个视频，等待指定时间
        if i < total:
            print(f"\n⏳ 等待 {wait_seconds} 秒后下载下一个视频...")
            for remaining in range(wait_seconds, 0, -1):
                print(f"   {remaining} 秒...", end='\r')
                time.sleep(1)
            print("                  ", end='\r')  # 清空倒计时显示
    
    print("\n" + "=" * 70)
    print("✉️  所有视频下载完成!")
    print("=" * 70)


def main():
    """主程序入口"""
    print("\n" + "=" * 70)
    print("🎬 视频批量下载工具")
    print("=" * 70)
    
    # 首先尝试从命令行参数获取 CSV 文件
    csv_path = get_csv_file_from_args()
    
    if csv_path:
        print(f"📂 检测到命令行参数: {csv_path}")
    else:
        # 如果没有命令行参数，从用户输入获取
        csv_path = get_csv_file_from_user()
    
    # 读取 CSV 文件
    print(f"\n📂 读取 CSV 文件: {csv_path}")
    videos = read_csv_file(csv_path)
    
    if not videos:
        print("❌ 未找到任何有效的视频记录")
        return
    
    print(f"✅ 成功读取 {len(videos)} 条视频记录")
    
    # 确认下载
    if not confirm_download(videos):
        print("\n❌ 已取消下载")
        return
    
    # 开始下载
    download_videos(videos, wait_seconds=5)


if __name__ == "__main__":
    try:
        main()
            
        # 保持程序运行，等待用户按下 Ctrl+C
        print("\n按 Ctrl+C 退出...")
        try:
            # 使用一个无限循环来保持程序运行
            # 使用 time.sleep() 而不是其他方式以保持跨平台兼容性
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n收到中断信号，程序退出")
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断下载任务")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序错误: {e}")
        sys.exit(1)
