import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, Spinner, StatusIcon } from "components";

interface CreateControlsProps {
  isSubmitting: boolean;
  isValid: boolean;
  errorMessage?: React.ReactNode;
  onBack?: () => void;
}

const ButtonContainer = styled.div`
  padding: 15px 0;
  // display: flex;
  // align-items: center;
  // justify-content: space-between;
  // flex-direction: column;
`;

const LoadingContainer = styled(ButtonContainer)`
  font-weight: 600;
  font-size: 14px;
  line-height: 17px;
  color: ${({ theme }) => theme.darkPrimaryColor};
  justify-content: center;
`;

const Loader = styled.div`
  margin-right: 10px;
`;

const Success = styled(StatusIcon)`
  width: 26px;
  min-width: 26px;
  height: 26px;
  padding-top: 5px;
  font-size: 17px;
`;

const Error = styled(Success)`
  padding-top: 4px;
  padding-left: 1px;
`;

const ErrorBlock = styled.div`
  display: flex;
  justify-content: left;
  align-items: center;
  font-weight: 600;
  font-size: 12px;
  line-height: 18px;
  color: ${({ theme }) => theme.darkPrimaryColor};
`;

const ErrorText = styled.div`
  font-weight: normal;
  color: ${({ theme }) => theme.dangerColor};
  max-width: 400px;
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

const CreateControls: React.FC<CreateControlsProps> = ({ isSubmitting, errorMessage, isValid, onBack }) => {
  if (isSubmitting) {
    return (
      <LoadingContainer>
        <Loader>
          <Spinner />
        </Loader>
        <FormattedMessage id="form.testingConnection" />
      </LoadingContainer>
    );
  }
  return (
    <ButtonContainer>
      {errorMessage ? (
        <ErrorBlock>
          <Error />
          <div>
            <FormattedMessage id="form.failedTests" />
            <ErrorText>{errorMessage}</ErrorText>
          </div>
        </ErrorBlock>
      ) : (
        <div />
      )}
      <ButtonRows>
        <BackButton type="button" onClick={onBack}>
          <FormattedMessage id="form.button.back" />
        </BackButton>
        <SubmitButton type="submit" disabled={isSubmitting || !isValid}>
          <FormattedMessage id="form.button.finishSetup" />
        </SubmitButton>
      </ButtonRows>
    </ButtonContainer>
  );
};

export default CreateControls;
