# WebRTC M94 - Cross-Platform Build

Cross-platform WebRTC repository for LLS-Player project. This is branch M94 with LLS-Player specific modifications.

## Features

- **Minimal Dependencies**: Only ~374MB of Python runtime dependencies (down from 28GB)
- **External Toolchains**: Build tools (3.8GB) packaged separately for easy management
- **Cross-Platform**: Supports Linux and Android builds
- **Clean Architecture**: Follows the design in `docs/cross-platform-webrtc-repository-design.md`
- **HOST Platform**: Current setup is Linux x86-64 host, can compile Linux and Android targets

## Repository Structure

```
webrtc_m94/
├── src/              # WebRTC core source code
├── third_party/      # Python runtime dependencies (~374MB)
│   └── llvm-build -> /home/harry/awork/webrtc-toolchains/llvm-build (symlink)
├── build/            # Build configuration files
├── scripts/          # Build and toolchain management scripts
├── toolchains/       # External build toolchains (symlinks, not in git)
├── out/              # Build outputs (not in git)
└── docs/             # Documentation

External toolchains (organized by HOST platform):
/home/harry/awork/webrtc-toolchains/
├── linux-x64/        # Linux x86-64 HOST (3.8GB, current)
│   ├── build-tools/  # GN, Ninja (232KB)
│   ├── llvm-build/   # LLVM 14.0.0 (195MB)
│   └── ndk/          # Android NDK r21 (3.6GB)
├── darwin-x64/       # macOS HOST (future support)
└── windows-x64/      # Windows HOST (future support)
```

## Quick Start

### 1. Clone the Repository

```bash
git clone git@github.com:zyjiang08/webrtc_m94.git
cd webrtc_m94
```

### 2. Download Toolchain

Toolchains are organized by HOST platform (where you run the compiler):

```bash
# Auto-detect and setup for current HOST
python3 scripts/download_toolchain.py linux-x64    # Linux HOST
python3 scripts/download_toolchain.py darwin-x64   # macOS HOST
python3 scripts/download_toolchain.py windows-x64  # Windows HOST

# Or setup all
python3 scripts/download_toolchain.py all
```

### 3. Build

```bash
# Android ARM64
./scripts/build_android.sh arm64

# Android ARMv7
./scripts/build_android.sh armv7

# Android x64
./scripts/build_android.sh x64

# Linux x64
./scripts/build_linux.sh x64
```

## Build Options

### Android Architectures
- `arm64` - ARM 64-bit (default)
- `armv7` - ARM 32-bit
- `x64` - x86 64-bit
- `x86` - x86 32-bit

### Build Types
- `Release` - Optimized release build (default)
- `Debug` - Debug build with symbols

Example:
```bash
./scripts/build_android.sh arm64 Debug
```

## Output Files

After successful build:

**Android:**
- `out/android_arm64/obj/libwebrtc.a` - Static library
- `out/android_arm64/libjingle_peerconnection_so.so` - Shared library

**Linux:**
- `out/linux_x64/obj/libwebrtc.a` - Static library

## Integration with RTN-Player

This repository is designed to be used as a Git submodule:

```bash
cd /path/to/RTN-Player
git submodule add git@github.com:zyjiang08/webrtc_m94.git webrtc
git submodule update --init --recursive
```

## Requirements

- **Python**: 3.6+ (tested with Python 3.12)
- **Git**: For version control
- **Disk Space**: ~10GB for source + toolchains
- **Memory**: 8GB RAM minimum, 16GB recommended

## Documentation

- [Build Troubleshooting](docs/build-troubleshooting.md) - Common build issues and solutions
- [Repository Design](docs/cross-platform-webrtc-repository-design.md) - Architecture and design decisions
- [CLAUDE.md](CLAUDE.md) - Development guide for Claude Code

## Key Changes from Standard WebRTC

1. **Python 3.12 Compatibility**: Fixed jinja2 imports to use `collections.abc`
2. **Simplified Dependencies**: Removed 26.6GB of unnecessary build tools and test frameworks
3. **External Toolchains**: NDK, SDK, and build tools are now external downloads
4. **LLS-Player Modifications**: Custom changes for LLS-Player integration (commit 414bcf2405)

## Troubleshooting

See [docs/build-troubleshooting.md](docs/build-troubleshooting.md) for common issues:
- Python 3.12 compatibility
- Missing toolchain errors
- Build failures

## License

WebRTC is licensed under a BSD-style license. See [LICENSE](src/LICENSE) for details.

## Version

- **WebRTC Branch**: M94
- **Repository Version**: 1.0.0
- **Last Updated**: 2026-01-13
