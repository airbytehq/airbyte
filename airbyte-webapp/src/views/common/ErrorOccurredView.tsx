import React from "react";
import styled from "styled-components";

import { H4, ContentCard } from "components";
import BaseClearView from "components/BaseClearView";

const Content = styled(ContentCard)`
  width: 100%;
  max-width: 600px;
  padding: 50px 15px;
`;

const ErrorOccurredView: React.FC<{ message: React.ReactNode }> = ({ message, children }) => {
  return (
    <BaseClearView>
      <Content>
        <H4 center>{message}</H4>
        {children}
      </Content>
    </BaseClearView>
  );
};

export { ErrorOccurredView };
