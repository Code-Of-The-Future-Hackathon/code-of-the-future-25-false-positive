"use client";

import dynamic from "next/dynamic";

export const MapVisualsNoSSR = dynamic(() => import("@/app/map/MapVisuals"), {
	ssr: false,
});
