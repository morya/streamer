# Screen Capture & Streaming Tool

A Windows screen capture tool that captures screen regions and streams via SRT/RTMP protocols with high-performance capture and encoding.

## Features

- **High-performance screen capture** using DXcam (60+ FPS)
- **Dynamic region selection** (1/4, 1/2, full screen)
- **Real-time preview** with red dashed overlay
- **H.264 hardware encoding** (NVENC)
- **SRT (priority) and RTMP streaming** support
- **Configuration persistence** in user data directory
- **Always-on-top control panel** with modern UI

## System Requirements

- **Operating System**: Windows 10/11 64-bit
- **Python**: 3.11+ (recommended: 3.11.9)
- **Graphics**: NVIDIA GPU with NVENC support (for hardware encoding)
- **Memory**: 4GB RAM minimum, 8GB recommended

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd streamer
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate
```

### 3. Install Dependencies
This project uses **uv** for dependency management (faster alternative to pip). All dependencies are defined in `pyproject.toml`.

```bash
# Install uv (if not already installed)
pip install uv

# Install all dependencies (core + Windows-specific)
uv pip install --system .
uv pip install --system .[windows]

# For development and building:
uv pip install --system .[dev,build]

# Note: requirements.txt is provided for compatibility but may be outdated
# Always use uv pip install with pyproject.toml for accurate dependency resolution
```

### 4. Run the Application
```bash
python src/main.py
```

## Project Structure

```
src/
├── main.py              # Application entry point
├── ui/                  # UI components
│   ├── main_window.py   # Main window implementation
│   └── widgets/         # Custom widgets
├── core/                # Core functionality
│   ├── capture.py       # Screen capture module
│   ├── encoder.py       # Video encoding module
│   └── streamer.py      # Streaming module
├── config/              # Configuration management
│   ├── manager.py       # Config loading/saving
│   ├── models.py        # Config models (Pydantic)
│   └── schema.py        # Config validation (legacy)
├── resources/           # Icons, fonts, etc.
└── utils/               # Utility functions
```

## Usage

### Basic Streaming
1. Launch the application
2. Select capture region using +/- buttons
3. Choose bitrate (1Mbps, 2Mbps, 5Mbps, 8Mbps, or Custom)
4. Select streaming protocol (SRT or RTMP)
5. Enter stream URL (e.g., `rtmp://server/live/stream` or `srt://server:9000`)
6. Click "Start Streaming"

### Region Selection
- **+ button**: Increase capture region size
- **- button**: Decrease capture region size
- Regions cycle through: 1/4 screen → 1/2 screen → Full screen

### Protocols
- **SRT**: Secure Reliable Transport (low latency, error correction)
- **RTMP**: Real-Time Messaging Protocol (widely supported)

## Development

### Setting Up Development Environment
```bash
# Install development dependencies
pip install black ruff pytest pytest-qt

# Format code
black src/

# Lint code
ruff check src/
ruff format src/

# Run tests
pytest tests/
```

### Building for Distribution
```bash
# Build with Nuitka (recommended)
python -m nuitka --standalone --onefile --windows-console-mode=disable --enable-plugin=pyside6 --output-dir=dist src/main.py

# Build with PyInstaller
pyinstaller --onefile --windowed --hidden-import=PySide6 --add-data="resources;resources" src/main.py
```

## Dependencies

### Core Dependencies
- **PySide6** (6.8.x): Qt-based GUI framework
- **dxcam** (0.5.x): High-performance Windows screen capture
- **vidgear[core]** (0.3.x): Video processing and streaming
- **numpy** (1.24.x): Numerical computing
- **opencv-python** (4.9.x): Computer vision library
- **appdirs** (1.4.x): Platform-specific directory paths

### Development Dependencies
- **black**: Code formatting
- **ruff**: Code linting and formatting
- **pytest**: Testing framework
- **pytest-qt**: Qt testing utilities

## Configuration

Configuration files are stored in the user's application data directory:
- **Windows**: `%APPDATA%\screen-streamer\`
- **macOS**: `~/Library/Application Support/screen-streamer/`
- **Linux**: `~/.local/share/screen-streamer/`

## Troubleshooting

### Common Issues

1. **"ImportError: No module named 'dxcam'"**
   - Ensure you're on Windows 10/11 64-bit
   - Run `pip install dxcam` manually

2. **"Failed to start capture"**
   - Check if another application is using the screen capture
   - Run as administrator if needed

3. **"Encoder initialization failed"**
   - Verify NVIDIA GPU with NVENC support is available
   - Update NVIDIA graphics drivers

4. **"Stream connection failed"**
   - Verify stream URL is correct
   - Check firewall settings
   - Ensure streaming server is running

## License

[Specify your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues and feature requests, please use the [GitHub Issues](https://github.com/yourusername/screen-streamer/issues) page.