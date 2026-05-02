from app.infra.config import settings,PROJECT_ROOT,TEMP_VIDEO_PATH

import os

output_dir_url = str(TEMP_VIDEO_PATH)
os.makedirs(output_dir_url, exist_ok=True)

# "format": "bv*[height<=720]+ba/b[height<=720]/best"

ydl_opts = {
    'ffmpeg_location': settings.FFMPEG_PATH,
    "impersonate_targets": ["Chrome-131",'Chrome-124','Chrome-116'],
    "format": "b[height<=720][vcodec^=h264]/b[height<=720]/best",
    "merge_output_format": "mp4",
    "outtmpl": f'{output_dir_url}/%(id)s.%(ext)s',
    "quiet": True,
    "check_formats": False,
    'proxy': settings.PROXY,
    'extractor_args': {'tiktok': {'webpage_downloader': 'curl'}}
}
