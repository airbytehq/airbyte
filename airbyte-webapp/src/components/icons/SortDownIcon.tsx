interface IProps {
  width?: number;
  height?: number;
}

export const SortDownIcon = ({ width = 12, height = 16 }: IProps) => {
  return (
    <svg width={`${width}`} height={`${height}`} viewBox="0 0 12 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M1 5L6.11628 1L11 5" stroke="#4F46E5" stroke-width="1.5" stroke-linecap="round" />
      <path d="M1 11L6.11628 15L11 11" stroke="#999999" stroke-width="1.5" stroke-linecap="round" />
    </svg>
  );
};
