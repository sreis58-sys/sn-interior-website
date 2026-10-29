import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const projeler = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/projeler' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      category: z.enum(['Konut', 'Ticari']),
      location: z.string(),
      year: z.number(),
      area: z.string().optional(),
      scope: z.string().optional(),
      summary: z.string(),
      order: z.number(),
      cover: image(),
      coverAlt: z.string(),
      gallery: z.array(z.object({ src: image(), alt: z.string() })).default([]),
    }),
});

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/blog' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date().optional(),
    category: z.enum(['Konut', 'Ticari', 'Malzeme & Teknik']),
  }),
});

export const collections = { projeler, blog };
