import { faEye, faEyeSlash } from "@fortawesome/free-regular-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React, { useState } from "react";
import styled from "styled-components";
import { Theme } from "theme";

import Button from "../Button";

type IStyleProps = InputProps & { theme: Theme };

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

const InputComponent = styled.input<InputProps>`
  outline: none;
  width: 100%;
  padding: 7px 18px 7px 8px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 20px;
  font-weight: normal;
  border: 1px solid ${(props) => (props.error ? props.theme.dangerColor : props.theme.greyColor0)};
  background: ${(props) => getBackgroundColor(props)};
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

const Container = styled.div`
  width: 100%;
  position: relative;
`;

const VisibilityButton = styled(Button)`
  position: absolute;
  right: 2px;
  top: 7px;
`;

const Input: React.FC<InputProps> = (props) => {
  const [isContentVisible, setIsContentVisible] = useState(false);

  if (props.type === "password") {
    return (
      <Container>
        <InputComponent {...props} type={isContentVisible ? "text" : "password"} />
        {props.disabled ? null : (
          <VisibilityButton iconOnly onClick={() => setIsContentVisible(!isContentVisible)} type="button">
            <FontAwesomeIcon icon={isContentVisible ? faEyeSlash : faEye} />
          </VisibilityButton>
        )}
      </Container>
    );
  }

  return <InputComponent {...props} />;
};

export default Input;
export { Input };
