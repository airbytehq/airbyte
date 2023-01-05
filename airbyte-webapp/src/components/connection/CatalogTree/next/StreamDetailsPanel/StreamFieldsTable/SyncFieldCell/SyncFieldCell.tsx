import { useCallback } from "react";
import { FormattedMessage } from "react-intl";

import { CheckBox } from "components/ui/CheckBox";
import { Tooltip } from "components/ui/Tooltip";

import { SyncSchemaField, SyncSchemaFieldObject } from "core/domain/catalog";

interface SyncFieldCellProps {
  field: SyncSchemaField;
  checkIsCursor: (path: string[]) => boolean;
  checkIsPrimaryKey: (path: string[]) => boolean;
  isSelected: boolean;
  handleFieldToggle: (fieldPath: string[], isSelected: boolean) => void;
  shouldDefineCursor: boolean;
  shouldDefinePrimaryKey: boolean;
}

export const SyncFieldCell: React.FC<SyncFieldCellProps> = ({
  checkIsCursor,
  checkIsPrimaryKey,
  isSelected,
  field,
  handleFieldToggle,
  shouldDefineCursor,
  shouldDefinePrimaryKey,
}) => {
  const isNestedField = SyncSchemaFieldObject.isNestedField(field);
  const isCursor = checkIsCursor(field.path);
  const isPrimaryKey = checkIsPrimaryKey(field.path);
  const isDisabled = (shouldDefineCursor && isCursor) || (shouldDefinePrimaryKey && isPrimaryKey) || isNestedField;

  const renderDisabledReasonMessage = useCallback(() => {
    if (isNestedField) {
      return <FormattedMessage id="form.field.sync.nestedFieldTooltip" values={{ fieldName: field.path[0] }} />;
    }
    if (isPrimaryKey) {
      return <FormattedMessage id="form.field.sync.primaryKeyTooltip" />;
    }
    if (isCursor) {
      return <FormattedMessage id="form.field.sync.cursorFieldTooltip" />;
    }
    return null;
  }, [isCursor, isPrimaryKey, isNestedField, field.path]);

  return (
    <>
      {!isDisabled && (
        <CheckBox checkboxSize="sm" checked={isSelected} onChange={() => handleFieldToggle(field.path, !isSelected)} />
      )}
      {isDisabled && (
        <Tooltip control={<CheckBox checkboxSize="sm" disabled checked={isSelected} />}>
          {renderDisabledReasonMessage()}
        </Tooltip>
      )}
    </>
  );
};
