import "dotenv/config";
import {mkdir, writeFile, rm} from "node:fs/promises";
import {join} from "node:path";

const MODEL = "@cf/black-forest-labs/flux-1-schnell";

const clean = (value, max = 500) => String(value || "").replace(/\s+/g, " ").trim().slice(0, max);

function makePrompt(story, scene, index) {
  const firstCharacter = clean(story.scenes?.[0]?.dialogue?.[0]?.character || "the young protagonist", 80);
  const characterAnchor = `Recurring character continuity: show ${firstCharacter} as the same character in every scene, with consistent face, age, hairstyle, clothing, and proportions. Use the scene description as the source for the character design; do not redesign the character between shots.`;
  const sceneText = clean(scene.visual_description, 650);
  const camera = clean(scene.camera_motion, 180);
  const mood = clean(story.genre, 60);
  return [
    "Create one original frame from a premium, cinematic 3D animated family adventure film.",
    "Vertical portrait 9:16 composition, beautifully composed for a mobile short video.",
    "High-end stylized 3D character animation, expressive readable faces, detailed environment geometry, realistic material textures, soft global illumination, volumetric lighting, atmospheric depth, cinematic color grading, subtle depth of field.",
    characterAnchor,
    `Scene ${index + 1}: ${sceneText}`,
    camera ? `Camera framing and movement inspiration: ${camera}.` : "",
    `Story mood: ${mood}.`,
    "Keep the main subject clearly visible and leave some uncluttered space near the lower edge for video captions.",
    "No text, no subtitles, no lettering, no logos, no watermarks, no borders, no collage, no split-screen."
  ].filter(Boolean).join(" ").slice(0, 2000);
}

export async function generateArtwork(story) {
  if ((process.env.IMAGE_PROVIDER || "cloudflare").toLowerCase() === "none") {
    console.log("Image generation disabled (IMAGE_PROVIDER=none). Using the built-in renderer artwork.");
    return {enabled: false, generated: 0};
  }

  const accountId = process.env.CLOUDFLARE_ACCOUNT_ID;
  const apiToken = process.env.CLOUDFLARE_API_TOKEN;
  if (!accountId || !apiToken) {
    console.log("Cloudflare image generation is not configured yet. Skipping artwork and using the built-in renderer.");
    console.log("Add CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN to your local .env file to enable it.");
    return {enabled: false, generated: 0};
  }

  const steps = Math.min(8, Math.max(1, Number(process.env.CLOUDFLARE_IMAGE_STEPS || 4)));
  const outputDir = join("public", "generated");
  await mkdir(outputDir, {recursive: true});
  const endpoint = `https://api.cloudflare.com/client/v4/accounts/${encodeURIComponent(accountId)}/ai/run/${MODEL}`;

  console.log(`Generating ${story.scenes.length} cinematic scene images with Cloudflare Workers AI (${MODEL}, ${steps} steps)...`);
  let generated = 0;

  try {
    for (const [index, scene] of story.scenes.entries()) {
      const sceneNumber = String(scene.scene_number || index + 1).padStart(2, "0");
      const outputPath = join(outputDir, `scene-${sceneNumber}.jpg`);
      console.log(`  Generating artwork for scene ${sceneNumber}/${story.scenes.length}...`);

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${apiToken}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          prompt: makePrompt(story, scene, index),
          steps,
          seed: 24000 + index
        }),
        signal: AbortSignal.timeout(120000)
      });

      const payload = await response.json().catch(() => ({}));
      const imageBase64 = payload?.result?.image;
      if (!response.ok || payload?.success === false || typeof imageBase64 !== "string") {
        const detail = payload?.errors?.map((item) => item.message).filter(Boolean).join("; ");
        throw new Error(`Cloudflare image request failed for scene ${sceneNumber} (HTTP ${response.status}). ${detail || "Check your account, token permissions, and Workers AI quota."}`);
      }

      await writeFile(outputPath, Buffer.from(imageBase64, "base64"));
      generated += 1;
    }
  } catch (error) {
    for (const scene of story.scenes) {
      const sceneNumber = String(scene.scene_number).padStart(2, "0");
      await rm(join(outputDir, `scene-${sceneNumber}.jpg`), {force: true}).catch(() => {});
    }
    throw error;
  }

  console.log(`Generated ${generated} scene images in ${outputDir}.`);
  return {enabled: generated === story.scenes.length, generated};
}
