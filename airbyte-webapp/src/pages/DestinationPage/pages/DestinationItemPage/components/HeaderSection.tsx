import React from "react";
import styled from "styled-components";

import { DefinitioDetails } from "components/ConnectorBlocks";
import { TabMenu, CategoryItem } from "components/TabMenu";

import { DestinationDefinitionRead } from "core/request/AirbyteClient";

const TabContainer = styled.div`
  margin: 20px 20px 40px 0;
`;

interface Iprops {
  data: CategoryItem[];
  destinationDefinition: DestinationDefinitionRead;
  onSelect: (newPath: string) => void;
  activeItem: string;
}

const HeaderSection: React.FC<Iprops> = ({ data, destinationDefinition, onSelect, activeItem }) => {
  return (
    <>
      <DefinitioDetails name={destinationDefinition.name} icon={destinationDefinition.icon} type="destination" />
      <TabContainer>
        <TabMenu data={data} onSelect={onSelect} activeItem={activeItem} size="16" lastOne />
      </TabContainer>
    </>
  );
};

export default HeaderSection;
