"use client";

import React, { useState } from "react";
import { MapContainer, TileLayer, Polygon, Marker } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import { DropdownMenuDemo } from "@/components/dropdown-menu-demo";
import { SliderDemo } from "@/components/slider-demo";
import { Card } from "@/components/ui/card";

interface Node {
	id: string;
	displayName: string;
	latitude: number;
	longitude: number;
	node_type: string;
	created_at: string;
	updated_at: string;
}

interface Dam extends Node {
	borderGeometry: [number, number][];
	maxVolume: number;
	description: string;
}

const MapPage = () => {
	const dams: Dam[] = [
		{
			id: "1",
			displayName: "Dam 1",
			latitude: 42.43967,
			longitude: 23.63365,
			node_type: "dam",
			created_at: "2021-08-09T12:00:00Z",
			updated_at: "2021-08-09T12:00:00Z",
			borderGeometry: [
				[42.43967, 23.63365],
				[42.51703, 23.53495],
				[42.45196, 23.55984],
				[42.43714, 23.59795],
			],
			maxVolume: 1000,
			description: "Dam 1 description",
		},
		{
			id: "2",
			displayName: "Dam 2",
			latitude: 42.52196,
			longitude: 23.62249,
			node_type: "dam",
			created_at: "2021-08-09T12:00:00Z",
			updated_at: "2021-08-09T12:00:00Z",
			borderGeometry: [
				[42.52196, 23.62249],
				[42.53025, 23.59589],
				[42.50887, 23.59563],
			],
			maxVolume: 2000,
			description: "Dam 2 description",
		},
	];

	const [year, setYear] = React.useState(2015);
	const [isCardVisible, setIsCardVisible] = useState(false);

	const [selectedDam, setSelectedDam] = useState<Dam | null>(null);

	const handleMarkerClick = (dam: Dam) => {
		setIsCardVisible(true);
		setSelectedDam(dam);
	};

	const handleCloseClick = () => {
		setIsCardVisible(false);
	};

	return (
		<div className="relative h-screen w-screen overflow-hidden">
			<div
				className="absolute top-0 left-1/2 transform -translate-x-1/2 text-xl"
				style={{
					zIndex: 100000,
				}}
			>
				<SliderDemo value={year} onChange={setYear} />
			</div>

			<div style={{ zIndex: 100000 }} className="absolute right-5 top-5">
				<DropdownMenuDemo />
			</div>

			<div
				className={`absolute right-0 bottom-0 transition-transform transform ${
					isCardVisible ? "translate-x-0" : "translate-x-full"
				}`}
				style={{ zIndex: 10000 }}
			>
				<Card className="p-12 max-w-xl">
					<button onClick={handleCloseClick} className="absolute top-2 right-2">
						Close
					</button>
					<h1>{JSON.stringify(selectedDam)}</h1>
					<h1>Hello world</h1>
					<h1>Hello world</h1>
					<h1>Hello world</h1>
					<h1>Hello world</h1>
				</Card>
			</div>

			<MapContainer
				center={[42.4633, 23.6122]}
				zoom={13}
				className="h-full w-full"
			>
				<TileLayer
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
					attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
				/>
				{dams.map((dam, index) => (
					<div key={index}>
						<Polygon
							pathOptions={{ color: "blue" }}
							positions={dam.borderGeometry}
						/>
						<Marker
							position={[dam.latitude, dam.longitude]}
							eventHandlers={{
								click: () => handleMarkerClick(dam),
							}}
						/>
					</div>
				))}
			</MapContainer>
		</div>
	);
};

export default MapPage;
