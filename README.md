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
- A Groq API key for story generation

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

The script requests a validated 60-second storyboard from the local Groq-powered API, saves the Remotion input to `out/story-props.json`, and renders `out/story-video.mp4`. Replace the genre and premise with your own. Supported genres: `sad`, `scary`, `what-if`, `bizarre`, and `unusual-facts`.

The current renderer creates animated, cinematic 3D-inspired scene layouts from the storyboard text. Character artwork, generated backgrounds, speech synthesis, and sound effects are subsequent pipeline stages.
