import React from "react";
import MapVisuals from "@/app/map/MapVisuals";

const MapPage = async () => {
	const response = await fetch("http://localhost:8000/dams?skip=0&limit=10");
	const dams = await response.json();
	return <MapVisuals dams={dams} />;
};

export default MapPage;
