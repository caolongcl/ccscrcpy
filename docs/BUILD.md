# CCScrcpy 打包说明

本文档说明如何为不同平台打包 CCScrcpy 应用程序。

## 系统要求

### macOS
- macOS 10.15（Catalina）或更高版本
- Python 3.12
- Xcode Command Line Tools（用于编译）

### Windows
- Windows 10 或更高版本
- Python 3.12
- Windows SDK（可选，用于 UPX 压缩）

## 准备工作

### 1. 创建虚拟环境

```bash
# macOS/Linux
python3.12 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. 安装项目依赖

```bash
# 确保在虚拟环境中
pip install -r requirements.txt
```

### 3. 安装 PyInstaller（打包工具）

```bash
pip install pyinstaller
```

### 4. （可选）安装 UPX 压缩工具

UPX 可以显著减小打包后的文件体积（减少 30-50%）。

**macOS:**
```bash
brew install upx
```

**Windows:**
1. 访问 https://github.com/upx/upx/releases
2. 下载 `upx-xxx-win64.zip`
3. 解压并将 `upx.exe` 添加到系统 PATH

### 5. 确保 scrcpy-server.jar 存在

确认 `scrcpy/scrcpy-server.jar` 文件存在于项目中。这是投屏功能的核心组件。

```bash
ls -lh scrcpy/scrcpy-server.jar
```

### 6. 准备图标文件

项目使用 `res/` 目录下的图标文件：

- **Windows**: 使用 `res/icon.ico`
- **macOS**: 使用 `res/icon.icns`

如果只有 icon.ico，需要转换为 icon.icns（macOS 使用）：

```bash
cd res/
python3 create_icns.py
```

## 打包方式

我们提供三种打包模式，适应不同场景：

### 模式对比

| 模式 | 文件大小 | 启动速度 | 适用场景 | 特点 |
|------|---------|---------|---------|------|
| `balanced` | ⭐⭐⭐ 中等 | ⭐⭐⭐ 中等 (2-3s) | 日常使用 | 单文件，平衡体积和速度 |
| `fast` | ⛔ 较大 | ⭐⭐⭐⭐⭐ 最快 (1-2s) | 开发测试 | 多文件，启动最快 |
| `small` | ⭐⭐⭐⭐⭐ 最小 | ⛔ 较慢 (4-5s) | 软件分发 | 单文件，UPX 压缩 |

### 1. Balanced 模式（推荐）

**特点：**
- 单文件可执行程序
- 不使用 UPX 压缩
- 启动速度适中（2-3秒）
- 文件大小适中（约 70-90MB）

**使用：**
```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# .\.venv\Scripts\activate  # Windows

# 打包
python script/build_optimized.py --mode balanced

# 或直接运行（默认就是 balanced 模式）
python script/build_optimized.py
```

**输出：**
- macOS: `dist/CCScrcpy.app`
- Windows: `dist/CCScrcpy.exe`

### 2. Fast 模式（开发测试）

**特点：**
- 多文件模式（一个目录）
- 启动最快（1-2秒）
- 直接运行，无需解压
- 文件总大小较大（约 100-120MB）

**使用：**
```bash
# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# .\.venv\Scripts\activate  # Windows

# 打包
python script/build_optimized.py --mode fast
```

**输出：**
- macOS: `dist/CCScrcpy/CCScrcpy`
- Windows: `dist/CCScrcpy/CCScrcpy.exe`

**说明：** 文件会保存在 `dist/CCScrcpy/` 目录中，包含所有依赖文件。

### 3. Small 模式（发布分发）

**特点：**
- 单文件可执行程序
- 使用 UPX 压缩（必须安装 UPX）
- 文件体积最小（约 40-60MB）
- 启动较慢（需要解压）

**使用：**
```bash
# 1. 先安装 UPX（macOS 示例）
brew install upx

# 2. 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# .\.venv\Scripts\activate  # Windows

# 3. 打包
python script/build_optimized.py --mode small
```

**输出：**
- macOS: `dist/CCScrcpy.app`
- Windows: `dist/CCScrcpy.exe`

## GitHub Actions 自动打包

项目已配置 GitHub Actions，可以自动构建 macOS 和 Windows 版本。

### 触发方式

**方式一：推送到 main/dev 分支**
```bash
git add .
git commit -m "更新功能"
git push origin main
```

**方式二：创建 Release**
```bash
git tag v1.0.0
git push origin v1.0.0
# 然后在 GitHub 上创建 Release
```

### 下载构建产物

**从 Actions 下载（90天有效期）：**
1. 访问 GitHub 仓库 → **Actions** 标签
2. 选择最新的 workflow 运行
3. 滚动到页面底部的 **Artifacts**
4. 下载对应的文件

**从 Release 下载（永久保存）：**
1. 访问 GitHub 仓库 → **Releases** 标签
2. 选择对应的版本
3. 下载构建好的文件

### 产物说明

构建产物包括：

- **CCScrcpy-macOS.zip**: macOS 应用程序（.app 格式）
- **CCScrcpy-Windows.exe**: Windows 可执行文件
- **CCScrcpy-macOS-Installer.dmg**: macOS DMG 安装包（发布时生成）

## 故障排除

### 1. 缺少 scrcpy-server.jar

**错误信息：**
```
PyInstallerImportError: Failed to collect 'scrcpy/scrcpy-server.jar'
```

**解决：**
确保 `scrcpy/scrcpy-server.jar` 文件存在于项目目录中。可以从 scrcpy 官方项目获取。

### 2. ModuleNotFoundError: No module named 'XXXX'

**错误信息：**
```
ModuleNotFoundError: No module named 'PIL'
```

**解决：**
在 `script/build_optimized.py` 中 `--hidden-import=XXXX` 参数。

### 3. UPX 压缩后程序无法运行

**原因：** UPX 可能与某些杀毒软件冲突

**解决：**
```bash
# 不使用 UPX 压缩
python script/build_optimized.py --mode balanced

# 或排除特定文件（编辑 build_optimized.py）
--upx-exclude=vcruntime140.dll
```

### 4. macOS 应用无法启动（无法验证开发者）

**原因：** 未签名的应用程序

**解决：**
- 右键点击应用，选择"打开"
- 或在终端执行：
```bash
xattr -cr /path/to/CCScrcpy.app
```

### 5. Windows 杀毒软件误报

**原因：** PyInstaller 打包的程序可能被误报

**解决：**
将生成的可执行文件添加到杀毒软件的白名单中。

### 6. 打包后文件仍然很大

**正常范围：** 50-100MB 是正常现象

**原因：** PySide6 (Qt) + OpenCV + AV 库本身就很大

**优化建议：**
1. 使用 `small` 模式并安装 UPX
2. 检查是否可以移除不必要的依赖
3. 使用 `fast` 模式（虽然总大小更大，但结构更清晰）

### 7. 启动速度问题

**预期启动时间：**
- `fast` 模式: 1-2 秒
- `balanced` 模式: 2-3 秒
- `small` 模式: 4-5 秒

**优化建议：**
1. 使用 SSD 磁盘
2. 关闭杀毒软件的实时扫描
3. 选择合适的打包模式

## 高级配置

### 自定义排除模块

编辑 `script/build_optimized.py`，在排除列表中添加：
```python
"--exclude-module=your_module",
```

### 强制使用/禁用 UPX

编辑 `script/build_optimized.py`：
```python
# 强制使用 UPX
has_upx = True

# 禁用 UPX
has_upx = False
```

### 添加隐藏导入

如果打包后缺少模块：
```python
"--hidden-import=missing_module",
```

## 发布建议

### 给开发者/测试人员
```bash
python script/build_optimized.py --mode fast
# 输出: dist/CCScrcpy/
```

### 给内部用户
```bash
python script/build_optimized.py --mode balanced
# 输出: dist/CCScrcpy.app 或 dist/CCScrcpy.exe
```

### 给最终用户（发布）
```bash
# 1. 安装 UPX
brew install upx  # macOS

# 2. 打包
python script/build_optimized.py --mode small

# 3. 创建 DMG (macOS)
# 打包完成后会提示创建 DMG

# 4. 数字签名（可选，需要 Apple 开发者账号）
# codesign --deep --force --verify --verbose --sign "Developer ID" dist/CCScrcpy.app
# codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" dist/CCScrcpy.app
```

## 文件清单

打包相关文件：
- `script/build_optimized.py` - 优化版打包脚本
- `docs/BUILD.md` - 本文档
- `.github/workflows/build.yml` - GitHub Actions 配置
- `res/create_icns.py` - 图标转换工具

项目依赖文件：
- `scrcpy/scrcpy-server.jar` - Android 投屏服务端
- `res/icon.ico` - Windows 图标
- `res/icon.icns` - macOS 图标

## 平台限制

**重要：** PyInstaller 不支持交叉编译

- ✅ 在 macOS 上只能打包 macOS 应用
- ✅ 在 Windows 上只能打包 Windows 程序
- ❌ macOS 无法直接打包 Windows 程序
- ❌ Windows 无法直接打包 macOS 应用

**解决方案：**
- 使用 GitHub Actions 自动打包（推荐）
- 在虚拟机上分别打包
- 使用 CI/CD 服务

## 安全考虑

1. 始终在安全的环境中打包
2. 发布前对可执行文件进行病毒扫描
3. 考虑使用代码签名证书（广泛分发时）
4. 定期更新依赖库到最新版本

## 技术支持

如果遇到问题：
1. 查看 **故障排除** 章节
2. 检查 GitHub Issues
3. 提交新的 Issue 并附上错误日志
