import React from "react";
import { FormattedMessage } from "react-intl";
import styled, { keyframes } from "styled-components";

interface ProgressBarProps {
  runTime?: number;
  text?: React.ReactNode;
}

export const GrowAnimation = keyframes`
  0% {
    width: 0;
  }
  20% {
    width: 65%;
  }
  50% {
    width: 80%;
  }
  80% {
    width: 95%;
  }
  100% {
    width: 100%;
  }
`;
export const fadeInAnimation = keyframes`
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
`;

const Bar = styled.div`
  width: 100%;
  max-width: 370px;
  height: 19px;
  border: 1px solid ${({ theme }) => theme.greyColor20};
  border-radius: 4px;
  overflow: hidden;
  position: relative;
  display: inline-block;
`;

const Progress = styled.div<{ runTime: number }>`
  width: 100%;
  height: 100%;
  background: ${({ theme }) => theme.primaryColor25};
  animation: ${GrowAnimation} ${({ runTime }) => runTime}s linear 0s;
`;

const Text = styled.div<{ delay: number }>`
  text-align: center;
  position: absolute;
  width: 100%;
  top: 0;
  left: 0;
  color: ${({ theme }) => theme.whiteColor};
  font-size: 12px;
  font-weight: bold;
  animation: ${fadeInAnimation} 1s linear ${({ delay }) => delay + 0.5}s forwards;
  opacity: 0;
`;

export const ProgressBar: React.FC<ProgressBarProps> = ({ runTime, text }) => {
  const animationRunTime = runTime || 20;
  return (
    <Bar>
      <Progress runTime={animationRunTime} />
      <Text delay={animationRunTime}>{text || <FormattedMessage id="form.wait" />}</Text>
    </Bar>
  );
};
