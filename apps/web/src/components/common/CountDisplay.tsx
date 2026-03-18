"use client";

import type { Count } from "@/lib/types";

function Dots({
  count,
  max,
  activeColor,
}: {
  count: number;
  max: number;
  activeColor: string;
}) {
  return (
    <div className="flex gap-1">
      {Array.from({ length: max }).map((_, i) => (
        <div
          key={i}
          className={`w-2.5 h-2.5 rounded-full border ${
            i < count ? activeColor : "bg-gray-700 border-gray-600"
          }`}
        />
      ))}
    </div>
  );
}

export default function CountDisplay({ count }: { count: Count }) {
  return (
    <div className="flex gap-3 items-center text-[10px] font-mono uppercase tracking-wider text-gray-400">
      <div className="flex items-center gap-1">
        <span>B</span>
        <Dots count={count.balls} max={4} activeColor="bg-green-500 border-green-400" />
      </div>
      <div className="flex items-center gap-1">
        <span>S</span>
        <Dots count={count.strikes} max={3} activeColor="bg-yellow-500 border-yellow-400" />
      </div>
      <div className="flex items-center gap-1">
        <span>O</span>
        <Dots count={count.outs} max={3} activeColor="bg-red-500 border-red-400" />
      </div>
    </div>
  );
}
