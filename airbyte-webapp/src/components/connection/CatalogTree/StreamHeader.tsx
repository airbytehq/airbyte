import classnames from "classnames";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import { Cell, Row } from "components";
import { MinusIcon } from "components/icons/MinusIcon";
import { PlusIcon } from "components/icons/PlusIcon";
import { CheckBox } from "components/ui/CheckBox";
import { DropDownOptionDataItem } from "components/ui/DropDown";
import { Switch } from "components/ui/Switch";

import { Path, SyncSchemaField, SyncSchemaStream } from "core/domain/catalog";
import { DestinationSyncMode, SyncMode } from "core/request/AirbyteClient";
import { useBulkEditSelect } from "hooks/services/BulkEdit/BulkEditService";

import { Arrow as ArrowBlock } from "./Arrow";
import { IndexerType, PathPopout } from "./PathPopout";
import styles from "./StreamHeader.module.scss";
import { ArrowCell, HeaderCell } from "./styles";
import { SyncSettingsDropdown } from "./SyncSettingsDropdown";

interface SyncSchema {
  syncMode: SyncMode;
  destinationSyncMode: DestinationSyncMode;
}

export interface StreamHeaderProps {
  stream: SyncSchemaStream;
  destName: string;
  destNamespace: string;
  availableSyncModes: Array<{
    value: SyncSchema;
  }>;
  onSelectSyncMode: (selectedMode: DropDownOptionDataItem) => void;
  onSelectStream: () => void;
  primitiveFields: SyncSchemaField[];
  pkType: IndexerType;
  onPrimaryKeyChange: (pkPath: Path[]) => void;
  cursorType: IndexerType;
  onCursorChange: (cursorPath: Path) => void;
  isRowExpanded: boolean;
  fields: SyncSchemaField[];
  onExpand: () => void;
  changedSelected: boolean;
  hasError: boolean;
  configErrors?: Record<string, string>;
  disabled?: boolean;
}

export const StreamHeader: React.FC<StreamHeaderProps> = ({
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
  isRowExpanded,
  fields,
  onExpand,
  changedSelected,
  hasError,
  disabled,
}) => {
  const { primaryKey, syncMode, cursorField, destinationSyncMode } = stream.config ?? {};
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

  const paths = primitiveFields.map((field) => field.path);

  const hasFields = fields && fields.length > 0;

  const iconStyle = classnames(styles.icon, {
    [styles.plus]: isStreamEnabled,
    [styles.minus]: !isStreamEnabled,
  });

  const streamHeaderContentStyle = classnames(styles.streamHeaderContent, {
    [styles.greenBackground]: changedSelected && isStreamEnabled,
    [styles.redBackground]: changedSelected && !isStreamEnabled,
    [styles.purpleBackground]: isSelected,
    [styles.redBorder]: hasError,
  });
  const checkboxCellCustomStyle = classnames(styles.checkboxCell, { [styles.streamRowCheckboxCell]: true });

  return (
    <Row className={styles.catalogSectionRow}>
      {!disabled && (
        <div className={checkboxCellCustomStyle}>
          <div className={iconStyle}>{changedSelected && (isStreamEnabled ? <PlusIcon /> : <MinusIcon />)}</div>
          <CheckBox checked={isSelected} onChange={selectForBulkEdit} />
        </div>
      )}
      <ArrowCell>
        {hasFields ? (
          <ArrowBlock
            onExpand={onExpand}
            isItemHasChildren={hasFields}
            isItemOpen={isRowExpanded}
            data-testid={`${stream.stream?.name}_expandStreamDetails`}
          />
        ) : null}
      </ArrowCell>
      <div className={streamHeaderContentStyle}>
        <HeaderCell flex={0.4}>
          <Switch
            size="sm"
            checked={stream.config?.selected}
            onChange={onSelectStream}
            disabled={disabled}
            data-testid={`${stream.stream?.name}-stream-sync-switch`}
          />
        </HeaderCell>
        <HeaderCell ellipsis title={stream.stream?.namespace || ""}>
          {stream.stream?.namespace || (
            <span className={styles.noHeader}>
              <FormattedMessage id="form.noNamespace" />
            </span>
          )}
        </HeaderCell>
        <HeaderCell ellipsis title={stream.stream?.name || ""} data-testid="streamNameCell">
          {stream.stream?.name}
        </HeaderCell>
        <Cell flex={1.5}>
          {disabled ? (
            <HeaderCell ellipsis title={`${syncSchema.syncMode} | ${syncSchema.destinationSyncMode}`}>
              {syncSchema.syncMode} | {syncSchema.destinationSyncMode}
            </HeaderCell>
          ) : (
            <SyncSettingsDropdown value={syncSchema} options={availableSyncModes} onChange={onSelectSyncMode} />
          )}
        </Cell>
        <HeaderCell>
          {cursorType && (
            <PathPopout
              pathType={cursorType}
              paths={paths}
              path={cursorType === "sourceDefined" ? defaultCursorField : cursorField}
              placeholder={<FormattedMessage id="connectionForm.cursor.searchPlaceholder" />}
              onPathChange={onCursorChange}
              id={`${stream.stream?.name}_cursor`}
            />
          )}
        </HeaderCell>
        <HeaderCell ellipsis>
          {pkType && (
            <PathPopout
              pathType={pkType}
              paths={paths}
              path={primaryKey}
              isMulti
              placeholder={<FormattedMessage id="connectionForm.primaryKey.searchPlaceholder" />}
              onPathChange={onPrimaryKeyChange}
              id={`${stream.stream?.name}_primaryKey`}
            />
          )}
        </HeaderCell>
        <HeaderCell ellipsis title={destNamespace}>
          {destNamespace}
        </HeaderCell>
        <HeaderCell ellipsis title={destName}>
          {destName}
        </HeaderCell>
      </div>
    </Row>
  );
};
