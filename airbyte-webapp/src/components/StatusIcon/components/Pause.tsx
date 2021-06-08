const PauseIcon = ({
  color = "currentColor",
}: {
  color?: string;
}): JSX.Element => (
  <svg width="6" height="11" viewBox="0 0 6 11" fill="none">
    <line x1="1" y1="1.5" x2="1" y2="10.5" stroke={color} strokeWidth="2" />
    <line x1="5" y1="1.5" x2="5" y2="10.5" stroke={color} strokeWidth="2" />
  </svg>
);

export default PauseIcon;
