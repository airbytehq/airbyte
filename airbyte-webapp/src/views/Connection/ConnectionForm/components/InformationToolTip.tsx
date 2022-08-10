import React from "react";
import styled from "styled-components";

import { InfoIcon } from "components/icons/InfoIcon";
import ToolTip from "components/ToolTip";

const Info = styled.div`
  display: inline-block;
  vertical-align: text-top;
  margin-left: 5px;
  color: ${({ theme }) => theme.lightTextColor};
`;

const InformationToolTip: React.FC = ({ children }) => {
  return (
    <ToolTip
      control={
        <Info>
          <InfoIcon />
        </Info>
      }
    >
      {children}
    </ToolTip>
  );
};

export default InformationToolTip;
