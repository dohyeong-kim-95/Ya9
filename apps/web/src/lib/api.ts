import type { TodayGamesResponse, GameDetail, EventsResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json() as Promise<T>;
}

export function fetchTodayGames() {
  return fetchJSON<TodayGamesResponse>("/api/games/today");
}

export function fetchGameDetail(gameId: string) {
  return fetchJSON<GameDetail>(`/api/games/${gameId}`);
}

export function fetchGameEvents(gameId: string) {
  return fetchJSON<EventsResponse>(`/api/games/${gameId}/events`);
}
