import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components";

import { TestingConnectionError, FetchingConnectorError } from "./TestingConnectionError";
// import TestingConnectionSpinner from "./TestingConnectionSpinner";
// import TestingConnectionSuccess from "./TestingConnectionSuccess";

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

const SubmitButton = styled(Button)`
  // margin-left: auto;
  width: 264px;
  height: 68px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 18px;
  line-height: 22px;
`;

const BackButton = styled(Button)`
  // margin-left: auto;
  width: 264px;
  height: 68px;
  border-radius: 6px;
  font-weight: 500;
  font-size: 18px;
  line-height: 22px;
  background: #fff;
  color: #6b6b6f;
  border-color: #d1d5db;
`;

const ButtonRows = styled.div`
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-top: 40px;
  width: 100%;
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
      <ButtonRows>
        <BackButton type="button" onClick={onBack}>
          <FormattedMessage id="form.button.back" />
        </BackButton>
        <SubmitButton type="submit" disabled={disabled}>
          <FormattedMessage id="form.button.saveTest" />
        </SubmitButton>
      </ButtonRows>
    </ButtonContainer>
  );
};

export default CreateControls;
