import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { LoadingButton } from "components";
import { Button } from "components/base/Button";
import Modal from "components/Modal";

import useLoadingState from "../../hooks/useLoadingState";

const Content = styled.div`
  width: 585px;
  font-size: 14px;
  line-height: 28px;
  padding: 25px;
  white-space: pre-line;
`;

const ButtonContent = styled.div`
  margin-top: 26px;
  display: flex;
  justify-content: flex-end;
`;

const ButtonWithMargin = styled(Button)`
  margin-right: 12px;
`;

export interface ConfirmationModalProps {
  onClose: () => void;
  title: string;
  text: string;
  submitButtonText: string;
  onSubmit: () => void;
  submitButtonDataId?: string;
  cancelButtonText?: string;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  onClose,
  title,
  text,
  onSubmit,
  submitButtonText,
  submitButtonDataId,
  cancelButtonText,
}) => {
  const { isLoading, startAction } = useLoadingState();
  const onSubmitBtnClick = () => startAction({ action: () => onSubmit() });

  return (
    <Modal onClose={onClose} title={<FormattedMessage id={title} />}>
      <Content>
        <FormattedMessage id={text} />
        <ButtonContent>
          <ButtonWithMargin onClick={onClose} type="button" secondary disabled={isLoading}>
            <FormattedMessage id={cancelButtonText ?? "form.cancel"} />
          </ButtonWithMargin>
          <LoadingButton danger onClick={onSubmitBtnClick} data-id={submitButtonDataId} isLoading={isLoading}>
            <FormattedMessage id={submitButtonText} />
          </LoadingButton>
        </ButtonContent>
      </Content>
    </Modal>
  );
};
