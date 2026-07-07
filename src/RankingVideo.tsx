import React from "react";
import {
  Audio,
  useCurrentFrame,
  interpolate,
  staticFile,
  AbsoluteFill,
  Sequence,
} from "remotion";
import { VIDEO_CONFIG, FPS, SCENES } from "./data";
import { VideoBackground } from "./Scenes";
import { EffectsLayer } from "./Effects";
import type { RankingVideoProps } from "./calculateMetadata";

// SFX timeline — khớp với scripts/generate_sfx2.py cho video này
const T = (sec: number) => Math.round(sec * FPS);

// SFX calibrated từ scripts/calc_scene_timing.py — điền lại sau khi có voice + generate_sfx2.py mới
const SFX_TIMELINE: { fromFrame: number; file: string; volume: number }[] = [];

// ── Opening title card (first 8 seconds) ─────────────────────────────
const OpeningTitle: React.FC<{ frame: number }> = ({ frame }) => {
  if (frame > 240) return null;

  const opacity = interpolate(frame, [0, 20, 175, 225], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const slideY = interpolate(frame, [0, 40], [28, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const accent = VIDEO_CONFIG.accentColor;

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity,
        transform: `translateY(${slideY}px)`,
        pointerEvents: "none",
      }}
    >
      {/* Accent line */}
      <div
        style={{
          width: 2,
          height: 56,
          background: accent,
          opacity: 0.65,
          marginBottom: 22,
        }}
      />
      {/* Main title */}
      <div
        style={{
          fontSize: 46,
          fontWeight: 900,
          fontFamily: "'Arial Black', 'Arial', sans-serif",
          color: "#FFFFFF",
          textAlign: "center",
          letterSpacing: "0.05em",
          textShadow: `0 0 40px ${accent}70`,
          maxWidth: 960,
          lineHeight: 1.25,
          padding: "0 40px",
        }}
      >
        {VIDEO_CONFIG.title}
      </div>
      {/* Subtitle */}
      <div
        style={{
          fontSize: 22,
          fontFamily: '"Segoe UI", Arial, sans-serif',
          fontStyle: "italic",
          color: "#C7D5E0",
          marginTop: 18,
          letterSpacing: "0.10em",
          opacity: 0.82,
        }}
      >
        {VIDEO_CONFIG.subtitle}
      </div>
      {/* Bottom line */}
      <div
        style={{
          width: 100,
          height: 1,
          background: accent,
          opacity: 0.40,
          marginTop: 22,
        }}
      />
    </AbsoluteFill>
  );
};

// ── Main composition ─────────────────────────────────────────────────
export const RankingVideo: React.FC<RankingVideoProps> = ({ sceneTimings }) => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ background: "#020508" }}>
      {/* ── VIDEO BACKGROUND (1 ảnh/video mỗi scene) ──────────────── */}
      <VideoBackground globalFrame={frame} sceneTimings={sceneTimings} />

      {/* ── GIỌNG ĐỌC — 1 file riêng mỗi scene, nối tiếp nhau ─────── */}
      {/* Lọc bỏ scene giả (id=0 fallback khi SCENES rỗng) — không có file thật */}
      {sceneTimings
        .filter((timing) => SCENES.some((s) => s.id === timing.id))
        .map((timing) => (
          <Sequence
            key={timing.id}
            from={timing.fromFrame}
            durationInFrames={timing.durationFrames}
          >
            <Audio
              src={staticFile(`voice/scene-${String(timing.id).padStart(2, "0")}.mp3`)}
              volume={1}
            />
          </Sequence>
        ))}

      {/* ── NHẠC NỀN ──────────────────────────────────────────────── */}
      <Audio src={staticFile("background-music.wav")} volume={0.11} />

      {/* ── SFX ───────────────────────────────────────────────────── */}
      {SFX_TIMELINE.map(({ fromFrame, file, volume }, i) => (
        <Sequence key={i} from={fromFrame}>
          <Audio src={staticFile(file)} volume={volume} />
        </Sequence>
      ))}

      {/* ── CINEMATIC EFFECTS (keyword glow, counters, emoji, slash cards) ── */}
      <EffectsLayer />

      {/* ── OPENING TITLE ─────────────────────────────────────────── */}
      <OpeningTitle frame={frame} />

      {/* ── SOURCE WATERMARK ──────────────────────────────────────── */}
      <div
        style={{
          position: "absolute",
          bottom: 20,
          right: 38,
          fontSize: 15,
          color: "#C7D5E0",
          fontFamily: "'Arial', sans-serif",
          opacity: 0.25,
          letterSpacing: "0.05em",
          pointerEvents: "none",
        }}
      >
        {VIDEO_CONFIG.source}
      </div>
    </AbsoluteFill>
  );
};
