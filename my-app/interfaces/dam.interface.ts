import Node from "./node.interface";

interface Dam extends Node {
	borderGeometry: [number, number][];
	maxVolume: number;
	description: string;
}

export default Dam;
