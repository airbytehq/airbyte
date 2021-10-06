import React from "react";
import styled from "styled-components";

import ContentCard from "components/ContentCard";
import BaseClearView from "components/BaseClearView";
import { H4 } from "components";

const Content = styled(ContentCard)`
  width: 100%;
  max-width: 600px;
  padding: 50px 15px;
`;

const ErrorOccurredView: React.FC<{ message: React.ReactNode }> = ({
  message,
}) => {
  return (
    <BaseClearView>
      <Content>
        <H4 center>{message}</H4>
      </Content>
    </BaseClearView>
  );
};

export { ErrorOccurredView };
