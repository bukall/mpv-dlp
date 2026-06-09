#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接从调用的命令行参数中提取视频链接和标题，保存到 CSV
用法与 show_args.py 类似，接收 mpv 传入的参数
第一列为链接，第二列为标题，第三列为外挂字幕列表
"""

import sys
import io
import os
import re
import csv
from datetime import datetime

# 强制 stdout/stderr 使用 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def get_csv_file_path():
    """获取 CSV 输出文件的完整路径（与脚本同目录）"""
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(script_dir, "videos_from_args.csv")


def extract_from_argv():
    """从命令行参数中提取链接和标题并保存为 CSV"""
    if len(sys.argv) <= 1:
        print("没有传入任何参数")
        return False

    csv_file = get_csv_file_path()
    videos = []

    # 构建完整的命令行参数字符串
    args_string = " ".join(sys.argv[1:])

    # 提取视频项（--{ ... --}）
    items = re.findall(r"--\{\s+(.+?)\s+--\}", args_string, re.DOTALL)

    if not items:
        print(f"未找到包含 --{{ 和 --}} 的视频项")
        return False

    for item in items:
        # 提取 URL（以 http:// 或 https:// 开头）
        url_match = re.search(r"(https?://[^\s]+)", item)
        if not url_match:
            continue

        url = url_match.group(1).strip()

        # 提取标题（--force-media-title= 后面的内容，直到下一个 --）
        title_match = re.search(
            r"--force-media-title=(.+?)(?:\s+--|\s*$)", item
        )

        if title_match:
            title = title_match.group(1).strip()
        else:
            title = ""

        # 提取外挂字幕列表（所有 --sub-file= 参数）
        subtitles = re.findall(r"--sub-file=(https?://[^\s]+)", item)
        subtitles = [s.strip() for s in subtitles]  # 清理空格
        
        if url:
            videos.append((url, title, str(subtitles)))
            subtitle_info = f", {len(subtitles)} 个字幕" if subtitles else ""
            print(f"发现视频: {title or '(无标题)'}{subtitle_info}")

    # 去重（保持原有顺序）
    if videos:
        seen = set()
        unique_videos = []
        for url, title, subtitles in videos:
            if url not in seen:
                seen.add(url)
                unique_videos.append((url, title, subtitles))

        # 写入 CSV（追加模式）
        try:
            # file_exists = os.path.exists(csv_file)
            with open(csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # # 如果文件不存在，写入表头
                # if not file_exists:
                #     writer.writerow(["链接", "标题"])
                writer.writerows(unique_videos)

            print(f"\n成功提取 {len(unique_videos)} 条记录到 CSV")
            print(f"CSV 文件位置: {csv_file}")
            return True
        except Exception as e:
            print(f"保存 CSV 时出错: {e}")
            return False
    else:
        print("未找到任何有效的视频记录")
        return False


def main():
    # 获取脚本名称
    script_name = os.path.basename(sys.argv[0])

    # 打印基本信息
    print(f"脚本名称: {script_name}")
    print(f"参数个数: {len(sys.argv) - 1}")

    # 打印所有参数
    if len(sys.argv) > 1:
        print("\n传入的参数列表:")
        for i, arg in enumerate(sys.argv[1:], start=1):
            # 缩短 URL 显示
            if arg.startswith("http"):
                display_arg = arg[:80] + "..." if len(arg) > 80 else arg
            else:
                display_arg = arg
            print(f"  参数 {i}: {display_arg}")
    else:
        print("\n没有传入任何参数")

    print("\n" + "=" * 50)
    print("正在提取链接和标题...")
    print("=" * 50)

    # 提取并保存到 CSV
    extract_from_argv()


if __name__ == "__main__":
    main()
