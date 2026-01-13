# llvm-build-android 目录问题说明

## 问题描述

在 LLS-Player 源码目录 (`/home/harry/work/LLS-Player/LLS-Player/src/build_android.sh`) 中，脚本引用了 `llvm-build-android` 目录，但该目录不存在。

## 原因分析

### 目录结构对比

#### 1. LLS-Player 源码目录结构
```
/home/harry/work/LLS-Player/LLS-Player/src/
├── api/
├── audio/
├── build/
├── build_android.sh
├── BUILD.gn
├── call/
├── media/
├── modules/
├── pc/
├── rtc_base/
├── rtd/                    # LLS-Player 特有目录
├── third_party/
│   └── http/              # 仅包含 http 目录
└── video/
```

#### 2. WebRTC 编译目录结构
```
/home/harry/work/LLS-Player/webrtc.compile/src/
├── api/
├── audio/
├── build/
├── build_android.sh
├── BUILD.gn
├── third_party/
│   ├── android_ndk/       # Android NDK
│   ├── llvm-build/        # LLVM 构建工具
│   ├── llvm-libc/
│   ├── boringssl/
│   ├── abseil-cpp/
│   └── ... (完整的 WebRTC 依赖)
└── ...
```

### 脚本差异

#### LLS-Player 源码中的 build_android.sh (第 8-11 行)
```bash
cd $ROOT_DIR/third_party
rm -rf llvm-build
ln -s $ROOT_DIR/third_party/llvm-build-android llvm-build
cd $ROOT_DIR
```

这段代码的作用：
1. 进入 `third_party` 目录
2. 删除现有的 `llvm-build` 目录
3. 创建符号链接：`llvm-build` -> `llvm-build-android`
4. 返回根目录

#### WebRTC 编译目录中的 build_android.sh (第 8-11 行)
```bash
# cd $ROOT_DIR/third_party
# rm -rf llvm-build
# ln -s $ROOT_DIR/third_party/llvm-build-android llvm-build
cd $ROOT_DIR
```

这段代码已被注释掉，因为：
- WebRTC 编译目录已经包含完整的 `third_party/llvm-build` 目录
- 不需要创建符号链接

## 为什么找不到 llvm-build-android 目录

### 1. LLS-Player 是精简的源码仓库

LLS-Player 源码仓库只包含：
- 修改过的 WebRTC 核心代码
- LLS-Player 特有的代码（如 `rtd/` 目录）
- 最小化的依赖（`third_party/http/`）

**不包含**：
- 完整的 WebRTC 第三方依赖
- LLVM 构建工具
- Android NDK
- 其他编译工具链

### 2. WebRTC 编译目录是完整的构建环境

WebRTC 编译目录 (`/home/harry/work/LLS-Player/webrtc.compile/src/`) 包含：
- 完整的 WebRTC 源码
- 所有第三方依赖（`third_party/`）
- 构建工具链（GN, Ninja, LLVM 等）
- Android NDK

### 3. llvm-build-android 的用途

`llvm-build-android` 目录应该包含：
- 针对 Android 平台的 LLVM 编译器工具链
- 用于交叉编译 Android 目标的工具

在 WebRTC 编译目录中，这个功能由 `third_party/llvm-build/` 提供，因此不需要单独的 `llvm-build-android` 目录。

## 解决方案

### 方案 1: 使用 WebRTC 编译目录（推荐）

**当前状态**：已经在使用，且编译成功。

在 `/home/harry/work/LLS-Player/webrtc.compile/src/` 目录下编译：
```bash
cd /home/harry/work/LLS-Player/webrtc.compile/src
./build_android.sh arm64
```

**优点**：
- 包含完整的构建环境
- 已经修复了 Python 3.12 兼容性问题
- 脚本已经适配（注释掉了 llvm-build-android 相关代码）

### 方案 2: 修改 LLS-Player 源码中的脚本

如果需要在 LLS-Player 源码目录编译，需要：

1. **注释掉符号链接创建代码**：

编辑 `/home/harry/work/LLS-Player/LLS-Player/src/build_android.sh`：
```bash
# cd $ROOT_DIR/third_party
# rm -rf llvm-build
# ln -s $ROOT_DIR/third_party/llvm-build-android llvm-build
cd $ROOT_DIR
```

2. **复制完整的 third_party 目录**：
```bash
cp -r /home/harry/work/LLS-Player/webrtc.compile/src/third_party/* \
      /home/harry/work/LLS-Player/LLS-Player/src/third_party/
```

**注意**：这会占用大量磁盘空间（约 10+ GB）。

### 方案 3: 创建符号链接到 WebRTC 编译目录

在 LLS-Player 源码目录中创建符号链接：
```bash
cd /home/harry/work/LLS-Player/LLS-Player/src
mv third_party third_party.backup
ln -s /home/harry/work/LLS-Player/webrtc.compile/src/third_party third_party
```

**优点**：
- 节省磁盘空间
- 共享构建工具链

**缺点**：
- 两个仓库耦合在一起
- 可能导致混淆

## 推荐的工作流程

### 开发流程

1. **修改代码**：在 LLS-Player 源码目录修改
   ```bash
   cd /home/harry/work/LLS-Player/LLS-Player/src
   # 编辑代码...
   ```

2. **同步到编译目录**：
   ```bash
   # 同步修改的文件到 WebRTC 编译目录
   rsync -av --exclude='third_party' \
             /home/harry/work/LLS-Player/LLS-Player/src/ \
             /home/harry/work/LLS-Player/webrtc.compile/src/
   ```

3. **编译**：在 WebRTC 编译目录编译
   ```bash
   cd /home/harry/work/LLS-Player/webrtc.compile/src
   ./build_android.sh arm64
   ```

### 为什么这样设计

这种分离设计的原因：
1. **源码仓库轻量化**：便于版本控制和分发
2. **编译环境独立**：避免将大量第三方依赖提交到 Git
3. **灵活性**：可以使用不同版本的构建工具链

## 相关文件

- [build-troubleshooting.md](build-troubleshooting.md) - 编译问题排查指南
- [CLAUDE.md](../CLAUDE.md) - 代码库开发指南

## 总结

- **llvm-build-android 目录不存在**是正常的，因为 LLS-Player 源码仓库是精简版本
- **应该在 WebRTC 编译目录**（`/home/harry/work/LLS-Player/webrtc.compile/src/`）进行编译
- **LLS-Player 源码目录**主要用于代码开发和版本控制
- 两个目录的 `build_android.sh` 脚本已经适配各自的环境

## 更新日志

- **2026-01-12**: 创建文档，说明 llvm-build-android 目录问题
