import React, { memo, useCallback } from "react";
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
import { IndexerType, pathDisplayName } from "./PathPopout";
import { NameContainer, SyncCheckboxContainer } from "./styles";

interface FieldRowProps {
  cursorIndexerType: IndexerType;
  primaryKeyIndexerType: IndexerType;
  isSelected: boolean;
  onPrimaryKeyChange: (pk: string[]) => void;
  onCursorChange: (cs: string[]) => void;
  onToggleFieldSelected: (fieldPath: string[], isSelected: boolean) => void;
  field: SyncSchemaField;
  config: AirbyteStreamConfiguration | undefined;
  shouldDefinePrimaryKey: boolean;
  shouldDefineCursor: boolean;
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
  cursorIndexerType,
  primaryKeyIndexerType,
  isSelected,
  shouldDefinePrimaryKey,
  shouldDefineCursor,
}) => {
  const isColumnSelectionEnabled = useExperiment("connection.columnSelection", false);
  const dataType = useTranslateDataType(field);
  const name = pathDisplayName(field.path);

  const isCursor = equal(config?.cursorField, field.path);
  const isPrimaryKey = !!config?.primaryKey?.some((p) => equal(p, field.path));
  const isNestedField = SyncSchemaFieldObject.isNestedField(field);
  // The indexer type tells us whether a cursor or pk is user-defined, source-defined or not required (null)
  const fieldSelectionDisabled =
    (cursorIndexerType !== null && isCursor) || (primaryKeyIndexerType !== null && isPrimaryKey) || isNestedField;

  const renderDisabledReasonMessage = useCallback(() => {
    if (isNestedField) {
      return <FormattedMessage id="form.field.sync.nestedFieldTooltip" values={{ fieldName: field.path[0] }} />;
    }
    if (primaryKeyIndexerType !== null && isPrimaryKey) {
      return <FormattedMessage id="form.field.sync.primaryKeyTooltip" />;
    }
    if (cursorIndexerType !== null && isCursor) {
      return <FormattedMessage id="form.field.sync.cursorFieldTooltip" />;
    }
    return null;
  }, [isCursor, isPrimaryKey, isNestedField, field.path, cursorIndexerType, primaryKeyIndexerType]);

  return (
    <>
      {isColumnSelectionEnabled && (
        <Cell flex={0}>
          <SyncCheckboxContainer>
            <Tooltip
              disabled={!fieldSelectionDisabled}
              control={
                <Switch
                  size="sm"
                  disabled={fieldSelectionDisabled}
                  checked={isSelected}
                  onChange={() => onToggleFieldSelected(field.path, !isSelected)}
                />
              }
            >
              {renderDisabledReasonMessage()}
            </Tooltip>
          </SyncCheckboxContainer>
        </Cell>
      )}
      {isColumnSelectionEnabled && (
        <Cell ellipsis flex={1.5}>
          <span title={name} data-testid="nameCell">
            {name}
          </span>
        </Cell>
      )}
      {!isColumnSelectionEnabled && (
        <FirstCell ellipsis flex={1.5}>
          <NameContainer title={name} data-testid="nameCell">
            {name}
          </NameContainer>
        </FirstCell>
      )}
      <DataTypeCell data-testid="dataTypeCell">{dataType}</DataTypeCell>
      <Cell>
        {shouldDefineCursor && <RadioButton checked={isCursor} onChange={() => onCursorChange(field.path)} />}
      </Cell>
      <Cell>
        {shouldDefinePrimaryKey && <CheckBox checked={isPrimaryKey} onChange={() => onPrimaryKeyChange(field.path)} />}
      </Cell>
      <LastCell ellipsis title={field.cleanedName} flex={1.5}>
        {field.cleanedName}
      </LastCell>
    </>
  );
};

export const FieldRow = memo(FieldRowInner);
