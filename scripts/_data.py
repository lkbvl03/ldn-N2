"""
_data.py — Đọc cấu hình từ src/data.ts (nguồn sự thật duy nhất).
Import module này trong mọi script pipeline để luôn đồng bộ với data.ts.

Không chạy trực tiếp. Dùng: from _data import get_scenes, get_voice_config, ...
"""
import re, os, sys

ROOT = os.path.join(os.path.dirname(__file__), "..")

def _src() -> str:
    path = os.path.join(ROOT, "src", "data.ts")
    with open(path, encoding="utf-8") as f:
        return f.read()


def get_fps() -> int:
    """FPS của composition (src/data.ts)."""
    m = re.search(r'export const FPS\s*=\s*(\d+)', _src())
    return int(m.group(1)) if m else 30


def get_voice_config() -> dict:
    """PIPELINE_CONFIG — voice, rate, volume."""
    src = _src()
    voice  = re.search(r'VOICE:\s*["\']([^"\']+)["\']', src)
    rate   = re.search(r'RATE:\s*["\']([^"\']+)["\']', src)
    volume = re.search(r'VOLUME:\s*["\']([^"\']+)["\']', src)
    return {
        "voice":  voice.group(1)  if voice  else "en-US-AriaNeural",
        "rate":   rate.group(1)   if rate   else "-8%",
        "volume": volume.group(1) if volume else "+0%",
    }


def get_scenes() -> list:
    """SCENES[] — danh sách phân cảnh (id, label, text, imagePrompt).
    Số lượng biến thiên theo kịch bản (không cố định)."""
    src = _src()
    m = re.search(r'export const SCENES:\s*Scene\[\]\s*=\s*\[(.*?)\];', src, re.DOTALL)
    if not m:
        raise ValueError("Không tìm thấy SCENES trong src/data.ts")
    block = m.group(1)

    item_re = re.compile(
        r'\{\s*'
        r'id:\s*(?P<id>\d+),\s*'
        r'label:\s*"(?P<label>(?:[^"\\]|\\.)*)",\s*'
        r'text:\s*`(?P<text>(?:[^`\\]|\\.)*)`,\s*'
        r'imagePrompt:\s*"(?P<imagePrompt>(?:[^"\\]|\\.)*)",?\s*'
        r'\}',
        re.DOTALL,
    )
    scenes = [
        {
            "id": int(mo.group("id")),
            "label": mo.group("label"),
            "text": mo.group("text").strip(),
            "imagePrompt": mo.group("imagePrompt"),
        }
        for mo in item_re.finditer(block)
    ]
    if not scenes:
        raise ValueError("SCENES rỗng — điền phân cảnh vào src/data.ts trước khi chạy pipeline")
    return scenes


def get_video_config() -> dict:
    """VIDEO_CONFIG — title, accentColor, v.v."""
    src = _src()
    def pick(key):
        m = re.search(rf'{key}:\s*["\']([^"\']+)["\']', src)
        return m.group(1) if m else ""
    return {
        "title":       pick("title"),
        "subtitle":    pick("subtitle"),
        "accentColor": pick("accentColor"),
        "bgColor":     pick("bgColor"),
    }


# ── Quick self-test ───────────────────────────────────────────────
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== _data.py self-test ===")
    cfg = get_video_config()
    print(f"Video   : {cfg['title']}")
    vc = get_voice_config()
    print(f"Voice   : {vc['voice']} rate={vc['rate']}")
    scenes = get_scenes()
    print(f"Scenes  : {len(scenes)}")
    for s in scenes:
        print(f"  [{s['id']}] {s['label']}: text={len(s['text'])} chars, "
              f"imagePrompt={s['imagePrompt'][:60]!r}")
    print("=== OK ===")
