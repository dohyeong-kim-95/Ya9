"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import type { GameSummary } from "@/lib/types";

export default function GameSwitcher({
  games,
  currentGameId,
}: {
  games: GameSummary[];
  currentGameId: string;
}) {
  const otherGames = games.filter((g) => g.game_id !== currentGameId);
  if (otherGames.length === 0) return null;

  return (
    <div className="overflow-x-auto -mx-4 px-4">
      <div className="flex gap-2 pb-1">
        {otherGames.map((g) => (
          <Link key={g.game_id} href={`/game/${g.game_id}`}>
            <motion.div
              className="flex-shrink-0 bg-surface border border-border rounded-lg px-3 py-2 active:bg-surface-hover min-w-[100px]"
              whileTap={{ scale: 0.95 }}
            >
              <div className="flex items-center justify-between gap-3">
                <div className="text-[10px]">
                  <div className="text-gray-400">{g.away_team.name}</div>
                  <div className="text-gray-400">{g.home_team.name}</div>
                </div>
                <div className="text-[10px] font-bold tabular-nums">
                  <div>{g.score.away}</div>
                  <div>{g.score.home}</div>
                </div>
              </div>
              {g.status === "live" && (
                <div className="text-[8px] text-live font-mono mt-1">
                  {g.inning.half === "top" ? "▲" : "▼"}{g.inning.number}
                </div>
              )}
              {g.status === "final" && (
                <div className="text-[8px] text-final font-mono mt-1">F</div>
              )}
            </motion.div>
          </Link>
        ))}
      </div>
    </div>
  );
}
