#!/usr/bin/env python3
"""
Nuitka build script for Screen Streaming Tool.

Builds a standalone executable with PySide6 support.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def build_with_nuitka() -> bool:
    """Build the application using Nuitka.
    
    Returns:
        True if build successful, False otherwise
    """
    print("Building Screen Streaming Tool with Nuitka...")
    
    # Configuration
    app_name = "ScreenStreamer"
    src_dir = Path(__file__).parent.parent
    dist_dir = Path("dist")
    build_dir = Path("build")
    
    # Clean previous builds
    if dist_dir.exists():
        print(f"Cleaning previous distribution: {dist_dir}")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        print(f"Cleaning previous build: {build_dir}")
        shutil.rmtree(build_dir)
        
    # Create output directory
    dist_dir.mkdir(exist_ok=True)
    
    # Nuitka command
    nuitka_cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--windows-console-mode=disable",
        "--enable-plugin=pyside6",
        "--include-package=vidgear",
        "--include-package=dxcam",
        "--include-package=appdirs",
        "--include-package=numpy",
        "--include-package=cv2",
        "--output-dir=dist",
        "--windows-icon-from-ico=resources/icon.ico" if Path("resources/icon.ico").exists() else "",
        "--product-name=Screen Streamer",
        "--file-version=1.0.0",
        "--product-version=1.0.0",
        "--company-name=ScreenStreamer",
        "--copyright=Copyright © 2024 ScreenStreamer",
        "--nofollow-import-to=*.tests",
        "--nofollow-import-to=*.distutils",
        "--remove-output",
        str(src_dir / "main.py")
    ]
    
    # Remove empty strings from command
    nuitka_cmd = [arg for arg in nuitka_cmd if arg]
    
    print(f"Running command: {' '.join(nuitka_cmd)}")
    
    try:
        # Run Nuitka
        result = subprocess.run(nuitka_cmd, check=True, capture_output=True, text=True)
        print("Build output:")
        print(result.stdout)
        
        if result.stderr:
            print("Build warnings/errors:")
            print(result.stderr)
            
        # Check if executable was created
        exe_name = "main.exe" if os.name == "nt" else "main"
        exe_path = dist_dir / exe_name
        
        if exe_path.exists():
            # Rename to app name
            final_exe = dist_dir / f"{app_name}.exe" if os.name == "nt" else dist_dir / app_name
            shutil.move(exe_path, final_exe)
            
            print(f"\n✅ Build successful!")
            print(f"Executable: {final_exe}")
            print(f"Size: {final_exe.stat().st_size / (1024*1024):.2f} MB")
            
            # Copy FFmpeg binaries if available
            copy_ffmpeg_binaries(dist_dir)
            
            return True
        else:
            print(f"\n❌ Build failed: Executable not found at {exe_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code {e.returncode}")
        print(f"Error output:\n{e.stderr}")
        return False
    except Exception as e:
        print(f"\n❌ Build failed with exception: {e}")
        return False


def copy_ffmpeg_binaries(dist_dir: Path) -> None:
    """Copy FFmpeg binaries to distribution directory.
    
    Args:
        dist_dir: Distribution directory path
    """
    ffmpeg_src = Path("ffmpeg")
    ffmpeg_dst = dist_dir / "ffmpeg"
    
    if ffmpeg_src.exists():
        print(f"Copying FFmpeg binaries from {ffmpeg_src}...")
        
        # Create ffmpeg directory in dist
        ffmpeg_dst.mkdir(exist_ok=True)
        
        # Copy FFmpeg executables
        for exe in ["ffmpeg.exe", "ffplay.exe", "ffprobe.exe"]:
            src_file = ffmpeg_src / exe
            if src_file.exists():
                shutil.copy2(src_file, ffmpeg_dst / exe)
                print(f"  - Copied {exe}")
                
        print(f"FFmpeg binaries copied to {ffmpeg_dst}")
    else:
        print("Note: FFmpeg directory not found. FFmpeg must be in system PATH.")


def create_portable_package(dist_dir: Path) -> None:
    """Create a portable package with all dependencies.
    
    Args:
        dist_dir: Distribution directory path
    """
    print("\nCreating portable package...")
    
    portable_dir = dist_dir / "ScreenStreamer-Portable"
    portable_dir.mkdir(exist_ok=True)
    
    # Copy executable
    exe_name = "ScreenStreamer.exe" if os.name == "nt" else "ScreenStreamer"
    exe_src = dist_dir / exe_name
    if exe_src.exists():
        shutil.copy2(exe_src, portable_dir / exe_name)
        
    # Copy FFmpeg directory if it exists
    ffmpeg_src = dist_dir / "ffmpeg"
    if ffmpeg_src.exists():
        shutil.copytree(ffmpeg_src, portable_dir / "ffmpeg", dirs_exist_ok=True)
        
    # Create README
    readme_content = """# Screen Streamer - Portable Version

## System Requirements
- Windows 10/11 64-bit
- NVIDIA GPU with NVENC support (recommended)
- 4GB RAM minimum

## Usage
1. Run `ScreenStreamer.exe`
2. Configure capture region and streaming settings
3. Enter stream URL and click "Start Streaming"

## FFmpeg
This package includes FFmpeg binaries for SRT/RTMP streaming.
If you have FFmpeg installed system-wide, you can delete the `ffmpeg` folder.

## Troubleshooting
- If streaming fails, ensure FFmpeg is in system PATH
- Update NVIDIA drivers for hardware encoding
- Check firewall settings for network streaming

## Support
For issues and feature requests, visit the project repository.
"""
    
    with open(portable_dir / "README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
        
    print(f"Portable package created: {portable_dir}")


def main() -> None:
    """Main build function."""
    print("=" * 60)
    print("Screen Streaming Tool - Build Script")
    print("=" * 60)
    
    # Check if Nuitka is installed
    try:
        import nuitka
        print(f"Nuitka version: {nuitka.__version__}")
    except ImportError:
        print("❌ Nuitka not installed. Install with: pip install nuitka")
        sys.exit(1)
        
    # Build with Nuitka
    if build_with_nuitka():
        # Create portable package
        create_portable_package(Path("dist"))
        
        print("\n" + "=" * 60)
        print("Build completed successfully!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Build failed!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()