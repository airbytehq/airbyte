interface Props {
  color?: string;
  width?: number;
  height?: number;
}

export const RightArrowHeadIcon = ({ color = "#6B6B6F", width = 14, height = 14 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 18L15 12L9 6" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
