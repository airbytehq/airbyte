import React from "react";
import styled from "styled-components";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";

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
  return (
    <>
      <TreeRowWrapper noBorder>
        <FieldHeader />
      </TreeRowWrapper>
      <RowsContainer>
        {props.syncSchemaFields.map((field) => (
          <TreeRowWrapper depth={1} key={pathDisplayName(field.path)}>
            <FieldRow
              field={field}
              config={props.config}
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
