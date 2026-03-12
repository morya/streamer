#!/usr/bin/env python3
"""
PyInstaller build script for Screen Streaming Tool.

Alternative build method using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def build_with_pyinstaller() -> bool:
    """Build the application using PyInstaller.

    Returns:
        True if build successful, False otherwise
    """
    print("Building Screen Streaming Tool with PyInstaller...")

    # Configuration
    app_name = "ScreenStreamer"
    src_dir = Path(__file__).parent.parent
    dist_dir = Path("dist")
    build_dir = Path("build")
    spec_file = Path(f"{app_name}.spec")

    # Clean previous builds
    if dist_dir.exists():
        print(f"Cleaning previous distribution: {dist_dir}")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        print(f"Cleaning previous build: {build_dir}")
        shutil.rmtree(build_dir)
    if spec_file.exists():
        print(f"Cleaning spec file: {spec_file}")
        spec_file.unlink()

    # Create spec file content
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Add hidden imports for PySide6 and other libraries
hiddenimports = [
    'PySide6',
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'numpy',
    'numpy.core._multiarray_umath',
    'numpy.lib.format',
    'cv2',
    'dxcam',
    'vidgear',
    'vidgear.gears',
    'appdirs',
]

# Collect data files
datas = []

# Add PySide6 translation files
try:
    import PySide6
    pyside6_dir = os.path.dirname(PySide6.__file__)
    translations_dir = os.path.join(pyside6_dir, 'translations')
    if os.path.exists(translations_dir):
        for file in os.listdir(translations_dir):
            if file.endswith('.qm'):
                datas.append((os.path.join(translations_dir, file), 'PySide6/translations'))
except ImportError:
    pass

# Add icon if exists
icon_path = None
if os.path.exists('resources/icon.ico'):
    icon_path = 'resources/icon.ico'

a = Analysis(
    ['{src_dir / "main.py"}'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='{app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='{app_name}',
)
'''

    # Write spec file
    with open(spec_file, "w", encoding="utf-8") as f:
        f.write(spec_content)

    print(f"Created spec file: {spec_file}")

    # PyInstaller command
    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        str(spec_file)
    ]

    print(f"Running command: {' '.join(pyinstaller_cmd)}")

    try:
        # Run PyInstaller
        result = subprocess.run(
            pyinstaller_cmd, check=True, capture_output=True, text=True)
        print("Build output:")
        print(result.stdout)

        if result.stderr:
            print("Build warnings/errors:")
            print(result.stderr)

        # Check if executable was created
        exe_path = dist_dir / app_name / \
            f"{app_name}.exe" if os.name == "nt" else dist_dir / app_name / app_name
        
        if exe_path.exists():
            print(f"\n✅ Build successful!")
            print(f"Executable: {exe_path}")
            print(f"Size: {exe_path.stat().st_size / (1024*1024):.2f} MB")

            # Copy FFmpeg binaries if available
            copy_ffmpeg_binaries(dist_dir / app_name)

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


def create_installer_script() -> None:
    """Create Inno Setup installer script."""
    print("\nCreating Inno Setup installer script...")

    iss_content = '''; Inno Setup Script for Screen Streamer
; Generated by build script

#define MyAppName "Screen Streamer"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ScreenStreamer"
#define MyAppURL "https://github.com/yourusername/screen-streamer"
#define MyAppExeName "ScreenStreamer.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={{autopf}}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=installer\output
OutputBaseFilename=ScreenStreamer-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ScreenStreamer\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  // Check for FFmpeg in system PATH
  if not Exec('ffmpeg', '-version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if MsgBox('FFmpeg was not found in your system PATH. The application requires FFmpeg for streaming. Do you want to continue installation?', mbConfirmation, MB_YESNO) = IDNO then
    begin
      Result := False;
    end
    else
    begin
      Result := True;
    end;
  end
  else
  begin
    Result := True;
  end;
end;
'''

    iss_dir = Path("installer")
    iss_dir.mkdir(exist_ok=True)

    with open(iss_dir / "setup.iss", "w", encoding="utf-8") as f:
        f.write(iss_content)

    print(f"Inno Setup script created: {iss_dir / 'setup.iss'}")

    # Create license file
    license_content = '''Screen Streamer
Copyright © 2024 ScreenStreamer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. In no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the software or the use or other dealings in the software.

Third-party libraries:
- PySide6: LGPL v3
- FFmpeg: LGPL v2.1/GPL v2
- dxcam: MIT License
- vidgear: MIT License
- numpy: BSD License
- OpenCV: Apache 2.0 License
- appdirs: MIT License
'''

    with open(iss_dir / "LICENSE.txt", "w", encoding="utf-8") as f:
        f.write(license_content)


def main() -> None:
    """Main build function."""
    print("=" * 60)
    print("Screen Streaming Tool - PyInstaller Build Script")
    print("=" * 60)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller available")
    except ImportError:
        print("❌ PyInstaller not installed. Install with: pip install pyinstaller")
        sys.exit(1)

    # Build with PyInstaller
    if build_with_pyinstaller():
        # Create installer script
        create_installer_script()

        print("\n" + "=" * 60)
        print("Build completed successfully!")
        print("Next steps:")
        print("1. Download FFmpeg binaries to 'ffmpeg/' directory")
        print("2. Run Inno Setup to create installer: iscc installer/setup.iss")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("Build failed!")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
