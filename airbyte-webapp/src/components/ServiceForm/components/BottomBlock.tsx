import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Button from "components/Button";
import TestingConnectionSpinner from "./TestingConnectionSpinner";
import TestingConnectionSuccess from "./TestingConnectionSuccess";
import TestingConnectionError from "./TestingConnectionError";

type IProps = {
  formType: "source" | "destination" | "connection";
  isSubmitting: boolean;
  hasSuccess?: boolean;
  isLoadSchema?: boolean;
  errorMessage?: React.ReactNode;
  additionBottomControls?: React.ReactNode;
};

const ButtonContainer = styled.div`
  margin-top: 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const BottomBlock: React.FC<IProps> = ({
  isSubmitting,
  formType,
  hasSuccess,
  errorMessage,
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
      {errorMessage ? (
        <TestingConnectionError errorMessage={errorMessage} />
      ) : (
        <div />
      )}
      <div>
        {additionBottomControls || null}
        <Button type="submit" disabled={isLoadSchema}>
          <FormattedMessage id={`onboarding.${formType}SetUp.buttonText`} />
        </Button>
      </div>
    </ButtonContainer>
  );
};

export default BottomBlock;
