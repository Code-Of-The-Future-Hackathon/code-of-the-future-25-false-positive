import Link from "next/link";

export default function Header() {
	return (
		<header className="bg-red-600 text-white p-6">
			<div className="container mx-auto flex justify-between items-center">
				<Link href="/home" passHref>
					<p className="text-2xl font-bold">Logo</p>
				</Link>
				<nav>
					<ul className="flex space-x-6">
						<li>
							<a href="#" className="hover:underline text-lg font-bold">
								За нас
							</a>
						</li>
						<li>
							<a href="#" className="hover:underline text-lg font-bold">
								Нашата мисия
							</a>
						</li>
						<li>
							<a href="#" className="hover:underline text-lg font-bold">
								Контакти
							</a>
						</li>
					</ul>
				</nav>
			</div>
		</header>
	);
}
