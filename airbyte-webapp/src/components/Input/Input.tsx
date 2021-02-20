import React from "react";
import styled from "styled-components";

type IStyleProps = InputProps & { theme: any };

const getBackgroundColor = (props: IStyleProps) => {
  if (props.error) {
    return props.theme.greyColor10;
  } else if (props.light) {
    return props.theme.whiteColor;
  }

  return props.theme.greyColor0;
};

export type InputProps = {
  error?: boolean;
  light?: boolean;
} & React.InputHTMLAttributes<HTMLInputElement>;

const Input = styled.input<InputProps>`
  outline: none;
  width: 100%;
  padding: 7px 8px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 20px;
  font-weight: normal;
  border: 1px solid
    ${(props) =>
      props.error ? props.theme.dangerColor : props.theme.greyColor0};
  background: ${(props) => getBackgroundColor(props)};
  color: ${({ theme }) => theme.textColor};
  caret-color: ${({ theme }) => theme.primaryColor};

  &::placeholder {
    color: ${({ theme }) => theme.greyColor40};
  }

  &:hover {
    background: ${({ theme, light }) =>
      light ? theme.whiteColor : theme.greyColor20};
    border-color: ${(props) =>
      props.error ? props.theme.dangerColor : props.theme.greyColor20};
  }

  &:focus {
    background: ${({ theme, light }) =>
      light ? theme.whiteColor : theme.primaryColor12};
    border-color: ${({ theme }) => theme.primaryColor};
  }

  &:disabled {
    pointer-events: none;
    color: ${({ theme }) => theme.greyColor55};
  }
`;

// TODO: figure out problem with prettier
// export type { InputProps };
export default Input;
