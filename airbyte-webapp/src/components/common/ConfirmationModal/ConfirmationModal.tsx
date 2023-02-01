import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";
import { Modal } from "components/ui/Modal";

import styles from "./ConfirmationModal.module.scss";
import useLoadingState from "../../../hooks/useLoadingState";

export interface ConfirmationModalProps {
  onClose: () => void;
  title: string;
  text: string;
  textValues?: Record<string, string>;
  submitButtonText: string;
  onSubmit: () => void;
  submitButtonDataId?: string;
  cancelButtonText?: string;
  additionalContent?: React.ReactNode;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  onClose,
  title,
  text,
  additionalContent,
  textValues,
  onSubmit,
  submitButtonText,
  submitButtonDataId,
  cancelButtonText,
}) => {
  const { isLoading, startAction } = useLoadingState();
  const onSubmitBtnClick = () => startAction({ action: () => onSubmit() });

  return (
    <Modal onClose={onClose} title={<FormattedMessage id={title} />} testId="confirmationModal">
      <div className={styles.content}>
        <FormattedMessage id={text} values={textValues} />
        {additionalContent}
        <div className={styles.buttonContent}>
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
        </div>
      </div>
    </Modal>
  );
};
