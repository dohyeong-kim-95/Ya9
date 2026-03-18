"use client";

import { motion } from "framer-motion";
import type { Bases } from "@/lib/types";

export default function BaseDiamond({
  bases,
  size = "md",
}: {
  bases: Bases;
  size?: "sm" | "md" | "lg";
}) {
  const sizeMap = { sm: 24, md: 40, lg: 56 };
  const s = sizeMap[size];
  const half = s / 2;
  const baseSize = size === "sm" ? 5 : size === "md" ? 7 : 9;

  const basePositions = [
    { key: "first", occupied: bases.first, cx: s - 2, cy: half },
    { key: "second", occupied: bases.second, cx: half, cy: 2 },
    { key: "third", occupied: bases.third, cx: 2, cy: half },
  ];

  return (
    <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}>
      {/* Diamond outline */}
      <path
        d={`M ${half} 2 L ${s - 2} ${half} L ${half} ${s - 2} L 2 ${half} Z`}
        fill="none"
        stroke="#4b5563"
        strokeWidth={1}
      />
      {/* Bases */}
      {basePositions.map((b) => (
        <motion.rect
          key={b.key}
          x={b.cx - baseSize / 2}
          y={b.cy - baseSize / 2}
          width={baseSize}
          height={baseSize}
          rx={1}
          fill={b.occupied ? "#facc15" : "#374151"}
          stroke={b.occupied ? "#fbbf24" : "#4b5563"}
          strokeWidth={0.5}
          animate={{
            fill: b.occupied ? "#facc15" : "#374151",
            scale: b.occupied ? [1, 1.3, 1] : 1,
          }}
          transition={{ duration: 0.3 }}
          style={{ transformOrigin: `${b.cx}px ${b.cy}px` }}
        />
      ))}
    </svg>
  );
}
