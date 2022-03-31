import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import TestingConnectionSpinner from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";
import {
  TestingConnectionError,
  FetchingConnectorError,
} from "./TestingConnectionError";

type IProps = {
  formType: "source" | "destination";
  isSubmitting: boolean;
  errorMessage?: React.ReactNode;
  hasSuccess?: boolean;
  isLoadSchema?: boolean;
  fetchingConnectorError?: Error | null;

  isTestConnectionInProgress: boolean;
  onCancelTesting?: () => void;
};

const ButtonContainer = styled.div`
  margin-top: 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const SubmitButton = styled(Button)`
  margin-left: auto;
`;

const CreateControls: React.FC<IProps> = ({
  isTestConnectionInProgress,
  isSubmitting,
  formType,
  hasSuccess,
  errorMessage,
  fetchingConnectorError,
  isLoadSchema,
  onCancelTesting,
}) => {
  if (isSubmitting) {
    return (
      <TestingConnectionSpinner
        isCancellable={isTestConnectionInProgress}
        onCancelTesting={onCancelTesting}
      />
    );
  }

  if (hasSuccess) {
    return <TestingConnectionSuccess />;
  }

  return (
    <ButtonContainer>
      {errorMessage && !fetchingConnectorError && (
        <TestingConnectionError errorMessage={errorMessage} />
      )}
      {fetchingConnectorError && <FetchingConnectorError />}
      <SubmitButton type="submit" disabled={isLoadSchema}>
        <FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />
      </SubmitButton>
    </ButtonContainer>
  );
};

export default CreateControls;
