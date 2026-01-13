# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a modified WebRTC codebase (branch M94) for the LLS-Player project. WebRTC is a free, open-source project providing Real-Time Communications (RTC) capabilities. This fork includes LLS-Player specific modifications.

## Build System

This project uses **GN** (Generate Ninja) for build configuration and **Ninja** for compilation.

### Building for Android

Use the `build_android.sh` script in the root directory:

```bash
# Build for specific architecture
./build_android.sh arm64      # ARM 64-bit
./build_android.sh armv7      # ARM 32-bit
./build_android.sh x64        # x86 64-bit
./build_android.sh x86        # x86 32-bit

# Build for all architectures
./build_android.sh --allarch

# Build with shared libraries
./build_android.sh arm64 --enable-shared
```

The script:
- Uses GN to generate build files with args: `target_os="android" rtc_use_h264=true rtc_include_internal_audio_device=false treat_warnings_as_errors=false use_custom_libcxx=false`
- Compiles with Ninja
- Outputs to `out/andorid_<arch>/` directories
- Optionally builds shared libraries (.so) using CMake (when `--enable-shared` is used)
- Requires Android NDK at `third_party/android_ndk`

### Building for Desktop/Other Platforms

```bash
# Generate build files (Debug by default)
gn gen out/Default

# Generate Release build
gn gen out/Default --args='is_debug=false'

# Compile
ninja -C out/Default

# Build specific target
ninja -C out/Default webrtc

# Build everything
ninja all -C out/Default

# Clean build artifacts (keeps GN config)
gn clean out/Default
```

### Common GN Arguments

Key build arguments you can pass via `--args`:
- `is_debug=false` - Release build
- `target_os="android"` - Target Android
- `target_cpu="arm64"` / `"arm"` / `"x64"` / `"x86"` - Target architecture
- `rtc_use_h264=true` - Enable H.264 codec
- `rtc_include_ilbc=true` - Include iLBC audio codec
- `rtc_include_opus=true` - Include Opus audio codec
- `use_libfuzzer=true optimize_for_fuzzing=true` - Build fuzzers

View all available options: `gn args out/Default --list`

## Testing

```bash
# Build and run all tests
ninja -C out/Default

# Specific test targets
ninja -C out/Default rtc_unittests
ninja -C out/Default modules_unittests
ninja -C out/Default peerconnection_unittests
ninja -C out/Default webrtc_perf_tests

# Run a test binary
./out/Default/rtc_unittests
```

## Code Architecture

### Key Directories

- **`api/`** - Public WebRTC API headers and interfaces. This is the stable API surface.
- **`pc/`** - PeerConnection implementation (high-level WebRTC API)
- **`call/`** - Call management and media routing
- **`video/`** - Video engine implementation
- **`audio/`** - Audio engine implementation
- **`modules/`** - Core functional modules:
  - `audio_coding/` - Audio codecs (Opus, iLBC, G.711, etc.)
  - `video_coding/` - Video codecs (VP8, VP9, H.264, AV1)
  - `audio_processing/` - Audio processing (AEC, AGC, NS)
  - `rtp_rtcp/` - RTP/RTCP protocol implementation
  - `pacing/` - Packet pacing
  - `congestion_controller/` - Bandwidth estimation and congestion control
  - `audio_device/` - Audio device abstraction
  - `video_capture/` - Video capture abstraction
- **`media/`** - Media engine (combines audio/video/data)
- **`p2p/`** - P2P networking, ICE, STUN, TURN
- **`rtc_base/`** - Base utilities (threading, logging, networking primitives)
- **`common_audio/`** - Common audio utilities and signal processing
- **`common_video/`** - Common video utilities
- **`system_wrappers/`** - OS abstraction layer
- **`test/`** - Test infrastructure and utilities
- **`examples/`** - Example applications (peerconnection, etc.)
- **`sdk/`** - Platform-specific SDKs (Android, iOS, Objective-C)
- **`net/dcsctp/`** - Data Channel SCTP implementation

### Architecture Patterns

1. **Threading Model**: WebRTC uses multiple threads with specific responsibilities:
   - Network thread - handles all network I/O
   - Worker thread - media processing
   - Signaling thread - API calls and callbacks
   - See `api/g3doc/threading_design.md` for details

2. **Task Queues**: Asynchronous operations use task queues (`api/task_queue/`)

3. **RTC Event Log**: Structured logging for debugging (`logging/`, `api/rtc_event_log/`)

4. **Field Trials**: Runtime configuration system for A/B testing features

5. **Stats Collection**: Comprehensive statistics API (`stats/`, `api/stats/`)

## Coding Style

- Follows **Chromium C++ style guide** (takes precedence over Google C++ style)
- Written in **C++14** (subset compatible with C++17)
- No C++20 designated initializers
- Uses subset of **Abseil** library (see `g3doc/abseil-in-webrtc.md`)
- `.h` and `.cc` files come in pairs (see `g3doc/style-guide/h-cc-pairs.md`)
- Format code with: `git cl format`

## Important Notes

- This is branch **M94** with LLS-Player modifications (see commit 414bcf2405)
- The `third_party/` directory is excluded from git (managed separately)
- Build outputs go to `out/` directory (gitignored)
- Component builds are NOT supported (WebRTC uses static/shared libraries directly)
- The codebase uses GN build files (`BUILD.gn`) throughout
- **Python 3.12+ Compatibility**: jinja2 imports have been fixed to use `collections.abc` (see `docs/build-troubleshooting.md`)
- **Shared Library Build**: The `--enable-shared` option requires `rtd/src` directory with CMakeLists.txt. Most builds only need the static libraries from Ninja

## Development Workflow

1. Make changes to source files
2. Build with `ninja -C out/Default`
3. Run relevant tests
4. Format code: `git cl format`
5. Commit changes

## Example Applications

- **peerconnection_server** - Signaling server for WebRTC clients
- **peerconnection_client** - Example WebRTC client application
- **stunserver** - STUN server implementation
- **turnserver** - TURN server for testing

Build examples: `ninja -C out/Default examples` (if `rtc_build_examples=true`)

## Troubleshooting

If you encounter build issues, see:
- `docs/build-troubleshooting.md` - Common build problems and solutions (Python 3.12 compatibility, CMake issues)
- `docs/llvm-build-android-issue.md` - Explanation of llvm-build-android directory dependencies
- `docs/cross-platform-webrtc-repository-design.md` - Repository design and toolchain architecture
