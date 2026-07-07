"""
calc_scene_timing.py — Đo thời lượng THẬT của từng public/voice/scene-NN.mp3
bằng ffprobe, in ra mốc giây/frame tuyệt đối cộng dồn của từng scene.

Dùng số liệu này để viết `EFFECTS` (src/Effects.tsx) và `SFX_TIMELINE`
(src/RankingVideo.tsx) với startSec/fromFrame ĐÚNG NGAY LẦN ĐẦU — không cần
remap sau (Remotion tự tính lại durationInFrames của composition qua
calculateMetadata trong Root.tsx, độc lập với script này).

Chạy SAU step1_voice.py:
  python -X utf8 scripts/calc_scene_timing.py
"""
import os, sys, subprocess, json

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))
from _data import get_scenes, get_fps

ROOT      = os.path.join(os.path.dirname(__file__), "..")
VOICE_DIR = os.path.join(ROOT, "public", "voice")


def ffprobe_duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    )
    return float(r.stdout.strip())


def main():
    scenes = get_scenes()
    fps    = get_fps()

    print("=" * 70)
    print(f"{'Scene':<10}{'Label':<14}{'Duration(s)':<14}{'StartSec':<12}{'StartFrame':<10}")
    print("=" * 70)

    cumulative_sec = 0.0
    total_frames   = 0
    missing        = []

    for scene in scenes:
        name = f"scene-{scene['id']:02d}"
        path = os.path.join(VOICE_DIR, f"{name}.mp3")

        if not os.path.exists(path):
            missing.append(name)
            print(f"{name:<10}{scene['label']:<14}{'-- chưa có --':<14}")
            continue

        dur_sec     = ffprobe_duration(path)
        start_sec   = cumulative_sec
        start_frame = round(start_sec * fps)
        dur_frames  = round(dur_sec * fps)

        print(f"{name:<10}{scene['label']:<14}{dur_sec:<14.2f}{start_sec:<12.2f}{start_frame:<10}")

        cumulative_sec += dur_sec
        total_frames   += dur_frames

    print("=" * 70)
    print(f"Tổng thời lượng : {cumulative_sec:.2f}s  ({total_frames} frame @ {fps}fps)")

    if missing:
        print(f"\nCẢNH BÁO: {len(missing)} scene chưa có voice: {', '.join(missing)}")
        print("Chạy: python -X utf8 scripts/step1_voice.py")
    else:
        print("\nDùng bảng StartSec ở trên để viết EFFECTS/SFX_TIMELINE.")
        print("Composition tự tính lại durationInFrames qua calculateMetadata —")
        print("không cần ghi tay TOTAL_DURATION_FRAMES.")


if __name__ == "__main__":
    main()
