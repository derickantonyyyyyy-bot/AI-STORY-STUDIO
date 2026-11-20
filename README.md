# AI Story Studio

An AI-assisted story-video studio. The first milestone provides a Remotion renderer and a server-side Groq story-planning endpoint.

## Current features

- Remotion + React + TypeScript
- Vertical 1080×1920 composition at 30 fps
- One-minute placeholder scene with an animated progress bar
- Express API with a health check and story-generation route
- Groq-generated six-scene storyboard with validated JSON structure
- API keys kept on the server; no secrets committed

## Requirements

- Node.js 20 or newer
- npm
- A Groq API key for story generation. Cloudflare Workers AI credentials are optional for generated scene artwork.

## Install

```bash
npm install
```

## Configure the story engine

Copy `.env.example` to `.env` and add your Groq key:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-20b
PORT=8787

# Optional generated scene artwork (Cloudflare Workers AI free allocation applies)
IMAGE_PROVIDER=cloudflare
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_workers_ai_token
CLOUDFLARE_IMAGE_STEPS=4
```

Keep `.env` private. Never put the key in React/browser code, commit it, or share it in chat.

## Start the API

```bash
npm run server
```

Health check: `http://localhost:8787/api/health`

Generate a storyboard:

```bash
curl -X POST http://localhost:8787/api/story/generate \
  -H "Content-Type: application/json" \
  -d '{"genre":"what-if","premise":"What if every shadow started moving one second before its owner?"}'
```

The API returns a validated story object containing six scenes whose durations must total exactly 60 seconds. No video is rendered or published by this endpoint yet.

## Start Remotion

In a second terminal:

```bash
npm run dev
```

Render the one-minute placeholder:

```bash
npm run render
```

Output: `out/story-video.mp4`

## Planned architecture

1. **Story planner:** Groq generates concepts, narration, dialogue, and scene plans.
2. **Voice:** Google Cloud Text-to-Speech is planned for character speech. Credentials stay server-side.
3. **Sound effects:** ElevenLabs is reserved for sound effects and ambience, not character voices.
4. **Renderer:** Remotion assembles scenes, transitions, captions, and audio.
5. **Queue and storage:** Supabase can hold approved jobs and generated assets.
6. **Publishing:** YouTube, Facebook, and Telegram integrations require explicit approval before each publish.

## Publishing and credentials

Never commit API keys, OAuth tokens, service-account files, or other secrets. Store them in server-side environment variables or deployment secrets. The app must show a preview and require approval before publishing; it must not silently publish.

## Planned schedule

- Short videos: target publishing time 3:30 PM India time.
- Long-form videos: Wednesday and Saturday; duration remains configurable.

## Next milestone

Connect the story endpoint to a preview/approval screen, then generate voice audio and scene assets before implementing the full Remotion timeline.


## Generate a complete story video

Keep the API server running in one terminal:

```powershell
npm.cmd run server
```

Open a second terminal in the project folder and run:

```powershell
npm.cmd run create:video -- "what-if" "What if humans could hear the thoughts of trees?"
```

The script requests a validated 60-second storyboard from the local Groq-powered API, optionally generates one scene image per storyboard scene with Cloudflare Workers AI FLUX.1 schnell, saves the Remotion input to `out/story-props.json`, and renders `out/story-video.mp4`. Replace the genre and premise with your own. Supported genres: `sad`, `scary`, `what-if`, `bizarre`, and `unusual-facts`.

When Cloudflare credentials are configured, the renderer uses generated cinematic scene artwork with a slow camera push-in. Without credentials, it safely falls back to the built-in vector artwork. Generated images are stored under `public/generated/` and are not committed to Git. Character-consistent animation, speech synthesis, and sound effects remain later pipeline stages.


## Optional: enable free-tier scene artwork

1. In Cloudflare, open **Workers AI** and choose **Use REST API**.
2. Create a Workers AI API token with the required Workers AI permissions and copy your Account ID.
3. Add both values to your local `.env` file. Do not paste them into chat or commit them.
4. Keep `CLOUDFLARE_IMAGE_STEPS=4` to use the model's default step count.
5. Run the normal `npm.cmd run create:video -- "what-if" "Your premise"` command.

The integration uses `@cf/black-forest-labs/flux-1-schnell`. Cloudflare documents a daily free Workers AI allocation, but it is quota-limited, not unlimited. Usage above the free allocation may be billable on a paid Workers plan. Check the current [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/) before enabling it. The generator creates up to six scene images for the current one-minute storyboard and does not automatically retry failed requests.

The same character description is repeated in each image prompt to encourage visual consistency. Text-to-image generation does not guarantee a perfectly identical character between scenes.


## Blender 3D prototype (new)

The first Blender milestone is a real 3D scene prototype: a stylized forest set, a simple cartoon character built from 3D geometry, basic arm/body motion, cinematic lighting, and a slow camera move. It is an early visual foundation, not the finished reference-quality animation. Character lip-sync, detailed scene-specific sets, and sound are not implemented yet.

1. Install Blender 4.2 or newer on your computer.
2. Keep the API server running and generate the storyboard/video props using the normal workflow above. This creates `out/story-props.json`.
3. From the project folder, run:

```powershell
blender -b -P scripts/blender_scene.py -- out/story-props.json out/blender-story.mp4
```

The Blender executable must be available as `blender` in PowerShell's PATH. The prototype renders a 1080×1920, 30 FPS MP4 to `out/blender-story.mp4`. Rendering time depends heavily on your computer and Blender settings. This is a separate prototype command; the existing Remotion workflow remains unchanged while we validate the 3D renderer.
