const ConnectionsIcon = ({
  color = "currentColor",
}: {
  color?: string;
}): JSX.Element => (
  <svg width="28" height="22" viewBox="0 0 28 22" fill="none">
    <rect
      x="0.5"
      y="0.5"
      width="5.93478"
      height="5.30435"
      rx="0.5"
      stroke={color}
    />
    <rect
      x="0.5"
      y="8.06641"
      width="5.93478"
      height="5.30435"
      rx="0.5"
      stroke={color}
    />
    <rect
      x="0.5"
      y="15.6289"
      width="5.93478"
      height="5.30435"
      rx="0.5"
      stroke={color}
    />
    <rect
      x="21.3044"
      y="0.5"
      width="5.93478"
      height="5.30435"
      rx="0.5"
      stroke={color}
    />
    <rect
      x="21.3044"
      y="8.06641"
      width="5.93478"
      height="5.30435"
      rx="0.5"
      stroke={color}
    />
    <rect
      x="21.3044"
      y="15.6289"
      width="5.93478"
      height="5.30435"
      rx="0.5"
      stroke={color}
    />
    <circle cx="14.0498" cy="10.7186" r="2.65217" stroke={color} />
    <line x1="6.30438" y1="10.8477" x2="11.3479" y2="10.8477" stroke={color} />
    <line x1="16.3913" y1="10.8477" x2="21.4348" y2="10.8477" stroke={color} />
    <path
      d="M18.2826 10.7176V4.15234C18.2826 3.60006 18.7303 3.15234 19.2826 3.15234H21.4348"
      stroke={color}
    />
    <path
      d="M9.45654 10.716L9.45654 17.2812C9.45654 17.8335 9.00883 18.2812 8.45654 18.2812H6.9348"
      stroke={color}
    />
    <path
      d="M20.8043 18.2812H19.2826C18.7303 18.2812 18.2826 17.8335 18.2826 17.2812V10.716"
      stroke={color}
    />
    <path
      d="M6.9348 3.15234L8.45654 3.15234C9.00883 3.15234 9.45654 3.60006 9.45654 4.15234L9.45654 10.7176"
      stroke={color}
    />
  </svg>
);

export default ConnectionsIcon;
