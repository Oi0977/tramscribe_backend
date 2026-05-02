# -*- coding: utf-8 -*-
import subprocess

from app.infra.config import settings  # 导入动态配置
from app.infra.config import TEMP_AUDIO_PATH
from app.infra.logger import get_logger

logger = get_logger(__name__)

def extract_audio(input_file: str, output_file: str = "unnamed") -> str:
    """
    通用工具方法：将任意视频/音频 → 转换为16kHz单声道标准音频
    路径全部动态获取，支持部署迁移
    """

    output_dir = str(TEMP_AUDIO_PATH/output_file) + settings.EXTEND_NAME
    ffmpeg_cmd = [
        # 动态FFmpeg路径（自动适配项目）
        str(settings.FFMPEG_EXEC_PATH),
        "-i", input_file,
        settings.AUDIO_ONLY,
        "-ar", str(settings.TARGET_SAMPLE_RATE),
        "-ac", str(settings.TARGET_CHANNELS),
        "-sample_fmt", "s16",
        "-c:a", "pcm_s16le",
        "-y",
        output_dir
    ]
    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        logger.info(f"ffmpeg转码失败：{e.stderr.decode('utf-8')}")
        raise RuntimeError(f"音频提取失败：{e.stderr.decode('utf-8')}")

    return output_dir