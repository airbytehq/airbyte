import React from "react";
import styled from "styled-components";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowRight } from "@fortawesome/free-solid-svg-icons";

import ImageBlock from "components/ImageBlock";

const Content = styled.div`
  height: 36px;
  width: 100%;
  padding: 0 12px;
  border-radius: 4px;
  font-size: 14px;
  line-height: 20px;
  border: 1px solid ${({ theme }) => theme.greyColor0};
  background: ${({ theme }) => theme.greyColor0};
  color: ${({ theme }) => theme.textColor};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Icon = styled(ImageBlock)`
  margin-right: 6px;
  display: inline-block;
  vertical-align: sub;
`;

const ConnectorName = styled.div`
  display: flex;
  align-items: center;
  flex-direction: row;
`;

type IProps = {
  name: string;
  icon?: string;
};

const Connector: React.FC<IProps> = ({ name, icon }) => {
  return (
    <Content>
      <ConnectorName>
        <Icon img={icon} small />
        <span>{name}</span>
      </ConnectorName>
      <FontAwesomeIcon icon={faArrowRight} />
    </Content>
  );
};

export default Connector;
