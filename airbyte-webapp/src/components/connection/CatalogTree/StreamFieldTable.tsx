import isEqual from "lodash/isEqual";
import React, { useCallback } from "react";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

import { FieldHeader } from "./FieldHeader";
import { FieldRow } from "./FieldRow";
import { pathDisplayName } from "./PathPopout";
import styles from "./StreamFieldTable.module.scss";
import { TreeRowWrapper } from "./TreeRowWrapper";

interface StreamFieldTableProps {
  config: AirbyteStreamConfiguration | undefined;
  onCursorSelect: (cursorPath: string[]) => void;
  onPkSelect: (pkPath: string[]) => void;
  handleFieldToggle: (fieldPath: string[], isSelected: boolean) => void;
  shouldDefineCursor: boolean;
  shouldDefinePk: boolean;
  syncSchemaFields: SyncSchemaField[];
}

export const StreamFieldTable: React.FC<StreamFieldTableProps> = ({
  config,
  onCursorSelect,
  onPkSelect,
  handleFieldToggle,
  shouldDefineCursor,
  shouldDefinePk,
  syncSchemaFields,
}) => {
  const isFieldSelected = useCallback(
    (field: SyncSchemaField): boolean => {
      // All fields are implicitly selected if field selection is disabled
      if (!config?.fieldSelectionEnabled) {
        return true;
      }

      // path[0] is the top-level field name for all nested fields
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
              isPrimaryKeyEnabled={shouldDefinePk && SyncSchemaFieldObject.isPrimitive(field)}
              isCursorEnabled={shouldDefineCursor && SyncSchemaFieldObject.isPrimitive(field)}
              onPrimaryKeyChange={onPkSelect}
              onCursorChange={onCursorSelect}
              onToggleFieldSelected={handleFieldToggle}
              isSelected={isFieldSelected(field)}
            />
          </TreeRowWrapper>
        ))}
      </div>
    </div>
  );
};
