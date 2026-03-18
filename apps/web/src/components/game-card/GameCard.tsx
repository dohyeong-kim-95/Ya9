"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import type { GameSummary } from "@/lib/types";
import StatusBadge from "@/components/common/StatusBadge";
import SituationTags from "@/components/common/SituationTags";
import BaseDiamond from "@/components/common/BaseDiamond";
import CountDisplay from "@/components/common/CountDisplay";

export default function GameCard({ game }: { game: GameSummary }) {
  const isLive = game.status === "live";

  return (
    <Link href={`/game/${game.game_id}`}>
      <motion.div
        className="bg-surface border border-border rounded-xl p-4 active:bg-surface-hover transition-colors"
        whileTap={{ scale: 0.98 }}
      >
        {/* Top row: status + tags */}
        <div className="flex items-center justify-between mb-3">
          <StatusBadge status={game.status} />
          <SituationTags tags={game.situation_tags} />
        </div>

        {/* Score section */}
        <div className="flex items-center justify-between">
          <div className="flex-1">
            {/* Away team */}
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-300">
                {game.away_team.name}
              </span>
              <span className="text-xl font-bold tabular-nums">
                {game.score.away}
              </span>
            </div>
            {/* Home team */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-300">
                {game.home_team.name}
              </span>
              <span className="text-xl font-bold tabular-nums">
                {game.score.home}
              </span>
            </div>
          </div>

          {/* Live mini HUD */}
          {isLive && (
            <div className="ml-4 flex flex-col items-center gap-1.5">
              <span className="text-[10px] font-mono text-gray-400">
                {game.inning.half === "top" ? "▲" : "▼"} {game.inning.number}회
              </span>
              <BaseDiamond bases={game.bases} size="sm" />
              <CountDisplay count={game.count} />
            </div>
          )}

          {/* Final / Scheduled info */}
          {game.status === "final" && (
            <div className="ml-4 text-xs text-gray-500 font-mono">종료</div>
          )}
          {game.status === "scheduled" && (
            <div className="ml-4 text-xs text-scheduled font-mono">
              {new Date(game.start_time).toLocaleTimeString("ko-KR", {
                hour: "2-digit",
                minute: "2-digit",
              })}
            </div>
          )}
        </div>
      </motion.div>
    </Link>
  );
}
