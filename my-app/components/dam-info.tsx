import Dam from "@/interfaces/dam.interface";
import { Tendency } from "@/interfaces/dam.interface";

interface DamInfoProps {
	damInfo: Dam;
	onClose: () => void;
}

// Hardcoded Measurements (For Testing) DELETE THIS
const hardcodedMeasurements = [
	{
		dam_id: "feb0577f-335b-4516-a148-21d27f40ad5e",
		timestamp: "2024-07-15T08:00:00Z",
		fill_volume: 218260000,
		avg_incoming_flow: 4.2,
		avg_outgoing_flow: 7.8,
		id: "b1bed856-63da-46ce-a8a1-f963ba5af804",
	},
	{
		dam_id: "feb0577f-335b-4516-a148-21d27f40ad5e",
		timestamp: "2024-04-20T08:00:00Z",
		fill_volume: 305564000,
		avg_incoming_flow: 18.3,
		avg_outgoing_flow: 15.7,
		id: "d8d97b74-5dbd-45b8-9ffe-cce79d54eae1",
	},
];

//  Based only on two measurements
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

function DamInfoComponent({ damInfo, onClose }: DamInfoProps) {
	// DENIS TO DO : DELETE THIS, GET ALL FROM /dams:id
	const mergedMeasurements = [
		...hardcodedMeasurements,
		...(damInfo.measurements ?? []),
	].map((m) => ({
		...m,
		timestamp: new Date(m.timestamp),
		fill_volume: m.fill_volume ? parseFloat(m.fill_volume as any) : null,
		avg_incoming_flow: m.avg_incoming_flow
			? parseFloat(m.avg_incoming_flow as any)
			: null,
		avg_outgoing_flow: m.avg_outgoing_flow
			? parseFloat(m.avg_outgoing_flow as any)
			: null,
		tendency: null,
	}));

	const measurements = calculateTendency(
		mergedMeasurements.sort(
			(a, b) => b.timestamp.getTime() - a.timestamp.getTime(),
		),
	);

	const latestMeasurement = measurements ? measurements[0] : null;

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
			<p className="text-xl mb-4">
				{damInfo.description ?? "Няма описание"}
			</p>
			<p className="text-xl mb-4">
				{damInfo.municipality ?? "Няма описание"}
			</p>

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
						<tr className="border-b border-gray-300">
							<td className="font-bold p-2 bg-gray-100">
								Тенденция
							</td>
							<td className="p-2">
								{latestMeasurement.tendency === Tendency.UP ? (
									<span className="text-green-500">
										Повишава се
									</span>
								) : latestMeasurement.tendency ===
								  Tendency.DOWN ? (
									<span className="text-red-500">
										Намалява
									</span>
								) : (
									"Без промяна"
								)}
							</td>
						</tr>
					</tbody>
				</table>
			)}
		</div>
	);
}

export default DamInfoComponent;
