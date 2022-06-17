import React from "react";
import styled from "styled-components";

import Step from "./components/Step";

export interface StepMenuItem {
  id: string;
  name: string | React.ReactNode;
  status?: string;
  isPartialSuccess?: boolean;
  onSelect?: () => void;
}

interface IProps {
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

const StepsMenu: React.FC<IProps> = ({ data, onSelect, activeStep, lightMode }) => {
  return (
    <Content>
      {data.map((item, key) => (
        <Step
          status={item.status}
          isPartialSuccess={item.isPartialSuccess}
          lightMode={lightMode}
          key={item.id}
          num={key + 1}
          {...item}
          onClick={item.onSelect || onSelect}
          isActive={activeStep === item.id}
        />
      ))}
    </Content>
  );
};

export default StepsMenu;
