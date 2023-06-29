import React from "react";
import styled from "styled-components";

import { Button } from "components";

import { ButtonProps } from "./types";

interface ButtonRowsProps {
  top?: string;
  bottom?: string;
  width?: string;
  position?: "fixed" | "absolute" | "static";
  background?: string;
}

export const ButtonRows = styled.div<ButtonRowsProps>`
  display: flex;
  justify-content: center;
  align-items: center;
  width: ${({ width }) => (width ? width : "100%")};
  margin-left: auto;
  margin-right: auto;
  margin-top: ${({ top }) => (top ? top : 100)}px;
  margin-bottom: ${({ bottom }) => (bottom ? bottom : 0)}px;
  padding: 15px 0;
  background: ${({ background, theme }) => background || theme.white};
  position: ${({ position }) => position || "static"};
  bottom: 0;
  z-index: 1;
  gap: 120px;
`;

export const BtnText = styled.div`
  font-weight: 500;
  font-size: 16px;
  padding: 5px 3px;
`;

export const BtnInnerContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  min-width: 150px;
`;

export const BigButton: React.FC<ButtonProps> = (props) => {
  return (
    <Button {...props}>
      <BtnInnerContainer>
        <BtnText>{props.children}</BtnText>
      </BtnInnerContainer>
    </Button>
  );
};
