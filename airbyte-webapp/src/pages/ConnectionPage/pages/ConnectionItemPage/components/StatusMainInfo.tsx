import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { ContentCard } from "components";
import { ConnectorIcon } from "components/ConnectorIcon";
import { ReleaseStageBadge } from "components/ReleaseStageBadge";
import { Header, Row, Cell } from "components/SimpleTableComponents";

import { Connection } from "core/domain/connection";
import { DestinationDefinition, SourceDefinition } from "core/domain/connector";

import EnabledControl from "./EnabledControl";

const MainInfo = styled(ContentCard)`
  margin-bottom: 14px;
  padding: 23px 20px 20px 23px;
`;

const Img = styled(ConnectorIcon)`
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
  allowSync?: boolean;
};

const StatusMainInfo: React.FC<IProps> = ({
  connection,
  frequencyText,
  destinationDefinition,
  sourceDefinition,
  allowSync,
}) => {
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
          <Img icon={sourceDefinition?.icon} />
          {connection.source?.sourceName}
          <ReleaseStageBadge stage={sourceDefinition?.releaseStage} />
        </SourceCell>
        <SourceCell flex={2}>
          <Img icon={destinationDefinition?.icon} />
          {connection.destination?.destinationName}
          <ReleaseStageBadge stage={destinationDefinition?.releaseStage} />
        </SourceCell>
        <Cell>{frequencyText}</Cell>
        <EnabledCell flex={1.1}>
          <EnabledControl disabled={!allowSync} connection={connection} frequencyText={frequencyText} />
        </EnabledCell>
      </Row>
    </MainInfo>
  );
};

export default StatusMainInfo;
