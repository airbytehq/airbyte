import React from "react";
import styled from "styled-components";

import { ButtonProps } from "components/ui/Button";

const StyledButton = styled.button<ButtonProps>`
  align-items: center;
  background: #4285f4;
  border: 0 solid #4285f4;
  color: #ffffff;
  cursor: pointer;
  display: flex;
  font-family: Roboto, sans-serif;
  font-weight: 500;
  font-size: 14px;
  font-style: normal;
  line-height: 15px;
  outline: none;
  padding: 0 10px 0 0;
  pointer-events: ${(props) => (props.wasActive && !props.clickable ? "none" : "all")};
  text-align: center;
  text-decoration: none;
  width: ${(props) => (props.full ? "100%" : "auto")};

  &:disabled {
    opacity: 0.3;
    background: transparent;
    border: none;
    color: #ffffff;
    pointer-events: none;
  }

  &:hover {
    box-shadow: 0 1px 3px rgba(53, 53, 66, 0.2), 0 1px 2px rgba(53, 53, 66, 0.12), 0 1px 1px rgba(53, 53, 66, 0.14);
  }
`;

const Img = styled.img`
  display: inline-block;
  padding-right: 10px;
  height: 40px;
`;

const GoogleAuthButton: React.FC<React.PropsWithChildren<unknown>> = (props) => (
  <StyledButton {...props}>
    <Img src="/connectors/google/btn_google_light_normal_ios.svg" alt="Sign in with Google" />
    {props.children}
  </StyledButton>
);

export default GoogleAuthButton;
