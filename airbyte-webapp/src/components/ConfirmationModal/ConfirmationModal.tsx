import React from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Button } from "components/ui/Button";
import { Modal } from "components/ui/Modal";

import useLoadingState from "../../hooks/useLoadingState";
import styles from "./ConfirmationModal.module.scss";

const Content = styled.div`
  width: 585px;
  font-size: 14px;
  padding: 25px;
  white-space: pre-line;
`;

const ButtonContent = styled.div`
  margin-top: 26px;
  display: flex;
  justify-content: flex-end;
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
          <Button
            className={styles.buttonWithMargin}
            onClick={onClose}
            type="button"
            variant="secondary"
            disabled={isLoading}
          >
            <FormattedMessage id={cancelButtonText ?? "form.cancel"} />
          </Button>
          <Button variant="danger" onClick={onSubmitBtnClick} data-id={submitButtonDataId} isLoading={isLoading}>
            <FormattedMessage id={submitButtonText} />
          </Button>
        </ButtonContent>
      </Content>
    </Modal>
  );
};
