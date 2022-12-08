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
import { CatalogTreeTableCell } from "./CatalogTreeTableCell";
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

  const checkboxCellCustomStyle = classnames(styles.checkboxCell, styles.streamRowCheckboxCell);

  return (
    <Row onClick={onRowClick} className={streamHeaderContentStyle}>
      {!disabled && (
        <div className={checkboxCellCustomStyle}>
          <CatalogTreeTableRowIcon stream={stream} />
          <CheckBox checked={isSelected} onChange={selectForBulkEdit} />
        </div>
      )}
      <CatalogTreeTableCell size="small">
        <Switch small checked={stream.config?.selected} onChange={onSelectStream} disabled={disabled} />
      </CatalogTreeTableCell>
      {/* <Cell>{fieldCount}</Cell> */}
      <CatalogTreeTableCell>
        <Text size="md" className={styles.cellText}>
          {stream.stream?.namespace || <FormattedMessage id="form.noNamespace" />}
        </Text>
      </CatalogTreeTableCell>
      <CatalogTreeTableCell>
        <Text size="md" className={styles.cellText}>
          {stream.stream?.name}
        </Text>
      </CatalogTreeTableCell>
      <CatalogTreeTableCell size="large">
        {disabled ? (
          <Cell>
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
      </CatalogTreeTableCell>
      <CatalogTreeTableCell>
        {cursorType && (
          <StreamPathSelect
            pathType={cursorType}
            paths={paths}
            path={cursorType === "sourceDefined" ? defaultCursorField : cursorField}
            onPathChange={onCursorChange}
            variant={pillButtonVariant}
          />
        )}
      </CatalogTreeTableCell>
      <CatalogTreeTableCell>
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
      </CatalogTreeTableCell>
      <FontAwesomeIcon icon={faArrowRight} className={styles.arrowCell} />
      <CatalogTreeTableCell>
        <Text size="md" className={styles.cellText}>
          {destNamespace}
        </Text>
      </CatalogTreeTableCell>
      <CatalogTreeTableCell>
        <Text size="md" className={styles.cellText}>
          {destName}
        </Text>
      </CatalogTreeTableCell>
    </Row>
  );
};
