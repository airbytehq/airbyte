import { faArrowRight, faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import classNames from "classnames";
import { isEqual } from "lodash";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { ModificationIcon } from "components/icons/ModificationIcon";
import { Cell, Row } from "components/SimpleTableComponents";
import { CheckBox } from "components/ui/CheckBox";
import { Switch } from "components/ui/Switch";
import { Text } from "components/ui/Text";

import { useBulkEditSelect } from "hooks/services/BulkEdit/BulkEditService";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

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

  const { initialValues } = useConnectionFormService();

  const statusToDisplay = useMemo(() => {
    const rowStatusChanged =
      initialValues.syncCatalog.streams.find(
        (item) => item.stream?.name === stream.stream?.name && item.stream?.namespace === stream.stream?.namespace
      )?.config?.selected !== stream.config?.selected;

    const rowChanged = !isEqual(
      initialValues.syncCatalog.streams.find(
        (item) =>
          item.stream &&
          stream.stream &&
          item.stream.name === stream.stream.name &&
          item.stream.namespace === stream.stream.namespace
      )?.config,
      stream.config
    );

    if (rowStatusChanged) {
      return isStreamEnabled ? "added" : "removed";
    } else if (rowChanged) {
      return "changed";
    } else if (!isStreamEnabled && !rowStatusChanged) {
      return "disabled";
    }
    return "unchanged";
  }, [initialValues.syncCatalog.streams, stream, isStreamEnabled]);

  const [isSelected, selectForBulkEdit] = useBulkEditSelect(stream.id);

  const paths = useMemo(() => primitiveFields.map((field) => field.path), [primitiveFields]);
  const fieldCount = fields?.length ?? 0;
  const onRowClick = fieldCount > 0 ? () => onExpand() : undefined;

  const streamHeaderContentStyle = classnames(styles.streamHeaderContent, {
    [styles.added]: statusToDisplay === "added",
    [styles.removed]: statusToDisplay === "removed",
    [styles.changed]: isSelected || statusToDisplay === "changed",
    [styles.disabled]: statusToDisplay === "disabled",
    [styles.error]: hasError,
  });

  const statusIcon = useMemo(() => {
    if (statusToDisplay === "added") {
      return <FontAwesomeIcon icon={faPlus} size="2x" className={classNames(styles.icon, styles.plus)} />;
    } else if (statusToDisplay === "removed") {
      return <FontAwesomeIcon icon={faMinus} size="2x" className={classNames(styles.icon, styles.minus)} />;
    } else if (statusToDisplay === "changed") {
      return (
        // todo: styles need adjusting, especially color and possibly alignment
        <span className={classNames(styles.icon, styles.changed)}>
          <ModificationIcon color={styles.modificationIconColor} />
        </span>
      );
    }
    return null;
  }, [statusToDisplay]);

  const pillButtonVariant = useMemo(() => {
    if (statusToDisplay === "added") {
      return "green";
    } else if (statusToDisplay === "removed") {
      return "red";
    } else if (statusToDisplay === "changed") {
      return "blue";
    }
    return "grey";
  }, [statusToDisplay]);

  const checkboxCellCustomStyle = classnames(styles.checkboxCell, styles.streamRowCheckboxCell);

  // todo: the primary key and cursor dropdowns should be full width of the cell
  return (
    <Row onClick={onRowClick} className={streamHeaderContentStyle}>
      {!disabled && (
        <div className={checkboxCellCustomStyle}>
          {statusIcon}
          <CheckBox checked={isSelected} onChange={selectForBulkEdit} />
        </div>
      )}
      <Cell flex={0.5} flush>
        <Switch small checked={stream.config?.selected} onChange={onSelectStream} disabled={disabled} />
      </Cell>
      {/* <Cell>{fieldCount}</Cell> */}
      <Cell flex={1} title={stream.stream?.namespace || ""}>
        <Text size="md" className={styles.cellText}>
          {stream.stream?.namespace || <FormattedMessage id="form.noNamespace" />}
        </Text>
      </Cell>
      <Cell flex={1} title={stream.stream?.name || ""}>
        <Text size="md" className={styles.cellText}>
          {stream.stream?.name}
        </Text>
      </Cell>
      <div className={styles.syncModeCell}>
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
      </div>
      <Cell flex={1}>
        {cursorType && (
          <StreamPathSelect
            pathType={cursorType}
            paths={paths}
            path={cursorType === "sourceDefined" ? defaultCursorField : cursorField}
            onPathChange={onCursorChange}
            variant={pillButtonVariant}
          />
        )}
      </Cell>
      <Cell flex={1}>
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
      </Cell>
      <FontAwesomeIcon icon={faArrowRight} className={styles.arrowCell} />
      <Cell flex={1} title={destNamespace}>
        <Text size="md" className={styles.cellText}>
          {destNamespace}
        </Text>
      </Cell>
      <Cell flex={1} title={destName}>
        <Text size="md" className={styles.cellText}>
          {destName}
        </Text>
      </Cell>
    </Row>
  );
};
