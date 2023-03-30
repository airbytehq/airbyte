import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LoadingButton } from "components";
import { Button } from "components/base/Button";
import Modal from "components/Modal";

import useLoadingState from "../../hooks/useLoadingState";

const Content = styled.div`
  width: 540px;
`;

const ButtonContent = styled.div<{
  reverse?: boolean;
}>`
  width: 85%;
  margin: 50px auto 36px auto;
  display: flex;
  justify-content: space-around;
  flex-direction: ${({ reverse }) => (reverse ? "row" : "row-reverse")};
`;

const ButtonWithMargin = styled(Button)<{
  secondary?: boolean;
}>`
  min-width: 140px;
  height: 44px;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  color: ${({ secondary }) => (secondary ? "#27272a" : "#fff")};
`;

const ButtonLoadingContainer = styled(LoadingButton)`
  border-radius: 6px;
  font-size: 16px;
  margin-right: 12px;
  min-width: 140px;
`;

const Text = styled.div<{
  center?: boolean;
}>`
  white-space: pre-line;
  font-size: 15px;
  line-height: 30px;
  text-align: ${({ center }) => (center ? "center" : "left")};
  padding: ${({ center }) => (center ? "20px 30px" : "0 0 20px 0")};
  display: flex;
  justify-content: center;
  align-items: center;
`;

export interface ConfirmationModalProps {
  onClose: () => void;
  title: string;
  text: string;
  submitButtonText: string;
  onSubmit: () => void;
  submitButtonDataId?: string;
  cancelButtonText?: string;
  center?: boolean;
  contentValues?: any;
  loading?: boolean;
  buttonReverse?: boolean;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  onClose,
  title,
  text,
  center,
  onSubmit,
  contentValues,
  submitButtonText,
  submitButtonDataId,
  cancelButtonText,
  loading,
  buttonReverse,
}) => {
  const { isLoading, startAction } = useLoadingState();
  const onSubmitBtnClick = () => startAction({ action: () => onSubmit() });
  return (
    <Modal onClose={onClose} title={<FormattedMessage id={title} />}>
      <Content>
        <Text center={center}>
          <FormattedMessage id={text} values={contentValues ?? {}} />
        </Text>
        <ButtonContent reverse={buttonReverse}>
          <ButtonWithMargin onClick={onClose} type="button" disabled={loading || isLoading} secondary={buttonReverse}>
            <FormattedMessage id={cancelButtonText ?? "form.cancel"} />
          </ButtonWithMargin>
          <ButtonLoadingContainer
            onClick={onSubmitBtnClick}
            secondary={!buttonReverse}
            data-id={submitButtonDataId}
            isLoading={loading || isLoading}
          >
            <FormattedMessage id={submitButtonText} />
          </ButtonLoadingContainer>
        </ButtonContent>
      </Content>
    </Modal>
  );
};
