from pydantic import BaseModel,field_validator
import re
from urllib.parse import urlparse,urlunparse

class VideoTranscribeRequest(BaseModel):
    video_url: str
    language: str | None = None

    @field_validator('video_url')
    def validate_tiktok_url(cls, value: str) -> str:
        tiktok_pattern = r'^https?://(www\.)?tiktok\.com/@.+/video/\d+(\?.*)?$'
        if not re.match(tiktok_pattern, value):
            raise ValueError('仅支持TikTok分享链接！')
        parsed_url = urlparse(value)
        cleaned_url = parsed_url._replace(query='').geturl()
        return cleaned_url

class VideoTranscribeResponse(BaseModel):
    filepath:str|None
    language: str|None = None
    title: str
    webpage_url: str
    uploader: str
    uploader_url: str
    duration_string: str
    timestamp: int
    id: str
    view_count: int
    like_count: int
    repost_count: int
    comment_count: int
    save_count: int
    segments: list
