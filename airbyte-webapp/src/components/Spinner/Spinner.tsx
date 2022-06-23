import React from "react";
import styled, { keyframes } from "styled-components";

interface IProps {
  backgroundColor?: string;
  small?: boolean;
}

export const SpinAnimation = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const SpinnerWheel = styled.div<{ small?: boolean }>`
  display: inline-block;
  height: ${({ small }) => (small ? 30 : 42)}px;
  width: ${({ small }) => (small ? 30 : 42)}px;
  border-radius: 50%;
  border: 4px solid ${({ theme }) => theme.primaryColor12};
  position: relative;
  animation: ${SpinAnimation} 1.5s linear 0s infinite;
`;

const BreakRec = styled.div<IProps>`
  width: 13px;
  height: 7px;
  background: ${({ theme, backgroundColor }) => (backgroundColor ? backgroundColor : theme.whiteColor)};
  top: -4px;
  position: relative;
  margin: 0 auto;
`;

const Spinner: React.FC<IProps> = ({ backgroundColor, small }) => (
  <SpinnerWheel small={small}>
    <BreakRec backgroundColor={backgroundColor} />
  </SpinnerWheel>
);

export default Spinner;
