interface MoonProps {
  title?: string;
}

export const MoonIcon = ({ title }: MoonProps): JSX.Element => (
  <svg viewBox="0 0 10 10" fill="none" role="img" data-icon="moon">
    {title && <title>{title}</title>}
    <path
      fillRule="evenodd"
      clipRule="evenodd"
      d="M6.38 3.74396V4.31818H9.49719V3.48295H7.69996L9.50465 1.07422V0.5H6.38746V1.33523H8.18469L6.38 3.74396ZM2.75 3.49998C2.75 5.98526 4.76472 7.99998 7.25 7.99998C7.68548 7.99998 8.10652 7.93812 8.5048 7.82271C7.67992 8.84561 6.41638 9.49998 5 9.49998C2.51472 9.49998 0.5 7.48526 0.5 4.99998C0.5 2.95018 1.87052 1.22048 3.7452 0.677246C3.12269 1.44921 2.75 2.43107 2.75 3.49998Z"
      fill="white"
    />
  </svg>
);
