"use client";

import * as React from "react";
import {
	BrandFacebook,
	BrandLinkedin,
	BrandX,
	Check,
	Record,
} from "@mynaui/icons-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
	Popover,
	PopoverContent,
	PopoverTrigger,
} from "@/components/ui/popover";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";
import Header from "@/components/header";
import Footer from "@/components/footer";

import { useState } from "react";

const dams = [
	"Язовир Батак",
	"Язовир Белмекен",
	"Язовир Бистришко",
	"Язовир Божурка",
	"Язовир Боровица",
	"Язовир Боснек",
	"Язовир Бояново",
];

const API_BASE_URL = "http://localhost:8000";

const complaintOptions = {
	"water-loss-route":
		"Открих, че по маршрута на моята вода, има много загуби.",
	"future-bad":
		"Открих, че според изчисленията на тази платформа, в бъдеще язовирът ми ще претърпи бедствие.",
	"water-polution": "Забелязах, че водата ми е замърсена.",
	"illegal-building": "Забелязах незаконно строителство в района на язовира.",
	"illegal-fishing": "Забелязах незаконен риболов.",
	other: "Друг проблем.",
};

type FormData = {
	name?: string;
	user_email?: string;
	phone?: string;
	address?: string;
	dam_id?: string;
	description?: string;
	subject?: string;
	complaint_text?: string;
};

export default function ComplaintFormPage() {
	const [step, setStep] = useState(1);
	const [damOpen, setDamOpen] = React.useState(false);
	const [complaintOpen, setComplaintOpen] = React.useState(false);
	const [formData, setFormData] = React.useState<FormData | null>(null);

	const handleInputChange = (
		e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
	) => {
		const { name, value } = e.target;
		setFormData((prev) => ({ ...prev, [name]: value }));
	};

	const handleDamSelect = (value: string) => {
		setFormData((prev) => ({ ...prev, dam_id: value }));
		setDamOpen(false);
	};

	const handleComplaintSelect = (key: keyof typeof complaintOptions) => {
		setFormData((prev) => ({
			...prev,
			subject: complaintOptions[key],
		}));
		setComplaintOpen(false);
	};

	const handleNext = () => setStep((prev) => prev + 1);

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();

		setFormData((prev) => {
			if (!prev) return null;

			const newDescription = `Подавам сигнал за язовир ${prev.dam_id ?? "Неизвестен"} за проблем ${prev.subject ?? "Неуточнен"}.${
				prev.complaint_text
					? " Допълнителна информация: " + prev.complaint_text
					: ""
			}`;

			const updatedFormData = { ...prev, description: newDescription };

			submitComplaint(updatedFormData);

			return updatedFormData;
		});

		setTimeout(() => {
			setFormData(null);
			handleNext();
		}, 100);
	};

	const submitComplaint = async (complaint: FormData) => {
		try {
			const response = await fetch(`${API_BASE_URL}/complaints`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(complaint),
			});

			if (!response.ok) {
				throw new Error("Failed to submit complaint");
			}

			const data = await response.json();
			return data;
		} catch (error) {
			console.error("Error submitting complaint:", error);
		}
	};

	return (
		<div className="min-h-screen bg-white flex flex-col">
			<Header />
			<main className="container mx-auto px-4 py-8 flex flex-col items-center flex-grow">
				<h1 className="text-4xl font-bold p-4 text-center mb-8">
					<span className="text-red-600">Подай сигнал</span>, <br />{" "}
					подобри своето бъдеще!
				</h1>

				<div className="max-w-2xl w-full">
					<div className="relative mb-8">
						<div className="absolute left-0 top-1/2 h-0.5 w-full -translate-y-1/2 bg-gray-200" />
						<div
							className="absolute left-0 top-1/2 h-0.5 -translate-y-1/2 bg-red-600 transition-all duration-500"
							style={{ width: `${((step - 1) / 2) * 100}%` }}
						/>
						<div className="relative z-10 flex justify-between">
							{[1, 2, 3].map((number) => (
								<div
									key={number}
									className={cn(
										"flex h-8 w-8 items-center justify-center rounded-full border-2 border-gray-300 bg-white text-sm font-semibold",
										step >= number &&
											"border-red-600 bg-red-600 text-white",
									)}
								>
									{step > number ? (
										<Check className="h-4 w-4" />
									) : (
										number
									)}
								</div>
							))}
						</div>
					</div>
					<Card>
						<CardHeader>
							<CardTitle className="text-center text-xl font-semibold">
								{step === 1 && "Информация за теб"}
								{step === 2 && "Данни за сигнала"}
								{step === 3 && "Сигналът е подаден!"}
							</CardTitle>
						</CardHeader>
						<CardContent>
							<form onSubmit={handleSubmit} className="space-y-4">
								{step === 1 && (
									<>
										<div className="mb-4">
											<Label htmlFor="name">
												Пълно име
											</Label>
											<Input
												id="name"
												name="name"
												value={formData?.name}
												onChange={handleInputChange}
												required
											/>
										</div>

										<div className="mb-4 grid grid-cols-2 gap-4">
											<div className="mb-4">
												<Label htmlFor="phone">
													Телефонен номер
												</Label>
												<Input
													id="phone"
													name="phone"
													type="tel"
													value={formData?.phone}
													onChange={handleInputChange}
													required
												/>
											</div>

											<div className="mb-4">
												<Label htmlFor="phone">
													Имейл адрес
												</Label>
												<Input
													id="user_email"
													name="user_email"
													type="user_email"
													value={formData?.user_email}
													onChange={handleInputChange}
													required
												/>
											</div>
										</div>

										<div className="mb-4">
											<Label htmlFor="address">
												Адрес
											</Label>
											<Input
												id="address"
												name="address"
												type="address"
												value={formData?.address}
												onChange={handleInputChange}
												required
											/>
										</div>

										<Button
											type="button"
											className="w-full bg-red-600 hover:bg-red-700 text-white"
											onClick={handleNext}
										>
											Напред
										</Button>
									</>
								)}

								{step === 2 && (
									<>
										<div className="mb-4">
											<Label>
												Язовир, за който искаш да
												подадеш сигнал:
											</Label>
											<Popover
												open={damOpen}
												onOpenChange={setDamOpen}
											>
												<PopoverTrigger asChild>
													<Button
														variant="outline"
														className="w-full justify-between"
													>
														{formData?.dam_id ||
															"Избери язовир"}
													</Button>
												</PopoverTrigger>
												<PopoverContent
													align="start"
													className="w-full max-w-lg p-2 shadow-lg border rounded-lg bg-white"
												>
													{dams.map((dept) => (
														<div
															key={dept}
															onClick={() =>
																handleDamSelect(
																	dept,
																)
															}
															className="cursor-pointer p-2 hover:bg-gray-200"
														>
															{dept}
														</div>
													))}
												</PopoverContent>
											</Popover>
										</div>

										<div className="mb-4">
											<Label>
												За какво подаваш сигнал?
											</Label>
											<Popover
												open={complaintOpen}
												onOpenChange={setComplaintOpen}
											>
												<PopoverTrigger asChild>
													<Button
														variant="outline"
														className="w-full justify-between overflow-hidden text-gray-400"
													>
														{formData?.subject ||
															"Избери вид сигнал"}
													</Button>
												</PopoverTrigger>
												<PopoverContent
													align="start"
													className="w-full max-w-lg p-2 shadow-lg border rounded-lg bg-white"
												>
													{Object.entries(
														complaintOptions,
													).map(
														([key, complaint]) => (
															<div
																key={key}
																onClick={() =>
																	handleComplaintSelect(
																		key as keyof typeof complaintOptions,
																	)
																}
																className="cursor-pointer p-2 hover:bg-gray-200"
															>
																{complaint}
															</div>
														),
													)}
												</PopoverContent>
											</Popover>
										</div>

										{formData?.subject ===
											"Друг проблем." && (
											<div className="mb-4">
												<Label htmlFor="complaint">
													Опиши сигнала, който искаш
													да подадеш:
												</Label>
												<Textarea
													id="complaintText"
													name="complaintText"
													value={
														formData?.complaint_text
													}
													onChange={handleInputChange}
													required
												/>
											</div>
										)}

										<Button
											type="submit"
											className="w-full bg-red-600 hover:bg-red-700 text-white"
										>
											Подай сигнал
										</Button>
									</>
								)}
								{step === 3 && (
									<div className="space-y-6 text-center p-2">
										<p className="text-lg">
											Благодарим ти за подаденият сигнал.
											Благодарение на теб, всички сме една
											стъпка по-близо до решаването на
											проблема!
										</p>
										<p className="text-sm text-muted-foreground">
											Помогни ни да разпространим
											информацията, като я споделиш със
											своите познати и приятели:
										</p>
										<div className="flex justify-center gap-4">
											<Button
												variant="outline"
												size="icon"
											>
												<BrandFacebook className="h-5 w-5" />
											</Button>
											<Button
												variant="outline"
												size="icon"
											>
												<BrandX className="h-5 w-5" />
											</Button>
											<Button
												variant="outline"
												size="icon"
											>
												<BrandLinkedin className="h-5 w-5" />
											</Button>
										</div>
										<Button
											variant="ghost"
											className="text-sm text-muted-foreground underline"
											onClick={() => setStep(1)}
										>
											Пропусни
										</Button>
									</div>
								)}
							</form>
						</CardContent>
					</Card>
				</div>
			</main>
			<Footer />
		</div>
	);
}
