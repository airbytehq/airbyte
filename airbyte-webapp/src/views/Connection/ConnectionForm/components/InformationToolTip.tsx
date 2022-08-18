import React from "react";
import styled from "styled-components";

import { Tooltip } from "components/base/Tooltip";
import { InfoIcon } from "components/icons/InfoIcon";

const Info = styled.div`
  display: inline-block;
  vertical-align: text-top;
  margin-left: 5px;
  color: ${({ theme }) => theme.lightTextColor};
`;

const InformationToolTip: React.FC = ({ children }) => {
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

export default InformationToolTip;
