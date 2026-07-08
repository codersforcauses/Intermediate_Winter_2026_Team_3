import clsx from 'clsx';
import Image from 'next/image';
import { ChevronRight } from 'lucide-react';

export function StatCard ({ src, width, height, title, hours, achievements, lastPlayed }) {
	return	(
	<div className="flex justify-center flex-nowrap items-center p-10 gap-5">
		<div className="w-24">
			<Image
				src={ src }
				alt={ `${title}` }
				width={ width }
				height={ height }
			/>
		</div>
		<div className="flex gap-5 bg-neutral-800 flex-1 h-full">
			<div className="flex flex-col flex-1 justify-left">
				<span className="bg-neutral-500 px-5"><p className="font-extrabold text-lg">{title}</p></span>
				<div className="p-5">
				<p><b className="font-bold">Hours Played:</b> {hours}</p>
				<p><b className="font-bold">Achievements Owned:</b> {achievements}</p>
				<p><b className="font-bold">Last Played:</b> {lastPlayed}</p>
			
				</div>
			</div>
			<div className="flex items-center">
				<ChevronRight size={32} />
			</div>
		</div>
	</div>
	);
}
