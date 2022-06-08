import { classy } from "utils/components";

interface CardProps {
  full?: boolean;
}

export const Card = classy("div", ({ full }: CardProps) => [
  "bg-white rounded-4 shadow-2",
  {
    "w-full": full,
  },
]);
