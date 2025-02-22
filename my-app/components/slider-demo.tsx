"use client";

import type React from "react";
import { cn } from "@/lib/utils";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

type SliderProps = Omit<
  React.ComponentProps<typeof Slider>,
  "value" | "onValueChange"
>;

interface SliderDemoProps extends SliderProps {
  value: number;
  onChange: (value: number) => void;
}

export function SliderDemo({
  className,
  value,
  onChange,
  ...props
}: SliderDemoProps) {
  const minYear = 2000;
  const maxYear = 2030;

  return (
    <Card className="w-[500px]">
      <CardHeader className="text-center">
        <CardTitle>Линия на времето - {value}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Slider
          value={[value]}
          min={minYear}
          max={maxYear}
          step={1}
          onValueChange={(value) => onChange(value[0])}
          className={cn("w-full", className)}
          {...props}
        />
      </CardContent>
    </Card>
  );
}
