import Image from "next/image";
import Link from 'next/link';

export default function Home() {
  return (
    <div>
      <main className="flex flex-1 w-full max-w-3xl flex-col items-center justify-between py-32 px-16 sm:items-start">
        <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
        <video autoPlay loop muted playsInline style={{
		position:"fixed",
		width: "100%",
		height: "100%",
		objectFit: "cover",
		zIndex: -1,
		top: 0,
		left: 0,
	}}>
		<source src="/background.mp4" type="video/mp4" />
	</video>
	<h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
            Welcome Gamer.
          </h1>
          <p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
            All your game stats in one place.
          </p>
        </div>
        <div className="flex flex-col gap-4 text-base font-medium sm:flex-row mt-10">
          <Link
            className="flex h-12 w-full items-center justify-center rounded-full border border-solid border-black/[.08] px-5 transition-colors hover:border-transparent hover:bg-black/[.04] dark:border-white/[.145] dark:hover:bg-[#1a1a1a] md:w-[158px]"
            href="/login"
            target="_blank"
            rel="noopener noreferrer"
          >
            Log in
          </Link>
        </div>
      </main>
    </div>
  );
}
