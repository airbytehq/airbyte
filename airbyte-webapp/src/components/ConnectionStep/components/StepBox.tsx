import React from "react";
import styled from "styled-components";

interface StepProps {
  id: string;
  lightMode?: boolean;
  name: string | React.ReactNode;
  onClick?: (id: string) => void;
  isActive?: boolean;
  isPartialSuccess?: boolean;
  stepNumber: number;
  status?: string;
  currentStepNumber: number;
}

export const StepBlock = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
`;

export const StepContent = styled.div<{
  isActive?: boolean;
  lightMode?: boolean;
  nonClickable?: boolean;
}>`
  display: flex;
  justify-content: center;
  align-items: center;
  color: ${({ theme, isActive }) => (isActive ? theme.primaryColor : theme.greyColor60)};
  cursor: ${({ nonClickable }) => (nonClickable ? "default" : "pointer")};
`;

export const CircleNumber = styled.div<{
  isActive?: boolean;
}>`
  display: flex;
  justify-content: center;
  align-items: center;
  width: 34px;
  height: 34px;
  border: 2px solid ${({ theme, isActive }) => (isActive ? theme.primaryColor : " #d1d5db")};
  border-radius: 20px;
  margin-right: 16px;
`;

export const StepLine = styled.div<{
  isActive?: boolean;
}>`
  width: 110px;
  border: 1px solid ${({ theme, isActive }) => (isActive ? theme.primaryColor : " #d1d5db")};
  margin: 0 30px;
`;

const Image = styled.img`
  width: 36px;
  height: 36px;
  display: inline-block;
  margin-right: 16px;
`;

const StepBox: React.FC<StepProps> = ({ name, id, isActive, onClick, stepNumber, lightMode, currentStepNumber }) => {
  const onItemClickItem = () => {
    if (onClick) {
      onClick(id);
    }
  };

  stepNumber++;
  return (
    <StepBlock>
      {stepNumber > 1 ? <StepLine isActive={isActive} /> : null}
      <StepContent
        data-id={`${id.toLowerCase()}-step`}
        nonClickable={!onClick}
        onClick={onItemClickItem}
        isActive={isActive}
        lightMode={lightMode}
      >
        {currentStepNumber > stepNumber ? (
          <Image src="/icons/step-success.png" alt="success-icon" />
        ) : (
          <CircleNumber isActive={isActive}>{stepNumber > 9 ? stepNumber : `0${stepNumber}`}</CircleNumber>
        )}
        {name}
      </StepContent>
    </StepBlock>
  );
};

export default StepBox;
