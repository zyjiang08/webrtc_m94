# WebRTC M94 快速开始指南

本指南帮助您快速设置并编译 WebRTC M94。

## 系统要求

### 硬件要求
- **磁盘空间**: 至少 15GB 可用空间
  - 源码: 2.2GB
  - 工具链: 3.6GB (Android) + 232KB (Linux)
  - 编译输出: 约 5-8GB
- **内存**: 至少 8GB RAM，推荐 16GB
- **CPU**: 多核处理器（编译时使用多线程）

### 软件要求
- **操作系统**: Linux (已测试 Ubuntu 18.04+)
- **Python**: 3.6+ (已修复 Python 3.12 兼容性)
- **Git**: 用于版本控制

## 快速开始（5 分钟）

### 步骤 1: 获取代码

```bash
# 克隆仓库（当推送到 GitHub 后）
git clone git@github.com:zyjiang08/webrtc_m94.git
cd webrtc_m94

# 或者使用本地路径（临时）
cd /home/harry/awork/webrtc_m94_temp
```

### 步骤 2: 设置工具链

工具链已打包到本地路径 `/home/harry/awork/webrtc-toolchains/`。

```bash
# 检查工具链是否存在
ls -la /home/harry/awork/webrtc-toolchains/

# 应该看到:
# - android/  (3.6GB - Android NDK, GN, Ninja)
# - linux/    (232KB - GN, Ninja)
```

**重要**: 工具链路径已在 `DEPS.json` 中配置为：
- Android: `/home/harry/awork/webrtc-toolchains/android`
- Linux: `/home/harry/awork/webrtc-toolchains/linux`

如果工具链不存在，请联系管理员获取。

### 步骤 3: 初始化工具链符号链接

```bash
# 运行工具链设置脚本
python3 scripts/download_toolchain.py android
python3 scripts/download_toolchain.py linux

# 这会在 toolchains/ 目录下创建符号链接
```

### 步骤 4: 编译

#### 编译 Android 版本

```bash
# ARM 64-bit (推荐 - 现代 Android 设备)
./scripts/build_android.sh arm64

# ARM 32-bit (旧设备)
./scripts/build_android.sh armv7

# x86 64-bit (模拟器)
./scripts/build_android.sh x64

# x86 32-bit
./scripts/build_android.sh x86
```

#### 编译 Linux 版本

```bash
# x86 64-bit
./scripts/build_linux.sh x64
```

### 步骤 5: 查看输出

编译成功后，输出文件位于：

**Android:**
```bash
out/android_arm64/obj/libwebrtc.a              # 静态库
out/android_arm64/libjingle_peerconnection_so.so  # 共享库
```

**Linux:**
```bash
out/linux_x64/obj/libwebrtc.a                  # 静态库
```

## 编译时间参考

| 平台 | 架构 | 首次编译 | 增量编译 |
|------|------|---------|---------|
| Android | arm64 | 30-60分钟 | 2-5分钟 |
| Android | armv7 | 30-60分钟 | 2-5分钟 |
| Linux | x64 | 20-40分钟 | 2-5分钟 |

*编译时间取决于 CPU 核心数和系统性能*

## 常见问题

### Q1: 工具链路径不存在

**问题**: `Toolchain not found` 错误

**解决方案**:
```bash
# 检查工具链是否存在
ls /home/harry/awork/webrtc-toolchains/

# 如果不存在，需要从备份复制或重新打包
# 工具链原始位置: /home/harry/awork/webrtc_m94_temp/toolchains/
```

### Q2: Python 导入错误

**问题**: `ImportError: cannot import name 'Mapping' from 'collections'`

**解决方案**:
- 这个问题已经修复（Python 3.12 兼容）
- jinja2 已更新为使用 `collections.abc.Mapping`
- 详见 `docs/build-troubleshooting.md`

### Q3: 内存不足

**问题**: 编译时出现 `Out of Memory` 错误

**解决方案**:
```bash
# 限制并行编译任务数
ninja -j 4 -C out/android_arm64  # 只使用 4 个线程

# 或者编辑构建脚本，在 ninja 命令后添加 -j 参数
```

### Q4: NDK 路径错误

**问题**: `ANDROID_NDK_HOME not found`

**解决方案**:
```bash
# 设置环境变量
export ANDROID_NDK_HOME=/home/harry/awork/webrtc-toolchains/android/ndk

# 或者修改构建脚本中的路径
```

## 高级选项

### 清理编译产物

```bash
# 清理特定架构的编译输出
rm -rf out/android_arm64

# 清理所有编译输出
rm -rf out/
```

### 调试构建

```bash
# 编译 Debug 版本（包含符号）
./scripts/build_android.sh arm64 Debug
./scripts/build_linux.sh x64 Debug
```

### 查看 GN 配置

```bash
# 查看当前构建配置
gn args out/android_arm64 --list

# 编辑构建参数
gn args out/android_arm64
```

## 下一步

- 阅读 [详细使用文档](USAGE.md) 了解更多编译选项
- 查看 [故障排查指南](build-troubleshooting.md) 解决编译问题
- 了解 [仓库设计](cross-platform-webrtc-repository-design.md) 架构细节

## 获取帮助

- 查看文档: `docs/` 目录
- 问题排查: `docs/build-troubleshooting.md`
- 项目说明: `README.md`
