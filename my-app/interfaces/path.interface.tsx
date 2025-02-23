interface Path {
	id: string;
	node_type: string;
	display_name: string;
	latitude: string;
	longitude: string;
	distance_from_start: string;
	dam_data?: {
		max_volume: string;
		description: string;
		municipality: string;
		owner: string;
		operator: string;
	} | null;
	place_data?: {
		population: number;
		consumption_per_capita: string;
		water_price: string;
		non_dam_incoming_flow: string;
		radius: string;
		municipality: string;
	} | null;
}

export default Path;
