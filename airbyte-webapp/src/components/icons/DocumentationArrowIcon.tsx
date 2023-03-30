interface IProps {
  color?: string;
  width?: number;
  height?: number;
}

export const DocumentationArrowIcon = ({ color = "currentColor", width = 14, height = 14 }: IProps) => {
  return (
    <svg width={width} height={height} viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M1 7V1.85714C1 1.38376 1.38376 1 1.85714 1H12.1429C12.6163 1 13 1.38376 13 1.85714V12.1429C13 12.6163 12.6163 13 12.1429 13H7M3.66667 7H7M7 7V10.3333M7 7L1 13"
        stroke={color}
        stroke-width="1.2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  );
};
