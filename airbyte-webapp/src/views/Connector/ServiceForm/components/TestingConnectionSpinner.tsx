import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, ProgressBar } from "components";

import styles from "./TestingConnectionSpinner.module.scss";

const LoadingContainer = styled.div`
  margin: 34px 0 9px;
  display: flex;
  align-items: center;
  justify-content: center;
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
        <Button
          customStyle={styles.styledButton}
          variant="secondary"
          type="button"
          onClick={() => props.onCancelTesting?.()}
        >
          <FormattedMessage id="form.cancel" />
        </Button>
      )}
    </LoadingContainer>
  );
};

export default TestingConnectionSpinner;
