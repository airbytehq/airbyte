import { Placement } from "@floating-ui/react-dom";

export type ToolTipCursor = "pointer" | "help" | "not-allowed" | "initial";
export type ToolTipTheme = "dark" | "light";

export interface ToolTipProps {
  control: React.ReactNode;
  className?: string;
  disabled?: boolean;
  cursor?: ToolTipCursor;
  theme?: ToolTipTheme;
  placement?: Placement;
}

export type TooltipContext = ToolTipProps;
