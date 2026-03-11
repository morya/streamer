# FFmpeg Setup for Screen Streaming Tool

This document provides instructions for setting up FFmpeg with the required codecs and protocols for the Screen Streaming Tool.

## Requirements

FFmpeg must be compiled with support for:
- **libx264**: H.264 video encoding
- **libx265**: H.265/HEVC video encoding (optional)
- **libsrt**: SRT protocol support
- **librtmp**: RTMP protocol support
- **NVENC**: NVIDIA hardware encoding (for performance)

## Recommended Version

- **FFmpeg 6.1.1** or higher
- **Windows 10/11 64-bit** compatible

## Installation Options

### Option 1: Pre-built Binaries (Recommended)

1. Download FFmpeg from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. Choose the "full" build which includes most codecs
3. Extract to a directory (e.g., `C:\ffmpeg`)
4. Add to system PATH:
   ```batch
   setx PATH "%PATH%;C:\ffmpeg\bin"
   ```

### Option 2: Build from Source (Advanced)

If you need specific features not in pre-built binaries:

```bash
# Clone FFmpeg repository
git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
cd ffmpeg

# Configure with required features
./configure \
  --enable-gpl \
  --enable-version3 \
  --enable-libx264 \
  --enable-libx265 \
  --enable-libsrt \
  --enable-librtmp \
  --enable-nvenc \
  --enable-cuda \
  --enable-cuvid \
  --extra-cflags=-I/usr/local/cuda/include \
  --extra-ldflags=-L/usr/local/cuda/lib64

# Build and install
make -j$(nproc)
sudo make install
```

## Verification

After installation, verify FFmpeg has the required features:

```bash
ffmpeg -version
```

Check for these lines in the output:
```
configuration: --enable-libx264 --enable-libx265 --enable-libsrt --enable-librtmp --enable-nvenc
```

Verify codec support:
```bash
# Check H.264 support
ffmpeg -codecs | grep h264

# Check SRT support
ffmpeg -protocols | grep srt

# Check RTMP support
ffmpeg -protocols | grep rtmp

# Check NVENC support
ffmpeg -encoders | grep nvenc
```

## Integration with Python Application

The Screen Streaming Tool uses `vidgear` which internally calls FFmpeg. Ensure FFmpeg is in one of these locations:

1. **System PATH** (recommended)
2. **Application directory** (for portable distribution)
3. **Custom path** specified in configuration

### Portable Distribution

For distributing the application as a standalone executable, include FFmpeg binaries:

```
dist/
├── screen-streamer.exe
└── ffmpeg/
    ├── ffmpeg.exe
    ├── ffplay.exe
    └── ffprobe.exe
```

Update the application to use relative paths:
```python
import os

def get_ffmpeg_path():
    """Get FFmpeg executable path."""
    # Try system PATH first
    if os.system("ffmpeg -version >nul 2>&1") == 0:
        return "ffmpeg"
    
    # Try relative path for portable distribution
    app_dir = os.path.dirname(os.path.abspath(__file__))
    ffmpeg_path = os.path.join(app_dir, "ffmpeg", "ffmpeg.exe")
    
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    # Fallback to system PATH
    return "ffmpeg"
```

## SRT Protocol Configuration

### SRT URL Format
```
srt://<hostname>:<port>?mode=caller&latency=200000&maxbw=10000000
```

### Key Parameters
- **mode**: `caller` (client) or `listener` (server)
- **latency**: Buffer size in microseconds (default: 120000)
- **maxbw**: Maximum bandwidth in bytes per second
- **passphrase**: Encryption password (optional)
- **pbkeylen**: Encryption key length (16, 24, or 32)

### Example SRT URLs
```python
# Basic SRT stream
"srt://192.168.1.100:9000?mode=caller"

# SRT with encryption
"srt://example.com:9000?mode=caller&passphrase=MySecret&pbkeylen=16"

# SRT with custom latency
"srt://192.168.1.100:9000?mode=caller&latency=200000"
```

## RTMP Protocol Configuration

### RTMP URL Format
```
rtmp://<server>/<application>/<stream_key>
```

### Common RTMP Servers
- **YouTube Live**: `rtmp://a.rtmp.youtube.com/live2/<stream_key>`
- **Twitch**: `rtmp://live.twitch.tv/app/<stream_key>`
- **Facebook Live**: `rtmp://live-api-s.facebook.com:80/rtmp/<stream_key>`
- **Custom Nginx-RTMP**: `rtmp://your-server/live/stream`

### Example RTMP URLs
```python
# YouTube Live
"rtmp://a.rtmp.youtube.com/live2/abcd-efgh-ijkl-mnop"

# Twitch
"rtmp://live.twitch.tv/app/live_123456789_abcdefghijklmnopqrstuvwxyz"

# Local Nginx-RTMP server
"rtmp://192.168.1.100/live/mystream"
```

## Hardware Encoding (NVENC)

### NVENC Parameters
```python
output_params = {
    "-vcodec": "h264_nvenc",      # Use NVIDIA hardware encoder
    "-preset": "fast",            # Encoding preset
    "-tune": "ll",                # Low latency tuning
    "-rc": "cbr",                 # Constant bitrate
    "-b:v": "2000k",              # Bitrate
    "-profile": "high",           # H.264 profile
    "-level": "4.2",              # H.264 level
    "-g": 60,                     # GOP size (keyframe interval)
    "-bf": 2,                     # B-frames
    "-refs": 3,                   # Reference frames
}
```

### Supported Presets
- `slow` - Best quality, highest latency
- `medium` - Balanced quality/latency
- `fast` - Good quality, low latency (recommended)
- `hp` - High performance
- `hq` - High quality
- `bd` - Blu-ray disk
- `ll` - Low latency
- `llhq` - Low latency high quality
- `llhp` - Low latency high performance

## Troubleshooting

### Common Issues

1. **"FFmpeg not found" error**
   - Verify FFmpeg is in system PATH
   - Check if `ffmpeg -version` works in command prompt
   - Restart terminal/IDE after adding to PATH

2. **"Unsupported codec" error**
   - Ensure FFmpeg is compiled with libx264
   - Use `ffmpeg -codecs` to verify codec support

3. **SRT connection failed**
   - Verify SRT server is running
   - Check firewall settings
   - Ensure correct port is open
   - Verify `mode` parameter (caller/listener)

4. **NVENC not available**
   - Update NVIDIA graphics drivers
   - Verify GPU supports NVENC (GeForce 600+ or Quadro K-series+)
   - Check if FFmpeg was compiled with NVENC support

5. **High latency in streaming**
   - Reduce GOP size (`-g` parameter)
   - Use lower latency preset (`ll` or `llhp`)
   - Adjust SRT latency parameter
   - Check network conditions

### Debug Commands

```bash
# Test FFmpeg installation
ffmpeg -version

# Test SRT connection
ffmpeg -re -i test.mp4 -c copy -f mpegts "srt://localhost:9000?mode=caller"

# Test RTMP connection
ffmpeg -re -i test.mp4 -c copy -f flv "rtmp://localhost/live/test"

# Monitor GPU usage (Windows)
nvidia-smi -l 1

# Check network latency
ping <server-address>
```

## Resources

- [FFmpeg Official Documentation](https://ffmpeg.org/documentation.html)
- [SRT Protocol Documentation](https://github.com/Haivision/srt)
- [NVIDIA Video Codec SDK](https://developer.nvidia.com/nvidia-video-codec-sdk)
- [Vidgear Documentation](https://abhitronix.github.io/vidgear/)