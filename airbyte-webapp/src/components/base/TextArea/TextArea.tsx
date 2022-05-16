import React from "react";
import styled from "styled-components";

type TextAreaProps = {
  error?: boolean;
  light?: boolean;
} & React.TextareaHTMLAttributes<HTMLTextAreaElement>;

const TextArea = styled.textarea<TextAreaProps>`
  outline: none;
  resize: none;
  width: 100%;
  padding: 7px 8px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 20px;
  font-weight: normal;
  border: 1px solid ${(props) => (props.error ? props.theme.dangerColor : props.theme.greyColor0)};
  background: ${({ theme }) => theme.greyColor0};
  color: ${({ theme }) => theme.textColor};
  caret-color: ${({ theme }) => theme.primaryColor};

  &::placeholder {
    color: ${({ theme }) => theme.greyColor40};
  }

  &:hover {
    background: ${({ theme, light }) => (light ? theme.whiteColor : theme.greyColor20)};
    border-color: ${(props) => (props.error ? props.theme.dangerColor : props.theme.greyColor20)};
  }

  &:focus {
    background: ${({ theme, light }) => (light ? theme.whiteColor : theme.primaryColor12)};
    border-color: ${({ theme }) => theme.primaryColor};
  }

  &:disabled {
    pointer-events: none;
    color: ${({ theme }) => theme.greyColor55};
  }
`;

export { TextArea };
export type { TextAreaProps };
