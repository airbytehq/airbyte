import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

// import {  LoadingButton } from "components";
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

const Buttons = styled.div`
  // display: flex;
  // justify-content: space-between;
  // align-items: center;
  // flex-direction: row;
  // margin-top: 16px;
`;

// const ButtonRows = styled.div`
//   display: flex;
//   justify-content: space-around;
//   align-items: center;
//   margin-top: 40px;
//   width: 100%;
// `;

// const ControlButton = styled(LoadingButton)`
//   // margin-left: 10px;
//   width: 264px;
//   height: 68px;
//   border-radius: 6px;
//   font-weight: 500;
//   font-size: 18px;
//   line-height: 22px;
// `;

// const BackButton = styled(Button)`
//   // margin-left: auto;
//   width: 264px;
//   height: 68px;
//   border-radius: 6px;
//   font-weight: 500;
//   font-size: 18px;
//   line-height: 22px;
//   background: #fff;
//   color: #6b6b6f;
//   border-color: #d1d5db;
// `;

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
      <Buttons>
        <div>{showStatusMessage()}</div>
        <ButtonRows top="40" bottom="20">
          <BigButton
            type="button"
            secondary
            // disabled={isSubmitting || (!dirty && !enableControls)}
            onClick={onBack}
          >
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
      </Buttons>
    </>
  );
};

export default EditControls;
