#!/usr/bin/env python3
"""
工具链下载和验证脚本
"""

import json
import os
import sys
import hashlib
import urllib.request
import zipfile
import shutil

def load_deps():
    """加载 DEPS.json"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    deps_file = os.path.join(root_dir, 'DEPS.json')

    with open(deps_file, 'r') as f:
        return json.load(f), root_dir

def calculate_sha256(filepath):
    """计算文件 SHA256"""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()

def download_file(url, filepath):
    """下载文件并显示进度"""
    print(f"Downloading {url}...")

    def report_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        sys.stdout.write(f"\rProgress: {percent:.1f}%")
        sys.stdout.flush()

    urllib.request.urlretrieve(url, filepath, report_progress)
    print("\nDownload complete!")

def extract_zip(zip_path, extract_dir):
    """解压 zip 文件"""
    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("Extraction complete!")

def setup_toolchain(platform, root_dir, deps):
    """设置指定平台的工具链"""
    if platform not in deps['toolchains']:
        print(f"Error: Unknown platform '{platform}'")
        print(f"Available platforms: {', '.join(deps['toolchains'].keys())}")
        return False

    toolchain_info = deps['toolchains'][platform]
    url = toolchain_info.get('url', '')
    local_path = toolchain_info.get('local_path', '')
    expected_sha256 = toolchain_info.get('sha256', '')

    # 创建目录
    toolchains_dir = os.path.join(root_dir, 'toolchains')
    platform_dir = os.path.join(toolchains_dir, platform)
    downloads_dir = os.path.join(root_dir, 'downloads')

    os.makedirs(downloads_dir, exist_ok=True)
    os.makedirs(toolchains_dir, exist_ok=True)

    # 检查是否已存在
    if os.path.exists(platform_dir) and os.listdir(platform_dir):
        print(f"✓ Toolchain already exists at: {platform_dir}")
        print("  Use --force to re-download")
        return True

    # 检查本地路径
    if local_path and os.path.exists(local_path):
        print(f"Found local toolchain at: {local_path}")
        print(f"Creating symlink: {platform_dir} -> {local_path}")

        # 创建符号链接
        if os.path.exists(platform_dir):
            if os.path.islink(platform_dir):
                os.unlink(platform_dir)
            else:
                shutil.rmtree(platform_dir)

        os.symlink(local_path, platform_dir)
        print(f"\n✓ Toolchain setup complete for {platform}!")
        print(f"  Location: {platform_dir} -> {local_path}")
        return True

    # 检查 URL
    if not url or url.startswith("file://"):
        print("=" * 60)
        print("TOOLCHAIN SETUP REQUIRED")
        print("=" * 60)
        print(f"\nThe {platform} toolchain is configured to use local path:")
        print(f"  {local_path}")
        print("\nBut the path does not exist.")
        print("\nPlease ensure the toolchain is available at the configured location.")
        return False

    # 下载文件
    filename = os.path.basename(url)
    zip_path = os.path.join(downloads_dir, filename)

    if os.path.exists(zip_path):
        print(f"Toolchain already downloaded: {zip_path}")
    else:
        download_file(url, zip_path)

    # 验证 SHA256（如果提供）
    if expected_sha256 and expected_sha256 != "TODO":
        print("Verifying checksum...")
        actual_sha256 = calculate_sha256(zip_path)

        if actual_sha256 != expected_sha256:
            print(f"Error: Checksum mismatch!")
            print(f"Expected: {expected_sha256}")
            print(f"Actual:   {actual_sha256}")
            return False

        print("Checksum verified!")

    # 解压
    if os.path.exists(platform_dir):
        print(f"Removing existing toolchain directory: {platform_dir}")
        shutil.rmtree(platform_dir)

    extract_zip(zip_path, platform_dir)

    print(f"\n✓ Toolchain setup complete for {platform}!")
    print(f"  Location: {platform_dir}")

    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 download_toolchain.py <platform>")
        print("Platforms: linux, android, all")
        sys.exit(1)

    platform = sys.argv[1]
    deps, root_dir = load_deps()

    if platform == 'all':
        platforms = list(deps['toolchains'].keys())
        for p in platforms:
            if not setup_toolchain(p, root_dir, deps):
                print(f"\nNote: {p} toolchain setup incomplete.")
                print("Please follow the manual setup instructions above.\n")
    else:
        if not setup_toolchain(platform, root_dir, deps):
            print("\nNote: Toolchain setup incomplete.")
            print("Please follow the manual setup instructions above.\n")

if __name__ == '__main__':
    main()
