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
  withLine?: boolean;
};

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

const ControlButton = styled(Button)`
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

const SpinnerContainer = styled.div`
  margin: -13px 0 0 10px;
  display: inline-block;
  position: relative;
  top: 10px;
`;

const Line = styled.div`
  min-width: 100%;
  height: 1px;
  background: ${({ theme }) => theme.greyColor20};
  margin: 16px -27px 0 -24px;
`;

const EditControls: React.FC<IProps> = ({
  isSubmitting,
  dirty,
  resetForm,
  successMessage,
  errorMessage,
  editSchemeMode,
  withLine,
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
          <ControlButton
            type="submit"
            disabled={
              (isSubmitting || !dirty) && (!editSchemeMode || isSubmitting)
            }
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
