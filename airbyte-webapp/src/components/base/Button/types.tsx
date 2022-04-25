export interface IProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  full?: boolean;
  danger?: boolean;
  secondary?: boolean;
  isLoading?: boolean;
  iconOnly?: boolean;
  wasActive?: boolean;
  clickable?: boolean;
  size?: "m" | "xl";
}
