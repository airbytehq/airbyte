import React, { memo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Cell } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { RadioButton } from "components/ui/RadioButton";
import { Switch } from "components/ui/Switch";
import { Tooltip } from "components/ui/Tooltip";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { useExperiment } from "hooks/services/Experiment";
import { equal } from "utils/objects";
import { useTranslateDataType } from "utils/useTranslateDataType";

import DataTypeCell from "./DataTypeCell";
import { pathDisplayName } from "./PathPopout";
import { NameContainer, SyncCheckboxContainer } from "./styles";

interface FieldRowProps {
  isPrimaryKeyEnabled: boolean;
  isCursorEnabled: boolean;
  isSelected: boolean;
  onPrimaryKeyChange: (pk: string[]) => void;
  onCursorChange: (cs: string[]) => void;
  onToggleFieldSelected: (fieldPath: string[], isSelected: boolean) => void;
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
  onToggleFieldSelected,
  field,
  config,
  isCursorEnabled,
  isPrimaryKeyEnabled,
  isSelected,
}) => {
  const isColumnSelectionEnabled = useExperiment("connection.columnSelection", false);
  const dataType = useTranslateDataType(field);
  const name = pathDisplayName(field.path);

  const isCursor = equal(config?.cursorField, field.path);
  const isPrimaryKey = !!config?.primaryKey?.some((p) => equal(p, field.path));
  const isNestedField = SyncSchemaFieldObject.isNestedField(field);

  return (
    <>
      {isColumnSelectionEnabled && (
        <Cell flex={0}>
          <SyncCheckboxContainer>
            {!isNestedField && (
              <Switch size="sm" checked={isSelected} onChange={() => onToggleFieldSelected(field.path, !isSelected)} />
            )}
            {isNestedField && (
              <Tooltip control={<Switch size="sm" disabled checked={isSelected} />}>
                <FormattedMessage id="form.field.sync.nestedFieldTooltip" values={{ fieldName: field.path[0] }} />
              </Tooltip>
            )}
          </SyncCheckboxContainer>
        </Cell>
      )}
      {isColumnSelectionEnabled && (
        <Cell ellipsis flex={1.5}>
          <span title={name}>{name}</span>
        </Cell>
      )}
      {!isColumnSelectionEnabled && (
        <FirstCell ellipsis flex={1.5}>
          <NameContainer title={name}>{name}</NameContainer>
        </FirstCell>
      )}
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
