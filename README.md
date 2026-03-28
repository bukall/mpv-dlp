# mpv-dlp - 基于 mpv 的视频流下载工具

一个轻量级的 Python 工具，通过调用 mpv 播放器来保存受限视频资源。支持交互式向导和命令行两种使用方式，提供完整的 Python API 供二次开发。

## ⚠️ 免责声明

**本项目 100% 使用 AI 编写，如出现任何问题与本人无关。**

本项目仅供学习研究使用。用户需自行承担使用本工具所产生的一切后果。

## 📌 项目说明

### 适用场景

本项目初衷是用来下载**部分只允许在线播放而不允许下载的视频资源**，例如：
- 大多数 Emby 服务器上的视频
- 一些无法使用标准下载器但可以使用 mpv 播放器播放的视频

> **重要提示**：如果你要下载的资源允许使用标准下载器下载，那完全**没必要使用本项目**。

### 工作原理

本项目通过以下方式工作：
1. 调用系统中的 mpv 播放器来流式读取视频
2. 在播放过程中使用 `--stream-dump` 或 `--stream-record` 参数将流数据保存为文件
3. 在服务器眼里，你只是在使用外部的 mpv 播放器播放视频

**安全性考虑**：理论上无直接封号风险，但长时间连续下载可能被通过各种特征识别。建议：
- 合理控制下载频率
- 自行进行限速或间隔下载

### 获取直链

如何获取视频直链不在本项目范围内，可参考以下方式：

#### 方式 1：使用 Fiddler 抓包
- 使用 Fiddler 抓包分析网络请求
- 找到视频流的真实地址

#### 方式 2：使用 Process Explorer 查看参数
- 调用外部 mpv 播放器后使用 Process Explorer 查看调用参数

#### 方式 3：使用 show_args.exe（新增）
1. **下载预编译版本**：从项目的 GitHub Releases 页面下载打包好的 `show_args.exe`
2. **或者自行编译**：运行 `python build_show_args_exe.py` 自行打包（需要 `pip install pyinstaller`）
3. **配置外部播放器**：在播放器设置中将外部播放器路径设置为 `show_args.exe`
4. **获取直链**：在要获取直链的视频界面点击"外部播放器"按钮，程序会将所有参数记录到 `show_args.log` 文件中
5. **查看直链**：在 `show_args.log` 文件中找到完整的命令行，从中提取视频直链

**注意**：`show_args.exe` 会在显示参数后保持运行，按 Ctrl+C 退出。日志文件会保存在与 `show_args.exe` 相同的目录中。

## 🔧 环境要求

- **Python 版本**: 理论支持3.11+ (推荐 3.14)
- **mpv 播放器**: mpv 播放器已安装并添加到 PATH，或放在脚本同目录（[mpv下载链接](https://mpv.io/installation/)）
- **操作系统**: Windows（其他系统需要自行修改查找调用mpv部分适配）

## 📖 使用方法

### 方法 1: 交互式向导（推荐新手）

运行主程序，按提示操作：

```bash
python main.py
```

操作流程：
1. 输入视频链接（必需）
2. 选择录制模式（默认：stream-dump）
3. 配置其他参数（一般直接回车使用默认值）
4. 确认配置后开始下载

**快速下载**：输完链接后一路回车即可！

### 方法 2: 命令行调用（最简洁）

最少只需提供一个 URL：

```bash
# 最简单的方式（使用所有默认值）
python mpv_download.py "https://example.com/video.mp4"

# 自定义输出文件名
python mpv_download.py "https://example.com/video.mp4" --output my_video

# 使用 stream-record 模式，显示画面和声音
python mpv_download.py "https://example.com/video.mp4" --mode stream-record --display --audio

# 保存字幕
python mpv_download.py "https://example.com/video.mp4" --save-subtitle --subtitle-file my_subs

# 查看所有选项
python mpv_download.py --help
```

**命令行参数说明**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `url` | 视频链接（必需） | - |
| `--mode` | 录制模式：`stream-dump` 或 `stream-record` | stream-dump |
| `--output` | 输出文件名（不含后缀） | 自动从 URL 提取 |
| `--save-subtitle` | 是否保存字幕 | 否 |
| `--subtitle-file` | 字幕文件名 | 自动生成 |
| `--display` | 显示播放窗口 | 否 |
| `--audio` | 开启声音 | 否 |
| `--no-cache` | 关闭缓存 | 否（默认开启） |

### 方法 3: Python API（最灵活）

在自己的 Python 程序中导入并使用：

```python
from mpv_download import download_video

# 简单下载
success = download_video("https://example.com/video.mp4")

# 自定义参数下载
success = download_video(
    url="https://example.com/video.mp4",
    mode="stream-dump",              # 录制模式
    save_subtitle=True,              # 保存字幕
    subtitle_filename="my_subs",     # 字幕文件名
    display_video=False,             # 不显示画面
    enable_audio=False,              # 不开启声音
    enable_cache=True,               # 开启缓存
    output_filename="my_video"       # 输出文件名
)

if success:
    print("✅ 下载成功！")
else:
    print("❌ 下载失败")
```

### 字幕下载 API（新增）

`download_subtitles()` 函数用于下载多个外挂字幕文件，自动生成 MPV 能识别的字幕文件名：

```python
from mpv_download import download_subtitles

# 下载字幕列表
subtitle_urls = [
    "https://example.com/subtitle1.srt",
    "https://example.com/subtitle2.srt",
    "https://example.com/subtitle3.srt"
]

success = download_subtitles(subtitle_urls, "video.mkv")

if success:
    print("✅ 所有字幕下载成功！")
else:
    print("⚠️ 部分字幕下载失败")
```

**字幕文件命名规则**（MPV 自动读取）：
- 第一个字幕：`video.srt`（主字幕）
- 第二个字幕：`video.1.srt`（辅助字幕1）
- 第三个字幕：`video.2.srt`（辅助字幕2）
- 以此类推...

**参数说明**：
| 参数 | 说明 |
|------|------|
| `subtitle_urls` | 字幕 URL 列表，必须是列表类型 |
| `video_filename` | 视频文件名（含后缀），用于确定字幕保存位置和名称 |

**返回值**：
- `True` - 所有字幕下载成功
- `False` - 部分或全部字幕下载失败

## 📋 录制模式说明

### stream-dump（推荐用于完整视频）

```
--stream-dump=output.mkv
```

- **原理**：原始传输层数据包直接保存
- **特点**：保留完整传输协议信息
- **优势**：完整下载所有音轨和字幕
- **不推荐用于**：直播流

### stream-record（推荐用于直播）

```
--stream-record=output.mkv
```

- **原理**：在播放过程中实时转封装原始流数据
- **特点**：保持原始编码格式，不进行重编码
- **优势**：零质量损失，低系统资源占用
- **限制**：只录制一个音轨和一个字幕轨道
- **不推荐用于**：完整视频下载

## 🎯 核心特性

✅ **三种使用方式** - 满足不同用户需求  
✅ **智能文件名处理** - 自动清理非法字符，处理重复  
✅ **灵活的后缀处理** - 用户指定 → URL 提取 → 默认值  
✅ **完整的 API** - 易于集成和二次开发  
✅ **详细的中文注释** - 代码易于理解和修改  
✅ **实时显示进度** - 看到下载的实时输出  

## 📁 项目结构

```
mpv-dlp/
├── main.py                      # 交互式主程序
├── mpv_download.py             # 核心下载模块
├── extract_links_and_titles.py  # 从日志提取视频信息脚本
├── extract_from_args.py         # 从参数提取视频信息脚本
├── batch_download_videos.py     # 批量下载视频及字幕脚本
├── show_args.py                 # 参数显示工具
├── DESIGN_MAIN.md              # main.py 设计文档
├── DESIGN_MPV_DOWNLOAD.md      # mpv_download.py 设计文档
└── README.md                    # 本文件
```

## 📥 批量下载工具

### 1. extract_links_and_titles.py - 从日志提取视频信息

**用途**：从 `show_args.log` 日志文件中提取视频直链、标题和外挂字幕，输出为 CSV 格式

**适用场景**：
- 使用 show_args.exe 作为外部播放器记录了多个视频信息
- 需要批量处理已记录的视频链接
- 想从日志中提取完整的视频和字幕信息

**使用方法**：

```bash
python extract_links_and_titles.py
```

**输出格式**：
- 生成 `videos_from_log.csv` 文件
- 三列数据：视频链接、视频标题、字幕URL列表
- 示例：
  ```csv
  https://example.com/video1.mkv,我的视频1,"['https://example.com/sub1.srt', 'https://example.com/sub2.srt']"
  https://example.com/video2.mkv,我的视频2,"[]"
  ```

### 2. extract_from_args.py - 从参数直接提取视频信息

**用途**：直接从 mpv 的命令行参数中提取视频直链、标题和外挂字幕，输出为 CSV 格式

**适用场景**：
- 已获得完整的 mpv 调用参数字符串
- 需要快速从参数中提取视频信息
- 与播放器的直链获取流程集成

**使用方法**：

作为模块调用（自动处理 mpv 参数）：

```bash
# 直接在 mpv 参数中调用
mpv [参数...] --external-file=extract_from_args.py
```

或手动运行（从日志中复制的参数）：

```bash
python extract_from_args.py
```

**输出格式**：
- 生成 `videos_from_args.csv` 文件（追加模式）
- 三列数据：视频链接、视频标题、字幕URL列表
- 与 `extract_links_and_titles.py` 相同的 CSV 格式

### 3. batch_download_videos.py - 批量下载视频及字幕

**用途**：从 CSV 文件批量下载视频和外挂字幕，自动处理多字幕的命名和下载

**适用场景**：
- 需要批量下载多个视频
- 需要同时下载视频和外挂字幕
- 只需下载字幕而不下载视频

**使用方法**：

```bash
# 方式1：直接运行（然后输入CSV文件路径）
python batch_download_videos.py

# 方式2：指定 CSV 文件路径 (其余参数自动默认)
python batch_download_videos.py videos_from_args.csv
```

**交互流程**：

1. **加载 CSV 文件**
   ```
   请输入 CSV 文件路径 (默认: videos_from_args.csv): 
   ```

2. **确认下载列表**
   ```
   📋 将要下载 3 个视频:
   1. 文件名: 我的视频1
      URL: https://example.com/video1.mkv...
      📝 字幕: 2 个
   ...
   确认开始下载? (Y/n): 
   ```

3. **选择下载模式** ✨ **新增**
   ```
   📋 选择下载模式:
   只下载字幕? (y/N): 
   ```
   - 输入 `y` → 仅下载字幕（跳过视频下载）
   - 输入 `n` 或回车 → 下载视频和字幕（默认）

4. **开始批量下载**
   ```
   📥 [1/3] 正在下载: 我的视频1
   ✅ [1/3] 视频下载完成: 我的视频1
   📝 [1/3] 正在下载 2 个字幕...
   ✅ 字幕 1 下载完成
   ✅ 字幕 2 下载完成
   
   ⏳ 等待 5 秒后下载下一个视频...
   ```

**CSV 文件格式**：

| 列 | 名称 | 说明 | 必需 |
|----|------|------|------|
| 1 | 视频链接 | 视频的完整 URL | ✅ |
| 2 | 视频标题 | 作为输出文件名（自动打包后缀） | ✅ |
| 3 | 字幕列表 | Python 列表格式：`['url1', 'url2']` | ❌ 可选 |

**示例 CSV 内容**：
```csv
https://media.example.com/videos/123/original.mkv?token=abc,刀剑神域S1E1,"['https://sub.example.com/123_zh.srt', 'https://sub.example.com/123_en.srt']"
https://media.example.com/videos/124/original.mkv?token=def,刀剑神域S1E2,"['https://sub.example.com/124_zh.srt']"
https://media.example.com/videos/125/original.mkv?token=ghi,刀剑神域S1E3,"[]"
```

**字幕下载规则**：

- 字幕自动保存与视频同目录
- 第 1 个字幕：`video.srt`
- 第 2 个字幕：`video.1.srt`
- 第 3 个字幕：`video.2.srt`
- MPV 会自动识别并加载所有字幕

**中断处理**：

按 `Ctrl+C` 可以随时中断下载，程序会：
- 清理部分下载的文件
- 显示中断消息
- 优雅退出

**工作流示例**：

```bash
# 步骤1：使用 show_args.exe 获取视频参数
# （在播放器设置中配置外部播放器）

# 步骤2：提取视频信息
python extract_links_and_titles.py
# 输出：videos_from_log.csv

# 步骤3：编辑 CSV（如果需要）
# 可选：删除不需要下载的行，修改文件名等

# 步骤4：批量下载
python batch_download_videos.py videos_from_log.csv
```

## 🔧 进阶用法

### 限速下载

为了避免被服务器识别为机器人，可使用 mpv 的限速参数：

```python
from mpv_download import download_video

download_video(
    "https://example.com/video.mp4",
    **{"stream-http-max-buffer-size": "50M"}  # 限制缓冲区大小
)
```

### 一键下载剧集

编写脚本批量下载：

```python
from mpv_download import download_video

episodes = [
    ("https://example.com/ep01.mp4", "episode_01"),
    ("https://example.com/ep02.mp4", "episode_02"),
    # ...
]

for url, name in episodes:
    print(f"正在下载: {name}")
    download_video(url, output_filename=name)
```

## 📝 异常处理

模块提供了明确的异常类供你捕获：

```python
from mpv_download import (
    download_video,
    MPVNotFoundError,
    InvalidURLError,
    DownloadFailedError
)

try:
    download_video("https://example.com/video.mp4")
except MPVNotFoundError:
    print("未找到 mpv，请确保已安装")
except InvalidURLError:
    print("无效的 URL")
except Exception as e:
    print(f"下载失败: {e}")
```

## 🤝 二次开发

欢迎对本项目进行二次开发！API 已清晰分离，便于集成和扩展：

### 核心模块说明

#### 1. `download_video()` - 视频下载的主要接口

**功能**：下载单个视频，支持自定义参数

```python
from mpv_download import download_video

# 基础用法
success = download_video("https://example.com/video.mp4")

# 完整参数示例
success = download_video(
    url="https://example.com/video.mp4",
    mode="stream-dump",              # 录制模式
    output_filename="my_video",      # 输出文件名
    save_subtitle=False,             # 是否保存字幕
    display_video=False,             # 是否显示画面
    enable_audio=False,              # 是否开启声音
    enable_cache=True,               # 是否开启缓存
    custom_arg1="value1"             # 自定义 mpv 参数
)
```

#### 2. `download_subtitles()` - 外挂字幕下载接口（新增）

**功能**：批量下载多个外挂字幕文件，自动处理文件命名

```python
from mpv_download import download_subtitles

# 下载字幕列表
subtitles = [
    "https://example.com/subtitles/chinese.srt",
    "https://example.com/subtitles/english.srt",
    "https://example.com/subtitles/japanese.srt"
]

success = download_subtitles(subtitles, "video_title.mkv")

if success:
    print("✅ 所有字幕已下载")
    # 输出文件：
    # - video_title.srt (中文，主字幕)
    # - video_title.1.srt (英文，辅助字幕1)
    # - video_title.2.srt (日文，辅助字幕2)
else:
    print("⚠️ 部分字幕下载失败")
```

**参数详解**：
- `subtitle_urls` (List[str]): 字幕 URL 列表
- `video_filename` (str): 视频文件名（含后缀）
- **返回值**: True 表示全部成功，False 表示部分失败

#### 3. `FileNameManager` - 文件名处理类

**功能**：智能处理文件名，包括后缀判断、非法字符清理、重复处理

```python
from mpv_download import FileNameManager, MPVPathFinder

# 初始化
mpv_finder = MPVPathFinder()
mpv_path = mpv_finder.get_mpv_path()
fnm = FileNameManager(mpv_path)

# 获取视频文件名（自动处理后缀）
video_name = fnm.get_video_filename(
    url="https://example.com/video.mp4?token=xyz",
    custom_name="My Video"  # 会输出 "My Video.mp4"
)

# 获取字幕文件名（自动与视频同名）
subtitle_name = fnm.get_subtitle_filename(
    video_filename="My Video.mp4",
    custom_name="custom"  # 会输出 "custom.srt"
)

# 输出
print(video_name)      # "My Video.mp4"
print(subtitle_name)   # "custom.srt"
```

#### 4. `DownloadConfig` - 下载配置类

**功能**：管理所有下载参数，统一配置管理

```python
from mpv_download import DownloadConfig

# 创建配置对象
config = DownloadConfig(
    url="https://example.com/video.mp4",
    mode="stream-dump",
    save_subtitle=False,
    display_video=False,
    enable_audio=False,
    enable_cache=True
)

# 验证配置
if config.validate():
    print("✅ 配置有效")
    # 获取 mpv 参数列表
    args = config.to_mpv_args()
    print(f"将使用以下参数: {args}")
else:
    print("❌ 配置无效")

# 获取格式化的参数显示
print(config.get_mpv_args_display())
```

#### 5. `VideoDownloader` - 下载执行类

**功能**：执行实际的下载过程，处理 mpv 进程

```python
from mpv_download import VideoDownloader, FileNameManager, DownloadConfig, MPVPathFinder

# 初始化
mpv_finder = MPVPathFinder()
mpv_path = mpv_finder.get_mpv_path()
file_name_manager = FileNameManager(mpv_path)
downloader = VideoDownloader(mpv_path, file_name_manager)

# 创建配置
config = DownloadConfig(
    url="https://example.com/video.mp4",
    output_filename="my_video"
)

# 执行下载
success = downloader.download(config)

if success:
    print("✅ 下载完成")
else:
    print("❌ 下载失败")
```

### 二次开发示例

#### 示例 1: 批量下载剧集

```python
from mpv_download import download_video, download_subtitles

episodes = [
    {
        "url": "https://example.com/ep01.mp4",
        "name": "Episode 01",
        "subtitles": ["https://example.com/ep01_zh.srt"]
    },
    {
        "url": "https://example.com/ep02.mp4",
        "name": "Episode 02",
        "subtitles": [
            "https://example.com/ep02_zh.srt",
            "https://example.com/ep02_en.srt"
        ]
    },
    # ... 更多集数
]

for i, ep in enumerate(episodes, 1):
    print(f"\n[{i}/{len(episodes)}] 下载中: {ep['name']}")
    
    # 下载视频
    if download_video(ep["url"], output_filename=ep["name"]):
        print(f"✅ 视频下载完成: {ep['name']}")
        
        # 下载字幕
        video_file = ep['name'] + '.mkv'
        if download_subtitles(ep['subtitles'], video_file):
            print(f"✅ 字幕下载完成")
        else:
            print(f"⚠️ 部分字幕下载失败")
    else:
        print(f"❌ 视频下载失败: {ep['name']}")
```

#### 示例 2: GUI 应用（PyQt 示例）

```python
from PyQt5.QtWidgets import QMainWindow, QPushButton
from mpv_download import download_video

class DownloadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_btn = QPushButton("开始下载")
        self.download_btn.clicked.connect(self.on_download)
        self.setCentralWidget(self.download_btn)
    
    def on_download(self):
        url = "https://example.com/video.mp4"
        self.download_btn.setEnabled(False)
        self.download_btn.setText("downloading...")
        
        success = download_video(url, output_filename="downloaded_video")
        
        if success:
            self.download_btn.setText("✅ 完成")
        else:
            self.download_btn.setText("❌ 失败")
        
        self.download_btn.setEnabled(True)
```

#### 示例 3: Web 服务（Flask 示例）

```python
from flask import Flask, request, jsonify
from mpv_download import download_video, download_subtitles
import threading

app = Flask(__name__)

@app.route('/download', methods=['POST'])
def download():
    """异步下载视频和字幕"""
    data = request.json
    url = data.get('url')
    name = data.get('name', 'video')
    subtitles = data.get('subtitles', [])
    
    # 在后台线程中执行下载
    def download_task():
        if download_video(url, output_filename=name):
            if subtitles:
                download_subtitles(subtitles, name + '.mkv')
    
    threading.Thread(target=download_task, daemon=True).start()
    
    return jsonify({'status': 'downloading', 'name': name})

if __name__ == '__main__':
    app.run(debug=True)
```

#### 示例 4: 定时下载任务

```python
from apscheduler.schedulers.background import BackgroundScheduler
from mpv_download import download_video, download_subtitles
import json

class DownloadScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def schedule_download(self, url, name, subtitles=None, hour=0, minute=0):
        """每天指定时间下载"""
        def task():
            print(f"开始下载: {name}")
            if download_video(url, output_filename=name):
                if subtitles:
                    download_subtitles(subtitles, name + '.mkv')
                print(f"✅ {name} 下载完成")
            else:
                print(f"❌ {name} 下载失败")
        
        self.scheduler.add_job(
            task,
            'cron',
            hour=hour,
            minute=minute,
            id=name
        )
    
    def start(self):
        self.scheduler.start()
        print("定时下载器已启动")

# 使用示例
scheduler = DownloadScheduler()
scheduler.schedule_download(
    url="https://example.com/video.mp4",
    name="Daily Video",
    hour=2,  # 每天凌晨2点
    minute=0
)
scheduler.start()
```

### 模块依赖关系

```
download_video()
    ├─ MPVPathFinder (查找 mpv)
    ├─ FileNameManager (处理文件名)
    ├─ DownloadConfig (管理配置)
    └─ VideoDownloader (执行下载)

download_subtitles()
    └─ _download_subtitle_file() (下载单个字幕)
```

### 你可以基于这些模块开发

✨ **前端应用**
- 桌面 GUI（PyQt/PySimpleGUI）
- Web 界面（Flask/Django）
- 命令行工具增强版

💼 **服务集成**
- REST API 服务
- 微服务架构
- 云函数（AWS Lambda）

🤖 **自动化任务**
- 定时下载脚本
- 大规模批量处理
- 与其他工具的流程整合

📊 **数据分析**
- 下载统计和监控
- 性能分析
- 错误日志收集

## 🐛 常见问题

### Q: 找不到 mpv 怎么办？
A: 确保 mpv 已正确安装。mpv 查找优先级为：
1. 当前工作目录
2. 脚本所在目录
3. 系统 PATH 环境变量

## 📝 许可证

GPL-3.0 许可证

---

**Made with ❤️ by AI**
