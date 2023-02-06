interface PlusIconProps {
  color?: string;
}

export const PlusIcon: React.FC<PlusIconProps> = ({ color = "currentColor" }) => (
  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
    <path
      d="M5.16669 5.1665V0.166504H6.83335V5.1665H11.8334V6.83317H6.83335V11.8332H5.16669V6.83317H0.166687V5.1665H5.16669Z"
      fill={color}
    />
  </svg>
);
