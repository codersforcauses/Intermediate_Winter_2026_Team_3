import { CenterNav } from '@/app/dashboard/ui/navbar';

export default function Layout({ children } : { children: React.ReactNode }) {
	return (
		<div>
			<CenterNav />
			<div>{ children }</div>
		</div>
	);
}
