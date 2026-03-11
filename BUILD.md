# Build Instructions

This project uses GitHub Actions for automated Windows builds.

## Build Configuration

### Dependencies
The project uses `uv` for dependency management. Key dependencies:

- **Runtime**: dxcam, PySide6, vidgear, numpy, opencv-python
- **Build**: nuitka (for Windows executable)
- **Development**: black, ruff, mypy, pytest

### Local Build (for testing)
```bash
# Install dependencies
uv pip install .
uv pip install .[build]

# Run build script
python src/installer/build-nuitka.py
```

## GitHub Actions Workflow

The `.github/workflows/ci.yml` file defines the automated build process:

### Triggers
- Push to `main` branch
- Pull requests to `main` branch
- Manual trigger via GitHub UI

### Jobs
1. **Test** (Ubuntu): Runs linting, type checking, and tests on Python 3.11 and 3.12
2. **Build Windows** (Windows): Builds Windows executable using Nuitka

### Build Process
1. Sets up Python 3.11 (for PySide6 compatibility)
2. Installs dependencies using `uv`
3. Runs Nuitka build script
4. Creates portable package with README
5. Uploads artifacts:
   - `ScreenStreamer.exe`: Standalone executable
   - `ScreenStreamer-Portable-Windows.zip`: Portable package

### Artifacts
- Available for 30 days in GitHub Actions
- Automatically attached to releases when pushing to `main`

## System Requirements for Built Executable

- **OS**: Windows 10/11 64-bit (version 1890 or later)
- **RAM**: 4GB minimum
- **GPU**: NVIDIA GPU with NVENC support (recommended for hardware encoding)
- **Additional**: FFmpeg required for SRT/RTMP streaming

## Notes

- The build uses Nuitka for best PySide6 compatibility
- Windows console is disabled for cleaner UI
- Portable package includes all dependencies except FFmpeg
- No code signing is applied (as requested)