import React from "react";
import styled from "styled-components";

import { Step } from "./Step";

interface StepMenuItem {
  id: string;
  name: string | React.ReactNode;
  icon?: React.ReactNode;
  onSelect?: () => void;
}

interface StepMenuProps {
  lightMode?: boolean;
  data: StepMenuItem[];
  activeStep?: string;
  onSelect?: (id: string) => void;
}

const Content = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: center;
  font-family: ${({ theme }) => theme.regularFont};
`;

export const StepsMenu: React.FC<StepMenuProps> = ({ data, onSelect, activeStep, lightMode }) => {
  return (
    <Content>
      {data.map((item, key) => (
        <Step
          icon={item.icon}
          lightMode={lightMode}
          key={item.id}
          num={key + 1}
          name={item.name}
          id={item.id}
          onClick={item.onSelect || onSelect}
          isActive={activeStep === item.id}
        />
      ))}
    </Content>
  );
};
