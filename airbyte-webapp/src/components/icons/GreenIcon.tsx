interface Props {
  width?: number;
  height?: number;
}

export const GreenIcon = ({ width = 24, height = 24 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="10" fill="#068C24" />
    <path
      d="M17.125 8.63745L10.4563 15.3062L7.42505 12.275"
      stroke="white"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
);
