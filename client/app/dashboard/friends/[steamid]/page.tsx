"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, ExternalLink, Gamepad2, Library, Trophy, Users } from "lucide-react";
import { ApiError, apiFetch } from "@/app/lib/api";
import type { FriendProfile, FriendProfileGame } from "@/app/types/steam";

function formatMinutes(minutes: number) {
  if (minutes < 60) return `${minutes} min`;
  return `${(minutes / 60).toFixed(minutes >= 600 ? 0 : 1)} hrs`;
}

function GameCard({ game, recent = false }: { game: FriendProfileGame; recent?: boolean }) {
  const minutes = recent ? game.playtime_recent_minutes : game.playtime_forever_minutes;
  return (
    <article className="overflow-hidden rounded-xl border border-neutral-800 bg-neutral-900">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={game.header_image} alt="" className="aspect-[460/215] w-full object-cover" />
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <h3 className="font-bold">{game.name}</h3>
          {game.shared && <span className="rounded-full bg-green-950 px-2 py-1 text-xs font-semibold text-green-300">Shared</span>}
        </div>
        <p className="mt-2 text-sm text-neutral-400">{formatMinutes(minutes)} {recent ? "in the last 2 weeks" : "played"}</p>
      </div>
    </article>
  );
}

export default function FriendProfilePage({ params }: { params: Promise<{ steamid: string }> }) {
  const { steamid } = use(params);
  const router = useRouter();
  const [profile, setProfile] = useState<FriendProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<FriendProfile>(`/api/steam/friends/${steamid}/profile/`)
      .then(setProfile)
      .catch((caught) => {
        if (caught instanceof ApiError && [401, 403].includes(caught.status)) { router.replace("/login"); return; }
        setError(caught instanceof Error ? caught.message : "Unable to load this friend.");
      })
      .finally(() => setLoading(false));
  }, [router, steamid]);

  if (loading) return <p className="p-10">Loading friend profile…</p>;
  if (error || !profile) return <main className="mx-auto max-w-7xl p-6 md:p-10"><Link href="/dashboard/friends" className="inline-flex items-center gap-2 text-green-400"><ArrowLeft size={18}/>Back to friends</Link><div className="mt-6 rounded-xl border border-red-500 bg-red-950/30 p-5">{error || "Friend not found."}</div></main>;

  const friend = profile.friend;
  return (
    <main className="mx-auto max-w-7xl p-6 md:p-10">
      <Link href="/dashboard/friends" className="inline-flex items-center gap-2 text-green-400 hover:text-green-300"><ArrowLeft size={18}/>Back to friends</Link>

      <section className="mt-6 rounded-2xl bg-neutral-900 p-6 md:p-8">
        <div className="flex flex-col gap-6 md:flex-row md:items-center">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={friend.avatar_full_url || friend.avatar_url} alt="" className="h-28 w-28 rounded-full border-4 border-neutral-800" />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-3"><h1 className="text-3xl font-bold">{friend.persona_name || friend.steamid}</h1><span className={`rounded-full px-3 py-1 text-sm font-semibold ${profile.status === "Offline" ? "bg-neutral-800 text-neutral-300" : "bg-green-950 text-green-300"}`}>{profile.status}</span></div>
            {profile.real_name && <p className="mt-1 text-neutral-300">{profile.real_name}</p>}
            <p className="mt-2 text-sm text-neutral-400">Steam ID: {friend.steamid}{friend.country_code ? ` · ${friend.country_code}` : ""}</p>
            {profile.current_game && <p className="mt-3 inline-flex items-center gap-2 font-semibold text-green-400"><Gamepad2 size={18}/>Currently playing {profile.current_game}</p>}
          </div>
          {friend.profile_url && <a href={friend.profile_url} target="_blank" rel="noreferrer" className="inline-flex items-center justify-center gap-2 rounded-lg border border-green-500 px-5 py-3 font-semibold text-green-400 hover:bg-green-950/30">Open Steam profile<ExternalLink size={17}/></a>}
        </div>
      </section>

      <section className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          [Library, "Games", profile.summary.games_owned],
          [Users, "Shared games", profile.summary.shared_games],
          [Trophy, "Achievements stored", profile.summary.achievements_unlocked],
          [Gamepad2, "Total playtime", `${profile.summary.total_playtime_hours.toLocaleString()} hrs`],
        ].map(([Icon, label, value]) => {
          const IconComponent = Icon as typeof Library;
          return <div key={String(label)} className="rounded-xl bg-neutral-900 p-5"><IconComponent className="text-green-400"/><p className="mt-4 text-2xl font-bold">{String(value)}</p><p className="text-sm text-neutral-400">{String(label)}</p></div>;
        })}
      </section>

      {profile.games_private && <div className="mt-6 rounded-xl border border-amber-600 bg-amber-950/20 p-5 text-amber-200">This friend&apos;s game details are private, so Steam did not return their library or recent activity.</div>}

      {profile.recent_games.length > 0 && <section className="mt-10"><h2 className="text-2xl font-bold">Recently played</h2><div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{profile.recent_games.map((game) => <GameCard key={game.steam_appid} game={game} recent />)}</div></section>}

      {profile.top_games.length > 0 && <section className="mt-10"><h2 className="text-2xl font-bold">Most played games</h2><p className="mt-1 text-neutral-400">Games marked Shared are also in your library.</p><div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">{profile.top_games.map((game) => <GameCard key={game.steam_appid} game={game} />)}</div></section>}
    </main>
  );
}
