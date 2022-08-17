import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import styles from "./CreateControls.module.scss";
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
  fetchingConnectorError,
  isLoadSchema,
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
      {errorMessage && !fetchingConnectorError && <TestingConnectionError errorMessage={errorMessage} />}
      {fetchingConnectorError && <FetchingConnectorError />}
      <Button
        customStyles={styles.submit_button}
        type="submit"
        disabled={isLoadSchema}
        label={<FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />}
      />
    </ButtonContainer>
  );
};

export default CreateControls;
