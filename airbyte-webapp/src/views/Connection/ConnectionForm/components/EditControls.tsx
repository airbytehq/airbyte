import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { BigButton, ButtonRows } from "components/base/Button/BigButton";

interface EditControlProps {
  isSubmitting: boolean;
  dirty: boolean;
  submitDisabled?: boolean;
  resetForm: () => void;
  onBack?: () => void;
  successMessage?: React.ReactNode;
  errorMessage?: React.ReactNode;
  enableControls?: boolean;
  withLine?: boolean;
}

// const Container = styled.div``;

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
  onBack,
  successMessage,
  errorMessage,
  enableControls,
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
      {withLine && <Line />}
      {showStatusMessage() ? <div>showStatusMessage()</div> : null}
      <ButtonRows top="0" bottom="0" position="fixed" width="calc(100% - 240px)">
        <BigButton type="button" secondary onClick={onBack}>
          <FormattedMessage id="form.button.back" />
        </BigButton>
        <BigButton
          type="submit"
          isLoading={isSubmitting}
          disabled={submitDisabled || isSubmitting || (!dirty && !enableControls)}
        >
          <FormattedMessage id="form.saveChanges" />
        </BigButton>
      </ButtonRows>
    </>
  );
};

export default EditControls;
