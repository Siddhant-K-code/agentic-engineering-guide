import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const chapters = defineCollection({
  loader: glob({ pattern: "**/*.mdx", base: "./src/content/chapters" }),
  schema: z.object({
    title: z.string(),
    chapter: z.number().optional(),
    part: z.number().optional(),
    partTitle: z.string().optional(),
    description: z.string(),
    order: z.number(),
  }),
});

export const collections = { chapters };
