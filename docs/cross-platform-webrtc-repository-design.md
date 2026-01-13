# 跨平台 WebRTC 源码仓库设计方案

## 目录
- [1. 设计目标](#1-设计目标)
- [2. 架构设计](#2-架构设计)
- [3. 目录结构](#3-目录结构)
- [4. 依赖管理策略](#4-依赖管理策略)
- [5. 工具链打包方案](#5-工具链打包方案)
- [6. 构建脚本设计](#6-构建脚本设计)
- [7. 实施步骤](#7-实施步骤)
- [8. 最佳实践](#8-最佳实践)

---

## 1. 设计目标

### 1.1 核心目标

1. **单一源码仓库**：一个仓库支持 Linux、Android、iOS 三平台编译
2. **避免 Submodule**：不使用 Git Submodule，简化仓库管理
3. **最小化 third_party**：只保留必需的运行时依赖
4. **工具链外置**：编译工具链打包成 zip，按需下载
5. **易于维护**：清晰的目录结构和构建流程

### 1.2 约束条件

- 支持平台：Linux (x64)、Android (arm64/armv7/x86/x64)、iOS (arm64/x64)
- 构建系统：GN + Ninja
- 版本控制：Git（单仓库，无 Submodule）
- 工具链分发：独立 zip 包，支持版本管理

---

## 2. 架构设计

### 2.1 整体架构

```
WebRTC-CrossPlatform-Repo/
│
├── Source Code Repository (Git)
│   ├── WebRTC 核心代码
│   ├── 必需的运行时依赖
│   └── 构建配置文件
│
├── Toolchain Packages (独立分发)
│   ├── linux-toolchain-v1.0.0.zip
│   ├── android-toolchain-v1.0.0.zip
│   └── ios-toolchain-v1.0.0.zip
│
└── Build Environment (本地生成)
    ├── 下载并解压工具链
    ├── 配置环境变量
    └── 执行编译
```

### 2.2 依赖分类

#### 核心原则
- **必需保留**：编译和运行时必需的代码库
- **工具链外置**：编译工具、SDK、NDK 等
- **可选移除**：测试、示例、文档等

#### 分类详情

| 类别 | 处理方式 | 示例 |
|------|----------|------|
| **运行时依赖** | 保留在源码仓库 | abseil-cpp, boringssl, libvpx, opus, libyuv |
| **编译工具** | 打包到工具链 zip | llvm-build, depot_tools, clang |
| **平台 SDK** | 打包到工具链 zip | android_ndk, android_sdk, iOS SDK |
| **构建系统** | 打包到工具链 zip | GN, Ninja |
| **测试框架** | 可选移除 | gtest (可保留精简版) |
| **示例代码** | 可选移除 | examples (根据需求) |
| **文档资源** | 可选移除 | blink, catapult (浏览器相关) |

---

## 3. 目录结构

### 3.1 源码仓库结构

```
webrtc-crossplatform/
├── README.md                          # 项目说明
├── CHANGELOG.md                       # 版本变更记录
├── .gitignore                         # Git 忽略规则
├── DEPS.json                          # 依赖版本清单
│
├── src/                               # WebRTC 核心源码
│   ├── api/                          # 公共 API
│   ├── audio/                        # 音频模块
│   ├── video/                        # 视频模块
│   ├── call/                         # 呼叫管理
│   ├── media/                        # 媒体引擎
│   ├── modules/                      # 功能模块
│   ├── pc/                           # PeerConnection
│   ├── p2p/                          # P2P 网络
│   ├── rtc_base/                     # 基础库
│   ├── common_audio/                 # 音频工具
│   ├── common_video/                 # 视频工具
│   ├── system_wrappers/              # 系统抽象层
│   ├── stats/                        # 统计
│   ├── logging/                      # 日志
│   └── net/                          # 网络
│
├── third_party/                       # 第三方依赖（精简版）
│   ├── abseil-cpp/                   # Abseil C++ 库
│   ├── boringssl/                    # SSL/TLS 库
│   ├── libvpx/                       # VP8/VP9 编解码器
│   ├── libyuv/                       # YUV 转换库
│   ├── opus/                         # Opus 音频编解码器
│   ├── usrsctp/                      # SCTP 协议栈
│   ├── protobuf/                     # Protocol Buffers
│   ├── jsoncpp/                      # JSON 解析
│   ├── libaom/                       # AV1 编解码器（可选）
│   ├── openh264/                     # H.264 编解码器（可选）
│   └── README.md                     # 依赖说明
│
├── build/                             # 构建配置
│   ├── config/                       # 平台配置
│   │   ├── linux/
│   │   ├── android/
│   │   └── ios/
│   ├── toolchain/                    # 工具链配置
│   │   ├── linux.gni
│   │   ├── android.gni
│   │   └── ios.gni
│   └── BUILDCONFIG.gn                # 全局构建配置
│
├── scripts/                           # 构建和工具脚本
│   ├── setup_toolchain.sh            # 工具链设置脚本
│   ├── download_toolchain.py         # 工具链下载脚本
│   ├── build_linux.sh                # Linux 构建脚本
│   ├── build_android.sh              # Android 构建脚本
│   ├── build_ios.sh                  # iOS 构建脚本
│   ├── clean.sh                      # 清理脚本
│   └── package_release.sh            # 打包发布脚本
│
├── toolchains/                        # 工具链目录（本地生成，不提交到 Git）
│   ├── linux/
│   │   ├── gn
│   │   ├── ninja
│   │   ├── clang/
│   │   └── sysroot/
│   ├── android/
│   │   ├── gn
│   │   ├── ninja
│   │   ├── ndk/
│   │   └── sdk/
│   └── ios/
│       ├── gn
│       ├── ninja
│       └── xcode-tools/
│
├── out/                               # 编译输出（不提交到 Git）
│   ├── linux_x64/
│   ├── android_arm64/
│   ├── android_armv7/
│   ├── ios_arm64/
│   └── ios_x64/
│
├── docs/                              # 文档
│   ├── build-instructions.md         # 构建说明
│   ├── api-reference.md              # API 参考
│   ├── architecture.md               # 架构说明
│   └── troubleshooting.md            # 问题排查
│
└── examples/                          # 示例代码（可选）
    ├── simple_peer_connection/
    └── audio_video_chat/
```

### 3.2 .gitignore 配置

```gitignore
# 编译产物
out/
*.o
*.a
*.so
*.dll
*.dylib
*.framework

# 工具链（不提交）
toolchains/

# 临时文件
*.pyc
*.swp
*~
.DS_Store

# IDE 文件
.vscode/
.idea/
*.xcodeproj/xcuserdata/

# 构建缓存
.ninja_deps
.ninja_log
build.ninja

# 下载的依赖
downloads/
```

---

## 4. 依赖管理策略

### 4.1 必需的第三方依赖（保留在仓库）

#### 核心库（约 2-3 GB）

| 依赖 | 大小 | 用途 | 说明 |
|------|------|------|------|
| **abseil-cpp** | ~50 MB | C++ 基础库 | Google 的 C++ 通用库 |
| **boringssl** | ~370 MB | SSL/TLS | 加密通信 |
| **libvpx** | ~20 MB | VP8/VP9 编解码 | 视频编解码器 |
| **libyuv** | ~5 MB | YUV 处理 | 颜色空间转换 |
| **opus** | ~10 MB | 音频编解码 | 音频编解码器 |
| **usrsctp** | ~5 MB | SCTP 协议 | DataChannel 支持 |
| **protobuf** | ~80 MB | 序列化 | 数据序列化（轻量版） |
| **jsoncpp** | ~2 MB | JSON 解析 | 配置文件解析 |

#### 可选库（根据需求保留）

| 依赖 | 大小 | 用途 | 说明 |
|------|------|------|------|
| **libaom** | ~450 MB | AV1 编解码 | 新一代视频编解码器 |
| **openh264** | ~185 MB | H.264 编解码 | H.264 视频编解码器 |
| **libsrtp** | ~5 MB | SRTP | 媒体加密 |

**总计**：核心依赖约 **550 MB**，加上可选依赖约 **1.2 GB**

### 4.2 移除的依赖（移到工具链）

#### 编译工具（约 8 GB）

| 依赖 | 大小 | 移动位置 | 说明 |
|------|------|----------|------|
| **android_ndk** | ~5.6 GB | android-toolchain.zip | Android NDK |
| **android_sdk** | ~1.3 GB | android-toolchain.zip | Android SDK |
| **llvm-build** | ~195 MB | {platform}-toolchain.zip | LLVM 编译器 |
| **depot_tools** | ~787 MB | {platform}-toolchain.zip | GN, Ninja 等工具 |

#### 测试和开发工具（约 5 GB）

| 依赖 | 大小 | 处理方式 | 说明 |
|------|------|----------|------|
| **blink** | ~2.0 GB | 完全移除 | 浏览器相关 |
| **catapult** | ~1.0 GB | 完全移除 | 性能测试工具 |
| **instrumented_libs** | ~2.2 GB | 完全移除 | 内存检测库 |
| **robolectric** | ~610 MB | 可选保留 | Android 单元测试 |

### 4.3 依赖版本管理

#### DEPS.json 示例

```json
{
  "version": "1.0.0",
  "webrtc_branch": "m94",
  "dependencies": {
    "abseil-cpp": {
      "version": "20210324.2",
      "commit": "273292d1cfc0a94a65082ee350509af1d113344d"
    },
    "boringssl": {
      "version": "master",
      "commit": "1607f54fed72c06e05c6e20f0d6d35e6c8c9f7f8"
    },
    "libvpx": {
      "version": "1.10.0",
      "commit": "d5d6bb0f84b86abb2c4a7e6dc16e5e87c1e7cb51"
    },
    "opus": {
      "version": "1.3.1",
      "commit": "ad8fe90db79b7d2a135e3dfd2ed6631b0c5662ab"
    }
  },
  "toolchains": {
    "linux": {
      "url": "https://example.com/toolchains/linux-toolchain-v1.0.0.zip",
      "sha256": "abc123...",
      "size": "500MB"
    },
    "android": {
      "url": "https://example.com/toolchains/android-toolchain-v1.0.0.zip",
      "sha256": "def456...",
      "size": "7.5GB"
    },
    "ios": {
      "url": "https://example.com/toolchains/ios-toolchain-v1.0.0.zip",
      "sha256": "ghi789...",
      "size": "2GB"
    }
  }
}
```

---

## 5. 工具链打包方案

### 5.1 工具链组成

#### Linux 工具链 (~500 MB)

```
linux-toolchain-v1.0.0.zip
├── gn                          # GN 构建工具
├── ninja                       # Ninja 编译工具
├── clang/                      # Clang 编译器
│   ├── bin/
│   ├── lib/
│   └── include/
├── sysroot/                    # Linux sysroot
│   ├── usr/
│   └── lib/
└── depot_tools/                # Chromium depot_tools
    ├── gn.py
    └── ninja
```

#### Android 工具链 (~7.5 GB)

```
android-toolchain-v1.0.0.zip
├── gn                          # GN 构建工具
├── ninja                       # Ninja 编译工具
├── ndk/                        # Android NDK
│   ├── toolchains/
│   │   └── llvm/
│   ├── sources/
│   └── platforms/
├── sdk/                        # Android SDK（精简版）
│   ├── build-tools/
│   ├── platforms/
│   │   └── android-29/
│   └── tools/
└── depot_tools/                # Chromium depot_tools
```

#### iOS 工具链 (~2 GB)

```
ios-toolchain-v1.0.0.zip
├── gn                          # GN 构建工具
├── ninja                       # Ninja 编译工具
├── xcode-tools/                # Xcode 命令行工具
│   ├── bin/
│   ├── lib/
│   └── Platforms/
│       ├── iPhoneOS.platform/
│       └── iPhoneSimulator.platform/
└── depot_tools/                # Chromium depot_tools
```

### 5.2 工具链打包脚本

#### 打包脚本：`scripts/package_toolchain.sh`

```bash
#!/bin/bash

PLATFORM=$1  # linux, android, ios
VERSION=$2   # 例如：v1.0.0

if [ -z "$PLATFORM" ] || [ -z "$VERSION" ]; then
    echo "Usage: $0 <platform> <version>"
    echo "Example: $0 android v1.0.0"
    exit 1
fi

TOOLCHAIN_DIR="toolchains/${PLATFORM}"
OUTPUT_FILE="${PLATFORM}-toolchain-${VERSION}.zip"

echo "Packaging ${PLATFORM} toolchain..."

case $PLATFORM in
    linux)
        cd $TOOLCHAIN_DIR
        zip -r ../../$OUTPUT_FILE \
            gn \
            ninja \
            clang/ \
            sysroot/ \
            depot_tools/
        ;;
    android)
        cd $TOOLCHAIN_DIR
        zip -r ../../$OUTPUT_FILE \
            gn \
            ninja \
            ndk/ \
            sdk/ \
            depot_tools/
        ;;
    ios)
        cd $TOOLCHAIN_DIR
        zip -r ../../$OUTPUT_FILE \
            gn \
            ninja \
            xcode-tools/ \
            depot_tools/
        ;;
    *)
        echo "Unknown platform: $PLATFORM"
        exit 1
        ;;
esac

cd ../..
echo "Toolchain packaged: $OUTPUT_FILE"

# 计算 SHA256
sha256sum $OUTPUT_FILE > ${OUTPUT_FILE}.sha256
echo "SHA256: $(cat ${OUTPUT_FILE}.sha256)"
```

### 5.3 工具链下载和安装脚本

#### 下载脚本：`scripts/download_toolchain.py`

```python
#!/usr/bin/env python3
"""
工具链下载和验证脚本
"""

import json
import os
import sys
import hashlib
import urllib.request
import zipfile
import shutil

def load_deps():
    """加载 DEPS.json"""
    with open('DEPS.json', 'r') as f:
        return json.load(f)

def calculate_sha256(filepath):
    """计算文件 SHA256"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def download_file(url, filepath):
    """下载文件并显示进度"""
    print(f"Downloading {url}...")

    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        sys.stdout.write(f"\rProgress: {percent:.1f}%")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, filepath, report_progress)
    print("\nDownload complete!")

def extract_zip(zip_path, extract_dir):
    """解压 zip 文件"""
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("Extraction complete!")

def setup_toolchain(platform):
    """设置指定平台的工具链"""
    deps = load_deps()

    if platform not in deps['toolchains']:
        print(f"Error: Unknown platform '{platform}'")
        print(f"Available platforms: {', '.join(deps['toolchains'].keys())}")
        return False

    toolchain_info = deps['toolchains'][platform]
    url = toolchain_info['url']
    expected_sha256 = toolchain_info['sha256']

    # 创建目录
    toolchains_dir = 'toolchains'
    platform_dir = os.path.join(toolchains_dir, platform)
    downloads_dir = 'downloads'

    os.makedirs(downloads_dir, exist_ok=True)
    os.makedirs(toolchains_dir, exist_ok=True)

    # 下载文件
    filename = os.path.basename(url)
    zip_path = os.path.join(downloads_dir, filename)

    if os.path.exists(zip_path):
        print(f"Toolchain already downloaded: {zip_path}")
    else:
        download_file(url, zip_path)

    # 验证 SHA256
    print("Verifying checksum...")
    actual_sha256 = calculate_sha256(zip_path)

    if actual_sha256 != expected_sha256:
        print(f"Error: Checksum mismatch!")
        print(f"Expected: {expected_sha256}")
        print(f"Actual:   {actual_sha256}")
        return False

    print("Checksum verified!")

    # 解压
    if os.path.exists(platform_dir):
        print(f"Removing existing toolchain directory: {platform_dir}")
        shutil.rmtree(platform_dir)

    extract_zip(zip_path, platform_dir)

    print(f"\n✓ Toolchain setup complete for {platform}!")
    print(f"  Location: {platform_dir}")

    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 download_toolchain.py <platform>")
        print("Platforms: linux, android, ios, all")
        sys.exit(1)

    platform = sys.argv[1]

    if platform == 'all':
        deps = load_deps()
        platforms = list(deps['toolchains'].keys())
        for p in platforms:
            if not setup_toolchain(p):
                sys.exit(1)
    else:
        if not setup_toolchain(platform):
            sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## 6. 构建脚本设计

### 6.1 统一的构建脚本接口

所有平台的构建脚本使用统一的接口：

```bash
./scripts/build_<platform>.sh <architecture> [options]
```

### 6.2 Linux 构建脚本

#### `scripts/build_linux.sh`

```bash
#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 检查工具链
if [ ! -d "$ROOT_DIR/toolchains/linux" ]; then
    echo "Error: Linux toolchain not found!"
    echo "Please run: python3 scripts/download_toolchain.py linux"
    exit 1
fi

# 设置环境变量
export PATH="$ROOT_DIR/toolchains/linux:$PATH"
export CC="$ROOT_DIR/toolchains/linux/clang/bin/clang"
export CXX="$ROOT_DIR/toolchains/linux/clang/bin/clang++"

# 架构
ARCH=${1:-x64}  # 默认 x64

# 构建类型
BUILD_TYPE=${2:-Release}  # Debug 或 Release

# 输出目录
OUT_DIR="$ROOT_DIR/out/linux_${ARCH}"

echo "Building WebRTC for Linux (${ARCH}, ${BUILD_TYPE})..."

# GN 参数
GN_ARGS="target_os=\"linux\" target_cpu=\"${ARCH}\""

if [ "$BUILD_TYPE" = "Release" ]; then
    GN_ARGS="$GN_ARGS is_debug=false"
else
    GN_ARGS="$GN_ARGS is_debug=true"
fi

# 生成构建文件
cd "$ROOT_DIR/src"
$ROOT_DIR/toolchains/linux/gn gen "$OUT_DIR" --args="$GN_ARGS"

# 编译
$ROOT_DIR/toolchains/linux/ninja -C "$OUT_DIR"

echo "✓ Build complete!"
echo "  Output: $OUT_DIR/libwebrtc.a"
```

### 6.3 Android 构建脚本

#### `scripts/build_android.sh`

```bash
#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 检查工具链
if [ ! -d "$ROOT_DIR/toolchains/android" ]; then
    echo "Error: Android toolchain not found!"
    echo "Please run: python3 scripts/download_toolchain.py android"
    exit 1
fi

# 设置环境变量
export PATH="$ROOT_DIR/toolchains/android:$PATH"
export ANDROID_NDK_HOME="$ROOT_DIR/toolchains/android/ndk"
export ANDROID_SDK_ROOT="$ROOT_DIR/toolchains/android/sdk"

# 架构
ARCH=${1:-arm64}  # arm64, armv7, x64, x86

# 构建类型
BUILD_TYPE=${2:-Release}

# 输出目录
OUT_DIR="$ROOT_DIR/out/android_${ARCH}"

echo "Building WebRTC for Android (${ARCH}, ${BUILD_TYPE})..."

# GN 参数
GN_ARGS="target_os=\"android\" target_cpu=\"${ARCH}\""
GN_ARGS="$GN_ARGS rtc_use_h264=true"
GN_ARGS="$GN_ARGS rtc_include_internal_audio_device=false"
GN_ARGS="$GN_ARGS treat_warnings_as_errors=false"

if [ "$BUILD_TYPE" = "Release" ]; then
    GN_ARGS="$GN_ARGS is_debug=false"
else
    GN_ARGS="$GN_ARGS is_debug=true"
fi

# 生成构建文件
cd "$ROOT_DIR/src"
$ROOT_DIR/toolchains/android/gn gen "$OUT_DIR" --args="$GN_ARGS"

# 编译
$ROOT_DIR/toolchains/android/ninja -C "$OUT_DIR"

echo "✓ Build complete!"
echo "  Output: $OUT_DIR/libwebrtc.a"
echo "  Output: $OUT_DIR/libjingle_peerconnection_so.so"
```

### 6.4 iOS 构建脚本

#### `scripts/build_ios.sh`

```bash
#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 检查工具链
if [ ! -d "$ROOT_DIR/toolchains/ios" ]; then
    echo "Error: iOS toolchain not found!"
    echo "Please run: python3 scripts/download_toolchain.py ios"
    exit 1
fi

# 设置环境变量
export PATH="$ROOT_DIR/toolchains/ios:$PATH"

# 架构
ARCH=${1:-arm64}  # arm64 (device), x64 (simulator)

# 构建类型
BUILD_TYPE=${2:-Release}

# 输出目录
OUT_DIR="$ROOT_DIR/out/ios_${ARCH}"

echo "Building WebRTC for iOS (${ARCH}, ${BUILD_TYPE})..."

# GN 参数
GN_ARGS="target_os=\"ios\" target_cpu=\"${ARCH}\""
GN_ARGS="$GN_ARGS ios_enable_code_signing=false"

if [ "$BUILD_TYPE" = "Release" ]; then
    GN_ARGS="$GN_ARGS is_debug=false"
else
    GN_ARGS="$GN_ARGS is_debug=true"
fi

# 生成构建文件
cd "$ROOT_DIR/src"
$ROOT_DIR/toolchains/ios/gn gen "$OUT_DIR" --args="$GN_ARGS"

# 编译
$ROOT_DIR/toolchains/ios/ninja -C "$OUT_DIR"

echo "✓ Build complete!"
echo "  Output: $OUT_DIR/WebRTC.framework"
```

### 6.5 一键构建所有平台

#### `scripts/build_all.sh`

```bash
#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Building WebRTC for all platforms..."

# Linux
echo "=== Building Linux x64 ==="
$SCRIPT_DIR/build_linux.sh x64 Release

# Android
echo "=== Building Android arm64 ==="
$SCRIPT_DIR/build_android.sh arm64 Release

echo "=== Building Android armv7 ==="
$SCRIPT_DIR/build_android.sh armv7 Release

# iOS
echo "=== Building iOS arm64 ==="
$SCRIPT_DIR/build_ios.sh arm64 Release

echo "=== Building iOS x64 (Simulator) ==="
$SCRIPT_DIR/build_ios.sh x64 Release

echo "✓ All builds complete!"
```

---

## 7. 实施步骤

### 7.1 准备阶段

#### 第 1 步：创建仓库结构

```bash
# 创建目录结构
mkdir -p webrtc-crossplatform/{src,third_party,build,scripts,docs,toolchains,out}

cd webrtc-crossplatform

# 初始化 Git 仓库
git init

# 创建 .gitignore
cat > .gitignore << 'EOF'
# 编译产物
out/
*.o
*.a
*.so
*.dll
*.dylib
*.framework

# 工具链
toolchains/

# 下载
downloads/

# 临时文件
*.pyc
*.swp
*~
.DS_Store

# IDE
.vscode/
.idea/
*.xcodeproj/xcuserdata/

# 构建缓存
.ninja_deps
.ninja_log
build.ninja
EOF

# 创建 DEPS.json
cat > DEPS.json << 'EOF'
{
  "version": "1.0.0",
  "webrtc_branch": "m94",
  "dependencies": {},
  "toolchains": {}
}
EOF

# 创建 README.md
cat > README.md << 'EOF'
# WebRTC Cross-Platform

跨平台 WebRTC 源码仓库，支持 Linux、Android、iOS 编译。

## 快速开始

1. 克隆仓库
2. 下载工具链：`python3 scripts/download_toolchain.py <platform>`
3. 编译：`./scripts/build_<platform>.sh <arch>`

详见 [docs/build-instructions.md](docs/build-instructions.md)
EOF
```

#### 第 2 步：迁移 WebRTC 核心代码

```bash
# 从现有 WebRTC 仓库复制核心代码
SOURCE_WEBRTC="/home/harry/work/LLS-Player/webrtc.compile/src"

# 复制核心源码目录
cp -r $SOURCE_WEBRTC/api src/
cp -r $SOURCE_WEBRTC/audio src/
cp -r $SOURCE_WEBRTC/video src/
cp -r $SOURCE_WEBRTC/call src/
cp -r $SOURCE_WEBRTC/media src/
cp -r $SOURCE_WEBRTC/modules src/
cp -r $SOURCE_WEBRTC/pc src/
cp -r $SOURCE_WEBRTC/p2p src/
cp -r $SOURCE_WEBRTC/rtc_base src/
cp -r $SOURCE_WEBRTC/common_audio src/
cp -r $SOURCE_WEBRTC/common_video src/
cp -r $SOURCE_WEBRTC/system_wrappers src/
cp -r $SOURCE_WEBRTC/stats src/
cp -r $SOURCE_WEBRTC/logging src/
cp -r $SOURCE_WEBRTC/net src/

# 复制构建文件
cp $SOURCE_WEBRTC/BUILD.gn src/
cp $SOURCE_WEBRTC/.gn src/
cp $SOURCE_WEBRTC/webrtc.gni src/

# 复制构建配置
cp -r $SOURCE_WEBRTC/build build/
```

#### 第 3 步：精简 third_party 依赖

```bash
# 只复制必需的运行时依赖
ESSENTIAL_DEPS=(
    "abseil-cpp"
    "boringssl"
    "libvpx"
    "libyuv"
    "opus"
    "usrsctp"
    "protobuf"
    "jsoncpp"
)

for dep in "${ESSENTIAL_DEPS[@]}"; do
    echo "Copying $dep..."
    cp -r $SOURCE_WEBRTC/third_party/$dep third_party/
done

# 可选依赖（根据需求）
OPTIONAL_DEPS=(
    "libaom"
    "openh264"
    "libsrtp"
)

# 创建依赖说明
cat > third_party/README.md << 'EOF'
# Third-Party Dependencies

## Essential Dependencies (Always Required)

- **abseil-cpp**: Abseil C++ library
- **boringssl**: SSL/TLS library
- **libvpx**: VP8/VP9 codec
- **libyuv**: YUV conversion
- **opus**: Opus audio codec
- **usrsctp**: SCTP stack for DataChannel
- **protobuf**: Protocol Buffers
- **jsoncpp**: JSON parser

## Optional Dependencies

- **libaom**: AV1 codec
- **openh264**: H.264 codec
- **libsrtp**: SRTP encryption

Total size: ~1.2 GB (with optional dependencies)
EOF
```

### 7.2 工具链准备阶段

#### 第 4 步：打包 Linux 工具链

```bash
# 创建 Linux 工具链目录
mkdir -p toolchains/linux

# 从现有环境复制工具
cp $SOURCE_WEBRTC/buildtools/linux64/gn toolchains/linux/
cp /usr/bin/ninja toolchains/linux/

# 复制 Clang（如果使用系统 Clang，可以跳过）
# cp -r /usr/lib/llvm-10 toolchains/linux/clang

# 打包
./scripts/package_toolchain.sh linux v1.0.0
```

#### 第 5 步：打包 Android 工具链

```bash
# 创建 Android 工具链目录
mkdir -p toolchains/android

# 复制工具
cp $SOURCE_WEBRTC/buildtools/linux64/gn toolchains/android/
cp /usr/bin/ninja toolchains/android/

# 复制 NDK 和 SDK
cp -r $SOURCE_WEBRTC/third_party/android_ndk toolchains/android/ndk
cp -r $SOURCE_WEBRTC/third_party/android_sdk toolchains/android/sdk

# 打包（会比较大，约 7.5 GB）
./scripts/package_toolchain.sh android v1.0.0
```

#### 第 6 步：打包 iOS 工具链

```bash
# 创建 iOS 工具链目录
mkdir -p toolchains/ios

# 复制工具
cp $SOURCE_WEBRTC/buildtools/mac/gn toolchains/ios/
cp /usr/bin/ninja toolchains/ios/

# Xcode 工具需要在 macOS 上准备
# 这里假设已经有 Xcode 命令行工具

# 打包
./scripts/package_toolchain.sh ios v1.0.0
```

### 7.3 发布阶段

#### 第 7 步：上传工具链到服务器

```bash
# 上传到文件服务器或对象存储
# 示例：使用 rsync 或 AWS S3

# 使用 rsync
rsync -avz linux-toolchain-v1.0.0.zip user@server:/path/to/toolchains/

# 或使用 AWS S3
# aws s3 cp linux-toolchain-v1.0.0.zip s3://your-bucket/toolchains/

# 更新 DEPS.json 中的 URL 和 SHA256
```

#### 第 8 步：更新 DEPS.json

```json
{
  "version": "1.0.0",
  "webrtc_branch": "m94",
  "dependencies": {
    "abseil-cpp": {
      "version": "20210324.2",
      "commit": "273292d1cfc0a94a65082ee350509af1d113344d"
    }
  },
  "toolchains": {
    "linux": {
      "url": "https://your-server.com/toolchains/linux-toolchain-v1.0.0.zip",
      "sha256": "计算出的SHA256值",
      "size": "500MB"
    },
    "android": {
      "url": "https://your-server.com/toolchains/android-toolchain-v1.0.0.zip",
      "sha256": "计算出的SHA256值",
      "size": "7.5GB"
    },
    "ios": {
      "url": "https://your-server.com/toolchains/ios-toolchain-v1.0.0.zip",
      "sha256": "计算出的SHA256值",
      "size": "2GB"
    }
  }
}
```

#### 第 9 步：提交代码到 Git

```bash
# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: WebRTC cross-platform repository

- Core WebRTC source code (M94 branch)
- Essential third-party dependencies (~1.2 GB)
- Build scripts for Linux, Android, iOS
- Toolchain download and setup scripts
- Documentation
"

# 推送到远程仓库
git remote add origin <your-repo-url>
git push -u origin main
```

### 7.4 验证阶段

#### 第 10 步：验证构建流程

```bash
# 在新环境中测试

# 1. 克隆仓库
git clone <your-repo-url>
cd webrtc-crossplatform

# 2. 下载 Linux 工具链
python3 scripts/download_toolchain.py linux

# 3. 编译 Linux 版本
./scripts/build_linux.sh x64 Release

# 4. 验证输出
ls -lh out/linux_x64/libwebrtc.a

# 5. 测试 Android 编译
python3 scripts/download_toolchain.py android
./scripts/build_android.sh arm64 Release
ls -lh out/android_arm64/libwebrtc.a
```

---

## 8. 最佳实践

### 8.1 版本管理

#### 语义化版本

```
主版本.次版本.修订版本
1.0.0 -> 初始版本
1.1.0 -> 添加新功能
1.1.1 -> Bug 修复
2.0.0 -> 重大变更（不兼容）
```

#### 版本发布流程

1. **更新版本号**：修改 `DEPS.json` 中的 `version`
2. **创建 Git 标签**：`git tag v1.0.0`
3. **更新 CHANGELOG.md**：记录变更内容
4. **打包工具链**：如果工具链有更新
5. **发布**：推送标签 `git push origin v1.0.0`

### 8.2 持续集成（CI）

#### GitHub Actions 示例

`.github/workflows/build.yml`:

```yaml
name: Build WebRTC

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Download Linux toolchain
        run: python3 scripts/download_toolchain.py linux

      - name: Build Linux x64
        run: ./scripts/build_linux.sh x64 Release

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: linux-x64
          path: out/linux_x64/libwebrtc.a

  build-android:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        arch: [arm64, armv7]
    steps:
      - uses: actions/checkout@v2

      - name: Download Android toolchain
        run: python3 scripts/download_toolchain.py android

      - name: Build Android ${{ matrix.arch }}
        run: ./scripts/build_android.sh ${{ matrix.arch }} Release

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: android-${{ matrix.arch }}
          path: out/android_${{ matrix.arch }}/libwebrtc.a
```

### 8.3 依赖更新策略

#### 更新第三方依赖

```bash
# 1. 更新 abseil-cpp
cd third_party/abseil-cpp
git fetch origin
git checkout <new-commit>

# 2. 更新 DEPS.json
# 记录新的 commit hash

# 3. 测试编译
./scripts/build_linux.sh x64 Debug

# 4. 提交更新
git add third_party/abseil-cpp DEPS.json
git commit -m "Update abseil-cpp to <version>"
```

#### 自动化依赖更新

可以编写脚本定期检查依赖更新：

```python
#!/usr/bin/env python3
"""
检查第三方依赖是否有更新
"""

import json
import subprocess

def check_updates():
    with open('DEPS.json', 'r') as f:
        deps = json.load(f)

    for name, info in deps['dependencies'].items():
        print(f"Checking {name}...")
        path = f"third_party/{name}"

        # 获取最新 commit
        result = subprocess.run(
            ['git', '-C', path, 'fetch', 'origin'],
            capture_output=True
        )

        result = subprocess.run(
            ['git', '-C', path, 'rev-parse', 'origin/HEAD'],
            capture_output=True,
            text=True
        )

        latest_commit = result.stdout.strip()
        current_commit = info['commit']

        if latest_commit != current_commit:
            print(f"  ⚠️  Update available:")
            print(f"    Current: {current_commit[:8]}")
            print(f"    Latest:  {latest_commit[:8]}")
        else:
            print(f"  ✓ Up to date")

if __name__ == '__main__':
    check_updates()
```

### 8.4 工具链管理

#### 工具链版本矩阵

| 工具链版本 | WebRTC 版本 | 支持平台 | 发布日期 |
|-----------|------------|----------|---------|
| v1.0.0 | M94 | Linux, Android, iOS | 2026-01-01 |
| v1.1.0 | M94 | Linux, Android, iOS | 2026-02-01 |
| v2.0.0 | M96 | Linux, Android, iOS | 2026-03-01 |

#### 工具链镜像

为了加速下载，可以设置多个镜像：

```json
{
  "toolchains": {
    "linux": {
      "urls": [
        "https://primary-server.com/toolchains/linux-toolchain-v1.0.0.zip",
        "https://mirror1.com/toolchains/linux-toolchain-v1.0.0.zip",
        "https://mirror2.com/toolchains/linux-toolchain-v1.0.0.zip"
      ],
      "sha256": "abc123...",
      "size": "500MB"
    }
  }
}
```

### 8.5 文档维护

#### 必备文档

1. **README.md** - 项目概述和快速开始
2. **docs/build-instructions.md** - 详细构建说明
3. **docs/architecture.md** - 架构设计文档
4. **docs/api-reference.md** - API 参考
5. **docs/troubleshooting.md** - 问题排查指南
6. **CHANGELOG.md** - 版本变更记录
7. **CONTRIBUTING.md** - 贡献指南

### 8.6 性能优化

#### 并行编译

```bash
# 使用所有 CPU 核心
./scripts/build_linux.sh x64 Release -j$(nproc)

# 或在 build 脚本中默认启用
ninja -j$(nproc) -C out/linux_x64
```

#### 增量编译

```bash
# 只重新编译修改的文件
ninja -C out/linux_x64
```

#### ccache 加速

```bash
# 安装 ccache
sudo apt-get install ccache

# 配置 GN 使用 ccache
GN_ARGS="$GN_ARGS cc_wrapper=\"ccache\""
```

---

## 9. 总结

### 9.1 方案优势

1. **单一仓库**：所有平台共享一个源码仓库，便于管理
2. **无 Submodule**：避免 Submodule 的复杂性
3. **精简依赖**：只保留 ~1.2 GB 必需依赖，大幅减小仓库体积
4. **工具链外置**：编译工具链打包成 zip，按需下载
5. **统一接口**：所有平台使用统一的构建脚本接口
6. **版本管理**：通过 DEPS.json 管理所有依赖和工具链版本
7. **易于扩展**：可以轻松添加新平台或更新依赖

### 9.2 关键指标

| 指标 | 数值 |
|------|------|
| **源码仓库大小** | ~1.5 GB（包含核心代码 + 精简依赖） |
| **原始 third_party 大小** | ~15 GB |
| **精简后 third_party** | ~1.2 GB |
| **减少比例** | 92% ↓ |
| **Linux 工具链** | ~500 MB |
| **Android 工具链** | ~7.5 GB |
| **iOS 工具链** | ~2 GB |

### 9.3 后续改进

1. **增量下载**：支持工具链的增量更新
2. **多镜像加速**：设置全球镜像节点
3. **Docker 支持**：提供预配置的 Docker 镜像
4. **云构建**：集成云构建服务（AWS CodeBuild, GitHub Actions）
5. **自动化测试**：添加单元测试和集成测试
6. **性能监控**：监控编译时间和二进制大小

---

## 10. 参考资料

- [WebRTC Native Code](https://webrtc.googlesource.com/src/)
- [GN Reference](https://gn.googlesource.com/gn/)
- [Ninja Build System](https://ninja-build.org/)
- [Android NDK](https://developer.android.com/ndk)
- [Xcode Command Line Tools](https://developer.apple.com/xcode/)

---

**文档版本**: v1.0.0
**最后更新**: 2026-01-12
**作者**: WebRTC 团队
**许可**: MIT License
