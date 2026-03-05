#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mpv-dlp 交互式主程序

与用户交互，收集下载参数，调用 mpv_download.py 执行实际下载。
支持显示所有默认值，按 Enter 使用默认值，循环菜单修改参数等功能。

典型用法:
    python main.py
"""

import sys
import os

# 导入下载模块
from mpv_download import download_video, MPVNotFoundError


class DownloadUI:
    """交互式用户界面"""
    
    def __init__(self):
        """初始化 UI"""
        self.url = ""
        self.mode = "stream-dump"
        self.save_subtitle = False
        self.subtitle_filename = ""
        self.display_video = False
        self.enable_audio = False
        self.enable_cache = True
        self.output_filename = ""
    
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """打印标题"""
        print("=" * 60)
        print("          🎬 mpv-dlp 视频下载工具")
        print("=" * 60)
    
    def print_separator(self):
        """打印分隔线"""
        print("-" * 60)
    
    def prompt_url(self) -> bool:
        """
        询问视频链接
        
        返回值:
            True 成功输入，False 用户中止
        """
        self.print_header()
        print("\n📌 第一步：输入视频链接")
        print("\n您需要提供要下载的视频地址。")
        print("支持的格式：http:// 或 https:// 开头的链接\n")
        
        while True:
            url = input("请输入视频链接 (输入 'q' 返回): ").strip()
            
            if url.lower() == 'q':
                return False
            
            if not url:
                print("❌ 链接不能为空，请重试\n")
                continue
            
            if not (url.startswith('http://') or url.startswith('https://')):
                print("❌ 链接必须以 http:// 或 https:// 开头，请重试\n")
                continue
            
            self.url = url
            return True
    
    def prompt_mode(self) -> bool:
        """
        选择录制模式
        
        返回值:
            True 成功选择，False 用户中止
        """
        self.clear_screen()
        self.print_header()
        print("\n📌 第二步：选择录制模式")
        print(self.print_separator())
        
        print("\n【模式说明】")
        print("\n1️⃣  stream-dump (推荐用于完整下载)")
        print("   实现原理: 原始传输层数据包直接保存")
        print("   技术特点: 保留完整传输协议信息")
        print("   优势: 完整下载所有音轨和字幕")
        print("   ⚠️  不推荐用于直播\n")
        
        print("2️⃣  stream-record (推荐用于直播)")
        print("   实现原理: 在播放过程中实时转封装原始流数据")
        print("   技术特点: 保持原始编码格式，不进行重编码")
        print("   优势: 零质量损失，低系统资源占用")
        print("   ⚠️  只录制一个音轨和一个字幕轨道")
        print("   ⚠️  不推荐用于完整视频下载\n")
        
        while True:
            print(f"当前选择: {self.mode}")
            choice = input("请选择 (1: stream-dump, 2: stream-record, 按 Enter 使用默认): ").strip()
            
            if choice == '':
                print(f"✅ 使用默认: {self.mode}\n")
                return True
            
            if choice == '1':
                self.mode = "stream-dump"
                print(f"✅ 已选择: stream-dump\n")
                return True
            elif choice == '2':
                self.mode = "stream-record"
                print(f"✅ 已选择: stream-record\n")
                return True
            else:
                print("❌ 无效选择，请输入 1 或 2\n")
    
    def prompt_subtitle(self) -> bool:
        """
        询问是否保存字幕
        
        返回值:
            True 成功选择，False 用户中止
        """
        self.clear_screen()
        self.print_header()
        print("\n📌 第三步：是否保存字幕")
        print(self.print_separator())
        
        print("\n【说明】")
        print("视频文件中通常内嵌了字幕，建议不单独保存。")
        print("仅在需要提取单独字幕文件时选择保存。\n")
        
        while True:
            current = "是" if self.save_subtitle else "否"
            print(f"当前选择: {current}")
            choice = input("是否保存字幕? (是/y/yes/1 或 否/n/no/0, 按 Enter 使用默认): ").strip().lower()
            
            if choice == '':
                print(f"✅ 使用默认: {'是' if self.save_subtitle else '否'}\n")
                return True
            
            if choice in ['是', 'y', 'yes', '1']:
                self.save_subtitle = True
                print("✅ 将保存字幕文件\n")
                return True
            elif choice in ['否', 'n', 'no', '0']:
                self.save_subtitle = False
                print("✅ 不保存字幕文件\n")
                return True
            else:
                print("❌ 无效选择，请输入 '是'/'y'/'yes'/'1' 或 '否'/'n'/'no'/'0'\n")
    
    def prompt_subtitle_filename(self) -> bool:
        """
        询问字幕文件名（仅当 save_subtitle=True 时调用）
        
        返回值:
            True 成功输入，False 用户中止
        """
        self.clear_screen()
        self.print_header()
        print("\n📌 第三步续：输入字幕文件名")
        print(self.print_separator())
        
        print("\n【说明】")
        print("输入自定义字幕文件名（可含或不含后缀）")
        print("示例: 'my_subtitle' 或 'my_subtitle.srt'")
        print("默认: 自动生成（使用视频文件名 + .srt）\n")
        
        default_desc = "自动生成"
        current = self.subtitle_filename if self.subtitle_filename else default_desc
        print(f"当前设置: {current}")
        
        filename = input("输入字幕文件名 (按 Enter 使用默认): ").strip()
        
        if filename:
            self.subtitle_filename = filename
            print(f"✅ 已设置: {filename}\n")
        else:
            self.subtitle_filename = None  # 设置为 None 而不是空字符串
            print(f"✅ 使用默认: 自动生成\n")
        
        return True
    
    def prompt_display_video(self) -> bool:
        """
        询问是否显示画面
        
        返回值:
            True 成功选择，False 用户中止
        """
        self.clear_screen()
        self.print_header()
        print("\n📌 第四步：是否显示画面")
        print(self.print_separator())
        
        # 根据模式设置默认值
        if self.mode == "stream-record":
            default_display = True
            default_str = "是 (stream-record 模式默认)"
        else:
            default_display = False
            default_str = "否 (stream-dump 模式默认)"
        
        print("\n【说明】")
        print("关闭画面可以减少资源占用，加快下载速度。\n")
        print(f"默认值 ({self.mode} 模式): {default_str}\n")
        
        while True:
            current = "是" if self.display_video else "否"
            choice = input("显示画面? (是/y/yes/1 或 否/n/no/0, 按 Enter 使用默认): ").strip().lower()
            
            if choice == '':
                self.display_video = default_display
                print(f"✅ 使用默认: {'是' if self.display_video else '否'}\n")
                return True
            
            if choice in ['是', 'y', 'yes', '1']:
                self.display_video = True
                print("✅ 将显示下载过程\n")
                return True
            elif choice in ['否', 'n', 'no', '0']:
                self.display_video = False
                print("✅ 不显示下载过程\n")
                return True
            else:
                print("❌ 无效选择，请输入 '是'/'y'/'yes'/'1' 或 '否'/'n'/'no'/'0'\n")
    
    def prompt_enable_audio(self) -> bool:
        """
        询问是否开启声音
        
        返回值:
            True 成功选择，False 用户中止
        """
        self.clear_screen()
        self.print_header()
        print("\n📌 第五步：是否开启声音")
        print(self.print_separator())
        
        # 根据模式设置默认值
        if self.mode == "stream-record":
            default_audio = True
            default_str = "是 (stream-record 模式默认)"
        else:
            default_audio = False
            default_str = "否 (stream-dump 模式默认)"
        
        print("\n【说明】")
        print("关闭声音可以减少资源占用。\n")
        print(f"默认值 ({self.mode} 模式): {default_str}\n")
        
        while True:
            current = "是" if self.enable_audio else "否"
            choice = input("开启声音? (是/y/yes/1 或 否/n/no/0, 按 Enter 使用默认): ").strip().lower()
            
            if choice == '':
                self.enable_audio = default_audio
                print(f"✅ 使用默认: {'是' if self.enable_audio else '否'}\n")
                return True
            
            if choice in ['是', 'y', 'yes', '1']:
                self.enable_audio = True
                print("✅ 将开启声音\n")
                return True
            elif choice in ['否', 'n', 'no', '0']:
                self.enable_audio = False
                print("✅ 不开启声音\n")
                return True
            else:
                print("❌ 无效选择，请输入 '是'/'y'/'yes'/'1' 或 '否'/'n'/'no'/'0'\n")
    
    def prompt_enable_cache(self) -> bool:
        """
        询问是否开启缓存
        
        返回值:
            True 成功选择，False 用户中止
        """
        self.clear_screen()
        self.print_header()
        print("\n📌 第六步：是否开启缓存")
        print(self.print_separator())
        
        print("\n【说明】")
        print("缓存可以提高网络流的下载稳定性。")
        print("对于网络较差的环境，建议开启。")
        print("默认值: 是 (推荐)\n")
        
        while True:
            current = "是" if self.enable_cache else "否"
            choice = input("开启缓存? (是/y/yes/1 或 否/n/no/0, 按 Enter 使用默认): ").strip().lower()
            
            if choice == '':
                self.enable_cache = True
                print("✅ 使用默认: 是\n")
                return True
            
            if choice in ['是', 'y', 'yes', '1']:
                self.enable_cache = True
                print("✅ 将开启缓存\n")
                return True
            elif choice in ['否', 'n', 'no', '0']:
                self.enable_cache = False
                print("✅ 不开启缓存\n")
                return True
            else:
                print("❌ 无效选择，请输入 '是'/'y'/'yes'/'1' 或 '否'/'n'/'no'/'0'\n")
    
    def prompt_output_filename(self) -> bool:
        """
        询问自定义输出文件名
        
        返回值:
            True 成功输入，False 用户中止
        """
        self.clear_screen()
        self.print_header()
        print("\n📌 第七步：自定义输出文件名")
        print(self.print_separator())
        
        print("\n【说明】")
        print("输入自定义视频文件名（可含或不含后缀）")
        print("示例: 'my_video' 或 'my_video.mkv'")
        print("默认: 自动从 URL 提取或生成\n")
        
        print("后缀优先级:")
        print("  1. 用户指定的后缀 (如 .mp4, .mkv)")
        print("  2. 从 URL 提取的后缀")
        print("  3. 默认后缀 (.mkv)\n")
        
        default_desc = "自动获取"
        current = self.output_filename if self.output_filename else default_desc
        print(f"当前设置: {current}")
        
        filename = input("输入视频文件名 (按 Enter 使用默认): ").strip()
        
        if filename:
            self.output_filename = filename
            print(f"✅ 已设置: {filename}\n")
        else:
            self.output_filename = None  # 设置为 None 而不是空字符串
            print(f"✅ 使用默认: 自动获取\n")
        
        return True
    
    def show_confirmation(self):
        """显示配置确认界面"""
        self.clear_screen()
        self.print_header()
        print("\n📋 下载配置确认")
        print("=" * 60)
        
        print(f"\n视频链接:           {self.url}")
        print(f"录制模式:           {self.mode}")
        print(f"保存字幕:           {'是' if self.save_subtitle else '否'}")
        
        if self.save_subtitle:
            subtitle_name = self.subtitle_filename if self.subtitle_filename else "[自动生成]"
            print(f"字幕文件名:         {subtitle_name}")
        
        print(f"显示画面:           {'是' if self.display_video else '否'}")
        print(f"开启声音:           {'是' if self.enable_audio else '否'}")
        print(f"开启缓存:           {'是' if self.enable_cache else '否'}")
        
        output_name = self.output_filename if self.output_filename else "[自动获取]"
        print(f"视频文件名:         {output_name}")
        
        print("\n" + "=" * 60)
        
        # 显示预览的 mpv 命令（需要先生成文件名）
        print("\n🎬 预览 mpv 命令:")
        print("-" * 60)
        try:
            from mpv_download import (
                MPVPathFinder, FileNameManager, DownloadConfig, VideoDownloader
            )
            
            # 初始化必要的对象
            mpv_finder = MPVPathFinder()
            mpv_path = mpv_finder.get_mpv_path()
            file_name_manager = FileNameManager(mpv_path)
            
            # 获取实际的文件名
            actual_output = file_name_manager.get_video_filename(
                self.url, self.output_filename
            )
            
            actual_subtitle = None
            if self.save_subtitle:
                actual_subtitle = file_name_manager.get_subtitle_filename(
                    actual_output, self.subtitle_filename
                )
            
            # 创建配置对象
            config = DownloadConfig(
                url=self.url,
                mode=self.mode,
                save_subtitle=self.save_subtitle,
                subtitle_filename=actual_subtitle,
                display_video=self.display_video,
                enable_audio=self.enable_audio,
                enable_cache=self.enable_cache,
                output_filename=actual_output
            )
            
            # 创建下载器来获取完整命令
            downloader = VideoDownloader(mpv_path, file_name_manager)
            full_command = downloader.get_full_command_display(config)
            
            print(full_command)
        except Exception as e:
            print(f"(无法显示完整命令: {e})")
        
        print("\n" + "=" * 60)
    
    def prompt_confirm_download(self) -> bool:
        """
        确认开始下载
        
        返回值:
            True 确认下载，False 返回修改
        """
        while True:
            choice = input("\n按 Enter 开始下载，输入 'q' 返回修改: ").strip().lower()
            
            if choice == '':
                return True
            elif choice == 'q':
                return False
            else:
                print("❌ 无效选择\n")
    
    def prompt_modify_parameters(self) -> str:
        """
        询问用户要修改哪个参数
        
        返回值:
            参数代号 ('1'-'7' 表示要修改的参数) 或 'q' 返回
        """
        print("\n修改参数 (按数字选择):")
        print("  1. 视频链接")
        print("  2. 录制模式")
        print("  3. 保存字幕")
        print("  4. 显示画面")
        print("  5. 开启声音")
        print("  6. 开启缓存")
        print("  7. 视频文件名")
        print("  q. 确认并下载\n")
        
        return input("请选择 (1-7 或 q): ").strip().lower()
    
    def run_interactive(self):
        """
        运行交互式界面
        
        返回值:
            True 如果用户成功完成了设置，False 如果用户中止
        """
        # 收集参数
        if not self.prompt_url():
            print("用户中止")
            return False
        
        if not self.prompt_mode():
            return self.run_interactive()  # 重新开始
        
        if not self.prompt_subtitle():
            return self.run_interactive()
        
        # 如果保存字幕，询问字幕文件名
        if self.save_subtitle:
            if not self.prompt_subtitle_filename():
                return False
        
        if not self.prompt_display_video():
            return self.run_interactive()
        
        if not self.prompt_enable_audio():
            return self.run_interactive()
        
        if not self.prompt_enable_cache():
            return self.run_interactive()
        
        if not self.prompt_output_filename():
            return self.run_interactive()
        
        # 循环显示确认和修改界面
        while True:
            self.show_confirmation()
            
            if self.prompt_confirm_download():
                return True
            
            # 返回修改参数
            while True:
                choice = self.prompt_modify_parameters()
                
                if choice == '1':
                    if not self.prompt_url():
                        continue
                    break
                elif choice == '2':
                    if not self.prompt_mode():
                        continue
                    break
                elif choice == '3':
                    if not self.prompt_subtitle():
                        continue
                    # 重新询问字幕文件名
                    if self.save_subtitle:
                        if not self.prompt_subtitle_filename():
                            continue
                    break
                elif choice == '4':
                    if not self.prompt_display_video():
                        continue
                    break
                elif choice == '5':
                    if not self.prompt_enable_audio():
                        continue
                    break
                elif choice == '6':
                    if not self.prompt_enable_cache():
                        continue
                    break
                elif choice == '7':
                    if not self.prompt_output_filename():
                        continue
                    break
                elif choice == 'q':
                    return True
                else:
                    print("❌ 无效选择\n")
                    continue


def main():
    """主函数"""
    try:
        # 创建 UI
        ui = DownloadUI()
        
        # 运行交互式界面
        if not ui.run_interactive():
            print("\n⚠️  操作已取消")
            return 1
        
        # 开始下载
        print("\n" + "=" * 60)
        print("开始下载...")
        print("=" * 60 + "\n")
        
        success = download_video(
            url=ui.url,
            mode=ui.mode,
            save_subtitle=ui.save_subtitle,
            display_video=ui.display_video,
            enable_audio=ui.enable_audio,
            enable_cache=ui.enable_cache,
            output_filename=ui.output_filename,
            subtitle_filename=ui.subtitle_filename if ui.save_subtitle else None
        )
        
        if success:
            print("\n✅ 所有操作完成!")
            return 0
        else:
            print("\n❌ 下载失败")
            return 1
    
    except MPVNotFoundError as e:
        print(f"❌ {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        return 1
    except Exception as e:
        print(f"❌ 发生意外错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
