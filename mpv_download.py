#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mpv 视频下载模块

核心下载功能，支持两种使用方式：
1. 作为模块被 main.py 调用，提供函数接口
2. 作为独立脚本运行，支持命令行一键下载

典型用法:
    - 作为模块: from mpv_download import download_video
    - 作为脚本: python mpv_download.py https://example.com/video.mp4
"""

import os
import sys
import subprocess
import shutil
import hashlib
import re
import time
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse, parse_qs
import argparse


class MPVNotFoundError(Exception):
    """找不到 mpv 可执行文件时抛出"""
    pass


class InvalidURLError(Exception):
    """无效 URL 时抛出"""
    pass


class DownloadFailedError(Exception):
    """下载失败时抛出"""
    pass


class MPVPathFinder:
    """
    查找本机安装的 mpv.exe
    
    mpv 查找优先级:
        1. 当前工作目录下的 mpv.exe
        2. 脚本所在目录下的 mpv.exe
        3. 系统 PATH 环境变量中的 mpv.exe
    """
    
    def __init__(self):
        """初始化 MPVPathFinder，自动查找 mpv.exe 路径"""
        self._mpv_path = self._find_mpv()
    
    def _find_mpv(self) -> str:
        """
        查找 mpv.exe 的完整路径
        
        返回值:
            mpv.exe 的完整路径
        
        异常:
            MPVNotFoundError: 如果找不到 mpv
        """
        # 第一优先级：当前工作目录
        cwd_mpv = os.path.join(os.getcwd(), "mpv.exe")
        if os.path.isfile(cwd_mpv):
            return cwd_mpv
        
        # 第二优先级：脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_mpv = os.path.join(script_dir, "mpv.exe")
        if os.path.isfile(script_mpv):
            return script_mpv
        
        # 第三优先级：系统 PATH
        mpv_path = shutil.which("mpv.exe") or shutil.which("mpv")
        if mpv_path:
            return mpv_path
        
        # 未找到 mpv
        raise MPVNotFoundError(
            "找不到 mpv 可执行文件。请确保:\n"
            "  1. mpv.exe 存在于当前目录\n"
            "  2. mpv.exe 存在于脚本目录\n"
            "  3. mpv 已添加到系统 PATH 环境变量\n"
            "  4. 已正确安装 mpv"
        )
    
    def get_mpv_path(self) -> str:
        """
        获取 mpv.exe 的完整路径
        
        返回值:
            mpv.exe 的完整路径
        """
        return self._mpv_path
    
    def is_mpv_available(self) -> bool:
        """
        检查 mpv 是否可用
        
        返回值:
            True 如果 mpv 可用，False 否则
        """
        try:
            self._find_mpv()
            return True
        except MPVNotFoundError:
            return False


class FileNameManager:
    """
    处理文件名的获取、验证、清理和去重
    
    功能:
        - 自动从 URL 或用户输入获取文件名
        - 处理后缀名（优先级处理）
        - 清理非法字符
        - 处理文件名重复
    """
    
    # 无效的文件名词根 - 如果去掉后缀后是这些词，则使用 MD5
    INVALID_STEMS = {
        "original",
        "index",
        "video",
        "stream",
        "play",
        "download",
        "file",
        "media",
        "content",
        "data",
        "temp",
        "tmp",
        "untitled",
        "unnamed",
        "noname",
    }
    
    # 默认后缀名
    DEFAULT_VIDEO_EXT = ".mkv"
    DEFAULT_SUBTITLE_EXT = ".srt"
    
    def __init__(self, mpv_path: str):
        """
        初始化文件名管理器
        
        参数:
            mpv_path: mpv 可执行文件路径，用于查询视频信息
        """
        self.mpv_path = mpv_path
    
    def get_video_filename(self, url: str, custom_name: str = None) -> str:
        """
        自动获取视频文件名（包含后缀）
        
        参数:
            url: 视频链接
            custom_name: 用户自定义视频文件名（可含可不含后缀）
        
        返回值:
            完整的视频文件名（含后缀）
        
        优先级:
            1. 用户自定义名 - 检查是否含后缀，处理后缀逻辑
            2. 从 URL 查询视频源信息获取的文件名
            3. 从 URL 直接提取的文件名
            4. URL 的 MD5 哈希值前 8 位 + 默认后缀
        """
        # 第一优先级：用户自定义名
        if custom_name:
            return self._get_video_filename_with_extension(custom_name, url)
        
        # 第二优先级：从 URL 查询视频源信息（先保留接口，暂时跳过实现）
        # filename = self._query_filename_from_source(url)
        # if filename and self._is_valid_filename(filename):
        #     return self._get_video_filename_with_extension(filename, url)
        
        # 第三优先级：从 URL 直接提取
        filename = self._extract_filename_from_url(url)
        if filename and self._is_valid_filename(filename):
            return self._get_video_filename_with_extension(filename, url)
        
        # 第四优先级：使用 MD5 + URL 提取的后缀（或默认后缀）
        md5_name = self._md5_url(url)
        url_ext = self._get_extension_from_url(url)
        if url_ext:
            filename = md5_name + url_ext
        else:
            filename = md5_name + self.DEFAULT_VIDEO_EXT
        return self._handle_filename_duplication(filename)
    
    def get_subtitle_filename(self, video_filename: str, custom_name: str = None) -> str:
        """
        处理字幕文件名，包含后缀名逻辑
        
        参数:
            video_filename: 已确定的视频输出文件名（含后缀）
            custom_name: 用户自定义字幕文件名（可含可不含后缀）
        
        返回值:
            完整的字幕文件名（含后缀）
        
        处理步骤:
            1. 如果未提供 custom_name，使用视频文件名替换后缀为 .srt
            2. 如果提供了 custom_name：
               a. 判断是否包含后缀
               b. 如果包含后缀 → 使用用户指定的后缀
               c. 如果不包含后缀 → 使用默认后缀 .srt
            3. 执行文件名清理和去重处理
            4. 返回最终的字幕文件名
        """
        if not custom_name:
            # 使用视频文件名，替换后缀
            base_name = os.path.splitext(video_filename)[0]
            subtitle_name = base_name + self.DEFAULT_SUBTITLE_EXT
        else:
            # 检查用户输入的后缀
            base_name, ext = self._get_file_extension(custom_name)
            if ext:
                # 用户提供了后缀，直接使用
                subtitle_name = custom_name
            else:
                # 用户未提供后缀，使用默认
                subtitle_name = custom_name + self.DEFAULT_SUBTITLE_EXT
        
        # 清理文件名并处理重复
        subtitle_name = self._clean_filename(subtitle_name)
        subtitle_name = self._handle_filename_duplication(subtitle_name)
        return subtitle_name
    
    def _query_filename_from_source(self, url: str) -> Optional[str]:
        """
        尝试从视频源查询文件名（调用 mpv 获取文件信息）
        
        参数:
            url: 视频链接
        
        返回值:
            文件名（包含后缀），如果查询失败返回 None
        
        注意:
            此方法当前为占位符，完整实现需要解析 mpv 的 JSON 输出
        """
        # TODO: 实现通过 mpv 查询文件信息的功能
        # 例如：mpv --dump-json=all --no-config <url>
        return None
    
    def _extract_filename_from_url(self, url: str) -> Optional[str]:
        """
        从 URL 提取文件名
        
        参数:
            url: 视频链接
        
        处理步骤:
            1. 获取 URL 最后一个 '/' 后的部分
            2. 移除查询参数 ('?' 及之后的内容)
            3. 移除 URL 编码
        
        返回值:
            提取出的文件名，如果无效返回 None
        """
        try:
            # 解析 URL
            parsed = urlparse(url)
            path = parsed.path
            
            # 获取最后一个 '/' 后的部分
            filename = path.split('/')[-1]
            
            # 移除查询参数
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # URL 解码（处理 %20 等情况）
            filename = unquote_url_filename(filename)
            
            if filename:
                return filename
            return None
        except Exception:
            return None
    
    def _is_valid_filename(self, name: str) -> bool:
        """
        判断文件名是否有效
        
        参数:
            name: 文件名（不含路径）
        
        检查项:
            1. 文件名不为空
            2. 去掉后缀的文件名不在 INVALID_STEMS 中
        
        返回值:
            True 如果有效，False 如果无效
        """
        if not name or not name.strip():
            return False
        
        # 获取文件名部分（去掉后缀）
        base_name, _ = self._get_file_extension(name)
        base_name = base_name.lower().strip()
        
        # 检查是否在无效词根列表中
        return base_name not in self.INVALID_STEMS
    
    def _clean_filename(self, filename: str) -> str:
        """
        清理文件名中的非法字符
        
        参数:
            filename: 原始文件名
        
        处理步骤:
            1. 分离文件名和后缀名
            2. 移除非法字符: \ / : * ? " < > |
            3. 移除首尾空格
            4. 替换连续空格为单个空格
            5. 重新组合文件名和后缀名
        
        返回值:
            清理后的文件名
        """
        # 分离文件名和后缀
        base_name, ext = self._get_file_extension(filename)
        
        # 定义非法字符集合
        illegal_chars = r'[\\/:*?"<>|]'
        
        # 移除非法字符
        base_name = re.sub(illegal_chars, '', base_name)
        
        # 移除首尾空格
        base_name = base_name.strip()
        
        # 替换连续空格为单个空格
        base_name = re.sub(r'\s+', ' ', base_name)
        
        # 重新组合
        return base_name + ext if base_name else f"video{ext}"
    
    def _get_file_extension(self, filename: str) -> Tuple[str, str]:
        """
        分离文件名和后缀名
        
        参数:
            filename: 完整文件名
        
        返回值:
            (文件名不含后缀, 后缀名含点)
            示例: "video.mkv" → ("video", ".mkv")
                  "no_ext" → ("no_ext", "")
        
        说明:
            用于提取文件名中的后缀，判断用户是否指定了后缀名
        """
        if '.' in filename:
            parts = filename.rsplit('.', 1)
            return parts[0], '.' + parts[1]
        return filename, ""
    
    def _handle_filename_duplication(self, filename: str) -> str:
        """
        处理文件名重复，自动加数字后缀
        
        参数:
            filename: 目标文件名
        
        处理步骤:
            1. 如果文件不存在，直接返回
            2. 如果文件存在，在后缀前添加 _2, _3 ... 直到找到不存在的文件名
        
        返回值:
            不重复的文件名
        """
        if not os.path.exists(filename):
            return filename
        
        # 分离文件名和后缀
        base_name, ext = self._get_file_extension(filename)
        
        # 添加数字后缀
        counter = 2
        while True:
            new_filename = f"{base_name}_{counter}{ext}"
            if not os.path.exists(new_filename):
                return new_filename
            counter += 1
    
    def _md5_url(self, url: str) -> str:
        """
        计算 URL 的 MD5 哈希值前 8 位
        
        参数:
            url: 视频链接
        
        返回值:
            MD5 哈希值的前 8 位字符
        """
        md5_hash = hashlib.md5(url.encode()).hexdigest()
        return md5_hash[:8]
    
    def _get_extension_from_url(self, url: str) -> str:
        """
        从 URL 提取视频文件的后缀名
        
        参数:
            url: 视频链接
        
        处理步骤:
            1. 获取 URL 最后一个 '/' 后的部分
            2. 移除查询参数 ('?' 及之后的内容)
            3. 提取文件后缀名（含点）
            4. 如果无法提取，返回空字符串
        
        返回值:
            提取出的后缀名（含点），如 .mp4, .mkv, .flv
            无法提取返回 ""
        
        示例:
            URL: "https://example.com/video.mp4?key=value" → ".mp4"
            URL: "https://example.com/stream" → ""
            URL: "https://example.com/show.mkv" → ".mkv"
        """
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # 获取最后一个 '/' 后的部分
            filename = path.split('/')[-1]
            
            # 移除查询参数
            if '?' in filename:
                filename = filename.split('?')[0]
            
            # 提取后缀
            if '.' in filename:
                ext = filename.rsplit('.', 1)[1]
                return '.' + ext if ext else ""
            return ""
        except Exception:
            return ""
    
    def _get_video_filename_with_extension(self, base_filename: str, url: str) -> str:
        """
        处理视频文件名，包含后缀名逻辑（3 级优先级）
        
        参数:
            base_filename: 基础文件名（不含后缀）或含后缀 - 来自自动获取或用户输入
            url: 视频链接 - 用于提取后缀作为备选
        
        返回值:
            完整的视频文件名（含后缀）
        
        后缀处理优先级:
            1. 用户指定了后缀 (base_filename 中包含后缀)
               → 使用用户指定的后缀
               
            2. 用户未指定后缀，尝试从 URL 提取
               → 如果 URL 中有后缀 (如 .mp4, .mkv) → 使用该后缀
               
            3. 都无法获取
               → 使用默认后缀 .mkv
        
        处理步骤:
            a. 检查 base_filename 是否包含后缀
            b. 如果 base_filename 不包含后缀，从 URL 提取后缀
            c. 如果 URL 也无后缀，使用默认后缀
            d. 执行文件名清理和去重处理
            e. 返回最终的视频文件名
        """
        # 检查用户是否提供了后缀
        base_name, ext = self._get_file_extension(base_filename)
        
        if ext:
            # 用户提供了后缀，直接使用
            filename = base_filename
        else:
            # 用户未提供后缀，尝试从 URL 提取
            url_ext = self._get_extension_from_url(url)
            if url_ext:
                filename = base_filename + url_ext
            else:
                # 使用默认后缀
                filename = base_filename + self.DEFAULT_VIDEO_EXT
        
        # 清理文件名并处理重复
        filename = self._clean_filename(filename)
        filename = self._handle_filename_duplication(filename)
        return filename


class DownloadConfig:
    """
    存储和管理下载配置参数
    """
    
    def __init__(self, url: str, **kwargs):
        """
        初始化下载配置
        
        参数:
            url: 视频链接（必需）
            **kwargs: 其他可选参数
        """
        self.url = url
        self.mode = kwargs.get('mode', 'stream-dump')
        self.save_subtitle = kwargs.get('save_subtitle', False)
        self.subtitle_filename = kwargs.get('subtitle_filename', None)
        self.display_video = kwargs.get('display_video', False)
        self.enable_audio = kwargs.get('enable_audio', False)
        self.enable_cache = kwargs.get('enable_cache', True)
        self.output_filename = kwargs.get('output_filename', None)
        self.custom_mpv_args = kwargs.get('custom_mpv_args', {})
    
    def to_mpv_args(self) -> list:
        """
        转换为 mpv 命令行参数列表
        
        返回值:
            mpv 命令行参数列表
        
        生成的参数:
            - --no-config (总是启用)
            - --stream-record 或 --stream-dump (根据 mode)
            - --sub-file=<字幕文件名> (如果 save_subtitle=True)
            - --vo=null (如果 display_video=False)
            - --ao=null (如果 enable_audio=False)
            - --cache (如果 enable_cache=True)
            - --no-resume-playback (总是启用，避免播放中断)
            - 其他自定义参数
        """
        args = []
        
        # 不使用配置文件
        args.append('--no-config')
        
        # 禁用播放进度记忆，避免播放中断
        args.append('--no-resume-playback')
        
        # 录制模式
        if self.mode == 'stream-record':
            args.append(f'--stream-record={self.output_filename}')
        else:
            args.append(f'--stream-dump={self.output_filename}')
        
        # 字幕处理
        if self.save_subtitle and self.subtitle_filename:
            args.append(f'--sub-file={self.subtitle_filename}')
        
        # 显示画面
        if not self.display_video:
            args.append('--vo=null')
        
        # 声音处理
        if not self.enable_audio:
            args.append('--ao=null')
        
        # 缓存
        if self.enable_cache:
            args.append('--cache')
        
        # 自定义参数
        for key, value in self.custom_mpv_args.items():
            if value is True:
                args.append(f'--{key}')
            elif value is not False and value is not None:
                args.append(f'--{key}={value}')
        
        return args
    
    def validate(self) -> bool:
        """
        验证配置是否有效
        
        检查项:
            1. URL 不为空且格式有效
            2. mode 为有效值
            3. output_filename 不能为空（会由 download() 方法自动生成）
        
        返回值:
            True 如果有效，False 否则
        """
        if not self.url or not self.url.strip():
            return False
        
        if self.mode not in ['stream-record', 'stream-dump']:
            return False
        
        # output_filename 会在 download() 中自动生成，这里只检查 URL
        return True
    
    def get_mpv_args_display(self) -> str:
        """
        获取 mpv 参数的详细显示文本
        
        返回值:
            格式化的参数列表文本
        """
        args = self.to_mpv_args()
        return "\n  ".join(args)


class VideoDownloader:
    """
    执行 mpv 进程，管理下载过程
    """
    
    def __init__(self, mpv_path: str, file_name_manager: FileNameManager):
        """
        初始化下载器
        
        参数:
            mpv_path: mpv 可执行文件路径
            file_name_manager: 文件名管理器实例
        """
        self.mpv_path = mpv_path
        self.file_name_manager = file_name_manager
    
    def download(self, config: DownloadConfig) -> bool:
        """
        执行下载
        
        参数:
            config: DownloadConfig 对象
        
        返回值:
            True 下载成功，False 下载失败
        
        处理步骤:
            1. 验证配置有效性
            2. 获取输出文件名
            3. 构建 mpv 命令行
            4. 执行 mpv 进程
            5. 实时显示 mpv 的输出（下载进度、警告等）
            6. 等待进程完成并返回状态
        """
        # 验证配置
        if not config.validate():
            print("❌ 配置无效，请检查参数")
            print("\n📋 当前 mpv 参数:")
            print(f"  {config.get_mpv_args_display()}")
            return False
        
        # 获取输出文件名
        output_filename = self.file_name_manager.get_video_filename(
            config.url, config.output_filename
        )
        config.output_filename = output_filename
        
        # 处理字幕文件名
        if config.save_subtitle:
            subtitle_filename = self.file_name_manager.get_subtitle_filename(
                output_filename, config.subtitle_filename
            )
            config.subtitle_filename = subtitle_filename
        
        print(f"\n📥 开始下载: {output_filename}")
        if config.save_subtitle:
            print(f"📝 字幕文件: {config.subtitle_filename}")
        
        # 构建和执行命令
        cmd = self._build_mpv_command(config)
        return self._execute_mpv(cmd)
    
    def _build_mpv_command(self, config: DownloadConfig) -> list:
        """
        构建 mpv 命令行
        
        参数:
            config: DownloadConfig 对象
        
        返回值:
            完整的命令行列表
        
        示例:
            ["mpv.exe", "--no-config", "--stream-dump=output.mkv", 
             "--vo=null", "--ao=null", "--cache", "https://example.com/video.mp4"]
        """
        cmd = [self.mpv_path]
        cmd.extend(config.to_mpv_args())
        # 视频地址用引号包裹
        cmd.append(config.url)
        return cmd
    
    def get_full_command_display(self, config: DownloadConfig) -> str:
        """
        获取完整的 mpv 命令行字符串（用于显示给用户）
        
        参数:
            config: DownloadConfig 对象
        
        返回值:
            格式化的完整命令行字符串
        
        示例:
            mpv.exe --no-config --no-resume-playback --stream-dump=output.mkv \\
            --vo=null --ao=null --cache "https://example.com/video.mp4"
        """
        cmd = self._build_mpv_command(config)
        # 第一行显示 mpv 和参数，URL 用引号包裹并单独显示
        cmd_str = cmd[0] + " " + " ".join(cmd[1:-1])
        url_str = f'"{cmd[-1]}"'
        return f"{cmd_str} \\\n    {url_str}"
    
    def _execute_mpv(self, cmd: list) -> bool:
        """
        执行 mpv 进程
        
        参数:
            cmd: 完整的命令行列表
        
        处理:
            1. 启动子进程
            2. 实时读取和显示 stdout/stderr
            3. 处理用户中断 (Ctrl+C)
            4. 等待进程完成
        
        返回值:
            True 进程成功完成，False 进程失败或被中断
        """
        try:
            print(f"🎬 执行命令: {' '.join(cmd)}\n")
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 实时显示输出
            self._display_mpv_output(process)
            
            # 等待进程完成
            return_code = process.wait()
            
            if return_code == 0:
                print("\n✅ 下载完成！")
                return True
            else:
                print(f"\n❌ mpv 进程失败，返回码: {return_code}")
                return False
        
        except KeyboardInterrupt:
            print("\n⚠️  用户中断下载")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            return False
        except Exception as e:
            print(f"❌ 执行 mpv 出错: {e}")
            return False
    
    def _display_mpv_output(self, process):
        """
        实时显示 mpv 的输出信息
        
        参数:
            process: subprocess.Popen 实例
        
        显示内容:
            - 下载进度百分比
            - 文件大小
            - 下载速度
            - 警告信息
            - 错误信息
        
        刷新频率:
            约每 1 秒刷新一次
        """
        if process.stdout:
            last_flush = time.time()
            for line in process.stdout:
                line = line.strip()
                if line:
                    print(line)
                    # 每 1 秒刷新一次输出
                    current_time = time.time()
                    if current_time - last_flush >= 1.0:
                        sys.stdout.flush()
                        last_flush = current_time
            # 最后确保所有输出都刷新
            sys.stdout.flush()


def download_video(
    url: str,
    mode: str = "stream-dump",
    save_subtitle: bool = False,
    display_video: bool = False,
    enable_audio: bool = False,
    enable_cache: bool = True,
    output_filename: str = None,
    subtitle_filename: str = None,
    **custom_mpv_args
) -> bool:
    """
    下载视频的主要接口函数
    
    参数:
        url: 视频链接（必需）
        mode: 录制模式，默认 "stream-dump"
        save_subtitle: 是否保存字幕，默认 False
        display_video: 是否显示画面，默认 False
        enable_audio: 是否开启声音，默认 False
        enable_cache: 是否开启缓存，默认 True
        output_filename: 自定义输出视频文件名（不含后缀）
        subtitle_filename: 自定义字幕文件名（不含后缀，当 save_subtitle=True 时使用）
        **custom_mpv_args: 其他自定义 mpv 参数
    
    返回值:
        True 下载成功，False 下载失败
    
    异常:
        MPVNotFoundError: 找不到 mpv
        ValueError: 无效的 URL 或配置
    
    典型用法:
        # 简单下载
        download_video("https://example.com/video.mp4")
        
        # 带参数的下载
        download_video(
            "https://example.com/video.mp4",
            mode="stream-record",
            display_video=True,
            save_subtitle=True,
            output_filename="my_video"
        )
    """
    try:
        # 初始化 mpv 查找器
        mpv_finder = MPVPathFinder()
        mpv_path = mpv_finder.get_mpv_path()
        
        # 初始化文件名管理器
        file_name_manager = FileNameManager(mpv_path)
        
        # 创建下载配置
        config = DownloadConfig(
            url=url,
            mode=mode,
            save_subtitle=save_subtitle,
            subtitle_filename=subtitle_filename,
            display_video=display_video,
            enable_audio=enable_audio,
            enable_cache=enable_cache,
            output_filename=output_filename,
            custom_mpv_args=custom_mpv_args
        )
        
        # 创建下载器并执行
        downloader = VideoDownloader(mpv_path, file_name_manager)
        return downloader.download(config)
    
    except MPVNotFoundError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False


def unquote_url_filename(filename: str) -> str:
    """
    简单的 URL 解码（处理常见的 URL 编码）
    
    参数:
        filename: URL 编码的文件名
    
    返回值:
        解码后的文件名
    """
    # 处理常见的 URL 编码
    filename = filename.replace('%20', ' ')
    filename = filename.replace('%2F', '/')
    filename = filename.replace('%3A', ':')
    return filename


if __name__ == "__main__":
    # 命令行使用
    parser = argparse.ArgumentParser(
        description="使用 mpv 下载视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础下载（使用所有默认值）
  python mpv_download.py https://example.com/video.mp4
  
  # 使用 stream-record 模式，显示画面和声音
  python mpv_download.py https://example.com/video.mp4 --mode stream-record --display --audio
  
  # 保存字幕，自定义文件名
  python mpv_download.py https://example.com/video.mp4 --output my_video --save-subtitle --subtitle-file my_subs
        """
    )
    
    parser.add_argument("url", help="视频链接")
    parser.add_argument(
        "--mode",
        default="stream-dump",
        choices=["stream-record", "stream-dump"],
        help="录制模式，默认 stream-dump"
    )
    parser.add_argument(
        "--output",
        help="输出视频文件名（不含后缀）"
    )
    parser.add_argument(
        "--save-subtitle",
        action="store_true",
        help="是否保存字幕"
    )
    parser.add_argument(
        "--subtitle-file",
        help="字幕文件名（当 --save-subtitle 时使用）"
    )
    parser.add_argument(
        "--display",
        action="store_true",
        help="显示画面"
    )
    parser.add_argument(
        "--audio",
        action="store_true",
        help="开启声音"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="关闭缓存"
    )
    
    args = parser.parse_args()
    
    # 执行下载
    success = download_video(
        url=args.url,
        mode=args.mode,
        save_subtitle=args.save_subtitle,
        display_video=args.display,
        enable_audio=args.audio,
        enable_cache=not args.no_cache,
        output_filename=args.output,
        subtitle_filename=args.subtitle_file
    )
    
    sys.exit(0 if success else 1)
