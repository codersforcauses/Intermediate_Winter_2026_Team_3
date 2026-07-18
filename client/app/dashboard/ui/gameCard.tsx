interface GameCardProps {
  name: string;
  href: string;
}

export function GameCard({ name, href }: GameCardProps) {
  return (
    <article className="w-56 overflow-hidden rounded-lg border border-neutral-700 bg-neutral-800 shadow-lg transition-transform hover:scale-[1.02]">
      {href ? (
        // Steam's CDN URLs are dynamic; a normal image avoids an unnecessary Next image allowlist.
        // eslint-disable-next-line @next/next/no-img-element
        <img src={href} alt={name} className="aspect-[460/215] w-full object-cover" />
      ) : (
        <div className="flex aspect-[460/215] items-center justify-center bg-neutral-700 p-3 text-center text-sm">
          {name}
        </div>
      )}
      <h3 className="p-3 text-sm font-semibold">{name}</h3>
    </article>
  );
}
