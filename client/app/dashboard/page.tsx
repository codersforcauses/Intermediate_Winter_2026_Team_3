import { GameCard } from '@/app/dashboard/ui/gameCard';
import { DashCard } from '@/app/dashboard/ui/dashCard';
import { Flag, UsersRound, Clock, Disc3 } from 'lucide-react';

// mock values.
const stats = [
	{
		label: "Friends",
		stat: 6000,
		component: (props = {}) => <UsersRound size={36}/>
	},
	{
		label: "Games Owned",
		stat: 732,
		component: (props = {}) => <Disc3 size={36}/>

	},
	{
		label: "Achievements",
		stat: 9321,
		component: (props = {}) => <Flag size={36}/>
	},
	{
		label: "Total Hours Played",
		stat: 1232412132,
		component: (props = {}) => <Clock size={36}/>
	},
]


const games = [
	{
		name: "StarWars Knights of the Old Republic",
		href: "https://cdn.mos.cms.futurecdn.net/vCcmrnsiyvxzwe88gndsod-865-80.jpg.webp",
		width: 551,
		height:	828
	},
	{
		name: "Quake Arena",
		href: "https://cdn.mos.cms.futurecdn.net/LjALNWXxWWqL99jLxGs4MY-865-80.jpg.webp",
		width: 551,
		height:	828
	},
	{
		name: "DOOM",
		href: "https://cdn.mos.cms.futurecdn.net/ZUWCJsgatCG95LYwDX92fh-865-80.jpg.webp",
		width: 551,
		height:	828
	},
	{
		name: "Street Fighter 4",
		href: "https://cdn.mos.cms.futurecdn.net/jDJLZw2paethAfR9VfH5be-865-80.jpg.webp",
		width: 551,
		height:	828
	},
	{
		name: "Half Life",
		href: "https://cdn.mos.cms.futurecdn.net/BcJjp5eKrp4agmwXAKECML-865-80.jpg.webp",
		width: 551,
		height:	828
	},
	{
		name: "Mortal Kombat",
		href: "https://cdn.mos.cms.futurecdn.net/8rpTv6MiS3KQcjkwbiWkWe-865-80.jpg.webp",
		width: 551,
		height:	828
	},
	{
		name: "Balder's Gate 2",
		href: "https://cdn.mos.cms.futurecdn.net/HLR9KMfM9QmwQYhBVbbVnC-865-80.jpg.webp",
		width: 551,
		height:	828
	},
]



export default function Page() {
  return (
	  <div>
		<div className="flex flex-row items-stretch gap-30 mx-20">
			{stats.map((stats, index) => (
			<DashCard 
			// need to add iconss
				key={index}
				label={ stats.label }
				stat={ stats.stat }
				icon={ stats.component({}) }
			/>)
				  )}
		</div>
		<div className="mb-10 mt-5 mx-10">
		<h2 className="text-2xl mb-5"> Game Library </h2>
			<div className="bg-neutral-900 flex flex-wrap justify-center items-center px-10 py-5">
				{games.map((games, index) => ( 
					<GameCard
						key={index}
						name={games.name}
						href={games.href}
						width={games.width}
						height={games.height}
						
					/>
								)
				  )}
			</div>
		</div>
	  </div>
  );
}
