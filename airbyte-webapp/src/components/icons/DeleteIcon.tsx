import { theme } from "theme";

interface IProps {
  color?: string;
  width?: number;
  height?: number;
}

export const DeleteIcon = ({ color = theme.black300, width = 16, height = 16 }: IProps) => {
  return (
    <svg width={`${width}`} height={`${height}`} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M4.5 5V22H19.5V5H4.5Z" stroke={color} strokeWidth="2" strokeLinejoin="round" />
      <path d="M10 10V16.5" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M14 10V16.5" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M2 5H22" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M8 5L9.6445 2H14.3885L16 5H8Z" stroke={color} strokeWidth="2" strokeLinejoin="round" />
    </svg>
  );
};
