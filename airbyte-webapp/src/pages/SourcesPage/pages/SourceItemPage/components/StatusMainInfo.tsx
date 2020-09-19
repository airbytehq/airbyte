import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";
import { useResource } from "rest-hooks";

import ContentCard from "../../../../../components/ContentCard";
import ImageBlock from "../../../../../components/ImageBlock";
import {
  Header,
  Row,
  Cell
} from "../../../../../components/SimpleTableComponents";
import FrequencyConfig from "../../../../../data/FrequencyConfig.json";
import Toggle from "../../../../../components/Toggle";
import DestinationImplementationResource from "../../../../../core/resources/DestinationImplementation";
import config from "../../../../../config";
import DestinationResource from "../../../../../core/resources/Destination";
import { Connection } from "../../../../../core/resources/Connection";

type IProps = {
  sourceData: Connection;
  onEnabledChange: () => void;
};

const MainInfo = styled(ContentCard)`
  margin-bottom: 14px;
  padding: 23px 20px 20px 23px;
`;

const Img = styled(ImageBlock)`
  display: inline-block;
  margin-right: 6px;
`;

const SourceCell = styled(Cell)`
  display: flex;
  align-items: center;
`;

const EnabledCell = styled(Cell)`
  display: flex;
  align-items: center;
  margin-top: -18px;
`;

const ToggleLabel = styled.label`
  text-transform: uppercase;
  font-size: 14px;
  line-height: 19px;
  color: ${({ theme }) => theme.greyColor40};
  display: inline-block;
  min-width: 75px;
  text-align: left;
  cursor: pointer;
`;

const StatusMainInfo: React.FC<IProps> = ({ sourceData, onEnabledChange }) => {
  const { destinations } = useResource(
    DestinationImplementationResource.listShape(),
    {
      workspaceId: config.ui.workspaceId
    }
  );
  const currentDestination = destinations[0]; // Now we have only one destination. If we support multiple destinations we will fix this line
  const destination = useResource(DestinationResource.detailShape(), {
    destinationId: currentDestination.destinationId
  });

  const cellText = FrequencyConfig.find(
    item => JSON.stringify(item.config) === JSON.stringify(sourceData.schedule)
  );

  return (
    <MainInfo>
      <Header>
        <Cell flex={2}>
          <FormattedMessage id="sources.source" />
        </Cell>
        <Cell flex={2}>
          <FormattedMessage id="sidebar.destination" />
        </Cell>
        <Cell>
          <FormattedMessage id="sources.frequency" />
        </Cell>
        <Cell flex={1.1}></Cell>
      </Header>
      <Row>
        <SourceCell flex={2}>
          <Img />
          {sourceData.source?.sourceName}
        </SourceCell>
        <SourceCell flex={2}>
          <Img />
          {destination.name}
        </SourceCell>
        <Cell>{cellText?.text}</Cell>
        <EnabledCell flex={1.1}>
          <ToggleLabel htmlFor="toggle-enabled-source">
            <FormattedMessage
              id={
                sourceData.status === "active"
                  ? "sources.enabled"
                  : "sources.disabled"
              }
            />
          </ToggleLabel>
          <Toggle
            onChange={onEnabledChange}
            checked={sourceData.status === "active"}
            id="toggle-enabled-source"
          />
        </EnabledCell>
      </Row>
    </MainInfo>
  );
};

export default StatusMainInfo;
