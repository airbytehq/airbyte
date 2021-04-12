import React from "react";
import styled from "styled-components";

import { Cell } from "components/SimpleTableComponents";
import { DropDown, DropdownProps } from "components/DropDown";

const DropDownContainer = styled.div`
  padding-right: 10px;
`;

const StyledDropDown = styled(DropDown)`
  & ~ .rw-popup-container {
    min-width: 260px;
    left: auto;
  }
`;

const SyncSettingsCell: React.FC<DropdownProps> = (props) => (
  <Cell>
    <DropDownContainer>
      <StyledDropDown {...props} fullText withBorder />
    </DropDownContainer>
  </Cell>
);

export { SyncSettingsCell };
