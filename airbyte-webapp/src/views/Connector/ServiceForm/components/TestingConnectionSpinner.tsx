import React from "react";
import styled from "styled-components";

import { ProgressBar } from "components";

const LoadingContainer = styled.div`
  margin: 34px 0 9px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

// Progress Bar runs 2min for checking connections
const PROGRESS_BAR_TIME = 60 * 2;

const TestingConnectionSpinner: React.FC = () => {
  return (
    <LoadingContainer>
      <ProgressBar runTime={PROGRESS_BAR_TIME} />
    </LoadingContainer>
  );
};

export default TestingConnectionSpinner;
