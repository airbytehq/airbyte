export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  full?: boolean;
  danger?: boolean;
  secondary?: boolean;
  light?: boolean;
  isLoading?: boolean;
  iconOnly?: boolean;
  wasActive?: boolean;
  clickable?: boolean;
  size?: "m" | "xl";
}
