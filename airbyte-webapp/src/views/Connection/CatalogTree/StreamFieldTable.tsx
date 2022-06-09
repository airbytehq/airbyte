import React from "react";
import styled from "styled-components";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { equal } from "utils/objects";

import { AirbyteStreamConfiguration } from "../../../core/request/AirbyteClient";
import { pathDisplayName } from "./components/PathPopout";
import { TreeRowWrapper } from "./components/TreeRowWrapper";
import { FieldHeader } from "./FieldHeader";
import { FieldRow } from "./FieldRow";

const RowsContainer = styled.div`
  background: ${({ theme }) => theme.whiteColor};
  border-radius: 8px;
  margin: 0 10px 5px 10px;
`;

interface StreamFieldTableProps {
  syncSchemaFields: SyncSchemaField[];
  config: AirbyteStreamConfiguration | undefined;
  shouldDefinePk: boolean;
  shouldDefineCursor: boolean;
  onCursorSelect: (cursorPath: string[]) => void;
  onPkSelect: (pkPath: string[]) => void;
}

export const StreamFieldTable: React.FC<StreamFieldTableProps> = (props) => {
  const { config } = props;

  const isCursor = (field: SyncSchemaField): boolean => equal(config?.cursorField, field.path);

  const isPrimaryKey = (field: SyncSchemaField): boolean => !!config?.primaryKey?.some((p) => equal(p, field.path));

  return (
    <>
      <TreeRowWrapper noBorder>
        <FieldHeader />
      </TreeRowWrapper>
      <RowsContainer>
        {props.syncSchemaFields.map((field) => (
          <TreeRowWrapper depth={1} key={pathDisplayName(field.path)}>
            <FieldRow
              path={field.path}
              name={pathDisplayName(field.path)}
              type={field.type}
              destinationName={field.cleanedName}
              isCursor={isCursor(field)}
              isPrimaryKey={isPrimaryKey(field)}
              isPrimaryKeyEnabled={props.shouldDefinePk && SyncSchemaFieldObject.isPrimitive(field)}
              isCursorEnabled={props.shouldDefineCursor && SyncSchemaFieldObject.isPrimitive(field)}
              onPrimaryKeyChange={props.onPkSelect}
              onCursorChange={props.onCursorSelect}
            />
          </TreeRowWrapper>
        ))}
      </RowsContainer>
    </>
  );
};
