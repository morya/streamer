"""
Configuration models using Pydantic for the screen streaming application.
"""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class CaptureConfig(BaseModel):
    """Capture configuration."""
    region: Literal["1", "2", "4"] = "1"
    fps: int = Field(default=60, ge=1, le=240)

    model_config = ConfigDict(extra="forbid")


class EncodingConfig(BaseModel):
    """Encoding configuration."""
    bitrate: str = Field(default="2Mbps", pattern=r"^\d+Mbps$|^Custom$")
    protocol: Literal["rtmp", "srt"] = "rtmp"
    preset: Literal["ultrafast", "superfast", "veryfast", "faster",
                    "fast", "medium", "slow", "slower", "veryslow"] = "fast"

    model_config = ConfigDict(extra="forbid")

    @field_validator("bitrate")
    @classmethod
    def validate_bitrate(cls, v: str) -> str:
        """Validate bitrate format."""
        if v == "Custom":
            return v
        if not v.endswith("Mbps"):
            raise ValueError("Bitrate must end with 'Mbps' or be 'Custom'")
        try:
            value = int(v[:-4])
            if value <= 0:
                raise ValueError("Bitrate value must be positive")
        except ValueError:
            raise ValueError("Bitrate must be in format '\\d+Mbps' or 'Custom'")
        return v


class StreamingConfig(BaseModel):
    """Streaming configuration."""
    last_url: str = ""
    auto_start: bool = False

    model_config = ConfigDict(extra="forbid")


class UIConfig(BaseModel):
    """UI configuration."""
    window_position: List[int] = Field(default_factory=lambda: [100, 100])
    always_on_top: bool = True
    theme: Literal["dark", "light", "system"] = "dark"

    model_config = ConfigDict(extra="forbid")

    @field_validator("window_position")
    @classmethod
    def validate_window_position(cls, v: List[int]) -> List[int]:
        """Validate window position."""
        if len(v) != 2:
            raise ValueError("Window position must have exactly 2 coordinates")
        if v[0] < 0 or v[1] < 0:
            raise ValueError("Window position coordinates must be non-negative")
        return v


class AppConfig(BaseModel):
    """Main application configuration."""
    capture: CaptureConfig = Field(default_factory=CaptureConfig)
    encoding: EncodingConfig = Field(default_factory=EncodingConfig)
    streaming: StreamingConfig = Field(default_factory=StreamingConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def default(cls) -> "AppConfig":
        """Create default configuration."""
        return cls(
            capture=CaptureConfig(),
            encoding=EncodingConfig(),
            streaming=StreamingConfig(),
            ui=UIConfig()
        )
