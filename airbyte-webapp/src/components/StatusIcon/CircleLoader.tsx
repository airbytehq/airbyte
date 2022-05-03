import styled, { keyframes } from "styled-components";

const spinAnimation = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const SpinnerSVG = styled.svg`
  animation: ${spinAnimation} 1000ms linear infinite normal forwards;
`;

interface Props {
  title?: string;
}

const CircleLoader = ({ title }: Props): JSX.Element => (
  <SpinnerSVG
    viewBox="0 0 16 16"
    width="18"
    height="18"
    shape-rendering="geometricPrecision"
    text-rendering="geometricPrecision"
    role="img"
    data-icon="circle-loader"
  >
    <defs>
      <linearGradient
        id="eDwmAshgIQE3-fill"
        x1="4.25"
        y1="0.5"
        x2="4.25"
        y2="15.5"
        spreadMethod="pad"
        gradientUnits="userSpaceOnUse"
        gradientTransform="translate(0 0)"
      >
        <stop id="eDwmAshgIQE3-fill-0" offset="17.9167%" stopColor="#d1d1db" />
        <stop id="eDwmAshgIQE3-fill-1" offset="100%" stopColor="rgba(209,209,219,0)" />
      </linearGradient>
    </defs>
    {title && <title>{title}</title>}
    <g>
      <g>
        <path
          d="M8,0.5C3.85775,0.5,0.5,3.85775,0.5,8s3.35775,7.5,7.5,7.5v-2c-3.03768,0-5.5-2.4623-5.5-5.5s2.46232-5.5,5.5-5.5v-2Z"
          clipRule="evenodd"
          fill="url(#eDwmAshgIQE3-fill)"
          fillRule="evenodd"
        />
        <path
          d="M8,15.5c4.1423,0,7.5-3.3577,7.5-7.5s-3.3577-7.5-7.5-7.5v2c3.0377,0,5.5,2.46232,5.5,5.5s-2.4623,5.5-5.5,5.5v2Z"
          clipRule="evenodd"
          fill="#d1d1db"
          fillRule="evenodd"
        />
      </g>
    </g>
  </SpinnerSVG>
);

export default CircleLoader;
