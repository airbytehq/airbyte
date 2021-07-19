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
  SyncSchemaStream,
} from "core/domain/catalog";
import { Popout } from "components/base/Popout";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSortDown } from "@fortawesome/free-solid-svg-icons";

const Arrow = styled(FontAwesomeIcon)<{ isOpen?: boolean }>`
  color: ${({ theme }) => theme.greyColor40};
  //font-size: 14px;
  margin-left: 6px;
  transform: ${({ isOpen }) => isOpen && "rotate(180deg)"};
  transition: 0.3s;
  vertical-align: sub;
`;

const Ct = styled.div`
  display: flex;
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
  onSelectSyncMode: (selectedMode: DropDownRow.IDataItem | null) => void;
  onSelectStream: () => void;

  primitiveFields: string[];

  pkRequired: boolean;
  onPrimaryKeyChange: (pkPath: string[][]) => void;
  cursorRequired: boolean;
  onCursorChange: (cursorPath: string[]) => void;

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
  pkRequired,
  onPrimaryKeyChange,
  onCursorChange,
  primitiveFields,
  cursorRequired,
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

  const dropdownFields = primitiveFields.map((f) => ({
    value: f.split("."),
    label: f,
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
      <Cell title={stream.stream.namespace || ""}>
        {stream.stream.namespace || (
          <EmptyField>
            <FormattedMessage id="form.noNamespace" />
          </EmptyField>
        )}
      </Cell>
      <Cell title={destNamespace}>{destNamespace}</Cell>
      <Cell light title={destName}>
        {destName}
      </Cell>
      <SyncSettingsCell
        value={syncSchema}
        options={availableSyncModes}
        onChange={onSelectSyncMode}
      />
      <Cell>
        {pkRequired && (
          <Popout
            options={dropdownFields}
            value={primaryKey}
            // @ts-ignore
            isMulti={true}
            onChange={(option: any) => {
              onPrimaryKeyChange(option.map((op: any) => op.value));
            }}
            components={{ MultiValue: () => null }}
            targetComponent={({ onOpen }) => (
              <div onClick={onOpen}>
                <FormattedMessage
                  id="form.pkSelected"
                  values={{
                    count: primaryKey.length,
                    items: primaryKey.map((k) => k.join(".")),
                  }}
                />
                <Arrow icon={faSortDown} />
              </div>
            )}
          />
        )}
      </Cell>
      <Cell>
        {cursorRequired && (
          <Popout
            options={dropdownFields}
            value={cursorField}
            onChange={(op) => onCursorChange(op.value)}
            targetComponent={({ onOpen }) => (
              <Ct onClick={onOpen}>
                {stream.config.cursorField.join(".")}
                <Arrow icon={faSortDown} />
              </Ct>
            )}
          />
        )}
      </Cell>
    </>
  );
};
