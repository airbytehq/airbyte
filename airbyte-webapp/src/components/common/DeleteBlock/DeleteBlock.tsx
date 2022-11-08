import React from "react";
import { FormattedMessage } from "react-intl";

import { H5 } from "components/base/Titles";
import { Button } from "components/ui/Button";
import { Card } from "components/ui/Card";

import styles from "./DeleteBlock.module.scss";
import { DeleteBlockProps } from "./interfaces";
import { useDeleteModal } from "./useDeleteModal";

export const DeleteBlock: React.FC<DeleteBlockProps> = ({ type, onDelete }) => {
  const { onDeleteButtonClick } = useDeleteModal({ type, onDelete });

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
