import React from "react";
import styled from "styled-components";

import { H4, ContentCard } from "components";
import BaseClearView from "components/BaseClearView";

const Content = styled(ContentCard)`
  width: 100%;
  max-width: 600px;
  padding: 50px 15px;
`;

interface ErrorOccurredViewProps {
  message: React.ReactNode;
  onLogoClick?: React.MouseEventHandler;
}

const ErrorOccurredView: React.FC<ErrorOccurredViewProps> = ({ message, onLogoClick, children }) => {
  return (
    <BaseClearView onLogoClick={onLogoClick}>
      <Content>
        <H4 center>{message}</H4>
        {children}
      </Content>
    </BaseClearView>
  );
};

export { ErrorOccurredView };
