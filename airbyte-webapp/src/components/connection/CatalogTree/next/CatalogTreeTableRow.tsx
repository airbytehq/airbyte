import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { ArrowRightIcon } from "components/icons/ArrowRightIcon";
import { Row } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { Switch } from "components/ui/Switch";
import { Text } from "components/ui/Text";

import { useBulkEditSelect } from "hooks/services/BulkEdit/BulkEditService";

import { CatalogTreeTableCell } from "./CatalogTreeTableCell";
import styles from "./CatalogTreeTableRow.module.scss";
import { CatalogTreeTableRowIcon } from "./CatalogTreeTableRowIcon";
import { StreamPathSelect } from "./StreamPathSelect";
import { SyncModeSelect } from "./SyncModeSelect";
import { useCatalogTreeTableRowProps } from "./useCatalogTreeTableRowProps";
import { StreamHeaderProps } from "../StreamHeader";

export const CatalogTreeTableRow: React.FC<StreamHeaderProps> = ({
  stream,
  destName,
  destNamespace,
  onSelectSyncMode,
  onSelectStream,
  availableSyncModes,
  pkType,
  onPrimaryKeyChange,
  onCursorChange,
  primitiveFields,
  cursorType,
  // isRowExpanded,
  fields,
  onExpand,
  disabled,
  configErrors,
}) => {
  const { primaryKey, cursorField, syncMode, destinationSyncMode } = stream.config ?? {};
  const { defaultCursorField } = stream.stream ?? {};
  const syncSchema = useMemo(
    () => ({
      syncMode,
      destinationSyncMode,
    }),
    [syncMode, destinationSyncMode]
  );

  const [isSelected, selectForBulkEdit] = useBulkEditSelect(stream.id);

  const paths = useMemo(() => primitiveFields.map((field) => field.path), [primitiveFields]);
  const fieldCount = fields?.length ?? 0;
  const onRowClick = fieldCount > 0 ? () => onExpand() : undefined;

  const { streamHeaderContentStyle, pillButtonVariant } = useCatalogTreeTableRowProps(stream);

  return (
    <Row onClick={onRowClick} className={streamHeaderContentStyle}>
      <CatalogTreeTableCell size="small" className={styles.streamRowCheckboxCell}>
        {!disabled && (
          <>
            <CatalogTreeTableRowIcon stream={stream} />
            <CheckBox checked={isSelected} onChange={selectForBulkEdit} />
          </>
        )}
      </CatalogTreeTableCell>
      <CatalogTreeTableCell size="small">
        <Switch size="sm" checked={stream.config?.selected} onChange={onSelectStream} disabled={disabled} />
      </CatalogTreeTableCell>
      {/* <Cell>{fieldCount}</Cell> */}
      <CatalogTreeTableCell withTooltip>
        <Text size="md" className={styles.cellText}>
          {stream.stream?.namespace || <FormattedMessage id="form.noNamespace" />}
        </Text>
      </CatalogTreeTableCell>
      <CatalogTreeTableCell withTooltip>
        <Text size="md" className={styles.cellText}>
          {stream.stream?.name}
        </Text>
      </CatalogTreeTableCell>
      <CatalogTreeTableCell size="large">
        {disabled ? (
          <Text size="md" className={styles.cellText}>
            {syncSchema.syncMode}
          </Text>
        ) : (
          // todo: SyncModeSelect should probably have a Tooltip, append/dedupe ends up ellipsing
          <SyncModeSelect
            options={availableSyncModes}
            onChange={onSelectSyncMode}
            value={syncSchema}
            variant={pillButtonVariant}
          />
        )}
      </CatalogTreeTableCell>
      <CatalogTreeTableCell>
        {cursorType && (
          <StreamPathSelect
            pathType={cursorType}
            paths={paths}
            path={cursorType === "sourceDefined" ? defaultCursorField : cursorField}
            onPathChange={onCursorChange}
            variant={pillButtonVariant}
            hasError={!!configErrors?.cursorField}
          />
        )}
      </CatalogTreeTableCell>
      <CatalogTreeTableCell withTooltip={pkType === "sourceDefined"}>
        {pkType && (
          <StreamPathSelect
            pathType={pkType}
            paths={paths}
            path={primaryKey}
            isMulti
            onPathChange={onPrimaryKeyChange}
            variant={pillButtonVariant}
            hasError={!!configErrors?.primaryKey}
          />
        )}
      </CatalogTreeTableCell>
      <CatalogTreeTableCell size="xsmall">
        <ArrowRightIcon />
      </CatalogTreeTableCell>
      <CatalogTreeTableCell withTooltip>
        <Text size="md" className={styles.cellText}>
          {destNamespace}
        </Text>
      </CatalogTreeTableCell>
      <CatalogTreeTableCell withTooltip>
        <Text size="md" className={styles.cellText}>
          {destName}
        </Text>
      </CatalogTreeTableCell>
    </Row>
  );
};
