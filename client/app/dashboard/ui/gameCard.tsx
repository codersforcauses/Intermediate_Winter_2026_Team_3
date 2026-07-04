import clsx from 'clsx';
import Image from 'next/image';

export function GameCard ({ name, href, width, height }) {
	return	(
	<div className="relative bg-white rounded-lg shadow-lg max-w-xs
        sm:max-w-md transform hover:scale-105 transition-transform 
        duration-300 ease-in-out w-48 overflow-hidden my-5 mx-2">
		<Image
			src={href}
			alt={`${name}`}
			width={width}
			height={height}
		/>
        </div>
	);
}
