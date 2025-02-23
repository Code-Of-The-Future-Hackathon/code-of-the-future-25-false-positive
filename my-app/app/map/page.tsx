import React from "react";
import MapVisuals from "@/app/map/MapVisuals";

const MapPage = async () => {
	const response = await fetch(
		"http://192.168.0.119:8000/dams?skip=0&limit=10",
	);
	const dams = await response.json();

	const res2 = await fetch(
		"http://192.168.0.119:8000/dams/feb0577f-335b-4516-a148-21d27f40ad5e",
	);
	dams.push(await res2.json());
	return <MapVisuals dams={dams} />;
};

export default MapPage;
