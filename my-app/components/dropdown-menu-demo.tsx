import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuLabel,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";

export function DropdownMenuDemo() {
	return (
		<DropdownMenu>
			<DropdownMenuTrigger asChild>
				<Button variant="outline">Select Option</Button>
			</DropdownMenuTrigger>
			<DropdownMenuContent className="w-56 p-3" style={{ zIndex: 100000 }}>
				<DropdownMenuLabel className="font-normal">
					<h3 className="mb-2 font-medium leading-none">Choose an option</h3>
					<RadioGroup defaultValue="option1">
						<div className="flex items-center space-x-2 mb-2">
							<RadioGroupItem value="option1" id="option1" />
							<Label htmlFor="option1">Option 1</Label>
						</div>
						<div className="flex items-center space-x-2 mb-2">
							<RadioGroupItem value="option2" id="option2" />
							<Label htmlFor="option2">Option 2</Label>
						</div>
						<div className="flex items-center space-x-2">
							<RadioGroupItem value="option3" id="option3" />
							<Label htmlFor="option3">Option 3</Label>
						</div>
					</RadioGroup>
				</DropdownMenuLabel>
			</DropdownMenuContent>
		</DropdownMenu>
	);
}
