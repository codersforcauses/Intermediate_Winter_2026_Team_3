"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { RefreshCw } from "lucide-react";
import { ApiError, apiFetch, apiPost } from "@/app/lib/api";
import type { NewsItem } from "@/app/types/steam";

function plainText(value: string) { return value.replace(/\[\/?[^\]]+\]/g, " ").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim(); }

export default function NewsPage() {
  const router = useRouter(); const [items, setItems] = useState<NewsItem[]>([]); const [error, setError] = useState<string | null>(null); const [syncing, setSyncing] = useState(false);
  async function load() { setItems(await apiFetch<NewsItem[]>("/api/steam/news/")); }
  useEffect(() => { load().catch((caught) => { if (caught instanceof ApiError && [401,403].includes(caught.status)) { router.replace("/login"); return; } setError(caught instanceof Error ? caught.message : "Unable to load news."); }); }, [router]);
  async function sync() { setSyncing(true); setError(null); try { await apiPost("/api/steam/news/"); await load(); } catch (caught) { setError(caught instanceof Error ? caught.message : "Unable to sync Steam news."); } finally { setSyncing(false); } }
  return <main className="mx-auto max-w-5xl p-6 md:p-10"><div className="flex items-center justify-between gap-4"><div><h1 className="text-3xl font-bold">Steam news</h1><p className="mt-2 text-neutral-400">Recent announcements for your most-played games.</p></div><button onClick={sync} disabled={syncing} className="rounded-lg bg-green-600 px-4 py-2 font-semibold disabled:opacity-50"><span className="inline-flex items-center gap-2"><RefreshCw size={17} className={syncing ? "animate-spin" : ""}/>{syncing ? "Syncing…" : "Refresh news"}</span></button></div>{error && <p className="mt-5 rounded-lg border border-red-500 p-4">{error}</p>}{!error && items.length === 0 && <p className="mt-8 rounded-xl bg-neutral-900 p-6">No news has been synchronised yet. Select “Refresh news”.</p>}<div className="mt-7 space-y-5">{items.map((item) => <article key={item.external_id} className="rounded-xl bg-neutral-900 p-6"><div className="flex flex-wrap items-center justify-between gap-2"><span className="text-sm font-semibold text-green-400">{item.game_name}</span><time className="text-xs text-neutral-500">{new Date(item.published_at).toLocaleString()}</time></div><h2 className="mt-2 text-xl font-bold"><a href={item.url} target="_blank" rel="noreferrer" className="hover:underline">{item.title}</a></h2>{item.author && <p className="mt-1 text-sm text-neutral-500">By {item.author}</p>}<p className="mt-3 text-sm leading-6 text-neutral-300">{plainText(item.contents).slice(0, 360)}{plainText(item.contents).length > 360 ? "…" : ""}</p></article>)}</div></main>;
}
