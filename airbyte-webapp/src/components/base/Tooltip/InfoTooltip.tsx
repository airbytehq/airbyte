import React from "react";
import styled from "styled-components";

import { InfoIcon } from "components/icons/InfoIcon";

import { Tooltip } from "./Tooltip";

const Info = styled.div`
  display: inline-block;
  vertical-align: text-top;
  margin-left: 5px;
  color: ${({ theme }) => theme.lightTextColor};
`;

export const InfoTooltip: React.FC = ({ children }) => {
  return (
    <Tooltip
      control={
        <Info>
          <InfoIcon />
        </Info>
      }
    >
      {children}
    </Tooltip>
  );
};
