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

# 转换架构名称（armv7 -> arm）
GN_CPU=$ARCH
if [ "$ARCH" = "armv7" ]; then
    GN_CPU="arm"
fi

# GN 参数
GN_ARGS="target_os=\"android\" target_cpu=\"${GN_CPU}\""
GN_ARGS="$GN_ARGS rtc_use_h264=true"
GN_ARGS="$GN_ARGS rtc_include_internal_audio_device=false"
GN_ARGS="$GN_ARGS treat_warnings_as_errors=false"
GN_ARGS="$GN_ARGS use_custom_libcxx=false"

if [ "$BUILD_TYPE" = "Release" ]; then
    GN_ARGS="$GN_ARGS is_debug=false"
else
    GN_ARGS="$GN_ARGS is_debug=true"
fi

# 生成构建文件
cd "$ROOT_DIR/src"
$ROOT_DIR/toolchains/android/gn gen "$OUT_DIR" --args="$GN_ARGS"

# 编译
$ROOT_DIR/toolchains/android/ninja -C "$OUT_DIR" webrtc

echo "✓ Build complete!"
echo "  Output: $OUT_DIR/obj/libwebrtc.a"
echo "  Output: $OUT_DIR/libjingle_peerconnection_so.so"
