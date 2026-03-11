#!/usr/bin/env python3
"""
Screen Capture & Streaming Tool - Main Entry Point

A Windows screen capture tool that captures screen regions and streams
via SRT/RTMP protocols with high-performance capture and encoding.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from config.manager import ConfigManager
from core.capture import ScreenCapture
from controller import StreamController


def main() -> None:
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Screen Streamer")
    app.setOrganizationName("ScreenStreamer")
    
    # Initialize configuration
    config = ConfigManager()
    config.load()
    
    # Initialize screen capture to get screen resolution
    capture = ScreenCapture()
    screen_res = capture.get_screen_resolution()
    
    # Create main window
    window = MainWindow()
    window.exit_btn.clicked.connect(app.exit)
    
    # Load configuration into UI
    window.load_configuration(config)
    
    # Set screen resolution if available
    if screen_res:
        window.set_screen_resolution(screen_res[0], screen_res[1])
    
    window.show()
    
    # Create controller
    controller = StreamController(window, config)
    
    # Save configuration and shutdown controller when application closes
    def shutdown():
        window.save_configuration(config)
        controller.shutdown()
    
    app.aboutToQuit.connect(shutdown)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()