import React from "react";
import styled, { keyframes } from "styled-components";

export const RollAnimation = keyframes`
  0% {
    width: 0;
  }
  100% {
    width: 100%;
  }
`;

export const ExitRollAnimation = keyframes`
  0% {
    width: 100%;
    float: right;
  }
  100% {
    width: 0;
    float: right;
  }
`;

export const EnterAnimation = keyframes`
  0% {
    left: -78px;
  }
  100% {
    left: calc(50% - 39px);
  }
`;

export const ExitAnimation = keyframes`
  0% {
    left: calc(50% - 39px);
  }
  100% {
    left: calc(100% + 78px);
  }
`;

const Line = styled.div<{ $onRight?: boolean }>`
  position: absolute;
  width: calc(50% - 275px);
  top: 345px;
  left: ${({ $onRight }) => ($onRight ? "calc(50% + 275px)" : 0)};
`;
const Path = styled.div<{ exit?: boolean }>`
  width: 100%;
  height: 2px;
  background: ${({ theme }) => theme.primaryColor};
  animation: ${({ exit }) => (exit ? ExitRollAnimation : RollAnimation)} 0.6s linear ${({ exit }) => (exit ? 0.8 : 0)}s;
  animation-fill-mode: forwards;
`;
const Img = styled.img<{ exit?: boolean }>`
  position: absolute;
  top: -58px;
  left: -78px;
  animation: ${({ exit }) => (exit ? ExitAnimation : EnterAnimation)} 0.8s linear ${({ exit }) => (exit ? 0 : 0.6)}s;
  animation-fill-mode: both;
`;

interface LetterLineProps {
  onRight?: boolean;
  exit?: boolean;
}

const LetterLine: React.FC<LetterLineProps> = ({ onRight, exit }) => {
  return (
    <Line $onRight={onRight}>
      <Path exit={exit} />
      <Img src="/newsletter.png" alt="" width={78} height={68} exit={exit} />
    </Line>
  );
};

export default LetterLine;
