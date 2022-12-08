import React, { useCallback } from "react";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration, SelectedFieldInfo } from "core/request/AirbyteClient";

import { FieldHeader } from "./FieldHeader";
import { FieldRow } from "./FieldRow";
import { pathDisplayName } from "./PathPopout";
import styles from "./StreamFieldTable.module.scss";
import { TreeRowWrapper } from "./TreeRowWrapper";

interface StreamFieldTableProps {
  config: AirbyteStreamConfiguration | undefined;
  onCursorSelect: (cursorPath: string[]) => void;
  onFirstFieldDeselected: (fieldName: string) => void;
  onPkSelect: (pkPath: string[]) => void;
  onSelectedFieldsUpdate: (selectedFields: SelectedFieldInfo[]) => void;
  onAllFieldsSelected: () => void;
  shouldDefineCursor: boolean;
  shouldDefinePk: boolean;
  syncSchemaFields: SyncSchemaField[];
  numberOfFieldsInStream: number;
}

export const StreamFieldTable: React.FC<StreamFieldTableProps> = ({
  config,
  onCursorSelect,
  onFirstFieldDeselected,
  onPkSelect,
  onSelectedFieldsUpdate,
  onAllFieldsSelected,
  shouldDefineCursor,
  shouldDefinePk,
  syncSchemaFields,
  numberOfFieldsInStream,
}) => {
  const handleFieldToggle = (fieldName: string, isSelected: boolean) => {
    const previouslySelectedFields = config?.selectedFields || [];

    if (!config?.fieldSelectionEnabled && !isSelected) {
      onFirstFieldDeselected(fieldName);
    } else if (isSelected && previouslySelectedFields.length === numberOfFieldsInStream - 1) {
      // In this case we are selecting the only unselected field
      onAllFieldsSelected();
    } else if (isSelected) {
      onSelectedFieldsUpdate([...previouslySelectedFields, { fieldName }]);
    } else {
      onSelectedFieldsUpdate(previouslySelectedFields.filter((f) => f.fieldName !== fieldName) || []);
    }
  };

  const isFieldSelected = useCallback(
    (field: SyncSchemaField): boolean => {
      // All fields are implicitly selected if field selection is disabled
      if (!config?.fieldSelectionEnabled) {
        return true;
      }

      // path[0] is the top-level field name for all nested fields
      return !!config?.selectedFields?.find((sf) => sf.fieldName === field.path[0]);
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
