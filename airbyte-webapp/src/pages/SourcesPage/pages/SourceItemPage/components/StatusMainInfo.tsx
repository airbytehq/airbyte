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
import { DestinationDefinition } from "../../../../../core/resources/DestinationDefinition";
import { Connection } from "../../../../../core/resources/Connection";

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
  sourceData: Connection;
  onEnabledChange: () => void;
  destinationDefinition: DestinationDefinition;
  frequencyText?: string;
};

const StatusMainInfo: React.FC<IProps> = ({
  sourceData,
  onEnabledChange,
  destinationDefinition,
  frequencyText
}) => {
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
          {destinationDefinition.name}
        </SourceCell>
        <Cell>{frequencyText}</Cell>
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
