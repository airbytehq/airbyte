const StatusIcon = ({ color = "currentColor" }: { color?: string }): JSX.Element => (
  <svg width="22" height="20" viewBox="0 0 22 20" fill="none">
    <path
      d="M8 5.53894L14 19.5389L17.659 10.9999H22V8.99994H16.341L14 14.4609L8 0.460938L4.341 8.99994H0V10.9999H5.659L8 5.53894Z"
      fill={color}
    />
  </svg>
);

export default StatusIcon;
