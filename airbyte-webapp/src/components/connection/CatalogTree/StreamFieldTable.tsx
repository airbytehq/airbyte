import isEqual from "lodash/isEqual";
import React, { useCallback } from "react";

import { SyncSchemaField } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

import { FieldHeader } from "./FieldHeader";
import { FieldRow } from "./FieldRow";
import { IndexerType, pathDisplayName } from "./PathPopout";
import styles from "./StreamFieldTable.module.scss";
import { TreeRowWrapper } from "./TreeRowWrapper";

interface StreamFieldTableProps {
  config: AirbyteStreamConfiguration | undefined;
  onCursorSelect: (cursorPath: string[]) => void;
  onPkSelect: (pkPath: string[]) => void;
  handleFieldToggle: (fieldPath: string[], isSelected: boolean) => void;
  cursorIndexerType: IndexerType;
  primaryKeyIndexerType: IndexerType;
  syncSchemaFields: SyncSchemaField[];
  shouldDefinePrimaryKey: boolean;
  shouldDefineCursor: boolean;
}

export const StreamFieldTable: React.FC<StreamFieldTableProps> = ({
  config,
  onCursorSelect,
  onPkSelect,
  handleFieldToggle,
  cursorIndexerType,
  primaryKeyIndexerType,
  syncSchemaFields,
  shouldDefinePrimaryKey,
  shouldDefineCursor,
}) => {
  const isFieldSelected = useCallback(
    (field: SyncSchemaField): boolean => {
      // All fields are implicitly selected if field selection is disabled
      if (!config?.fieldSelectionEnabled) {
        return true;
      }

      // Nested fields cannot currently be individually deselected, so we can just check whether the top-level field has been selected
      return !!config?.selectedFields?.find((f) => isEqual(f.fieldPath, [field.path[0]]));
    },
    [config]
  );

  return (
    <div className={styles.container}>
      <TreeRowWrapper noBorder>
        <FieldHeader />
      </TreeRowWrapper>
      <div className={styles.rowsContainer}>
        {syncSchemaFields.map((field) => (
          <TreeRowWrapper depth={1} key={pathDisplayName(field.path)}>
            <FieldRow
              field={field}
              config={config}
              cursorIndexerType={cursorIndexerType}
              primaryKeyIndexerType={primaryKeyIndexerType}
              onPrimaryKeyChange={onPkSelect}
              onCursorChange={onCursorSelect}
              onToggleFieldSelected={handleFieldToggle}
              isSelected={isFieldSelected(field)}
              shouldDefinePrimaryKey={shouldDefinePrimaryKey}
              shouldDefineCursor={shouldDefineCursor}
            />
          </TreeRowWrapper>
        ))}
      </div>
    </div>
  );
};
