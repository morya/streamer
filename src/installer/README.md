# Installer and Packaging

This directory contains scripts and configuration for packaging the Screen Streaming Tool for distribution.

## Build Options

### Option 1: Nuitka (Recommended)

Nuitka provides better PySide6 compatibility and smaller executable size.

```bash
# Install Nuitka
pip install nuitka

# Run build script
python src/installer/build-nuitka.py
```

Output:
- `dist/ScreenStreamer.exe` - Standalone executable
- `dist/ScreenStreamer-Portable/` - Portable package with FFmpeg

### Option 2: PyInstaller

PyInstaller is an alternative with good Windows support.

```bash
# Install PyInstaller
pip install pyinstaller

# Run build script
python src/installer/build-pyinstaller.py
```

Output:
- `dist/ScreenStreamer/ScreenStreamer.exe` - Application bundle
- `installer/setup.iss` - Inno Setup installer script

## FFmpeg Integration

The application requires FFmpeg for streaming. Two options:

### 1. System-wide FFmpeg
- Install FFmpeg and add to system PATH
- Download from: https://www.gyan.dev/ffmpeg/builds/

### 2. Bundled FFmpeg
- Place FFmpeg binaries in `ffmpeg/` directory:
  ```
  ffmpeg/
  ├── ffmpeg.exe
  ├── ffplay.exe
  └── ffprobe.exe
  ```
- The build scripts will copy these to the distribution

## Creating Installer

### Inno Setup (Windows)

1. Install Inno Setup 6.2+ from: https://jrsoftware.org/isinfo.php
2. Build the application first
3. Run Inno Setup:
   ```bash
   iscc installer/setup.iss
   ```
4. Installer will be created in `installer/output/`

### NSIS (Alternative)

NSIS can be used as an alternative to Inno Setup:
```bash
# Create NSIS script
makensis installer/setup.nsi
```

## Distribution Structure

### Portable Distribution
```
ScreenStreamer-Portable/
├── ScreenStreamer.exe
├── ffmpeg/
│   ├── ffmpeg.exe
│   ├── ffplay.exe
│   └── ffprobe.exe
└── README.txt
```

### Installer Distribution
```
ScreenStreamer-Setup.exe
├── Installs to: C:\Program Files\Screen Streamer\
├── Adds desktop shortcut
├── Adds start menu entry
└── Checks for FFmpeg during installation
```

## Version Management

Update version information in:
1. `src/installer/build-nuitka.py` - `--file-version` and `--product-version`
2. `src/installer/build-pyinstaller.py` - `MyAppVersion` in spec template
3. `installer/setup.iss` - `MyAppVersion`

## Code Signing (Optional)

For Windows Defender compatibility, sign the executable:

```bash
# Using signtool (Windows SDK)
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com ScreenStreamer.exe

# Using osslsigncode (cross-platform)
osslsigncode sign -certs certificate.pem -key private.key -n "Screen Streamer" -i https://yourwebsite.com -t http://timestamp.digicert.com -in ScreenStreamer.exe -out ScreenStreamer-signed.exe
```

## Testing the Build

1. **Standalone test**: Run the executable without Python installed
2. **FFmpeg test**: Verify FFmpeg is accessible
3. **Streaming test**: Test SRT and RTMP streaming
4. **UI test**: Verify all UI components work correctly

## Troubleshooting

### Common Issues

1. **"DLL not found" errors**
   - Ensure all dependencies are included in build
   - Use Dependency Walker to check missing DLLs

2. **PySide6 not loading**
   - Nuitka: Use `--enable-plugin=pyside6`
   - PyInstaller: Add hidden imports for PySide6 modules

3. **FFmpeg not found**
   - Check FFmpeg is in PATH or bundled
   - Test with `ffmpeg -version` in command prompt

4. **Large executable size**
   - Use UPX compression: `--upx` flag in PyInstaller
   - Nuitka automatically optimizes size

5. **Anti-virus false positives**
   - Sign the executable with a code signing certificate
   - Submit to anti-virus vendors for whitelisting

## Continuous Integration

Example GitHub Actions workflow:

```yaml
name: Build and Package

on:
  release:
    types: [created]

jobs:
  build:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install nuitka
        
    - name: Download FFmpeg
      run: |
        curl -L https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z -o ffmpeg.7z
        7z x ffmpeg.7z -offmpeg
        mv ffmpeg/ffmpeg-*-full_build/bin/* ffmpeg/
        
    - name: Build with Nuitka
      run: python src/installer/build-nuitka.py
      
    - name: Create installer
      run: iscc installer/setup.iss
      
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: ScreenStreamer
        path: |
          dist/
          installer/output/
```

## Resources

- [Nuitka Documentation](https://nuitka.net/doc/user-manual.html)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [Inno Setup Documentation](http://www.jrsoftware.org/ishelp/)
- [FFmpeg Windows Builds](https://www.gyan.dev/ffmpeg/builds/)
- [Code Signing Guide](https://docs.microsoft.com/en-us/windows/win32/seccrypto/cryptography-tools)