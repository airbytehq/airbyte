import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button, LoadingButton } from "components";

interface EditControlProps {
  isSubmitting: boolean;
  dirty: boolean;
  submitDisabled?: boolean;
  resetForm: () => void;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  editSchemeMode?: boolean;
  withLine?: boolean;
}

const Warning = styled.div`
  margin-bottom: 10px;
  font-size: 12px;
  font-weight: bold;
`;

const Buttons = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-direction: row;
  margin-top: 16px;
`;

const ControlButton = styled(LoadingButton)`
  margin-left: 10px;
`;

const Success = styled.span`
  color: ${({ theme }) => theme.successColor};
  font-size: 14px;
  line-height: 17px;
`;

const Error = styled(Success)`
  color: ${({ theme }) => theme.dangerColor};
`;

const Line = styled.div`
  min-width: 100%;
  height: 1px;
  background: ${({ theme }) => theme.greyColor20};
  margin: 16px -27px 0 -24px;
`;

const EditControls: React.FC<EditControlProps> = ({
  isSubmitting,
  dirty,
  submitDisabled,
  resetForm,
  successMessage,
  errorMessage,
  editSchemeMode,
  withLine,
}) => {
  const showStatusMessage = () => {
    if (errorMessage) {
      return <Error>{errorMessage}</Error>;
    }
    if (successMessage && !dirty) {
      return <Success data-id="success-result">{successMessage}</Success>;
    }
    return null;
  };

  return (
    <>
      {editSchemeMode && (
        <Warning>
          <FormattedMessage id="connection.warningUpdateSchema" />
        </Warning>
      )}
      {withLine && <Line />}
      <Buttons>
        <div>{showStatusMessage()}</div>
        <div>
          <Button type="button" secondary disabled={isSubmitting || (!dirty && !editSchemeMode)} onClick={resetForm}>
            <FormattedMessage id="form.cancel" />
          </Button>
          <ControlButton
            type="submit"
            isLoading={isSubmitting}
            disabled={submitDisabled || isSubmitting || (!dirty && !editSchemeMode)}
          >
            {editSchemeMode ? (
              <FormattedMessage id="connection.saveAndReset" />
            ) : (
              <FormattedMessage id="form.saveChanges" />
            )}
          </ControlButton>
        </div>
      </Buttons>
    </>
  );
};

export default EditControls;
