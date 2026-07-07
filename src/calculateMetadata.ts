import { CalculateMetadataFunction, staticFile } from "remotion";
import { getAudioDurationInSeconds } from "@remotion/media-utils";
import { SCENES, FPS } from "./data";

export type SceneTiming = {
  id: number;
  fromFrame: number;
  durationFrames: number;
};

export type RankingVideoProps = {
  sceneTimings: SceneTiming[];
};

// Dùng khi voice của scene chưa được sinh (template trống hoặc đang làm dở)
// — để Remotion Studio vẫn mở được thay vì crash.
const FALLBACK_SCENE_SEC = 3;

export const calculateSceneMetadata: CalculateMetadataFunction<
  RankingVideoProps
> = async () => {
  const sceneTimings: SceneTiming[] = [];
  let cursorFrame = 0;

  for (const scene of SCENES) {
    const file = `voice/scene-${String(scene.id).padStart(2, "0")}.mp3`;
    let durationSec: number;
    try {
      durationSec = await getAudioDurationInSeconds(staticFile(file));
    } catch {
      durationSec = FALLBACK_SCENE_SEC;
    }

    const durationFrames = Math.max(1, Math.round(durationSec * FPS));
    sceneTimings.push({ id: scene.id, fromFrame: cursorFrame, durationFrames });
    cursorFrame += durationFrames;
  }

  // Template trống hoàn toàn (chưa có scene nào) — giữ composition mở được
  if (sceneTimings.length === 0) {
    const durationFrames = FALLBACK_SCENE_SEC * FPS;
    sceneTimings.push({ id: 0, fromFrame: 0, durationFrames });
    cursorFrame = durationFrames;
  }

  return {
    durationInFrames: cursorFrame,
    fps: FPS,
    props: { sceneTimings },
  };
};
