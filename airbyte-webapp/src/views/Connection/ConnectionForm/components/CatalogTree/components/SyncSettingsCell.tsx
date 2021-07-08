import React from "react";
import styled from "styled-components";

import { Cell } from "components/SimpleTableComponents";
import { DropDown, DropdownProps } from "components/base";

const StyledDropDown = styled(DropDown)`
  & ~ .rw-popup-container {
    min-width: 260px;
    left: auto;
  }
`;

const SyncSettingsCell: React.FC<DropdownProps> = (props) => (
  <Cell flex={1.5}>
    <StyledDropDown {...props} fullText withBorder />
  </Cell>
);

export { SyncSettingsCell };
