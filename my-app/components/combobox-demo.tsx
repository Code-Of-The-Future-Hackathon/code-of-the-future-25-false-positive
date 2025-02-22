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

const frameworks = [
	{ value: "next.js", label: "Next.js" },
	{ value: "sveltekit", label: "SvelteKit" },
	{ value: "nuxt.js", label: "Nuxt.js" },
	{ value: "remix", label: "Remix" },
	{ value: "astro", label: "Astro" },
	{ value: "react", label: "React" },
	{ value: "vue", label: "Vue.js" },
	{ value: "angular", label: "Angular" },
	{ value: "ember", label: "Ember.js" },
	{ value: "svelte", label: "Svelte" },
	{ value: "gatsby", label: "Gatsby" },
	{ value: "eleventy", label: "Eleventy" },
	{ value: "preact", label: "Preact" },
	{ value: "solid", label: "SolidJS" },
	{ value: "qwik", label: "Qwik" },
	{ value: "vite", label: "Vite" },
	{ value: "nest", label: "NestJS" },
	{ value: "express", label: "Express.js" },
	{ value: "fastify", label: "Fastify" },
	{ value: "meteor", label: "Meteor" },
	{ value: "redwood", label: "RedwoodJS" },
	{ value: "blitz", label: "Blitz.js" },
	{ value: "alpinejs", label: "Alpine.js" },
	{ value: "htmx", label: "HTMX" },
	{ value: "lit", label: "Lit" },
];

export function ComboboxDemo() {
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
						? frameworks.find((framework) => framework.value === value)?.label
						: "Select framework..."}
					<ChevronsUpDown className="opacity-50" />
				</Button>
			</PopoverTrigger>
			<PopoverContent className="w-[250px] p-0" align="start" sideOffset={5}>
				<Command>
					<CommandInput placeholder="Search framework..." className="h-9" />
					<CommandList>
						<CommandEmpty>No framework found.</CommandEmpty>
						<CommandGroup>
							{frameworks.map((framework) => (
								<CommandItem
									key={framework.value}
									value={framework.value}
									onSelect={(currentValue) => {
										setValue(currentValue === value ? "" : currentValue);
										setOpen(false);
									}}
								>
									{framework.label}
									<Check
										className={cn(
											"ml-auto",
											value === framework.value ? "opacity-100" : "opacity-0",
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
