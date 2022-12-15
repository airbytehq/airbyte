import { theme } from "theme";

interface Props {
  color?: string;
  width?: number;
  height?: number;
}

export const TickIcon = ({ color = theme.primaryColor, width = 16, height = 16 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 6L9 17L4 12" stroke={color} stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
  </svg>
);
