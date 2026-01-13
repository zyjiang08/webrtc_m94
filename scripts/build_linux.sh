#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 检测 HOST 平台
case "$(uname -s)" in
    Linux*)     HOST_PLATFORM="linux-x64";;
    Darwin*)    HOST_PLATFORM="darwin-x64";;
    *)          echo "Error: Linux build only supported on Linux/macOS HOST"; exit 1;;
esac

echo "HOST platform: $HOST_PLATFORM"

# 检查工具链
TOOLCHAIN_DIR="$ROOT_DIR/toolchains/$HOST_PLATFORM"
if [ ! -d "$TOOLCHAIN_DIR" ]; then
    echo "Error: $HOST_PLATFORM toolchain not found!"
    echo "Please run: python3 scripts/download_toolchain.py $HOST_PLATFORM"
    exit 1
fi

# 设置环境变量
export PATH="$TOOLCHAIN_DIR/build-tools:$PATH"

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
gn gen "$OUT_DIR" --args="$GN_ARGS"

# 编译
ninja -C "$OUT_DIR" webrtc

echo "✓ Build complete!"
echo "  Output: $OUT_DIR/obj/libwebrtc.a"
