import { theme } from "theme";

interface Props {
  color?: string;
  width?: number;
  height?: number;
}

export const RemoveIcon = ({ color = theme.primaryColor, width = 22, height = 22 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="14" cy="14" r="13" stroke={color} stroke-width="2" />
    <rect x="7" y="13" width="14" height="2" rx="1" fill={color} />
  </svg>
);
