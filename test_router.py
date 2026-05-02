from app.schemas.video import VideoTranscribeRequest
from app.services.video import download_tiktok_video, extract_audio_from_video, transcribe_audio
import asyncio

async def test():
    request = VideoTranscribeRequest(video_url="https://www.tiktok.com/@slayspeech/video/7618451225570282783",language=None)

    video_info: dict = await download_tiktok_video(request.video_url)
    print(video_info)
    # 提取音频
    audio_path = await extract_audio_from_video(video_info.get('filepath'), video_info.get('id'))
    print(audio_path)
    # 将音频输入大模型提取文本
    transcribe_result = await transcribe_audio(audio_path, None)
    print(transcribe_result)

asyncio.run(test())