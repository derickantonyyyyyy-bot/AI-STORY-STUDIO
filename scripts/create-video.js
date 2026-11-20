import {mkdir, writeFile} from "node:fs/promises";
import {spawn} from "node:child_process";
import {join} from "node:path";
import {generateArtwork} from "./generate-artwork.js";

const [genre, ...premiseParts] = process.argv.slice(2);
const premise = premiseParts.join(" ").trim();
const allowedGenres = ["sad", "scary", "what-if", "bizarre", "unusual-facts"];

if (!allowedGenres.includes(genre) || premise.length < 8) {
  console.error('Usage: npm run create:video -- "what-if" "Your story premise here"');
  console.error("Genres: " + allowedGenres.join(", "));
  process.exit(1);
}

const apiUrl = process.env.STORY_API_URL || "http://localhost:8787";
console.log("Requesting a 60-second storyboard from Groq...");

const response = await fetch(`${apiUrl}/api/story/generate`, {
  method: "POST",
  headers: {"content-type": "application/json"},
  body: JSON.stringify({genre, premise}),
});

const result = await response.json();
if (!response.ok || !result.ok || !result.story) {
  console.error("Story generation failed:", result.error || response.statusText);
  process.exit(1);
}

const totalSeconds = result.story.scenes.reduce((sum, scene) => sum + scene.duration_seconds, 0);
if (totalSeconds !== 60) {
  console.error(`Expected a 60-second story, received ${totalSeconds} seconds.`);
  process.exit(1);
}

await mkdir("out", {recursive: true});
const propsPath = join("out", "story-props.json");
console.log(`Generated: ${result.story.title}`);
let artwork = {enabled: false, generated: 0};
try {
  artwork = await generateArtwork(result.story);
} catch (error) {
  console.error("Artwork generation failed:", error.message);
  console.error("The video will continue with the built-in renderer artwork.");
}
await writeFile(propsPath, JSON.stringify({story: result.story, artworkEnabled: artwork.enabled}, null, 2), "utf8");
console.log(`Saved storyboard props to ${propsPath}`);
console.log("Starting Remotion render...");

const command = process.platform === "win32" ? "npx.cmd" : "npx";
const child = spawn(command, [
  "remotion",
  "render",
  "src/index.ts",
  "StoryVideo",
  "out/story-video.mp4",
  `--props=${propsPath}`,
], {stdio: "inherit", shell: process.platform === "win32"});

child.on("error", (error) => {
  console.error("Could not start Remotion:", error.message);
  process.exitCode = 1;
});
child.on("exit", (code) => {
  process.exitCode = code ?? 1;
});
