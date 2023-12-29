interface IProps {
  width?: number;
  height?: number;
  color?: any;
}

export const ArrowUpIcon = ({ width = 12, height = 14, color }: IProps) => {
  return (
    <svg width={`${width}`} height={`${height}`} viewBox="0 0 12 6" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M1 5L6.11628 1L11 5" stroke={color} stroke-width="1.5" stroke-linecap="round" />
    </svg>
  );
};
