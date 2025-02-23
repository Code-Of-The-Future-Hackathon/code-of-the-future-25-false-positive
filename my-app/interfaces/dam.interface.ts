import Node from "./node.interface";

enum Tendency {
	UP = "Повишава се",
	NO_CHANGE = "Без промяна",
	DOWN = "Понижава се",
}

interface DamMeasurements {
	timestamp: Date;
	avg_incoming_flow: number | null;
	avg_outgoing_flow: number | null;
	fill_volume: number | null;
	id: string;
}

interface Dam extends Node {
	border_geometry: [number, number][] | null;
	max_volume: number | null;
	description: string | null;
	municipality: string | null;
	owner: string | null;
	owner_contact: string | null;
	operator: string | null;
	operator_contact: string | null;
	places: Record<string, string>;
	measurements: DamMeasurements[] | null;
	future_tendency: Tendency | null;
	will_it_dry_up: boolean;
}

export default Dam;
export { Tendency };
