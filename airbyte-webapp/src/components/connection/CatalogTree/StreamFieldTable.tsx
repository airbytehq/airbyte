import React from "react";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration, SelectedFieldInfo } from "core/request/AirbyteClient";

import { FieldHeader } from "./FieldHeader";
import { FieldRow } from "./FieldRow";
import { pathDisplayName } from "./PathPopout";
import styles from "./StreamFieldTable.module.scss";
import { TreeRowWrapper } from "./TreeRowWrapper";

interface StreamFieldTableProps {
  syncSchemaFields: SyncSchemaField[];
  config: AirbyteStreamConfiguration | undefined;
  shouldDefinePk: boolean;
  shouldDefineCursor: boolean;
  onCursorSelect: (cursorPath: string[]) => void;
  onPkSelect: (pkPath: string[]) => void;
  onSelectedFieldsUpdate: (selectedFields: SelectedFieldInfo[]) => void;
}

export const StreamFieldTable: React.FC<StreamFieldTableProps> = (props) => {
  const handleFieldToggle = (fieldName: string, isSelected: boolean) => {
    if (isSelected) {
      props.onSelectedFieldsUpdate([...(props.config?.selectedFields || []), { fieldName }]);
    } else {
      props.onSelectedFieldsUpdate(props.config?.selectedFields?.filter((f) => f.fieldName !== fieldName) || []);
    }
  };

  return (
    <div className={styles.container}>
      <TreeRowWrapper noBorder>
        <FieldHeader />
      </TreeRowWrapper>
      <div className={styles.rowsContainer}>
        {props.syncSchemaFields.map((field) => (
          <TreeRowWrapper depth={1} key={pathDisplayName(field.path)}>
            <FieldRow
              field={field}
              config={props.config}
              isPrimaryKeyEnabled={props.shouldDefinePk && SyncSchemaFieldObject.isPrimitive(field)}
              isCursorEnabled={props.shouldDefineCursor && SyncSchemaFieldObject.isPrimitive(field)}
              onPrimaryKeyChange={props.onPkSelect}
              onCursorChange={props.onCursorSelect}
              onToggleFieldSelected={handleFieldToggle}
              isSelected={!!props.config?.selectedFields?.find((sf) => sf.fieldName === field.cleanedName)}
            />
          </TreeRowWrapper>
        ))}
      </div>
    </div>
  );
};
