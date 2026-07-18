"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiError, apiFetch } from "@/app/lib/api";
import type { UserGame } from "@/app/types/steam";

export default function GraphsPage() {
  const router = useRouter();
  const [games, setGames] = useState<UserGame[]>([]);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => { apiFetch<UserGame[]>("/api/steam/games/?ordering=-playtime_forever_minutes").then(setGames).catch((caught) => {
    if (caught instanceof ApiError && [401, 403].includes(caught.status)) { router.replace("/login"); return; }
    setError(caught instanceof Error ? caught.message : "Unable to load graph data.");
  }); }, [router]);
  const top = games.slice(0, 10);
  const max = Math.max(...top.map((g) => g.playtime_forever_minutes), 1);
  const totals = useMemo(() => ({ windows: games.reduce((n, g) => n + g.playtime_windows_minutes, 0), mac: games.reduce((n, g) => n + g.playtime_mac_minutes, 0), linux: games.reduce((n, g) => n + g.playtime_linux_minutes, 0) }), [games]);
  const platformTotal = totals.windows + totals.mac + totals.linux || 1;
  return <main className="mx-auto max-w-7xl p-6 md:p-10"><h1 className="text-3xl font-bold">Playtime graphs</h1>{error && <p className="mt-5 rounded-lg border border-red-500 p-4">{error}</p>}
    <section className="mt-7 rounded-xl bg-neutral-900 p-6"><h2 className="text-xl font-bold">Top games by total playtime</h2><div className="mt-6 space-y-4">{top.map((row) => <div key={row.game.steam_appid}><div className="mb-1 flex justify-between gap-4 text-sm"><span className="truncate">{row.game.name}</span><span>{row.playtime_hours.toLocaleString()} h</span></div><div className="h-4 overflow-hidden rounded bg-neutral-800"><div className="h-full rounded bg-green-600" style={{ width: `${Math.max(2, (row.playtime_forever_minutes / max) * 100)}%` }} /></div></div>)}</div></section>
    <section className="mt-7 rounded-xl bg-neutral-900 p-6"><h2 className="text-xl font-bold">Platform playtime</h2><div className="mt-6 flex h-10 overflow-hidden rounded-lg bg-neutral-800"><div className="flex items-center justify-center bg-blue-600 text-xs font-bold" style={{width:`${totals.windows/platformTotal*100}%`}}>Windows</div><div className="flex items-center justify-center bg-neutral-500 text-xs font-bold" style={{width:`${totals.mac/platformTotal*100}%`}}>Mac</div><div className="flex items-center justify-center bg-orange-600 text-xs font-bold" style={{width:`${totals.linux/platformTotal*100}%`}}>Linux</div></div><div className="mt-4 grid grid-cols-3 gap-3 text-center text-sm"><div>Windows<br/><strong>{(totals.windows/60).toFixed(1)} h</strong></div><div>Mac<br/><strong>{(totals.mac/60).toFixed(1)} h</strong></div><div>Linux<br/><strong>{(totals.linux/60).toFixed(1)} h</strong></div></div></section>
  </main>;
}
