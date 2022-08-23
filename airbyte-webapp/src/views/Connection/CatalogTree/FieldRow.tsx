import React, { memo } from "react";
import styled from "styled-components";

import { Cell, CheckBox, RadioButton } from "components";

import { SyncSchemaField } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { equal } from "utils/objects";

import { useTranslateDataType } from "../../../utils/useTranslateDataType";
import DataTypeCell from "./components/DataTypeCell";
import { pathDisplayName } from "./components/PathPopout";
import { NameContainer } from "./styles";

interface FieldRowProps {
  isPrimaryKeyEnabled: boolean;
  isCursorEnabled: boolean;

  onPrimaryKeyChange: (pk: string[]) => void;
  onCursorChange: (cs: string[]) => void;
  field: SyncSchemaField;
  config: AirbyteStreamConfiguration | undefined;
}

const FirstCell = styled(Cell)`
  margin-left: -10px;
`;

const LastCell = styled(Cell)`
  margin-right: -10px;
`;

const FieldRowInner: React.FC<FieldRowProps> = ({
  onPrimaryKeyChange,
  onCursorChange,
  field,
  config,
  isCursorEnabled,
  isPrimaryKeyEnabled,
}) => {
  const dataType = useTranslateDataType(field);
  const name = pathDisplayName(field.path);

  const isCursor = equal(config?.cursorField, field.path);
  const isPrimaryKey = !!config?.primaryKey?.some((p) => equal(p, field.path));

  return (
    <>
      <FirstCell ellipsis flex={1.5}>
        <NameContainer title={name}>{name}</NameContainer>
      </FirstCell>
      <DataTypeCell>{dataType}</DataTypeCell>
      <Cell>{isCursorEnabled && <RadioButton checked={isCursor} onChange={() => onCursorChange(field.path)} />}</Cell>
      <Cell>
        {isPrimaryKeyEnabled && <CheckBox checked={isPrimaryKey} onChange={() => onPrimaryKeyChange(field.path)} />}
      </Cell>
      <LastCell ellipsis title={field.cleanedName} flex={1.5}>
        {field.cleanedName}
      </LastCell>
    </>
  );
};

export const FieldRow = memo(FieldRowInner);
