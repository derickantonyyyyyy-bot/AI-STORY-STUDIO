import React from "react";
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from "remotion";

export const StoryVideo: React.FC = () => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: "linear-gradient(145deg, #10152d 0%, #321b45 55%, #111827 100%)",
        color: "white",
        justifyContent: "center",
        alignItems: "center",
        fontFamily: "Arial, sans-serif",
        padding: 80,
      }}
    >
      <div style={{fontSize: 30, letterSpacing: 8, opacity: 0.7, marginBottom: 28}}>
        AI STORY STUDIO
      </div>
      <div style={{fontSize: 76, fontWeight: 800, textAlign: "center", lineHeight: 1.08}}>
        Your next story
        <br />
        starts here.
      </div>
      <div style={{fontSize: 28, opacity: 0.75, marginTop: 32}}>
        A first Remotion scene
      </div>
      <div
        style={{
          position: "absolute",
          bottom: 100,
          left: 80,
          right: 80,
          height: 8,
          borderRadius: 99,
          background: "rgba(255,255,255,0.18)",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${progress * 100}%`,
            height: "100%",
            background: "#f5b942",
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
