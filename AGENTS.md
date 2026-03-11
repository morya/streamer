# AGENTS.md - Screen Capture & Streaming Tool

This document provides essential information for AI coding agents working on this Python screen capture and streaming project.

## Project Overview

A Windows screen capture tool that captures screen regions and streams via SRT/RTMP protocols. Features include:
- High-performance screen capture using DXcam (60+ FPS)
- Dynamic region selection (1/4, 1/2, full screen)
- Real-time preview with red dashed overlay
- H.264 hardware encoding (NVENC)
- SRT (priority) and RTMP streaming support
- Configuration persistence in user data directory

## Development Environment

### Python Version
- Python 3.11+ (recommended: 3.11.9 for PySide6 compatibility)

### Operating System
- Windows 10/11 64-bit only (due to DXcam dependency)

### Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

## Build, Lint, and Test Commands

### Package Management
```bash
# Install dependencies
pip install -r requirements.txt

# Generate requirements (if needed)
pip freeze > requirements.txt

# Install development dependencies
pip install black ruff pytest pytest-qt
```

### Linting and Formatting
```bash
# Format code with Black
black src/

# Lint with Ruff
ruff check src/
ruff format src/

# Type checking (if using type hints)
mypy src/
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_capture.py

# Run single test
pytest tests/test_capture.py::TestCapture::test_region_selection

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=src tests/
```

### Building and Packaging
```bash
# Build with Nuitka (recommended)
python -m nuitka --standalone --onefile --windows-console-mode=disable --enable-plugin=pyside6 --output-dir=dist src/main.py

# Build with PyInstaller (alternative)
pyinstaller --onefile --windowed --hidden-import=PySide6 --add-data="resources;resources" src/main.py

# Create installer with Inno Setup
# Requires Inno Setup 6.2+ installed
iscc installer/setup.iss
```

## Code Style Guidelines

### Import Organization
```python
# Standard library imports
import os
import sys
from typing import Optional, List, Dict

# Third-party imports
from PySide6.QtWidgets import QApplication, QMainWindow
import numpy as np
import cv2

# Local imports
from core.capture import ScreenCapture
from ui.main_window import MainWindow
```

### Naming Conventions
- **Classes**: `PascalCase` (e.g., `ScreenCapture`, `MainWindow`)
- **Functions/Methods**: `snake_case` (e.g., `start_streaming`, `get_capture_region`)
- **Variables**: `snake_case` (e.g., `capture_fps`, `stream_url`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_FPS`, `MAX_BITRATE`)
- **Private members**: `_leading_underscore` (e.g., `_internal_state`)

### Type Hints
Always use type hints for function signatures and class attributes:
```python
def capture_region(
    region: Tuple[int, int, int, int],
    fps: int = 60
) -> Optional[np.ndarray]:
    """Capture screen region with specified FPS."""
    pass

class StreamConfig:
    def __init__(self, bitrate: int, protocol: str) -> None:
        self.bitrate: int = bitrate
        self.protocol: str = protocol
```

### Error Handling
- Use specific exception types, not bare `except:` statements
- Log errors with context using the `logging` module
- Provide user-friendly error messages in UI components

```python
import logging

logger = logging.getLogger(__name__)

def start_streaming(self) -> bool:
    try:
        self._encoder.start()
        return True
    except (IOError, ConnectionError) as e:
        logger.error(f"Failed to start streaming: {e}")
        self._show_error_message(f"Streaming failed: {str(e)}")
        return False
    except Exception as e:
        logger.exception("Unexpected error during streaming")
        return False
```

### UI Code (PySide6)
- Use Qt signals and slots for event handling
- Keep UI logic separate from business logic
- Use resource files for icons and assets

```python
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self) -> None:
        self.setWindowTitle("Screen Streamer")
        self.setFixedSize(400, 150)
        
    def _connect_signals(self) -> None:
        self.start_button.clicked.connect(self._on_start_clicked)
        self.region_minus.clicked.connect(self._on_region_minus)
        self.region_plus.clicked.connect(self._on_region_plus)
```

### Performance Considerations
- Use hardware acceleration (NVENC) for encoding
- Minimize memory copies in capture pipeline
- Use Qt timers for UI updates, not busy loops
- Release resources properly in cleanup methods

### Configuration Management
- Store user config in `appdirs.user_data_dir("screen-streamer")`
- Use JSON for configuration files
- Validate config on load with schema validation

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

## Dependencies
Core dependencies (from step2.md):
- PySide6 == 6.8.x
- dxcam == 0.5.x
- vidgear[core] == 0.3.x
- numpy == 1.24.x
- opencv-python == 4.9.x
- appdirs == 1.4.x

Development dependencies:
- black, ruff, mypy (formatting/linting)
- pytest, pytest-qt (testing)
- nuitka, pyinstaller (packaging)

## Testing Guidelines
- Write unit tests for core functionality
- Use pytest fixtures for test setup
- Mock external dependencies (FFmpeg, network)
- Test UI components with pytest-qt
- Include integration tests for capture/stream pipeline

## Packaging Notes
- Target Windows 10/11 64-bit only
- Use Nuitka for best PySide6 compatibility
- Include FFmpeg binaries with SRT/RTMP support
- Create installer with Inno Setup
- Sign executable for Windows Defender compatibility

## Common Tasks for Agents
1. When adding new features, follow existing patterns in similar modules
2. Update requirements.txt when adding dependencies
3. Write tests for new functionality
4. Update configuration schema if adding new settings
5. Follow UI design specifications from step3.md
6. Ensure Windows compatibility for all changes