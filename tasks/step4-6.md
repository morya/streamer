## 步骤6：FFmpeg编码与推流模块实现

请使用VidGear的WriteGear组件实现视频编码和推流模块。要求：

    创建Streamer类，封装WriteGear操作

    初始化参数：输出分辨率、码率、推流协议、推流地址

    支持协议：优先SRT，同时兼容RTMP

    FFmpeg输出参数配置：

        编码器：h264_nvenc（硬件编码）

        低延迟优化：-tune zerolatency -preset fast

        码率控制：-rc cbr（恒定码率）

        SRT参数（如适用）：srt://...?mode=caller&latency=200000

        RTMP参数（如适用）：rtmp://...

    实现start()方法：初始化WriteGear，准备接收帧数据

    实现stop()方法：关闭WriteGear，释放资源

    实现write_frame(frame)方法：将捕获的帧送入编码器

    错误处理：网络中断时自动重连机制