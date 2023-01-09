interface MinusIconProps {
  color?: string;
}

export const MinusIcon: React.FC<MinusIconProps> = ({ color = "currentColor" }) => (
  <svg width="12" height="2" viewBox="0 0 12 2" fill="none">
    <path d="M11.8334 1.83317V0.166504H0.166687V1.83317H11.8334Z" fill={color} />
  </svg>
);
