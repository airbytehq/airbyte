import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Tooltip } from "components/base/Tooltip";
import { TickIcon } from "components/icons/TickIcon";

interface IProps {
  isActive: boolean;
  onClick?: () => void;
  isLoading?: boolean;
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

export const NotificationFlag: React.FC<IProps> = ({ isActive, onClick, isLoading }) => {
  return (
    <Tooltip
      control={
        <IconContainer
          onClick={() => {
            if (!isLoading) {
              onClick?.();
            }
          }}
        >
          <TickIcon color={isActive ? "#4F46E5" : "#D1D5DB"} width={20} height={20} />
        </IconContainer>
      }
      placement="top"
    >
      <FormattedMessage id={isActive ? "notification.status.enabled" : "notification.status.disabled"} />
    </Tooltip>
  );
};
