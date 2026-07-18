"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { ApiError, apiFetch } from "@/app/lib/api";
import type { UserGame } from "@/app/types/steam";
import { StatCard } from "@/app/dashboard/ui/statCard";

export default function StatsPage() {
  const router = useRouter();
  const [games, setGames] = useState<UserGame[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<UserGame[]>("/api/steam/games/?ordering=-playtime_forever_minutes")
      .then(setGames)
      .catch((caught) => {
        if (caught instanceof ApiError && (caught.status === 401 || caught.status === 403)) {
          router.replace("/login");
          return;
        }
        setError(caught instanceof Error ? caught.message : "Unable to load games.");
      })
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) return <p className="p-10">Loading game statistics…</p>;

  return (
    <main className="mx-auto max-w-7xl p-6 md:p-10">
      <h1 className="mb-6 text-3xl font-bold">Game statistics</h1>
      {error && <p className="rounded-lg border border-red-500 p-4">{error}</p>}
      {!error && games.length === 0 && <p>No games have been synchronised yet.</p>}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        {games.map((entry) => (
          <StatCard
            key={entry.game.steam_appid}
            src={entry.game.header_image}
            title={entry.game.name}
            hours={entry.playtime_hours}
            lastPlayed={entry.last_played_at ? new Date(entry.last_played_at).toLocaleDateString() : "Never"}
          />
        ))}
      </div>
    </main>
  );
}
