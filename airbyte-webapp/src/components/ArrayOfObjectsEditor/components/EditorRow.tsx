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

  const body = (
    <div className={styles.body}>
      <div className={styles.name}>{name || id}</div>
      <div className={styles.actions}>
        <Button
          type="button"
          iconOnly
          arial-label={formatMessage({ id: "form.edit" })}
          onClick={() => onEdit(id)}
          disabled={disabled}
        >
          <PencilIcon />
        </Button>
        <Button
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

  return <div className={styles.container}>{description ? <ToolTip control={body}>{description}</ToolTip> : body}</div>;
};
