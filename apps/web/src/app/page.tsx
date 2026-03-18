"use client";

import { useEffect, useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { GameSummary } from "@/lib/types";
import { fetchTodayGames } from "@/lib/api";
import { POLL_INTERVAL_HOME } from "@/lib/constants";
import GameCard from "@/components/game-card/GameCard";

export default function HomePage() {
  const [games, setGames] = useState<GameSummary[]>([]);
  const [date, setDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await fetchTodayGames();
      setGames(data.games);
      setDate(data.date);
      setError(null);
    } catch {
      setError("데이터를 불러올 수 없습니다");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, POLL_INTERVAL_HOME);
    const handleVisibility = () => {
      if (document.hidden) return;
      load();
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      clearInterval(interval);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [load]);

  const liveGames = games.filter((g) => g.status === "live");
  const scheduledGames = games.filter((g) => g.status === "scheduled");
  const finalGames = games.filter((g) => g.status === "final");

  return (
    <div className="px-4 py-6">
      {/* Header */}
      <header className="mb-6">
        <h1 className="text-lg font-bold tracking-tight">KBO Live HUD</h1>
        {date && (
          <p className="text-xs text-gray-500 mt-1 font-mono">{date}</p>
        )}
      </header>

      {/* Loading */}
      {loading && (
        <div className="flex items-center justify-center py-20 text-gray-500 text-sm">
          로딩 중...
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm p-4 text-center">
          {error}
        </div>
      )}

      {/* Game sections */}
      {!loading && !error && (
        <AnimatePresence mode="wait">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.2 }}
          >
            {/* Live */}
            {liveGames.length > 0 && (
              <Section title="진행 중" count={liveGames.length}>
                {liveGames.map((g) => (
                  <GameCard key={g.game_id} game={g} />
                ))}
              </Section>
            )}

            {/* Scheduled */}
            {scheduledGames.length > 0 && (
              <Section title="예정" count={scheduledGames.length}>
                {scheduledGames.map((g) => (
                  <GameCard key={g.game_id} game={g} />
                ))}
              </Section>
            )}

            {/* Final */}
            {finalGames.length > 0 && (
              <Section title="종료" count={finalGames.length}>
                {finalGames.map((g) => (
                  <GameCard key={g.game_id} game={g} />
                ))}
              </Section>
            )}

            {/* Empty state */}
            {games.length === 0 && (
              <div className="text-center py-20 text-gray-500 text-sm">
                오늘 예정된 경기가 없습니다
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      )}
    </div>
  );
}

function Section({
  title,
  count,
  children,
}: {
  title: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <section className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-gray-400">
          {title}
        </h2>
        <span className="text-[10px] bg-surface px-1.5 py-0.5 rounded text-gray-500">
          {count}
        </span>
      </div>
      <div className="flex flex-col gap-3">{children}</div>
    </section>
  );
}
