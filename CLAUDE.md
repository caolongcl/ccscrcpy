# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

CCScrcpy 是一个基于 Python 的 Android 多设备投屏管理工具，支持同时连接和管理多个 Android 设备，提供实时投屏显示、键盘鼠标事件控制、剪切板同步等功能。项目基于开源项目 scrcpy 进行二次开发，使用 PySide6 (Qt6) 构建图形界面。

## 开发环境准备

### Python 环境
- Python 3.10.13
- 安装依赖：`pip install -r requirements.txt`

### 主要依赖
- PySide6 (6.5.2): Qt 图形界面框架
- adbutils (1.2.15): Android 设备通信
- opencv-python (4.9.0.80): 图像处理
- av (9.2.0): 音视频处理

### 运行项目
```bash
python CCScrcpy.py
```

## 打包和分发

### 打包准备
- 依赖: `pip install pyinstaller` (必须)
- 可选: `brew install upx` (macOS) 用于减小文件体积
- 确保 `scrcpy/scrcpy-server.jar` 存在
- 确保图标文件存在: `res/icon.ico` (Windows), `res/icon.icns` (macOS)

### 打包方式
项目提供三种打包模式 (使用 `script/build_optimized.py`):

**1. Balanced 模式 (默认, 推荐)**
```bash
python script/build_optimized.py --mode balanced
```
- 单文件, 平衡体积和启动速度 (约 70-90MB, 启动 2-3s)

**2. Fast 模式 (开发测试)**
```bash
python script/build_optimized.py --mode fast
```
- 多文件, 启动最快 (启动 1-2s), 适合频繁测试

**3. Small 模式 (发布分发)**
```bash
python script/build_optimized.py --mode small  # 需要先安装 UPX
```
- 单文件, UPX 压缩, 体积最小 (约 40-60MB, 启动 4-5s)

### GitHub Actions 自动打包
配置在 `.github/workflows/build.yml`, 支持:
- 推送到 main/dev 分支自动构建
- 创建 Release 时自动上传构建文件
- 产物: macOS (.app), Windows (.exe), macOS DMG 安装包

详见 `docs/BUILD.md`。

## 代码架构

项目采用 MVC 架构模式：

**Model 层** (`model/`)
- `device.py`: Device 和 DeviceManager 类，管理设备连接、状态监控、投屏控制
- `config.py`: UI 配置常量（日志开关、全局控制选项）

**View 层** (`view/`)
- `cc_ui.py`: 主窗口 UI 组装（左侧设备列表 + 右侧投屏视图）
- `cc_left_view.py`: 左侧设备列表视图，显示在线设备和全局控制按钮
- `cc_right_view.py`: 右侧多设备投屏显示视图，处理屏幕渲染和交互事件
- `cc_menu_bar.py`: 菜单栏（设备列数、缩放比例设置）
- `dialog.py`: 重命名设备对话框
- `settings.py`: 设备名称持久化配置管理（ccsettings.ini）
- `cc_frame.py`: Qt 自定义事件/信号框架

**Controller 层** (`CCScrcpy.py`)
- 主入口文件，集成 Model 和 View
- 键盘鼠标事件处理（支持 Ctrl+C/V/X 剪切板同步）
- Qt 键码到 Android 键码的映射（`map_code()` 函数）

**Scrcpy 核心模块** (`scrcpy/`)
- 第三方 scrcpy 客户端的适配实现
- 包含 Android 服务端组件 `scrcpy-server.jar`

## 核心设计

### 设备管理
- `DeviceManager` 使用 `adb.track_devices()` 监控设备连接状态
- 每个设备对应一个 `Device` 实例和独立线程
- 设备状态变化时触发 UI 更新（`__on_devices_changed`）

### 多线程架构
- 主线程：Qt UI 事件循环
- DeviceMonitor 线程：设备连接监控
- Device 线程：scrcpy 投屏流接收（每个设备独立线程）
- Frame 事件线程：图像帧渲染处理

### 事件处理流程
1. scrcpy 接收 Android 设备视频帧 → `__on_frame`
2. 帧数据投递到 Frame 事件 → `post_frame()`
3. Frame 事件触发 → `__on_post`
4. UI 渲染图像 → `render_device_screen()`

### 剪切板同步
- Ctrl+C: 从 Android 设备复制到系统剪切板（`get_clipboard()`）
- Ctrl+V: 从系统剪切板粘贴到 Android 设备（`set_clipboard()`）
- Ctrl+X: 从 Android 设备剪切到系统剪切板

## 配置说明

- `model/config.py`: 可开启调试日志（`ui_config_show_log = True`）
- `view/settings.py`: 管理 `ccsettings.ini` 配置文件，用于存储设备自定义名称
- 菜单栏可动态调整设备列数和屏幕缩放比例

## 注意事项

- 修改 `scrcpy/` 目录下的文件需谨慎，这些是适配后的第三方库
- 设备投屏使用独立线程，避免阻塞 UI
- 图像渲染通过 OpenCV 处理，支持分辨率自适应缩放
- 支持的快捷键映射在 `map_code()` 函数中定义

## 项目结构 (2024-01-15 更新)

### 主要目录
```
ccscrcpy/
├── CCScrcpy.py              # 主入口文件
├── requirements.txt         # Python 依赖
├── CLAUDE.md               # Claude Code 项目说明
├── README.md               # 项目简介
├── LICENSE                 # 许可证
├── .gitignore             # Git 忽略文件
├── .github/               # GitHub Actions 配置
│   └── workflows/
│       ├── build.yml      # 自动打包配置
│       └── README.md      # Actions 说明文档
├── docs/                  # 文档
│   ├── BUILD.md          # 打包说明（主要文档）
│   └── CCScrcpy_image.jpeg # 应用截图
├── script/               # 脚本工具
│   └── build_optimized.py # 优化版打包脚本
├── model/                # Model 层
│   ├── device.py         # 设备管理
│   └── config.py         # 配置
├── view/                # View 层
│   ├── cc_ui.py         # 主窗口
│   ├── cc_left_view.py  # 左侧设备列表
│   ├── cc_right_view.py # 右侧投屏视图
│   ├── cc_menu_bar.py   # 菜单栏
│   ├── dialog.py        # 对话框
│   ├── settings.py      # 设置管理
│   └── cc_frame.py      # 事件框架
├── scrcpy/              # Scrcpy 核心模块
│   ├── __init__.py
│   ├── core.py
│   ├── control.py
│   ├── __main__.py
│   └── scrcpy-server.jar # Android 服务端
└── res/                 # 资源文件
    ├── icon.ico         # Windows 图标
    ├── icon.icns        # macOS 图标
    └── create_icns.py   # 图标转换工具
```

### 主要文件说明
- **CCScrcpy.py**: 应用主入口，集成 Model 和 View，处理输入事件
- **script/build_optimized.py**: 优化版打包脚本，支持三种打包模式
- **docs/BUILD.md**: 打包和分发完整说明文档
- **model/device.py**: 核心设备管理逻辑
- **scrcpy/scrcpy-server.jar**: Android 投屏服务端（必须）

### 最近修改 (2024-01-15)
- ✅ 整理打包脚本：删除 `build.py`，保留优化版 `build_optimized.py`
- ✅ 整理文档：删除 `BUILD_OPTIMIZED.md`，合并到 `BUILD.md`
- ✅ 整理资源：删除冗余图标转换脚本，保留 `create_icns.py`
- ✅ 更新文档：添加详细打包步骤、依赖说明和故障排除
- ✅ 添加 GitHub Actions：自动打包配置 (`.github/workflows/build.yml`)
- ✅ 更新 CLAUDE.md：添加打包和分发章节，更新项目结构说明

