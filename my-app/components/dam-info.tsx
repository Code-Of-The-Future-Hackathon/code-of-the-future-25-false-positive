import Dam, { Tendency } from "@/interfaces/dam.interface";
import { useEffect, useState } from "react";
import Link from "next/link";

interface DamInfoProps {
	damInfo: Dam;
	onClose: () => void;
	mapType: string;
}

function DamInfoComponent({ damInfo, onClose }: DamInfoProps) {
	const latestMeasurement =
		damInfo.measurements && damInfo.measurements.length > 0
			? damInfo.measurements[0]
			: null;

	useEffect(() => {
		console.log(damInfo);
	}, [damInfo]);

	const [tendency, setTendency] = useState<Tendency | null>(null);
	const [will_it_dry_up, setWillItDryUp] = useState<boolean | null>(null);

	useEffect(() => {
		const fetchData = async () => {
			try {
				const response = await fetch(
					`http://localhost:8000/dams/${damInfo.id}`,
				);
				const forecastData = await response.json();

				if (forecastData.length < 2) {
					console.warn("Not enough data for trend calculation.");
					return;
				}

				// Get first and last forecasted volume
				const firstValue =
					forecastData[0].forecasted_available_useful_volume;
				const lastValue =
					forecastData[forecastData.length - 1]
						.forecasted_available_useful_volume;
				const tendencyValue = lastValue - firstValue;

				let calculatedTendency: Tendency;
				if (tendencyValue > 0) {
					calculatedTendency = Tendency.UP;
				} else if (tendencyValue < 0) {
					calculatedTendency = Tendency.DOWN;
				} else {
					calculatedTendency = Tendency.NO_CHANGE;
				}

				if (damInfo.max_volume) {
					const threshold = damInfo.max_volume * 0.4;
					const willDry = forecastData.some(
						(data: {
							forecasted_available_useful_volume: number;
						}) =>
							data.forecasted_available_useful_volume < threshold,
					);
					setWillItDryUp(willDry);
				}

				setTendency(calculatedTendency);
			} catch (error) {
				// console.error("Error fetching forecast data:", error);
			}
		};

		fetchData().then((r) => r);
	});

	const tendencyColor =
		tendency === Tendency.UP
			? "text-green-500"
			: tendency === Tendency.DOWN
				? "text-red-500"
				: "text-gray-600";

	return (
		<div className="relative mr-3 p-6 text-center max-w-3xl">
			<button
				onClick={onClose}
				className="absolute top-1 right-1 text-gray-600 hover:text-gray-900 font-bold text-2xl"
				aria-label="Close"
			>
				&times;
			</button>

			<h2 className="text-xl font-semibold">Име на язовира</h2>
			<h2 className="text-xl mb-4">{damInfo.display_name}</h2>
			<h2 className="text-xl font-semibold">Описание</h2>
			<p className="text-xl mb-4">{damInfo.description}</p>
			<h2 className="text-xl font-semibold">Община</h2>
			<p className="text-xl mb-4">{damInfo.municipality}</p>
			<h2 className="text-xl font-semibold">
				Отговорна страна и контакти
			</h2>
			<p className="text-xl mb-2">
				{damInfo.operator} - {damInfo.operator_contact}
			</p>
			<p className="text-xl mb-3">
				{damInfo.owner} - {damInfo.owner_contact}
			</p>

			{latestMeasurement && (
				<table className="w-full border-collapse border border-gray-300 mt-6">
					<tbody>
						<tr className="border-b border-gray-300">
							<td className="font-bold p-2 bg-gray-100">Дата</td>
							<td className="p-2">
								{new Date(
									latestMeasurement.timestamp,
								).toLocaleDateString()}
							</td>
						</tr>
						<tr className="border-b border-gray-300">
							<td className="font-bold p-2 bg-gray-100">Обем</td>
							<td className="p-2">
								{latestMeasurement.fill_volume?.toLocaleString()}{" "}
								м<sup>3</sup>
							</td>
						</tr>
						<tr className="border-b border-gray-300">
							<td className="font-bold p-2 bg-gray-100">
								Входящ поток
							</td>
							<td className="p-2">
								{latestMeasurement.avg_incoming_flow?.toFixed(
									2,
								)}{" "}
								м<sup>3</sup>/с
							</td>
						</tr>
						<tr className="border-b border-gray-300">
							<td className="font-bold p-2 bg-gray-100">
								Изходящ поток
							</td>
							<td className="p-2">
								{latestMeasurement.avg_outgoing_flow?.toFixed(
									2,
								)}{" "}
								м<sup>3</sup>/с
							</td>
						</tr>
					</tbody>
				</table>
			)}

			{tendency && (
				<p className={`text-xl font-semibold mt-4 ${tendencyColor}`}>
					Тенденция: {tendency}
				</p>
			)}

			{!will_it_dry_up && (
				<>
					<h2 className="text-xl font-semibold mt-4 text-red-500">
						Язовирът ще се изсуши в бъдеще. Бъди промяната!
					</h2>

					<Link href="/home#help">
						<button className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded mt-4">
							Подай сигнал
						</button>
					</Link>
				</>
			)}
		</div>
	);
}

export default DamInfoComponent;
