import React, { memo } from "react";
import styled from "styled-components";

import { Cell } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { RadioButton } from "components/ui/RadioButton";

import { SyncSchemaField } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { equal } from "utils/objects";
import { useTranslateDataType } from "utils/useTranslateDataType";

import DataTypeCell from "./DataTypeCell";
import { pathDisplayName } from "./PathPopout";
import { SyncCheckboxContainer } from "./styles";

interface FieldRowProps {
  isPrimaryKeyEnabled: boolean;
  isCursorEnabled: boolean;
  isSelected: boolean;
  onPrimaryKeyChange: (pk: string[]) => void;
  onCursorChange: (cs: string[]) => void;
  onToggleFieldSelected: (fieldName: string, isSelected: boolean) => void;
  field: SyncSchemaField;
  config: AirbyteStreamConfiguration | undefined;
}

const LastCell = styled(Cell)`
  margin-right: -10px;
`;

const FieldRowInner: React.FC<FieldRowProps> = ({
  onPrimaryKeyChange,
  onCursorChange,
  onToggleFieldSelected,
  field,
  config,
  isCursorEnabled,
  isPrimaryKeyEnabled,
  isSelected,
}) => {
  const dataType = useTranslateDataType(field);
  const name = pathDisplayName(field.path);

  const isCursor = equal(config?.cursorField, field.path);
  const isPrimaryKey = !!config?.primaryKey?.some((p) => equal(p, field.path));
  console.log("fieldrow rendered");
  return (
    <>
      <Cell flex={0}>
        <SyncCheckboxContainer title={name}>
          <CheckBox checked={isSelected} onChange={() => onToggleFieldSelected(field.cleanedName, !isSelected)} />
        </SyncCheckboxContainer>
      </Cell>
      <Cell ellipsis flex={1.5}>
        {name}
      </Cell>
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
