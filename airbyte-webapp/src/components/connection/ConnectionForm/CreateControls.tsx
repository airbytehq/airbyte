import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";
import { FlexContainer } from "components/ui/Flex";
import { StatusIcon } from "components/ui/StatusIcon";

import styles from "./CreateControls.module.scss";

interface CreateControlsProps {
  isSubmitting: boolean;
  isValid: boolean;
  errorMessage?: React.ReactNode;
}

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
  justify-content: right;
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

const CreateControls: React.FC<CreateControlsProps> = ({ isSubmitting, errorMessage, isValid }) => {
  return (
    <FlexContainer alignItems="center" justifyContent="space-between" className={styles.container}>
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
      <div>
        <Button type="submit" isLoading={isSubmitting} disabled={isSubmitting || !isValid}>
          <FormattedMessage id="onboarding.setUpConnection" />
        </Button>
      </div>
    </FlexContainer>
  );
};

export default CreateControls;
