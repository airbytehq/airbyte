import React from "react";
import styled from "styled-components";

import { Button } from "components";

import { ButtonProps } from "./types";

export const ButtonRows = styled.div<{
  top?: string;
  bottom?: string;
  full?: boolean;
}>`
  display: flex;
  justify-content: space-around;
  align-items: center;
  width: ${({ full }) => (full ? "100%" : "50%")};
  margin-left: auto;
  margin-right: auto;
  margin-top: ${({ top }) => (top ? top : 100)}px;
  margin-bottom: ${({ bottom }) => (bottom ? bottom : 0)}px;
`;

const BtnText = styled.div`
  font-weight: 500;
  font-size: 16px;
  padding: 5px 3px;
  // color: #ffffff;
`;

const BtnInnerContainer = styled.div`
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 8px 4px;
  min-width: 150px;
  justify-content: center;
`;

// export const ButtonContainer = styled(Button)`
//   // box-sizing: border-box;
//   padding: 8px 16px;
//   // width: 264px;
//   height: 54px;
//   border: 1px solid #d1d5db;
//   border-radius: 6px;
//   display: inline-flex;
//   align-items: center;
//   justify-content: center;
//   font-weight: 500;
//   font-size: 16px;
// `;

export const BigButton: React.FC<ButtonProps> = (props) => {
  return (
    <Button {...props}>
      <BtnInnerContainer>
        <BtnText>{props.children}</BtnText>
      </BtnInnerContainer>
    </Button>
  );
};
