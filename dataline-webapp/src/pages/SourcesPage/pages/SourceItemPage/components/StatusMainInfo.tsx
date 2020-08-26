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
import FrequencyConfig from "../../../../../data/FrequencyConfig.json";
import Toggle from "../../../../../components/Toggle";

type IProps = {
  sourceData: any;
  onEnabledChange: () => void;
};

const MainInfo = styled(ContentCard)`
  margin-bottom: 14px;
  padding: 23px 20px 24px 23px;
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
  margin-top: -20px;
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
  const cellText = FrequencyConfig.find(
    item => item.value === sourceData.frequency
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
          {sourceData.source}
        </SourceCell>
        <SourceCell flex={2}>
          <Img />
          {sourceData.destination}
        </SourceCell>
        <Cell>{cellText?.text}</Cell>
        <EnabledCell flex={1.1}>
          <ToggleLabel htmlFor="toggle-enabled-source">
            <FormattedMessage
              id={sourceData.enabled ? "sources.enabled" : "sources.disabled"}
            />
          </ToggleLabel>
          <Toggle
            onChange={onEnabledChange}
            value={sourceData.enabled}
            id="toggle-enabled-source"
          />
        </EnabledCell>
      </Row>
    </MainInfo>
  );
};

export default StatusMainInfo;
