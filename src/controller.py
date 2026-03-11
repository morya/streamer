"""
Main controller that integrates all modules for screen streaming.
"""

import threading
import time
from typing import Optional

from ui.main_window import MainWindow
from core.capture import ScreenCapture
from core.streamer import Streamer
from config.manager import ConfigManager


class StreamController:
    """Main controller that coordinates UI, capture, and streaming."""
    
    def __init__(self, main_window: MainWindow, config_manager: ConfigManager) -> None:
        """Initialize the stream controller.
        
        Args:
            main_window: Main window instance
            config_manager: Configuration manager instance
        """
        self.main_window = main_window
        self.config_manager = config_manager
        
        # Initialize modules
        self.capture: Optional[ScreenCapture] = None
        self.streamer: Optional[Streamer] = None
        
        # State variables
        self._is_streaming = False
        self._streaming_thread: Optional[threading.Thread] = None
        self._stats_thread: Optional[threading.Thread] = None
        
        # Performance statistics
        self._current_fps = 0
        self._frame_count = 0
        self._last_stats_time = time.time()
        
        # Connect signals
        self._connect_signals()
        
    def _connect_signals(self) -> None:
        """Connect UI signals to controller methods."""
        self.main_window.region_changed.connect(self._on_region_changed)
        self.main_window.bitrate_changed.connect(self._on_bitrate_changed)
        self.main_window.protocol_changed.connect(self._on_protocol_changed)
        self.main_window.streaming_toggled.connect(self._on_streaming_toggled)
        
    def _on_region_changed(self, region: str) -> None:
        """Handle region change.
        
        Args:
            region: New region ("1/4", "1/2", "full")
        """
        if self._is_streaming and self.streamer:
            # Update region while streaming
            self.streamer.change_region(region)
            
        # Update overlay
        self.main_window.show_overlay()
        
    def _on_bitrate_changed(self, bitrate: str) -> None:
        """Handle bitrate change.
        
        Args:
            bitrate: New bitrate (e.g., "2Mbps")
        """
        if self._is_streaming and self.streamer:
            # Update bitrate while streaming
            self.streamer.change_bitrate(bitrate)
            
    def _on_protocol_changed(self, protocol: str) -> None:
        """Handle protocol change.
        
        Args:
            protocol: New protocol ("SRT" or "RTMP")
        """
        if self._is_streaming and self.streamer:
            # Update protocol while streaming
            self.streamer.change_protocol(protocol.lower())
            
    def _on_streaming_toggled(self, start: bool, stream_url: str) -> None:
        """Handle streaming start/stop.
        
        Args:
            start: True to start streaming, False to stop
            stream_url: Stream URL
        """
        if start:
            self._start_streaming(stream_url)
        else:
            self._stop_streaming()
            
    def _start_streaming(self, stream_url: str) -> bool:
        """Start streaming.
        
        Args:
            stream_url: Stream URL
            
        Returns:
            True if streaming started successfully, False otherwise
        """
        if self._is_streaming:
            return False
            
        try:
            # Get current settings from UI
            region = self.main_window._current_region
            bitrate = self.main_window.bitrate_combo.currentText()
            protocol = self.main_window.protocol_combo.currentText().lower()
            
            # Get screen resolution
            screen_res = self.main_window._screen_width, self.main_window._screen_height
            
            # Initialize capture
            self.capture = ScreenCapture(fps=60)
            
            # Calculate capture region
            capture_region = self.capture.calculate_region(screen_res, region)
            
            # Start capture
            if not self.capture.start_capture(capture_region):
                self.main_window.update_status("Failed to start capture", is_error=True)
                return False
                
            # Initialize streamer
            self.streamer = Streamer()
            
            # Start streaming
            if not self.streamer.start_streaming(
                stream_url=stream_url,
                region=region,
                bitrate=bitrate,
                protocol=protocol
            ):
                self.capture.stop_capture()
                self.main_window.update_status("Failed to start streaming", is_error=True)
                return False
                
            # Start streaming thread
            self._is_streaming = True
            self._streaming_thread = threading.Thread(
                target=self._streaming_loop,
                daemon=True
            )
            self._streaming_thread.start()
            
            # Start stats thread
            self._stats_thread = threading.Thread(
                target=self._stats_loop,
                daemon=True
            )
            self._stats_thread.start()
            
            # Update UI
            self.main_window.update_streaming_status(True, 0, bitrate)
            self.main_window.update_status("Streaming started")
            
            # Hide overlay during streaming
            self.main_window.hide_overlay()
            
            return True
            
        except Exception as e:
            self.main_window.update_status(f"Error starting stream: {str(e)}", is_error=True)
            self._cleanup()
            return False
            
    def _stop_streaming(self) -> None:
        """Stop streaming."""
        if not self._is_streaming:
            return
            
        self._is_streaming = False
        
        # Wait for threads to finish
        if self._streaming_thread and self._streaming_thread.is_alive():
            self._streaming_thread.join(timeout=2.0)
            
        if self._stats_thread and self._stats_thread.is_alive():
            self._stats_thread.join(timeout=1.0)
            
        # Stop modules
        self._cleanup()
        
        # Update UI
        self.main_window.update_streaming_status(False)
        self.main_window.update_status("Streaming stopped")
        
        # Show overlay again
        self.main_window.show_overlay()
        
    def _streaming_loop(self) -> None:
        """Main streaming loop."""
        frame_count = 0
        start_time = time.time()
        
        while self._is_streaming and self.capture and self.streamer:
            try:
                # Capture frame
                frame = self.capture.get_frame()
                if frame is None:
                    time.sleep(0.001)
                    continue
                    
                # Update frame count for FPS calculation
                frame_count += 1
                elapsed = time.time() - start_time
                
                if elapsed >= 1.0:  # Update FPS every second
                    self._current_fps = frame_count / elapsed
                    frame_count = 0
                    start_time = time.time()
                    
                # Stream frame
                # Note: The streamer handles encoding and streaming internally
                
                # Control frame rate
                # DXcam handles FPS control, but we add small delay for safety
                time.sleep(0.001)
                
            except Exception as e:
                print(f"Streaming error: {e}")
                time.sleep(0.01)
                
    def _stats_loop(self) -> None:
        """Statistics update loop."""
        while self._is_streaming:
            try:
                # Update UI with current stats
                if self.streamer:
                    settings = self.streamer.get_current_settings()
                    bitrate = settings.get("bitrate", "")
                    
                    self.main_window.update_streaming_status(
                        True, 
                        int(self._current_fps), 
                        bitrate
                    )
                    
                time.sleep(1.0)  # Update every second
                
            except Exception as e:
                print(f"Stats error: {e}")
                time.sleep(1.0)
                
    def _cleanup(self) -> None:
        """Clean up resources."""
        # Stop streamer
        if self.streamer:
            self.streamer.stop_streaming()
            self.streamer = None
            
        # Stop capture
        if self.capture:
            self.capture.stop_capture()
            self.capture = None
            
    def shutdown(self) -> None:
        """Shutdown the controller and clean up resources."""
        self._stop_streaming()
        self._cleanup()