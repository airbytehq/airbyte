import { theme } from "theme";

interface IProps {
  color?: string;
}

export const EndIcon = ({ color = theme.black300 }: IProps) => {
  return (
    <svg width="8" height="10" viewBox="0 0 12 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M1 13L7 7L1 1" stroke={color} stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      <line
        x1="1"
        y1="-1"
        x2="12"
        y2="-1"
        transform="matrix(4.37114e-08 1 1 -4.37114e-08 12 1)"
        stroke={color}
        stroke-width="2"
        stroke-linecap="round"
      />
    </svg>
  );
};
