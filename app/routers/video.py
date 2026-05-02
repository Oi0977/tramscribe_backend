from pathlib import Path

from fastapi import APIRouter,HTTPException
from app.schemas.video import *
from app.schemas.common import BaseResponse
from app.services.video import download_tiktok_video, extract_audio_from_video, transcribe_audio
from app.infra.config import TEMP_VIDEO_PATH,PROJECT_ROOT
from app.infra.logger import get_logger

from fastapi.responses import FileResponse
from typing import Any
import os

logger = get_logger(__name__)
TEMP_VIDEO_PATH = PROJECT_ROOT / 'temp_video'
TEMP_AUDIO_PATH = PROJECT_ROOT / 'temp_audio'

router = APIRouter(
    prefix="/video",
    tags=["video"],
    responses={404: {"description": "Not found"}},
)


@router.post('/transcribe', response_model=BaseResponse[VideoTranscribeResponse])
async def transcribe_video(request: VideoTranscribeRequest) -> Any:
    #下载视频
    video_info:dict = await download_tiktok_video(request.video_url)
    #提取音频
    audio_path = await extract_audio_from_video(video_info.get('filepath'), video_info.get('id'))
    #将音频输入大模型提取文本
    transcribe_result = await transcribe_audio(audio_path,request.language)
    video_data = VideoTranscribeResponse(**video_info,**transcribe_result)
    return BaseResponse(data=video_data)

@router.get('/{video_id}')
async def get_video_by_id(video_id: str) -> Any:
    video_path = TEMP_VIDEO_PATH / f"{video_id}.mp4"
    if not(Path(video_path).exists()):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(
        path=video_path,
        media_type='video/mp4',
        filename=f"{video_id}.mp4"
    )