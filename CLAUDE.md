# CLAUDE.md — Remotion Short-form Video Template

Template Remotion cho video short-form (Shorts/Reels/TikTok) phong cách **colorful 3D
embossed hand-painted** theo hồ sơ thương hiệu kênh LẠ ĐỜI NHẤT.
Layout: **1080×1920 (9:16, dọc)**, nhiều mốc sự kiện, text & icon nổi màu sắc ấn tượng.

Bảng màu, font, giọng điệu chuẩn kênh: xem [`Du-lieu-lam-video/thuong-hieu-LDN.txt`](Du-lieu-lam-video/thuong-hieu-LDN.txt)
(hồ sơ thương hiệu — nguồn sự thật duy nhất cho mọi màu sắc & phong cách hình ảnh).

---

## Kiến trúc: mỗi SCENE = 1 ảnh/video nền + 1 file giọng đọc riêng

Mỗi phân cảnh (`Scene` trong `src/data.ts`) có: 1 đoạn kịch bản riêng, 1
ảnh/video nền riêng, 1 file giọng đọc riêng (`public/voice/scene-NN.mp3`).
Các scene được ghép **nối tiếp nhau** — thời lượng hiển thị của mỗi ảnh/video
= ĐÚNG thời lượng thật của file giọng đọc scene đó. Remotion tự tính tổng thời
lượng composition lúc runtime bằng `calculateMetadata` (`src/calculateMetadata.ts`,
dùng `@remotion/media-utils` đọc thời lượng audio thật) — KHÔNG cần ước lượng
trước rồi sửa tay, KHÔNG cần script "remap".

## Phân công nhiệm vụ (quy trình Claude thực hiện, theo đúng thứ tự)

Nhiệm vụ là: **nhận chủ đề → viết kịch bản → chờ xác nhận → phân tích →
chờ đủ tài nguyên → tạo âm thanh → dựng video → chờ xác nhận lần 2 → render.**
Không nhảy cóc bước nào, không tự ý render khi chưa qua đủ 2 lần xác nhận.

1. **Nhận chủ đề, viết kịch bản** — Claude nhận chủ đề từ người dùng, viết
   **toàn bộ kịch bản giọng đọc** (văn xuôi liền mạch, đúng quy tắc
   `Du-lieu-lam-video/ho-so-giong-doc-LDN.txt` + `Du-lieu-lam-video/cau-truc-ct-viet-kb-ldn.txt`
   — hook 3 lớp, công thức 5 nhịp/luận điểm, kết 4 lớp, marker `[DỪNG Xs]`).
   **CHƯA chia scene, CHƯA viết imagePrompt, CHƯA đụng vào `src/data.ts`.**

2. **Dừng lại, chờ xác nhận kịch bản** — gửi kịch bản cho người dùng đọc
   duyệt. **KHÔNG tự ý tiến hành bước tiếp theo cho tới khi người dùng xác
   nhận kịch bản OK.** Nếu người dùng yêu cầu sửa, sửa lại và chờ xác nhận lại.

3. **Sau khi kịch bản đã được xác nhận** — phân tích kịch bản đã duyệt,
   tính toán để xác định:
   - Cần chia thành **bao nhiêu SCENE** (số lượng KHÔNG cố định — tuỳ độ
     dài/nhịp kịch bản, thường mỗi hook/luận-điểm/pattern-interrupt/kết là
     1 scene riêng)
   - Cần viết **bao nhiêu prompt tạo ảnh/video nền** (= số scene, viết
     `imagePrompt` cho từng scene — mô tả nội dung, không viết style)
   - Cần tạo **bao nhiêu phân đoạn giọng đọc** (= số scene, 1 file
     giọng đọc riêng/scene)

   Rồi điền kết quả vào `SCENES` trong `src/data.ts`.

4. **Chờ đủ tài nguyên** — chạy `step1_voice.py` (giọng đọc) và `gen_scenes.py`
   (ảnh AI) hoặc chờ người dùng cung cấp clip VEO3 (nếu dùng video nền thay
   ảnh tĩnh — quy trình VEO3 là thủ công qua Google Flow, không tự động được).
   **Chưa đủ toàn bộ file video/ảnh nền + toàn bộ file giọng đọc từng scene
   thì chưa qua bước tiếp theo.**

5. **Tạo nhạc nền và hiệu ứng âm thanh** — chạy `generate_audio.py` (nhạc
   nền) và `generate_sfx2.py` (SFX), viết lại nội dung/mốc cảm xúc khớp
   kịch bản đã xác nhận (2 script này không tự sinh theo SCENES, cần điền
   tay nội dung mỗi video).

6. **Chạy pipeline tính thời gian** — `calc_scene_timing.py` để lấy mốc
   giây thật của từng scene, dùng số liệu đó viết `EFFECTS`
   (`src/Effects.tsx`) và `SFX_TIMELINE` (`src/RankingVideo.tsx`).

7. **Edit video** — tạo/tinh chỉnh hiệu ứng chuyển cảnh mượt mà, đẹp mắt
   (dùng các kỹ xảo điện ảnh: Ken Burns, cross-dissolve, flash, letterbox,
   glow... đã có sẵn trong `src/Scenes.tsx` + `src/Effects.tsx`), chuyển
   động cho ảnh/video nền.

8. **Xem bằng `npm start`** (Remotion Studio) — hoàn thiện, chỉnh sửa qua
   lại đến khi người dùng **xác nhận OK lần 2**. Đây là cổng xác nhận thứ
   hai (khác với xác nhận kịch bản ở bước 2) — **KHÔNG render khi chưa có
   xác nhận này.**

9. **Render** — chỉ sau khi đã xác nhận OK ở bước 8:
   `npx remotion render src/index.ts MyVideo out/video.mp4 --codec=h264 --crf=18`

---

## Khi làm video mới

> **Chỉ chỉnh `src/data.ts`. Không chỉnh file nào khác trong `src/`.**

### Bước 1 — Điền `src/data.ts`

Chỉnh 2 khu vực:

**`VIDEO_CONFIG`**
```typescript
title:         "TÊN VIDEO VIẾT HOA",
subtitle:      "Tagline ngắn",
accentColor:   "#FF3B30",    // chọn từ bảng màu bên dưới
hookTitle:     "Câu hook gây sốc",
hookSubtitle:  "Mở rộng hook",
ctaText:       "CTA TEXT",
source:        "Source A · Source B",
```

**`SCENES`** — mảng phân cảnh, số lượng biến thiên theo kịch bản
```typescript
{
  id: 0,
  label: "HOOK",         // "HOOK", "LĐ1", "PI1", "KẾT"...
  text: `...`,            // kịch bản RIÊNG của scene này, dùng marker khoảng lặng
  imagePrompt: "...",     // chỉ mô tả nội dung ảnh — không viết style
},
```

Marker khoảng lặng dùng trong `text` của mỗi scene:
```
[DỪNG 0.5s]   →  0.5 giây im lặng
[DỪNG 1s]     →  1.0 giây im lặng
[DỪNG 2s]     →  2.0 giây im lặng
[DỪNG 3s]     →  3.0 giây im lặng
[DỪNG 4s]     →  4.0 giây im lặng
[DỪNG AS]     →  3.5 giây im lặng (dấu ấn kênh LDN)
```

**`imagePrompt`** — prompt tạo ảnh AI cho scene đó
- Chỉ mô tả **nội dung** (chủ thể, hành động, bối cảnh) — **không viết style**.
- Phong cách **colorful 3D embossed hand-painted** (nổi khối, brush stroke dày, màu
  sắc rực rỡ) + nền tối Obsidian + màu nhấn thương hiệu được tự động thêm vào bởi
  `STYLE_PREFIX` trong `scripts/gen_scenes.py`
  (xem bảng màu chuẩn ở [`Du-lieu-lam-video/thuong-hieu-LDN.txt`](Du-lieu-lam-video/thuong-hieu-LDN.txt)).
- Ví dụ cách viết:
  ```
  "Vietnamese man lying in bed at midnight staring at ceiling, dark bedroom"
  ```
  KHÔNG viết: `"...photorealistic 4K cinematic lighting..."` — phần style đã có sẵn.
- Ảnh sinh ra ở khung dọc **1080×1920 (9:16)** — mô tả bố cục theo chiều dọc
  (chủ thể ở giữa/trên khung, chừa khoảng trống trên-dưới cho text overlay).

---

### Bước 4–6 — Chạy pipeline (tài nguyên → âm thanh → tính thời gian)

```bash
# Bước 4 — chờ đủ tài nguyên (giọng đọc + ảnh/video nền)
python -X utf8 scripts/step1_voice.py       # → public/voice/scene-NN.mp3  (Vbee TTS, 1 file/scene)
python -X utf8 scripts/gen_scenes.py        # → public/images/bg/bg-NN.jpg  (Wavespeed, colorful 3D embossed 1080x1920)
python -X utf8 scripts/gen_veo3_prompts.py  # → Du-lieu-lam-video/veo3_prompts.txt  (Google VEO 3, tuỳ chọn thay ảnh tĩnh)

# Bước 5 — tạo nhạc nền + hiệu ứng âm thanh
python -X utf8 scripts/generate_audio.py    # → public/background-music.wav
python -X utf8 scripts/generate_sfx2.py     # → public/sfx/sfx_*.wav

# Bước 6 — tính mốc thời gian thật để viết EFFECTS/SFX_TIMELINE
python -X utf8 scripts/calc_scene_timing.py
```

Dùng output của `calc_scene_timing.py` để viết `EFFECTS` (`src/Effects.tsx`,
startSec tuyệt đối) và `SFX_TIMELINE` (`src/RankingVideo.tsx`).

> **Biết trước**: `gen_scenes.py`/`gen_background.py` hiện gọi Wavespeed API
> `/api/v2/` — lúc kiểm thử gần nhất (2026-07-06) endpoint này trả lỗi
> `HTTP 403: "This API version is not available for your account. Please
> use the latest /api/v3 endpoints."` Cần migrate 2 script này sang `/api/v3/`
> trước khi dùng để sinh ảnh thật (xem chi tiết ở
> `Du-lieu-lam-video/gioi-thieu-template.txt`, mục X).

### Bước 8 — Xem & hoàn thiện

```bash
npm start                                   # Preview: http://localhost:3000
```

Chỉnh sửa `EFFECTS`/`SFX_TIMELINE`/Ken Burns qua lại đến khi người dùng
**xác nhận OK lần 2**. Thời lượng composition được Remotion tự tính
(`calculateMetadata` đọc thời lượng thật từng `public/voice/scene-NN.mp3`)
— không cần đo/ghi tay.

### Bước 9 — Render (chỉ sau khi đã xác nhận OK ở Bước 8)

```bash
npx remotion render src/index.ts MyVideo out/video.mp4 --codec=h264 --crf=18
```

---

### Giọng đọc Vbee TTS

Script `step1_voice.py` hoạt động (lặp qua từng scene trong `SCENES`):
1. Tách `text` của scene tại mỗi `[DỪNG Xs]` → đoạn text + khoảng im lặng
2. Generate TTS từng đoạn → checkpoint tạm (`public/_voice_chunks/scene-NN/`)
3. Tạo silence chính xác bằng ffmpeg
4. Nối tất cả → `public/voice/scene-NN.mp3` (1 file/scene)
5. Checkpoint tự động theo từng scene: nếu lỗi giữa chừng, chạy lại sẽ
   **skip scene/chunk đã xong**

**Giọng hiện dùng**: `n_yenbai_male_giongnamldn_zero_shot_story_vc`

Các giọng Nam khác:
```
sg_male_minhhoang_full_48k-fhg   — SG Minh Hoàng (trầm ấm)
sg_male_chidat_ebook_48k-phg     — SG Chí Đạt (kể chuyện)
hn_male_thanhlong_talk_48k-fhg   — HN Thanh Long (talk show)
hn_male_manhdung_news_48k-fhg    — HN Mạnh Dũng (tin tức, rõ ràng)
```

---

### Video nền (Google Studio VEO 3) — tuỳ chọn thay ảnh tĩnh

Script `gen_veo3_prompts.py` tự tính số clip 8s cần thiết CHO TỪNG SCENE (dựa
trên độ dài `text` của scene đó).

**Dùng output:**
1. Mở [studio.google.com/flow](https://studio.google.com/flow) → chọn VEO 3, tỉ lệ khung hình **9:16**
2. Copy từng prompt trong `Du-lieu-lam-video/veo3_prompts.txt` → tạo clip 8s
3. Dùng **Character reference** từ clip đầu mỗi scene để đồng bộ nhân vật
4. Ghép các clip của 1 scene lại = video nền cho scene đó (thay cho
   `public/images/bg/bg-NN.jpg` của scene đó)

**Ảnh tĩnh** (mặc định): đặt vào `public/images/bg/bg-00.jpg`, `bg-01.jpg`, ...
(khung dọc 1080×1920, phong cách colorful 3D embossed hand-painted, 1 ảnh/scene,
tên file khớp `id` của scene trong `data.ts` — scene đầu tiên nên đặt `id: 0`)

---

## Cấu trúc

```
src/
  data.ts             ← CHỈNH Ở ĐÂY khi làm video mới (VIDEO_CONFIG + SCENES)
  index.ts
  Root.tsx            ← Composition + calculateMetadata
  calculateMetadata.ts← tự tính durationInFrames + sceneTimings từ audio thật
  RankingVideo.tsx     ← ghép audio theo scene + SFX_TIMELINE (điền tay)
  Scenes.tsx          ← ảnh/video nền theo sceneTimings + Ken Burns
  Effects.tsx         ← EFFECTS array (6 loại hiệu ứng, điền tay theo scene)

scripts/
  _data.py              ← đọc data.ts (get_scenes, get_video_config, ...)
  step1_voice.py        ← tạo public/voice/scene-NN.mp3 (Vbee TTS + silence thực, 1 file/scene)
  calc_scene_timing.py  ← đo thời lượng thật từng scene (ffprobe) — thay calc_timestamps+remap cũ
  gen_scenes.py         ← tạo ảnh AI theo scene (Wavespeed Flux) → bg-NN.jpg
  gen_background.py     ← tạo 1 ảnh nền đơn (Wavespeed Flux, ít dùng)
  generate_audio.py     ← nhạc nền ambient (1 file cho cả video)
  generate_sfx2.py      ← SFX cinematic
  gen_veo3_prompts.py   ← prompts cho Google VEO 3 (theo từng scene)

public/
  voice/                ← scene-00.mp3, scene-01.mp3, ... (1 file/scene)
  background-music.wav  ← nhạc nền
  sfx/                  ← SFX files
  images/bg/            ← bg-00.jpg, bg-01.jpg, ... (1080×1920, colorful 3D embossed, 1 ảnh/scene)

Du-lieu-lam-video/
  thuong-hieu-LDN.txt              ← hồ sơ thương hiệu (màu, style ảnh) — KHÔNG xoá
  ho-so-giong-doc-LDN.txt          ← quy tắc viết kịch bản giọng đọc — KHÔNG xoá
  ho-so-cac-mau-hieu-ung-text.txt  ← hồ sơ hiệu ứng text — KHÔNG xoá
  ho-so-cac-mau-hieu-ung-icon-3d.txt ← hồ sơ hiệu ứng icon 3D — KHÔNG xoá
  cau-truc-ct-viet-kb-ldn.txt      ← cấu trúc kịch bản chuẩn kênh — KHÔNG xoá
  gioi-thieu-template.txt         ← tổng quan template & tiêu chuẩn kỹ thuật — KHÔNG xoá
  veo3_prompts.txt                 ← sinh bởi gen_veo3_prompts.py (xoá được, tạo lại mỗi video)
```

---

## Bảng màu

> Nguồn sự thật duy nhất cho màu sắc & phong cách hình ảnh:
> [`Du-lieu-lam-video/thuong-hieu-LDN.txt`](Du-lieu-lam-video/thuong-hieu-LDN.txt) — luôn đối chiếu file
> này trước khi chọn `accentColor` trong `data.ts` hoặc viết `imagePrompt`.

| Tên màu | Mã hex | Vai trò |
|---------|--------|---------|
| Obsidian | `#0A0A0F` | Nền chính — video & ảnh AI (chiếm tối thiểu 60% diện tích) |
| Signal Red | `#FF3B30` | Trụ cột 1 — Tư tưởng & Hành vi |
| Nature Green | `#30D158` | Trụ cột 2 — Thiên nhiên & Khoa học |
| Mind Purple | `#BF5AF2` | Trụ cột tâm linh / tư tưởng (dùng cho `accentColor` tâm lý học) |
| Data Yellow | `#FFD60A` | Màu nhấn phụ — số liệu, thống kê, counter |
| Ivory White | `#F5F5F0` | Chữ chính trên nền tối |
| Muted White | `#8E8E93` | Chữ phụ — caption, chú thích |
| Deep Gray | `#1C1C1E` | Nền phụ / background thứ cấp |

Quy tắc: mỗi video/ảnh chỉ dùng **tối đa 2 màu** (nền Obsidian + 1 màu nhấn theo
đúng trụ cột nội dung của video đó).

Typography (dùng trong code hiện tại — khác font kênh dùng cho thumbnail/kênh
trong `thuong-hieu-LDN.txt`, phần IV): **Arial Black** (headline) ·
*Segoe UI Italic* (tagline) · Arial (body)

---

## Lưu ý

- **Chỉ render (`npx remotion render`) sau khi đã xem qua `npm start` và
  người dùng xác nhận OK** (2 lần xác nhận trong quy trình: 1 lần cho kịch
  bản ở bước 2, 1 lần cho video hoàn thiện ở bước 8, trước khi render ở
  bước 9 — xem "Phân công nhiệm vụ").
- Chạy Python với `python -X utf8` trên Windows
- Vbee và Wavespeed đều cần internet
- **Wavespeed API `/api/v2/` hiện lỗi 403 cho tài khoản này** (xác nhận
  2026-07-06) — cần migrate `gen_scenes.py`/`gen_background.py` sang
  `/api/v3/` trước khi sinh ảnh thật (xem `Du-lieu-lam-video/gioi-thieu-template.txt`)
- `gen_scenes.py` bỏ qua ảnh đã tồn tại — chạy lại an toàn
- `step1_voice.py` có checkpoint theo từng scene — nếu lỗi giữa chừng, chạy
  lại để resume
- Cài dependencies: `pip install requests pillow numpy`
- Composition (`src/Root.tsx`) cố định **1080×1920** — không đổi sang ngang
- Thời lượng composition tự tính qua `calculateMetadata` (đọc thời lượng thật
  của `public/voice/scene-NN.mp3`) — KHÔNG có `TOTAL_DURATION_FRAMES` để ghi
  tay nữa
- Template đang ở trạng thái **trống** (`SCENES: []`): `EFFECTS`
  (Effects.tsx), `SFX_TIMELINE` (RankingVideo.tsx) đều rỗng — điền lại sau
  Bước 6 (dùng output `calc_scene_timing.py`)
