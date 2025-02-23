import React, { useEffect, useRef, useState } from "react";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import Address from "@/interfaces/address.interface";

interface GetAddressProps {
	onAddressSelect: (address: Address) => void;
	onClose: () => void;
}

function GetAddress({ onAddressSelect, onClose }: GetAddressProps) {
	const inputRef = useRef<HTMLInputElement | null>(null);
	const autocompleteRef = useRef<google.maps.places.Autocomplete | null>(
		null,
	);
	const [selectedAddress, setSelectedAddress] = useState<Address | null>(
		null,
	);

	useEffect(() => {
		if (!window.google?.maps?.places) {
			console.error(
				"Google Maps API is not available. Make sure the script is loaded.",
			);
			return;
		}

		if (!inputRef.current) {
			console.error(
				"Input reference is null. Autocomplete cannot initialize.",
			);
			return;
		}

		autocompleteRef.current = new google.maps.places.Autocomplete(
			inputRef.current,
			{
				types: ["geocode"],
				fields: ["address_components", "geometry"],
			},
		);

		autocompleteRef.current.addListener("place_changed", () => {
			const place = autocompleteRef.current!.getPlace();
			if (!place || !place.address_components || !place.geometry) {
				console.error(
					"No valid place selected. Address components or geometry missing.",
				);
				return;
			}

			const getAddressComponent = (type: string) =>
				place?.address_components?.find((comp) =>
					comp.types.includes(type),
				)?.long_name || "";

			const address: Address = {
				street: getAddressComponent("route"),
				streetNumber: getAddressComponent("street_number"),
				city:
					getAddressComponent("locality") ||
					getAddressComponent("administrative_area_level_1"),
				latitude: place.geometry.location?.lat() || 0,
				longitude: place.geometry.location?.lng() || 0,
			};

			setSelectedAddress(address);
		});
	}, []);

	const handleDone = () => {
		if (selectedAddress) {
			onAddressSelect(selectedAddress);
			onClose();
		} else {
			alert("Моля, въведете валиден адрес.");
		}
	};

	return (
		<div className="fixed z-10 top-0 left-0 w-full h-full flex items-center justify-center bg-black bg-opacity-50">
			<div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full">
				<h2 className="text-xl font-semibold mb-4">Въведете адрес</h2>
				<Label htmlFor="autocomplete" className="mb-2 block">
					Адрес
				</Label>
				<input
					id="autocomplete"
					ref={inputRef}
					className="w-full border shadow-sm p-2 rounded focus:outline-black"
					placeholder="Въведете своя адрес..."
				/>
				<div className="flex justify-end space-x-2 mt-4">
					<Button onClick={onClose} variant="outline">
						Отказ
					</Button>
					<Button onClick={handleDone}>Готово</Button>
				</div>
			</div>
		</div>
	);
}

export default GetAddress;
