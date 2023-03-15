import { theme } from "theme";

interface IProps {
  color?: string;
  width?: number;
  height?: number;
}

export const DashIcon = ({ color = theme.black300, width = 14, height = 2 }: IProps) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 14 2" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M-0.00012207 1C-0.00012207 0.734784 0.105235 0.48043 0.292771 0.292893C0.480307 0.105357 0.734661 0 0.999878 0H12.9999C13.2651 0 13.5194 0.105357 13.707 0.292893C13.8945 0.48043 13.9999 0.734784 13.9999 1C13.9999 1.26522 13.8945 1.51957 13.707 1.70711C13.5194 1.89464 13.2651 2 12.9999 2H0.999878C0.734661 2 0.480307 1.89464 0.292771 1.70711C0.105235 1.51957 -0.00012207 1.26522 -0.00012207 1Z"
      fill={color}
    />
  </svg>
);
