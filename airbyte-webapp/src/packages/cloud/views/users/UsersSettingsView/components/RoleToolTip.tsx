import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import ToolTip from "components/ToolTip";

import InfoIcon from "./InfoIcon";

const Info = styled.div`
  margin-left: 7px;
  vertical-align: middle;
  display: inline-block;
`;

const LineBlock = styled.div`
  text-transform: none;
  font-weight: 500;
  font-size: 11px;
  line-height: 13px;
  letter-spacing: 0.3px;
  min-width: 230px;
  color: ${({ theme }) => theme.whiteColor};
  margin-bottom: 5px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const RoleToolTip: React.FC = () => {
  return (
    <ToolTip
      control={
        <Info>
          <InfoIcon />
        </Info>
      }
    >
      <>
        <LineBlock>
          <FormattedMessage id="settings.accessManagement.roleViewers" />
        </LineBlock>
        <LineBlock>
          <FormattedMessage id="settings.accessManagement.roleEditors" />
        </LineBlock>

        <LineBlock>
          <FormattedMessage id="settings.accessManagement.roleAdmin" />
        </LineBlock>
      </>
    </ToolTip>
  );
};

export default RoleToolTip;
