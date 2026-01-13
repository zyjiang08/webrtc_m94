# Android 编译问题排查指南

本文档记录了在编译 WebRTC Android 版本时遇到的问题及解决方案。

## 问题概述

执行 `./build_android.sh arm64 --enable-shared` 时编译失败。

## 问题 1: Python 3.12 兼容性问题

### 错误信息

```
ImportError: cannot import name 'Mapping' from 'collections' (/usr/local/anaconda3/lib/python3.12/collections/__init__.py)
```

### 原因分析

在 Python 3.3+ 版本中，`Mapping` 和 `MutableMapping` 等抽象基类已从 `collections` 模块移动到 `collections.abc` 模块。本项目使用的 jinja2 版本较旧（来自 Chromium 依赖），不兼容 Python 3.12。

具体错误发生在以下文件：
- `third_party/jinja2/tests.py:13`
- `third_party/jinja2/sandbox.py:17`
- `third_party/jinja2/runtime.py:318`
- `third_party/jinja2/utils.py:485`

### 解决方案

修改 jinja2 相关文件，使其兼容 Python 3.3+ 和 Python 3.12+：

#### 1. 修复 `third_party/jinja2/tests.py`

```python
# 原代码（第 11-14 行）
import operator
import re
from collections import Mapping
from jinja2.runtime import Undefined

# 修改为
import operator
import re
try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
from jinja2.runtime import Undefined
```

#### 2. 修复 `third_party/jinja2/sandbox.py`

```python
# 原代码（第 15-18 行）
import types
import operator
from collections import Mapping
from jinja2.environment import Environment

# 修改为
import types
import operator
try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
from jinja2.environment import Environment
```

#### 3. 修复 `third_party/jinja2/runtime.py`

```python
# 原代码（第 316-321 行）
# register the context as mapping if possible
try:
    from collections import Mapping
    Mapping.register(Context)
except ImportError:
    pass

# 修改为
# register the context as mapping if possible
try:
    from collections.abc import Mapping
    Mapping.register(Context)
except ImportError:
    try:
        from collections import Mapping
        Mapping.register(Context)
    except ImportError:
        pass
```

#### 4. 修复 `third_party/jinja2/utils.py`

```python
# 原代码（第 483-488 行）
# register the LRU cache as mutable mapping if possible
try:
    from collections import MutableMapping
    MutableMapping.register(LRUCache)
except ImportError:
    pass

# 修改为
# register the LRU cache as mutable mapping if possible
try:
    from collections.abc import MutableMapping
    MutableMapping.register(LRUCache)
except ImportError:
    try:
        from collections import MutableMapping
        MutableMapping.register(LRUCache)
    except ImportError:
        pass
```

### 验证修复

修复后重新运行编译：

```bash
./build_android.sh arm64 --enable-shared
```

Ninja 编译应该能够成功完成所有 3089 个目标。

## 问题 2: CMake 共享库构建失败

### 错误信息

```
CMake Error: The source directory "/home/harry/work/LLS-Player/webrtc.compile/src/rtd/src" does not exist.
```

### 原因分析

`build_android.sh` 脚本中的 `--enable-shared` 选项会在 Ninja 编译完成后，尝试使用 CMake 构建额外的共享库。脚本中引用了 `rtd/src` 目录（第 53、71、89、106 行），但该目录在当前代码库中不存在。

相关代码位置：`build_android.sh:48-116`（函数定义）和第 133-135、150-152、167-169、184-186 行（函数调用）。

### 解决方案

#### 方案 1: 不使用 --enable-shared 选项（推荐）

如果只需要标准的 WebRTC 库，直接运行：

```bash
./build_android.sh arm64
```

这样会生成以下文件，已经足够使用：
- `out/andorid_arm64/libwebrtc.a` - 静态库
- `out/andorid_arm64/libjingle_peerconnection_so.so` - 共享库

#### 方案 2: 移除 CMake 构建部分

如果确定不需要 rtd 相关的共享库，可以从 `build_android.sh` 中移除 CMake 构建部分：

1. 删除或注释掉函数定义（第 48-116 行）：
   - `build_arm64()`
   - `build_arm32()`
   - `build_x64()`
   - `build_x86()`

2. 删除或注释掉函数调用：
   - 第 133-135 行（arm64 构建）
   - 第 150-152 行（armv7 构建）
   - 第 167-169 行（x64 构建）
   - 第 184-186 行（x86 构建）

#### 方案 3: 提供 rtd 源码

如果需要 rtd 相关的共享库，需要：
1. 创建 `rtd/src` 目录
2. 提供相应的 CMakeLists.txt 文件
3. 提供 rtd 库的源代码

## 编译成功验证

### 检查生成的文件

```bash
# 查看生成的库文件
ls -lh out/andorid_arm64/*.a out/andorid_arm64/*.so

# 查看库文件大小
du -h out/andorid_arm64/libwebrtc.a
du -h out/andorid_arm64/libjingle_peerconnection_so.so
```

### 预期输出

成功编译后应该看到：
- `libwebrtc.a` - WebRTC 静态库（约 200+ MB）
- `libjingle_peerconnection_so.so` - PeerConnection 共享库（约 10+ MB）

## 其他架构编译

修复 Python 兼容性问题后，可以编译其他架构：

```bash
# ARM 32位
./build_android.sh armv7

# x86 64位
./build_android.sh x64

# x86 32位
./build_android.sh x86

# 所有架构
./build_android.sh --allarch
```

## 环境要求

- **Python**: 3.6+ (已修复 3.12 兼容性)
- **GN**: 用于生成构建文件
- **Ninja**: 用于编译
- **Android NDK**: 位于 `third_party/android_ndk`
- **CMake**: 仅在使用 `--enable-shared` 时需要

## 相关文档

- [CLAUDE.md](../CLAUDE.md) - 代码库开发指南
- [WebRTC 官方文档](https://webrtc.googlesource.com/src/+/main/docs/native-code/android/index.md)
- [GN 构建系统](https://gn.googlesource.com/gn/)

## 更新日志

- **2026-01-12**: 修复 Python 3.12 兼容性问题，文档化 CMake 构建问题
