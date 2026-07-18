"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { RefreshCw } from "lucide-react";
import { ApiError, apiFetch, apiPost } from "@/app/lib/api";
import type { FriendAchievementSummary, FriendRecord, UserGame } from "@/app/types/steam";

export default function FriendsPage() {
  const router = useRouter();
  const [friends, setFriends] = useState<FriendRecord[]>([]);
  const [games, setGames] = useState<UserGame[]>([]);
  const [friendId, setFriendId] = useState("");
  const [appid, setAppid] = useState("");
  const [result, setResult] = useState<FriendAchievementSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      apiFetch<FriendRecord[]>("/api/steam/friends/"),
      apiFetch<UserGame[]>("/api/steam/games/?ordering=game__name"),
    ]).then(([friendRows, gameRows]) => {
      setFriends(friendRows); setGames(gameRows);
      if (friendRows[0]) setFriendId(friendRows[0].friend.steamid);
      if (gameRows[0]) setAppid(String(gameRows[0].game.steam_appid));
    }).catch((caught) => {
      if (caught instanceof ApiError && [401, 403].includes(caught.status)) { router.replace("/login"); return; }
      setError(caught instanceof Error ? caught.message : "Unable to load friends.");
    }).finally(() => setLoading(false));
  }, [router]);

  const selectedFriend = useMemo(() => friends.find((row) => row.friend.steamid === friendId), [friends, friendId]);

  async function loadAchievements(sync = false) {
    if (!friendId || !appid) return;
    setSyncing(true); setError(null);
    const path = `/api/steam/friends/${friendId}/games/${appid}/achievements/`;
    try {
      if (sync) await apiPost(path);
      setResult(await apiFetch<FriendAchievementSummary>(path));
    } catch (caught) {
      setResult(null);
      setError(caught instanceof Error ? caught.message : "Unable to load achievements. Steam privacy settings may prevent access.");
    } finally { setSyncing(false); }
  }

  if (loading) return <p className="p-10">Loading friends…</p>;

  return (
    <main className="mx-auto max-w-7xl p-6 md:p-10">
      <h1 className="text-3xl font-bold">Friends&apos; achievements</h1>
      <p className="mt-2 text-neutral-400">Choose a Steam friend and one of your games, then sync the friend&apos;s public achievement progress.</p>
      {error && <div className="mt-5 rounded-lg border border-red-500 bg-red-950/40 p-4">{error}</div>}
      <section className="mt-6 grid gap-4 rounded-xl bg-neutral-900 p-5 md:grid-cols-[1fr_1fr_auto]">
        <label className="text-sm font-semibold">Friend
          <select value={friendId} onChange={(e) => { setFriendId(e.target.value); setResult(null); }} className="mt-2 w-full rounded-lg bg-neutral-800 p-3">
            {friends.map((row) => <option key={row.friend.steamid} value={row.friend.steamid}>{row.friend.persona_name || row.friend.steamid}</option>)}
          </select>
        </label>
        <label className="text-sm font-semibold">Game
          <select value={appid} onChange={(e) => { setAppid(e.target.value); setResult(null); }} className="mt-2 w-full rounded-lg bg-neutral-800 p-3">
            {games.map((row) => <option key={row.game.steam_appid} value={row.game.steam_appid}>{row.game.name}</option>)}
          </select>
        </label>
        <button onClick={() => loadAchievements(true)} disabled={!friendId || !appid || syncing} className="self-end rounded-lg bg-green-600 px-5 py-3 font-semibold disabled:opacity-50">
          <span className="inline-flex items-center gap-2"><RefreshCw size={17} className={syncing ? "animate-spin" : ""} />{syncing ? "Syncing…" : "Sync achievements"}</span>
        </button>
      </section>

      {selectedFriend && (
        <section className="mt-6 flex items-center gap-4 rounded-xl bg-neutral-900 p-5">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={selectedFriend.friend.avatar_full_url || selectedFriend.friend.avatar_url} alt="" className="h-16 w-16 rounded-full" />
          <div className="flex-1"><Link href={`/dashboard/friends/${selectedFriend.friend.steamid}`} className="text-xl font-bold hover:text-green-400">{selectedFriend.friend.persona_name}</Link><p className="text-sm text-neutral-400">{selectedFriend.unlocked_achievements} achievements stored locally</p></div>
          <Link href={`/dashboard/friends/${selectedFriend.friend.steamid}`} className="rounded-lg border border-green-500 px-4 py-2 font-semibold text-green-400 hover:bg-green-950/30">View profile</Link>
        </section>
      )}

      {result && (
        <section className="mt-8">
          <div className="mb-4 flex items-end justify-between gap-4"><div><h2 className="text-2xl font-bold">{result.game_name}</h2><p className="text-neutral-400">{result.unlocked} of {result.total} unlocked</p></div><div className="text-3xl font-bold text-green-400">{result.total ? Math.round((result.unlocked / result.total) * 100) : 0}%</div></div>
          {result.total === 0 ? <p className="rounded-xl bg-neutral-900 p-6">No achievement data was returned. The game may not support achievements, or the friend&apos;s profile/game details are private.</p> :
          <div className="grid gap-4 md:grid-cols-2">
            {result.achievements.map((row) => (
              <article key={row.achievement.api_name} className={`flex gap-4 rounded-xl border p-4 ${row.achieved ? "border-green-600 bg-green-950/20" : "border-neutral-800 bg-neutral-900 opacity-75"}`}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={(row.achieved ? row.achievement.icon_url : row.achievement.locked_icon_url) || "/file.svg"} alt="" className="h-14 w-14 rounded" />
                <div><h3 className="font-bold">{row.achievement.display_name}</h3><p className="mt-1 text-sm text-neutral-400">{row.achievement.description || (row.achieved ? "Unlocked" : "Locked")}</p>{row.unlocked_at && <p className="mt-2 text-xs text-neutral-500">Unlocked {new Date(row.unlocked_at).toLocaleString()}</p>}</div>
              </article>
            ))}
          </div>}
        </section>
      )}
    </main>
  );
}
