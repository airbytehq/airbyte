export type IProps = {
  full?: boolean;
  danger?: boolean;
  secondary?: boolean;
  isLoading?: boolean;
  iconOnly?: boolean;
  wasActive?: boolean;
  clickable?: boolean;
} & React.ButtonHTMLAttributes<HTMLButtonElement>;
