interface Props {
  width?: number;
  height?: number;
}

export const WaitingIcon = ({ width = 24, height = 24 }: Props) => (
  <svg width={`${width}`} height={`${height}`} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="10" fill="#AAAAAA" />
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M13.38 10.744V11.3182H16.4972V10.4829H14.7L16.5047 8.07422V7.5H13.3875V8.33523H15.1847L13.38 10.744ZM9.75 10.5C9.75 12.9853 11.7647 15 14.25 15C14.6855 15 15.1065 14.9381 15.5048 14.8227C14.6799 15.8456 13.4164 16.5 12 16.5C9.51472 16.5 7.5 14.4853 7.5 12C7.5 9.95018 8.87052 8.22048 10.7452 7.67725C10.1227 8.44921 9.75 9.43107 9.75 10.5Z"
      fill="white"
    />
  </svg>
);
