import React from "react";
import { useIntl } from "react-intl";

import { CrossIcon } from "components/icons/CrossIcon";
import { PencilIcon } from "components/icons/PencilIcon";
import { Button } from "components/ui/Button";
import { Tooltip } from "components/ui/Tooltip";

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
          size="xs"
          type="button"
          variant="clear"
          arial-label={formatMessage({ id: "form.edit" })}
          onClick={() => onEdit(id)}
          disabled={disabled}
          icon={<PencilIcon />}
        />
        <Button
          size="xs"
          type="button"
          variant="clear"
          aria-label={formatMessage({ id: "form.delete" })}
          onClick={() => onRemove(id)}
          disabled={disabled}
          icon={<CrossIcon />}
        />
      </div>
    </div>
  );

  return (
    <div className={styles.container}>
      {description ? (
        <Tooltip control={body} placement="top">
          {description}
        </Tooltip>
      ) : (
        body
      )}
    </div>
  );
};
