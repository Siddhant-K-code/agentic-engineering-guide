export interface ChapterMeta {
  slug: string;
  title: string;
  chapter?: number;
  part?: number;
  partTitle?: string;
  order: number;
}

export interface PartGroup {
  part: number;
  title: string;
  chapters: ChapterMeta[];
}

export function groupByPart(chapters: ChapterMeta[]): PartGroup[] {
  const sorted = [...chapters].sort((a, b) => a.order - b.order);
  const parts: PartGroup[] = [];
  const frontMatter: ChapterMeta[] = [];
  const backMatter: ChapterMeta[] = [];

  for (const ch of sorted) {
    if (!ch.part) {
      if (ch.order < 100) frontMatter.push(ch);
      else backMatter.push(ch);
      continue;
    }
    let group = parts.find((p) => p.part === ch.part);
    if (!group) {
      group = { part: ch.part, title: ch.partTitle || "", chapters: [] };
      parts.push(group);
    }
    group.chapters.push(ch);
  }

  const result: PartGroup[] = [];
  if (frontMatter.length) {
    result.push({ part: 0, title: "", chapters: frontMatter });
  }
  result.push(...parts.sort((a, b) => a.part - b.part));
  if (backMatter.length) {
    result.push({ part: 99, title: "Back Matter", chapters: backMatter });
  }
  return result;
}

export function getAdjacentChapters(
  chapters: ChapterMeta[],
  currentSlug: string,
): { prev: ChapterMeta | null; next: ChapterMeta | null } {
  const sorted = [...chapters].sort((a, b) => a.order - b.order);
  const idx = sorted.findIndex((c) => c.slug === currentSlug);
  return {
    prev: idx > 0 ? sorted[idx - 1] : null,
    next: idx < sorted.length - 1 ? sorted[idx + 1] : null,
  };
}
