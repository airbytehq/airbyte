import React from "react";
import styled from "styled-components";

import {
  AirbyteStreamConfiguration,
  SyncSchemaField,
  SyncSchemaFieldObject,
} from "core/domain/catalog";
import { equal } from "utils/objects";
import { TreeRowWrapper } from "./components/TreeRowWrapper";
import { FieldHeader } from "./FieldHeader";
import { FieldRow } from "./FieldRow";

const RowsContainer = styled.div<{ depth?: number }>`
  background: ${({ theme }) => theme.whiteColor};
  border-radius: 8px;
  margin: 0
    ${({ depth = 0 }) => `${depth * 10}px ${depth * 5}px ${depth * 10}px`};
`;

type StreamFieldTableProps = {
  syncSchemaFields: SyncSchemaField[];
  config: AirbyteStreamConfiguration;
  shouldDefinePk: boolean;
  shouldDefineCursor: boolean;
  onCursorSelect: (cursorPath: string[]) => void;
  onPkSelect: (pkPath: string[]) => void;
};

export const StreamFieldTable: React.FC<StreamFieldTableProps> = (props) => {
  const { config } = props;

  const isCursor = (field: SyncSchemaField): boolean =>
    equal(config.cursorField, field.path);

  const isPrimaryKey = (field: SyncSchemaField): boolean => {
    const existIndex = config.primaryKey.findIndex((p) => equal(p, field.path));

    return existIndex !== -1;
  };

  return (
    <>
      <TreeRowWrapper noBorder>
        <FieldHeader depth={1} />
      </TreeRowWrapper>
      <RowsContainer depth={1}>
        {props.syncSchemaFields.map((field) => (
          <TreeRowWrapper depth={1} key={field.key}>
            <FieldRow
              depth={1}
              path={field.path}
              name={field.path.join(".")}
              type={field.type}
              destinationName={field.cleanedName}
              isCursor={isCursor(field)}
              isPrimaryKey={isPrimaryKey(field)}
              isPrimaryKeyEnabled={
                props.shouldDefinePk && SyncSchemaFieldObject.isPrimitive(field)
              }
              isCursorEnabled={
                props.shouldDefineCursor &&
                SyncSchemaFieldObject.isPrimitive(field)
              }
              onPrimaryKeyChange={props.onPkSelect}
              onCursorChange={props.onCursorSelect}
            />
          </TreeRowWrapper>
        ))}
      </RowsContainer>
    </>
  );
};
