import Dam from "@/interfaces/dam.interface";
import { Tendency } from "@/interfaces/dam.interface";
import { useEffect } from "react";

interface DamInfoProps {
	damInfo: Dam;
	onClose: () => void;
	mapType: string;
}

// **Function to calculate tendencies**
const calculateTendency = (measurements: Dam["measurements"]) => {
	if (!measurements || measurements.length < 2) return measurements;

	return measurements.map((record, index) => {
		if (index === 0) return { ...record, tendency: null };

		const prevRecord = measurements[index - 1];
		let tendency: Tendency = Tendency.NO_CHANGE;

		if (record.fill_volume && prevRecord.fill_volume) {
			if (record.fill_volume > prevRecord.fill_volume) {
				tendency = Tendency.UP;
			} else if (record.fill_volume < prevRecord.fill_volume) {
				tendency = Tendency.DOWN;
			}
		}

		return { ...record, tendency };
	});
};

function DamInfoComponent({ damInfo, onClose, mapType }: DamInfoProps) {
	const sortedMeasurements = (damInfo.measurements ?? [])
		.map((m) => ({
			...m,
			timestamp: new Date(m.timestamp),
			fill_volume: m.fill_volume
				? parseFloat(m.fill_volume as any)
				: null,
			avg_incoming_flow: m.avg_incoming_flow
				? parseFloat(m.avg_incoming_flow as any)
				: null,
			avg_outgoing_flow: m.avg_outgoing_flow
				? parseFloat(m.avg_outgoing_flow as any)
				: null,
			tendency: null,
		}))
		.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());

	const calculatedMeasurements = calculateTendency(sortedMeasurements);
	const latestMeasurement = calculatedMeasurements[0] || null;
	const nextMeasurement = calculatedMeasurements[1] || null; // The next closest measurement

	let trendSummary = "Запасът остава стабилен.";

	// **Tendency for mapType "1"**
	if (mapType === "1" && latestMeasurement && nextMeasurement) {
		const latestVolume = latestMeasurement.fill_volume;
		const nextVolume = nextMeasurement.fill_volume;

		if (latestVolume && nextVolume) {
			const change = latestVolume - nextVolume;

			if (change > 0) {
				latestMeasurement.tendency = Tendency.UP;
			} else if (change < 0) {
				latestMeasurement.tendency = Tendency.DOWN;
			} else {
				latestMeasurement.tendency = Tendency.NO_CHANGE;
			}
		}
	}

	useEffect(() => {
		console.log(damInfo);
	}, [damInfo]);

	return (
		<div className="relative mr-3 p-6 text-center">
			<button
				onClick={onClose}
				className="absolute top-1 right-1 text-gray-600 hover:text-gray-900 font-bold text-lg"
				aria-label="Close"
			>
				&times;
			</button>

			<h2 className="text-xl font-semibold">{damInfo.display_name}</h2>
			<p className="text-xl mb-4">{damInfo.description}</p>
			<p className="text-xl mb-4">{damInfo.municipality}</p>

			{latestMeasurement && (
				<table className="w-full border-collapse border border-gray-300 mt-6">
					<tbody>
						<tr className="border-b border-gray-300">
							<td className="font-bold p-2 bg-gray-100">Дата</td>
							<td className="p-2">
								{latestMeasurement.timestamp.toLocaleDateString()}
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
						{mapType === "1" &&
							latestMeasurement.tendency !== null && (
								<tr className="border-b border-gray-300">
									<td className="font-bold p-2 bg-gray-100">
										Тенденция
									</td>
									<td
										className={`p-2 font-bold ${
											latestMeasurement.tendency ===
											Tendency.UP
												? "text-green-600"
												: latestMeasurement.tendency ===
													  Tendency.DOWN
													? "text-red-600"
													: "text-gray-600"
										}`}
									>
										{latestMeasurement.tendency ===
										Tendency.UP
											? "⬆ Повишава се"
											: latestMeasurement.tendency ===
												  Tendency.DOWN
												? "⬇ Намалява"
												: "⏸ Без промяна"}
									</td>
								</tr>
							)}
					</tbody>
				</table>
			)}
		</div>
	);
}

export default DamInfoComponent;
