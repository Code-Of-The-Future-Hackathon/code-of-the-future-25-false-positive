import Dam from "@/interfaces/dam.interface";
import PathNode from "@/interfaces/path.interface";
import { Button } from "@/components/ui/button";
import Link from "next/link";

interface RouteInfoProps {
	dam: Dam | null;
	path: PathNode[]; // Array of PathNode
	total_distance: number;
}

function RouteInfo({ dam, path, total_distance }: RouteInfoProps) {
	return (
		<div className="bg-white z-50 p-6 rounded-lg shadow-md w-96 border border-gray-300">
			<h2 className="text-xl font-semibold text-center mb-4">
				Информация за маршрута
			</h2>

			{dam && (
				<div className="space-y-4">
					<div>
						<span className="block text-gray-700 text-sm font-medium mb-1">
							Източник на водата:
						</span>
						<p className="text-lg font-semibold">
							{dam.display_name}
						</p>
					</div>

					<div>
						<span className="block text-gray-700 text-sm font-medium mb-1">
							Максимален обем:
						</span>
						<p className="text-lg">
							{dam.max_volume?.toLocaleString()} м³
						</p>
					</div>

					<div>
						<span className="block text-gray-700 text-sm font-medium mb-1">
							Описание:
						</span>
						<p className="text-gray-600">
							{dam.description || "Няма описание"}
						</p>
					</div>
				</div>
			)}

			<div className="mt-6">
				<h3 className="text-lg font-semibold">Път на водата</h3>
				<p className="text-gray-600 mb-2">
					Водата преминава през следните места, като снабдява
					населението и индустрията:
				</p>

				<div className="space-y-4">
					{path.map((node) => (
						<div key={node.id} className="border-b pb-2">
							<p className="font-semibold text-lg">
								{node.display_name}
							</p>

							{node.node_type === "place" && node.place_data && (
								<div className="text-gray-600 text-sm">
									<p>
										Население:{" "}
										{node.place_data.population.toLocaleString()}{" "}
										души
									</p>
									<p>
										Потребление:{" "}
										{node.place_data.consumption_per_capita}{" "}
										м³/човек
									</p>
									<p>
										Цена на водата:{" "}
										{node.place_data.water_price} лв./м³
									</p>
								</div>
							)}

							{/* Dam Data */}
							{node.node_type === "dam" && node.dam_data && (
								<div className="text-gray-600 text-sm">
									<p>Описание: {node.dam_data.description}</p>
									<p>Община: {node.dam_data.municipality}</p>
									<p>Собственик: {node.dam_data.owner}</p>
									<p>Оператор: {node.dam_data.operator}</p>
								</div>
							)}

							{/* Distance from Start */}
							<p className="text-gray-500 text-xs">
								Разстояние от началото:{" "}
								{parseFloat(node.distance_from_start).toFixed(
									2,
								)}{" "}
								м
							</p>
						</div>
					))}
				</div>
			</div>

			<div className="mt-6">
				<h3 className="text-lg font-semibold">Общо разстояние</h3>
				<p className="text-gray-600">
					Водата е изминала{" "}
					<span className="font-semibold">
						{(total_distance / 1000).toFixed(2)} км
					</span>{" "}
					до крайната точка.
				</p>
			</div>

			<p className="text-gray-500 text-xs mt-4">
				Данните са приблизителни и подлежат на промяна според текущите
				условия.
			</p>

			<div className="text-center">
				<Link href={"/home"}>
					<Button className="mt-5 bg-red-500">
						Предприеми действие!
					</Button>
				</Link>
			</div>

			{/* ADD DO SOMETHING TAKE ACTION BUTTON */}
			{/* ADD MORE STATS */}
		</div>
	);
}

export default RouteInfo;
