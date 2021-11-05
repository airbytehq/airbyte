const StarsIcon = ({
  color = "currentColor",
}: {
  color?: string;
}): JSX.Element => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
    <path
      d="M12.5 0L14.4622 10.5378L25 12.5L14.4622 14.4622L12.5 25L10.5378 14.4622L0 12.5L10.5378 10.5378L12.5 0Z"
      fill={color}
    />
    <path
      d="M32.5 16L33.6773 22.3227L40 23.5L33.6773 24.6773L32.5 31L31.3227 24.6773L25 23.5L31.3227 22.3227L32.5 16Z"
      fill={color}
    />
    <path
      d="M17 28L17.9419 33.0581L23 34L17.9419 34.9419L17 40L16.0581 34.9419L11 34L16.0581 33.0581L17 28Z"
      fill={color}
    />
  </svg>
);

export default StarsIcon;
