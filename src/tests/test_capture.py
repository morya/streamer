"""
Unit tests for screen capture module.
"""

import pytest
from unittest.mock import Mock, patch

from core.capture import ScreenCapture


class TestScreenCapture:
    """Test screen capture functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.capture = ScreenCapture(fps=60)
        
    def test_initialization(self):
        """Test capture initialization."""
        assert self.capture.fps == 60
        assert self.capture.current_region is None
        assert self.capture.is_capturing() is False
        
    def test_calculate_region_full_screen(self):
        """Test region calculation for full screen."""
        screen_size = (1920, 1080)
        region = self.capture.calculate_region(screen_size, "4")
        
        assert region == (0, 0, 1920, 1080)
        
    def test_calculate_region_half_screen(self):
        """Test region calculation for half screen."""
        screen_size = (1920, 1080)
        region = self.capture.calculate_region(screen_size, "2")
        
        # Half screen should be centered
        expected_width = 960
        expected_height = 540
        expected_left = (1920 - expected_width) // 2
        expected_top = (1080 - expected_height) // 2
        
        assert region == (expected_left, expected_top, expected_width, expected_height)
        
    def test_calculate_region_quarter_screen(self):
        """Test region calculation for quarter screen."""
        screen_size = (1920, 1080)
        region = self.capture.calculate_region(screen_size, "1")
        
        # Quarter screen should be centered
        expected_width = 480
        expected_height = 270
        expected_left = (1920 - expected_width) // 2
        expected_top = (1080 - expected_height) // 2
        
        assert region == (expected_left, expected_top, expected_width, expected_height)
        
    def test_calculate_region_invalid_type(self):
        """Test region calculation with invalid region type."""
        screen_size = (1920, 1080)
        region = self.capture.calculate_region(screen_size, "invalid")
        
        # Should default to full screen
        assert region == (0, 0, 1920, 1080)
        
    @patch('core.capture.ScreenGear')
    @patch('core.capture.dxcam')
    def test_start_capture_success(self, mock_dxcam, mock_screengear):
        """Test successful capture start."""
        # Mock dxcam
        mock_camera = Mock()
        mock_camera.width = 1920
        mock_camera.height = 1080
        mock_dxcam.create.return_value = mock_camera
        
        # Mock ScreenGear
        mock_screengear_instance = Mock()
        mock_screengear.return_value = mock_screengear_instance
        
        # Start capture
        region = (100, 100, 800, 600)
        result = self.capture.start_capture(region)
        
        assert result is True
        assert self.capture.is_capturing() is True
        assert self.capture.current_region == region
        
        # Verify ScreenGear was called with correct parameters
        mock_screengear.assert_called_once_with(
            backend="dxcam",
            region=region,
            logging=False
        )
        
    @patch('core.capture.ScreenGear')
    def test_start_capture_failure(self, mock_screengear):
        """Test capture start failure."""
        # Make ScreenGear raise an exception
        mock_screengear.side_effect = Exception("Capture failed")
        
        # Start capture
        region = (100, 100, 800, 600)
        result = self.capture.start_capture(region)
        
        assert result is False
        assert self.capture.is_capturing() is False
        
    def test_stop_capture(self):
        """Test capture stop."""
        # Mock camera
        self.capture.camera = Mock()
        
        # Stop capture
        self.capture.stop_capture()
        
        # Verify camera was stopped
        self.capture.camera.stop.assert_called_once()
        assert self.capture.camera is None
        assert self.capture.is_capturing() is False
        
    def test_stop_capture_no_camera(self):
        """Test capture stop when no camera is active."""
        # Should not raise exception
        self.capture.stop_capture()
        
    @patch('core.capture.dxcam')
    def test_get_screen_resolution_success(self, mock_dxcam):
        """Test getting screen resolution successfully."""
        # Mock dxcam
        mock_camera = Mock()
        mock_camera.width = 1920
        mock_camera.height = 1080
        mock_dxcam.create.return_value = mock_camera
        
        resolution = self.capture.get_screen_resolution()
        
        assert resolution == (1920, 1080)
        
    @patch('core.capture.dxcam')
    def test_get_screen_resolution_failure(self, mock_dxcam):
        """Test getting screen resolution when dxcam fails."""
        # Make dxcam raise an exception
        mock_dxcam.create.side_effect = Exception("DXcam error")
        
        resolution = self.capture.get_screen_resolution()
        
        assert resolution is None
        
    def test_get_screen_resolution_no_dxcam(self):
        """Test getting screen resolution when dxcam is not available."""
        # Temporarily remove dxcam
        original_dxcam = self.capture.__module__.dxcam
        self.capture.__module__.dxcam = None
        
        try:
            resolution = self.capture.get_screen_resolution()
            assert resolution is None
        finally:
            # Restore dxcam
            self.capture.__module__.dxcam = original_dxcam
            
    def test_region_sizes_dict(self):
        """Test REGION_SIZES dictionary."""
        assert self.capture.REGION_SIZES == {
            "1": 0.25,
            "2": 0.5,
            "4": 1.0
        }


if __name__ == "__main__":
    pytest.main([__file__, "-v"])