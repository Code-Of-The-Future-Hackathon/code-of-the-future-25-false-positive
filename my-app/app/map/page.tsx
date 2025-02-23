import React from "react";
import MapVisuals from "@/app/map/MapVisuals";

const MapPage = async () => {
	try {
		const response = await fetch(
			"http://localhost:8000/dams?skip=0&limit=10",
		);
		const dams = await response.json();
		return <MapVisuals dams={dams} />;
	} catch (error) {
		console.error("Failed to fetch data", error);
		return <div>Failed to fetch data</div>;
	}
};

export default MapPage;
