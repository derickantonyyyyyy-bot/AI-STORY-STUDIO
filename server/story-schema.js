import {z} from "zod";

export const storyRequestSchema = z.object({
  genre: z.enum(["sad", "scary", "what-if", "bizarre", "unusual-facts"]),
  premise: z.string().trim().min(8).max(500),
});

export const storyResponseSchema = z.object({
  title: z.string().min(1).max(100),
  genre: z.enum(["sad", "scary", "what-if", "bizarre", "unusual-facts"]),
  logline: z.string().min(1).max(300),
  narration: z.string().min(1).max(5000),
  scenes: z.array(z.object({
    scene_number: z.number().int().positive(),
    duration_seconds: z.number().int().positive(),
    visual_description: z.string().min(1).max(600),
    emotion: z.enum(["neutral", "happy", "sad", "surprised", "worried", "curious", "determined", "awe"]),
    camera_motion: z.string().min(1).max(160),
    transition: z.string().min(1).max(160),
    narration_line: z.string().max(700),
    dialogue: z.array(z.object({
      character: z.string().min(1).max(80),
      line: z.string().min(1).max(500),
      delivery: z.string().min(1).max(120)
    }))
  })).min(3).max(12)
});

export const storyJsonSchema = {
  type: "object",
  properties: {
    title: {type: "string"},
    genre: {type: "string", enum: ["sad", "scary", "what-if", "bizarre", "unusual-facts"]},
    logline: {type: "string"},
    narration: {type: "string"},
    scenes: {
      type: "array",
      minItems: 3,
      maxItems: 12,
      items: {
        type: "object",
        properties: {
          scene_number: {type: "integer"},
          duration_seconds: {type: "integer"},
          visual_description: {type: "string"},
          emotion: {type: "string", enum: ["neutral", "happy", "sad", "surprised", "worried", "curious", "determined", "awe"]},
          camera_motion: {type: "string"},
          transition: {type: "string"},
          narration_line: {type: "string"},
          dialogue: {
            type: "array",
            items: {
              type: "object",
              properties: {
                character: {type: "string"},
                line: {type: "string"},
                delivery: {type: "string"}
              },
              required: ["character", "line", "delivery"],
              additionalProperties: false
            }
          }
        },
        required: ["scene_number", "duration_seconds", "visual_description", "emotion", "camera_motion", "transition", "narration_line", "dialogue"],
        additionalProperties: false
      }
    }
  },
  required: ["title", "genre", "logline", "narration", "scenes"],
  additionalProperties: false
};
