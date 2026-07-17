"use client";

import Image from "next/image";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, apiFetch, apiPost } from "@/app/lib/api";
import type { AchievementSummary, PlayerAchievement } from "@/app/types/steam";

export default function AchievementsPage() {
  const router = useRouter();
  const [items, setItems] = useState<PlayerAchievement[]>([]);
  const [summary, setSummary] = useState<AchievementSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");

  const load = useCallback(async () => {
    try {
      setError(null);
      const query = new URLSearchParams();
      if (status !== "all") query.set("status", status);
      if (search.trim()) query.set("search", search.trim());
      const [achievementRows, summaryData] = await Promise.all([
        apiFetch<PlayerAchievement[]>(`/api/steam/achievements/?${query.toString()}`),
        apiFetch<AchievementSummary>("/api/steam/achievements/summary/"),
      ]);
      setItems(achievementRows);
      setSummary(summaryData);
    } catch (caught) {
      if (caught instanceof ApiError && (caught.status === 401 || caught.status === 403)) {
        router.replace("/login");
        return;
      }
      setError(caught instanceof Error ? caught.message : "Unable to load achievements.");
    } finally {
      setLoading(false);
    }
  }, [router, search, status]);

  useEffect(() => {
    const timer = window.setTimeout(load, 250);
    return () => window.clearTimeout(timer);
  }, [load]);

  async function syncAchievements() {
    setSyncing(true);
    setError(null);
    try {
      await apiPost("/api/steam/achievements/sync/?max_games=50");
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Achievement sync failed.");
    } finally {
      setSyncing(false);
    }
  }

  const recent = useMemo(() => items.filter((item) => item.achieved && item.unlocked_at).slice(0, 6), [items]);

  if (loading) return <p className="p-10">Loading achievements…</p>;

  return (
    <main className="mx-auto max-w-7xl space-y-8 p-6 md:p-10">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Achievements</h1>
          <p className="mt-1 text-neutral-600">Track unlocked, locked, recent, and rare Steam achievements.</p>
        </div>
        <button onClick={syncAchievements} disabled={syncing} className="rounded-lg bg-green-600 px-5 py-3 font-semibold text-white disabled:opacity-60">
          {syncing ? "Syncing up to 50 games…" : "Sync achievements"}
        </button>
      </div>

      {error && <p className="rounded-lg border border-red-500 bg-red-50 p-4 text-red-800">{error}</p>}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[['Unlocked', summary?.unlocked ?? 0], ['Locked', summary?.locked ?? 0], ['Total tracked', summary?.total ?? 0], ['Completion', `${summary?.completion_percent ?? 0}%`]].map(([label, value]) => (
          <article key={String(label)} className="rounded-xl border bg-white p-5 shadow-sm"><p className="text-sm text-neutral-500">{label}</p><p className="mt-2 text-3xl font-bold">{value}</p></article>
        ))}
      </section>

      {recent.length > 0 && (
        <section>
          <h2 className="mb-4 text-2xl font-semibold">Recently unlocked</h2>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {recent.map((item) => <AchievementCard key={`${item.achievement.api_name}-${item.unlocked_at}`} item={item} />)}
          </div>
        </section>
      )}

      <section>
        <div className="mb-5 flex flex-wrap gap-3">
          <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search achievements or games" className="min-w-64 flex-1 rounded-lg border px-4 py-3" />
          <select value={status} onChange={(event) => setStatus(event.target.value)} className="rounded-lg border px-4 py-3">
            <option value="all">All</option><option value="unlocked">Unlocked</option><option value="locked">Locked</option>
          </select>
        </div>
        {items.length === 0 ? <p className="rounded-xl border p-6">No achievements are stored yet. Press <strong>Sync achievements</strong>. Games or profiles with private statistics may return no data.</p> : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{items.map((item) => <AchievementCard key={`${item.achievement.api_name}-${item.achievement.display_name}`} item={item} />)}</div>
        )}
      </section>

      {summary && summary.games.length > 0 && (
        <section>
          <h2 className="mb-4 text-2xl font-semibold">Completion by game</h2>
          <div className="space-y-3">{summary.games.map((game) => (
            <article key={game.achievement__game__steam_appid} className="rounded-xl border bg-white p-4">
              <div className="mb-2 flex justify-between gap-4"><strong>{game.achievement__game__name}</strong><span>{game.unlocked}/{game.total} ({game.completion_percent}%)</span></div>
              <div className="h-3 overflow-hidden rounded-full bg-neutral-200"><div className="h-full bg-green-600" style={{width: `${game.completion_percent}%`}} /></div>
            </article>
          ))}</div>
        </section>
      )}
    </main>
  );
}

function AchievementCard({ item }: { item: PlayerAchievement }) {
  const icon = item.achieved ? item.achievement.icon_url : item.achievement.locked_icon_url || item.achievement.icon_url;
  const rare = item.achievement.global_percent !== null && item.achievement.global_percent <= 10;
  return (
    <article className={`flex gap-4 rounded-xl border bg-white p-4 shadow-sm ${item.achieved ? "" : "opacity-70"}`}>
      <div className="relative h-16 w-16 shrink-0 overflow-hidden rounded-lg bg-neutral-200">{icon && <Image src={icon} alt="" fill className="object-cover" unoptimized />}</div>
      <div className="min-w-0">
        <div className="flex flex-wrap items-center gap-2"><h3 className="font-bold">{item.achievement.display_name}</h3>{rare && <span className="rounded-full bg-amber-100 px-2 py-1 text-xs font-semibold text-amber-900">Rare</span>}</div>
        <p className="mt-1 text-sm text-neutral-600">{item.achievement.description || (item.achievement.hidden ? "Hidden achievement" : "No description")}</p>
        <p className="mt-2 text-xs text-neutral-500">{item.achieved ? `Unlocked${item.unlocked_at ? ` ${new Date(item.unlocked_at).toLocaleString()}` : ""}` : "Locked"}{item.achievement.global_percent !== null ? ` · ${item.achievement.global_percent.toFixed(1)}% of players` : ""}</p>
      </div>
    </article>
  );
}
