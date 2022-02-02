import React from "react";
import styled from "styled-components";

import { ProgressBar } from "components";

const LoadingContainer = styled.div`
  margin: 34px 0 9px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const TestingConnectionSpinner: React.FC = () => {
  return (
    <LoadingContainer>
      <ProgressBar runTime={120} />
    </LoadingContainer>
  );
};

export default TestingConnectionSpinner;
