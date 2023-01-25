import styles from "./CircleLoader.module.scss";

interface CircleLoaderProps {
  title?: string;
}

export const CircleLoader = ({ title }: CircleLoaderProps): JSX.Element => (
  <svg className={styles.spinner} role="img" viewBox="0 0 16 16" width="18" height="18" data-icon="circle-loader">
    <defs>
      <linearGradient
        id="circleLoaderGradient"
        x1="4.25"
        y1="0.5"
        x2="4.25"
        y2="15.5"
        spreadMethod="pad"
        gradientUnits="userSpaceOnUse"
      >
        <stop offset="0%" stopColor={styles.gradientColor} />
        <stop offset="100%" stopColor={styles.gradientColor} stopOpacity=".1" />
      </linearGradient>
    </defs>
    {title && <title>{title}</title>}
    <g>
      <path
        d="M8,0.5C3.85775,0.5,0.5,3.85775,0.5,8s3.35775,7.5,7.5,7.5v-2c-3.03768,0-5.5-2.4623-5.5-5.5s2.46232-5.5,5.5-5.5v-2Z"
        clipRule="evenodd"
        fill="url(#circleLoaderGradient)"
        fillRule="evenodd"
      />
      <circle cx="8" cy="8" r="3" className={styles.centerDot} />
    </g>
  </svg>
);
