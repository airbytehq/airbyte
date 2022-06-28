import React from "react";
import styled from "styled-components";

import { StepType } from "../../types";
import StarsIcon from "./components/StarsIcon";
import StepItem from "./components/StepItem";

interface StepsCounterProps {
  steps: Array<{ id: StepType; name?: React.ReactNode }>;
  currentStep: StepType;
}

const Steps = styled.div`
  display: flex;
  flex-direction: row;
`;

const Content = styled.div`
  position: relative;
  display: flex;
  flex-direction: row;
`;

const Rocket = styled.img<{ stepNumber: number }>`
  position: absolute;
  width: 87px;
  transform: matrix(0.99, 0.12, -0.12, 0.99, 0, 0) rotate(6.73deg);
  top: 1px;
  left: ${({ stepNumber }) => -23 + stepNumber * 95.5}px;
  transition: 0.8s;
`;

const Stars = styled.div<{ isLastStep?: boolean }>`
  position: absolute;
  top: -23px;
  right: -35px;
  color: ${({ theme }) => theme.dangerColor};
  opacity: ${({ isLastStep }) => (isLastStep ? 1 : 0)};
  transition: 0.8s 0.2s;
`;

const StepsCounter: React.FC<StepsCounterProps> = ({ steps, currentStep }) => {
  const stepItem = steps.find((item) => item.id === currentStep);
  const stepIndex = stepItem ? steps.indexOf(stepItem) : 0;
  const isLastStep = currentStep === steps[steps.length - 1].id;

  return (
    <Content>
      <Steps>
        {steps.map((stepItem, key) => (
          <StepItem key={`step-${stepItem.id}-${key}`} active={stepIndex >= key} current={stepItem.id === currentStep}>
            {key === steps.length - 1 ? <StarsIcon /> : key}
          </StepItem>
        ))}
      </Steps>
      <Stars isLastStep={isLastStep}>
        <StarsIcon />
      </Stars>
      <Rocket src="/rocket.png" stepNumber={isLastStep ? steps.length : stepIndex} />
    </Content>
  );
};

export default StepsCounter;
