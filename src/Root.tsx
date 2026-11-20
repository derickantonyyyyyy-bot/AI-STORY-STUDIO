import React from "react";
import {Composition} from "remotion";
import {StoryVideo, type StoryVideoProps} from "./StoryVideo";

const demoProps: StoryVideoProps = {
  story: {
    title: "Whispering Canopy",
    genre: "what-if",
    logline: "A child discovers that trees have stories of their own.",
    narration: "What if the trees around us could finally speak?",
    scenes: [
      {scene_number: 1, duration_seconds: 10, visual_description: "A quiet child wanders beneath an ancient glowing forest canopy.", camera_motion: "Slow cinematic push-in", transition: "Soft light dissolve", narration_line: "At the edge of a quiet village stood a forest full of secrets.", dialogue: []},
      {scene_number: 2, duration_seconds: 10, visual_description: "A tiny golden leaf drifts down and glows in the child's hands.", camera_motion: "Gentle orbit", transition: "Golden particle sweep", narration_line: "One evening, a golden leaf whispered a sound no one had heard before.", dialogue: [{character: "Child", line: "Did you just speak to me?", delivery: "Curious and soft"}]},
      {scene_number: 3, duration_seconds: 10, visual_description: "Ancient trees shimmer as soft waves of light travel through their branches.", camera_motion: "Wide reveal", transition: "Branch-shaped wipe", narration_line: "Then the whole forest began sharing its memories.", dialogue: []},
      {scene_number: 4, duration_seconds: 10, visual_description: "A warm sunrise spreads across the forest as the child listens closely.", camera_motion: "Slow crane upward", transition: "Sun flare dissolve", narration_line: "The trees told stories about storms, seasons, and the people they had watched grow.", dialogue: []},
      {scene_number: 5, duration_seconds: 10, visual_description: "The child plants a young sapling beside the old tree.", camera_motion: "Low tracking shot", transition: "Leaf drift transition", narration_line: "The child promised to help the forest share its stories for generations.", dialogue: [{character: "Old Tree", line: "Every new leaf begins a new story.", delivery: "Gentle, wise, warm"}]},
      {scene_number: 6, duration_seconds: 10, visual_description: "A glowing green canopy stretches toward the sunrise, full of life and color.", camera_motion: "Epic pull-back", transition: "Fade to warm light", narration_line: "And from that day on, the village never walked past a tree without listening.", dialogue: []}
    ]
  }
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="StoryVideo"
    component={StoryVideo}
    defaultProps={demoProps}
    durationInFrames={30 * 60}
    fps={30}
    width={1080}
    height={1920}
  />
);
