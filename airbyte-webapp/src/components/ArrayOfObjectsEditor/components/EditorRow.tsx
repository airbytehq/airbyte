import React from "react";
import { useIntl } from "react-intl";

import { Button } from "components";
import { CrossIcon } from "components/icons/CrossIcon";
import { PencilIcon } from "components/icons/PencilIcon";
import ToolTip from "components/ToolTip";

import styles from "./EditorRow.module.scss";

interface EditorRowProps {
  name?: React.ReactNode;
  description?: React.ReactNode;
  id: number;
  onEdit: (id: number) => void;
  onRemove: (id: number) => void;
  disabled?: boolean;
}

export const EditorRow: React.FC<EditorRowProps> = ({ name, id, description, onEdit, onRemove, disabled }) => {
  const { formatMessage } = useIntl();

  const row = (
    <div className={styles.container}>
      <div className={styles.name}>{name || id}</div>
      <div className={styles.actions}>
        <Button
          className={styles.iconButton}
          type="button"
          iconOnly
          arial-label={formatMessage({ id: "form.edit" })}
          onClick={() => onEdit(id)}
          disabled={disabled}
        >
          <PencilIcon />
        </Button>
        <Button
          className={styles.iconButton}
          type="button"
          iconOnly
          aria-label={formatMessage({ id: "form.delete" })}
          onClick={() => onRemove(id)}
          disabled={disabled}
        >
          <CrossIcon />
        </Button>
      </div>
    </div>
  );

  return description ? <ToolTip control={row}>{description}</ToolTip> : row;
};
