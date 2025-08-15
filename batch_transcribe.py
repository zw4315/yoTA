import os
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from faster_whisper import WhisperModel

# 配置
VIDEO_URL = "https://www.bilibili.com/video/BV16M4m1m7YP/"
INPUT_DIR = Path.home() / "open-course/mit6.824"
NUM_CORES = 4
OUTPUT_SUFFIX = ".txt"

def download_video_to_mp3():
    print("📥 Downloading Bilibili video as mp3...")
    command = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "-o", str(INPUT_DIR / "%(title)s.%(ext)s"),
        VIDEO_URL
    ]
    subprocess.run(command, check=True)
    print("✅ Download finished.")

def transcribe_audio(mp3_path: Path):
    model_size = "medium.en"
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=1)

    output_path = mp3_path.with_suffix(OUTPUT_SUFFIX)
    segments, info = model.transcribe(str(mp3_path), beam_size=5)

    with open(output_path, "w") as f:
        f.write(f"# Detected language: {info.language} (p={info.language_probability:.2f})\n\n")
        for segment in segments:
            f.write("[%.2fs -> %.2fs] %s\n" % (segment.start, segment.end, segment.text))

    print(f"🎤 Transcribed: {mp3_path.name}")
    return str(output_path)

def main():
    # 确保目录存在
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: 下载视频
    download_video_to_mp3()

    # Step 2: 查找 mp3 文件
    mp3_files = sorted(INPUT_DIR.glob("*.mp3"))
    if not mp3_files:
        print("❌ No MP3 files found.")
        return

    # Step 3: 多核转录
    with ProcessPoolExecutor(max_workers=NUM_CORES) as executor:
        executor.map(transcribe_audio, mp3_files)

if __name__ == "__main__":
    main()

