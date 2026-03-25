#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 show_args.log 中提取视频链接和标题
将其保存为 CSV 文件
第一列为链接，第二列为标题
"""

import sys
import os
import re
import csv
from datetime import datetime


def get_log_file_path():
    """获取日志文件的完整路径（与脚本同目录）"""
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(script_dir, "show_args.log")


def get_csv_file_path():
    """获取 CSV 输出文件的完整路径（与脚本同目录）"""
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(script_dir, "videos_from_log.csv")


def extract_links_and_titles():
    """从日志文件中提取链接和标题"""
    log_file = get_log_file_path()
    csv_file = get_csv_file_path()

    if not os.path.exists(log_file):
        print(f"日志文件不存在: {log_file}")
        return False

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 提取完整命令行
        command_lines = re.findall(r"完整命令行: (.+?)(?=\n\[|$)", content, re.DOTALL)

        videos = []

        for command_line in command_lines:
            # 提取视频项（--{ ... --}）
            items = re.findall(r"--\{\s+(.+?)\s+--\}", command_line, re.DOTALL)

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

                if url:
                    videos.append((url, title))
                    print(f"发现: {title or '(无标题)'}")

        # 去重（保持原有顺序）
        seen = set()
        unique_videos = []
        for url, title in videos:
            if url not in seen:
                seen.add(url)
                unique_videos.append((url, title))

        # 写入 CSV
        if unique_videos:
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # writer.writerow(["链接", "标题"])
                writer.writerows(unique_videos)

            print(f"\n成功提取 {len(unique_videos)} 条记录")
            print(f"CSV 文件已保存到: {csv_file}")
            return True
        else:
            print("未找到任何视频记录")
            return False

    except Exception as e:
        print(f"处理文件时出错: {e}")
        return False


def main():
    print("正在从日志文件中提取链接和标题...")
    print("-" * 50)
    extract_links_and_titles()


if __name__ == "__main__":
    main()
