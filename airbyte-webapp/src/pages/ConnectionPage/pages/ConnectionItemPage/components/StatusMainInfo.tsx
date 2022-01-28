import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import ImageBlock from "components/ImageBlock";
import { Header, Row, Cell } from "components/SimpleTableComponents";
import EnabledControl from "./EnabledControl";
import { Connection } from "core/resources/Connection";
import { DestinationDefinition, SourceDefinition } from "core/domain/connector";

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
        </SourceCell>
        <SourceCell flex={2}>
          <Img img={destinationDefinition?.icon} />
          {connection.destination?.destinationName}
        </SourceCell>
        <Cell>{frequencyText}</Cell>
        <EnabledCell flex={1.1}>
          <EnabledControl
            connection={connection}
            frequencyText={frequencyText}
          />
        </EnabledCell>
      </Row>
    </MainInfo>
  );
};

export default StatusMainInfo;
