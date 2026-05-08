import json
import os

import yt_dlp as ytdl

from app.infra.config import PROJECT_ROOT
from utils.video_utils import get_ydl_opts

TIKTOK_URL = "https://www.tiktok.com/@slayspeech/video/7618451225570282783"

output_dir_url = str(PROJECT_ROOT / 'temp_video')
os.makedirs(output_dir_url, exist_ok=True)

ydl_opts = get_ydl_opts()

with ytdl.YoutubeDL(ydl_opts) as ydl:
    print("正在下载TikTok视频...")
    video_info = ydl.extract_info(TIKTOK_URL, download=True)
    video_file_path = ydl.prepare_filename(video_info)  # 获取下载的视频完整路径
    print(video_file_path)

print("下载完成！")
print("=== 所有元数据 ===")
for key, value in video_info.items():
    print(f"{key}: {value}")
video_id = video_info.get('id', 'unknown')
metadata_file = os.path.join(output_dir_url, f"{video_id}_metadata.json")

with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(video_info, f, ensure_ascii=False, indent=2, default=str)

print(f"元数据已保存到: {metadata_file}")