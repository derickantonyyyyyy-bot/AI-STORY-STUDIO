import React from "react";
import {Composition} from "remotion";
import {StoryVideo} from "./StoryVideo";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="StoryVideo"
    component={StoryVideo}
    durationInFrames={30 * 60}
    fps={30}
    width={1080}
    height={1920}
  />
);
