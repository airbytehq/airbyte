import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import Button from "components/Button";
import Spinner from "components/Spinner";
import { useServiceForm } from "../serviceFormContext";

type IProps = {
  isSubmitting: boolean;
  isValid: boolean;
  dirty: boolean;
  resetForm: () => void;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
};

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
  max-width: 68%;
  display: inline-block;
  vertical-align: middle;
`;

const SpinnerContainer = styled.div`
  margin: -13px 0 0 10px;
  display: inline-block;
  position: relative;
  top: 10px;
`;

const EditControls: React.FC<IProps> = ({
  isSubmitting,
  isValid,
  dirty,
  resetForm,
  successMessage,
  errorMessage,
}) => {
  const { unfinishedSecrets } = useServiceForm();

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
      <Button
        type="submit"
        disabled={
          isSubmitting ||
          !isValid ||
          !dirty ||
          Object.keys(unfinishedSecrets).length > 0
        }
      >
        <FormattedMessage id="form.saveChanges" />
      </Button>
      <ButtonContainer>
        <Button
          type="button"
          secondary
          disabled={isSubmitting || !isValid || !dirty}
          onClick={resetForm}
        >
          <FormattedMessage id="form.cancel" />
        </Button>
      </ButtonContainer>
      {showStatusMessage()}
    </Controls>
  );
};

export default EditControls;
