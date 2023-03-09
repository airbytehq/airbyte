import { theme } from "theme";

interface ModificationIconProps {
  color?: string;
}

export const ModificationIcon: React.FC<ModificationIconProps> = ({ color = theme.blue100 }) => {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M10.8332 9.16663L14.1665 6.66663L10.8332 4.16663V5.83329H4.1665V7.49996H10.8332V9.16663Z"
        fill={color}
      />
      <path
        fillRule="evenodd"
        clipRule="evenodd"
        d="M9.16683 15.8334L5.8335 13.3334L9.16683 10.8334V12.5H15.8335V14.1667H9.16683V15.8334Z"
        fill={color}
      />
    </svg>
  );
};
