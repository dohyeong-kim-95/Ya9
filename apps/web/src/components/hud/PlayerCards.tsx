"use client";

import type { BatterInfo, PitcherInfo } from "@/lib/types";

export default function PlayerCards({
  batter,
  pitcher,
}: {
  batter: BatterInfo | null;
  pitcher: PitcherInfo | null;
}) {
  if (!batter && !pitcher) return null;

  return (
    <div className="grid grid-cols-2 gap-3">
      {/* Batter */}
      <div className="bg-surface border border-border rounded-xl p-3">
        <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">
          타자
        </div>
        {batter ? (
          <>
            <div className="text-sm font-bold">{batter.name}</div>
            <div className="text-[10px] text-gray-400 mt-0.5">
              {batter.order}번 · {batter.position}
            </div>
          </>
        ) : (
          <div className="text-xs text-gray-500">—</div>
        )}
      </div>

      {/* Pitcher */}
      <div className="bg-surface border border-border rounded-xl p-3">
        <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-1">
          투수
        </div>
        {pitcher ? (
          <>
            <div className="text-sm font-bold">{pitcher.name}</div>
            <div className="text-[10px] text-gray-400 mt-0.5">
              {pitcher.throws === "L" ? "좌투" : "우투"}
            </div>
          </>
        ) : (
          <div className="text-xs text-gray-500">—</div>
        )}
      </div>
    </div>
  );
}
