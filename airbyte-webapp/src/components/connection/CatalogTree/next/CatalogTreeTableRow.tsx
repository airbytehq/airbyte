import { faArrowRight } from "@fortawesome/free-solid-svg-icons";
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
// eslint-disable-next-line css-modules/no-unused-class
import styles from "./CatalogTreeTableRow.module.scss";
import { CatalogTreeTableRowIcon } from "./CatalogTreeTableRowIcon";
import { StreamPathSelect } from "./StreamPathSelect";
import { SyncModeSelect } from "./SyncModeSelect";
import { useCatalogTreeTableRowProps } from "./useCatalogTreeTableRowProps";

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

  const checkboxCellCustomStyle = classnames(styles.checkboxCell, styles.streamRowCheckboxCell);

  return (
    <Row onClick={onRowClick} className={streamHeaderContentStyle}>
      {!disabled && (
        <div className={checkboxCellCustomStyle}>
          <CatalogTreeTableRowIcon stream={stream} />
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
          <SyncModeSelect
            options={availableSyncModes}
            onChange={onSelectSyncMode}
            value={syncSchema}
            variant={pillButtonVariant}
          />
        )}
      </TableCell>
      <TableCell>
        {cursorType && (
          <StreamPathSelect
            pathType={cursorType}
            paths={paths}
            path={cursorType === "sourceDefined" ? defaultCursorField : cursorField}
            onPathChange={onCursorChange}
            variant={pillButtonVariant}
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
            variant={pillButtonVariant}
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
