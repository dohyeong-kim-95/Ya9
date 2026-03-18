// Canonical types matching the backend API schema

export type GameStatus = "scheduled" | "live" | "final" | "delay" | "cancelled";
export type InningHalf = "top" | "bottom";
export type EventType =
  | "single" | "double" | "triple" | "homerun"
  | "walk" | "hit_by_pitch" | "strikeout"
  | "groundout" | "flyout" | "lineout" | "double_play"
  | "fielders_choice" | "sacrifice_fly" | "sacrifice_bunt"
  | "error" | "stolen_base" | "caught_stealing"
  | "wild_pitch" | "passed_ball" | "balk"
  | "pitching_change" | "inning_change" | "other";
export type Importance = "low" | "medium" | "high" | "critical";
export type SituationTag = "close" | "late" | "chance" | "extra" | "blowout";

export interface TeamInfo { code: string; name: string; }
export interface Score { away: number; home: number; }
export interface Inning { number: number; half: InningHalf; }
export interface Count { balls: number; strikes: number; outs: number; }
export interface Bases { first: boolean; second: boolean; third: boolean; }

export interface BatterInfo {
  name: string;
  team_code: string;
  order: number;
  position: string;
}

export interface PitcherInfo {
  name: string;
  team_code: string;
  throws: "L" | "R";
}

export interface GameSummary {
  game_id: string;
  status: GameStatus;
  start_time: string;
  away_team: TeamInfo;
  home_team: TeamInfo;
  score: Score;
  inning: Inning;
  count: Count;
  bases: Bases;
  situation_tags: SituationTag[];
}

export interface GameEvent {
  event_id: string;
  game_id: string;
  sequence: number;
  timestamp: string;
  event_type: EventType;
  result_label: string;
  zone_label: string;
  rbi: number;
  score_after: Score;
  count_after: Count;
  bases_after: Bases;
  importance: Importance;
}

export interface GameDetail extends GameSummary {
  current_batter: BatterInfo | null;
  current_pitcher: PitcherInfo | null;
  recent_events: GameEvent[];
}

export interface TodayGamesResponse {
  date: string;
  games: GameSummary[];
}

export interface EventsResponse {
  game_id: string;
  events: GameEvent[];
}
