import React from "react";
import styled from "styled-components";

import { DefaultLogoCatalog } from "components/common/DefaultLogoCatalog";

const IconContainer = styled.img`
  height: 100%;
  width: 100%;
  object-fit: contain;
`;

const IconDefaultContainer = styled.div`
  padding: 4px 0 3px;
`;

export const getIcon = (icon?: string): React.ReactNode => {
  if (!icon) {
    return (
      <IconDefaultContainer>
        <DefaultLogoCatalog />
      </IconDefaultContainer>
    );
  }

  return <IconContainer alt="" src={`data:image/svg+xml;utf8,${encodeURIComponent(icon)}`} />;
};
