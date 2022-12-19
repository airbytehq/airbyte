import React from "react";
import styled from "styled-components";

import { RightArrowHeadIcon } from "components/icons/RightArrowHeadIcon";

interface IProps {
  steps: string[];
  currentStep: string;
}

const Navbar = styled.nav`
  width: 100%;
  height: 100px;
  background-color: ${({ theme }) => theme.white};
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

const StepsContent = styled.div`
  display: flex;
  flex-direction: row;
  align-items: center;
`;

const Step = styled.div<{ isActive?: boolean }>`
  font-weight: 400;
  font-size: 14px;
  color: ${({ theme, isActive }) => (isActive ? theme.primaryColor : "#6B6B6F")};
`;

const ArrowIconContainer = styled.div`
  margin: 3px 60px 0 60px;
`;

const PaymentNav: React.FC<IProps> = ({ steps, currentStep }) => {
  return (
    <Navbar>
      <StepsContent>
        {steps.map((step, index) => (
          <>
            <Step isActive={step === currentStep}>{step}</Step>
            {!(index + 1 >= steps.length) && (
              <ArrowIconContainer>
                <RightArrowHeadIcon />
              </ArrowIconContainer>
            )}
          </>
        ))}
      </StepsContent>
    </Navbar>
  );
};

export default PaymentNav;
