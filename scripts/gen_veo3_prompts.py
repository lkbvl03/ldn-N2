"""
gen_veo3_prompts.py — Sinh prompt video nền cho Google Studio Flow VEO 3.

Cách dùng:
  python -X utf8 scripts/gen_veo3_prompts.py

Mỗi clip VEO 3 = 8 giây. Mỗi SCENE (src/data.ts) là 1 ranh giới tự nhiên —
script tự tính số clip cần thiết cho TỪNG scene dựa trên độ dài text của
scene đó (+ 15% dự phòng).
Output: Du-lieu-lam-video/veo3_prompts.txt  +  in ra terminal
"""
import re, os, sys, math

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))
from _data import get_scenes, get_video_config

# ── Hằng số ─────────────────────────────────────────────────────────────────
VEO3_CLIP_SEC   = 8      # Độ dài mỗi clip VEO 3 (giây)
BUFFER_PERCENT  = 0.15   # +15% dự phòng
AVG_SYL_PER_SEC = 3.5    # Tốc độ đọc tiếng Việt (âm tiết/giây) ≈ 210 syl/phút

STYLE_SUFFIX = (
    "Colorful 3D embossed hand-painted style, raised relief texture, thick painterly brush "
    "strokes, dark obsidian background #0A0A0F, vivid colorful palette with a dominant brand "
    "accent color splash (signal red #FF3B30, data yellow #FFD60A, mind purple #BF5AF2 or "
    "nature green #30D158), smooth camera movement, professional cinematography, vertical "
    "9:16 portrait framing, no text, no subtitles."
)

MOVEMENTS = [
    "slow push-in toward subject",
    "gentle parallax drift left",
    "smooth dolly forward",
    "subtle handheld sway",
    "slow crane tilt down",
    "graceful arc right",
    "steady pull-back reveal",
    "micro-float static shot",
]


# ─────────────────────────────────────────────────────────────────────────────
def estimate_duration_sec(script_raw: str) -> float:
    """Ước tính thời lượng giọng đọc của 1 đoạn kịch bản (1 scene)."""
    pause_total = 0.0
    pause_map = {
        r"\[DỪNG 0\.5s\]": 0.5,
        r"\[DỪNG 1s\]":    1.0,
        r"\[DỪNG 2s\]":    2.0,
        r"\[DỪNG 3s\]":    3.0,
        r"\[DỪNG 4s\]":    4.0,
        r"\[DỪNG AS\]":    1.5,   # Artistic silence ≈ 1.5s
    }
    text = script_raw
    for pattern, sec in pause_map.items():
        count = len(re.findall(pattern, text))
        pause_total += count * sec
        text = re.sub(pattern, "", text)

    words = text.split()
    syl_count = sum(
        max(1, len(re.findall(r"[aăâeêioôơuưyAĂÂEÊIOÔƠUƯY]", w)))
        for w in words if w
    )
    speech_sec = syl_count / AVG_SYL_PER_SEC
    return speech_sec + pause_total


def generate_prompts_for_scene(scene: dict) -> list[dict]:
    """Sinh N clip prompt cho 1 scene, dựa trên độ dài text của chính scene đó."""
    est_sec     = estimate_duration_sec(scene["text"])
    n_clips_raw = max(1, est_sec / VEO3_CLIP_SEC)
    n_clips     = math.ceil(n_clips_raw * (1 + BUFFER_PERCENT))

    prompts = []
    for j in range(n_clips):
        movement = MOVEMENTS[j % len(MOVEMENTS)]
        progress = j / max(1, n_clips - 1) if n_clips > 1 else 0.5
        if progress < 0.33:
            timing = "opening moment, establish atmosphere"
        elif progress < 0.67:
            timing = "mid-scene, peak emotional tension"
        else:
            timing = "closing beat, emotional resolution"

        prompt = f"{scene['imagePrompt']}, {timing}, {movement}. {STYLE_SUFFIX}"
        prompts.append({
            "clip":         j + 1,
            "total":        n_clips,
            "duration_sec": VEO3_CLIP_SEC,
            "prompt":       prompt,
        })
    return prompts, est_sec


# ─────────────────────────────────────────────────────────────────────────────
def main():
    scenes    = get_scenes()
    video_cfg = get_video_config()

    print("=" * 65)
    print(f"  VEO 3 PROMPT GENERATOR — {video_cfg.get('title', 'VIDEO')}")
    print("=" * 65)
    print(f"  Số scene : {len(scenes)}")
    print("=" * 65)

    out_dir  = os.path.join(os.path.dirname(__file__), "..", "Du-lieu-lam-video")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "veo3_prompts.txt")

    total_clips = 0
    total_est   = 0.0

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"VEO 3 PROMPTS — {video_cfg.get('title', 'VIDEO')}\n")
        f.write(f"Số scene: {len(scenes)}\n")
        f.write("=" * 65 + "\n\n")

        for scene in scenes:
            prompts, est_sec = generate_prompts_for_scene(scene)
            total_clips += len(prompts)
            total_est   += est_sec

            header = (
                f"SCENE {scene['id']:02d} — {scene['label']}  "
                f"(~{est_sec:.0f}s ước tính → {len(prompts)} clip × {VEO3_CLIP_SEC}s)"
            )
            print(f"\n{'─'*65}")
            print(f"  {header}")
            print(f"{'─'*65}")
            f.write(f"\n{'═'*65}\n{header}\n{'═'*65}\n\n")

            for p in prompts:
                line = f"[CLIP {p['clip']:02d}/{p['total']:02d}] {p['prompt']}"
                print(line)
                f.write(line + "\n\n")

    print(f"\n\n{'='*65}")
    print(f"  XONG! {total_clips} clip ({total_clips * VEO3_CLIP_SEC}s) đã lưu vào:")
    print(f"  Du-lieu-lam-video/veo3_prompts.txt")
    print(f"\n  Hướng dẫn dùng với Google Studio Flow VEO 3:")
    print(f"  1. Mở studio.google.com/flow")
    print(f"  2. Tạo project mới, chọn VEO 3, tỉ lệ khung hình 9:16")
    print(f"  3. Copy từng prompt vào — mỗi clip 8 giây")
    print(f"  4. Đồng bộ nhân vật: dùng 'Character reference' từ clip đầu mỗi scene")
    print(f"  5. Ghép các clip của 1 scene lại = video nền cho scene đó")
    print(f"     (thay thế cho public/images/bg/bg-{{NN}}.jpg của scene đó)")
    print(f"{'='*65}\n")


if __name__ == "__main__":
    main()
