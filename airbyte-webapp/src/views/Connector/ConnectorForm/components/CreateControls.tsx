import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";

import styles from "./CreateControls.module.scss";
import { TestingConnectionError } from "./TestingConnectionError";
import { TestingConnectionSpinner } from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";

interface CreateControlProps {
  formType: "source" | "destination";
  isSubmitting: boolean;
  errorMessage?: React.ReactNode;
  hasSuccess?: boolean;

  isTestConnectionInProgress: boolean;
  onCancelTesting?: () => void;
}

const ButtonContainer = styled.div`
  margin-top: 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const CreateControls: React.FC<CreateControlProps> = ({
  isTestConnectionInProgress,
  isSubmitting,
  formType,
  hasSuccess,
  errorMessage,
  onCancelTesting,
}) => {
  if (isSubmitting) {
    return <TestingConnectionSpinner isCancellable={isTestConnectionInProgress} onCancelTesting={onCancelTesting} />;
  }

  if (hasSuccess) {
    return <TestingConnectionSuccess />;
  }

  return (
    <ButtonContainer>
      {errorMessage && <TestingConnectionError errorMessage={errorMessage} />}
      <Button className={styles.submitButton} type="submit">
        <FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />
      </Button>
    </ButtonContainer>
  );
};

export default CreateControls;
