import { StatCard } from '@/app/dashboard/ui/statCard';

const games = [
	{
		name: "StarWars Knights of the Old Republic",
		href: "https://cdn.mos.cms.futurecdn.net/vCcmrnsiyvxzwe88gndsod-865-80.jpg.webp",
		width: 551,
		height:	828,
		hours: 20,
		achievements: 10,
		lastPlayed: "10/5/20"
	},
	{
		name: "Quake Arena",
		href: "https://cdn.mos.cms.futurecdn.net/LjALNWXxWWqL99jLxGs4MY-865-80.jpg.webp",
		width: 551,
		height:	828,
		hours: 20,
		achievements: 10,
		lastPlayed: "10/5/20"
	},
	{
		name: "DOOM",
		href: "https://cdn.mos.cms.futurecdn.net/ZUWCJsgatCG95LYwDX92fh-865-80.jpg.webp",
		width: 551,
		height:	828,
		hours: 20,
		achievements: 10,
		lastPlayed: "10/5/20"
	},
	{
		name: "Street Fighter 4",
		href: "https://cdn.mos.cms.futurecdn.net/jDJLZw2paethAfR9VfH5be-865-80.jpg.webp",
		width: 551,
		height:	828,
		hours: 20,
		achievements: 10,
		lastPlayed: "10/5/20"
	},
	{
		name: "Half Life",
		href: "https://cdn.mos.cms.futurecdn.net/BcJjp5eKrp4agmwXAKECML-865-80.jpg.webp",
		width: 551,
		height:	828,
		hours: 20,
		achievements: 10,
		lastPlayed: "10/5/20"
	},
	{
		name: "Mortal Kombat",
		href: "https://cdn.mos.cms.futurecdn.net/8rpTv6MiS3KQcjkwbiWkWe-865-80.jpg.webp",
		width: 551,
		height:	828,
		hours: 20,
		achievements: 10,
		lastPlayed: "10/5/20"
	},
	{
		name: "Balder's Gate 2",
		href: "https://cdn.mos.cms.futurecdn.net/HLR9KMfM9QmwQYhBVbbVnC-865-80.jpg.webp",
		width: 551,
		height:	828,
		hours: 20,
		achievements: 10,
		lastPlayed: "10/5/20"
	},
]

export default function Page() {
  return (
	<div className="grid grid-cols-2">
		{ games.map((games, index) => (
			<StatCard
				key={index}
				src={games.href}
				width={games.width}
				height={games.height}
				title={games.name}
				hours={games.hours}
				achievements={games.achievements}
				lastPlayed={games.lastPlayed}
			/>
		))}
	</div>	
  );
}
