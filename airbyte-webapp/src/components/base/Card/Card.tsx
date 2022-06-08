import { classy } from "utils/components";

interface CardProps {
  full?: boolean;
}

export const Card = classy("div", ({ full }: CardProps) => [
  "bg-white rounded-lg shadow-2",
  {
    "w-full": full,
  },
]);
