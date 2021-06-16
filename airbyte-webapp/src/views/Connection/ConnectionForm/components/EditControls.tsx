import React from "react";
import styled from "styled-components";
import { FormattedMessage } from "react-intl";

import { Button, Spinner } from "components";

type IProps = {
  isSubmitting: boolean;
  dirty: boolean;
  resetForm: () => void;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  editSchemeMode?: boolean;
};

const Warning = styled.div`
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: bold;
`;

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

const EditControls: React.FC<IProps> = ({
  isSubmitting,
  dirty,
  resetForm,
  successMessage,
  errorMessage,
  editSchemeMode,
}) => {
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
      {editSchemeMode && (
        <Warning>
          <FormattedMessage id="connection.warningUpdateSchema" />
        </Warning>
      )}
      <Button
        type="submit"
        disabled={(isSubmitting || !dirty) && (!editSchemeMode || isSubmitting)}
      >
        {editSchemeMode ? (
          <FormattedMessage id="connection.saveAndReset" />
        ) : (
          <FormattedMessage id="form.saveChanges" />
        )}
      </Button>
      <ButtonContainer>
        <Button
          type="button"
          secondary
          disabled={
            (isSubmitting || !dirty) && (!editSchemeMode || isSubmitting)
          }
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
