# WebRTC M94 详细使用文档

本文档提供 WebRTC M94 的完整使用说明，包括编译、配置和集成。

## 目录

1. [仓库结构](#仓库结构)
2. [工具链管理](#工具链管理)
3. [编译配置](#编译配置)
4. [构建脚本](#构建脚本)
5. [集成到项目](#集成到项目)
6. [高级用法](#高级用法)

## 仓库结构

```
webrtc_m94/
├── src/                    # WebRTC 核心源码
│   ├── api/               # 公共 API
│   ├── audio/             # 音频模块
│   ├── video/             # 视频模块
│   ├── modules/           # 功能模块
│   ├── pc/                # PeerConnection
│   ├── rtc_base/          # 基础库
│   └── ...
├── third_party/           # 第三方依赖 (1.4GB)
│   ├── abseil-cpp/        # C++ 基础库
│   ├── boringssl/         # SSL/TLS
│   ├── libvpx/            # VP8/VP9 编解码器
│   ├── opus/              # Opus 音频
│   └── ...
├── build/                 # 构建配置
├── scripts/               # 构建和管理脚本
│   ├── build_android.sh   # Android 构建脚本
│   ├── build_linux.sh     # Linux 构建脚本
│   ├── download_toolchain.py  # 工具链管理
│   └── test_build.sh      # 构建测试
├── toolchains/            # 工具链（符号链接到本地）
│   ├── android/           # -> /home/harry/awork/webrtc-toolchains/android
│   └── linux/             # -> /home/harry/awork/webrtc-toolchains/linux
├── out/                   # 编译输出（不提交）
├── docs/                  # 文档
├── README.md              # 项目说明
├── DEPS.json              # 依赖配置
└── CLAUDE.md              # 开发指南
```

### 仓库大小统计

| 目录 | 大小 | 说明 |
|------|------|------|
| `src/` | ~800MB | WebRTC 核心源码 |
| `third_party/` | 374MB | Python 运行时依赖（jinja2等） |
| `build/` | ~50MB | 构建配置文件 |
| `docs/` | <1MB | 文档 |
| **总计** | **~2.2GB** | 源码仓库大小（93% 缩减） |
| 工具链 (Android NDK) | 3.6GB | 独立存储，不在仓库中 |
| 工具链 (Linux) | 232KB | 独立存储，不在仓库中 |
| 工具链 (LLVM) | 195MB | 独立存储，HOST 平台相关 |
| **工具链总计** | **3.8GB** | Linux x86-64 HOST 工具链 |

## 工具链管理

### 工具链位置

工具链存储在独立目录，不随源码仓库分发。

**重要**: 工具链是 HOST 平台相关的（运行编译器的机器），而非 TARGET 平台相关（要编译的目标）。

当前配置为 **Linux x86-64 HOST**，可以编译：
- Linux x64 目标
- Android arm64/armv7/x86/x64 目标

```
/home/harry/awork/webrtc-toolchains/
├── android/               # Android NDK (3.6GB)
│   ├── gn                # GN 构建工具
│   ├── ninja             # Ninja 编译工具
│   └── ndk/              # Android NDK r21
├── linux/                # Linux 工具 (232KB)
│   ├── gn                # GN 构建工具
│   └── ninja             # Ninja 编译工具
└── llvm-build/           # LLVM 编译器 (195MB)
    └── Release+Asserts/
        ├── bin/clang     # Linux x86-64 HOST 二进制
        └── lib/          # Android 目标运行时库
```

### 工具链配置

工具链路径在 `DEPS.json` 中配置：

```json
{
  "toolchains": {
    "android": {
      "local_path": "/home/harry/awork/webrtc-toolchains/android",
      "url": "file:///home/harry/awork/webrtc-toolchains/android"
    },
    "linux": {
      "local_path": "/home/harry/awork/webrtc-toolchains/linux",
      "url": "file:///home/harry/awork/webrtc-toolchains/linux"
    }
  }
}
```

### 设置工具链

```bash
# 为 Android 创建符号链接
python3 scripts/download_toolchain.py android

# 为 Linux 创建符号链接
python3 scripts/download_toolchain.py linux

# 验证工具链
ls -l toolchains/
# 应该看到指向 /home/harry/awork/webrtc-toolchains/ 的符号链接
```

## 编译配置

### GN 构建参数

WebRTC 使用 GN (Generate Ninja) 进行构建配置。常用参数：

#### 平台参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `target_os` | `"android"`, `"linux"` | 目标操作系统 |
| `target_cpu` | `"arm64"`, `"arm"`, `"x64"`, `"x86"` | 目标 CPU 架构 |
| `is_debug` | `true`, `false` | Debug/Release 构建 |

#### WebRTC 专用参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `rtc_use_h264` | `true` | 启用 H.264 编解码器 |
| `rtc_include_internal_audio_device` | `false` | 包含内部音频设备 |
| `treat_warnings_as_errors` | `false` | 警告视为错误 |
| `use_custom_libcxx` | `false` | 使用自定义 libc++ |
| `rtc_include_opus` | `true` | 包含 Opus 编解码器 |
| `rtc_include_ilbc` | `true` | 包含 iLBC 编解码器 |

### Android 编译配置

```bash
# ARM 64-bit (推荐)
target_os="android"
target_cpu="arm64"
rtc_use_h264=true
rtc_include_internal_audio_device=false
treat_warnings_as_errors=false
use_custom_libcxx=false
is_debug=false

# ARM 32-bit
target_cpu="arm"  # armv7

# x86 64-bit (模拟器)
target_cpu="x64"

# x86 32-bit
target_cpu="x86"
```

### Linux 编译配置

```bash
target_os="linux"
target_cpu="x64"
rtc_use_h264=true
treat_warnings_as_errors=false
is_debug=false
```

## 构建脚本

### build_android.sh

Android 构建脚本支持多架构编译。

#### 使用方法

```bash
./scripts/build_android.sh <架构> [构建类型]

# 参数:
#   架构: arm64, armv7, x64, x86
#   构建类型: Release (默认), Debug
```

#### 示例

```bash
# Release 构建 (优化，无调试符号)
./scripts/build_android.sh arm64
./scripts/build_android.sh arm64 Release

# Debug 构建 (包含调试符号)
./scripts/build_android.sh arm64 Debug

# 其他架构
./scripts/build_android.sh armv7
./scripts/build_android.sh x64
./scripts/build_android.sh x86
```

#### 输出文件

```bash
out/android_arm64/
├── obj/
│   └── libwebrtc.a                          # 静态库 (~150MB)
├── libjingle_peerconnection_so.so           # PeerConnection 共享库 (~10MB)
└── args.gn                                  # GN 配置文件
```

### build_linux.sh

Linux 构建脚本。

#### 使用方法

```bash
./scripts/build_linux.sh [架构] [构建类型]

# 参数:
#   架构: x64 (默认)
#   构建类型: Release (默认), Debug
```

#### 示例

```bash
# 默认 x64 Release
./scripts/build_linux.sh

# 显式指定参数
./scripts/build_linux.sh x64 Release

# Debug 构建
./scripts/build_linux.sh x64 Debug
```

#### 输出文件

```bash
out/linux_x64/
├── obj/
│   └── libwebrtc.a                          # 静态库
└── args.gn                                  # GN 配置文件
```

## 集成到项目

### 作为 Git Submodule

推荐将 webrtc_m94 作为 Git submodule 集成：

```bash
# 在您的项目中
cd /path/to/your/project

# 添加 submodule
git submodule add git@github.com:zyjiang08/webrtc_m94.git webrtc

# 初始化和更新
git submodule update --init --recursive
```

### 使用本地路径（临时）

```bash
# 在 .gitmodules 中配置本地路径
[submodule "webrtc"]
    path = webrtc
    url = /home/harry/awork/webrtc_m94_temp
```

### CMake 集成示例

```cmake
# CMakeLists.txt

# 设置 WebRTC 路径
set(WEBRTC_ROOT "${CMAKE_SOURCE_DIR}/webrtc")
set(WEBRTC_OUT_DIR "${WEBRTC_ROOT}/out/android_arm64")

# 添加 WebRTC 静态库
add_library(webrtc STATIC IMPORTED)
set_target_properties(webrtc PROPERTIES
    IMPORTED_LOCATION "${WEBRTC_OUT_DIR}/obj/libwebrtc.a"
)

# 添加 WebRTC 头文件
target_include_directories(your_target PRIVATE
    ${WEBRTC_ROOT}/src
    ${WEBRTC_ROOT}/src/third_party/abseil-cpp
)

# 链接 WebRTC
target_link_libraries(your_target PRIVATE webrtc)
```

### Android.mk 集成示例

```makefile
# Android.mk

LOCAL_PATH := $(call my-dir)

# WebRTC 预编译库
include $(CLEAR_VARS)
LOCAL_MODULE := libwebrtc
LOCAL_SRC_FILES := $(WEBRTC_ROOT)/out/android_$(TARGET_ARCH_ABI)/obj/libwebrtc.a
LOCAL_EXPORT_C_INCLUDES := \
    $(WEBRTC_ROOT)/src \
    $(WEBRTC_ROOT)/src/third_party/abseil-cpp
include $(PREBUILT_STATIC_LIBRARY)

# 您的应用
include $(CLEAR_VARS)
LOCAL_MODULE := your_app
LOCAL_SRC_FILES := your_source.cpp
LOCAL_STATIC_LIBRARIES := libwebrtc
include $(BUILD_SHARED_LIBRARY)
```

## 高级用法

### 增量编译

Ninja 支持增量编译，只重新编译修改的文件：

```bash
# 修改源码后
ninja -C out/android_arm64

# Ninja 会自动检测修改并只编译相关文件
```

### 并行编译

```bash
# 使用所有 CPU 核心
ninja -j$(nproc) -C out/android_arm64

# 限制并行任务数（节省内存）
ninja -j4 -C out/android_arm64
```

### 清理构建

```bash
# 只清理编译产物（保留 GN 配置）
ninja -t clean -C out/android_arm64

# 完全清理（需要重新运行 GN）
rm -rf out/android_arm64

# 清理所有输出
rm -rf out/
```

### 查看依赖关系

```bash
# 查看目标依赖
gn desc out/android_arm64 //webrtc deps

# 查看反向依赖
gn desc out/android_arm64 //webrtc deps --tree

# 生成依赖图
gn desc out/android_arm64 //webrtc deps --format=dot > deps.dot
dot -Tpng deps.dot -o deps.png
```

### 编译特定目标

```bash
# 只编译 rtc_base
ninja -C out/android_arm64 rtc_base:rtc_base

# 编译 PeerConnection
ninja -C out/android_arm64 pc:peerconnection

# 编译测试
ninja -C out/android_arm64 rtc_unittests
```

### 交叉编译

WebRTC 支持交叉编译：

```bash
# 在 Linux 上编译 Android
target_os="android"
target_cpu="arm64"

# 使用 NDK 工具链
# NDK 路径在构建脚本中自动设置
```

## 性能优化

### 编译优化

```bash
# Release 构建（默认）
is_debug=false
is_official_build=true

# 启用 LTO (Link Time Optimization)
use_lto=true

# 优化级别
optimize="speed"  # 或 "size"
```

### 二进制大小优化

```bash
# 移除调试符号
is_debug=false
symbol_level=0

# 优化大小而非速度
optimize="size"

# 移除不需要的编解码器
rtc_include_ilbc=false  # 如果不需要 iLBC
```

## 故障排查

### 常见问题

1. **工具链未找到**
   ```bash
   # 检查符号链接
   ls -l toolchains/

   # 重新创建符号链接
   python3 scripts/download_toolchain.py android
   ```

2. **Python 3.12 兼容性**
   - 已修复 jinja2 导入问题
   - 详见 `docs/build-troubleshooting.md`

3. **内存不足**
   ```bash
   # 限制并行任务
   ninja -j4 -C out/android_arm64
   ```

4. **GN 生成失败**
   ```bash
   # 检查 buildtools
   ls buildtools/linux64/gn

   # 使用系统 GN
   export PATH="/home/harry/work/LLS-Player/depot_tools:$PATH"
   ```

更多故障排查，请参阅：
- `docs/build-troubleshooting.md`
- `docs/llvm-build-android-issue.md`

## 参考资料

- [WebRTC 官方文档](https://webrtc.org/native-code/)
- [GN 参考](https://gn.googlesource.com/gn/)
- [Ninja 构建系统](https://ninja-build.org/)
- [Android NDK](https://developer.android.com/ndk)

## 更新日志

- **v1.0.0** (2026-01-13)
  - 初始版本
  - 支持 Android (arm64, armv7, x64, x86) 和 Linux (x64)
  - 工具链本地化
  - Python 3.12 兼容性修复
  - 仓库大小优化（93% 缩减）
