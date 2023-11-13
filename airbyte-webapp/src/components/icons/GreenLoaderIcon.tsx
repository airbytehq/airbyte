interface Props {
  width?: number;
  height?: number;
}

export const GreenLoaderIcon = ({ width = 24, height = 24 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="9.5" fill="white" stroke="#068C24" />
    <g clip-path="url(#clip0_4581_19375)">
      <path
        d="M12.275 6.2124V8.6374"
        stroke="#068C24"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M12.275 15.9126V18.3376"
        stroke="#068C24"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M7.98877 7.98877L9.70446 9.70446"
        stroke="#068C24"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M14.8455 14.8455L16.5611 16.5611"
        stroke="#068C24"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M6.21252 12.2749H8.63752"
        stroke="#068C24"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M15.9125 12.2749H18.3375"
        stroke="#068C24"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M7.98877 16.5611L9.70446 14.8455"
        stroke="#068C24"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M14.8455 9.70446L16.5611 7.98877"
        stroke="#068C24"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </g>
    <defs>
      <clipPath id="clip0_4581_19375">
        <rect width="14.55" height="14.55" fill="white" transform="translate(5 5)" />
      </clipPath>
    </defs>
  </svg>
);
