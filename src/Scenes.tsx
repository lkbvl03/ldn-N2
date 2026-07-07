// Scenes.tsx — ảnh nền theo từng SCENE, cinematic Ken Burns + transitions
// Mỗi scene có thời lượng ĐÚNG bằng file giọng đọc thật của nó (xem
// src/calculateMetadata.ts) — không còn SECTION_MAP ước lượng thủ công.
import React from "react";
import {
  AbsoluteFill,
  interpolate,
  Sequence,
  Img,
  useCurrentFrame,
  staticFile,
} from "remotion";
import { FPS, SCENES } from "./data";
import type { SceneTiming } from "./calculateMetadata";

const FADE_IN_FRAMES  = 25;           // cross-dissolve vào
const FADE_OUT_FRAMES = 25;           // cross-dissolve ra
const FLASH_FRAMES    = 4;            // flash tím khi scene bắt đầu (trừ scene đầu)
const PURPLE_ACCENT   = "#C77DFF";

function imagePathForScene(sceneId: number): string {
  return `images/bg/bg-${String(sceneId).padStart(2, "0")}.jpg`;
}

// ── 4 kiểu Ken Burns xoay vòng ───────────────────────────────────────────────
function kenBurns(slotIndex: number, progress: number) {
  const type = slotIndex % 4;
  switch (type) {
    case 0: // Zoom in chậm + pan phải→trái
      return { scale: 1.0 + progress * 0.09, x: progress * -1.4, y: 0, rot: 0 };
    case 1: // Zoom out nhẹ + pan trái→phải
      return { scale: 1.09 - progress * 0.09, x: -1.4 + progress * 1.4, y: 0, rot: 0 };
    case 2: // Chéo: trên-trái → dưới-phải + zoom in
      return { scale: 1.04 + progress * 0.06, x: progress * -1.0, y: progress * -0.6, rot: progress * 0.25 };
    case 3: // Chéo: dưới-phải → trên-trái + zoom out
      return { scale: 1.10 - progress * 0.06, x: -1.0 + progress * 1.0, y: -0.6 + progress * 0.6, rot: -progress * 0.25 };
    default:
      return { scale: 1.0, x: 0, y: 0, rot: 0 };
  }
}

// ── Single scene image ───────────────────────────────────────────────────────
const SingleImage: React.FC<{ src: string; slotIndex: number; durationFrames: number }> = ({
  src,
  slotIndex,
  durationFrames,
}) => {
  const frame = useCurrentFrame();

  // Cross-dissolve: fade in + fade out
  const fadeOutStart = Math.max(FADE_IN_FRAMES, durationFrames - FADE_OUT_FRAMES);
  const opacity = interpolate(
    frame,
    [0, FADE_IN_FRAMES, fadeOutStart, durationFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Ken Burns progress 0→1
  const kbProgress = interpolate(frame, [0, durationFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Punch scale khi vào: từ 1.07 → 1.0 trong 22 frame (easeOut cubic)
  const punchScale = interpolate(frame, [0, 22], [1.07, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });

  const kb = kenBurns(slotIndex, kbProgress);
  const finalScale = kb.scale * punchScale;

  // Flash tím tại điểm bắt đầu scene (trừ scene đầu tiên của video)
  const flashOpacity =
    slotIndex > 0
      ? interpolate(frame, [0, FLASH_FRAMES], [0.35, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        })
      : 0;

  return (
    <AbsoluteFill style={{ opacity, overflow: "hidden" }}>
      <div
        style={{
          width: "100%",
          height: "100%",
          transform: `scale(${finalScale}) translateX(${kb.x}%) translateY(${kb.y}%) rotate(${kb.rot}deg)`,
          transformOrigin: "center center",
          willChange: "transform",
        }}
      >
        <Img
          src={staticFile(src)}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
          onError={() => console.warn(`Image load error: ${src}`)}
        />
      </div>
      {flashOpacity > 0 && (
        <AbsoluteFill
          style={{
            background: `radial-gradient(ellipse at center, ${PURPLE_ACCENT}88 0%, transparent 70%)`,
            opacity: flashOpacity,
            pointerEvents: "none",
            mixBlendMode: "screen",
          }}
        />
      )}
    </AbsoluteFill>
  );
};

// ── Vignette + color grade + scanlines ───────────────────────────────────────
const CinematicOverlay: React.FC<{ globalFrame: number }> = ({ globalFrame }) => {
  const fadeIn = interpolate(globalFrame, [0, 60], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Vignette thở nhẹ theo sin — chu kỳ ~4 giây
  const breathe = 1 + Math.sin((globalFrame / FPS / 4) * Math.PI * 2) * 0.04;

  return (
    <AbsoluteFill style={{ opacity: fadeIn, pointerEvents: "none" }}>
      {/* Top vignette */}
      <div style={{
        position: "absolute", top: 0, left: 0, right: 0,
        height: Math.round(200 * breathe),
        background: "linear-gradient(180deg, rgba(2,5,8,0.80) 0%, transparent 100%)",
      }} />
      {/* Bottom vignette */}
      <div style={{
        position: "absolute", bottom: 0, left: 0, right: 0,
        height: Math.round(240 * breathe),
        background: "linear-gradient(0deg, rgba(2,5,8,0.85) 0%, transparent 100%)",
      }} />
      {/* Left vignette */}
      <div style={{
        position: "absolute", top: 0, left: 0, bottom: 0,
        width: 180,
        background: "linear-gradient(90deg, rgba(2,5,8,0.50) 0%, transparent 100%)",
      }} />
      {/* Right vignette */}
      <div style={{
        position: "absolute", top: 0, right: 0, bottom: 0,
        width: 180,
        background: "linear-gradient(270deg, rgba(2,5,8,0.50) 0%, transparent 100%)",
      }} />
      {/* Purple psychology tint */}
      <div style={{
        position: "absolute", inset: 0,
        background: "linear-gradient(135deg, rgba(40,0,60,0.14) 0%, transparent 45%, rgba(10,0,30,0.10) 100%)",
        mixBlendMode: "color",
      }} />
      {/* Film grain scanlines */}
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage:
          "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,0,0,0.028) 3px, rgba(0,0,0,0.028) 4px)",
      }} />
    </AbsoluteFill>
  );
};

// ── Exported VideoBackground ──────────────────────────────────────────────────
export const VideoBackground: React.FC<{
  globalFrame: number;
  sceneTimings: SceneTiming[];
}> = ({ globalFrame, sceneTimings }) => {
  return (
    <AbsoluteFill style={{ background: "#020508" }}>
      {sceneTimings.map((timing, i) => {
        const scene = SCENES.find((s) => s.id === timing.id);
        // Bỏ qua scene giả (id=0 fallback khi SCENES rỗng) — không có ảnh thật
        if (!scene) return null;
        return (
          <Sequence
            key={timing.id}
            from={timing.fromFrame}
            durationInFrames={timing.durationFrames}
            layout="none"
          >
            <SingleImage
              src={imagePathForScene(scene.id)}
              slotIndex={i}
              durationFrames={timing.durationFrames}
            />
          </Sequence>
        );
      })}
      <CinematicOverlay globalFrame={globalFrame} />
    </AbsoluteFill>
  );
};
