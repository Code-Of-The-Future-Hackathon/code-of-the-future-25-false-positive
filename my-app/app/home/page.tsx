"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import Header from "@/components/header";
import Footer from "@/components/footer";
import Link from "next/link";

export default function Home() {
	return (
		<div className="min-h-screen bg-white flex flex-col">
			<Header />
			<main className="flex-grow container mx-auto px-4 py-8 sm:py-12 flex flex-col items-center">
				<h1 className="text-2xl sm:text-4xl lg:text-5xl p-4 mt-6 sm:mt-10 mb-8 sm:mb-16 font-bold text-center">
					Къде ми отиде <span className="text-red-600">водата</span>?
				</h1>
				<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-10 mb-12 sm:mb-16 w-full max-w-6xl">
					{[
						{
							title: "Знаеше ли, че в България има над <span class='font-bold'>3000 язовира</span>?",
							description:
								"А знаеш ли какво е тяхното <span class='font-bold'>състояние</span> и какви са <span class='font-bold'>тенденциите</span> на тези в твоя район?",
							mapParam: "map-1",
						},
						{
							title: "Къде се губи <span class='font-bold'>водата</span> от язовирите?",
							description:
								"Окрий пътя на водата от язовирите до твоята <span class='font-bold'>чешма</span> и си отговори на въпроса \"Къде изчезва тя?\"",
							mapParam: "map-2",
						},
						{
							title: "Как се променя пълноводитето на язовирите във времето?",
							description:
								"Посети страницата ни с <span class='font-bold'>история на пълноводието</span> на язовирите и <span class='font-bold'>прогнозите</span> ни за бъдещето на твоето населено място.",
							mapParam: "map-3",
						},
					].map((card, index) => (
						<Card
							key={index}
							className="p-6 sm:p-8 flex flex-col items-center text-center transition-shadow duration-300 hover:shadow-lg border"
						>
							<h3
								className="text-xl sm:text-2xl font-semibold mb-4 sm:mb-6 text-red-600"
								dangerouslySetInnerHTML={{ __html: card.title }}
							></h3>
							<p
								className="mb-6 text-base sm:text-lg"
								dangerouslySetInnerHTML={{
									__html: card.description,
								}}
							></p>
							<Link href={`/map?type=${card.mapParam}`} passHref>
								<Button className="bg-red-600 hover:bg-red-700 text-white mt-auto text-base sm:text-lg px-6 sm:px-8 py-2 sm:py-3">
									Виж тук
								</Button>
							</Link>
						</Card>
					))}
				</div>

				<h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold p-4 sm:p-6 mb-8 sm:mb-12 mt-8 sm:mt-12 text-center">
					<span className="text-red-600">Стани част</span> от каузата
					ни!
				</h1>
				<div className="w-full max-w-xl p-6 sm:p-10 border rounded-lg">
					<h2 className="text-xl sm:text-2xl mb-6 sm:mb-8 text-center">
						Регистрирай своето водоупотребление, за да ни помогнеш
						да пресметнем загубите на вода в населеното ти място
						по-точно.
					</h2>

					<form className="space-y-4 sm:space-y-6">
						<Input
							type="text"
							placeholder="Населено място"
							className="text-base sm:text-lg"
						/>
						<Input
							type="email"
							placeholder="Сметка за изминалия месец (лв)"
							className="text-base sm:text-lg"
						/>
						<Button
							type="submit"
							className="w-full bg-red-600 hover:bg-red-700 text-white text-base sm:text-lg py-2 sm:py-3"
						>
							Изпрати
						</Button>
					</form>
					<p className="text-xs sm:text-sm mt-6 sm:mt-8 text-center">
						* Въвеждайки колко си платил за водата си през изминалия
						месец, ние можем да определим колко точно си изразходил.
						Благодарение на информацията от теб и твоите съграждани,
						и използвайки обществено достъпна информация за водата,
						която излиза от всеки един язовир ежедневно, можем да
						пресметнем каква част от водата бива загубена преди да
						достигне до вас
					</p>
				</div>

				<div className="w-full max-w-2xl p-6 sm:p-10 mt-12 sm:mt-16 text-center">
					<h1 className="text-2xl sm:text-3xl font-bold text-center">
						Направи разлика, <br />{" "}
						<span className="text-red-600">подай сигнал</span>!
					</h1>
					<h2 className="text-xl sm:text-2xl mt-2 mb-8 sm:mb-12 text-center">
						Сега по-лесно от всякога!
					</h2>
					<Link href="/complaint-form">
						<Button
							type="submit"
							className="w-full sm:w-auto max-w-md min-h-12 sm:min-h-16 p-3 sm:p-4 bg-red-600 hover:bg-red-700 text-white text-base sm:text-lg"
						>
							Към страницата за подаване на сигнал
						</Button>
					</Link>
				</div>
			</main>
			<Footer />
		</div>
	);
}
