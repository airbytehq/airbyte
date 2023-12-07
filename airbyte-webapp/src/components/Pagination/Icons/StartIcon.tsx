interface IProps {
  color?: string;
}

export const StartIcon = ({ color = "#6B7280" }: IProps) => {
  return (
    <svg width="12" height="13" viewBox="0 0 12 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M11 13L5 7L11 1" stroke={color} stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      <line x1="1" y1="2" x2="0.999999" y2="13" stroke={color} stroke-width="2" stroke-linecap="round" />
    </svg>
  );
};
