"""
Unit tests for configuration management module with Pydantic.
"""

import json
import tempfile
import os
from pathlib import Path
import pytest
from pydantic import ValidationError

from config.manager import ConfigManager
from config.models import AppConfig, CaptureConfig, EncodingConfig, StreamingConfig, UIConfig


class TestConfigManager:
    """Test configuration manager functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        # Create temporary directory for test configs
        self.temp_dir = tempfile.mkdtemp()
        self.original_app_name = ConfigManager.APP_NAME
        ConfigManager.APP_NAME = "test-screen-streamer"
        
    def teardown_method(self):
        """Cleanup test environment."""
        ConfigManager.APP_NAME = self.original_app_name
        
    def test_default_config(self):
        """Test default configuration values."""
        config = ConfigManager()
        
        # Load default config
        config.load()
        
        # Check default values
        assert config.get("capture.region") == "full"
        assert config.get("capture.fps") == 60
        assert config.get("encoding.bitrate") == "2Mbps"
        assert config.get("encoding.protocol") == "rtmp"
        assert config.get("streaming.last_url") == ""
        assert config.get("streaming.auto_start") is False
        
    def test_save_and_load(self):
        """Test configuration save and load."""
        config = ConfigManager()
        
        # Set some values
        config.set("capture.region", "1/2")
        config.set("encoding.bitrate", "5Mbps")
        config.set("streaming.last_url", "rtmp://test.com/live")
        
        # Save configuration
        assert config.save() is True
        
        # Create new config instance and load
        config2 = ConfigManager()
        assert config2.load() is True
        
        # Verify loaded values
        assert config2.get("capture.region") == "1/2"
        assert config2.get("encoding.bitrate") == "5Mbps"
        assert config2.get("streaming.last_url") == "rtmp://test.com/live"
        
    def test_get_set_methods(self):
        """Test get and set methods with dot notation."""
        config = ConfigManager()
        
        # Test setting values
        config.set("capture.region", "1/4")
        config.set("ui.window_position", [100, 200])
        
        # Test getting values
        assert config.get("capture.region") == "1/4"
        assert config.get("ui.window_position") == [100, 200]
        assert config.get("non.existent.key", "default") == "default"
        
    def test_convenience_methods(self):
        """Test convenience methods."""
        config = ConfigManager()
        
        # Test stream URL methods
        config.set_stream_url("srt://test.com:9000")
        assert config.get_stream_url() == "srt://test.com:9000"
        
        # Test region methods
        config.set_capture_region("1/2")
        assert config.get_capture_region() == "1/2"
        
        # Test bitrate methods
        config.set_bitrate("8Mbps")
        assert config.get_bitrate() == "8Mbps"
        
        # Test protocol methods
        config.set_protocol("srt")
        assert config.get_protocol() == "srt"
        
        # Test window position methods
        config.set_window_position(150, 250)
        assert config.get_window_position() == [150, 250]
        
        # Test always on top methods
        config.set_always_on_top(False)
        assert config.is_always_on_top() is False
        
        # Test FPS methods
        config.set_fps(30)
        assert config.get_fps() == 30
        
        # Test preset methods
        config.set_preset("medium")
        assert config.get_preset() == "medium"
        
        # Test theme methods
        config.set_theme("light")
        assert config.get_theme() == "light"
        
        # Test auto-start methods
        config.set_auto_start(True)
        assert config.get_auto_start() is True


class TestPydanticModels:
    """Test Pydantic configuration models."""
    
    def test_valid_config_model(self):
        """Test validation of valid configuration with Pydantic."""
        valid_config = AppConfig(
            capture=CaptureConfig(region="full", fps=60),
            encoding=EncodingConfig(bitrate="2Mbps", protocol="rtmp", preset="fast"),
            streaming=StreamingConfig(last_url="rtmp://test.com/live", auto_start=False),
            ui=UIConfig(window_position=[100, 100], always_on_top=True, theme="dark")
        )
        
        # Should not raise ValidationError
        assert valid_config.capture.region == "full"
        assert valid_config.encoding.bitrate == "2Mbps"
        assert valid_config.streaming.last_url == "rtmp://test.com/live"
        assert valid_config.ui.window_position == [100, 100]
        
    def test_invalid_config_model(self):
        """Test validation of invalid configuration with Pydantic."""
        # Test invalid region
        with pytest.raises(ValidationError):
            CaptureConfig(region="invalid_region", fps=60)
            
        # Test invalid FPS (too high)
        with pytest.raises(ValidationError):
            CaptureConfig(region="full", fps=300)
            
        # Test invalid bitrate
        with pytest.raises(ValidationError):
            EncodingConfig(bitrate="invalid_bitrate", protocol="rtmp", preset="fast")
            
        # Test invalid protocol
        with pytest.raises(ValidationError):
            EncodingConfig(bitrate="2Mbps", protocol="invalid_protocol", preset="fast")
            
        # Test invalid window position (too few items)
        with pytest.raises(ValidationError):
            UIConfig(window_position=[100], always_on_top=True, theme="dark")
            
        # Test invalid window position (negative coordinates)
        with pytest.raises(ValidationError):
            UIConfig(window_position=[-100, 100], always_on_top=True, theme="dark")
            
        # Test invalid theme
        with pytest.raises(ValidationError):
            UIConfig(window_position=[100, 100], always_on_top=True, theme="invalid_theme")
            
    def test_type_validation(self):
        """Test type validation with Pydantic."""
        # Test wrong type for region
        with pytest.raises(ValidationError):
            CaptureConfig(region=123, fps=60)
            
        # Test wrong type for FPS
        with pytest.raises(ValidationError):
            CaptureConfig(region="full", fps="60")
            
        # Test wrong type for bitrate
        with pytest.raises(ValidationError):
            EncodingConfig(bitrate=2000, protocol="rtmp", preset="fast")
            
        # Test wrong type for protocol
        with pytest.raises(ValidationError):
            EncodingConfig(bitrate="2Mbps", protocol=True, preset="fast")
            
        # Test wrong type for window position
        with pytest.raises(ValidationError):
            UIConfig(window_position="100,200", always_on_top=True, theme="dark")
            
        # Test wrong type for always_on_top
        with pytest.raises(ValidationError):
            UIConfig(window_position=[100, 100], always_on_top="true", theme="dark")
            
        # Test wrong type for theme
        with pytest.raises(ValidationError):
            UIConfig(window_position=[100, 100], always_on_top=True, theme=123)
            
    def test_default_config(self):
        """Test default configuration creation."""
        default_config = AppConfig.default()
        
        assert default_config.capture.region == "full"
        assert default_config.capture.fps == 60
        assert default_config.encoding.bitrate == "2Mbps"
        assert default_config.encoding.protocol == "rtmp"
        assert default_config.encoding.preset == "fast"
        assert default_config.streaming.last_url == ""
        assert default_config.streaming.auto_start is False
        assert default_config.ui.window_position == [100, 100]
        assert default_config.ui.always_on_top is True
        assert default_config.ui.theme == "dark"
        
    def test_model_dump_and_load(self):
        """Test model serialization and deserialization."""
        config = AppConfig(
            capture=CaptureConfig(region="1/2", fps=30),
            encoding=EncodingConfig(bitrate="5Mbps", protocol="srt", preset="medium"),
            streaming=StreamingConfig(last_url="srt://test.com:9000", auto_start=True),
            ui=UIConfig(window_position=[200, 300], always_on_top=False, theme="light")
        )
        
        # Convert to dict
        config_dict = config.model_dump()
        
        # Convert back from dict
        loaded_config = AppConfig.model_validate(config_dict)
        
        # Verify values are preserved
        assert loaded_config.capture.region == "1/2"
        assert loaded_config.capture.fps == 30
        assert loaded_config.encoding.bitrate == "5Mbps"
        assert loaded_config.encoding.protocol == "srt"
        assert loaded_config.encoding.preset == "medium"
        assert loaded_config.streaming.last_url == "srt://test.com:9000"
        assert loaded_config.streaming.auto_start is True
        assert loaded_config.ui.window_position == [200, 300]
        assert loaded_config.ui.always_on_top is False
        assert loaded_config.ui.theme == "light"
        
    def test_extra_fields_forbidden(self):
        """Test that extra fields are forbidden."""
        config_dict = {
            "capture": {
                "region": "full",
                "fps": 60,
                "extra_field": "should_fail"  # Extra field
            },
            "encoding": {
                "bitrate": "2Mbps",
                "protocol": "rtmp",
                "preset": "fast"
            },
            "streaming": {
                "last_url": "",
                "auto_start": False
            },
            "ui": {
                "window_position": [100, 100],
                "always_on_top": True,
                "theme": "dark"
            }
        }
        
        # Should raise ValidationError due to extra field
        with pytest.raises(ValidationError):
            AppConfig.model_validate(config_dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])