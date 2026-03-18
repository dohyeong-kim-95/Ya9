// Team color map for KBO teams
export const TEAM_COLORS: Record<string, { primary: string; bg: string }> = {
  OB: { primary: "#131230", bg: "#131230" },   // 두산
  LT: { primary: "#002B5C", bg: "#002B5C" },   // 롯데
  SS: { primary: "#074CA1", bg: "#074CA1" },   // 삼성
  HH: { primary: "#FF6600", bg: "#FF6600" },   // 한화
  KT: { primary: "#000000", bg: "#000000" },   // KT
  NC: { primary: "#315288", bg: "#315288" },   // NC
  LG: { primary: "#C30452", bg: "#C30452" },   // LG
  KW: { primary: "#820024", bg: "#820024" },   // 키움
  SK: { primary: "#CE0E2D", bg: "#CE0E2D" },   // SSG
  HT: { primary: "#EA0029", bg: "#EA0029" },   // KIA
};

export const SITUATION_TAG_STYLES: Record<string, { label: string; className: string }> = {
  close: { label: "접전", className: "bg-amber-500/20 text-amber-400 border-amber-500/30" },
  late: { label: "후반", className: "bg-red-500/20 text-red-400 border-red-500/30" },
  chance: { label: "찬스", className: "bg-green-500/20 text-green-400 border-green-500/30" },
  extra: { label: "연장", className: "bg-purple-500/20 text-purple-400 border-purple-500/30" },
  blowout: { label: "대량득점", className: "bg-gray-500/20 text-gray-400 border-gray-500/30" },
};

export const EVENT_TYPE_LABELS: Record<string, string> = {
  single: "안타",
  double: "2루타",
  triple: "3루타",
  homerun: "홈런",
  walk: "볼넷",
  hit_by_pitch: "사구",
  strikeout: "삼진",
  groundout: "땅볼아웃",
  flyout: "플라이아웃",
  lineout: "라인아웃",
  double_play: "병살",
  fielders_choice: "야수선택",
  sacrifice_fly: "희생플라이",
  sacrifice_bunt: "희생번트",
  error: "실책",
  stolen_base: "도루",
  caught_stealing: "도루실패",
  wild_pitch: "폭투",
  passed_ball: "포일",
  balk: "보크",
  pitching_change: "투수교체",
  inning_change: "이닝전환",
  other: "기타",
};

export const POLL_INTERVAL_HOME = 5000;
export const POLL_INTERVAL_GAME = 3000;
