import React from "react";
import styled from "styled-components";

import { StepsMenu } from "components/ui/StepsMenu";

export interface TabsData {
  id: string;
  name: string | React.ReactNode;
  icon?: React.ReactNode;
  onSelect?: () => void;
}

interface TabsProps {
  isFailed?: boolean;
  activeStep?: string;
  onSelect?: (id: string) => void;
  data: TabsData[];
}

const TabsContent = styled.div<{ isFailed?: boolean }>`
  padding: 6px 0;
  border-bottom: 1px solid ${({ theme, isFailed }) => (isFailed ? theme.dangerTransparentColor : theme.greyColor20)};
`;

const Tabs: React.FC<TabsProps> = ({ isFailed, activeStep, onSelect, data }) => {
  return (
    <TabsContent isFailed={isFailed}>
      <StepsMenu lightMode activeStep={activeStep} onSelect={onSelect} data={data} />
    </TabsContent>
  );
};

export default Tabs;
