#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载视频脚本
从 CSV 文件读取视频链接、标题和字幕列表，逐个下载到本地
CSV 格式: 第一列为链接，第二列为标题（作为文件名），第三列为字幕URL列表
"""

import sys
import os
import csv
import time
from pathlib import Path
from typing import List, Tuple
import ast

# 导入 mpv_download 模块
from mpv_download import download_video, download_subtitles


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
    如果直接按回车，使用默认文件 "videos_from_args.csv"
    
    返回值:
        CSV 文件的完整路径
    """
    while True:
        csv_path = input("\n请输入 CSV 文件路径 (默认: videos_from_args.csv): ").strip()
        
        # 如果为空，使用默认值
        if not csv_path:
            csv_path = "videos_from_args.csv"
        
        # 移除引号（如果有）
        csv_path = csv_path.strip('"\'')
        
        if not os.path.exists(csv_path):
            print(f"❌ 文件不存在: {csv_path}")
            continue
        
        if not csv_path.lower().endswith('.csv'):
            print("❌ 请提供 .csv 文件")
            continue
        
        return csv_path


def read_csv_file(csv_path: str) -> List[Tuple[str, str, List[str]]]:
    """
    读取 CSV 文件并提取链接、标题和字幕列表
    
    参数:
        csv_path: CSV 文件路径
    
    返回值:
        [(链接, 标题, 字幕URL列表), ...] 列表
    """
    videos = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            for row_num, row in enumerate(reader, start=1):
                if len(row) < 1:
                    print(f"⚠️  第 {row_num} 行数据不足，跳过")
                    continue
                
                url = row[0].strip()
                title = row[1].strip() if len(row) > 1 else ""
                
                # 读取字幕列表（第三列）
                subtitles = []
                if len(row) > 2 and row[2].strip():
                    try:
                        # 尝试解析字幕列表字符串为 Python 列表
                        subtitles = ast.literal_eval(row[2].strip())
                        if not isinstance(subtitles, list):
                            subtitles = []
                    except (ValueError, SyntaxError):
                        # 解析失败时，尝试将其作为单个 URL
                        subtitle_str = row[2].strip()
                        if subtitle_str.startswith('http'):
                            subtitles = [subtitle_str]
                        else:
                            print(f"⚠️  第 {row_num} 行字幕格式无法解析: {subtitle_str[:50]}")
                            subtitles = []
                
                if not url:
                    print(f"⚠️  第 {row_num} 行链接为空，跳过")
                    continue
                
                if not title:
                    print(f"⚠️  第 {row_num} 行标题为空，使用链接作为文件名")
                    title = url.split('/')[-1].split('?')[0] or "video"
                
                videos.append((url, title, subtitles))
    
    except Exception as e:
        print(f"❌ 读取 CSV 文件失败: {e}")
        return []
    
    return videos


def confirm_download(videos: List[Tuple[str, str, List[str]]]) -> bool:
    """
    显示将要下载的视频和字幕列表，询问用户确认
    
    参数:
        videos: [(链接, 标题, 字幕URL列表), ...] 列表
    
    返回值:
        True 确认下载，False 取消
    """
    print("\n" + "=" * 70)
    print(f"📋 将要下载 {len(videos)} 个视频:")
    print("=" * 70)
    
    for i, (url, title, subtitles) in enumerate(videos, 1):
        print(f"{i}. 文件名: {title}")
        print(f"   URL: {url[:80]}{'...' if len(url) > 80 else ''}")
        if subtitles:
            print(f"   📝 字幕: {len(subtitles)} 个")
            for j, sub_url in enumerate(subtitles, 1):
                print(f"      {j}. {sub_url[:60]}{'...' if len(sub_url) > 60 else ''}")
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


def ask_download_mode() -> bool:
    """
    询问用户下载模式
    
    返回值:
        True 表示只下载字幕，False 表示下载视频和字幕
    """
    print("\n" + "=" * 70)
    print("📋 选择下载模式:")
    print("=" * 70)
    
    while True:
        choice = input("只下载字幕? (默认: 否)(y/N): ").strip().lower()
        if choice in ('y', 'yes', '是', '1'):
            return True
        elif choice in ('n', 'no', '否', '0', ''):
            return False
        else:
            print("❌ 请输入 y 或 n，或直接按回车")


def download_videos(videos: List[Tuple[str, str, List[str]]], wait_seconds: int = 5, subtitles_only: bool = False) -> None:
    """
    逐个下载视频及其字幕，每个下载完成后等待指定秒数
    
    参数:
        videos: [(链接, 标题, 字幕URL列表), ...] 列表
        wait_seconds: 每个下载完成后等待的秒数（默认 5）
        subtitles_only: 是否仅下载字幕，默认 False（同时下载视频和字幕）
    """
    total = len(videos)
    
    for i, (url, title, subtitles) in enumerate(videos, 1):
        print("\n" + "=" * 70)
        if subtitles_only:
            print(f"📝 [{i}/{total}] 正在下载字幕: {title}")
        else:
            print(f"📥 [{i}/{total}] 正在下载: {title}")
        print("=" * 70)
        
        try:
            # 如果不是仅下载字幕模式，先下载视频
            if not subtitles_only:
                success = download_video(
                    url=url,
                    output_filename=title
                )
                
                if not success:
                    print(f"❌ [{i}/{total}] 视频下载失败: {title}")
                    # 即使视频下载失败，也继续下载字幕（如果有的话）
                else:
                    print(f"✅ [{i}/{total}] 视频下载完成: {title}")
            
            # 下载字幕
            if subtitles:
                print(f"📝 [{i}/{total}] 正在下载 {len(subtitles)} 个字幕...")
                video_filename = title
                # 添加视频后缀（如果用户没有指定）
                if not any(title.endswith(ext) for ext in ['.mkv', '.mp4', '.flv', '.m3u8', '.avi', '.mov', '.webm']):
                    video_filename = title + '.mkv'  # 默认后缀
                
                if download_subtitles(subtitles, video_filename):
                    print(f"✅ [{i}/{total}] 字幕下载完成")
                else:
                    print(f"⚠️  [{i}/{total}] 部分字幕下载失败")
            elif not subtitles_only:
                # 仅在不是仅下载字幕模式且视频下载成功时才显示此消息
                if subtitles is not None:
                    pass  # 没有字幕，不显示任何消息
        
        except KeyboardInterrupt:
            print(f"\n⚠️  用户中断下载")
            raise
        
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
    
    # 询问下载模式
    subtitles_only = ask_download_mode()
    
    # 开始下载
    if subtitles_only:
        print("\n ⏳ 开始仅下载字幕...")
    else:
        print("\n ⏳ 开始下载视频和字幕...")
    
    download_videos(videos, wait_seconds=5, subtitles_only=subtitles_only)


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
