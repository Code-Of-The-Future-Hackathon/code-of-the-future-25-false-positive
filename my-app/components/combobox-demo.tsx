"use client";

import * as React from "react";
import { Check, ChevronsUpDown } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
	Command,
	CommandEmpty,
	CommandGroup,
	CommandInput,
	CommandItem,
	CommandList,
} from "@/components/ui/command";
import {
	Popover,
	PopoverContent,
	PopoverTrigger,
} from "@/components/ui/popover";

export function ComboboxDemo({ options, onChange }) {
	const [open, setOpen] = React.useState(false);
	const [value, setValue] = React.useState("");

	return (
		<Popover open={open} onOpenChange={setOpen}>
			<PopoverTrigger asChild>
				<Button
					variant="outline"
					role="combobox"
					aria-expanded={open}
					className="w-[250px] justify-between"
				>
					{value
						? options.find((option) => option.id === value)
								?.display_name
						: "Потърси язовир..."}
					<ChevronsUpDown className="opacity-50" />
				</Button>
			</PopoverTrigger>
			<PopoverContent
				className="w-[250px] p-0"
				align="start"
				sideOffset={5}
			>
				<Command>
					<CommandInput
						placeholder="Потърси язовир..."
						className="h-9"
					/>
					<CommandList>
						<CommandEmpty>Няма намерени язовири.</CommandEmpty>
						<CommandGroup>
							{options.map((option) => (
								<CommandItem
									key={option.id}
									value={option.id}
									onSelect={(currentValue) => {
										setValue(
											currentValue === value
												? ""
												: currentValue,
										);
										setOpen(false);
										onChange(currentValue);
									}}
								>
									{option.display_name}
									<Check
										className={cn(
											"ml-auto",
											value === option.value
												? "opacity-100"
												: "opacity-0",
										)}
									/>
								</CommandItem>
							))}
						</CommandGroup>
					</CommandList>
				</Command>
			</PopoverContent>
		</Popover>
	);
}
