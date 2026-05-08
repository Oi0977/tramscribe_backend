from yt_dlp.networking.impersonate import ImpersonateTarget

from app.infra.config import settings,TEMP_VIDEO_PATH

import os

output_dir_url = str(TEMP_VIDEO_PATH)
os.makedirs(output_dir_url, exist_ok=True)

# "format": "bv*[height<=720]+ba/b[height<=720]/best"
# 'extractor_args': {
#             'tiktok': {
#                 # 列表格式，把参数值填在引号里
#                 'app_info': ['735572885697939226', '30.0.0']
#             }
#         }
def get_ydl_opts():
    opts = {
        'ffmpeg_location': settings.FFMPEG_EXEC_PATH,
        'impersonate': ImpersonateTarget.from_str('chrome-124'),
        'format': 'b[height<=720][vcodec^=h264]/b[height<=720]/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'{output_dir_url}/%(id)s.%(ext)s',
        'quiet': True,
        'check_formats': False,
    }
    if settings.PROXY:
        opts['proxy'] = settings.PROXY
    return opts
