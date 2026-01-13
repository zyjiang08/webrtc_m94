# WebRTC M94 平台编译能力分析

## 目录
1. [交叉编译概述](#交叉编译概述)
2. [LLVM/Clang 能力](#llvmclang-能力)
3. [各平台编译矩阵](#各平台编译矩阵)
4. [iOS 编译限制](#ios-编译限制)
5. [Windows 编译说明](#windows-编译说明)
6. [推荐的工具链组织](#推荐的工具链组织)

---

## 交叉编译概述

### 术语定义

- **Host (主机平台)**: 运行编译器的操作系统
- **Target (目标平台)**: 编译产物运行的操作系统
- **交叉编译**: Host ≠ Target（例如：在 Linux 上编译 Android）

### WebRTC 支持的平台

| Target 平台 | 架构 | 状态 |
|------------|------|------|
| **Linux** | x86_64, ARM64 | ✅ 完全支持 |
| **Android** | ARM64, ARMv7, x86_64, x86 | ✅ 完全支持 |
| **iOS** | ARM64, x86_64 (模拟器) | ✅ 支持（有限制） |
| **macOS** | x86_64, ARM64 | ✅ 支持 |
| **Windows** | x86_64, ARM64 | ✅ 支持 |

---

## LLVM/Clang 能力

### 当前 llvm-build 分析

**位置**: `third_party/llvm-build/`
**大小**: 195MB
**版本**: Clang 14.0.0

#### 主机平台识别

```bash
$ file third_party/llvm-build/Release+Asserts/bin/clang
clang: ELF 64-bit LSB executable, x86-64, dynamically linked
      interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux
```

**结论**: 当前 llvm-build 是 **Linux x86-64 主机** 版本

#### 目标平台支持

```bash
$ ls third_party/llvm-build/Release+Asserts/lib/clang/14.0.0/lib/
linux/                         # Android 运行时库
aarch64-unknown-fuchsia/       # Fuchsia ARM64
x86_64-unknown-fuchsia/        # Fuchsia x86_64
```

**包含的 Android 运行时库**:
- `libclang_rt.asan-arm-android.so` (ARMv7)
- `libclang_rt.asan-aarch64-android.so` (ARM64)
- `libclang_rt.asan-i686-android.so` (x86)
- `libclang_rt.hwasan-aarch64-android.so` (ARM64 Hardware ASAN)
- `libclang_rt.ubsan_standalone-*-android.so` (Undefined Behavior Sanitizer)

### LLVM 交叉编译能力

Clang 理论上支持以下交叉编译：

| Host 平台 | 可编译 Target | 实际限制 |
|----------|--------------|---------|
| **Linux** | Android, Linux | ✅ 完全支持 |
| **Linux** | iOS, macOS | ⚠️ 技术可行，缺乏 SDK |
| **Linux** | Windows | ⚠️ 可行（MinGW），但推荐原生 |
| **macOS** | iOS, macOS, Android | ✅ 完全支持 |
| **macOS** | Linux | ✅ 可行 |
| **Windows** | Windows, Android | ✅ 完全支持 |
| **Windows** | iOS, macOS | ❌ 不可行（缺乏工具链） |

---

## 各平台编译矩阵

### Linux Host (当前环境)

| Target | 可行性 | 所需工具 | 说明 |
|--------|--------|---------|------|
| **Linux x86_64** | ✅ 原生 | Clang/GCC | 直接编译 |
| **Android (全架构)** | ✅ 交叉 | Android NDK + Clang | **当前支持** |
| **iOS** | ⚠️ 理论可行 | Xcode SDK + Clang | **有重大限制** |
| **macOS** | ⚠️ 理论可行 | macOS SDK | 几乎不可能 |
| **Windows** | ⚠️ 可行 | MinGW-w64 | 不推荐 |

### macOS Host

| Target | 可行性 | 所需工具 | 说明 |
|--------|--------|---------|------|
| **macOS** | ✅ 原生 | Xcode | 直接编译 |
| **iOS** | ✅ 交叉 | Xcode + iOS SDK | **标准方案** |
| **Android** | ✅ 交叉 | Android NDK | 完全支持 |
| **Linux** | ✅ 交叉 | Linux Sysroot | 可行但少用 |

### Windows Host

| Target | 可行性 | 所需工具 | 说明 |
|--------|--------|---------|------|
| **Windows** | ✅ 原生 | MSVC/Clang | 直接编译 |
| **Android** | ✅ 交叉 | Android NDK | 完全支持 |
| **iOS/macOS** | ❌ 不可行 | - | 无法获取工具链 |
| **Linux** | ⚠️ 可行 | WSL/MinGW | 不推荐 |

---

## iOS 编译限制

### 为什么 Linux 难以编译 iOS？

#### 1. **法律和许可限制** ⚖️

**Apple 开发者协议限制**:
- iOS SDK 和 Xcode 仅授权在 macOS 上使用
- 违反许可协议可能导致法律问题
- 企业使用尤其需要注意合规性

#### 2. **技术限制** 🔧

即使获得 iOS SDK，在 Linux 上编译 iOS 也面临：

**缺失的组件**:
```
iOS 编译需要:
├── iOS SDK (frameworks, headers, libraries)
│   ├── UIKit.framework
│   ├── Foundation.framework
│   ├── CoreGraphics.framework
│   └── ... (数百个框架)
├── Code Signing 工具
│   ├── codesign
│   ├── Security.framework
│   └── 需要 Apple 开发者证书
├── Xcode 构建系统
│   ├── xcrun
│   ├── xcodebuild
│   └── 特定构建脚本
└── Metal Compiler (iOS GPU)
    └── 闭源，仅在 macOS 可用
```

**具体问题**:

1. **iOS SDK 不开源**
   - Apple 的框架是闭源的
   - 无法在非 macOS 系统上合法获取

2. **代码签名强制要求**
   - iOS 应用必须签名
   - `codesign` 工具仅在 macOS 上可用
   - 需要 Apple 开发者账号和证书

3. **Metal Shader 编译**
   - iOS 使用 Metal 作为 GPU API
   - Metal 编译器是闭源的
   - WebRTC 的视频渲染可能依赖 Metal

4. **GN 和 WebRTC 构建系统假设**
   - WebRTC 的 iOS 构建脚本假设 macOS 环境
   - 依赖 `xcrun` 查找 SDK 路径
   - 硬编码了许多 macOS 特定的路径

#### 3. **社区尝试和项目** 🌐

**cctools-port / iOS-toolchain**:
- 开源项目尝试在 Linux 上编译 iOS
- 需要自行提取 iOS SDK (违反许可)
- 支持有限，WebRTC 这样的复杂项目几乎不可能

**结论**:
- ❌ **不推荐在 Linux 上编译 iOS WebRTC**
- ✅ **标准方案: 使用 macOS + Xcode**

### iOS 编译标准流程

```bash
# 在 macOS 上
cd webrtc_m94

# 安装 Xcode 和命令行工具
xcode-select --install

# 编译 iOS ARM64 (真机)
./scripts/build_ios.sh arm64

# 编译 iOS x86_64 (模拟器)
./scripts/build_ios.sh x64
```

---

## Windows 编译说明

### Windows 编译 Android

**完全支持** ✅

```
Windows Host → Android Target
需要:
├── Android NDK (Windows 版本)
├── Android SDK
├── Python 3.x (Windows)
├── GN + Ninja (Windows 版本)
└── LLVM/Clang (可选，NDK 自带)
```

**实施步骤**:

1. **下载 Windows 工具链**
   ```powershell
   # Android NDK for Windows
   https://developer.android.com/ndk/downloads

   # Android SDK via Android Studio
   https://developer.android.com/studio

   # Python for Windows
   https://www.python.org/downloads/windows/

   # GN for Windows
   从 depot_tools 获取
   ```

2. **环境配置**
   ```powershell
   # 设置环境变量
   $env:ANDROID_NDK_HOME = "C:\Android\ndk\21.4.7075529"
   $env:ANDROID_SDK_ROOT = "C:\Android\sdk"

   # 添加工具到 PATH
   $env:PATH += ";C:\depot_tools"
   ```

3. **编译命令**
   ```powershell
   # PowerShell 或 CMD
   python scripts\build_android.py arm64
   ```

### Windows 编译 iOS

**不可行** ❌

**原因**:
1. iOS SDK 仅在 macOS 上可用
2. Xcode 不支持 Windows
3. 无法获取合法的 iOS 工具链
4. Apple 不提供 Windows 开发支持

**替代方案**:
- 使用远程 macOS 构建服务器
- 使用 CI/CD (如 GitHub Actions 的 macOS runner)
- 租用 macOS 虚拟机（如 MacStadium, MacinCloud）

### Windows 编译 Linux

**可行但不推荐** ⚠️

**方案 1: WSL2 (推荐)**
```powershell
# 使用 Windows Subsystem for Linux
wsl --install Ubuntu-22.04

# 在 WSL2 中编译
wsl
cd /mnt/c/webrtc_m94
./scripts/build_linux.sh x64
```

**方案 2: MinGW / Cygwin**
- 复杂度高
- 兼容性问题多
- 不推荐用于 WebRTC

---

## 推荐的工具链组织

### 按 Host 平台组织

```
webrtc-toolchains/
├── linux-x64/                    # Linux 主机工具链
│   ├── gn                       # GN (Linux 二进制)
│   ├── ninja                    # Ninja (Linux 二进制)
│   ├── llvm-build/              # Clang 14 (Linux 二进制)
│   │   └── Release+Asserts/
│   │       ├── bin/clang        # ELF 64-bit x86-64
│   │       └── lib/clang/14.0.0/lib/
│   │           ├── linux/       # Android 目标库
│   │           └── fuchsia/     # Fuchsia 目标库
│   └── android/
│       └── ndk/                 # Android NDK
│
├── darwin-x64/                   # macOS Intel 主机工具链
│   ├── gn                       # GN (macOS 二进制)
│   ├── ninja                    # Ninja (macOS 二进制)
│   ├── llvm-build/              # Clang 14 (macOS 二进制)
│   │   └── Release+Asserts/
│   │       ├── bin/clang        # Mach-O 64-bit x86_64
│   │       └── lib/clang/14.0.0/lib/
│   │           ├── darwin/      # iOS/macOS 目标库
│   │           └── linux/       # Android 目标库
│   ├── android/
│   │   └── ndk/                 # Android NDK (macOS)
│   └── ios/
│       └── xcode-sdk/           # iOS SDK (从 Xcode 提取)
│
├── darwin-arm64/                 # macOS Apple Silicon 工具链
│   └── (同上，但二进制是 ARM64)
│
└── windows-x64/                  # Windows 主机工具链
    ├── gn.exe                   # GN (Windows 二进制)
    ├── ninja.exe                # Ninja (Windows 二进制)
    ├── llvm-build/              # Clang 14 (Windows 二进制)
    │   └── Release+Asserts/
    │       ├── bin/clang.exe    # PE32+ x86-64
    │       └── lib/clang/14.0.0/lib/
    │           ├── windows/     # Windows 目标库
    │           └── linux/       # Android 目标库
    └── android/
        └── ndk/                 # Android NDK (Windows)
```

### 当前实际情况

```
当前环境: Linux x86-64

/home/harry/awork/webrtc-toolchains/
├── android/                      # Android 工具链 (3.6GB)
│   ├── gn                       # ← 当前是脚本，应该是 Linux 二进制
│   ├── ninja                    # ✓ Linux 二进制
│   └── ndk/                     # ✓ Android NDK r21
│
├── linux/                        # Linux 工具链 (232KB)
│   ├── gn                       # ← 当前是脚本
│   └── ninja                    # ✓ Linux 二进制
│
└── [建议添加]
    └── llvm-build/               # LLVM 工具链 (195MB)
        └── Release+Asserts/
            ├── bin/clang        # ✓ Linux x86-64 二进制
            └── lib/             # ✓ Android 目标库
```

---

## 推荐方案总结

### 1. 当前 Linux 环境 (已实现)

**支持的编译**:
- ✅ Linux → Linux
- ✅ Linux → Android (全架构)

**工具链组织**:
```bash
# 将 llvm-build 也外置
mv third_party/llvm-build /home/harry/awork/webrtc-toolchains/
ln -s /home/harry/awork/webrtc-toolchains/llvm-build third_party/llvm-build

# 保留 jinja2 (Python 运行时依赖，不是二进制)
# third_party/jinja2/ 保留

# 最终 third_party 大小
# 从 1.4GB (含 llvm-build 195MB)
# 减少到 1.2GB (不含 llvm-build)
```

### 2. 如需支持 iOS (需要 macOS)

**标准流程**:
1. 在 macOS 机器上克隆仓库
2. 安装 Xcode: `xcode-select --install`
3. 使用 macOS 专用工具链
4. 编译: `./scripts/build_ios.sh arm64`

**不推荐**: 在 Linux 上交叉编译 iOS (法律和技术限制)

### 3. 如需支持 Windows

**Windows → Android**:
- 准备 Windows 版本的工具链
- 使用 PowerShell 脚本
- 完全支持

**Windows → iOS**:
- ❌ 不支持
- 使用远程 macOS 构建或 CI/CD

---

## 实施建议

### 短期 (当前项目)

**保持现状，仅支持 Linux Host**:

```json
// DEPS.json
{
  "toolchains": {
    "linux-host": {
      "targets": ["linux", "android"],
      "components": {
        "gn": "linux-x64",
        "ninja": "linux-x64",
        "llvm-build": "linux-x64 (支持 Android 交叉编译)",
        "android-ndk": "适用于 Linux"
      }
    }
  }
}
```

**优势**:
- 简单明确
- 符合当前使用场景
- 工具链大小: 3.6GB + 195MB = 3.8GB

### 长期 (支持多主机平台)

**准备多平台工具链**:

```
webrtc-toolchains/
├── linux-x64-host/      # Linux → Linux, Android
├── darwin-x64-host/     # macOS Intel → macOS, iOS, Android
├── darwin-arm64-host/   # macOS M1/M2 → macOS, iOS, Android
└── windows-x64-host/    # Windows → Windows, Android
```

**DEPS.json 配置**:
```json
{
  "toolchains": {
    "linux-x64": {
      "url": "https://storage.example.com/toolchains/linux-x64-host-v1.0.0.tar.gz",
      "targets": ["linux", "android"]
    },
    "darwin-x64": {
      "url": "https://storage.example.com/toolchains/darwin-x64-host-v1.0.0.tar.gz",
      "targets": ["macos", "ios", "android"]
    },
    "windows-x64": {
      "url": "https://storage.example.com/toolchains/windows-x64-host-v1.0.0.zip",
      "targets": ["windows", "android"]
    }
  }
}
```

---

## 常见问题 FAQ

### Q1: 为什么不能在 Linux 上编译 iOS？

**A**: 主要有两个原因:
1. **法律限制**: iOS SDK 许可禁止在非 macOS 系统上使用
2. **技术限制**: 缺少必需工具（Xcode, codesign, Metal 编译器等）

### Q2: llvm-build 需要针对每个目标平台准备一个吗？

**A**: 不需要。需要针对**主机平台**准备:
- Linux 主机 → Linux llvm-build (可编译 Linux + Android)
- macOS 主机 → macOS llvm-build (可编译 macOS + iOS + Android)
- Windows 主机 → Windows llvm-build (可编译 Windows + Android)

### Q3: Android NDK 是否也区分主机平台？

**A**: 是的，Android NDK 有三个版本:
- `android-ndk-r21e-linux-x86_64.zip` (Linux 主机)
- `android-ndk-r21e-darwin-x86_64.zip` (macOS 主机)
- `android-ndk-r21e-windows-x86_64.zip` (Windows 主机)

但目标平台都是 Android (ARM/ARM64/x86/x86_64)

### Q4: 我能在 Windows WSL2 中编译吗？

**A**: 可以。WSL2 实际是 Linux 环境:
- 使用 Linux 工具链
- 可以编译 Linux 和 Android
- 性能和兼容性都很好

### Q5: CI/CD 如何处理多平台？

**A**: 使用平台特定的 runner:
```yaml
# GitHub Actions 示例
jobs:
  build-android-on-linux:
    runs-on: ubuntu-latest

  build-ios-on-macos:
    runs-on: macos-latest

  build-android-on-windows:
    runs-on: windows-latest
```

---

## 总结

| 编译场景 | 推荐方案 | 工具链要求 |
|---------|---------|----------|
| **Linux → Android** | ✅ 当前方案 | Linux llvm-build + Android NDK |
| **Linux → Linux** | ✅ 当前方案 | Linux llvm-build |
| **Linux → iOS** | ❌ 不推荐 | 不可行 |
| **macOS → iOS** | ✅ 标准方案 | macOS llvm-build + Xcode |
| **macOS → Android** | ✅ 完全支持 | macOS llvm-build + Android NDK |
| **Windows → Android** | ✅ 完全支持 | Windows llvm-build + Android NDK |
| **Windows → iOS** | ❌ 不可行 | 无工具链 |

**当前项目建议**:
- 保持 Linux 主机支持 (Linux + Android)
- 将 `llvm-build` 移至工具链目录
- 保留 `jinja2` 在 third_party (Python 运行时)
- 如需 iOS 支持，在 macOS 环境单独构建

---

**文档版本**: v1.0.0
**更新日期**: 2026-01-13
**作者**: Claude Code
