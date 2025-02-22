"use client";

import React, { useState } from "react";
import { MapContainer, TileLayer, Polygon, Polyline } from "react-leaflet";
import "leaflet/dist/leaflet.css";

import { CardDropdownMenu } from "@/components/dropdown-menu-demo";
import { SliderDemo } from "@/components/slider-demo";
import { Card } from "@/components/ui/card";
import { ComboboxDemo } from "@/components/combobox-demo";
import { Button } from "@/components/ui/button";

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
	const [isPopupVisible, setIsPopupVisible] = useState(false);
	const [selectedDam, setSelectedDam] = useState<Dam | null>(null);
	const [selectedMap, setSelectedMap] = useState("1");

	React.useEffect(() => {
		if (selectedMap === "2") {
			setIsPopupVisible(true);
		} else {
			setIsPopupVisible(false);
		}
	}, [selectedMap]);

	const handleDamClick = (dam: Dam) => {
		setIsCardVisible(true);
		setSelectedDam(dam);
	};

	const handleCardClose = () => {
		setIsCardVisible(false);
	};

	const handlePopupClose = () => {
		setIsPopupVisible(false);
		//TODO: set selected dam and update map
	};

	const handleMapSelect = (value: string) => {
		setSelectedMap(value);
		setSelectedDam(null);
		setIsCardVisible(false);
	};

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
				<CardDropdownMenu onChange={handleMapSelect} selected={selectedMap} />
			</div>

			{selectedMap == "1" && (
				<div style={{ zIndex: 100000 }} className="absolute left-5 bottom-5">
					<ComboboxDemo />
				</div>
			)}

			{isPopupVisible && (
				<div
					className="absolute top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50"
					style={{ zIndex: 1 }}
				>
					<div className="bg-white p-4 rounded shadow-lg">
						<h2 className="mb-4 text-center">Избери град</h2>
						<ComboboxDemo />
						<div className="mt-4 text-center">
							<Button onClick={handlePopupClose}>Избери</Button>
						</div>
					</div>
				</div>
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
				center={[42.4633, 23.6122]}
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
								positions={dam.borderGeometry}
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
			</MapContainer>
		</div>
	);
};

export default MapPage;
