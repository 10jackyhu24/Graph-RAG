import os
import torch
import numpy as np
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from pyannote.audio import Pipeline
from pydub import AudioSegment
from app.utils.config import WHISPER_LOCAL_DIR, PYANNOTE_LOCAL_DIR


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02}:{minutes:02}:{secs:06.3f}"


def cut_audio(audio: AudioSegment, start_sec: float, end_sec: float) -> AudioSegment:
    return audio[int(start_sec * 1000): int(end_sec * 1000)]


def main():
    # ============ 你要改的設定 ============

    AUDIO_PATH = "./test/audio.wav"

    OUTPUT_TXT = "./test/result.txt"

    # zh / ja / en ... (Whisper語言提示)
    LANGUAGE = "zh"

    # ====================================

    if not os.path.exists(AUDIO_PATH):
        print(f"[ERROR] 音檔不存在: {AUDIO_PATH}")
        return

    if not os.path.exists(WHISPER_LOCAL_DIR):
        print(f"[ERROR] Whisper 模型資料夾不存在: {WHISPER_LOCAL_DIR}")
        return

    if not os.path.exists(PYANNOTE_LOCAL_DIR):
        print(f"[ERROR] Pyannote 模型資料夾不存在: {PYANNOTE_LOCAL_DIR}")
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    print(f"[INFO] device={device}, dtype={dtype}")

    # ============ Whisper (HF Transformers pipeline) ============

    print("[INFO] Loading Whisper model from local folder...")

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        WHISPER_LOCAL_DIR,
        torch_dtype=dtype,
        low_cpu_mem_usage=True
    ).to(device)

    processor = AutoProcessor.from_pretrained(WHISPER_LOCAL_DIR)

    whisper_asr = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        device=0 if device == "cuda" else -1
    )

    # ============ Pyannote diarization ============

    print("[INFO] Loading Pyannote pipeline from local folder...")
    diarization_pipeline = Pipeline.from_pretrained(PYANNOTE_LOCAL_DIR)

    # ============ Load full audio ============

    print("[INFO] Loading audio...")
    audio = AudioSegment.from_file(AUDIO_PATH)

    # ============ Speaker diarization ============

    print("[INFO] Running diarization...")
    diarization = diarization_pipeline(AUDIO_PATH)

    # ============ Transcribe each speaker segment ============

    print("[INFO] Transcribing segments...")
    results = []

    for turn, _, speaker in diarization.itertracks(yield_label=True):
        start = float(turn.start)
        end = float(turn.end)

        # 太短的段落直接跳過
        if end - start < 0.5:
            continue

        segment_audio = cut_audio(audio, start, end)

        temp_wav = "temp_segment.wav"
        segment_audio.export(temp_wav, format="wav")

        # Whisper transcription
        asr_result = whisper_asr(
            temp_wav,
            generate_kwargs={"language": LANGUAGE},
            return_timestamps=False
        )

        text = asr_result["text"].strip()

        results.append({
            "speaker": speaker,
            "start": start,
            "end": end,
            "text": text
        })

        print(f"{speaker} [{format_timestamp(start)} - {format_timestamp(end)}] {text}")

    # ============ Save output ============

    print("[INFO] Writing output...")
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"{r['speaker']} [{format_timestamp(r['start'])} - {format_timestamp(r['end'])}]\n")
            f.write(r["text"] + "\n\n")

    print(f"[DONE] Saved to {OUTPUT_TXT}")

    # 清除暫存檔
    if os.path.exists("temp_segment.wav"):
        os.remove("temp_segment.wav")


if __name__ == "__main__":
    main()
