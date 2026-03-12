"""
Screen capture module using DXcam for high-performance screen capture.
"""

from typing import Optional, Tuple
import numpy as np

try:
    import dxcam
    from vidgear.gears import ScreenGear
except ImportError:
    dxcam = None
    ScreenGear = None


class ScreenCapture:
    """High-performance screen capture using DXcam."""

    REGION_SIZES = {
        "1": 0.25,
        "2": 0.5,
        "4": 1.0
    }

    def __init__(self, fps: int = 60) -> None:
        """Initialize screen capture.

        Args:
            fps: Target frames per second for capture
        """
        self.fps = fps
        self.current_region: Optional[Tuple[int, int, int, int]] = None
        self.camera: Optional[ScreenGear] = None
        self._is_capturing = False

    def start_capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """Start screen capture.

        Args:
            region: Optional region to capture (left, top, width, height)

        Returns:
            True if capture started successfully, False otherwise
        """
        if self._is_capturing:
            return False

        try:
            # Use ScreenGear with DXcam backend
            stream_params = {
                "backend": "dxcam",
                "region": region,
                "logging": False
            }

            self.camera = ScreenGear(**stream_params)
            self.current_region = region
            self._is_capturing = True
            return True

        except Exception as e:
            print(f"Failed to start capture: {e}")
            return False

    def stop_capture(self) -> None:
        """Stop screen capture."""
        if self.camera:
            self.camera.stop()
            self.camera = None
        self._is_capturing = False

    def get_frame(self) -> Optional[np.ndarray]:
        """Get the next frame from the capture.

        Returns:
            Captured frame as numpy array, or None if no frame available
        """
        if not self.camera or not self._is_capturing:
            return None

        try:
            frame = self.camera.read()
            if frame is None:
                return None
            return frame
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None

    def calculate_region(self, screen_size: Tuple[int, int],
                         region_type: str = "1") -> Tuple[int, int, int, int]:
        """Calculate capture region based on screen size and region type.

        Args:
            screen_size: Tuple of (width, height) of the screen
            region_type: One of "1", "2", "4"

        Returns:
            Tuple of (left, top, width, height) for the capture region
        """
        if region_type not in self.REGION_SIZES:
            region_type = "1"

        scale = self.REGION_SIZES[region_type]
        screen_width, screen_height = screen_size

        region_width = int(screen_width * scale)
        region_height = int(screen_height * scale)

        # Center the region on screen
        left = (screen_width - region_width) // 2
        top = (screen_height - region_height) // 2

        return (left, top, region_width, region_height)

    def get_screen_resolution(self) -> Optional[Tuple[int, int]]:
        """Get the primary screen resolution.

        Returns:
            Tuple of (width, height) or None if failed
        """
        try:
            if dxcam:
                camera = dxcam.create()
                return camera.width, camera.height
            return None
        except Exception:
            return None

    def is_capturing(self) -> bool:
        """Check if capture is currently active."""
        return self._is_capturing
