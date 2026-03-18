"use client";

import type { GameDetail } from "@/lib/types";
import BaseDiamond from "@/components/common/BaseDiamond";
import CountDisplay from "@/components/common/CountDisplay";
import SituationTags from "@/components/common/SituationTags";

export default function GameStatePanel({ game }: { game: GameDetail }) {
  if (game.status !== "live") return null;

  return (
    <div className="bg-surface border border-border rounded-xl p-4 flex items-center justify-between">
      <div className="flex flex-col gap-3">
        <CountDisplay count={game.count} />
        <SituationTags tags={game.situation_tags} />
      </div>
      <BaseDiamond bases={game.bases} size="lg" />
    </div>
  );
}
