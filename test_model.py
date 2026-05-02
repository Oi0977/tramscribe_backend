from faster_whisper import WhisperModel
from app.infra.config import settings
import time

model = WhisperModel(
    model_size_or_path=str(settings.LOCAL_MODEL_PATH),
    device=settings.DEVICE,
    compute_type="int8"
)
print('开始执行解析')
start_time = time.perf_counter()
segments, info = model.transcribe(
    audio= r"S:\Code\python_code\e_commerce\temp_audio\test_16k.wav",
    language=settings.LANGUAGE,
    beam_size=5,
    vad_filter=True,
    vad_parameters=settings.VAD_PARAMS
)
print("\n"+"="*32)
with open("test_result.txt", 'w', encoding="utf-8") as f:
    for segment in segments:
        line = segment.text.strip()
        if line:
            f.write(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {line}\n")

end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(F'识别结果以保存到test_result.txt')
print(f"识别耗时：{elapsed_time:.2f}s")