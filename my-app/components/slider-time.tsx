"use client";

import React, { use, useEffect, useMemo } from "react";
import { cn } from "@/lib/utils";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import TimeRecord from "@/interfaces/time-record.interface";

interface SliderTimeProps {
	value: TimeRecord;
	onChange: (value: TimeRecord) => void;
	className?: string;
}

export function SliderTime({ className, value, onChange }: SliderTimeProps) {
	const months = [
		"Януари",
		"Февруари",
		"Март",
		"Април",
		"Май",
		"Юни",
		"Юли",
		"Август",
		"Септември",
		"Октомври",
		"Ноември",
		"Декември",
	];

	const minYear = 2020;
	const maxYear = 2026;
	const totalMonths = (maxYear - minYear) * 12 + 1;

	// Generate labels for slider
	const labels = useMemo(() => {
		const arr = [];
		for (let i = 0; i < totalMonths; i++) {
			const year = minYear + Math.floor(i / 12);
			const month = months[i % 12];
			arr.push({ label: `${month} ${year}`, value: i, year, month });
		}
		return arr;
	}, []);

	const pivotIndex = labels.findIndex((l) => l.year === 2025);

	const selected =
		labels.find((l) => l.year === value.year && l.month === value.month) ||
		labels[0];

	return (
		<Card className="w-[700px] mt-4 p-5">
			<CardHeader className="text-center">
				<CardTitle>Линия на времето - {selected.label}</CardTitle>
			</CardHeader>
			<CardContent className="space-y-4">
				<div className="relative">
					<Slider
						value={[selected.value]}
						min={0}
						max={totalMonths - 1}
						step={1}
						onValueChange={(val) => {
							const selectedTime = labels[val[0]];
							onChange({ year: selectedTime.year, month: selectedTime.month });
						}}
						className={cn("w-full", className)}
					/>

					<div className="relative mt-2 flex w-full justify-between">
						{labels.map((label, index) => (
							<span
								key={index}
								className={cn(
									"text-xs text-gray-500",
									index === pivotIndex ? "text-red-600 font-bold" : "",
									index % 12 === 0 ? "text-sm font-semibold" : "",
								)}
								style={{
									transform: "translateX(-50%)",
									position: "absolute",
									left: `${(index / (totalMonths - 1)) * 100}%`,
								}}
							>
								{index % 12 === 0 ? label.label.split(" ")[1] : ""}
							</span>
						))}
					</div>
				</div>
			</CardContent>
		</Card>
	);
}
