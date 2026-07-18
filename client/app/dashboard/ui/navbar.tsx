"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import clsx from "clsx";
import { apiPost } from "@/app/lib/api";

export function CenterNav() {
  const pathname = usePathname();
  const router = useRouter();

  async function logOut() {
    try { await apiPost<void>("/api/auth/logout/"); }
    finally { router.replace("/login"); router.refresh(); }
  }

  const links = [
    ["/dashboard", "Dashboard"],
    ["/dashboard/stats", "Stats"],
    ["/dashboard/friends", "Friends"],
    ["/dashboard/achievements", "Achievements"],
    ["/dashboard/news", "News"],
    ["/dashboard/stats/graphs", "Graphs"],
  ] as const;

  return (
    <nav className="border-b border-green-300 bg-green-600 px-5 py-4 text-white" aria-label="Main navigation">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4">
        <Link href="/dashboard" className="text-xl font-bold">Steam Stats</Link>
        <ul className="flex flex-wrap items-center gap-5 text-sm font-semibold">
          {links.map(([href, label]) => (
            <li key={href}>
              <Link href={href} className={clsx("hover:text-neutral-200", (pathname === href || (href !== "/dashboard" && pathname.startsWith(href))) && "underline underline-offset-4")}>{label}</Link>
            </li>
          ))}
        </ul>
        <button onClick={logOut} className="rounded-md border border-white/60 px-3 py-2 text-sm font-semibold hover:bg-white/10">Log out</button>
      </div>
    </nav>
  );
}
