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

如何获取视频直链不在本项目范围内，可参考：
- 使用 Fiddler 抓包
- 调用外部 mpv 播放器后使用 Process Explorer 查看调用参数

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
├── DESIGN_MAIN.md              # main.py 设计文档
├── DESIGN_MPV_DOWNLOAD.md      # mpv_download.py 设计文档
└── README.md                    # 本文件
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

欢迎对本项目进行二次开发！API 已清晰分离：

- `FileNameManager` - 文件名处理逻辑
- `DownloadConfig` - 配置管理
- `VideoDownloader` - 下载执行
- `download_video()` - 简单接口

你可以基于这些模块开发：
- 一键下载剧集脚本
- GUI 应用
- Web 服务
- 定时任务集成
- 等等

## 🐛 常见问题

### Q: 找不到 mpv 怎么办？
A: 确保 mpv 已正确安装。mpv 查找优先级为：
1. 当前工作目录
2. 脚本所在目录
3. 系统 PATH 环境变量

## 📝 许可证

MIT License

---

**Made with ❤️ by AI**
