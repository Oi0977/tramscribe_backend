import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from faster_whisper.utils import download_model

path_model = download_model(size_or_id='distil-large-v3',output_dir='./ai_model/distil-large-v3')