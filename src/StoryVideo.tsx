import React from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type StoryDialogue = {
  character: string;
  line: string;
  delivery: string;
};

export type StoryScene = {
  scene_number: number;
  duration_seconds: number;
  visual_description: string;
  camera_motion: string;
  transition: string;
  narration_line: string;
  dialogue: StoryDialogue[];
};

export type Story = {
  title: string;
  genre: string;
  logline: string;
  narration: string;
  scenes: StoryScene[];
};

export type StoryVideoProps = {
  story: Story;
};

const palettes = [
  ["#081a2c", "#164b59", "#f2a65a"],
  ["#17142e", "#49336c", "#f3a6a6"],
  ["#092c31", "#176b62", "#d9d98b"],
  ["#24152f", "#75435f", "#f6bd60"],
  ["#101d3b", "#315a81", "#a8d8ea"],
  ["#1b2336", "#5a526e", "#ffc98b"],
];

const SceneVisual: React.FC<{scene: StoryScene; index: number; title: string}> = ({
  scene,
  index,
  title,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const entrance = spring({frame, fps, config: {damping: 18, stiffness: 85}});
  const drift = Math.sin(frame / 24) * 18;
  const [base, glow, accent] = palettes[index % palettes.length];
  const titleOpacity = interpolate(frame, [0, 18, 38], [0, 1, 1], {
    extrapolateRight: "clamp",
  });
  const dialogue = scene.dialogue?.[0];

  return (
    <AbsoluteFill
      style={{
        overflow: "hidden",
        color: "#fff",
        background: `radial-gradient(ellipse at 72% 30%, ${glow} 0%, transparent 48%), linear-gradient(145deg, ${base}, #080b18 88%)`,
        fontFamily: "Arial, sans-serif",
      }}
    >
      <AbsoluteFill
        style={{
          opacity: 0.22,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.08) 1px, transparent 1px)",
          backgroundSize: "90px 90px",
          transform: `perspective(700px) rotateX(58deg) scale(1.8) translateY(${drift}px)`,
          transformOrigin: "center bottom",
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 560,
          height: 560,
          borderRadius: "50%",
          right: -130 + drift,
          top: 170,
          background: `radial-gradient(circle, ${accent}55 0%, ${accent}16 42%, transparent 70%)`,
          filter: "blur(8px)",
          transform: `scale(${0.92 + entrance * 0.12})`,
        }}
      />
      <div
        style={{
          position: "absolute",
          width: 360,
          height: 360,
          border: `2px solid ${accent}55`,
          borderRadius: "50%",
          right: 20,
          top: 260,
          transform: `translateY(${drift}px) rotate(${frame * 0.12}deg)`,
          boxShadow: `0 0 70px ${accent}22, inset 0 0 60px ${accent}18`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: -100,
          right: -100,
          bottom: 330,
          height: 360,
          borderRadius: "50% 50% 0 0",
          background: "linear-gradient(160deg, rgba(10,22,38,.25), rgba(3,8,18,.96))",
          transform: `translateY(${drift * 0.35}px)`,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 105,
          top: 390,
          width: 210,
          height: 310,
          opacity: 0.82,
          transform: `translateY(${(1 - entrance) * 55 + drift * 0.25}px) scale(${0.96 + entrance * 0.04})`,
          filter: `drop-shadow(0 18px 45px ${accent}55)`,
        }}
      >
        <div
          style={{
            position: "absolute",
            width: 126,
            height: 126,
            borderRadius: "50%",
            left: 42,
            top: 0,
            background: `radial-gradient(circle at 35% 30%, #fff8e8, ${accent} 38%, #182338 78%)`,
            boxShadow: `0 0 45px ${accent}77`,
          }}
        />
        <div
          style={{
            position: "absolute",
            width: 180,
            height: 205,
            left: 15,
            top: 105,
            borderRadius: "48% 48% 18% 18%",
            background: "linear-gradient(115deg, #263d56, #101b30 70%)",
            border: "1px solid rgba(255,255,255,.18)",
            boxShadow: "inset 18px 0 35px rgba(255,255,255,.12)",
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          top: 92,
          left: 82,
          right: 82,
          opacity: titleOpacity,
          transform: `translateY(${(1 - entrance) * 28}px)`,
        }}
      >
        <div style={{fontSize: 22, letterSpacing: 7, color: accent, fontWeight: 700}}>
          AI STORY STUDIO  •  {String(scene.scene_number).padStart(2, "0")}
        </div>
        <div style={{fontSize: 54, fontWeight: 800, marginTop: 18, lineHeight: 1.05}}>
          {title}
        </div>
      </div>
      <div
        style={{
          position: "absolute",
          left: 82,
          right: 82,
          bottom: 125,
          padding: "34px 36px",
          borderRadius: 28,
          background: "linear-gradient(135deg, rgba(8,13,27,.86), rgba(20,25,43,.68))",
          border: "1px solid rgba(255,255,255,.18)",
          boxShadow: "0 22px 70px rgba(0,0,0,.35)",
          backdropFilter: "blur(14px)",
          transform: `translateY(${(1 - entrance) * 45}px)`,
        }}
      >
        <div style={{fontSize: 19, color: accent, letterSpacing: 4, marginBottom: 14}}>
          SCENE {scene.scene_number}  /  {scene.duration_seconds}s
        </div>
        <div style={{fontSize: 31, fontWeight: 700, lineHeight: 1.25}}>
          {scene.visual_description}
        </div>
        {scene.narration_line ? (
          <div style={{fontSize: 25, lineHeight: 1.35, color: "#e5e9f2", marginTop: 22}}>
            “{scene.narration_line}”
          </div>
        ) : null}
        {dialogue ? (
          <div style={{fontSize: 21, color: accent, marginTop: 18}}>
            {dialogue.character}: “{dialogue.line}”
          </div>
        ) : null}
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 48,
          left: 82,
          right: 82,
          height: 5,
          borderRadius: 20,
          background: "rgba(255,255,255,.18)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${interpolate(frame, [0, scene.duration_seconds * fps], [0, 100], {extrapolateRight: "clamp"})}%`,
            height: "100%",
            background: accent,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};

export const StoryVideo: React.FC<StoryVideoProps> = ({story}) => {
  let startFrame = 0;

  return (
    <AbsoluteFill style={{backgroundColor: "#080b18"}}>
      {story.scenes.map((scene, index) => {
        const from = startFrame;
        const durationInFrames = scene.duration_seconds * 30;
        startFrame += durationInFrames;
        return (
          <Sequence
            key={scene.scene_number}
            from={from}
            durationInFrames={durationInFrames}
          >
            <SceneVisual scene={scene} index={index} title={story.title} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
