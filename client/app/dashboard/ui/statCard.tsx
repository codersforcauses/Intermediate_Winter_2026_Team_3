interface StatCardProps {
  src: string;
  title: string;
  hours: number;
  achievements?: number;
  lastPlayed: string;
}

export function StatCard({ src, title, hours, achievements, lastPlayed }: StatCardProps) {
  return (
    <article className="flex overflow-hidden rounded-lg border border-neutral-700 bg-neutral-800">
      {src ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={src} alt={title} className="w-44 object-cover" />
      ) : (
        <div className="flex w-44 items-center justify-center bg-neutral-700 p-4 text-center">{title}</div>
      )}
      <div className="flex-1 p-5">
        <h2 className="text-lg font-extrabold">{title}</h2>
        <dl className="mt-3 space-y-1 text-sm text-neutral-200">
          <div><dt className="inline font-bold">Hours played: </dt><dd className="inline">{hours.toFixed(1)}</dd></div>
          {achievements !== undefined && <div><dt className="inline font-bold">Achievements: </dt><dd className="inline">{achievements}</dd></div>}
          <div><dt className="inline font-bold">Last played: </dt><dd className="inline">{lastPlayed}</dd></div>
        </dl>
      </div>
    </article>
  );
}
