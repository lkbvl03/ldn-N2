// Effects.tsx — Cinematic emphasis effects synced to documentary audio
// Inspired by: ho-so-cac-mau-hieu-ung-text.txt + ho-so-cac-mau-hieu-ung-icon-3d.txt
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { FPS } from "./data";

const GOLD    = "#c9a84c";
const PURPLE  = "#C77DFF";   // accent kênh LDN — video tâm lý học
const YELLOW  = "#ffd60a";
const RED     = "#E63946";
const FONT_HEADING = '"Arial Black", "Arial Bold", Arial, sans-serif';
const FONT_BODY    = '"Segoe UI", "Arial", sans-serif';

// ─── Helpers ─────────────────────────────────────────────────────────────────

function easeOut(t: number) {
  return 1 - Math.pow(1 - t, 3);
}

function spring(frame: number, fps = 30, stiffness = 180, damping = 22) {
  // Simple spring approximation
  const omega = Math.sqrt(stiffness);
  const zeta = damping / (2 * omega);
  const t = frame / fps;
  if (zeta < 1) {
    const omegaD = omega * Math.sqrt(1 - zeta * zeta);
    return 1 - Math.exp(-zeta * omega * t) * (Math.cos(omegaD * t) + (zeta / Math.sqrt(1 - zeta * zeta)) * Math.sin(omegaD * t));
  }
  return 1 - Math.exp(-omega * t) * (1 + omega * t);
}

// ─── 1. SLASH SECTION CARD (Hiệu ứng E: Slash Transition) ───────────────────
// Xuất hiện ở bottom-left khi bắt đầu mỗi Bước

const SlashSectionCard: React.FC<{
  frame: number;
  label: string;   // "BƯỚC 1"
  title: string;   // "DOPAMINE"
  emoji: string;
  color: string;
}> = ({ frame, label, title, emoji, color }) => {
  const ENTER = 18; // 0.6s
  const HOLD = 120; // 4s — đủ để đọc
  const EXIT = 15;  // 0.5s
  const total = ENTER + HOLD + EXIT;

  if (frame < 0 || frame > total) return null;

  const slideX = interpolate(frame, [0, ENTER], [-340, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: easeOut,
  });
  const opacity = interpolate(
    frame,
    [0, 8, ENTER + HOLD, total],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const scaleX = interpolate(frame, [0, ENTER], [0.6, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: easeOut,
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 165,
        left: 54,
        opacity,
        transform: `translateX(${slideX}px)`,
      }}
    >
      {/* Shadow slash */}
      <div style={{
        position: "absolute",
        top: 6, left: 6,
        width: 280, height: 68,
        clipPath: "polygon(2% 0%, 100% 0%, 98% 100%, 0% 100%)",
        background: "rgba(0,0,0,0.45)",
        zIndex: 0,
      }} />
      {/* Main slash bar */}
      <div style={{
        position: "relative",
        width: 280, height: 68,
        clipPath: "polygon(2% 0%, 100% 0%, 98% 100%, 0% 100%)",
        background: `linear-gradient(90deg, ${color}ee, ${color}aa)`,
        display: "flex",
        alignItems: "center",
        paddingLeft: 18,
        gap: 10,
        zIndex: 1,
        transform: `scaleX(${scaleX})`,
        transformOrigin: "left center",
      }}>
        <span style={{ fontSize: 28, lineHeight: 1 }}>{emoji}</span>
        <div>
          <div style={{
            fontSize: 10,
            fontFamily: FONT_BODY,
            color: "rgba(0,0,0,0.6)",
            letterSpacing: "0.25em",
            fontWeight: 700,
            textTransform: "uppercase",
          }}>{label}</div>
          <div style={{
            fontSize: 19,
            fontFamily: FONT_HEADING,
            fontWeight: 900,
            color: "#000",
            letterSpacing: "0.04em",
            lineHeight: 1.1,
          }}>{title}</div>
        </div>
      </div>
      {/* Accent line */}
      <div style={{
        height: 2,
        width: interpolate(frame, [ENTER, ENTER + 10], [0, 280], {
          extrapolateLeft: "clamp", extrapolateRight: "clamp"
        }),
        background: GOLD,
        marginTop: 3,
        transformOrigin: "left",
      }} />
    </div>
  );
};

// ─── 2. COUNTER REVEAL (Hiệu ứng G: Counter Reveal) ─────────────────────────
// Vị trí: góc trên-trái, có backdrop tối rõ ràng

const CounterReveal: React.FC<{
  frame: number;
  value: string;
  label: string;
  sublabel?: string;
}> = ({ frame, value, label, sublabel }) => {
  const ENTER = 20;
  const HOLD = 75;
  const EXIT = 18;
  const total = ENTER + HOLD + EXIT;

  if (frame < 0 || frame > total) return null;

  const sp = Math.min(spring(Math.min(frame, ENTER), 30, 220, 20), 1);
  const opacity = interpolate(
    frame,
    [0, 10, ENTER + HOLD, total],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const slideY = interpolate(frame, [0, ENTER], [24, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut,
  });
  const barW = interpolate(frame, [ENTER, ENTER + 14], [0, 100], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <div style={{
      position: "absolute",
      top: 110,
      left: 54,
      opacity,
      transform: `translateY(${slideY}px)`,
      textAlign: "center",
    }}>
      {/* Backdrop */}
      <div style={{
        background: "rgba(0,0,0,0.65)",
        backdropFilter: "blur(6px)",
        borderRadius: 12,
        border: `1px solid ${GOLD}55`,
        padding: "16px 28px 18px",
        display: "inline-block",
        minWidth: 180,
      }}>
        <div style={{
          fontSize: 11,
          fontFamily: FONT_BODY,
          color: "rgba(255,255,255,0.45)",
          letterSpacing: "0.3em",
          textTransform: "uppercase",
          marginBottom: 6,
        }}>{label}</div>
        <div style={{
          fontSize: 76,
          fontFamily: FONT_HEADING,
          fontWeight: 900,
          color: "#fff",
          lineHeight: 1,
          transform: `scale(${sp})`,
          textShadow: `0 0 40px ${GOLD}88, 0 3px 10px rgba(0,0,0,0.9)`,
        }}>{value}</div>
        <div style={{
          width: barW,
          height: 2,
          background: GOLD,
          margin: "10px auto 0",
          boxShadow: `0 0 8px ${GOLD}`,
        }} />
        {sublabel && (
          <div style={{
            fontSize: 11,
            fontFamily: FONT_BODY,
            color: `${GOLD}cc`,
            letterSpacing: "0.15em",
            textTransform: "uppercase",
            marginTop: 8,
            opacity: interpolate(frame, [ENTER + 8, ENTER + 20], [0, 1], {
              extrapolateLeft: "clamp", extrapolateRight: "clamp",
            }),
          }}>{sublabel}</div>
        )}
      </div>
    </div>
  );
};

// ─── 3. KEYWORD GLOW (Hiệu ứng B: Particle Title + chữ nổi sáng) ─────────────
// Vị trí: góc trên-phải để không đè chủ thể video

const KeywordGlow: React.FC<{
  frame: number;
  text: string;
  color?: string;
  position?: "center" | "bottom" | "top-right";
}> = ({ frame, text, color = PURPLE, position = "top-right" }) => {
  const ENTER = 12;
  const HOLD = 80;  // ~2.7s — đủ để mắt bắt kịp
  const EXIT = 14;
  const total = ENTER + HOLD + EXIT;

  if (frame < 0 || frame > total) return null;

  const sp = Math.min(spring(Math.min(frame, ENTER), 30, 300, 18), 1);
  const opacity = interpolate(
    frame,
    [0, 6, ENTER + HOLD, total],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const slideY = interpolate(frame, [0, ENTER], [20, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut,
  });

  const posStyle: React.CSSProperties =
    position === "center"
      ? { top: "18%", left: "50%", transform: `translateX(-50%) translateY(${slideY}px) scale(${sp})`, textAlign: "center" }
      : position === "bottom"
      ? { bottom: 130, left: "50%", transform: `translateX(-50%) translateY(${slideY}px) scale(${sp})`, textAlign: "center" }
      : { top: 120, right: 52, transform: `translateY(${slideY}px) scale(${sp})`, textAlign: "right" };

  return (
    <div style={{
      position: "absolute",
      ...posStyle,
      opacity,
      pointerEvents: "none",
    }}>
      {/* Backdrop tối để dễ đọc trên bất kỳ nền nào */}
      <div style={{
        background: "rgba(0,0,0,0.55)",
        backdropFilter: "blur(4px)",
        borderRadius: 8,
        padding: "10px 22px",
        border: `1px solid ${color}44`,
        display: "inline-block",
      }}>
        <div style={{
          fontSize: 44,
          fontFamily: FONT_HEADING,
          fontWeight: 900,
          color: "#fff",
          letterSpacing: "0.08em",
          textTransform: "uppercase",
          textShadow: `0 0 30px ${color}cc, 0 2px 8px rgba(0,0,0,0.9)`,
          whiteSpace: "nowrap",
        }}>{text}</div>
        <div style={{
          width: "100%",
          height: 2,
          background: color,
          opacity: 0.85,
          marginTop: 6,
          boxShadow: `0 0 10px ${color}`,
        }} />
      </div>
    </div>
  );
};

// ─── 4. WOBBLE EMOJI (Hiệu ứng icon 3D: float + bounce ngộ nghĩnh) ───────────

const WobbleEmoji: React.FC<{
  frame: number;
  emoji: string;
  x: number;  // 0-100 % từ trái
  y: number;  // 0-100 % từ trên
  size?: number;
  delay?: number;
}> = ({ frame, emoji, x, y, size = 104, delay = 0 }) => {
  const scaledSize = Math.round(size * 1.7);
  const f = Math.max(0, frame - delay);
  const LIFE = 110; // giữ thêm 1/3s
  if (f < 0 || f > LIFE + 20) return null;

  const sp = Math.min(spring(Math.min(f, 12), 30, 280, 15), 1.1);
  const opacity = interpolate(f, [0, 8, LIFE, LIFE + 22], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  // Float wave — chậm hơn, tự nhiên hơn
  const waveY = Math.sin((f / 38) * Math.PI) * 9;
  // Tilt wobble — nhẹ nhàng
  const tilt = Math.sin((f / 52) * Math.PI) * 6;

  return (
    <div style={{
      position: "absolute",
      left: `${x}%`,
      top: `${y}%`,
      transform: `translate(-50%, -50%) scale(${sp}) translateY(${waveY}px) rotate(${tilt}deg)`,
      opacity,
      fontSize: scaledSize,
      lineHeight: 1,
      filter: "drop-shadow(0 8px 20px rgba(0,0,0,0.7)) drop-shadow(0 0 30px rgba(255,255,255,0.15))",
      pointerEvents: "none",
    }}>
      {emoji}
    </div>
  );
};

// ─── 5. WAVE QUOTE (Hiệu ứng F: Fade-up Quote với wave accent) ───────────────

const WaveQuote: React.FC<{
  frame: number;
  text: string;
  accent?: string;
}> = ({ frame, text, accent = GOLD }) => {
  const ENTER = 20;
  const HOLD = 130; // ~4.3s — đủ đọc 2 dòng
  const EXIT = 18;
  const total = ENTER + HOLD + EXIT;

  if (frame < 0 || frame > total) return null;

  const slideY = interpolate(frame, [0, ENTER], [28, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: easeOut,
  });
  const opacity = interpolate(frame, [0, ENTER, ENTER + HOLD, total], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const barW = interpolate(frame, [6, ENTER], [0, 40], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <div style={{
      position: "absolute",
      bottom: 185,
      left: 54,
      maxWidth: 740,
      opacity,
      transform: `translateY(${slideY}px)`,
    }}>
      {/* Backdrop */}
      <div style={{
        background: "rgba(0,0,0,0.68)",
        backdropFilter: "blur(6px)",
        borderRadius: "0 10px 10px 0",
        borderLeft: `3px solid ${accent}`,
        padding: "14px 22px 16px",
      }}>
        <div style={{
          width: barW,
          height: 3,
          background: accent,
          marginBottom: 12,
          boxShadow: `0 0 10px ${accent}`,
        }} />
        <div style={{
          fontSize: 23,
          fontFamily: FONT_BODY,
          fontStyle: "normal",
          fontWeight: 500,
          color: "#ffffff",
          lineHeight: 1.7,
          textShadow: "0 1px 4px rgba(0,0,0,0.9)",
          whiteSpace: "pre-line",
        }}>{text}</div>
      </div>
    </div>
  );
};

// ─── 6. LETTERBOX TRANSITION (Hiệu ứng A: Letterbox Title) ──────────────────
// Thanh đen trên/dưới kiểu rạp chiếu phim cho transition section

const LetterboxFlash: React.FC<{ frame: number; text: string }> = ({ frame, text }) => {
  const ENTER = 8;
  const HOLD = 45;
  const EXIT = 12;
  const total = ENTER + HOLD + EXIT;

  if (frame < 0 || frame > total) return null;

  const barH = interpolate(frame, [0, ENTER, ENTER + HOLD, total], [0, 90, 90, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const textOpacity = interpolate(frame, [ENTER, ENTER + 12, ENTER + HOLD, total], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: barH, background: "#000" }} />
      <div style={{ position: "absolute", bottom: 0, left: 0, right: 0, height: barH, background: "#000" }} />
      <div style={{
        position: "absolute", top: "50%", left: "50%",
        transform: "translate(-50%, -50%)",
        opacity: textOpacity, textAlign: "center",
      }}>
        <div style={{
          fontSize: 30,
          fontFamily: FONT_BODY,
          color: "#fff",
          letterSpacing: "0.2em",
          textTransform: "uppercase",
          fontWeight: 700,
          whiteSpace: "pre-line",
          textAlign: "center",
        }}>{text}</div>
        <div style={{ width: 140, height: 1, background: `${GOLD}99`, margin: "10px auto 0" }} />
      </div>
    </>
  );
};

// ─── EFFECTS TIMELINE ─────────────────────────────────────────────────────────
// startSec = playback seconds trong video thực
// Điền lại danh sách effects bám sát kịch bản mới sau khi có voice.mp3 + calc_timestamps.py

type EffectItem =
  | { type: "slash"; startSec: number; label: string; title: string; emoji: string; color: string }
  | { type: "counter"; startSec: number; value: string; label: string; sublabel?: string }
  | { type: "keyword"; startSec: number; text: string; color?: string; position?: "center" | "bottom" }
  | { type: "emoji"; startSec: number; emoji: string; x: number; y: number; size?: number; delay?: number }
  | { type: "quote"; startSec: number; text: string; accent?: string }
  | { type: "letterbox"; startSec: number; text: string };

export const EFFECTS: EffectItem[] = [];

// ─── MAIN EFFECTS LAYER ───────────────────────────────────────────────────────

const MAX_EFFECT_WINDOW_SEC = 6.5; // max duration của bất kỳ effect nào

export const EffectsLayer: React.FC = () => {
  const frame = useCurrentFrame();
  const currentSec = frame / FPS;

  return (
    <AbsoluteFill style={{ pointerEvents: "none" }}>
      {EFFECTS.map((effect, idx) => {
        const elapsed = currentSec - effect.startSec;
        // Bỏ qua effects chưa đến hoặc đã qua — giảm DOM elements thừa
        if (elapsed < -0.5 || elapsed > MAX_EFFECT_WINDOW_SEC) return null;
        const localFrame = Math.round(elapsed * FPS);

        switch (effect.type) {
          case "slash":
            return (
              <SlashSectionCard
                key={idx}
                frame={localFrame}
                label={effect.label}
                title={effect.title}
                emoji={effect.emoji}
                color={effect.color}
              />
            );
          case "counter":
            return (
              <CounterReveal
                key={idx}
                frame={localFrame}
                value={effect.value}
                label={effect.label}
                sublabel={effect.sublabel}
              />
            );
          case "keyword":
            return (
              <KeywordGlow
                key={idx}
                frame={localFrame}
                text={effect.text}
                color={effect.color}
                position={effect.position}
              />
            );
          case "emoji":
            return (
              <WobbleEmoji
                key={idx}
                frame={localFrame}
                emoji={effect.emoji}
                x={effect.x}
                y={effect.y}
                size={effect.size}
                delay={effect.delay}
              />
            );
          case "quote":
            return (
              <WaveQuote
                key={idx}
                frame={localFrame}
                text={effect.text}
                accent={effect.accent}
              />
            );
          case "letterbox":
            return (
              <LetterboxFlash
                key={idx}
                frame={localFrame}
                text={effect.text}
              />
            );
        }
      })}
    </AbsoluteFill>
  );
};
