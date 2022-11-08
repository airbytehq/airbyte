import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";
import { Spinner } from "components/ui/Spinner";

interface IProps {
  isSubmitting: boolean;
  isValid: boolean;
  dirty: boolean;
  resetForm: () => void;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
}

const Controls = styled.div`
  margin-top: 34px;
`;

const ButtonContainer = styled.span`
  margin-left: 10px;
`;

const Success = styled(ButtonContainer)`
  color: ${({ theme }) => theme.successColor};
  font-size: 14px;
  line-height: 17px;
`;

const Error = styled(Success)`
  color: ${({ theme }) => theme.dangerColor};
`;

const SpinnerContainer = styled.div`
  margin: -13px 0 0 10px;
  display: inline-block;
  position: relative;
  top: 10px;
`;

const EditControls: React.FC<IProps> = ({ isSubmitting, isValid, dirty, resetForm, successMessage, errorMessage }) => {
  const showStatusMessage = () => {
    if (isSubmitting) {
      return (
        <SpinnerContainer>
          <Spinner small />
        </SpinnerContainer>
      );
    }
    if (errorMessage) {
      return <Error>{errorMessage}</Error>;
    }
    if (successMessage && !dirty) {
      return <Success data-id="success-result">{successMessage}</Success>;
    }
    return null;
  };

  return (
    <Controls>
      <Button type="submit" disabled={isSubmitting || !isValid || !dirty}>
        <FormattedMessage id="form.saveChanges" />
      </Button>
      <ButtonContainer>
        <Button type="button" variant="secondary" disabled={isSubmitting || !dirty} onClick={resetForm}>
          <FormattedMessage id="form.cancel" />
        </Button>
      </ButtonContainer>
      {showStatusMessage()}
    </Controls>
  );
};

export default EditControls;
