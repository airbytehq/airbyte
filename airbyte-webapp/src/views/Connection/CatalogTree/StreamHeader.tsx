import { faMinus, faPlus } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import classnames from "classnames";
import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Cell, CheckBox, DropDownRow, Row, Switch } from "components";

import { Path, SyncSchemaField, SyncSchemaStream } from "core/domain/catalog";
import { DestinationSyncMode, SyncMode } from "core/request/AirbyteClient";
import { useBulkEditSelect } from "hooks/services/BulkEdit/BulkEditService";

import { ConnectionFormMode } from "../ConnectionForm/ConnectionForm";
import { Arrow as ArrowBlock } from "./components/Arrow";
import { IndexerType, PathPopout } from "./components/PathPopout";
import { SyncSettingsDropdown } from "./components/SyncSettingsDropdown";
import styles from "./StreamHeader.module.scss";
import { ArrowCell, HeaderCell } from "./styles";

const EmptyField = styled.span`
  color: ${({ theme }) => theme.greyColor40};
`;

interface SyncSchema {
  syncMode: SyncMode;
  destinationSyncMode: DestinationSyncMode;
}

interface StreamHeaderProps {
  stream: SyncSchemaStream;
  destName: string;
  destNamespace: string;
  availableSyncModes: Array<{
    value: SyncSchema;
  }>;
  onSelectSyncMode: (selectedMode: DropDownRow.IDataItem) => void;
  onSelectStream: () => void;
  primitiveFields: SyncSchemaField[];
  pkType: IndexerType;
  onPrimaryKeyChange: (pkPath: Path[]) => void;
  cursorType: IndexerType;
  onCursorChange: (cursorPath: Path) => void;
  isRowExpanded: boolean;
  hasFields: boolean;
  onExpand: () => void;
  mode?: ConnectionFormMode;
  changedSelected: boolean;
  hasError: boolean;
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
  hasFields,
  onExpand,
  mode,
  changedSelected,
  hasError,
}) => {
  const { primaryKey, syncMode, cursorField, destinationSyncMode } = stream.config ?? {};
  const isEnabled = stream.config?.selected;

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

  const iconStyle = classnames(styles.icon, {
    [styles.plus]: isEnabled,
    [styles.minus]: !isEnabled,
  });

  const streamHeaderContentStyle = classnames(styles.streamHeaderContent, {
    [styles.greenBackground]: changedSelected && isEnabled,
    [styles.redBackground]: changedSelected && !isEnabled,
    [styles.purpleBackground]: isSelected,
    [styles.redBorder]: hasError,
  });
  //  FIXME: find out why checkboxCell warns as unused
  // eslint-disable-next-line css-modules/no-undef-class
  const checkboxCellCustomStyle = classnames(styles.checkboxCell, { [styles.streamRowCheckboxCell]: true });

  return (
    <Row className={styles.catalogSectionRow}>
      {mode !== "readonly" && (
        <div className={checkboxCellCustomStyle}>
          {changedSelected && (
            <div>
              {isEnabled ? (
                <FontAwesomeIcon icon={faPlus} size="2x" className={iconStyle} />
              ) : (
                <FontAwesomeIcon icon={faMinus} size="2x" className={iconStyle} />
              )}
            </div>
          )}
          <CheckBox checked={isSelected} onChange={selectForBulkEdit} />
        </div>
      )}
      <ArrowCell>
        {hasFields ? <ArrowBlock onExpand={onExpand} isItemHasChildren={hasFields} isItemOpen={isRowExpanded} /> : null}
      </ArrowCell>
      <div className={streamHeaderContentStyle}>
        <HeaderCell flex={0.4}>
          <Switch small checked={stream.config?.selected} onChange={onSelectStream} disabled={mode === "readonly"} />
        </HeaderCell>
        <HeaderCell ellipsis title={stream.stream?.namespace || ""}>
          {stream.stream?.namespace || (
            <EmptyField>
              <FormattedMessage id="form.noNamespace" />
            </EmptyField>
          )}
        </HeaderCell>
        <HeaderCell ellipsis title={stream.stream?.name || ""}>
          {stream.stream?.name}
        </HeaderCell>
        <Cell flex={1.5}>
          {mode !== "readonly" ? (
            <SyncSettingsDropdown value={syncSchema} options={availableSyncModes} onChange={onSelectSyncMode} />
          ) : (
            <HeaderCell ellipsis title={`${syncSchema.syncMode} | ${syncSchema.destinationSyncMode}`}>
              {syncSchema.syncMode} | {syncSchema.destinationSyncMode}
            </HeaderCell>
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
