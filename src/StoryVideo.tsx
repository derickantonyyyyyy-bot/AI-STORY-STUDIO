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
  {sky: "#83c9bb", deep: "#173e3b", light: "#f7d88a", leaf: "#2f7654"},
  {sky: "#718e9d", deep: "#192c3c", light: "#e8c6a2", leaf: "#365b4c"},
  {sky: "#6ab7a0", deep: "#153c35", light: "#f3d77c", leaf: "#39805b"},
  {sky: "#86b9a6", deep: "#234b40", light: "#f6d49a", leaf: "#397451"},
  {sky: "#8eb8b0", deep: "#1b3b3c", light: "#f4d995", leaf: "#39745b"},
  {sky: "#6d9b91", deep: "#1b3438", light: "#f3c98d", leaf: "#315d4c"},
];

const Tree: React.FC<{x: number; y: number; scale: number; color: string; sway: number; kind?: "pine" | "round"}> = ({x, y, scale, color, sway, kind = "round"}) => (
  <g transform={`translate(${x} ${y}) scale(${scale})`}>
    <path d="M-9 0 L-5 -145 L7 -145 L12 0Z" fill="#654b38" />
    {kind === "pine" ? (
      <g fill={color}>
        <path d="M0 -300 L-76 -174 L-37 -174 L-105 -92 L-48 -92 L-91 -22 L88 -22 L45 -92 L103 -92 L38 -174 L76 -174Z" />
        <path d="M0 -280 L0 -18" stroke="#b3c58b" strokeWidth="5" opacity=".28" />
      </g>
    ) : (
      <g transform={`rotate(${sway} 0 -190)`} fill={color}>
        <circle cx="-45" cy="-205" r="67" />
        <circle cx="34" cy="-235" r="82" />
        <circle cx="82" cy="-175" r="62" />
        <circle cx="-4" cy="-155" r="76" />
        <circle cx="-92" cy="-155" r="49" />
        <circle cx="2" cy="-278" r="48" />
        <path d="M-5 -145 Q-60 -90 -83 -44 M8 -148 Q60 -98 88 -52" fill="none" stroke="#b5c98a" strokeWidth="7" opacity=".5" />
      </g>
    )}
  </g>
);

const Lily: React.FC<{frame: number; entrance: number; accent: string; listening?: boolean}> = ({frame, entrance, accent, listening}) => {
  const bob = Math.sin(frame / 12) * 5;
  return (
    <g transform={`translate(280 ${1320 + (1 - entrance) * 100 + bob})`}>
      <ellipse cx="0" cy="8" rx="130" ry="25" fill="#071a18" opacity=".35" />
      <path d="M-48 -220 Q-88 -170 -91 -48 L-72 0 L72 0 L91 -48 Q85 -170 48 -220Z" fill="#d36d55" stroke="#f4c49a" strokeWidth="7" />
      <path d="M-47 -198 L-88 -105 L-115 -48" fill="none" stroke="#e6b18d" strokeWidth="22" strokeLinecap="round" />
      <path d="M47 -198 L87 -125 L111 -78" fill="none" stroke="#e6b18d" strokeWidth="22" strokeLinecap="round" />
      <path d="M-39 -4 L-48 0 L-55 82 M38 -4 L48 0 L58 82" stroke="#e6b18d" strokeWidth="25" strokeLinecap="round" />
      <path d="M-74 82 L-34 82 M36 82 L78 82" stroke="#4a3c35" strokeWidth="24" strokeLinecap="round" />
      <ellipse cx="0" cy="-260" rx="76" ry="88" fill="#e9b58d" />
      <path d="M-76 -278 Q-92 -375 3 -371 Q91 -367 78 -268 Q53 -316 17 -316 Q-25 -293 -76 -278Z" fill="#5b382b" />
      <path d="M-69 -285 Q-117 -249 -84 -205 M70 -291 Q110 -240 77 -197" stroke="#5b382b" strokeWidth="22" fill="none" strokeLinecap="round" />
      <ellipse cx="-27" cy="-263" rx="8" ry="11" fill="#283b38" />
      <ellipse cx="27" cy="-263" rx="8" ry="11" fill="#283b38" />
      <path d={listening ? "M-12 -224 Q0 -211 13 -224" : "M-13 -226 Q0 -217 13 -226"} stroke="#9b5149" strokeWidth="5" fill="none" strokeLinecap="round" />
      <path d="M-80 -353 Q0 -398 78 -352" stroke={accent} strokeWidth="10" fill="none" strokeLinecap="round" />
    </g>
  );
};

const TalkingOak: React.FC<{frame: number; accent: string}> = ({frame, accent}) => {
  const mouth = 12 + Math.abs(Math.sin(frame / 5)) * 13;
  return (
    <g transform="translate(760 1370)">
      <path d="M-130 450 Q-90 190 -110 -30 Q-120 -220 -60 -360 L-15 -405 L25 -360 Q115 -210 80 -20 Q45 190 145 450Z" fill="#76513a" stroke="#bd9360" strokeWidth="12" />
      <path d="M-55 30 Q-220 -60 -300 -180 M42 15 Q205 -95 280 -215 M-40 -190 Q-160 -290 -190 -370 M42 -175 Q150 -280 195 -370" stroke="#76513a" strokeWidth="38" fill="none" strokeLinecap="round" />
      <path d="M-80 -360 Q-155 -510 -55 -565 Q20 -625 105 -540 Q190 -480 125 -360 Q20 -315 -80 -360Z" fill="#377a55" />
      <path d="M-210 -385 Q-300 -470 -215 -550 Q-150 -625 -75 -555 M95 -390 Q170 -500 255 -445 Q330 -365 245 -300" fill="#43865b" />
      <ellipse cx="-35" cy="-260" rx="13" ry="19" fill="#f7e8bd" />
      <ellipse cx="47" cy="-260" rx="13" ry="19" fill="#f7e8bd" />
      <circle cx="-35" cy="-258" r="6" fill="#253d30" />
      <circle cx="47" cy="-258" r="6" fill="#253d30" />
      <path d={`M-22 -205 Q5 ${-205 + mouth} 28 -205`} stroke="#2a211b" strokeWidth="11" fill="none" strokeLinecap="round" />
      <path d="M-60 -300 Q-35 -320 -10 -302 M25 -302 Q55 -322 75 -300" stroke="#543c2c" strokeWidth="10" fill="none" strokeLinecap="round" />
      <circle cx="-145" cy="-425" r="12" fill={accent} opacity=".9" />
      <circle cx="175" cy="-480" r="9" fill={accent} opacity=".9" />
    </g>
  );
};

const SceneVisual: React.FC<{scene: StoryScene; index: number; title: string}> = ({scene, index, title}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const entrance = spring({frame, fps, config: {damping: 18, stiffness: 85}});
  const drift = Math.sin(frame / 25) * 12;
  const palette = palettes[index % palettes.length];
  const oakScene = index === 2 || index === 3;
  const night = index === 1 || index === 5;
  const progress = interpolate(frame, [0, scene.duration_seconds * fps], [0, 100], {extrapolateRight: "clamp"});
  const particles = Array.from({length: 22}, (_, i) => ({
    x: (i * 173 + 73) % 1080,
    y: (i * 251 + frame * (0.45 + (i % 3) * 0.18)) % 1920,
    r: 3 + (i % 4) * 1.5,
  }));

  return (
    <AbsoluteFill style={{overflow: "hidden", color: "#fff", fontFamily: "Arial, sans-serif", background: palette.deep}}>
      <svg width="100%" height="100%" viewBox="0 0 1080 1920" preserveAspectRatio="xMidYMid slice" style={{position: "absolute", inset: 0}}>
        <defs>
          <linearGradient id="forestSky" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={night ? "#172d42" : palette.sky} />
            <stop offset="58%" stopColor={palette.deep} />
            <stop offset="100%" stopColor="#10251f" />
          </linearGradient>
          <radialGradient id="sunGlow">
            <stop offset="0%" stopColor={palette.light} stopOpacity=".9" />
            <stop offset="100%" stopColor={palette.light} stopOpacity="0" />
          </radialGradient>
          <linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#477452" />
            <stop offset="100%" stopColor="#132b24" />
          </linearGradient>
        </defs>
        <rect width="1080" height="1920" fill="url(#forestSky)" />
        <circle cx="800" cy="410" r="360" fill="url(#sunGlow)" opacity={night ? ".12" : ".6"} />
        <path d="M0 1050 Q240 900 470 1055 T1080 1000 L1080 1920 L0 1920Z" fill="#315b49" opacity=".62" />
        <path d="M0 1270 Q250 1080 510 1240 T1080 1180 L1080 1920 L0 1920Z" fill="url(#ground)" />
        <g opacity=".62">
          <Tree x={-10} y={1120} scale={1.6} color="#204b3b" sway={-2} kind="pine" />
          <Tree x={180} y={1130} scale={1.25} color="#2c6045" sway={2} />
          <Tree x={930} y={1120} scale={1.55} color="#214b3b" sway={-2} kind="pine" />
          <Tree x={1100} y={1160} scale={1.3} color="#2e6448" sway={2} />
        </g>
        <g transform={`translate(${drift} 0)`}>
          <Tree x={80} y={1320} scale={2.1} color="#285d42" sway={Math.sin(frame / 18) * 3} />
          <Tree x={990} y={1320} scale={2.15} color="#285d42" sway={Math.sin(frame / 20) * -3} />
          <Tree x={485} y={1240} scale={1.05} color="#3c7951" sway={2} kind="pine" />
        </g>
        {oakScene ? <TalkingOak frame={frame} accent={palette.light} /> : <Lily frame={frame} entrance={entrance} accent={palette.light} listening={index === 1 || index === 4} />}
        {index === 4 ? <g stroke="#c3d78b" strokeWidth="9" fill="none" opacity=".8"><path d="M100 1690 Q250 1580 380 1710 T680 1680 T980 1740" /><path d="M360 1700 L330 1630 M610 1690 L650 1615 M830 1710 L790 1640" /></g> : null}
        {particles.map((p, i) => <circle key={i} cx={p.x} cy={p.y} r={p.r} fill={palette.light} opacity={.2 + (i % 4) * .12} />)}
        <rect width="1080" height="1920" fill="none" stroke="rgba(255,255,255,.12)" strokeWidth="3" />
      </svg>

      <div style={{position: "absolute", inset: 0, background: "linear-gradient(180deg, rgba(5,18,20,.36) 0%, transparent 34%, transparent 58%, rgba(4,15,15,.8) 100%)"}} />
      <div style={{position: "absolute", top: 78, left: 68, right: 68, opacity: interpolate(frame, [0, 16], [0, 1], {extrapolateRight: "clamp"}), transform: `translateY(${(1 - entrance) * 24}px)`}}>
        <div style={{fontSize: 22, letterSpacing: 7, color: palette.light, fontWeight: 800}}>AI STORY STUDIO  •  {String(scene.scene_number).padStart(2, "0")}</div>
        <div style={{fontSize: 58, fontWeight: 900, marginTop: 18, lineHeight: 1.05, textShadow: "0 5px 24px rgba(0,0,0,.3)"}}>{title}</div>
      </div>
      <div style={{position: "absolute", left: 54, right: 54, bottom: 112, padding: "34px 36px 38px", borderRadius: 30, background: "linear-gradient(135deg, rgba(8,25,25,.88), rgba(12,35,31,.72))", border: "1px solid rgba(255,255,255,.25)", boxShadow: "0 24px 80px rgba(0,0,0,.34)", backdropFilter: "blur(12px)", transform: `translateY(${(1 - entrance) * 42}px)`}}>
        <div style={{fontSize: 19, color: palette.light, letterSpacing: 4, fontWeight: 800, marginBottom: 14}}>SCENE {scene.scene_number}  /  {scene.duration_seconds}s</div>
        <div style={{fontSize: 29, fontWeight: 750, lineHeight: 1.25}}>{scene.visual_description}</div>
        {scene.narration_line ? <div style={{fontSize: 23, lineHeight: 1.35, color: "#e4eee7", marginTop: 20}}>“{scene.narration_line}”</div> : null}
        {scene.dialogue?.[0] ? <div style={{fontSize: 21, color: palette.light, marginTop: 16}}>{scene.dialogue[0].character}: “{scene.dialogue[0].line}”</div> : null}
      </div>
      <div style={{position: "absolute", bottom: 48, left: 64, right: 64, height: 6, borderRadius: 20, background: "rgba(255,255,255,.24)", overflow: "hidden"}}>
        <div style={{width: `${progress}%`, height: "100%", background: palette.light, boxShadow: `0 0 18px ${palette.light}`}} />
      </div>
    </AbsoluteFill>
  );
};

export const StoryVideo: React.FC<StoryVideoProps> = ({story}) => {
  let startFrame = 0;
  return (
    <AbsoluteFill style={{backgroundColor: "#10251f"}}>
      {story.scenes.map((scene, index) => {
        const from = startFrame;
        const durationInFrames = scene.duration_seconds * 30;
        startFrame += durationInFrames;
        return <Sequence key={scene.scene_number} from={from} durationInFrames={durationInFrames}><SceneVisual scene={scene} index={index} title={story.title} /></Sequence>;
      })}
    </AbsoluteFill>
  );
};
