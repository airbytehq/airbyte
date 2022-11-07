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
      <Cell flex={0.5} flush>
        <Switch small checked={stream.config?.selected} onChange={onSelectStream} disabled={disabled} />
      </Cell>
      {/* <Cell>{fieldCount}</Cell> */}
      <Cell flex={1} ellipsis title={stream.stream?.namespace || ""}>
        <Text size="md">{stream.stream?.namespace || <FormattedMessage id="form.noNamespace" />}</Text>
      </Cell>
      <Cell flex={1} ellipsis title={stream.stream?.name || ""}>
        <Text size="md">{stream.stream?.name}</Text>
      </Cell>
      <Cell flex={2}>
        {disabled ? (
          <Cell ellipsis title={syncSchema.syncMode}>
            <Text size="md">{syncSchema.syncMode}</Text>
          </Cell>
        ) : (
          // todo: SyncModeSelect should probably have a Tooltip, append/dedupe ends up ellipsing
          <SyncModeSelect options={availableSyncModes} onChange={onSelectSyncMode} value={syncSchema} />
        )}
      </Cell>
      <Cell flex={1}>
        {cursorType && (
          <StreamPathSelect
            pathType={cursorType}
            paths={paths}
            path={cursorType === "sourceDefined" ? defaultCursorField : cursorField}
            onPathChange={onCursorChange}
          />
        )}
      </Cell>
      <Cell flex={1} ellipsis>
        {pkType && (
          <StreamPathSelect
            pathType={pkType}
            paths={paths}
            path={primaryKey}
            isMulti
            onPathChange={onPrimaryKeyChange}
          />
        )}
      </Cell>
      <FontAwesomeIcon icon={faArrowRight} className={styles.arrowCell} />
      <Cell flex={1} ellipsis title={destNamespace}>
        <Text size="md"> {destNamespace}</Text>
      </Cell>
      <Cell flex={1} ellipsis title={destName}>
        <Text size="md"> {destName}</Text>
      </Cell>
    </Row>
  );
};
