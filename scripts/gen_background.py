"""
Tạo background image bằng Wavespeed AI (Flux Dev).
Chỉnh PROMPT bên dưới theo chủ đề video.

Chạy: python -X utf8 scripts/gen_background.py
"""
import requests, json, time, os, sys
from PIL import Image
from io import BytesIO

sys.stdout.reconfigure(encoding='utf-8')

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ[k.strip()] = v.strip()

load_env()

API_KEY = os.environ.get('WAVESPEED_API_KEY', '')
if not API_KEY or API_KEY == 'your_wavespeed_api_key_here':
    print("LỖI: Chưa cấu hình WAVESPEED_API_KEY trong .env")
    sys.exit(1)

HDR_AUTH = {"Authorization": f"Bearer {API_KEY}"}
HDR_JSON = {**HDR_AUTH, "Content-Type": "application/json"}

# ← CHỈNH: mô tả hình nền phù hợp chủ đề video
# Phong cách "colorful 3D embossed hand-painted" theo hồ sơ thương hiệu LDN
# (Du-lieu-lam-video/thuong-hieu-LDN.txt) — nền Obsidian tối, điểm nhấn màu thương hiệu
PROMPT = (
    "colorful 3D embossed hand-painted style, raised relief texture, thick painterly brush strokes, "
    "abstract scientific visualization, "
    "dark obsidian background #0A0A0F, "
    "vivid colorful palette with a dominant brand accent color splash "
    "(signal red #FF3B30, data yellow #FFD60A, mind purple #BF5AF2 or nature green #30D158), "
    "moody atmosphere, high detail illustration, vertical portrait composition 9:16, "
    "no text, no people"
)

OUT = os.path.join(os.path.dirname(__file__), "..", "public", "images", "background.jpg")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

print("Tạo background image via Wavespeed AI...")
r = requests.post(
    "https://api.wavespeed.ai/api/v2/wavespeed-ai/flux-dev",
    headers=HDR_JSON,
    json={
        "prompt":               PROMPT,
        "size":                 "1080x1920",
        "num_inference_steps":  28,
        "guidance_scale":       3.5,
        "enable_safety_checker": False,
        "num_images":           1,
    },
    timeout=30,
)
print(f"HTTP {r.status_code}")
body = r.json()

data     = body.get("data", body)
pred_id  = data.get("id")
urls_obj = data.get("urls", {})
poll_url = urls_obj.get("get") if isinstance(urls_obj, dict) else None

if not pred_id or not poll_url:
    print("ERROR: Không có prediction ID hoặc poll URL")
    sys.exit(1)

print(f"Prediction ID: {pred_id}")

img_url = None
for i in range(120):
    time.sleep(3)
    p      = requests.get(poll_url, headers=HDR_AUTH, timeout=15)
    pd     = p.json()
    d      = pd.get("data", pd)
    status = d.get("status", "")
    err    = d.get("error", "")
    print(f"  [{i*3:3d}s] status={status:<12} err={err[:40]}")
    if status in ("completed", "succeeded"):
        outs    = d.get("outputs", [])
        img_url = outs[0] if outs else None
        break
    if status == "failed":
        print(f"THẤT BẠI: {json.dumps(d)[:300]}")
        sys.exit(1)

if not img_url:
    print("ERROR: Không lấy được URL ảnh.")
    sys.exit(1)

ir  = requests.get(img_url, timeout=60)
img = Image.open(BytesIO(ir.content))
print(f"Kích thước gốc: {img.size}")

# Scale & crop về 1080x1920 (dọc 9:16)
target_w, target_h = 1080, 1920
scale = max(target_w / img.width, target_h / img.height)
img   = img.resize((int(img.width*scale), int(img.height*scale)), Image.LANCZOS)
left  = (img.width  - target_w) // 2
top   = (img.height - target_h) // 2
img   = img.crop((left, top, left+target_w, top+target_h))

img.save(OUT, "JPEG", quality=92)
print(f"Saved: {OUT} ({os.path.getsize(OUT)//1024} KB, 1080x1920)")
print("HOÀN THÀNH!")
