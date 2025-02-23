import { MapVisualsNoSSR } from "@/app/map/MapVisualsNoSSR";

const MapPage = async () => {
	const response = await fetch("http://localhost:8000/dams?skip=0&limit=10");
	const dams = await response.json();

	const res2 = await fetch(
		"http://localhost:8000/dams/feb0577f-335b-4516-a148-21d27f40ad5e",
	);
	dams.push(await res2.json());
	return <MapVisualsNoSSR dams={dams} />;
};

export default MapPage;
