import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button } from "components";
import TestingConnectionSpinner from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";
import TestingConnectionError from "./TestingConnectionError";
import FetchingConnectorError from "./FetchingConnectorError";

type IProps = {
  formType: "source" | "destination" | "connection";
  isSubmitting: boolean;
  hasSuccess?: boolean;
  isLoadSchema?: boolean;
  errorMessage?: React.ReactNode;
  fetchingConnectorError?: Error;
  additionBottomControls?: React.ReactNode;
};

const ButtonContainer = styled.div`
  margin-top: 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const CreateControls: React.FC<IProps> = ({
  isSubmitting,
  formType,
  hasSuccess,
  errorMessage,
  fetchingConnectorError,
  isLoadSchema,
  additionBottomControls,
}) => {
  if (hasSuccess) {
    return <TestingConnectionSuccess />;
  }

  if (isSubmitting) {
    return <TestingConnectionSpinner />;
  }

  return (
    <ButtonContainer>
      {errorMessage && !fetchingConnectorError && (
        <TestingConnectionError errorMessage={errorMessage} />
      )}
      {fetchingConnectorError && <FetchingConnectorError />}
      {!errorMessage && !fetchingConnectorError && <div />}
      <div>
        {additionBottomControls || null}
        <Button type="submit" disabled={isLoadSchema}>
          <FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />
        </Button>
      </div>
    </ButtonContainer>
  );
};

export default CreateControls;
