# 基础架构选型与版本指定

## 编程语言与运行环境
- Python 3.11+ (推荐3.11.9，稳定且对PySide6支持最佳)
- 运行环境：Windows 10/11 64位

## 核心依赖库及版本（生产环境锁定版本）

### GUI框架
- PySide6 == 6.8.x (最新稳定版，如6.8.3) - 提供Qt 6.8+的全部功能，支持WebEngine集成[citation:1]

### 屏幕捕获
- dxcam == 0.5.x (最新版) - Windows平台高性能屏幕捕获库，支持240+ FPS，是替代MSS的最佳选择
- vidgear[core] == 0.3.x - 封装了ScreenGear组件，自动使用DXcam后端，提供简洁的捕获接口

### 视频编码与推流
- FFmpeg (6.1.1或更高版本，需包含libx264、libx265、libsrt、librtmp支持)
- vidgear[writer] - 提供WriteGear组件，封装FFmpeg编码和推流功能

### SRT/RTMP支持
- FFmpeg需编译启用libsrt和librtmp模块
- 如需要Python层控制，可选用pyrtmp (0.3.1) 或 aiortc，但优先通过FFmpeg实现[citation:8]

### 其他工具库
- numpy (1.24.x) - 图像数据处理
- opencv-python (4.9.x) - 图像格式转换（如需）
- appdirs (1.4.x) - 获取用户配置目录路径

## 开发工具链
- 包管理：pip + requirements.txt (生产环境锁定版本)
- 版本控制：Git
- IDE推荐：VS Code / PyCharm

## 打包工具选型
- Nuitka (推荐) - 对PySide6支持更好，打包后体积小（约15-20MB），启动快[citation:4]
  - 配合插件：--enable-plugin=pyside6
- PyInstaller (备选) - 使用--hidden-import处理PySide6模块依赖[citation:4][citation:9]
- UPX (可选) - 进一步压缩可执行文件体积[citation:4]

## 安装包制作
- Inno Setup (6.2+) - 轻量、稳定，与PySide6应用兼容性好
- 或 NSIS (3.0+) - 功能强大，学习曲线略陡