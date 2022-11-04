import React, { useCallback } from "react";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";

import { H5 } from "components/base/Titles";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";

import { useConfirmationModalService } from "hooks/services/ConfirmationModal";

import styles from "./DeleteBlock.module.scss";

interface IProps {
  type: "source" | "destination" | "connection";
  onDelete: () => Promise<unknown>;
}

export const DeleteBlock: React.FC<IProps> = ({ type, onDelete }) => {
  const { openConfirmationModal, closeConfirmationModal } = useConfirmationModalService();
  const navigate = useNavigate();

  const onDeleteButtonClick = useCallback(() => {
    openConfirmationModal({
      text: `tables.${type}DeleteModalText`,
      title: `tables.${type}DeleteConfirm`,
      submitButtonText: "form.delete",
      onSubmit: async () => {
        await onDelete();
        closeConfirmationModal();
        navigate("../..");
      },
      submitButtonDataId: "delete",
    });
  }, [closeConfirmationModal, onDelete, openConfirmationModal, navigate, type]);

  return (
    <Card className={styles.deleteBlock}>
      <div className={styles.text}>
        <H5 bold>
          <FormattedMessage id={`tables.${type}Delete.title`} />
        </H5>
        <FormattedMessage id={`tables.${type}DataDelete`} />
      </div>
      <Button variant="danger" onClick={onDeleteButtonClick} data-id="open-delete-modal">
        <FormattedMessage id={`tables.${type}Delete`} />
      </Button>
    </Card>
  );
};
