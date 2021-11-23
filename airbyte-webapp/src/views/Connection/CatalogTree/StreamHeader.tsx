import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import styled from "styled-components";

import { DropDownRow } from "components";
import { MainInfoCell } from "./components/MainInfoCell";
import { Cell } from "components/SimpleTableComponents";
import { SyncSettingsCell } from "./components/SyncSettingsCell";
import {
  DestinationSyncMode,
  SyncMode,
  SyncSchemaField,
  SyncSchemaStream,
} from "core/domain/catalog";
import { Popout } from "components/base/Popout";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSortDown } from "@fortawesome/free-solid-svg-icons";
import Tooltip from "./components/Tooltip";

const Arrow = styled(FontAwesomeIcon)<{ isOpen?: boolean }>`
  color: ${({ theme }) => theme.greyColor40};
  margin-left: 6px;
  transform: ${({ isOpen }) => isOpen && "rotate(180deg)"};
  transition: 0.3s;
  vertical-align: sub;
`;

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

  pkType: null | "required" | "sourceDefined";
  onPrimaryKeyChange: (pkPath: string[][]) => void;
  cursorType: null | "required" | "sourceDefined";
  onCursorChange: (cursorPath: string[]) => void;

  isRowExpanded: boolean;
  hasFields: boolean;
  onExpand: () => void;
}

const PkPopupComponents = { MultiValue: () => null };

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
  const {
    primaryKey,
    syncMode,
    cursorField,
    destinationSyncMode,
  } = stream.config;
  const syncSchema = useMemo(
    () => ({
      syncMode,
      destinationSyncMode,
    }),
    [syncMode, destinationSyncMode]
  );

  const dropdownFields = primitiveFields.map((field) => ({
    value: field.path,
    label: field.path.join("."),
  }));

  return (
    <>
      <MainInfoCell
        label={stream.stream.name}
        onCheckBoxClick={onSelectStream}
        onExpand={onExpand}
        isItemChecked={stream.config.selected}
        isItemHasChildren={hasFields}
        isItemOpen={isRowExpanded}
      />
      <Cell ellipsis title={stream.stream.namespace || ""}>
        {stream.stream.namespace || (
          <EmptyField>
            <FormattedMessage id="form.noNamespace" />
          </EmptyField>
        )}
      </Cell>
      <Cell ellipsis light title={destNamespace}>
        {destNamespace}
      </Cell>
      <Cell ellipsis title={destName}>
        {destName}
      </Cell>
      <SyncSettingsCell
        value={syncSchema}
        options={availableSyncModes}
        onChange={onSelectSyncMode}
      />
      <Cell ellipsis>
        {pkType === "required" ? (
          <Popout
            options={dropdownFields}
            value={primaryKey}
            // @ts-ignore need to solve issue with typings
            isMulti={true}
            isSearchable
            onChange={(options: { value: string[] }[]) => {
              onPrimaryKeyChange(options.map((op) => op.value));
            }}
            placeholder={
              <FormattedMessage id="connectionForm.primaryKey.searchPlaceholder" />
            }
            components={PkPopupComponents}
            targetComponent={({ onOpen }) => (
              <div onClick={onOpen}>
                {primaryKey.map((k) => k.join(".")).join(", ")}
                <Arrow icon={faSortDown} />
                <Tooltip items={primaryKey.map((k) => k.join("."))} />
              </div>
            )}
          />
        ) : pkType === "sourceDefined" ? (
          "<sourceDefined>"
        ) : null}
      </Cell>
      <Cell>
        {cursorType === "required" ? (
          <Popout
            options={dropdownFields}
            value={cursorField}
            placeholder={
              <FormattedMessage id="connectionForm.cursor.searchPlaceholder" />
            }
            onChange={(op) => onCursorChange(op.value)}
            targetComponent={({ onOpen }) => (
              <div onClick={onOpen}>
                {stream.config.cursorField.join(".")}
                <Arrow icon={faSortDown} />
                <Tooltip items={stream.config.cursorField} />
              </div>
            )}
          />
        ) : cursorType === "sourceDefined" ? (
          "<sourceDefined>"
        ) : null}
      </Cell>
    </>
  );
};
