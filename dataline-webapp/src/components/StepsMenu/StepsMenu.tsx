import React from "react";
import styled from "styled-components";

import Step from "./components/Step";

type IProps = {
  lightMode?: boolean;
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

const StepsMenu: React.FC<IProps> = ({
  data,
  onSelect,
  activeStep,
  lightMode
}) => {
  return (
    <Content>
      {data.map((item, key) => (
        <Step
          lightMode={lightMode}
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
