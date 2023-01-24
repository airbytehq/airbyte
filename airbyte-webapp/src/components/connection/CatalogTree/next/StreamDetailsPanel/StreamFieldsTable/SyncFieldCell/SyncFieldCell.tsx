import { useCallback } from "react";
import { FormattedMessage } from "react-intl";

import { CheckBox } from "components/ui/CheckBox";
import { Tooltip } from "components/ui/Tooltip";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";
import { SyncMode, DestinationSyncMode } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

interface SyncFieldCellProps {
  field: SyncSchemaField;
  checkIsCursor: (path: string[]) => boolean;
  checkIsChildFieldCursor: (path: string[]) => boolean;
  checkIsPrimaryKey: (path: string[]) => boolean;
  checkIsChildFieldPrimaryKey: (path: string[]) => boolean;
  isFieldSelected: boolean;
  handleFieldToggle: (fieldPath: string[], isSelected: boolean) => void;
  syncMode?: SyncMode;
  destinationSyncMode?: DestinationSyncMode;
}

export const SyncFieldCell: React.FC<SyncFieldCellProps> = ({
  checkIsCursor,
  checkIsChildFieldCursor,
  checkIsPrimaryKey,
  checkIsChildFieldPrimaryKey,
  isFieldSelected,
  field,
  handleFieldToggle,
  syncMode,
  destinationSyncMode,
}) => {
  const { mode } = useConnectionFormService();
  const isNestedField = SyncSchemaFieldObject.isNestedField(field);
  const isCursor = checkIsCursor(field.path);
  const isChildFieldCursor = checkIsChildFieldCursor(field.path);
  const isPrimaryKey = checkIsPrimaryKey(field.path);
  const isChildFieldPrimaryKey = checkIsChildFieldPrimaryKey(field.path);
  const isDisabled =
    mode === "readonly" ||
    (syncMode === SyncMode.incremental && (isCursor || isChildFieldCursor)) ||
    (destinationSyncMode === DestinationSyncMode.append_dedup && (isPrimaryKey || isChildFieldPrimaryKey)) ||
    isNestedField;
  const showTooltip = isDisabled && mode !== "readonly";

  const renderDisabledReasonMessage = useCallback(() => {
    if (isNestedField) {
      return <FormattedMessage id="form.field.sync.nestedFieldTooltip" values={{ fieldName: field.path[0] }} />;
    }
    if (isPrimaryKey || isChildFieldPrimaryKey) {
      return <FormattedMessage id="form.field.sync.primaryKeyTooltip" />;
    }
    if (isCursor || isChildFieldCursor) {
      return <FormattedMessage id="form.field.sync.cursorFieldTooltip" />;
    }
    return null;
  }, [isCursor, isChildFieldCursor, isPrimaryKey, isChildFieldPrimaryKey, isNestedField, field.path]);

  return (
    <>
      {!showTooltip && (
        <CheckBox
          checkboxSize="sm"
          checked={isFieldSelected}
          disabled={isDisabled}
          onChange={() => handleFieldToggle(field.path, !isFieldSelected)}
        />
      )}
      {showTooltip && (
        <Tooltip control={<CheckBox checkboxSize="sm" disabled checked={isFieldSelected} readOnly />}>
          {renderDisabledReasonMessage()}
        </Tooltip>
      )}
    </>
  );
};
