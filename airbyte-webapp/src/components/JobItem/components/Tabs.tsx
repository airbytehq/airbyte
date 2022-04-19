import React from "react";
import styled from "styled-components";

import { StepsMenu } from "components/StepsMenu";

type IProps = {
  isFailed?: boolean;
  activeStep?: string;
  onSelect?: (id: string) => void;
  data: {
    id: string;
    name: string | React.ReactNode;
    status?: string;
    onSelect?: () => void;
  }[];
};

const TabsContent = styled.div<{ isFailed?: boolean }>`
  padding: 6px 0;
  border-bottom: 1px solid
    ${({ theme, isFailed }) =>
      isFailed ? theme.dangerTransparentColor : theme.greyColor20};
`;

const Tabs: React.FC<IProps> = ({ isFailed, activeStep, onSelect, data }) => {
  return (
    <TabsContent isFailed={isFailed}>
      <StepsMenu
        lightMode
        activeStep={activeStep}
        onSelect={onSelect}
        data={data}
      />
    </TabsContent>
  );
};

export default Tabs;
