import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuLabel,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

interface DropdownMenuDemoProps {
	onChange: (value: string) => void;
	selected: string;
}

export function DropdownMenuDemo({
	onChange,
	selected,
}: DropdownMenuDemoProps) {
	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Button variant="outline">Select Option</Button>
			</DropdownMenuTrigger>
			<DropdownMenuContent className="w-56 p-3" style={{ zIndex: 100000 }}>
				<DropdownMenuLabel className="font-normal">
					<h3 className="mb-2 font-medium leading-none">Choose an option</h3>
					<RadioGroup defaultValue={selected} onValueChange={onChange}>
						<div className="flex items-center space-x-2 mb-2">
							<RadioGroupItem value="1" id="option1" />
							<Label htmlFor="1">Map 1</Label>
						</div>
						<div className="flex items-center space-x-2 mb-2">
							<RadioGroupItem value="2" id="option2" />
							<Label htmlFor="2">Map 2</Label>
						</div>
						<div className="flex items-center space-x-2">
							<RadioGroupItem value="3" id="option3" />
							<Label htmlFor="3">Map 3</Label>
						</div>
					</RadioGroup>
				</DropdownMenuLabel>
			</DropdownMenuContent>
		</DropdownMenu>
	);
}
