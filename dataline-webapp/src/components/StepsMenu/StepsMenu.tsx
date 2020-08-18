import React from "react";
import styled from "styled-components";

import Step from "./components/Step";

type IProps = {
  data: Array<{
    id: string;
    name: string | React.ReactNode;
  }>;
  activeStep?: string;
  onSelect: (id: string) => void;
};

const Content = styled.div`
  display: flex;
  flex-direction: row;
  justify-content: center;
`;

const StepsMenu: React.FC<IProps> = ({ data, onSelect, activeStep }) => {
  return (
    <Content>
      {data.map((item, key) => (
        <Step
          key={item.id}
          num={key + 1}
          {...item}
          onClick={onSelect}
          isActive={activeStep === item.id}
        />
      ))}
    </Content>
  );
};

export default StepsMenu;
