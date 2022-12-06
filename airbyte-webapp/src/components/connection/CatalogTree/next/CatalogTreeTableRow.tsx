import { faArrowRight, faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Cell, Row } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { Switch } from "components/ui/Switch";
import { Text } from "components/ui/Text";

import { useBulkEditSelect } from "hooks/services/BulkEdit/BulkEditService";

import { StreamHeaderProps } from "../StreamHeader";
import styles from "./CatalogTreeTableRow.module.scss";
import { StreamPathSelect } from "./StreamPathSelect";
import { SyncModeSelect } from "./SyncModeSelect";

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
  changedSelected,
  hasError,
  disabled,
}) => {
  const { primaryKey, cursorField, syncMode, destinationSyncMode } = stream.config ?? {};
  const isStreamEnabled = stream.config?.selected;

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

  const iconStyle = classnames(styles.icon, {
    [styles.plus]: isStreamEnabled,
    [styles.minus]: !isStreamEnabled,
  });

  const TableCell: React.FC<{ flex?: string; title?: string; className?: string }> = ({
    flex = "0 0 120px",
    title,
    className,
    children,
  }) => (
    <Cell flex={flex} title={title} className={className}>
      {children}
    </Cell>
  );

  const streamHeaderContentStyle = classnames(styles.streamHeaderContent, {
    [styles.enabledChange]: changedSelected && isStreamEnabled,
    [styles.disabledChange]: changedSelected && !isStreamEnabled,
    [styles.selected]: isSelected,
    [styles.error]: hasError,
    [styles.disabled]: !changedSelected && !isStreamEnabled,
  });

  return (
    <Row onClick={onRowClick} className={streamHeaderContentStyle}>
      {!disabled && (
        <div className={styles.streamRowCheckboxCell}>
          {changedSelected && (
            <div>
              {isStreamEnabled ? (
                <FontAwesomeIcon icon={faPlus} size="2x" className={iconStyle} />
              ) : (
                <FontAwesomeIcon icon={faMinus} size="2x" className={iconStyle} />
              )}
            </div>
          )}
          <CheckBox checked={isSelected} onChange={selectForBulkEdit} />
        </div>
      )}
      <TableCell flex="0 0 60px">
        <Switch small checked={stream.config?.selected} onChange={onSelectStream} disabled={disabled} />
      </TableCell>
      {/* <Cell>{fieldCount}</Cell> */}
      <TableCell title={stream.stream?.namespace || ""}>
        <Text size="md" className={styles.cellText}>
          {stream.stream?.namespace || <FormattedMessage id="form.noNamespace" />}
        </Text>
      </TableCell>
      <TableCell title={stream.stream?.name || ""}>
        <Text size="md" className={styles.cellText}>
          {stream.stream?.name}
        </Text>
      </TableCell>
      <TableCell flex="0 0 200px">
        {disabled ? (
          <Cell title={syncSchema.syncMode}>
            <Text size="md" className={styles.cellText}>
              {syncSchema.syncMode}
            </Text>
          </Cell>
        ) : (
          // todo: SyncModeSelect should probably have a Tooltip, append/dedupe ends up ellipsing
          <SyncModeSelect options={availableSyncModes} onChange={onSelectSyncMode} value={syncSchema} />
        )}
      </TableCell>
      <TableCell>
        {cursorType && (
          <StreamPathSelect
            pathType={cursorType}
            paths={paths}
            path={cursorType === "sourceDefined" ? defaultCursorField : cursorField}
            onPathChange={onCursorChange}
          />
        )}
      </TableCell>
      <TableCell>
        {pkType && (
          <StreamPathSelect
            pathType={pkType}
            paths={paths}
            path={primaryKey}
            isMulti
            onPathChange={onPrimaryKeyChange}
          />
        )}
      </TableCell>
      <FontAwesomeIcon icon={faArrowRight} className={styles.arrowCell} />
      <TableCell title={destNamespace}>
        <Text size="md" className={styles.cellText}>
          {destNamespace}
        </Text>
      </TableCell>
      <TableCell title={destName}>
        <Text size="md" className={styles.cellText}>
          {destName}
        </Text>
      </TableCell>
    </Row>
  );
};
