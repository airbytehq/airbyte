import React from "react";
import { FormattedMessage } from "react-intl";

import { H5 } from "components/base/Titles";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";

import { useDeleteModal } from "hooks/useDeleteModal";

import styles from "./DeleteBlock.module.scss";

interface IProps {
  type: "source" | "destination" | "connection";
  onDelete: () => Promise<unknown>;
  modalAdditionalContent?: React.ReactNode;
}

export const DeleteBlock: React.FC<IProps> = ({ type, onDelete }) => {
  const onDeleteButtonClick = useDeleteModal(type, onDelete);

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
