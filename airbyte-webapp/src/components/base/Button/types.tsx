export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  full?: boolean;
  danger?: boolean;
  white?: boolean;
  secondary?: boolean;
  isLoading?: boolean;
  iconOnly?: boolean;
  wasActive?: boolean;
  clickable?: boolean;
  size?: "m" | "lg" | "xl";
}
