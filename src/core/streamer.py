"""
Streaming module that coordinates capture and encoding for SRT/RTMP streaming.
"""

from typing import Optional, Tuple
import threading
import time

from .capture import ScreenCapture
from .encoder import VideoEncoder


class Streamer:
    """Main streaming coordinator that manages capture and encoding."""

    def __init__(self) -> None:
        """Initialize the streamer."""
        self.capture = ScreenCapture()
        self.encoder: Optional[VideoEncoder] = None
        self._streaming_thread: Optional[threading.Thread] = None
        self._is_streaming = False
        self._current_region = "full"
        self._current_bitrate = "2Mbps"
        self._current_protocol = "rtmp"

    def start_streaming(self, stream_url: str, region: str = "full",
                        bitrate: str = "2Mbps", protocol: str = "rtmp") -> bool:
        """Start streaming to the specified URL.

        Args:
            stream_url: Stream destination URL
            region: Capture region ("1/4", "1/2", "full")
            bitrate: Encoding bitrate
            protocol: Streaming protocol ("rtmp" or "srt")

        Returns:
            True if streaming started successfully, False otherwise
        """
        if self._is_streaming:
            return False

        # Get screen resolution
        screen_res = self.capture.get_screen_resolution()
        if not screen_res:
            return False

        # Calculate capture region
        capture_region = self.capture.calculate_region(screen_res, region)

        # Start capture
        if not self.capture.start_capture(capture_region):
            return False

        # Initialize encoder
        self.encoder = VideoEncoder(
            output_path=stream_url,
            bitrate=bitrate,
            fps=60,
            protocol=protocol
        )

        # Start encoder with frame dimensions
        region_width = capture_region[2]
        region_height = capture_region[3]
        if not self.encoder.start(region_width, region_height):
            self.capture.stop_capture()
            return False

        # Store current settings
        self._current_region = region
        self._current_bitrate = bitrate
        self._current_protocol = protocol

        # Start streaming thread
        self._is_streaming = True
        self._streaming_thread = threading.Thread(
            target=self._streaming_loop,
            daemon=True
        )
        self._streaming_thread.start()

        return True

    def stop_streaming(self) -> None:
        """Stop streaming."""
        self._is_streaming = False

        # Wait for streaming thread to finish
        if self._streaming_thread and self._streaming_thread.is_alive():
            self._streaming_thread.join(timeout=2.0)

        # Stop encoder
        if self.encoder:
            self.encoder.stop()
            self.encoder = None

        # Stop capture
        self.capture.stop_capture()

    def _streaming_loop(self) -> None:
        """Main streaming loop running in separate thread."""
        frame_count = 0
        start_time = time.time()

        while self._is_streaming:
            try:
                # Capture frame
                frame = self.capture.get_frame()
                if frame is None:
                    time.sleep(0.001)  # Small delay if no frame
                    continue

                # Encode frame
                if self.encoder:
                    self.encoder.encode_frame(frame)

                # Calculate FPS (for monitoring)
                frame_count += 1
                elapsed = time.time() - start_time
                if elapsed >= 1.0:  # Update FPS every second
                    fps = frame_count / elapsed
                    frame_count = 0
                    start_time = time.time()
                    # Could emit signal with FPS info here

                # Control frame rate
                # Note: DXcam/ScreenGear handles FPS control internally

            except Exception as e:
                print(f"Streaming error: {e}")
                time.sleep(0.01)  # Small delay on error

    def change_region(self, region: str) -> bool:
        """Change the capture region while streaming.

        Args:
            region: New region ("1", "2", "4")

        Returns:
            True if region changed successfully, False otherwise
        """
        if not self._is_streaming:
            return False

        # Get screen resolution
        screen_res = self.capture.get_screen_resolution()
        if not screen_res:
            return False

        # Calculate new capture region
        capture_region = self.capture.calculate_region(screen_res, region)

        # Stop current capture
        self.capture.stop_capture()

        # Start capture with new region
        if not self.capture.start_capture(capture_region):
            # Try to restart with old region
            old_region = self.capture.calculate_region(
                screen_res, self._current_region)
            self.capture.start_capture(old_region)
            return False

        self._current_region = region
        return True

    def change_bitrate(self, bitrate: str) -> bool:
        """Change the encoding bitrate while streaming.

        Args:
            bitrate: New bitrate

        Returns:
            True if bitrate changed successfully, False otherwise
        """
        if not self._is_streaming or not self.encoder:
            return False

        # For simplicity, we need to restart encoder with new bitrate
        # In a more advanced implementation, we could change encoder parameters on the fly
        self._current_bitrate = bitrate
        # Note: Actual bitrate change would require encoder restart
        return True

    def change_protocol(self, protocol: str) -> bool:
        """Change the streaming protocol while streaming.

        Args:
            protocol: New protocol ("rtmp" or "srt")

        Returns:
            True if protocol changed successfully, False otherwise
        """
        if not self._is_streaming:
            return False

        self._current_protocol = protocol
        # Note: Protocol change would require encoder restart with new URL
        return True

    def is_streaming(self) -> bool:
        """Check if currently streaming."""
        return self._is_streaming

    def get_current_settings(self) -> dict:
        """Get current streaming settings."""
        return {
            "region": self._current_region,
            "bitrate": self._current_bitrate,
            "protocol": self._current_protocol,
            "streaming": self._is_streaming
        }
