import React from "react";
import styled from "styled-components";

import { ConnectorIcon } from "components/common/ConnectorIcon";

interface IProps {
  name: string;
  icon?: string;
}

export const Content = styled.div`
  background: ${({ theme }) => theme.lightPrimaryColor};
  border-radius: 4px;
  width: 356px;
  height: 36px;
  display: flex;
  align-items: center;
  flex-direction: row;
  padding: 0 9px;
`;

const Name = styled.div`
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 14px;
  line-height: 20px;
  margin-left: 6px;
`;

const ConnectionBlockItem: React.FC<IProps> = (props) => {
  return (
    <Content>
      <ConnectorIcon icon={props.icon} />
      <Name>{props.name}</Name>
    </Content>
  );
};

export { ConnectionBlockItem };
