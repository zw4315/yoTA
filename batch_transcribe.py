import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from faster_whisper import WhisperModel

INPUT_DIR = Path.home() / "open-course/mithpc"
OUTPUT_SUFFIX = ".txt"
NUM_CORES = 3

def transcribe_audio(mp3_path: Path):
    model_size = "medium.en"
    model = WhisperModel(model_size, device="cpu", compute_type="int8", cpu_threads=1)

    output_path = mp3_path.with_suffix(OUTPUT_SUFFIX)
    segments, info = model.transcribe(str(mp3_path), beam_size=5)

    with open(output_path, "w") as f:
        f.write(f"# Detected language: {info.language} (p={info.language_probability:.2f})\n\n")
        for segment in segments:
            f.write("[%.2fs -> %.2fs] %s\n" % (segment.start, segment.end, segment.text))

    print(f"✅ Done: {mp3_path.name}")
    return str(output_path)

def main():
    mp3_files = sorted(INPUT_DIR.glob("*.mp3"))
    if not mp3_files:
        print("No MP3 files found.")
        return

    with ProcessPoolExecutor(max_workers=NUM_CORES) as executor:
        executor.map(transcribe_audio, mp3_files)

if __name__ == "__main__":
    main()

