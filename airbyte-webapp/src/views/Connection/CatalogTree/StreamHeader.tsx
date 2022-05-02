import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";
import styled from "styled-components";

import { Cell, CheckBox, DropDownRow, Toggle } from "components";

import { DestinationSyncMode, Path, SyncMode, SyncSchemaField, SyncSchemaStream } from "core/domain/catalog";
import { useBulkEditSelect } from "hooks/services/BulkEdit/BulkEditService";

import { Arrow as ArrowBlock } from "./components/Arrow";
import { IndexerType, PathPopout } from "./components/PathPopout";
import { SyncSettingsDropdown } from "./components/SyncSettingsDropdown";
import { ArrowCell, CheckboxCell, HeaderCell } from "./styles";

const EmptyField = styled.span`
  color: ${({ theme }) => theme.greyColor40};
`;

type SyncSchema = {
  syncMode: SyncMode;
  destinationSyncMode: DestinationSyncMode;
};

interface StreamHeaderProps {
  stream: SyncSchemaStream;
  destName: string;
  destNamespace: string;
  availableSyncModes: {
    value: SyncSchema;
  }[];
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
}) => {
  const { primaryKey, syncMode, cursorField, destinationSyncMode } = stream.config;

  const { defaultCursorField } = stream.stream;
  const syncSchema = useMemo(
    () => ({
      syncMode,
      destinationSyncMode,
    }),
    [syncMode, destinationSyncMode]
  );

  const [isSelected, selectForBulkEdit] = useBulkEditSelect(stream.id);

  const paths = primitiveFields.map((field) => field.path);

  return (
    <>
      <CheckboxCell>
        <CheckBox checked={isSelected} onChange={selectForBulkEdit} />
      </CheckboxCell>
      <ArrowCell>
        {hasFields ? <ArrowBlock onExpand={onExpand} isItemHasChildren={hasFields} isItemOpen={isRowExpanded} /> : null}
      </ArrowCell>
      <HeaderCell flex={0.4}>
        <Toggle small checked={stream.config.selected} onChange={onSelectStream} />
      </HeaderCell>
      <HeaderCell ellipsis title={stream.stream.namespace || ""}>
        {stream.stream.namespace || (
          <EmptyField>
            <FormattedMessage id="form.noNamespace" />
          </EmptyField>
        )}
      </HeaderCell>
      <HeaderCell ellipsis title={stream.stream.name || ""}>
        {stream.stream.name}
      </HeaderCell>
      <Cell flex={1.5}>
        <SyncSettingsDropdown value={syncSchema} options={availableSyncModes} onChange={onSelectSyncMode} />
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
            isMulti={true}
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
    </>
  );
};
