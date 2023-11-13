import React from "react";
import styled from "styled-components";

import { DefaultLogoCatalog } from "components";

const IconContainer = styled.img`
  height: 100%;
  width: 100%;
`;

const IconDefaultContainer = styled.div`
  padding: 4px 0 3px;
`;
// <IconContainer alt="" src={`data:image/svg+xml;utf8,${encodeURIComponent(icon)}`} />
export const getIcon = (icon?: string): React.ReactNode => {
  if (!icon) {
    return (
      <IconDefaultContainer>
        <DefaultLogoCatalog />
      </IconDefaultContainer>
    );
  }

  return <IconContainer alt="" src={icon} />;
};
