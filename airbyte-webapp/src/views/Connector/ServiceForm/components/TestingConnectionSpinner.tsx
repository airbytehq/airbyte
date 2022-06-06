import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, ProgressBar } from "components";

const LoadingContainer = styled.div`
  margin: 34px 0 9px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const StyledButton = styled(Button)`
  margin-left: 10px;
`;

// Progress Bar runs 2min for checking connections
const PROGRESS_BAR_TIME = 60 * 2;

interface TestingConnectionSpinnerProps {
  isCancellable?: boolean;
  onCancelTesting?: () => void;
}

const TestingConnectionSpinner: React.FC<TestingConnectionSpinnerProps> = (props) => {
  return (
    <LoadingContainer>
      <ProgressBar runTime={PROGRESS_BAR_TIME} />
      {props.isCancellable && (
        <StyledButton secondary type="button" onClick={() => props.onCancelTesting?.()}>
          <FormattedMessage id="form.cancel" />
        </StyledButton>
      )}
    </LoadingContainer>
  );
};

export default TestingConnectionSpinner;
