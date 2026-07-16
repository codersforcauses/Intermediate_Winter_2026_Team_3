"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Gamepad2 } from "lucide-react";

import { API_URL, apiFetch } from "@/app/lib/api";
import type { SessionData } from "@/app/types/steam";

export default function LoginPage() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    apiFetch<SessionData>("/api/auth/session/")
      .then((session) => {
        if (session.authenticated) router.replace("/dashboard");
      })
      .finally(() => setChecking(false));
  }, [router]);

  return (
    <main className="min-h-screen flex items-center justify-center px-6 bg-neutral-950 text-white">
      <section className="w-full max-w-md rounded-2xl border border-neutral-700 bg-neutral-900 p-8 shadow-2xl text-center">
        <Gamepad2 className="mx-auto mb-5" size={52} aria-hidden="true" />
        <h1 className="text-3xl font-bold">Steam Stats</h1>
        <p className="mt-3 text-neutral-300">
          Sign in with Steam to create your account automatically and load your game statistics.
        </p>
        <a
          className="mt-8 inline-flex w-full items-center justify-center rounded-lg bg-green-600 px-5 py-3 font-semibold hover:bg-green-500 focus:outline-none focus-visible:ring-2 focus-visible:ring-green-300"
          href={`${API_URL}/auth/login/steam/`}
        >
          {checking ? "Checking session…" : "Sign in through Steam"}
        </a>
        <p className="mt-5 text-sm text-neutral-400">
          New users are registered during their first successful Steam login.
        </p>
      </section>
    </main>
  );
}
