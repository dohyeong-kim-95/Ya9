"use client";

import type { GameStatus } from "@/lib/types";

const STATUS_CONFIG: Record<GameStatus, { label: string; className: string }> = {
  live: { label: "LIVE", className: "bg-live/20 text-live border-live/40 animate-pulse" },
  final: { label: "종료", className: "bg-final/20 text-final border-final/40" },
  scheduled: { label: "예정", className: "bg-scheduled/20 text-scheduled border-scheduled/40" },
  delay: { label: "지연", className: "bg-amber-500/20 text-amber-400 border-amber-500/40" },
  cancelled: { label: "취소", className: "bg-red-500/20 text-red-400 border-red-500/40" },
};

export default function StatusBadge({ status }: { status: GameStatus }) {
  const config = STATUS_CONFIG[status];
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded border ${config.className}`}
    >
      {config.label}
    </span>
  );
}
