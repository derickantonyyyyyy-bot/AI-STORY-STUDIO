import "dotenv/config";
import express from "express";
import Groq from "groq-sdk";
import {storyJsonSchema, storyRequestSchema, storyResponseSchema} from "./story-schema.js";

const app = express();
app.disable("x-powered-by");
app.use(express.json({limit: "16kb"}));

app.get("/api/health", (_req, res) => {
  res.json({ok: true, service: "ai-story-studio-api"});
});

app.post("/api/story/generate", async (req, res) => {
  const parsedRequest = storyRequestSchema.safeParse(req.body);

  if (!parsedRequest.success) {
    return res.status(400).json({
      error: "Please provide a supported genre and a premise between 8 and 500 characters."
    });
  }

  if (!process.env.GROQ_API_KEY) {
    return res.status(503).json({
      error: "The story engine is not configured yet. Add GROQ_API_KEY to the server environment."
    });
  }

  try {
    const groq = new Groq({apiKey: process.env.GROQ_API_KEY});
    const {genre, premise} = parsedRequest.data;

    const completion = await groq.chat.completions.create({
      model: process.env.GROQ_MODEL || "openai/gpt-oss-20b",
      temperature: 0.8,
      max_completion_tokens: 6000,
      messages: [
        {
          role: "system",
          content: [
            "You are the story planner for AI Story Studio.",
            "Create an original, engaging, family-friendly one-minute vertical-video story.",
            "Return a complete six-scene storyboard with scene durations adding up to exactly 60 seconds.",
            "Every scene needs a clear visual description, camera movement, transition, narration line, and dialogue array.",
            "Assign every spoken line to the correct named character and include a concise voice-delivery direction.",
            "Make visuals cinematic and suitable for 3D animation, with expressive characters, lighting, color, and reactive environments.",
            "For scary stories, use suspense and atmosphere only; do not include graphic violence or gore.",
            "For sad stories, handle emotions thoughtfully and end with a constructive or hopeful note.",
            "For unusual facts, avoid presenting uncertain claims as facts.",
            "Do not include copyrighted characters or imitate a living creator's style."
          ].join(" ")
        },
        {
          role: "user",
          content: `Genre: ${genre}\nPremise: ${premise}\nCreate the 60-second storyboard now.`
        }
      ],
      response_format: {
        type: "json_schema",
        json_schema: {
          name: "ai_story_video",
          strict: true,
          schema: storyJsonSchema
        }
      }
    });

    const raw = completion.choices?.[0]?.message?.content;
    if (!raw) {
      return res.status(502).json({error: "The story model returned an empty response. Please try again."});
    }

    const parsedStory = storyResponseSchema.safeParse(JSON.parse(raw));
    if (!parsedStory.success) {
      return res.status(502).json({error: "The generated storyboard did not pass validation. Please try again."});
    }

    const story = parsedStory.data;
    const totalSeconds = story.scenes.reduce((sum, scene) => sum + scene.duration_seconds, 0);
    if (totalSeconds !== 60) {
      return res.status(502).json({
        error: "The generated scenes did not total exactly 60 seconds. Please generate again."
      });
    }

    return res.json({ok: true, story});
  } catch (error) {
    console.error("Story generation failed:", error?.message || "Unknown error");
    return res.status(502).json({error: "Story generation failed. Check the server configuration and try again."});
  }
});

const port = Number(process.env.PORT || 8787);
app.listen(port, () => {
  console.log(`AI Story Studio API listening on http://localhost:${port}`);
});
