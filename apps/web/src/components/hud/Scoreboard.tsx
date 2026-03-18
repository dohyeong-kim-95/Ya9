"use client";

import { motion } from "framer-motion";
import type { GameDetail } from "@/lib/types";
import StatusBadge from "@/components/common/StatusBadge";

export default function Scoreboard({ game }: { game: GameDetail }) {
  return (
    <div className="bg-surface border border-border rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <StatusBadge status={game.status} />
        <span className="text-[10px] font-mono text-gray-500">
          {game.status === "live" && (
            <>
              {game.inning.half === "top" ? "▲" : "▼"} {game.inning.number}회
            </>
          )}
          {game.status === "final" && "경기 종료"}
          {game.status === "scheduled" &&
            new Date(game.start_time).toLocaleTimeString("ko-KR", {
              hour: "2-digit",
              minute: "2-digit",
            })}
        </span>
      </div>

      {/* Score rows */}
      <div className="space-y-2">
        <ScoreRow
          teamName={game.away_team.name}
          teamCode={game.away_team.code}
          score={game.score.away}
          isActive={game.status === "live" && game.inning.half === "top"}
        />
        <ScoreRow
          teamName={game.home_team.name}
          teamCode={game.home_team.code}
          score={game.score.home}
          isActive={game.status === "live" && game.inning.half === "bottom"}
        />
      </div>
    </div>
  );
}

function ScoreRow({
  teamName,
  teamCode,
  score,
  isActive,
}: {
  teamName: string;
  teamCode: string;
  score: number;
  isActive: boolean;
}) {
  return (
    <div
      className={`flex items-center justify-between py-1 px-2 rounded-lg ${
        isActive ? "bg-white/5" : ""
      }`}
    >
      <div className="flex items-center gap-2">
        {isActive && (
          <div className="w-1.5 h-1.5 rounded-full bg-live animate-pulse" />
        )}
        <span className="text-xs text-gray-500 font-mono w-6">{teamCode}</span>
        <span className="text-sm font-medium">{teamName}</span>
      </div>
      <motion.span
        key={score}
        className="text-2xl font-bold tabular-nums"
        initial={{ scale: 1.4, color: "#facc15" }}
        animate={{ scale: 1, color: "#e5e7eb" }}
        transition={{ duration: 0.5 }}
      >
        {score}
      </motion.span>
    </div>
  );
}
