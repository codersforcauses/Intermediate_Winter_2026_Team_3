import clsx from 'clsx';
import Image from 'next/image';

export function GameCard ({ name, href, width, height }) {
	return	(
	<div className="rounded-lg shadow-lg transform hover:scale-105 transition-transform 
        duration-300 ease-in-out w-48 my-5 mx-2">
		<Image
			src={href}
			alt={`${name}`}
			width={width}
			height={height}
		/>
        </div>
	);
}
