import clsx from 'clsx';
import Image from 'next/image';

export function DashCard ({ label, stat, icon }) {
	return	(
	<div className="relative bg-neutral-900 rounded-lg shadow-lg max-w-xs
        sm:max-w-md mx-auto transform transition-transform 
        duration-300 ease-in-out overflow-hidden p-10 m-10
	flex-1 flex flex-row border border-neutral-500 text-center
	justify-center items-center">
		<div className="text-center flex flex-col justify-center items-center">
			<div className="pb-5">{ icon }</div>
			<p className="text-2xl">{ stat }</p>
			<p className="text-base">{ label }</p>
        	</div>
	</div>
	);
}
