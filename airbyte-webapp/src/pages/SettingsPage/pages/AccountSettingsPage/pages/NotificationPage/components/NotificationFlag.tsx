import React from "react";
import styled from "styled-components";

import { TickIcon } from "components/icons/TickIcon";

interface IProps {
  isActive: boolean;
  onClick?: () => void;
}

const IconContainer = styled.div`
  width: 25px;
  height: 25px;
  background-color: transparent;
  cursor: pointer;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
`;

export const NotificationFlag: React.FC<IProps> = ({ isActive, onClick }) => {
  return (
    <IconContainer onClick={onClick}>
      <TickIcon color={isActive ? "#4F46E5" : "#D1D5DB"} width={20} height={20} />
    </IconContainer>
  );
};
