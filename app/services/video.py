import yt_dlp as ytdl
from yt_dlp.utils import DownloadError,ExtractorError,PostProcessingError,UnavailableVideoError
from fastapi import HTTPException
import socket
import asyncio
from faster_whisper import WhisperModel

from app.infra.config import settings
from app.infra.logger import get_logger
from utils.video_utils import get_ydl_opts
from utils.audio_utils import extract_audio

logger = get_logger(__name__)

model = WhisperModel(
        model_size_or_path=str(settings.LOCAL_MODEL_PATH),
        device=settings.DEVICE,
        compute_type='int8'
    )

REQUIRED_FIELDS = [
    "title",#视频标题
    "webpage_url",#视频链接
    "uploader",#作者
    "uploader_url",#作者主页
    "duration_string",#分秒形式的时间
    "timestamp", #时间戳
    "id", #传参id，用于给下载的视频命名
    "view_count",#观看量
    "like_count",#喜欢数
    "repost_count",#转发量
    "comment_count",#评论量
    "save_count"#收藏量
]


def _download(video_url: str) -> dict:
    with ytdl.YoutubeDL(get_ydl_opts()) as ydl:
        raw_video_info = ydl.extract_info(video_url, download=True)
        # 新增：防呆检查，确保提取到视频信息
        if not raw_video_info:
            raise ExtractorError("提取的视频元数据为空，无法生成有效信息")
        # 处理元数据
        video_meta_info = {field: raw_video_info.get(field) for field in REQUIRED_FIELDS}

        # 优先使用 yt-dlp 实际下载结果中的 filepath，避免 prepare_filename 的模板推导异常。
        requested_downloads = raw_video_info.get("requested_downloads") or []
        if requested_downloads and isinstance(requested_downloads, list):
            video_meta_info["filepath"] = requested_downloads[0].get("filepath")
        else:
            video_meta_info["filepath"] = raw_video_info.get("_filename")

        if not video_meta_info.get("filepath"):
            raise ExtractorError("下载完成但未解析到本地视频路径")
        return video_meta_info
async def download_tiktok_video(video_url: str) -> dict:
    try:
        video_info = await asyncio.to_thread(_download, video_url)
        return video_info

    # ====================== 1. 视频/链接问题（客户端错误 400）======================
    except ExtractorError as e:
        logger.error(f"视频解析失败 | URL: {video_url} | 原因: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="视频解析失败：链接无效、视频已删除、私密或地区限制"
        )
    except UnavailableVideoError as e:
        logger.error(f"视频链接错误 | URL：{video_url} | 原因：{str(e)}")
        raise HTTPException(
            status_code=404,
            detail="视频不存在：已下架、账号封禁或无权限访问"
        )

    # ====================== 2. 下载失败（客户端/反爬问题 400）======================
    except DownloadError as e:
        logger.error(f"视频下载失败 | URL: {video_url} | 原因: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail="视频下载失败：反爬拦截、代理失效、无720P画质或网络中断"
        )

    # ====================== 3. FFmpeg/服务器配置错误（服务端错误 500）======================
    except PostProcessingError as e:
        logger.error(f"FFmpeg 处理失败 | URL: {video_url} | 原因: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="服务器处理失败：FFmpeg 未安装/路径错误/转码失败"
        )

    # ====================== 4. 网络/代理超时（服务端错误 504）======================
    except (ConnectionError, TimeoutError, socket.timeout) as e:
        logger.error(f"网络/代理超时 | URL: {video_url} | 原因: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="网络请求超时：代理连接失败、TikTok服务器响应超时"
        )

    # ====================== 5. 系统/文件权限错误（服务端错误 500）======================
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f"文件打开失败 | URL：{video_url} | 原因：: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="服务器文件错误：目录不存在、无写入权限或磁盘空间不足"
        )

    # ====================== 6. 未知错误兜底 ======================
    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.exception(f"未知错误 | URL: {video_url} | 原因: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"下载未知错误：{str(e)}"
        )

async def extract_audio_from_video(url_in: str, url_out: str|None) -> str:
    try:
        return await asyncio.to_thread(extract_audio, url_in, url_out)
    except Exception as e:
        logger.error(f"音频提取失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"音频提取失败：{str(e)}")

async def transcribe_audio(url_in: str, language:str|None = None) -> dict:

    def _transcribe():
        segment_list = []
        segments, info = model.transcribe(
            audio=url_in,
            language=language or settings.LANGUAGE,
            beam_size=5,
            vad_filter=True,
            vad_parameters=settings.VAD_PARAMS
        )
        for segment in segments:
            line = segment.text.strip()
            if line:
                segment_list.append({
                    'start': round(segment.start, 2),
                    'text': line
                })
        return {
            'language': info.language,
            'segments': segment_list
        }

    try:
        result = await asyncio.to_thread(_transcribe)
        return result
    except Exception as e:
        logger.error(f"语言识别失败：{str(e)}")
        raise HTTPException(status_code=500, detail=f"语音识别失败：{str(e)}")