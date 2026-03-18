"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import type { GameDetail, GameSummary, DataMeta } from "@/lib/types";
import { fetchGameDetail, fetchTodayGames } from "@/lib/api";
import { POLL_INTERVAL_GAME } from "@/lib/constants";
import Scoreboard from "@/components/hud/Scoreboard";
import GameStatePanel from "@/components/hud/GameStatePanel";
import PlayerCards from "@/components/hud/PlayerCards";
import EventFeed from "@/components/hud/EventFeed";
import GameSwitcher from "@/components/hud/GameSwitcher";
import AdPlaceholder from "@/components/common/AdPlaceholder";

export default function GameHUDPage() {
  const params = useParams();
  const gameId = params.gameId as string;

  const [game, setGame] = useState<GameDetail | null>(null);
  const [meta, setMeta] = useState<DataMeta | null>(null);
  const [allGames, setAllGames] = useState<GameSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadGame = useCallback(async () => {
    try {
      const [detailResp, today] = await Promise.all([
        fetchGameDetail(gameId),
        fetchTodayGames(),
      ]);
      setGame(detailResp.game);
      setMeta(detailResp.meta);
      setAllGames(today.games);
      setError(null);
    } catch {
      setError("경기 데이터를 불러올 수 없습니다");
    } finally {
      setLoading(false);
    }
  }, [gameId]);

  useEffect(() => {
    setLoading(true);
    loadGame();
    const interval = setInterval(loadGame, POLL_INTERVAL_GAME);
    const handleVisibility = () => {
      if (!document.hidden) loadGame();
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () => {
      clearInterval(interval);
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [loadGame]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-gray-500 text-sm">
        로딩 중...
      </div>
    );
  }

  if (error || !game) {
    return (
      <div className="px-4 py-6">
        <Link href="/" className="text-xs text-accent mb-4 inline-block">
          ← 전체 경기
        </Link>
        <div className="rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm p-4 text-center">
          {error || "경기를 찾을 수 없습니다"}
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 py-4 flex flex-col gap-3">
      {/* Back link + staleness */}
      <div className="flex items-center justify-between">
        <Link href="/" className="text-xs text-accent">
          ← 전체 경기
        </Link>
        {meta?.warning && (
          <span className="text-[10px] text-amber-400">{meta.warning}</span>
        )}
        {meta && !meta.warning && meta.source !== "mock" && (
          <span className="text-[10px] text-gray-500">
            {meta.source} · {meta.stale_seconds}s ago
          </span>
        )}
      </div>

      {/* Scoreboard */}
      <Scoreboard game={game} />

      {/* Count / Bases / Tags */}
      <GameStatePanel game={game} />

      {/* Batter / Pitcher */}
      <PlayerCards
        batter={game.current_batter}
        pitcher={game.current_pitcher}
      />

      {/* Event feed */}
      <EventFeed events={game.recent_events} />

      {/* Ad slot */}
      <AdPlaceholder />

      {/* Game switcher */}
      <div>
        <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">
          다른 경기
        </div>
        <GameSwitcher games={allGames} currentGameId={gameId} />
      </div>
    </div>
  );
}
