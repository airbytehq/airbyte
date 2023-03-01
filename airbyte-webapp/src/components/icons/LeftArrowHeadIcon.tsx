interface Props {
  color?: string;
  width?: number;
  height?: number;
}

export const LeftArrowHeadIcon = ({ color = "#4F46E5", width = 6, height = 12 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 6 12" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 1L1 6.11628L5 11" stroke={color} strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);
