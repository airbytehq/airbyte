interface Props {
  color?: string;
  title?: string;
}

export const PauseIcon = ({ color = "currentColor", title }: Props): JSX.Element => (
  <svg viewBox="0 0 6 11" fill="none" role="img" data-icon="pause">
    {title && <title>{title}</title>}
    <line x1="1" y1="1.5" x2="1" y2="10.5" stroke={color} strokeWidth="2" />
    <line x1="5" y1="1.5" x2="5" y2="10.5" stroke={color} strokeWidth="2" />
  </svg>
);
