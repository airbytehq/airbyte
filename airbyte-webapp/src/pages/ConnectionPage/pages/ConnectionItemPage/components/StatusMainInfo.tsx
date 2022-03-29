import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ContentCard, ImageBlock } from "components";
import { Header, Row, Cell } from "components/SimpleTableComponents";
import EnabledControl from "./EnabledControl";
import { DestinationDefinition, SourceDefinition } from "core/domain/connector";

import { Connection } from "core/resources/Connection";
import { ReleaseStageBadge } from "components/ReleaseStageBadge";
import { ConnectionStatus } from "core/domain/connection";

const MainInfo = styled(ContentCard)`
  margin-bottom: 14px;
  padding: 23px 20px 20px 23px;
`;

const Img = styled(ImageBlock)`
  display: inline-block;
`;

const SourceCell = styled(Cell)`
  display: flex;
  align-items: center;
  gap: 6px;
`;

const EnabledCell = styled(Cell)`
  display: flex;
  align-items: center;
  margin-top: -18px;
`;

type IProps = {
  connection: Connection;
  frequencyText?: string;
  destinationDefinition?: DestinationDefinition;
  sourceDefinition?: SourceDefinition;
};

const StatusMainInfo: React.FC<IProps> = ({
  connection,
  frequencyText,
  destinationDefinition,
  sourceDefinition,
}) => {
  const actionsDisabled = connection.status === ConnectionStatus.DEPRECATED;

  return (
    <MainInfo>
      <Header>
        <Cell flex={2}>
          <FormattedMessage id="sources.source" />
        </Cell>
        <Cell flex={2}>
          <FormattedMessage id="sidebar.destinations" />
        </Cell>
        <Cell>
          <FormattedMessage id="tables.frequency" />
        </Cell>
        <Cell flex={1.1}></Cell>
      </Header>
      <Row>
        <SourceCell flex={2}>
          <Img img={sourceDefinition?.icon} />
          {connection.source?.sourceName}
          <ReleaseStageBadge stage={sourceDefinition?.releaseStage} />
        </SourceCell>
        <SourceCell flex={2}>
          <Img img={destinationDefinition?.icon} />
          {connection.destination?.destinationName}
          <ReleaseStageBadge stage={destinationDefinition?.releaseStage} />
        </SourceCell>
        <Cell>{frequencyText}</Cell>
        <EnabledCell flex={1.1}>
          <EnabledControl
            disabled={actionsDisabled}
            connection={connection}
            frequencyText={frequencyText}
          />
        </EnabledCell>
      </Row>
    </MainInfo>
  );
};

export default StatusMainInfo;
