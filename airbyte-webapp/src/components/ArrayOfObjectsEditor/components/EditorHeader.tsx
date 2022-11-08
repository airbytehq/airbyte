import React from "react";
import { FormattedMessage } from "react-intl";

import { Button } from "components/ui/Button";

import { ConnectionFormMode } from "hooks/services/ConnectionForm/ConnectionFormService";

import styles from "./EditorHeader.module.scss";

interface EditorHeaderProps {
  mainTitle?: React.ReactNode;
  addButtonText?: React.ReactNode;
  itemsCount: number;
  onAddItem: () => void;
  mode?: ConnectionFormMode;
  disabled?: boolean;
}

const EditorHeader: React.FC<EditorHeaderProps> = ({
  itemsCount,
  onAddItem,
  mainTitle,
  addButtonText,
  mode,
  disabled,
}) => {
  return (
    <div className={styles.editorHeader}>
      {mainTitle || <FormattedMessage id="form.items" values={{ count: itemsCount }} />}
      {mode !== "readonly" && (
        <Button variant="secondary" type="button" onClick={onAddItem} data-testid="addItemButton" disabled={disabled}>
          {addButtonText || <FormattedMessage id="form.addItems" />}
        </Button>
      )}
    </div>
  );
};

export { EditorHeader };
