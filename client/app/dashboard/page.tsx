"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Clock, Disc3, Flag, RefreshCw, UsersRound } from "lucide-react";

import { apiFetch, apiPost, ApiError } from "@/app/lib/api";
import type { DashboardData } from "@/app/types/steam";
import { DashCard } from "@/app/dashboard/ui/dashCard";
import { GameCard } from "@/app/dashboard/ui/gameCard";

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [syncing, setSyncing] = useState(false);

  async function load() {
    try {
      setError(null);
      setData(await apiFetch<DashboardData>("/api/dashboard/"));
    } catch (caught) {
      if (caught instanceof ApiError && (caught.status === 401 || caught.status === 403)) {
        router.replace("/login");
        return;
      }
      setError(caught instanceof Error ? caught.message : "Unable to load the dashboard.");
    }
  }

  useEffect(() => {
    let cancelled = false;

    apiFetch<DashboardData>("/api/dashboard/")
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((caught) => {
        if (cancelled) return;
        if (caught instanceof ApiError && (caught.status === 401 || caught.status === 403)) {
          router.replace("/login");
          return;
        }
        setError(caught instanceof Error ? caught.message : "Unable to load the dashboard.");
      });

    return () => {
      cancelled = true;
    };
  }, [router]);

  async function syncSteam() {
    setSyncing(true);
    try {
      await apiPost("/api/steam/sync/");
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Steam synchronisation failed.");
    } finally {
      setSyncing(false);
    }
  }

  if (!data && !error) return <p className="p-10">Loading your Steam statistics…</p>;

  return (
    <main className="mx-auto max-w-7xl p-6 md:p-10">
      <div className="mb-7 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          {data?.profile.avatar_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img className="h-16 w-16 rounded-full" src={data.profile.avatar_url} alt="Steam avatar" />
          )}
          <div>
            <h1 className="text-3xl font-bold">{data?.profile.persona_name || "Your dashboard"}</h1>
            <p className="text-sm text-neutral-400">
              {data?.profile.last_synced ? `Last synced ${new Date(data.profile.last_synced).toLocaleString()}` : "Not synced yet"}
            </p>
          </div>
        </div>
        <button onClick={syncSteam} disabled={syncing} className="inline-flex items-center gap-2 rounded-lg bg-green-600 px-4 py-2 font-semibold disabled:opacity-60">
          <RefreshCw size={18} className={syncing ? "animate-spin" : ""} />
          {syncing ? "Syncing…" : "Sync Steam"}
        </button>
      </div>

      {error && <div className="mb-6 rounded-lg border border-red-500 bg-red-950/50 p-4 text-red-100">{error}</div>}

      {data && (
        <>
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <DashCard label="Friends" stat={data.summary.friends} icon={<UsersRound size={34} />} />
            <DashCard label="Games owned" stat={data.summary.games_owned} icon={<Disc3 size={34} />} />
            <DashCard label="Achievements" stat={data.summary.achievements_unlocked} icon={<Flag size={34} />} />
            <DashCard label="Total hours played" stat={data.summary.total_playtime_hours.toLocaleString()} icon={<Clock size={34} />} />
          </section>

          <section className="mt-10">
            <h2 className="mb-5 text-2xl font-bold">Top games</h2>
            {data.top_games.length ? (
              <div className="flex flex-wrap gap-5 rounded-xl bg-neutral-900 p-5">
                {data.top_games.map((entry) => (
                  <GameCard key={entry.game.steam_appid} name={entry.game.name} href={entry.game.header_image} />
                ))}
              </div>
            ) : (
              <p className="rounded-lg bg-neutral-900 p-6 text-neutral-300">No public game data is available yet. Select “Sync Steam” or make your Steam game details public.</p>
            )}
          </section>
        </>
      )}
    </main>
  );
}
