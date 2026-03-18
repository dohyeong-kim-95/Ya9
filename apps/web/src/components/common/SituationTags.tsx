"use client";

import type { SituationTag } from "@/lib/types";
import { SITUATION_TAG_STYLES } from "@/lib/constants";

export default function SituationTags({ tags }: { tags: SituationTag[] }) {
  if (tags.length === 0) return null;
  return (
    <div className="flex gap-1 flex-wrap">
      {tags.map((tag) => {
        const style = SITUATION_TAG_STYLES[tag];
        if (!style) return null;
        return (
          <span
            key={tag}
            className={`px-1.5 py-0.5 text-[10px] font-semibold rounded border ${style.className}`}
          >
            {style.label}
          </span>
        );
      })}
    </div>
  );
}
