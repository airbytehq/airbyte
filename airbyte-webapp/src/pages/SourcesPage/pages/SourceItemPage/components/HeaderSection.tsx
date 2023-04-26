import React from "react";
import styled from "styled-components";

import { DefinitioDetails } from "components/ConnectorBlocks";
import { TabMenu, CategoryItem } from "components/TabMenu";

import { SourceDefinitionRead } from "core/request/AirbyteClient";

const TabContainer = styled.div`
  margin: 20px 20px 40px 0;
`;

interface Iprops {
  data: CategoryItem[];
  sourceDefinition: SourceDefinitionRead;
  onSelect: (newPath: string) => void;
  activeItem: string;
}

const HeaderSection: React.FC<Iprops> = ({ data, sourceDefinition, onSelect, activeItem }) => {
  return (
    <>
      <DefinitioDetails name={sourceDefinition.name} icon={sourceDefinition.icon} type="source" />
      <TabContainer>
        <TabMenu data={data} onSelect={onSelect} activeItem={activeItem} size="16" lastOne />
      </TabContainer>
    </>
  );
};

export default HeaderSection;
