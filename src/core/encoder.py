"""
Video encoding module using hardware acceleration (NVENC).
"""

from typing import Optional, Dict, Any
import subprocess
import threading
import queue
import time

try:
    import numpy as np
    from vidgear.gears import WriteGear
except ImportError:
    np = None
    WriteGear = None


class VideoEncoder:
    """H.264 hardware encoder using NVENC."""

    BITRATE_MAP = {
        "500k": "500k",
        "1Mbps": "1000k",
        "2Mbps": "2000k",
        "5Mbps": "5000k",
        "8Mbps": "8000k"
    }

    def __init__(self, output_path: str, bitrate: str = "2Mbps",
                 fps: int = 60, protocol: str = "rtmp") -> None:
        """Initialize video encoder.

        Args:
            output_path: Output file path or stream URL
            bitrate: Target bitrate (e.g., "2Mbps")
            fps: Target frames per second
            protocol: Streaming protocol ("rtmp" or "srt")
        """
        self.output_path = output_path
        self.bitrate = bitrate
        self.fps = fps
        self.protocol = protocol.lower()
        self.encoder: Optional[WriteGear] = None
        self._is_encoding = False
        self._frame_queue = queue.Queue(maxsize=30)
        self._encoding_thread: Optional[threading.Thread] = None

    def start(self, width: int, height: int) -> bool:
        """Start the encoder.

        Args:
            width: Frame width
            height: Frame height

        Returns:
            True if encoder started successfully, False otherwise
        """
        if self._is_encoding:
            return False

        try:
            # Configure output parameters for FFmpeg
            output_params = {
                "-input_framerate": self.fps,
                "-vcodec": "h264_nvenc",  # Hardware encoding using NVENC
                "-preset": "fast",        # Fast preset for low latency
                "-tune": "ll",            # Low latency tuning
                "-rc": "cbr",             # Constant bitrate
                "-b:v": self.BITRATE_MAP.get(self.bitrate, "2000k"),
                "-pix_fmt": "bgr24",      # Input pixel format
                "-g": 60,                 # GOP size (keyframe interval)
                "-bf": 2,                 # B-frames
                "-refs": 3,               # Reference frames
                "-profile:v": "high",     # H.264 profile
                "-level:v": "4.2",        # H.264 level
            }

            # Protocol-specific parameters
            if self.protocol == "rtmp":
                output_params.update({
                    "-f": "flv",          # RTMP uses FLV container
                    "-flvflags": "no_duration_filesize"
                })
            elif self.protocol == "srt":
                output_params.update({
                    "-f": "mpegts",       # SRT uses MPEG-TS container
                    "-muxdelay": "0.1",   # Reduced muxing delay
                    "-fflags": "+genpts"  # Generate presentation timestamps
                })

            # Initialize WriteGear with output parameters
            self.encoder = WriteGear(
                output=self.output_path,
                logging=False,
                **output_params
            )

            # Start encoding thread
            self._is_encoding = True
            self._encoding_thread = threading.Thread(
                target=self._encoding_loop,
                daemon=True
            )
            self._encoding_thread.start()

            return True

        except Exception as e:
            print(f"Failed to start encoder: {e}")
            return False

    def stop(self) -> None:
        """Stop the encoder."""
        self._is_encoding = False

        # Wait for encoding thread to finish
        if self._encoding_thread and self._encoding_thread.is_alive():
            self._encoding_thread.join(timeout=2.0)

        # Close encoder
        if self.encoder:
            self.encoder.close()
            self.encoder = None

        # Clear frame queue
        while not self._frame_queue.empty():
            try:
                self._frame_queue.get_nowait()
            except queue.Empty:
                break

    def encode_frame(self, frame: np.ndarray) -> bool:
        """Queue a frame for encoding.

        Args:
            frame: Frame to encode as numpy array

        Returns:
            True if frame was queued successfully, False otherwise
        """
        if not self._is_encoding or not self.encoder:
            return False

        try:
            # Non-blocking put with timeout
            self._frame_queue.put(frame, block=False, timeout=0.1)
            return True
        except queue.Full:
            # Drop frame if queue is full (maintain real-time performance)
            return False
        except Exception:
            return False

    def _encoding_loop(self) -> None:
        """Main encoding loop running in separate thread."""
        while self._is_encoding:
            try:
                # Get frame from queue with timeout
                frame = self._frame_queue.get(timeout=0.1)

                # Encode frame
                if self.encoder and frame is not None:
                    self.encoder.write(frame)

            except queue.Empty:
                # No frames to encode, continue
                continue
            except Exception as e:
                print(f"Encoding error: {e}")
                # Small delay to prevent tight loop on error
                time.sleep(0.01)

    def is_encoding(self) -> bool:
        """Check if encoder is currently active."""
        return self._is_encoding

    def get_bitrate_bps(self) -> int:
        """Get bitrate in bits per second."""
        bitrate_str = self.BITRATE_MAP.get(self.bitrate, "2000k")
        # Convert from kbps to bps
        if bitrate_str.endswith("k"):
            return int(bitrate_str[:-1]) * 1000
        return 2000000  # Default 2Mbps
