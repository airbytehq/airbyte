import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

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
  isCopyMode?: boolean;
  isEditMode?: boolean;
}

const ButtonContainer = styled.div`
  margin-top: 20px;
  display: flex;
  //align-items: center;
  justify-content: space-between;
  flex-direction: column;

  // position: sticky;
  // bottom: 0;
  // z-index: 1;
  padding-right: 50px;
`;

const CreateControls: React.FC<CreateControlProps> = ({
  isSubmitting,
  disabled,
  hasSuccess,
  errorMessage,
  fetchingConnectorError,
  isEditMode,
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
      <ButtonRows top="0" width={isEditMode ? "calc(100% - 18px)" : "calc(100% - 90px)"} position="absolute">
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
