interface Props {
  width?: number;
  height?: number;
}

export const DisabledIcon = ({ width = 24, height = 24 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="10" fill="#AAAAAA" />
    <line x1="10" y1="8" x2="10" y2="16" stroke="white" stroke-width="2" stroke-linecap="round" />
    <line x1="14" y1="8" x2="14" y2="16" stroke="white" stroke-width="2" stroke-linecap="round" />
  </svg>
);
