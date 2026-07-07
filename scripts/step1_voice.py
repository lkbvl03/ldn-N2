"""
Bước 1: Tạo giọng đọc tiếng Việt qua Vbee TTS — MỖI SCENE 1 FILE RIÊNG.

Cách hoạt động (lặp qua từng scene trong SCENES của src/data.ts):
  1. Tách text của scene tại mỗi [DỪNG Xs] thành các đoạn text + khoảng lặng
  2. Generate TTS từng đoạn → checkpoint tạm
  3. Tạo silence chính xác (ffmpeg) → checkpoint tạm
  4. Nối tất cả theo thứ tự → public/voice/scene-NN.mp3

Giọng mặc định: n_yenbai_male_giongnamldn_zero_shot_story_vc (kênh LDN)
Chạy: python -X utf8 scripts/step1_voice.py
"""
import os, sys, re, requests, time, subprocess, shutil

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))
from _data import get_scenes, get_voice_config

ROOT       = os.path.join(os.path.dirname(__file__), "..")
VOICE_DIR  = os.path.join(ROOT, "public", "voice")
os.makedirs(VOICE_DIR, exist_ok=True)


def load_env():
    env_path = os.path.join(ROOT, ".env")
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()

# ─── CẤU HÌNH VBEE ────────────────────────────────────────────────────────
APP_ID  = os.environ.get("VBEE_APP_ID", "")
API_KEY = os.environ.get("VBEE_API_KEY", "")
if not APP_ID or not API_KEY:
    print("LỖI: Chưa cấu hình VBEE_APP_ID / VBEE_API_KEY trong .env")
    sys.exit(1)

VOICE     = get_voice_config()["voice"]
MAX_CHARS = 3000

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type":  "application/json",
}

# Ánh xạ marker → giây dừng thực
PAUSE_MAP = {
    r"\[DỪNG 0\.5s\]": 0.5,
    r"\[DỪNG 1s\]":    1.0,
    r"\[DỪNG 2s\]":    2.0,
    r"\[DỪNG 3s\]":    3.0,
    r"\[DỪNG 4s\]":    4.0,
    r"\[DỪNG AS\]":    3.5,   # dấu ấn kênh LDN — khoảng lặng dài
}

MIN_TEXT_CHARS = 12   # đoạn ngắn hơn sẽ được gộp vào đoạn kề


def parse_segments(raw: str) -> list:
    """
    Trả về list xen kẽ:
      {"type": "text",    "content": "..."}
      {"type": "silence", "sec": 1.0}
    Đoạn text < MIN_TEXT_CHARS được gộp vào đoạn text liền kề.
    """
    combined = "(" + "|".join(PAUSE_MAP.keys()) + ")"
    parts    = re.split(combined, raw)

    raw_segments = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        matched_sec = None
        for pattern, sec in PAUSE_MAP.items():
            if re.fullmatch(pattern, part):
                matched_sec = sec
                break
        if matched_sec is not None:
            raw_segments.append({"type": "silence", "sec": matched_sec})
        else:
            text = re.sub(r'[ \t]+', ' ', part).strip()
            if text:
                raw_segments.append({"type": "text", "content": text})

    # Gộp đoạn text quá ngắn vào đoạn text trước đó (hoặc sau nếu là đầu tiên)
    segments = []
    for seg in raw_segments:
        if seg["type"] == "text" and len(seg["content"]) < MIN_TEXT_CHARS:
            last_text_idx = None
            for i in range(len(segments) - 1, -1, -1):
                if segments[i]["type"] == "text":
                    last_text_idx = i
                    break
            if last_text_idx is not None:
                segments[last_text_idx]["content"] += " " + seg["content"]
            else:
                segments.append(seg)
        else:
            if (segments and segments[-1]["type"] == "text"
                    and len(segments[-1]["content"]) < MIN_TEXT_CHARS
                    and seg["type"] == "text"):
                segments[-1]["content"] += " " + seg["content"]
            else:
                segments.append(seg)

    return segments


def split_text_chunks(text: str) -> list[str]:
    """Tách text dài thành chunks <= MAX_CHARS tại ranh giới câu."""
    sentences = re.split(r'(?<=[.!?…\n])\s*', text)
    chunks, cur = [], ""
    for s in sentences:
        test = (cur + " " + s).strip() if cur else s
        if len(test) > MAX_CHARS and cur:
            chunks.append(cur.strip())
            cur = s
        else:
            cur = test
    if cur.strip():
        chunks.append(cur.strip())
    return [c for c in chunks if c]


def vbee_tts(text: str, label: str) -> bytes | None:
    """Gọi Vbee TTS, poll đến khi xong, trả về MP3 bytes."""
    body = {
        "input_text":   text,
        "voice_code":   VOICE,
        "app_id":       APP_ID,
        "callback_url": "https://httpbin.org/post",
    }
    for attempt in range(3):
        try:
            r = requests.post(
                "https://vbee.vn/api/v1/tts",
                headers=HEADERS, json=body, timeout=30,
            )
        except Exception as e:
            print(f"\n  Lỗi kết nối: {e}")
            time.sleep(3)
            continue

        if r.status_code != 200:
            print(f"\n  HTTP {r.status_code}: {r.text[:200]}")
            if attempt < 2:
                time.sleep(5)
            continue

        resp = r.json()
        if resp.get("status") != 1:
            print(f"\n  API lỗi: {resp}")
            return None

        req_id = resp["result"]["request_id"]
        print(f"  [{label}] req={req_id[:8]}... polling", end=" ", flush=True)

        poll_url = f"https://vbee.vn/api/v1/tts/{req_id}"
        for i in range(60):
            time.sleep(2)
            try:
                pr = requests.get(poll_url, headers=HEADERS, timeout=15)
                result = pr.json().get("result", {})
                status = result.get("status", "")
            except Exception:
                continue

            if status == "SUCCESS":
                link = result.get("audio_link", "")
                if not link:
                    print("\n  Không có audio_link")
                    return None
                ar = requests.get(link, timeout=60)
                if ar.status_code == 200 and ar.content[:3] == b"ID3":
                    print(f"OK ({len(ar.content)//1024} KB)")
                    return ar.content
                print(f"\n  Tải thất bại: {ar.status_code}")
                return None
            elif status in ("FAILED", "ERROR"):
                print(f"\n  Thất bại: {result}")
                return None
            if i % 5 == 4:
                print(f"{i*2}s...", end=" ", flush=True)

        print("\n  Timeout")
        return None
    return None


def make_silence_mp3(sec: float, out_path: str) -> bool:
    """Tạo file im lặng bằng ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"anullsrc=r=48000:cl=mono",
        "-t", str(sec),
        "-q:a", "9",
        "-acodec", "libmp3lame",
        out_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


def concat_mp3_files(file_list: list[str], out_path: str) -> bool:
    """Nối danh sách MP3 bằng ffmpeg concat demuxer."""
    list_path = out_path + ".list.txt"
    with open(list_path, "w", encoding="utf-8") as f:
        for fp in file_list:
            safe = fp.replace("\\", "/").replace("'", r"\'")
            f.write(f"file '{safe}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        out_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    os.remove(list_path)
    return result.returncode == 0


CHECKPOINT_ROOT = os.path.join(ROOT, "public", "_voice_chunks")  # lưu bền để resume


def generate_scene(scene: dict, idx: int, total: int) -> bool:
    scene_name = f"scene-{scene['id']:02d}"
    out_path   = os.path.join(VOICE_DIR, f"{scene_name}.mp3")

    if os.path.exists(out_path):
        print(f"[{idx+1}/{total}] {scene_name} ({scene['label']}) ... đã tồn tại — bỏ qua")
        return True

    print(f"\n[{idx+1}/{total}] {scene_name} ({scene['label']})")
    segments = parse_segments(scene["text"])
    text_segs    = [s for s in segments if s["type"] == "text"]
    silence_segs = [s for s in segments if s["type"] == "silence"]
    print(f"  Đoạn text   : {len(text_segs)}")
    print(f"  Khoảng lặng : {len(silence_segs)} ({sum(s['sec'] for s in silence_segs):.1f}s tổng)")

    checkpoint_dir = os.path.join(CHECKPOINT_ROOT, scene_name)
    os.makedirs(checkpoint_dir, exist_ok=True)

    ordered_files = []
    text_counter  = 0
    sil_counter   = 0

    for seg in segments:
        if seg["type"] == "silence":
            sil_counter += 1
            sec = seg["sec"]
            out = os.path.join(checkpoint_dir, f"sil_{sil_counter:04d}_{sec}s.mp3")
            if os.path.exists(out):
                print(f"  Silence {sec}s ... SKIP (cached)")
            else:
                print(f"  Silence {sec}s ... ", end="", flush=True)
                if make_silence_mp3(sec, out):
                    print("OK")
                else:
                    print("THẤT BẠI — dùng 0.5s thay thế")
                    make_silence_mp3(0.5, out)
            ordered_files.append(out)

        else:  # text
            text_counter += 1
            chunks = split_text_chunks(seg["content"])
            for ci, chunk in enumerate(chunks):
                label = f"T{text_counter}-{ci+1}/{len(chunks)}"
                out   = os.path.join(checkpoint_dir, f"txt_{text_counter:04d}_{ci:02d}.mp3")
                if os.path.exists(out):
                    print(f"  {label} ({len(chunk)} chars) ... SKIP (cached)")
                else:
                    print(f"  {label} ({len(chunk)} chars)")
                    audio = vbee_tts(chunk, label)
                    if audio is None:
                        print("  THẤT BẠI — dừng. Chạy lại để resume từ điểm này.")
                        return False
                    with open(out, "wb") as f:
                        f.write(audio)
                ordered_files.append(out)
            time.sleep(0.3)

    print(f"  Nối {len(ordered_files)} file → {scene_name}.mp3 ... ", end="", flush=True)
    if concat_mp3_files(ordered_files, out_path):
        size_kb = os.path.getsize(out_path) // 1024
        print(f"OK ({size_kb} KB)")
        shutil.rmtree(checkpoint_dir, ignore_errors=True)
        return True

    print("THẤT BẠI khi nối!")
    return False


def generate():
    scenes = get_scenes()
    print("=" * 62)
    print(f"VBEE TTS — Voice: {VOICE}")
    print(f"Số scene    : {len(scenes)}")
    print(f"Checkpoint  : {CHECKPOINT_ROOT}")
    print("=" * 62)

    ok = 0
    for idx, scene in enumerate(scenes):
        if generate_scene(scene, idx, len(scenes)):
            ok += 1
        else:
            print(f"\nDừng ở scene-{scene['id']:02d}. Chạy lại script để resume.")
            sys.exit(1)

    print(f"\n{'='*62}")
    print(f"HOÀN THÀNH: {ok}/{len(scenes)} scene → public/voice/scene-NN.mp3")
    print("Tiếp theo: python -X utf8 scripts/calc_scene_timing.py")
    print("=" * 62)


generate()
