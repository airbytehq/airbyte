import React from "react";
import styled from "styled-components";

import { Button, ProgressBar } from "components";

const LoadingContainer = styled.div`
  margin: 34px 0 9px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

// Progress Bar runs 2min for checking connections
const PROGRESS_BAR_TIME = 60 * 2;

type TestingConnectionSpinnerProps = {
  isCancellable?: boolean;
};

const TestingConnectionSpinner: React.FC<TestingConnectionSpinnerProps> = (
  props
) => {
  return (
    <LoadingContainer>
      <ProgressBar runTime={PROGRESS_BAR_TIME} />
      {props.isCancellable && (
        <Button secondary type="button">
          cancel
        </Button>
      )}
    </LoadingContainer>
  );
};

export default TestingConnectionSpinner;
