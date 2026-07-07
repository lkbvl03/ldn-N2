"""
Tạo ảnh minh họa cho từng SCENE (số lượng biến thiên theo kịch bản) phong
cách "colorful 3D embossed hand-painted" theo hồ sơ thương hiệu LDN qua
Wavespeed AI (Flux Dev). Khung dọc 9:16 (1080×1920).
Tự đọc SCENES từ src/data.ts — không cần chỉnh script này khi làm video mới.
Chỉ cần cập nhật SCENES trong src/data.ts.

Xem bảng màu & phong cách: Du-lieu-lam-video/thuong-hieu-LDN.txt

Output: public/images/bg/bg-{01..N}.jpg  (1080×1920, dọc, khớp id từng scene)
Chạy  : python -X utf8 scripts/gen_scenes.py
"""
import requests, json, time, os, sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))
from _data import get_scenes, get_video_config

try:
    from PIL import Image
    from io import BytesIO
except ImportError:
    print("LỖI: pip install Pillow")
    sys.exit(1)


def load_env():
    env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

load_env()

API_KEY = os.environ.get("WAVESPEED_API_KEY", "")
if not API_KEY or API_KEY == "your_key_here":
    print("LỖI: Chưa cấu hình WAVESPEED_API_KEY trong .env")
    sys.exit(1)

HEADERS_AUTH = {"Authorization": f"Bearer {API_KEY}"}
HEADERS_JSON = {**HEADERS_AUTH, "Content-Type": "application/json"}

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "public", "images", "bg")
os.makedirs(OUT_DIR, exist_ok=True)

API_URL     = "https://api.wavespeed.ai/api/v2/wavespeed-ai/flux-dev"
TARGET_W    = 1080
TARGET_H    = 1920

# Style prefix cố định — thêm vào trước mỗi imagePrompt từ SCENES
# SCENES[].imagePrompt chỉ cần mô tả nội dung hình ảnh, không cần viết style
# Phong cách "colorful 3D embossed hand-painted" — nền & màu theo hồ sơ thương hiệu LDN
# (Du-lieu-lam-video/thuong-hieu-LDN.txt): nền Obsidian #0A0A0F tối, điểm nhấn Signal Red /
# Data Yellow / Mind Purple / Nature Green tuỳ trụ cột nội dung.
STYLE_PREFIX = (
    "colorful 3D embossed hand-painted style, raised relief texture, thick painterly brush strokes, "
    "dark obsidian background #0A0A0F, moody atmospheric lighting, soft rim light on embossed edges, "
    "vivid colorful palette with a dominant brand accent color "
    "(signal red #FF3B30, data yellow #FFD60A, mind purple #BF5AF2 or nature green #30D158 "
    "depending on scene mood), high detail illustration, vertical portrait composition 9:16, "
    "no text, no people. "
)


def generate_image(scene_id: int, label: str, prompt: str) -> bool:
    filename = f"bg-{scene_id:02d}.jpg"
    out_path = os.path.join(OUT_DIR, filename)

    if os.path.exists(out_path):
        print(f"  [{scene_id}] {filename} đã tồn tại — bỏ qua")
        return True

    full_prompt = STYLE_PREFIX + prompt
    print(f"\n[{filename}] {label} ...")

    for attempt in range(3):
        r = requests.post(
            API_URL,
            headers=HEADERS_JSON,
            json={
                "prompt":                full_prompt,
                "size":                  "1080x1920",
                "num_inference_steps":   30,
                "guidance_scale":        3.8,
                "enable_safety_checker": False,
                "num_images":            1,
            },
            timeout=30,
        )
        print(f"  HTTP {r.status_code}")

        if r.status_code == 429:
            wait = 20 + attempt * 10
            print(f"  Rate limit — chờ {wait}s ...")
            time.sleep(wait)
            continue

        body     = r.json()
        data     = body.get("data", body)
        pred_id  = data.get("id")
        urls_obj = data.get("urls", {})
        poll_url = urls_obj.get("get") if isinstance(urls_obj, dict) else None

        if not pred_id or not poll_url:
            print(f"  ERROR: {json.dumps(data)[:200]}")
            return False

        print(f"  Prediction: {pred_id}")
        img_url = None
        for i in range(120):
            time.sleep(3)
            p      = requests.get(poll_url, headers=HEADERS_AUTH, timeout=15)
            d      = p.json().get("data", p.json())
            status = d.get("status", "")
            err    = d.get("error", "")
            print(f"  [{i*3:3d}s] {status} {err[:40]}")
            if status in ("completed", "succeeded"):
                outs    = d.get("outputs", [])
                img_url = outs[0] if outs else None
                break
            if status == "failed":
                print(f"  FAILED: {json.dumps(d)[:200]}")
                return False

        if not img_url:
            print("  ERROR: Không nhận được URL ảnh")
            return False

        ir  = requests.get(img_url, timeout=60)
        img = Image.open(BytesIO(ir.content)).convert("RGB")

        scale = max(TARGET_W / img.width, TARGET_H / img.height)
        img   = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
        left  = (img.width  - TARGET_W) // 2
        top   = (img.height - TARGET_H) // 2
        img   = img.crop((left, top, left + TARGET_W, top + TARGET_H))
        img.save(out_path, "JPEG", quality=93)

        kb = os.path.getsize(out_path) // 1024
        print(f"  Saved: {filename} ({kb} KB)")
        return True

    return False


if __name__ == "__main__":
    cfg    = get_video_config()
    scenes = get_scenes()

    print("=" * 60)
    print(f"Video  : {cfg['title']}")
    print(f"Scenes : {len(scenes)} cảnh minh họa (Wavespeed AI)")
    print("=" * 60)

    ok = 0
    for i, scene in enumerate(scenes):
        if generate_image(scene["id"], scene["label"], scene["imagePrompt"]):
            ok += 1
        else:
            print(f"  !! Thất bại: bg-{scene['id']:02d} ({scene['label']})")
        if i < len(scenes) - 1:
            time.sleep(8)

    print(f"\n{'='*60}")
    print(f"Hoàn thành: {ok}/{len(scenes)} ảnh")
    if ok == len(scenes):
        print("Tất cả ảnh sẵn sàng → npm start để xem preview")
    else:
        print("Một số ảnh thất bại. Chạy lại để retry (ảnh đã có sẽ bỏ qua).")
    print("=" * 60)
