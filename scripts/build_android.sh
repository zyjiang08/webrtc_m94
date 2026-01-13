#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 检测 HOST 平台
case "$(uname -s)" in
    Linux*)     HOST_PLATFORM="linux-x64";;
    Darwin*)    HOST_PLATFORM="darwin-x64";;
    MINGW*|MSYS*|CYGWIN*) HOST_PLATFORM="windows-x64";;
    *)          echo "Error: Unsupported HOST platform"; exit 1;;
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
export ANDROID_NDK_HOME="$TOOLCHAIN_DIR/ndk/ndk"

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
gn gen "$OUT_DIR" --args="$GN_ARGS"

# 编译
ninja -C "$OUT_DIR" webrtc

echo "✓ Build complete!"
echo "  Output: $OUT_DIR/obj/libwebrtc.a"
echo "  Output: $OUT_DIR/libjingle_peerconnection_so.so"
