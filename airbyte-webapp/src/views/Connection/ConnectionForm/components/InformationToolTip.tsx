import React from "react";
import styled from "styled-components";

import { InfoIcon } from "components/icons/InfoIcon";
import ToolTip from "components/ToolTip";

const ToolTipBlock = styled(ToolTip)`
  top: calc(100%);
  background: ${({ theme }) => theme.darkBlue90};
  color: ${({ theme }) => theme.whiteColor};
  padding: 11px 19px;
  min-width: 250px;
  font-size: 11px;
  line-height: 16px;
  font-weight: 500;
`;

const Info = styled.div`
  display: inline-block;
  vertical-align: text-top;
  margin-left: 5px;
  color: ${({ theme }) => theme.lightTextColor};
`;

const InformationToolTip: React.FC = ({ children }) => {
  return (
    <ToolTipBlock
      control={
        <Info>
          <InfoIcon />
        </Info>
      }
    >
      {children}
    </ToolTipBlock>
  );
};

export default InformationToolTip;
