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

def setup_toolchain(host_platform, root_dir, deps):
    """设置指定 HOST 平台的工具链"""
    # 过滤掉非平台键
    available_hosts = [k for k in deps['toolchains'].keys() if k not in ['note', 'current_host']]

    if host_platform not in available_hosts:
        print(f"Error: Unknown HOST platform '{host_platform}'")
        print(f"Available HOST platforms: {', '.join(available_hosts)}")
        return False

    toolchain_info = deps['toolchains'][host_platform]
    url = toolchain_info.get('url', '')
    local_path = toolchain_info.get('local_path', '')
    expected_sha256 = toolchain_info.get('sha256', '')
    status = toolchain_info.get('status', 'configured')

    # 检查是否未配置
    if status == 'not_configured':
        print(f"⚠ {host_platform} toolchain is not configured yet.")
        print(f"  This is a placeholder for future support.")
        print(f"  Expected location: {local_path}")
        return True  # 不算错误，只是未配置

    # 创建目录
    toolchains_dir = os.path.join(root_dir, 'toolchains')
    platform_dir = os.path.join(toolchains_dir, host_platform)
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
        print(f"\n✓ Toolchain setup complete for {host_platform}!")
        print(f"  Location: {platform_dir} -> {local_path}")
        return True

    # 检查 URL
    if not url or url.startswith("file://"):
        print("=" * 60)
        print("TOOLCHAIN SETUP REQUIRED")
        print("=" * 60)
        print(f"\nThe {host_platform} HOST toolchain is configured to use local path:")
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

    print(f"\n✓ Toolchain setup complete for {host_platform} HOST!")
    print(f"  Location: {platform_dir}")

    return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 download_toolchain.py <host_platform>")
        print("HOST platforms: linux-x64, darwin-x64, windows-x64, all")
        print("\nNote: Toolchains are organized by HOST platform (where you run the compiler)")
        sys.exit(1)

    host_platform = sys.argv[1]
    deps, root_dir = load_deps()

    if host_platform == 'all':
        # 只处理实际的 HOST 平台配置
        hosts = [k for k in deps['toolchains'].keys() if k not in ['note', 'current_host']]
        print(f"Setting up toolchains for all HOST platforms: {', '.join(hosts)}\n")
        for h in hosts:
            if not setup_toolchain(h, root_dir, deps):
                print(f"\nNote: {h} toolchain setup incomplete.")
                print("Please follow the manual setup instructions above.\n")
    else:
        if not setup_toolchain(host_platform, root_dir, deps):
            print("\nNote: Toolchain setup incomplete.")
            print("Please follow the manual setup instructions above.\n")

if __name__ == '__main__':
    main()
