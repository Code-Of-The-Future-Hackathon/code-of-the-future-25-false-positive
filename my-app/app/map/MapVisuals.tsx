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
import { SliderTime } from "@/components/slider-time";
import TimeRecord from "@/interfaces/time-record.interface";
import Dam from "@/interfaces/dam.interface";

import { Card } from "@/components/ui/card";
import { ComboboxDemo } from "@/components/combobox-demo";
import { Button } from "@/components/ui/button";
import DamInfoComponent from "@/components/dam-info";
import RouteInfo from "@/components/route-info";
import GetAddress from "@/components/get-address";
import Address from "@/interfaces/address.interface";
import Path from "@/interfaces/path.interface";
import { useSearchParams } from "next/navigation";

interface MapVisualsProps {
	dams: Dam[];
}

let map;
const MapRelocation = () => {
	map = useMap();
	return null;
};

const MapVisuals = ({ dams }: MapVisualsProps) => {
	const params = useSearchParams();

	let selectedMapParam = "1";

	switch (params.get("type")) {
		case "map-1":
			selectedMapParam = "1";
			break;
		case "map-2":
			selectedMapParam = "2";
			break;
		case "map-3":
			selectedMapParam = "3";
			break;
	}

	const [selectedMap, setSelectedMap] = useState(selectedMapParam);

	const [time, setTime] = useState<TimeRecord>({
		year: 2025,
		month: "Февруари",
	});
	const months = [
		"Януари",
		"Февруари",
		"Март",
		"Април",
		"Май",
		"Юни",
		"Юли",
		"Август",
		"Септември",
		"Октомври",
		"Ноември",
		"Декември",
	];
	const currentMonthInNumber = months.indexOf(time.month) + 1;

	const [isCardVisible, setIsCardVisible] = useState(false);
	const [isAddressPopupVisible, setIsAddressPopupVisible] = useState(false);
	const [selectedDam, setSelectedDam] = useState<Dam | null>(null);
	const [calculatedPath] = useState<Path[]>([]);
	const [calculatedTotalDistance] = useState(0);
	const [userAddress, setUserAddress] = useState<Address | null>(null);

	// FETCH CACLUATED PATH and TOTAL DISTANCE
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

	useEffect(() => {
		if (userAddress) {
			map.flyTo([userAddress.latitude, userAddress.longitude], 13);
		}
	}, [userAddress]);

	const [polylineCoords, setPolylineCoords] = useState([]);

	useEffect(() => {
		fetch(
			`http://localhost:8001/tiles/dam1/${time.year}/${currentMonthInNumber}/geojson`,
		) // Adjust path as necessary
			.then((response) => response.json())
			.then((data) => {
				const coords = [];
				data.features.forEach((feature) => {
					if (feature.geometry.type === "Polygon") {
						coords.push(
							...feature.geometry.coordinates[0].map(
								([lng, lat]) => [lat, lng],
							),
						);
					} else if (feature.geometry.type === "LineString") {
						coords.push(
							...feature.geometry.coordinates.map(
								([lng, lat]) => [lat, lng],
							),
						);
					}
				});
				setPolylineCoords(coords);
			})
			.catch((error) => {});
	}, [currentMonthInNumber, time]);

	return (
		<div className="relative h-screen w-screen overflow-hidden">
			{selectedMap == "3" && (
				<div
					className="absolute top-0 left-1/2 transform -translate-x-1/2 text-xl"
					style={{ zIndex: 100000 }}
				>
					<SliderTime value={time} onChange={setTime} />
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

			{isCardVisible && (
				<div
					className="fixed bottom-8 right-6 transform transition-opacity opacity-100"
					style={{ zIndex: 10000 }}
				>
					<Card className="p-5">
						{selectedMap == "1" && selectedDam && (
							<DamInfoComponent
								damInfo={selectedDam}
								onClose={handleCardClose}
								mapType="1"
							/>
						)}
						{selectedMap == "3" && selectedDam && (
							<DamInfoComponent
								damInfo={selectedDam}
								onClose={handleCardClose}
								mapType="3"
							/>
						)}
					</Card>
				</div>
			)}

			<MapContainer
				// @ts-expect-error because the types are wrong
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
					// @ts-expect-error because the types are wrong
					attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
				/>
				{(selectedMap == "1" || selectedMap == "3") &&
					dams.map((dam, index) => (
						<div key={index}>
							{dam.border_geometry && (
								<Polygon
									pathOptions={{ color: "blue" }}
									// @ts-expect-error because the types are wrong
									positions={dam.border_geometry.coordinates}
									eventHandlers={{
										click: () => handleDamClick(dam),
									}}
								/>
							)}
						</div>
					))}
				{selectedMap == "2" && (
					<Polyline
						pathOptions={{ color: "blue" }}
						positions={[
							[43.0886591327962, 26.792311928631108],
							[43.10477623507718, 26.791766937804624],
							[43.111390978075775, 26.77705218391471],
							[43.11338023459992, 26.79183506172035],
							[43.12630882625508, 26.786862019921795],
							[43.145696591190834, 26.827259470972777],
							[43.15986678556685, 26.82912598561543],
							[43.16049296888975, 26.825673932048765],
							[43.16166308476142, 26.823309855382377],
							[43.16097928566622, 26.8226545749675],
						]}
					/>
				)}

				{selectedMap == "2" && (
					<div className="absolute left-5 top-1/2 transform -translate-y-1/2 z-[10000] rounded-lg">
						<RouteInfo
							dam={selectedDam}
							path={calculatedPath}
							total_distance={calculatedTotalDistance}
						/>
					</div>
				)}

				{selectedMap == "3" && (
					<>
						<TileLayer
							url={`http://localhost:8001/tiles/dam1/${time.year}/${currentMonthInNumber}/{z}/{x}/{y}.png`}
							// @ts-expect-error because the types are wrong
							crossOrigin={true} // Ensure cross-origin requests work
							attribution="Custom Tile Server"
						/>
						{polylineCoords.length > 0 && (
							// @ts-expect-error because the types are wrong
							<Polyline positions={polylineCoords} color="blue" />
						)}
					</>
				)}
				<MapRelocation />
			</MapContainer>
		</div>
	);
};

export default MapVisuals;
