import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";

import { pathDisplayName } from "../PathPopout";
import { TreeRowWrapper } from "../TreeRowWrapper";
import { StreamFieldsTableHeader } from "./StreamFieldsTableHeader";
import { StreamFieldsTableRow } from "./StreamFieldsTableRow";

export interface StreamFieldsTableProps {
  config?: AirbyteStreamConfiguration;
  onCursorSelect: (cursorPath: string[]) => void;
  onPkSelect: (pkPath: string[]) => void;
  shouldDefinePk: boolean;
  shouldDefineCursor: boolean;
  syncSchemaFields: SyncSchemaField[];
}

export const StreamFieldsTable: React.FC<StreamFieldsTableProps> = ({
  config,
  onPkSelect,
  onCursorSelect,
  shouldDefineCursor,
  shouldDefinePk,
  syncSchemaFields,
}) => {
  return (
    <>
      <TreeRowWrapper noBorder>
        <StreamFieldsTableHeader />
      </TreeRowWrapper>
      {syncSchemaFields.map((field) => (
        <TreeRowWrapper depth={1} key={pathDisplayName(field.path)}>
          <StreamFieldsTableRow
            field={field}
            config={config}
            isPrimaryKeyEnabled={shouldDefinePk && SyncSchemaFieldObject.isPrimitive(field)}
            isCursorEnabled={shouldDefineCursor && SyncSchemaFieldObject.isPrimitive(field)}
            onPrimaryKeyChange={onPkSelect}
            onCursorChange={onCursorSelect}
          />
        </TreeRowWrapper>
      ))}
    </>
  );
};
