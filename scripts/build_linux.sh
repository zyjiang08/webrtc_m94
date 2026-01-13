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

# 架构
ARCH=${1:-x64}  # 默认 x64

# 构建类型
BUILD_TYPE=${2:-Release}  # Debug 或 Release

# 输出目录
OUT_DIR="$ROOT_DIR/out/linux_${ARCH}"

echo "Building WebRTC for Linux (${ARCH}, ${BUILD_TYPE})..."

# GN 参数
GN_ARGS="target_os=\"linux\" target_cpu=\"${ARCH}\""
GN_ARGS="$GN_ARGS rtc_use_h264=true"
GN_ARGS="$GN_ARGS treat_warnings_as_errors=false"

if [ "$BUILD_TYPE" = "Release" ]; then
    GN_ARGS="$GN_ARGS is_debug=false"
else
    GN_ARGS="$GN_ARGS is_debug=true"
fi

# 生成构建文件
cd "$ROOT_DIR/src"
$ROOT_DIR/toolchains/linux/gn gen "$OUT_DIR" --args="$GN_ARGS"

# 编译
$ROOT_DIR/toolchains/linux/ninja -C "$OUT_DIR" webrtc

echo "✓ Build complete!"
echo "  Output: $OUT_DIR/obj/libwebrtc.a"
