#!/usr/bin/env python3
"""
将 icon.ico 转换为 icon.icns（使用 PIL/Pillow）
适用于 Python 3 + Pillow
"""

from PIL import Image
import sys
import os
from pathlib import Path


def create_icns_with_pil():
    """使用 PIL 创建 icns 文件"""
    try:
        import PIL
        print(f"PIL 版本: {PIL.__version__}")
    except ImportError:
        print("错误: 未安装 Pillow")
        print("请运行: pip install Pillow")
        return False

    res_dir = Path(__file__).parent
    ico_path = res_dir / "icon.ico"
    icns_path = res_dir / "icon.icns"

    if not ico_path.exists():
        print(f"错误: 找不到 {ico_path}")
        return False

    print(f"加载: {ico_path}")

    try:
        # 加载 ICO 文件
        ico = Image.open(ico_path)

        # macOS .icns 文件需要的尺寸
        icon_sizes = [
            16, 16, 32, 32, 128, 128, 256, 256, 512, 512
        ]

        # 创建临时目标用于保存所有图标
        images = []

        for size in icon_sizes:
            print(f"创建 {size}x{size} 图标...")

            # 创建合适大小的图标
            img = ico.resize((size, size), Image.Resampling.LANCZOS)
            images.append(img)

        # 保存为 ICNS
        # 注意: PIL/Pillow 支持保存 ICNS 格式
        img.save(str(icns_path), format='ICNS', append_images=images)

        if icns_path.exists():
            size = icns_path.stat().st_size
            print(f"\n✓ 转换成功: {icns_path}")
            print(f"文件大小: {size / 1024:.2f} KB")
            return True
        else:
            print("✗ 转换失败")
            return False

    except Exception as e:
        print(f"错误: {e}")
        return False


if __name__ == "__main__":
    if create_icns_with_pil():
        print("\n完成！")
    else:
        sys.exit(1)
