import { theme } from "theme";

interface Props {
  color?: string;
  width?: number;
  height?: number;
}

export const NotificationIcon = ({ color = theme.primaryColor, width = 16, height = 16 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M27.5 15H20L17.5 18.75H12.5L10 15H2.5"
      stroke={color}
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <path
      d="M6.8125 6.3875L2.5 15V22.5C2.5 23.163 2.76339 23.7989 3.23223 24.2678C3.70107 24.7366 4.33696 25 5 25H25C25.663 25 26.2989 24.7366 26.7678 24.2678C27.2366 23.7989 27.5 23.163 27.5 22.5V15L23.1875 6.3875C22.9805 5.97098 22.6615 5.62046 22.2662 5.37535C21.8709 5.13024 21.4151 5.00025 20.95 5H9.05C8.58489 5.00025 8.12908 5.13024 7.73381 5.37535C7.33853 5.62046 7.01947 5.97098 6.8125 6.3875V6.3875Z"
      stroke={color}
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
);
