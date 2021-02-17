import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "../../../../../components/ContentCard";
import ImageBlock from "../../../../../components/ImageBlock";
import {
  Header,
  Row,
  Cell
} from "../../../../../components/SimpleTableComponents";
import Toggle from "../../../../../components/Toggle";
import { Connection } from "../../../../../core/resources/Connection";
import { AnalyticsService } from "../../../../../core/analytics/AnalyticsService";
import config from "../../../../../config";
import useConnection from "../../../../../components/hooks/services/useConnectionHook";

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

type IProps = {
  connection: Connection;
  frequencyText?: string;
};

const StatusMainInfo: React.FC<IProps> = ({ connection, frequencyText }) => {
  const { updateConnection } = useConnection();

  const onChangeStatus = async () => {
    await updateConnection({
      connectionId: connection.connectionId,
      syncCatalog: connection.syncCatalog,
      schedule: connection.schedule,
      status: connection.status === "active" ? "inactive" : "active"
    });

    AnalyticsService.track("Source - Action", {
      user_id: config.ui.workspaceId,
      action:
        connection.status === "active"
          ? "Disable connection"
          : "Reenable connection",
      connector_source: connection.source?.sourceName,
      connector_source_id: connection.source?.sourceDefinitionId,
      connector_destination: connection.destination?.name,
      connector_destination_definition_id:
        connection.destination?.destinationDefinitionId,
      frequency: frequencyText
    });
  };

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
          <FormattedMessage id="tables.frequency" />
        </Cell>
        <Cell flex={1.1}></Cell>
      </Header>
      <Row>
        <SourceCell flex={2}>
          <Img />
          {connection.source?.sourceName}
        </SourceCell>
        <SourceCell flex={2}>
          <Img />
          {connection.destination?.destinationName}
        </SourceCell>
        <Cell>{frequencyText}</Cell>
        <EnabledCell flex={1.1}>
          <ToggleLabel htmlFor="toggle-enabled-source">
            <FormattedMessage
              id={
                connection.status === "active"
                  ? "tables.enabled"
                  : "tables.disabled"
              }
            />
          </ToggleLabel>
          <Toggle
            onChange={onChangeStatus}
            checked={connection.status === "active"}
            id="toggle-enabled-source"
          />
        </EnabledCell>
      </Row>
    </MainInfo>
  );
};

export default StatusMainInfo;
