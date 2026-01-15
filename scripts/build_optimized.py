#!/usr/bin/env python3
"""
CCScrcpy 打包脚本（优化版）
支持 Windows 和 macOS 平台，提供多种打包模式

优化特性：
- 文件体积优化（使用 UPX 压缩，排除不必要的模块）
- 启动速度优化（提供 --fast 模式）
- 更细粒度的配置控制
"""

import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path


def check_and_install_pyinstaller():
    """检查并安装 PyInstaller"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} 已安装")
        return True
    except ImportError:
        print("正在安装 PyInstaller...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ PyInstaller 安装成功")
            return True
        else:
            print(f"✗ PyInstaller 安装失败: {result.stderr}")
            return False


def check_upx():
    """检查 UPX 是否可用，返回 UPX 路径或 None"""
    upx_path = None
    system = platform.system()

    # 检查 PATH 中的 upx
    upx_path = shutil.which("upx")

    # Windows: 检查常见安装路径
    if not upx_path and system == "Windows":
        common_paths = [
            r"C:\Program Files\upx.exe",
            r"C:\Program Files (x86)\upx.exe",
            r"C:\upx\upx.exe",
        ]
        for path in common_paths:
            if os.path.exists(path):
                upx_path = path
                break

    if upx_path:
        # Windows: 如果路径包含空格，尝试使用短路径
        if system == "Windows" and " " in upx_path:
            try:
                import ctypes
                import ctypes.wintypes

                # 获取短路径名（8.3 格式）
                GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW
                GetShortPathNameW.argtypes = [
                    ctypes.wintypes.LPCWSTR,
                    ctypes.wintypes.LPWSTR,
                    ctypes.wintypes.DWORD
                ]
                GetShortPathNameW.restype = ctypes.wintypes.DWORD

                short_path = ctypes.create_unicode_buffer(260)
                result = GetShortPathNameW(upx_path, short_path, 260)
                if result and result < 260:
                    upx_path = short_path.value
                    print(f"  使用短路径: {upx_path}")
            except Exception as e:
                print(f"  无法获取短路径: {e}")
        try:
            result = subprocess.run([upx_path, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"✓ UPX 可用: {version}")
                print(f"  路径: {upx_path}")
                return upx_path
        except Exception as e:
            print(f"⚠ UPX 检测失败: {e}")

    print("⚠ 警告: 未找到 UPX，建议安装以减小文件体积")
    print("  安装方法:")
    print("  - macOS: brew install upx")
    print("  - Windows: 下载 https://github.com/upx/upx/releases")
    print("  - 或添加到系统 PATH")
    return None


def get_platform_name():
    """获取当前平台名称"""
    system = platform.system()
    machine = platform.machine()

    if system == "Windows":
        return f"Windows-{machine}"
    elif system == "Darwin":
        return f"macOS-{machine}"
    else:
        return f"{system}-{machine}"


def get_scrcpy_server():
    """获取 scrcpy-server.jar 的路径"""
    possible_paths = [
        "scrcpy/scrcpy-server.jar",
        "./scrcpy/scrcpy-server.jar",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 如果找不到，提示用户
    print("⚠ 警告: 未找到 scrcpy-server.jar")
    response = input("是否继续打包？(y/n): ")
    if response.lower() != 'y':
        sys.exit(1)
    return None


def get_size_mb(file_path):
    """获取文件大小（MB）"""
    if not os.path.exists(file_path):
        return 0
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def get_icon_path():
    """获取当前平台的图标路径"""
    system = platform.system()
    if system == "Windows" and os.path.exists("res/icon.ico"):
        return "res/icon.ico"
    elif system == "Darwin" and os.path.exists("res/icon.icns"):
        return "res/icon.icns"
    return None


def build_windows(mode="balanced", clean=True):
    """Windows 平台打包配置

    Args:
        mode: 打包模式 - 'small' (文件最小), 'fast' (启动最快), 'balanced' (平衡)
        clean: 是否清理之前的构建
    """
    print("\n" + "="*60)
    print(f"开始打包 Windows 版本 - 模式: {mode}")
    print("="*60)

    system = platform.system()

    # 清理之前的构建
    if clean:
        for folder in ["build", "dist/CCScrcpy.exe"]:
            if os.path.exists(folder):
                if os.path.isdir(folder):
                    shutil.rmtree(folder)
                else:
                    os.remove(folder)
                print(f"清理 {folder}")

    scrcpy_server = get_scrcpy_server()
    icon_path = get_icon_path()
    upx_path = check_upx()

    # 基础 PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=CCScrcpy",
        # 包含必要的库
        "--hidden-import=PySide6",
        "--hidden-import=adbutils",
        "--hidden-import=av",
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        # 排除不必要的模块
        "--exclude-module=matplotlib",
        "--exclude-module=test",
        "--exclude-module=unittest",
        "--exclude-module=tkinter",
        "--exclude-module=Tkinter",
        # 去除调试符号（仅 Linux/macOS）
        "--strip" if system != "Windows" else "",
        # 不包含 Python 解释器（减小体积）
        "--noupx" if not upx_path else "",
    ]

    # 如果 UPX 可用，添加 upx 路径
    if upx_path:
        upx_dir = os.path.dirname(upx_path) or os.path.dirname(os.path.abspath(upx_path))
        if upx_dir and os.path.exists(upx_dir):
            # Windows: 如果路径包含空格，尝试使用短路径或提示用户
            if " " in upx_dir and system == "Windows":
                print(f"⚠ 警告: UPX 路径包含空格: {upx_dir}")
                print("  可能导致打包失败。建议:")
                print("  1. 将 UPX 移动到一个没有空格的路径，如 C:\\upx\\")
                print("  2. 或将 'Program Files' 的短路径添加到 PATH")
                print("  3. 或使用 --noupx 参数禁用 UPX 压缩")
                print()
            cmd.append(f"--upx-dir={upx_dir}")
            print(f"使用 UPX 目录: {upx_dir}")

    # 根据模式配置
    if mode == "small":
        # 文件最小化模式：--onefile + UPX
        print("模式: 文件最小化 (启动较慢，体积最小)")
        cmd.extend([
            "--onefile",
            "--windowed",
        ])
    elif mode == "fast":
        # 启动最快模式：--onedir，不压缩
        print("模式: 启动最快 (文件多，启动快)")
        cmd.extend([
            "--onedir",
            "--windowed",
        ])
    else:  # balanced
        # 平衡模式：--onefile，不使用 UPX（或轻度压缩）
        print("模式: 平衡 (单个文件，启动速度适中)")
        cmd.extend([
            "--onefile",
            "--windowed",
        ])

    # 添加图标（如果存在）
    if icon_path:
        cmd.append(f"--icon={icon_path}")
        print(f"使用图标: {icon_path}")

    # 添加数据文件
    if scrcpy_server:
        cmd.append(f"--add-data={scrcpy_server};scrcpy")
        print(f"包含: {scrcpy_server}")

    # UPX 配置
    if upx_path and mode == "small":
        # 只在最小化模式使用 UPX
        print("启用 UPX 压缩")
        # 添加 UPX 排除列表（跳过无法压缩或不应压缩的文件）
        upx_excludes = [
            "vcruntime140.dll",      # Visual C++ 运行时
            "python3.dll",           # Python 核心库（经常无法压缩）
            "python312.dll",         # Python 版本特定库
            "pyexpat.pyd",           # Python EXPAT 模块
            "select.pyd",            # select 模块
            "unicodedata.pyd",       # Unicode 数据模块
            "_bz2.pyd",              # bz2 压缩模块
            "_decimal.pyd",          # decimal 模块
            "_hashlib.pyd",          # hashlib 模块
            "_lzma.pyd",             # lzma 压缩模块
            "_socket.pyd",           # socket 模块
            "_ssl.pyd",              # SSL 模块
            "libcrypto-*.dll",       # OpenSSL 加密库
            "libssl-*.dll",          # OpenSSL SSL 库
            "libgcc_s_seh-*.dll",    # GCC SEH 库
            "libmp3lame-*.dll",      # MP3 LAME 库
            "libopencore-*.dll",     # OpenCORE 库
            "libopus-*.dll",         # Opus 音频库
        ]
        for exclude in upx_excludes:
            cmd.append(f"--upx-exclude={exclude}")
        print(f"  排除 {len(upx_excludes)} 个文件/模式")

    # 隐藏控制台
    cmd.append("--noconsole")

    # 主程序
    cmd.append("CCScrcpy.py")

    # 移除空字符串参数
    cmd = [arg for arg in cmd if arg]

    # 执行打包
    print(f"\n执行命令（长度: {len(cmd)}）:")
    print(f"{' '.join(cmd[:5])} ... {' '.join(cmd[-5:])}")
    print("="*60)

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "="*60)
        # 检查文件大小
        if mode == "fast":
            exe_path = "dist/CCScrcpy/CCScrcpy.exe"
        else:
            exe_path = "dist/CCScrcpy.exe"

        if os.path.exists(exe_path):
            size_mb = get_size_mb(exe_path)
            print(f"✓ Windows 版本打包成功！")
            print(f"文件位置: {os.path.abspath(exe_path)}")
            print(f"文件大小: {size_mb:.2f} MB")

            if mode == "small":
                print("💡 提示: 使用 UPX 压缩减小体积，启动可能稍慢")
            elif mode == "fast":
                print("💡 提示: 启动速度快，但文件分布在目录中")
            else:
                print("💡 提示: 平衡模式和文件大小")
        return True
    else:
        print("\n" + "="*60)
        print("✗ Windows 版本打包失败")
        print("="*60)
        return False


def build_macos(mode="balanced", clean=True):
    """macOS 平台打包配置

    Args:
        mode: 打包模式 - 'small' (文件最小), 'fast' (启动最快), 'balanced' (平衡)
        clean: 是否清理之前的构建
    """
    print("\n" + "="*60)
    print(f"开始打包 macOS 版本 - 模式: {mode}")
    print("="*60)

    system = platform.system()

    # 清理之前的构建
    if clean:
        for folder in ["build", "dist/CCScrcpy", "dist/CCScrcpy.app"]:
            if os.path.exists(folder):
                if os.path.isdir(folder):
                    shutil.rmtree(folder)
                else:
                    os.remove(folder)
                print(f"清理 {folder}")

    scrcpy_server = get_scrcpy_server()
    icon_path = get_icon_path()
    upx_path = check_upx()

    # 基础 PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=CCScrcpy",
        # 包含必要的库
        "--hidden-import=PySide6",
        "--hidden-import=adbutils",
        "--hidden-import=av",
        "--hidden-import=cv2",
        "--hidden-import=numpy",
        "--hidden-import=PIL",
        # 排除不必要的模块
        "--exclude-module=matplotlib",
        "--exclude-module=test",
        "--exclude-module=unittest",
        "--exclude-module=tkinter",
        "--exclude-module=Tkinter",
        # 去除调试符号（仅 Linux/macOS）
        "--strip" if system != "Windows" else "",
        # 不包含 Python 解释器（减小体积）
        "--noupx" if not upx_path else "",
    ]

    # 如果 UPX 可用，添加 upx 路径
    if upx_path:
        upx_dir = os.path.dirname(upx_path) or os.path.dirname(os.path.abspath(upx_path))
        if upx_dir and os.path.exists(upx_dir):
            # Windows: 如果路径包含空格，尝试使用短路径或提示用户
            if " " in upx_dir and system == "Windows":
                print(f"⚠ 警告: UPX 路径包含空格: {upx_dir}")
                print("  可能导致打包失败。建议:")
                print("  1. 将 UPX 移动到一个没有空格的路径，如 C:\\upx\\")
                print("  2. 或将 'Program Files' 的短路径添加到 PATH")
                print("  3. 或使用 --noupx 参数禁用 UPX 压缩")
                print()
            cmd.append(f"--upx-dir={upx_dir}")
            print(f"使用 UPX 目录: {upx_dir}")

    # 根据模式配置
    if mode == "small":
        print("模式: 文件最小化 (启动较慢，体积最小)")
        cmd.extend([
            "--onefile",
            "--windowed",
        ])
    elif mode == "fast":
        print("模式: 启动最快 (文件多，启动快)")
        cmd.extend([
            "--onedir",
            "--windowed",
        ])
    else:  # balanced
        print("模式: 平衡 (单个文件，启动速度适中)")
        cmd.extend([
            "--onefile",
            "--windowed",
        ])

    # 添加 macOS 特定选项
    cmd.append("--osx-bundle-identifier=com.ccscrcpy.app")

    # 添加图标（如果存在）
    if icon_path:
        cmd.append(f"--icon={icon_path}")
        print(f"使用图标: {icon_path}")

    # 添加数据文件（macOS 使用 : 作为路径分隔符）
    if scrcpy_server:
        cmd.append(f"--add-data={scrcpy_server}:scrcpy")
        print(f"包含: {scrcpy_server}")

    # UPX 配置
    if upx_path and mode == "small":
        print("启用 UPX 压缩")
        # 添加 UPX 排除列表（跳过无法压缩或不应压缩的文件）
        upx_excludes = [
            "libQt6Core.dylib",      # Qt6 核心库
            "libQt6Gui.dylib",       # Qt6 GUI 库
            "libQt6Widgets.dylib",   # Qt6 Widgets 库
            "libavcodec.dylib",      # FFmpeg 编码库
            "libavformat.dylib",     # FFmpeg 格式库
            "libavutil.dylib",       # FFmpeg 工具库
            "libswscale.dylib",      # FFmpeg 缩放库
            "libcrypto.*.dylib",     # OpenSSL 加密库
            "libssl.*.dylib",        # OpenSSL SSL 库
            "libopencv_*.*.dylib",   # OpenCV 库
            "libpython*.dylib",      # Python 库
        ]
        for exclude in upx_excludes:
            cmd.append(f"--upx-exclude={exclude}")
        print(f"  排除 {len(upx_excludes)} 个文件/模式")

    # 主程序
    cmd.append("CCScrcpy.py")

    # 移除空字符串参数
    cmd = [arg for arg in cmd if arg]

    print(f"\n执行命令（长度: {len(cmd)}）:")
    print(f"{' '.join(cmd[:5])} ... {' '.join(cmd[-5:])}")
    print("="*60)

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "="*60)
        print("✓ macOS 版本打包成功！")

        # 检查文件大小
        if mode == "fast":
            exe_path = "dist/CCScrcpy/CCScrcpy"
        else:
            exe_path = "dist/CCScrcpy"

        app_path = "dist/CCScrcpy.app"
        success = False

        # .app 应用包
        if os.path.exists(app_path):
            size_mb = get_size_mb(app_path)
            print(f"应用程序包位置: {os.path.abspath(app_path)}")
            print(f"文件大小: {size_mb:.2f} MB")
            success = True

            if mode == "small":
                print("💡 提示: 使用 UPX 压缩减小体积，启动可能稍慢")
            elif mode == "fast":
                print("💡 提示: 启动速度快，但文件分布在目录中")
            else:
                print("💡 提示: 平衡模式和文件大小")

            # 创建 dmg 的选项
            if mode != "fast":  # 只有单文件模式才适合创建 DMG
                print("\n是否创建 DMG 安装包？(y/n): ", end="")
                response = input().lower()
                if response == 'y':
                    create_dmg(mode)
        elif os.path.exists(exe_path):
            size_mb = get_size_mb(exe_path)
            print(f"可执行文件位置: {os.path.abspath(exe_path)}")
            print(f"文件大小: {size_mb:.2f} MB")
            success = True

        if success:
            print("\n" + "="*60)
            return True
    else:
        print("\n" + "="*60)
        print("✗ macOS 版本打包失败")
        print("="*60)
        return False


def create_dmg(mode="balanced"):
    """创建 DMG 安装包"""
    try:
        # 检查是否安装了 create-dmg
        result = subprocess.run(["which", "create-dmg"], capture_output=True)
        if result.returncode != 0:
            print("⚠ 未找到 create-dmg 工具，跳过 DMG 创建")
            print("可以通过 'brew install create-dmg' 安装")
            return

        if not os.path.exists("dist/CCScrcpy.app"):
            print("⚠ 未找到 CCScrcpy.app，跳过 DMG 创建")
            return

        # 清理旧的 dmg
        if os.path.exists("dist/CCScrcpy.dmg"):
            os.remove("dist/CCScrcpy.dmg")

        print("\n创建 DMG 安装包...")
        cmd = [
            "create-dmg",
            "--volname", "CCScrcpy",
            "--window-pos", "200", "120",
            "--window-size", "600", "400",
            "--icon-size", "100",
            "--icon", "CCScrcpy.app", "175", "120",
            "--hide-extension", "CCScrcpy.app",
            "--app-drop-link", "425", "120",
            "dist/CCScrcpy.dmg",
            "dist/CCScrcpy.app"
        ]

        subprocess.run(cmd, check=True)
        size_mb = get_size_mb("dist/CCScrcpy.dmg")
        print(f"✓ DMG 创建成功: dist/CCScrcpy.dmg")
        print(f"DMG 大小: {size_mb:.2f} MB")

    except subprocess.CalledProcessError as e:
        print(f"✗ DMG 创建失败: {e}")
    except Exception as e:
        print(f"✗ DMG 创建出错: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="CCScrcpy 打包工具（优化版）")
    parser.add_argument(
        "--mode",
        choices=["small", "fast", "balanced"],
        default="balanced",
        help="打包模式: small(文件最小), fast(启动最快), balanced(平衡)"
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="不清理之前的构建文件"
    )
    parser.add_argument(
        "--icon-only",
        action="store_true",
        help="只显示图标信息，不打包"
    )

    args = parser.parse_args()

    print("="*60)
    print("CCScrcpy 打包工具（优化版）")
    print(f"当前平台: {get_platform_name()}")
    print(f"Python 版本: {sys.version}")
    print("="*60)

    if args.icon_only:
        icon_path = get_icon_path()
        if icon_path:
            print(f"找到图标: {icon_path}")
        else:
            print("未找到图标文件")
        return

    # 检查 PyInstaller
    if not check_and_install_pyinstaller():
        sys.exit(1)

    # 检查主程序是否存在
    if not os.path.exists("CCScrcpy.py"):
        print("✗ 错误: 未找到 CCScrcpy.py 主程序文件")
        sys.exit(1)

    # 获取 scrcpy-server.jar
    scrcpy_server = get_scrcpy_server()
    if scrcpy_server:
        print(f"✓ 找到 scrcpy-server.jar: {scrcpy_server}")

    # 显示图标信息
    icon_path = get_icon_path()
    if icon_path:
        print(f"✓ 找到图标: {icon_path}")

    # 执行打包
    system = platform.system()
    clean = not args.no_clean

    if system == "Windows":
        success = build_windows(mode=args.mode, clean=clean)
    elif system == "Darwin":
        success = build_macos(mode=args.mode, clean=clean)
    else:
        print(f"⚠ 不支持的平台: {system}")
        print("本脚本仅支持 Windows 和 macOS")
        sys.exit(1)

    if success:
        print("\n" + "="*60)
        print("✓ 打包完成！")
        print("="*60)
        print("\n打包模式说明:")
        if args.mode == "small":
            print("📦 small: 文件体积最小，启动速度较慢（适合分发）")
        elif args.mode == "fast":
            print("⚡ fast: 启动速度最快，文件分布在目录中（适合开发）")
        else:
            print("⚖️  balanced: 单个文件，平衡体积和速度（推荐）")
    else:
        print("\n" + "="*60)
        print("✗ 打包失败")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
