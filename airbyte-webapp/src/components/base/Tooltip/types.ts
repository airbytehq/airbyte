import { Placement } from "@floating-ui/react-dom";

export type TooltipCursor = "pointer" | "help" | "not-allowed" | "initial";
export type TooltipTheme = "dark" | "light";

export interface TooltipProps {
  control: React.ReactNode;
  className?: string;
  disabled?: boolean;
  cursor?: TooltipCursor;
  theme?: TooltipTheme;
  placement?: Placement;
}

export type TooltipContext = TooltipProps;
