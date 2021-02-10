import React from "react";
import styled, { keyframes } from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faCircleNotch } from "@fortawesome/free-solid-svg-icons";

import { IProps } from "./types";
import Button from "./Button";

export const SpinAnimation = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const SymbolSpinner = styled(FontAwesomeIcon)<IProps>`
  display: inline-block;
  font-size: 18px;
  position: relative;
  animation: ${SpinAnimation} 1.5s linear 0s infinite;
  color: ${({ theme }) => theme.primaryColor};
  margin: -1px 0 -3px;
`;

const ButtonView = styled(Button)<IProps>`
  pointer-events: none;
  background: ${({ theme }) => theme.primaryColor25};
  border-color: transparent;
`;

const LoadingButton: React.FC<IProps> = props => {
  if (props.isLoading) {
    return (
      <ButtonView {...props}>
        {props.isLoading ? (
          <SymbolSpinner icon={faCircleNotch} />
        ) : (
          props.children
        )}{" "}
      </ButtonView>
    );
  }

  return <Button {...props} />;
};

export default LoadingButton;
