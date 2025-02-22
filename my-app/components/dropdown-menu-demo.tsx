"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { FineTune, ChevronDownCircle, Circle } from "@mynaui/icons-react";

interface CardDropdownMenuProps {
	onChange: (value: string) => void;
	selected: string;
}

export function CardDropdownMenu({
	onChange,
	selected,
}: CardDropdownMenuProps) {
	const [isOpen, setIsOpen] = useState(false);

	const handleSelect = (id: string) => {
		onChange(id);
		setIsOpen(false);
	};

	useEffect(() => {
		console.log("selected", selected);
	}, [selected]);

	return (
		<DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
			<DropdownMenuTrigger asChild>
				<Button variant="outline">
					<FineTune className="w-10 h-10" />
				</Button>
			</DropdownMenuTrigger>
			<DropdownMenuContent className="w-80 p-2 mr-3 bg-transparent shadow-none border-none">
				<div className="grid gap-2">
					<Card
						className={`cursor-pointer transition-colors duration-300 p-3 ${
							selected === "1"
								? "border-black bg-gray-200"
								: "border-gray-300 bg-white"
						}`}
						onClick={() => handleSelect("1")}
					>
						<CardContent className="flex flex-col items-center text-center p-4 space-y-2">
							{selected === "1" ? (
								<ChevronDownCircle className="w-6 h-6 text-gray-600" />
							) : (
								<Circle className="w-6 h-6 text-gray-600" />
							)}
							<p className="text-lg font-semibold">
								Карта на България с язовири
							</p>
							<p className="text-sm text-gray-700">
								Карта на България с всички язовири, оцветени различно според
								тяхното пълноводие.
							</p>
						</CardContent>
					</Card>

					<Card
						className={`cursor-pointer transition-colors duration-300 p-3 ${
							selected === "2"
								? "border-black bg-gray-200"
								: "border-gray-300 bg-white"
						}`}
						onClick={() => handleSelect("2")}
					>
						<CardContent className="flex flex-col items-center text-center p-4 space-y-2">
							{selected === "2" ? (
								<ChevronDownCircle className="w-6 h-6 text-gray-600" />
							) : (
								<Circle className="w-6 h-6 text-gray-600" />
							)}
							<p className="text-lg font-semibold">
								Открий пътя на твоята вода
							</p>
							<p className="text-sm text-gray-700">
								Въвеждайки адреса си, можеш да видиш целия път на водата от
								язовира до твоя дом и да откриеш къде се губи.
							</p>
						</CardContent>
					</Card>

					<Card
						className={`cursor-pointer transition-colors duration-300 p-3 ${
							selected === "3"
								? "border-black bg-gray-200"
								: "border-gray-300 bg-white"
						}`}
						onClick={() => handleSelect("3")}
					>
						<CardContent className="flex flex-col items-center text-center p-4 space-y-2">
							{selected === "3" ? (
								<ChevronDownCircle className="w-6 h-6 text-gray-600" />
							) : (
								<Circle className="w-6 h-6 text-gray-600" />
							)}
							<p className="text-lg font-semibold">
								Статистика за изменението на пълноводието
							</p>
							<p className="text-sm text-gray-700">
								Погледни как е изглеждал твоят язовир и преди и виж прогнози за
								бъдещето.
							</p>
						</CardContent>
					</Card>
				</div>
			</DropdownMenuContent>
		</DropdownMenu>
	);
}
