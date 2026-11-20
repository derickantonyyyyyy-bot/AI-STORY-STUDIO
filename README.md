# AI Story Studio

An AI-assisted story-video studio. This branch establishes the first working Remotion project structure. AI planning, speech, sound effects, storage, scheduling, and publishing will be added in separate, testable milestones.

## Current starter

- Remotion + React + TypeScript
- Vertical 1080×1920 composition at 30 fps
- A one-minute placeholder scene with an animated progress bar
- Build output and environment files excluded from Git

## Requirements

- Node.js 20 or newer
- npm

## Run locally

```bash
npm install
npm run dev
```

Render the one-minute test video:

```bash
npm run render
```

The output is written to `out/story-video.mp4`.

Run the TypeScript check:

```bash
npm run typecheck
```

## Planned architecture

1. **Story planner:** Groq generates structured story concepts, scenes, dialogue, and visual directions.
2. **Voice:** Google Cloud Text-to-Speech is the planned speech provider. Credentials stay on the server.
3. **Sound effects:** ElevenLabs is reserved for sound effects and ambience, not character voices.
4. **Renderer:** Remotion assembles scenes, transitions, captions, and audio.
5. **Queue and storage:** Supabase can hold approved jobs and generated assets.
6. **Publishing:** YouTube, Facebook, and Telegram integrations require an explicit approval step before each publish.

## Planned schedule

- Short videos: target publishing time 3:30 PM India time.
- Long-form videos: Wednesday and Saturday; duration remains configurable.

## Credentials and publishing

Never commit API keys, OAuth tokens, service-account files, or other secrets. Store them in server-side environment variables or deployment secrets. The application must show a preview and require approval before publishing; it must not silently publish.

## Next milestone

Add a backend story-generation endpoint with structured output validation and a preview/approval screen before connecting external voice or sound services.
