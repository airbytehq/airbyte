interface IProps {
  width?: number;
  height?: number;
  color?: any;
}

export const ArrowDownIcon = ({ width = 12, height = 6, color }: IProps) => {
  return (
    <svg width={`${width}`} height={`${height}`} viewBox="0 0 12 6" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M1 1L6.11628 5L11 1" stroke={color} stroke-width="1.5" stroke-linecap="round" />
    </svg>
  );
};
