import yt_dlp as ytdl
import os
from app.infra.config import settings, PROJECT_ROOT
import json

TIKTOK_URL = "https://www.tiktok.com/@slayspeech/video/7618451225570282783"

output_dir_url = str(PROJECT_ROOT / 'temp_video')
os.makedirs(output_dir_url, exist_ok=True)

ydl_opts = {
    'ffmpeg_location': settings.FFMPEG_PATH,
    "impersonate_targets": ["Chrome-131", 'Chrome-124', 'Chrome-116'],
    "format": "best[height=720]/best",
    "outtmpl": f'{output_dir_url}/%(id)s.%(ext)s',
    "quiet": True,
    'proxy': settings.PROXY,
    'extractor_args': {'tiktok': {'webpage_downloader': 'curl'}}
}

with ytdl.YoutubeDL(ydl_opts) as ydl:
    print("正在下载TikTok视频...")
    video_info = ydl.extract_info(TIKTOK_URL, download=True)
    video_file_path = ydl.prepare_filename(video_info)  # 获取下载的视频完整路径

print("下载完成！")
print("=== 所有元数据 ===")
for key, value in video_info.items():
    print(f"{key}: {value}")
video_id = video_info.get('id', 'unknown')
metadata_file = os.path.join(output_dir_url, f"{video_id}_metadata.json")

with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(video_info, f, ensure_ascii=False, indent=2, default=str)

print(f"元数据已保存到: {metadata_file}")