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
  @media (max-width: 768px) {
    font-size: 14px;
    flex-direction: column;
  }
  @media (max-width: 568px) {
    font-size: 12px;
  }
  @media (max-width: 468px) {
    font-size: 10px;
  }
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
  margin-right: 12px;
  @media (max-width: 768px) {
    width: 22px;
    height: 22px;
    font-size: 11px;
    border: 1px solid ${({ theme, isActive }) => (isActive ? theme.primaryColor : " #d1d5db")};
  }
`;

export const StepLine = styled.div<{
  isActive?: boolean;
}>`
  width: 160px;
  border: 1px solid ${({ theme, isActive }) => (isActive ? theme.primaryColor : " #d1d5db")};
  margin: 0 30px;
  @media (max-width: 1100px) {
    width: 80px;
    margin: 0 10px;
  }
  @media (max-width: 900px) {
    width: 60px;
    margin: 0 5px;
  }

  @media (max-width: 830px) {
    width: 2px;
    height: 40px;
    margin: 3px;
  }
  @media (max-width: 768px) {
    margin-right: 10px;
    margin-left: 10px;
  }
  @media (max-width: 600px) {
    margin-left: 5px;
  }
`;

const Image = styled.img`
  width: 34px;
  height: 34px;
  display: inline-block;
  margin-right: 12px;
  @media (max-width: 768px) {
    width: 22px;
    height: 22px;
  }
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
