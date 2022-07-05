import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { TestingConnectionError, FetchingConnectorError } from "./TestingConnectionError";
import TestingConnectionSpinner from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";

interface CreateControlProps {
  formType: "source" | "destination";
  isSubmitting: boolean;
  errorMessage?: React.ReactNode;
  hasSuccess?: boolean;
  isLoadSchema?: boolean;
  fetchingConnectorError?: Error | null;

  isTestConnectionInProgress: boolean;
  onCancelTesting?: () => void;
  isValid: boolean;
}

const ButtonContainer = styled.div`
  margin-top: 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const SubmitButton = styled(Button)`
  margin-left: auto;
`;

const CreateControls: React.FC<CreateControlProps> = ({
  isTestConnectionInProgress,
  isSubmitting,
  formType,
  hasSuccess,
  errorMessage,
  fetchingConnectorError,
  isLoadSchema,
  onCancelTesting,
  isValid,
}) => {
  if (isSubmitting) {
    return <TestingConnectionSpinner isCancellable={isTestConnectionInProgress} onCancelTesting={onCancelTesting} />;
  }

  if (hasSuccess) {
    return <TestingConnectionSuccess />;
  }

  return (
    <ButtonContainer>
      {errorMessage && !fetchingConnectorError && <TestingConnectionError errorMessage={errorMessage} />}
      {fetchingConnectorError && <FetchingConnectorError />}
      <SubmitButton type="submit" disabled={isLoadSchema || !isValid}>
        <FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />
      </SubmitButton>
    </ButtonContainer>
  );
};

export default CreateControls;
