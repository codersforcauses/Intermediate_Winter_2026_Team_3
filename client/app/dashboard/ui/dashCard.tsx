import type { ReactNode } from "react";

interface DashCardProps {
  label: string;
  stat: string | number;
  icon: ReactNode;
}

export function DashCard({ label, stat, icon }: DashCardProps) {
  return (
    <div className="flex min-w-0 flex-1 items-center justify-center rounded-lg border border-neutral-700 bg-neutral-900 p-6 shadow-lg">
      <div className="text-center">
        <div className="mb-3 flex justify-center">{icon}</div>
        <p className="text-2xl font-bold">{stat}</p>
        <p className="text-sm text-neutral-300">{label}</p>
      </div>
    </div>
  );
}
