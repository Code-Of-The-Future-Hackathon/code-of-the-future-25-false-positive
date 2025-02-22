"use client";

import React, { useEffect, useState } from "react";
import {
	MapContainer,
	TileLayer,
	Polygon,
	Polyline,
	useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";

import { CardDropdownMenu } from "@/components/dropdown-menu-demo";
import { SliderDemo } from "@/components/slider-demo";
import { Card } from "@/components/ui/card";
import { ComboboxDemo } from "@/components/combobox-demo";
import { Button } from "@/components/ui/button";

import GetAddress from "@/components/get-address";
import Address from "@/interfaces/address.interface";

interface Node {
	id: string;
	display_name: string;
	latitude: number;
	longitude: number;
	node_type: string;
	created_at: string;
	updated_at: string;
}

interface Dam extends Node {
	border_geometry: {
		type: string;
		coordinates: [number, number][];
	};
	max_volume: number;
	description: string;
}

interface MapVisualsProps {
	dams: Dam[];
}

let map;
const MapRelocation = () => {
	map = useMap();
	return null;
};

const MapVisuals = ({ dams }: MapVisualsProps) => {
	const [year, setYear] = React.useState(2015);
	const [isCardVisible, setIsCardVisible] = useState(false);
	const [isAddressPopupVisible, setIsAddressPopupVisible] = useState(false);
	const [selectedDam, setSelectedDam] = useState<Dam | null>(null);
	const [selectedMap, setSelectedMap] = useState("1");
	const [userAddress, setUserAddress] = useState<Address | null>(null);

	const handleUserAddressSelect = (address: Address) => {
		setUserAddress(address);
	};

	const handleDamClick = (dam: Dam) => {
		setIsCardVisible(true);
		setSelectedDam(dam);
	};

	const handleCardClose = () => {
		setIsCardVisible(false);
	};

	const handleMapSelect = (value: string) => {
		setSelectedMap(value);
		setSelectedDam(null);
		setIsCardVisible(false);
	};

	const [gotoDamLocation, setGotoDamLocation] = useState("");

	const handleGotoDamLocationSelect = () => {
		const dam = dams.find((dam) => dam.id === gotoDamLocation);
		if (dam) {
			map.flyTo([dam.latitude, dam.longitude], 13);
		}
	};

	const handleSearchRoute = () => {
		setIsAddressPopupVisible(false);
	};

	useEffect(() => {
		setIsAddressPopupVisible(selectedMap === "2");
	}, [selectedMap]);

	return (
		<div className="relative h-screen w-screen overflow-hidden">
			{selectedMap == "3" && (
				<div
					className="absolute top-0 left-1/2 transform -translate-x-1/2 text-xl"
					style={{
						zIndex: 100000,
					}}
				>
					<SliderDemo value={year} onChange={setYear} />
				</div>
			)}

			<div style={{ zIndex: 100000 }} className="absolute right-5 top-5">
				<CardDropdownMenu
					onChange={handleMapSelect}
					selected={selectedMap}
				/>
			</div>

			{selectedMap == "1" && (
				<div
					style={{ zIndex: 100000 }}
					className="absolute left-5 bottom-5"
				>
					<ComboboxDemo
						options={dams}
						onChange={setGotoDamLocation}
					/>
					<Button
						className="ml-1"
						onClick={handleGotoDamLocationSelect}
					>
						Избери
					</Button>
				</div>
			)}

			{isAddressPopupVisible && (
				<>
					<GetAddress
						onAddressSelect={handleUserAddressSelect}
						onClose={handleSearchRoute}
					/>
				</>
			)}

			<div
				className={`absolute right-1 bottom-1/2 transition-transform transform translate-y-1/2 ${
					isCardVisible ? "translate-x-0" : "translate-x-full"
				}`}
				style={{ zIndex: 10000 }}
			>
				<Card className="p-12 max-w-lg h-[40rem]">
					{selectedMap == "1" && (
						<>
							<Button
								onClick={handleCardClose}
								className="absolute top-2 right-2"
							>
								Затвори
							</Button>
							<h1>{JSON.stringify(selectedDam)}</h1>
						</>
					)}
					{selectedMap == "3" && (
						<>
							<h1>fortnite topki</h1>
						</>
					)}
				</Card>
			</div>

			<MapContainer
				center={
					// dams
					// ? [dams[0].latitude, dams[0].longitude]
					// : [42.4633, 23.6122]
					[43.0436, 26.7511]
				}
				zoom={13}
				className="h-full w-full z-0"
			>
				<TileLayer
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
					attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
				/>
				{(selectedMap == "1" || selectedMap == "3") &&
					dams.map((dam, index) => (
						<div key={index}>
							<Polygon
								pathOptions={{ color: "blue" }}
								positions={dam.border_geometry.coordinates}
								eventHandlers={{
									click: () => handleDamClick(dam),
								}}
							/>
						</div>
					))}
				{selectedMap == "2" && (
					<Polyline
						pathOptions={{ color: "blue" }}
						positions={[
							[42.43967, 23.63365],
							[42.51703, 23.53495],
						]}
					/>
				)}
				{selectedMap == "3" && (
					<TileLayer
						url={`http://localhost:8001/tiles/dam1/${year}/1/{z}/{x}/{y}.png`}
						crossOrigin={true} // Ensure cross-origin requests work
						attribution="Custom Tile Server"
					/>
				)}
				<MapRelocation />
			</MapContainer>
		</div>
	);
};

export default MapVisuals;
