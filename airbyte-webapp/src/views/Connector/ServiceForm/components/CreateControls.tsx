import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

// import { Button } from "components";

import { BigButton, ButtonRows } from "components/base/Button/BigButton";

import { TestingConnectionError, FetchingConnectorError } from "./TestingConnectionError";

interface CreateControlProps {
  formType: "source" | "destination";
  isSubmitting: boolean;
  errorMessage?: React.ReactNode;
  hasSuccess?: boolean;
  isLoadSchema?: boolean;
  fetchingConnectorError?: Error | null;
  isTestConnectionInProgress: boolean;
  onCancelTesting?: () => void;
  onBack?: () => void;
  disabled?: boolean;
}

const ButtonContainer = styled.div`
  margin-top: 34px;
  display: flex;
  //align-items: center;
  justify-content: space-between;
  flex-direction: column;
`;

const CreateControls: React.FC<CreateControlProps> = ({
  // isTestConnectionInProgress,
  isSubmitting,
  // formType,
  disabled,
  hasSuccess,
  errorMessage,
  fetchingConnectorError,
  // isLoadSchema,
  // onCancelTesting,
  onBack,
}) => {
  if (isSubmitting) {
    // return <TestingConnectionSpinner isCancellable={isTestConnectionInProgress} onCancelTesting={onCancelTesting} />;
  }

  if (hasSuccess) {
    // return <TestingConnectionSuccess />;
  }
  return (
    <ButtonContainer>
      {errorMessage && !fetchingConnectorError && <TestingConnectionError errorMessage={errorMessage} />}
      {fetchingConnectorError && <FetchingConnectorError />}
      <ButtonRows top="20" bottom="20" full>
        <BigButton type="button" onClick={onBack} secondary>
          <FormattedMessage id="form.button.back" />
        </BigButton>
        <BigButton type="submit" disabled={disabled}>
          <FormattedMessage id="form.button.saveTest" />
        </BigButton>
      </ButtonRows>
    </ButtonContainer>
  );
};

export default CreateControls;
