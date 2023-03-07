import styles from "./AirbyteIllustration.module.scss";

export type HighlightIndex = 0 | 1 | 2 | 3;

interface AirbyteIllustrationProps {
  sourceHighlighted: HighlightIndex;
  destinationHighlighted: HighlightIndex;
}

const regularPath = {
  stroke: styles.darkBlue,
  strokeWidth: 1.5,
  strokeDasharray: "3 6",
  opacity: 0.2,
};

const highlightedSource = {
  stroke: "url(#highlightedSource)",
  strokeWidth: 5,
};

const highlightedDestination = {
  stroke: "url(#highlightedDestination)",
  strokeWidth: 5,
};

export const AirbyteIllustration: React.FC<AirbyteIllustrationProps> = ({
  sourceHighlighted,
  destinationHighlighted,
}) => (
  <svg width="492" height="318" viewBox="0 0 492 318" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      id="sourcePath0"
      d="M0 25H16.3176C38.7973 25 58.5134 40.0021 64.5074 61.668L80.4605 119.332C86.4545 140.998 106.171 156 128.65 156H179"
      strokeLinejoin="round"
      {...(sourceHighlighted === 0 ? highlightedSource : regularPath)}
    />
    <path
      id="sourcePath1"
      d="M0 115H31.8265C46.1566 115 59.798 121.149 69.2887 131.885L75.6792 139.115C85.1699 149.851 98.8113 156 113.141 156H179"
      strokeLinejoin="round"
      {...(sourceHighlighted === 1 ? highlightedSource : regularPath)}
    />
    <path
      id="sourcePath2"
      d="M0 202H30.1023C45.422 202 59.8962 194.977 69.3771 182.943L75.5908 175.057C85.0717 163.023 99.5459 156 114.866 156H179"
      strokeLinejoin="round"
      {...(sourceHighlighted === 2 ? highlightedSource : regularPath)}
    />
    <path
      id="sourcePath3"
      d="M0 288H16.2406C38.7565 288 58.495 272.95 64.4563 251.238L80.5116 192.762C86.4729 171.049 106.211 156 128.727 156H179"
      strokeLinejoin="round"
      {...(sourceHighlighted === 3 ? highlightedSource : regularPath)}
    />
    {/* We need to render the highlighted element once more, so it will overlap the other dashed lines (since there's no z-index in SVG) */}
    <use xlinkHref={`#sourcePath${sourceHighlighted}`} />

    <path
      id="destinationPath0"
      d="M492 25H475.682C453.203 25 433.487 40.0021 427.493 61.668L411.539 119.332C405.545 140.998 385.829 156 363.35 156H313"
      strokeLinejoin="round"
      {...(destinationHighlighted === 0 ? highlightedDestination : regularPath)}
    />
    <path
      id="destinationPath1"
      d="M492 115H460.173C445.843 115 432.202 121.149 422.711 131.885L416.321 139.115C406.83 149.851 393.189 156 378.859 156H313"
      {...(destinationHighlighted === 1 ? highlightedDestination : regularPath)}
      strokeLinejoin="round"
    />
    <path
      id="destinationPath2"
      d="M492 202H461.898C446.578 202 432.104 194.977 422.623 182.943L416.409 175.057C406.928 163.023 392.454 156 377.134 156H313"
      strokeLinejoin="round"
      {...(destinationHighlighted === 2 ? highlightedDestination : regularPath)}
    />
    <path
      id="destinationPath3"
      d="M492 288H475.759C453.243 288 433.505 272.95 427.544 251.238L411.488 192.762C405.527 171.049 385.789 156 363.273 156H313"
      strokeLinejoin="round"
      {...(destinationHighlighted === 3 ? highlightedDestination : regularPath)}
    />
    {/* We need to render the highlighted element once more, so it will overlap the other dashed lines (since there's no z-index in SVG) */}
    <use xlinkHref={`#destinationPath${destinationHighlighted}`} />

    <circle cx="0" cy="0" r="6" fill={styles.dotColor} stroke="white" strokeWidth={2}>
      <animateMotion dur="3s" repeatCount="indefinite" rotate="auto">
        {/* Animate the dot along the current highlighted source path */}
        <mpath xlinkHref={`#sourcePath${sourceHighlighted}`} />
      </animateMotion>
    </circle>
    <circle cx="0" cy="0" r="6" fill={styles.dotColor} stroke="white" strokeWidth={2}>
      <animateMotion dur="3s" repeatCount="indefinite" rotate="auto" keyPoints="1;0" keyTimes="0;1" calcMode="linear">
        <mpath xlinkHref={`#destinationPath${destinationHighlighted}`} />
      </animateMotion>
    </circle>
    <g filter="url(#backgroundGradient)">
      <rect x="179" y="88" width="134" height="134" rx="48" fill="white" />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M235.109 128.384C242.704 119.85 255.281 117.347 265.621 122.273C279.359 128.818 284.371 145.49 276.891 158.351L260.065 187.25C259.125 188.865 257.577 190.043 255.763 190.526C253.948 191.009 252.015 190.757 250.387 189.826L270.759 154.831C276.185 145.497 272.556 133.398 262.595 128.635C255.122 125.061 245.986 126.846 240.465 132.993C237.42 136.367 235.71 140.724 235.653 145.255C235.596 149.785 237.196 154.183 240.155 157.632C240.687 158.251 241.259 158.834 241.869 159.378L229.976 179.845C229.511 180.645 228.892 181.346 228.154 181.908C227.416 182.471 226.574 182.883 225.675 183.123C224.776 183.362 223.839 183.423 222.917 183.302C221.995 183.182 221.105 182.882 220.3 182.42L233.21 160.201C231.356 157.546 230.024 154.567 229.285 151.42L221.374 165.063C220.433 166.678 218.886 167.856 217.071 168.339C215.257 168.822 213.324 168.57 211.696 167.638L232.155 132.447C233.007 131.002 233.996 129.641 235.109 128.384ZM258.722 139.585C263.649 142.411 265.351 148.695 262.5 153.586L242.881 187.246C241.941 188.861 240.394 190.039 238.579 190.522C236.765 191.005 234.831 190.753 233.204 189.822L251.42 158.484C249.959 158.179 248.581 157.562 247.383 156.676C246.185 155.79 245.195 154.657 244.48 153.354C243.766 152.052 243.345 150.61 243.247 149.13C243.148 147.65 243.374 146.167 243.909 144.782C244.444 143.397 245.276 142.144 246.346 141.109C247.416 140.074 248.7 139.283 250.108 138.789C251.516 138.295 253.016 138.11 254.503 138.247C255.99 138.385 257.43 138.841 258.722 139.585ZM251.586 145.911C251.249 146.168 250.966 146.488 250.754 146.854H250.753C250.432 147.405 250.284 148.037 250.326 148.672C250.368 149.306 250.598 149.914 250.988 150.418C251.378 150.923 251.91 151.301 252.516 151.505C253.122 151.709 253.776 151.731 254.394 151.566C255.013 151.401 255.568 151.058 255.99 150.58C256.412 150.102 256.682 149.511 256.766 148.881C256.849 148.25 256.743 147.609 256.46 147.039C256.176 146.469 255.729 145.995 255.175 145.677C254.807 145.466 254.4 145.329 253.979 145.274C253.558 145.219 253.129 145.247 252.719 145.356C252.308 145.465 251.923 145.654 251.586 145.911Z"
        fill={styles.logoColor}
      />
    </g>
    <defs>
      <filter
        id="backgroundGradient"
        x="101"
        y="0"
        width="297"
        height="318"
        filterUnits="userSpaceOnUse"
        colorInterpolationFilters="sRGB"
      >
        <feFlood floodOpacity="0" result="BackgroundImageFix" />
        <feColorMatrix
          in="SourceAlpha"
          type="matrix"
          values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
          result="hardAlpha"
        />
        <feMorphology radius="10" operator="erode" in="SourceAlpha" result="effect1_dropShadow_3082_52204" />
        <feOffset dy="13" />
        <feGaussianBlur stdDeviation="9" />
        <feColorMatrix type="matrix" values="0 0 0 0 0.101961 0 0 0 0 0.0980392 0 0 0 0 0.301961 0 0 0 0.17 0" />
        <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_3082_52204" />
        <feColorMatrix
          in="SourceAlpha"
          type="matrix"
          values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
          result="hardAlpha"
        />
        <feOffset dx="23" dy="-27" />
        <feGaussianBlur stdDeviation="30.5" />
        <feComposite in2="hardAlpha" operator="out" />
        <feColorMatrix type="matrix" values="0 0 0 0 0.984314 0 0 0 0 0.223529 0 0 0 0 0.372549 0 0 0 0.2 0" />
        <feBlend mode="normal" in2="effect1_dropShadow_3082_52204" result="effect2_dropShadow_3082_52204" />
        <feColorMatrix
          in="SourceAlpha"
          type="matrix"
          values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
          result="hardAlpha"
        />
        <feOffset dx="-20" dy="2" />
        <feGaussianBlur stdDeviation="29" />
        <feComposite in2="hardAlpha" operator="out" />
        <feColorMatrix type="matrix" values="0 0 0 0 0.262745 0 0 0 0 0.231373 0 0 0 0 0.984314 0 0 0 0.3 0" />
        <feBlend mode="normal" in2="effect2_dropShadow_3082_52204" result="effect3_dropShadow_3082_52204" />
        <feColorMatrix
          in="SourceAlpha"
          type="matrix"
          values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0"
          result="hardAlpha"
        />
        <feOffset dx="12" dy="23" />
        <feGaussianBlur stdDeviation="36.5" />
        <feComposite in2="hardAlpha" operator="out" />
        <feColorMatrix type="matrix" values="0 0 0 0 0.404861 0 0 0 0 0.854625 0 0 0 0 0.883333 0 0 0 0.41 0" />
        <feBlend mode="normal" in2="effect3_dropShadow_3082_52204" result="effect4_dropShadow_3082_52204" />
        <feBlend mode="normal" in="SourceGraphic" in2="effect4_dropShadow_3082_52204" result="shape" />
      </filter>
      <linearGradient id="highlightedSource" x1="490" y1="25" x2="5.00002" y2="115" gradientUnits="userSpaceOnUse">
        <stop stopColor={styles.gradientOrange} />
        <stop offset="1" stopColor={styles.gradientBlue} />
      </linearGradient>
      <linearGradient id="highlightedDestination" x1="492" y1="25" x2="-2" y2="115" gradientUnits="userSpaceOnUse">
        <stop stopColor={styles.gradientOrange} />
        <stop offset="1" stopColor={styles.gradientBlue} />
      </linearGradient>
    </defs>
  </svg>
);
