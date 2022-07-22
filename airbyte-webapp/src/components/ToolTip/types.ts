export type ToolTipCursor = "pointer" | "help" | "not-allowed" | "initial";
export type ToolTipTheme = "dark" | "light";
export type ToolTipAlignment = "top" | "right" | "bottom" | "left";

export interface ToolTipProps {
  control: React.ReactNode;
  className?: string;
  disabled?: boolean;
  cursor?: ToolTipCursor;
  theme?: ToolTipTheme;
  align?: ToolTipAlignment;
}

export type TooltipContext = ToolTipProps;
