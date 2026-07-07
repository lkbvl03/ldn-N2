// ═══════════════════════════════════════════════════════════════════
// data.ts — NGUỒN SỰ THẬT DUY NHẤT — KÊNH LẠ ĐỜI NHẤT (LDN)
// Khi làm video mới: CHỈ chỉnh file này. Không chỉnh file nào khác.
// Xem hướng dẫn: Du-lieu-lam-video/ho-so-giong-doc-LDN.txt
// Bảng màu chuẩn kênh: Du-lieu-lam-video/thuong-hieu-LDN.txt
//
// KIẾN TRÚC: mỗi phân cảnh (scene) = 1 đoạn kịch bản + 1 ảnh/video nền +
// 1 file giọng đọc RIÊNG (public/voice/scene-NN.mp3). Remotion tự tính
// thời lượng thật của từng scene lúc runtime (xem calculateMetadata trong
// Root.tsx) — KHÔNG cần ước lượng/ghi tay TOTAL_DURATION_FRAMES nữa.
// ═══════════════════════════════════════════════════════════════════

// ─── FPS ────────────────────────────────────────────────────────────
export const FPS = 30;

// ── VIDEO CONFIG ───────────────────────────────────────────────────
export const VIDEO_CONFIG = {
  title:         "TÊN VIDEO VIẾT HOA",
  subtitle:      "Tagline ngắn",

  // ► Màu accent — chọn từ Du-lieu-lam-video/thuong-hieu-LDN.txt theo trụ cột nội dung
  // Signal Red #FF3B30 (tư tưởng & hành vi) · Nature Green #30D158 (thiên nhiên & khoa học)
  // Mind Purple #BF5AF2 (tâm linh / tâm lý học) · Data Yellow #FFD60A (số liệu, thống kê)
  accentColor:    "#FF3B30",

  // ► Màu highlight nhấn mạnh số liệu
  highlightColor: "#FFD60A",

  // ► Màu nền & chữ (theo Du-lieu-lam-video/thuong-hieu-LDN.txt — không đổi)
  bgColor:       "#0A0A0F",
  primaryText:   "#F5F5F0",
  secondaryText: "#8E8E93",
  lineColor:     "#304050",

  // ► Câu hook mở đầu (hiện trên màn hình)
  hookTitle:    "Câu hook gây sốc",
  hookSubtitle: "Mở rộng hook",

  // ► Nút CTA
  ctaText: "CTA TEXT",

  // ► Nguồn / credit hiện góc dưới phải
  source: "Source A · Source B",

  year: "2026",
  theme: "psychology",
};

// ── SCENES — mỗi phân cảnh = 1 đoạn kịch bản + 1 ảnh/video + 1 giọng đọc ──
// Số lượng KHÔNG cố định — Claude phân tích kịch bản thật để quyết định
// (thường mỗi luận điểm/pattern-interrupt/hook/kết là 1 scene riêng).
//
// text        : kịch bản của RIÊNG scene này (có thể chứa [DỪNG Xs])
//               Quy tắc viết: Du-lieu-lam-video/ho-so-giong-doc-LDN.txt
// imagePrompt : chỉ mô tả NỘI DUNG ảnh — không viết style. Phong cách
//               "colorful 3D embossed hand-painted" + màu thương hiệu được
//               tự động thêm vào bởi scripts/gen_scenes.py
export type Scene = {
  id: number;
  label: string;        // "HOOK", "LĐ1", "PI1", "KẾT"...
  text: string;
  imagePrompt: string;
};

export const SCENES: Scene[] = [];

// ── PIPELINE CONFIG ────────────────────────────────────────────────
export const PIPELINE_CONFIG = {
  // Giọng đọc chuẩn kênh LDN — KHÔNG thay đổi
  VOICE:  "n_yenbai_male_giongnamldn_zero_shot_story_vc",
  RATE:   "0%",
  VOLUME: "+0%",
};
