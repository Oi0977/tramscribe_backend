from fastapi import FastAPI
from .routers import video
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import os
import time

from app.infra.logger import get_logger
from app.infra.config import TEMP_VIDEO_PATH
from app.infra.config import TEMP_AUDIO_PATH

logger = get_logger(__name__)

# 自动下载AI模型（部署Render用）
from huggingface_hub import snapshot_download
import os

# 模型保存路径（和你原来的路径一致）
model_path = "./ai_model/distil-large-v3"
if not os.path.exists(model_path):
    print("正在自动下载模型...")
    snapshot_download(
        repo_id="distil-whisper/distil-large-v3",
        local_dir=model_path,
        local_dir_use_symlinks=False,
        allow_patterns=[
            "config.json",
            "model.bin",
            "preprocessor_config.json",
            "tokenizer.json",
            "vocabulary.json"
        ]
    )

# 定义清理逻辑
async def cleanup_old_files():
    """后台保洁员：每小时清理一次超过 2 小时的临时音视频文件"""
    temp_video = TEMP_VIDEO_PATH
    temp_audio = TEMP_AUDIO_PATH
    # 设定过期时间（秒）：2小时 = 7200秒
    MAX_AGE_SECONDS = 2 * 60 * 60

    while True:
        try:
            await asyncio.sleep(60 * 60)  # 每隔 1 小时执行一次扫描

            for temp_dir in [temp_video, temp_audio]:
                if not temp_dir.exists():
                    continue
                for file_path in temp_dir.iterdir():
                    if file_path.is_file():
                        # 获取文件最后修改时间
                        file_age = os.path.getmtime(file_path)

                        # 简单写法：当前时间戳 - 文件修改时间戳 > 最大存活时间
                        if (time.time() - file_age) > MAX_AGE_SECONDS:
                            try:
                                os.remove(file_path)
                                logger.info(f"定时清理已删除: {file_path}")
                            except Exception as e:
                                logger.error(f"定时清理删除失败: {file_path} | {str(e)}")
        except Exception as e:
            logger.error(f"定时清理任务发生异常: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 服务启动时，在后台启动清理任务
    task = asyncio.create_task(cleanup_old_files())
    yield
    # 服务关闭时，取消任务（可选）
    task.cancel()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://e-commerce-phi-neon-34.vercel.app/",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)


app.include_router(video.router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
