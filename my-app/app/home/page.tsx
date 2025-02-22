import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";

export default function Home() {
	return (
		<div className="min-h-screen bg-white flex flex-col">
			<header className="bg-red-600 text-white p-4">
				<div className="container mx-auto flex justify-between items-center">
					<h1 className="text-2xl font-bold">Logo</h1>
					<nav>
						<ul className="flex space-x-4">
							<li>
								<a href="#" className="hover:underline">
									За нас
								</a>
							</li>
							<li>
								<a href="#" className="hover:underline">
									Нашата мисия
								</a>
							</li>
							<li>
								<a href="#" className="hover:underline">
									Контакти
								</a>
							</li>
						</ul>
					</nav>
				</div>
			</header>

			<main className="flex-grow container mx-auto px-4 py-8 flex flex-col items-center">
				<h2 className="text-6xl p-4 mt-10 mb-10 font-bold text-center">
					Къде ми отиде водата?
				</h2>
				<div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12 w-full max-w-5xl">
					<Card className="p-6 flex flex-col items-center text-center">
						<h3 className="text-xl font-semibold mb-4">Sectio</h3>
						<p className="mb-4">
							Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
							eiusmod tempor incididunt ut labore et dolore magna aliqua.
						</p>
						<Button className="bg-red-600 hover:bg-red-700 text-white mt-auto">
							Learn More
						</Button>
					</Card>
					<Card className="p-6 flex flex-col items-center text-center">
						<h3 className="text-xl font-semibold mb-4">Section</h3>
						<p className="mb-4">
							Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
							eiusmod tempor incididunt ut labore et dolore magna aliqua.
						</p>
						<Button className="bg-red-600 hover:bg-red-700 text-white mt-auto">
							Learn More
						</Button>
					</Card>
					<Card className="p-6 flex flex-col items-center text-center">
						<h3 className="text-xl font-semibold mb-4">Section</h3>
						<p className="mb-4">
							Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
							eiusmod tempor incididunt ut labore et dolore magna aliqua.
						</p>
						<Button className="bg-red-600 hover:bg-red-700 text-white mt-auto">
							Learn More
						</Button>
					</Card>
				</div>

				{/* Form section */}
				<div className="w-full max-w-md">
					<h2 className="text-2xl font-bold mb-6 text-center">Contact Us</h2>
					<form className="space-y-4">
						<Input type="text" placeholder="Your Name" />
						<Input type="email" placeholder="Your Email" />
						<Button
							type="submit"
							className="w-full bg-red-600 hover:bg-red-700 text-white"
						>
							Submit
						</Button>
					</form>
				</div>
			</main>
		</div>
	);
}
