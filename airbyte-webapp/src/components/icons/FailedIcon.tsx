interface Props {
  width?: number;
  height?: number;
}

export const FailedIcon = ({ width = 24, height = 24 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="10" fill="#FF5454" />
    <path
      d="M15.9091 8.63647L8.63635 15.9092"
      stroke="white"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M8.63635 8.63647L15.9091 15.9092"
      stroke="white"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
);
