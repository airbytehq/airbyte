import { theme } from "theme";
interface Props {
  color?: string;
  width?: number;
  height?: number;
}

export const RightArrowIcon = ({ color = theme.primaryColor, width = 52, height = 20 }: Props) => {
  return (
    <svg width={width} height={height} viewBox="0 0 52 20" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 14H48L38.9589 6" stroke={color} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};
