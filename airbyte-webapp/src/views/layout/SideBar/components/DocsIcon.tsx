const DocsIcon = ({
  color = "currentColor",
}: {
  color?: string;
}): JSX.Element => (
  <svg
    width="30"
    height="24"
    viewBox="0 0 30 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      d="M24 18H9C8.73478 18 8.48043 18.1054 8.29289 18.2929C8.10536 18.4804 8 18.7348 8 19C8 19.2652 8.10536 19.5196 8.29289 19.7071C8.48043 19.8946 8.73478 20 9 20H24V22H9C8.20435 22 7.44129 21.6839 6.87868 21.1213C6.31607 20.5587 6 19.7956 6 19V4C6 3.46957 6.21071 2.96086 6.58579 2.58579C6.96086 2.21071 7.46957 2 8 2H24V18ZM8 16.05C8.162 16.017 8.329 16 8.5 16H22V4H8V16.05ZM19 9H11V7H19V9Z"
      fill={color}
    />
  </svg>
);

export default DocsIcon;
