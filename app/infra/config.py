# -*- coding: utf-8 -*-
"""
采用Pydantic Settings管理，支持动态路径、跨平台、环境变量、自动校验
配置自动获取项目根目录，可直接迁移部署
"""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings

# 获取当前config.py文件的上一级项目目录
PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMP_VIDEO_PATH = PROJECT_ROOT / 'temp_video'
TEMP_AUDIO_PATH = PROJECT_ROOT / 'temp_audio'

class AppSettings(BaseSettings):
    """
    全局应用配置
    所有参数自带中文描述，IDE自动提示，文档自动生成
    """
    # "socks5://127.0.0.1:10808",
    # "socks5://MaB7HouwTW:wwRLgRouP7@38.49.38.21:13970"
    # ========================== 网络与代理配置 ==========================
    PROXY: str | None = Field(
        default = "socks5://127.0.0.1:10808",
        description="全局网络代理，部署到服务器如不需要可设为 null 或通过环境变量覆盖"
    )
    # ========================== FFmpeg 配置 ==========================
    FFMPEG_PATH: str = Field(
        default= str(PROJECT_ROOT/"tools"/"ffmpeg"/"ffmpeg-8.1-essentials_build"/"bin"),
        description='找到存放ffmpeg执行文件的文件夹'
    )
    # FFmpeg可执行文件完整路径
    FFMPEG_EXEC_PATH: Path = Field(
        default=PROJECT_ROOT/"tools"/"ffmpeg"/"ffmpeg-8.1-essentials_build"/"bin"/"ffmpeg.exe",
        description="FFmpeg工具路径，动态绑定项目根目录，部署无需修改"
    )
    # 目标音频采样率（VAD/Whisper模型标准采样率，固定16000）
    TARGET_SAMPLE_RATE: int = Field(
        default=16000,
        description="标准音频采样率，模型训练用16kHz，必须固定"
    )
    # 目标音频声道（单声道为模型最优输入，双声道会干扰识别）
    TARGET_CHANNELS: int = Field(
        default=1,
        description="标准音频声道，1=单声道（最优），2=双声道"
    )
    #扩展名
    EXTEND_NAME: str = Field(".wav",
        description="转化成wav格式，适配whisper")

    # ========================== 语音识别模型配置 ==========================
    # 本地模型路径（动态绑定项目根目录，models文件夹放在项目下即可）
    LOCAL_MODEL_PATH: Path = Field(
        default=PROJECT_ROOT / "ai_model" / "distil-large-v3",
        description="faster-whisper本地模型路径，自动适配项目目录"
    )
    # 运行设备（cpu：无显卡通用；cuda：NVIDIA显卡加速）
    DEVICE: str = Field(
        default="cuda",
        description="模型运行设备，可选：cpu / cuda"
    )
    # 识别语言（zh=中文，en=英文，auto=自动检测）
    LANGUAGE: str|None = Field(
        default=None,
        description="语音识别目标语言，指定后速度更快，zh=中文"
    )

    # ========================== VAD 静音过滤配置 ==========================
    VAD_PARAMS: dict = Field(
        default={
            "threshold": 0.5,
            "min_silence_duration_ms": 800,
            "speech_pad_ms": 400
        },
        description="VAD语音活动检测参数：过滤无人声静音片段"
    )
    # 单独拆分VAD参数（方便单独调用，注释更清晰）
    VAD_THRESHOLD: float = Field(
        default=0.5,
        description="VAD检测阈值：0~1，值越高越严格，只识别清晰人声"
    )
    VAD_MIN_SPEECH: int = Field(
        default=250,
        description="最小静音时长(毫秒)：超过该时长判定为静音并过滤"
    )
    VAD_SPEECH_PAD: int = Field(
        default=400,
        description="语音前后缓冲时长(毫秒)：防止说话开头/结尾被截断"
    )

    class Config:
        # 编码格式
        env_file_encoding = 'utf-8'

# 全局单例配置（全局调用一次，避免重复加载）
settings = AppSettings()