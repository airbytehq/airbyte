import React from "react";
import styled from "styled-components";

import { ConnectorIcon } from "components/ConnectorIcon";

import { ConnectorDefinition } from "core/domain/connector";

interface CardProps {
  checked: boolean;
  data: ConnectorDefinition;
  type: "source" | "destination";
  onClick: (data: ConnectorDefinition) => void;
}

export const Box = styled.div<{
  checked: boolean;
}>`
  box-sizing: border-box;
  width: 144px;
  height: 144px;
  box-shadow: 0px 10px 12px rgba(74, 74, 87, 0.1);
  border: 2px solid ${({ checked, theme }) => (checked ? theme.primaryColor : theme.whiteColor)};
  border-radius: 18px;
  display: flex;
  align-items: center;
  flex-direction: column;
  // margin-right: 94px;
  // margin-bottom: 44px;
  font-size: 16px;
  text-align: center;
  background: #fff;
  padding: 10px;
  &:hover {
    cursor: pointer;
  }
  &:nth-child(4n) {
    //  margin-right: 0;
  }
`;

export const Image = styled(ConnectorIcon)`
  width: 88px;
  height: 88px;
  margin-bottom: 10px;
`;

const Card: React.FC<CardProps> = ({ data, onClick, checked }) => {
  return (
    <Box
      checked={checked}
      onClick={() => {
        onClick(data);
      }}
    >
      <Image icon={data.icon} />
      <div>{data.name}</div>
    </Box>
  );
};

export default Card;
