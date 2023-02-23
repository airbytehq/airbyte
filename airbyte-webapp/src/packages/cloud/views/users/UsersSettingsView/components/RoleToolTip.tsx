import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { InfoTooltip } from "components/ui/Tooltip";

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
    <InfoTooltip>
      <LineBlock>
        <FormattedMessage id="settings.accessManagement.roleViewers" />
      </LineBlock>
      <LineBlock>
        <FormattedMessage id="settings.accessManagement.roleEditors" />
      </LineBlock>

      <LineBlock>
        <FormattedMessage id="settings.accessManagement.roleAdmin" />
      </LineBlock>
    </InfoTooltip>
  );
};

export default RoleToolTip;
