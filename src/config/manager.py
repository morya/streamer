"""
Configuration management for the screen streaming application using Pydantic.
"""

import json
import os
from typing import Any, Dict, Optional
from pathlib import Path

import appdirs
from pydantic import ValidationError

from .models import AppConfig


class ConfigManager:
    """Manages application configuration loading and saving using Pydantic."""
    
    APP_NAME = "screen-streamer"
    CONFIG_FILENAME = "config.json"
    
    def __init__(self) -> None:
        """Initialize configuration manager."""
        self.config_dir = Path(appdirs.user_data_dir(self.APP_NAME))
        self.config_file = self.config_dir / self.CONFIG_FILENAME
        self.config: AppConfig = AppConfig.default()
        
    def load(self) -> bool:
        """Load configuration from file.
        
        Returns:
            True if configuration loaded successfully, False otherwise
        """
        try:
            if not self.config_file.exists():
                # Create default config file
                self._ensure_config_dir()
                self.save()
                return True
                
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                
            # Parse with Pydantic
            self.config = AppConfig.model_validate(loaded_data)
            return True
            
        except (json.JSONDecodeError, IOError, OSError, ValidationError) as e:
            print(f"Failed to load configuration: {e}")
            # Use default configuration
            self.config = AppConfig.default()
            return False
            
    def save(self) -> bool:
        """Save configuration to file.
        
        Returns:
            True if configuration saved successfully, False otherwise
        """
        try:
            self._ensure_config_dir()
            
            # Convert to dict and save as JSON
            config_dict = self.config.model_dump()
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
                
            return True
            
        except (IOError, OSError, ValidationError) as e:
            print(f"Failed to save configuration: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot notation key.
        
        Args:
            key: Dot notation key (e.g., "capture.region")
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                if hasattr(value, k):
                    value = getattr(value, k)
                elif isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value
        except (AttributeError, KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot notation key.
        
        Args:
            key: Dot notation key (e.g., "capture.region")
            value: Value to set
        """
        keys = key.split('.')
        
        # Convert config to dict for manipulation
        config_dict = self.config.model_dump()
        current = config_dict
        
        # Navigate to the nested dictionary
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
            
        # Set the value
        current[keys[-1]] = value
        
        # Re-validate with Pydantic
        try:
            self.config = AppConfig.model_validate(config_dict)
        except ValidationError as e:
            print(f"Failed to set configuration value: {e}")
            raise
        
    def _ensure_config_dir(self) -> None:
        """Ensure configuration directory exists."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
    # Convenience methods for common configuration access
    
    def get_stream_url(self) -> str:
        """Get the last used stream URL."""
        return self.config.streaming.last_url
        
    def set_stream_url(self, url: str) -> None:
        """Set the last used stream URL."""
        self.config.streaming.last_url = url
        self.save()
        
    def get_capture_region(self) -> str:
        """Get the capture region setting."""
        return self.config.capture.region
        
    def set_capture_region(self, region: str) -> None:
        """Set the capture region setting."""
        self.config.capture.region = region
        self.save()
        
    def get_bitrate(self) -> str:
        """Get the encoding bitrate setting."""
        return self.config.encoding.bitrate
        
    def set_bitrate(self, bitrate: str) -> None:
        """Set the encoding bitrate setting."""
        self.config.encoding.bitrate = bitrate
        self.save()
        
    def get_protocol(self) -> str:
        """Get the streaming protocol setting."""
        return self.config.encoding.protocol
        
    def set_protocol(self, protocol: str) -> None:
        """Set the streaming protocol setting."""
        self.config.encoding.protocol = protocol
        self.save()
        
    def get_window_position(self) -> list:
        """Get the window position setting."""
        return self.config.ui.window_position
        
    def set_window_position(self, x: int, y: int) -> None:
        """Set the window position setting."""
        self.config.ui.window_position = [x, y]
        self.save()
        
    def is_always_on_top(self) -> bool:
        """Check if window should be always on top."""
        return self.config.ui.always_on_top
        
    def set_always_on_top(self, enabled: bool) -> None:
        """Set always on top setting."""
        self.config.ui.always_on_top = enabled
        self.save()
        
    def get_fps(self) -> int:
        """Get the capture FPS setting."""
        return self.config.capture.fps
        
    def set_fps(self, fps: int) -> None:
        """Set the capture FPS setting."""
        self.config.capture.fps = fps
        self.save()
        
    def get_preset(self) -> str:
        """Get the encoding preset setting."""
        return self.config.encoding.preset
        
    def set_preset(self, preset: str) -> None:
        """Set the encoding preset setting."""
        self.config.encoding.preset = preset
        self.save()
        
    def get_theme(self) -> str:
        """Get the UI theme setting."""
        return self.config.ui.theme
        
    def set_theme(self, theme: str) -> None:
        """Set the UI theme setting."""
        self.config.ui.theme = theme
        self.save()
        
    def get_auto_start(self) -> bool:
        """Get the auto-start streaming setting."""
        return self.config.streaming.auto_start
        
    def set_auto_start(self, enabled: bool) -> None:
        """Set the auto-start streaming setting."""
        self.config.streaming.auto_start = enabled
        self.save()