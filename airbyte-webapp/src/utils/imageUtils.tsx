import React from "react";
import styled from "styled-components";

import { DefaultLogoCatalog } from "components";

const IconContainer = styled.div`
  height: 100%;
  & > svg {
    height: 100%;
    width: 100%;
  }
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

  return <IconContainer dangerouslySetInnerHTML={{ __html: icon }} />;
};
