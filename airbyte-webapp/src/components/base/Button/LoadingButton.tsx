import { faCircleNotch } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import React from "react";
import styled, { keyframes } from "styled-components";

import Button from "./Button";
import { ButtonProps } from "./types";

export const SpinAnimation = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const SymbolSpinner = styled(FontAwesomeIcon)<ButtonProps>`
  display: inline-block;
  font-size: 18px;
  position: absolute;
  left: 50%;
  animation: ${SpinAnimation} 1.5s linear 0s infinite;
  color: ${({ theme }) => theme.primaryColor};
  margin: -1px 0 -3px -9px;
`;

const ButtonView = styled(Button)<ButtonProps>`
  pointer-events: none;
  background: ${({ theme }) => theme.primaryColor25};
  border-color: transparent;
  position: relative;
`;

const Invisible = styled.div`
  color: rgba(255, 255, 255, 0);
`;

const LoadingButton: React.FC<ButtonProps> = (props) => {
  if (props.isLoading) {
    return (
      <ButtonView {...props}>
        {props.isLoading ? (
          <>
            <SymbolSpinner icon={faCircleNotch} />
            <Invisible>{props.children}</Invisible>
          </>
        ) : (
          props.children
        )}
      </ButtonView>
    );
  }

  return <Button {...props} />;
};

export default LoadingButton;
