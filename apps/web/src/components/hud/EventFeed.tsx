"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { GameEvent, Importance } from "@/lib/types";

const IMPORTANCE_STYLES: Record<Importance, string> = {
  low: "border-l-gray-600",
  medium: "border-l-blue-500",
  high: "border-l-amber-500",
  critical: "border-l-red-500",
};

export default function EventFeed({ events }: { events: GameEvent[] }) {
  if (events.length === 0) {
    return (
      <div className="bg-surface border border-border rounded-xl p-4 text-center text-xs text-gray-500">
        이벤트 없음
      </div>
    );
  }

  const sorted = [...events].sort((a, b) => b.sequence - a.sequence);

  return (
    <div className="bg-surface border border-border rounded-xl p-3">
      <div className="text-[10px] uppercase tracking-wider text-gray-500 mb-2">
        최근 플레이
      </div>
      <div className="space-y-1.5 max-h-48 overflow-y-auto">
        <AnimatePresence initial={false}>
          {sorted.map((evt) => (
            <motion.div
              key={evt.event_id}
              className={`border-l-2 ${IMPORTANCE_STYLES[evt.importance]} pl-2.5 py-1`}
              initial={{ opacity: 0, x: -12 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25 }}
            >
              <div className="text-xs font-medium">{evt.result_label}</div>
              {evt.zone_label && (
                <div className="text-[10px] text-gray-500">{evt.zone_label}</div>
              )}
              {evt.rbi > 0 && (
                <div className="text-[10px] text-amber-400 font-semibold">
                  {evt.rbi} 타점
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
