import React, { useMemo } from "react";
import { FormattedMessage } from "react-intl";

import styled from "styled-components";

import { DropDownRow } from "components";
import { MainInfoCell } from "./components/MainInfoCell";
import { Cell } from "components/SimpleTableComponents";
import { ExpandFieldCell } from "./components/ExpandFieldCell";
import { SyncSettingsCell } from "./components/SyncSettingsCell";
import {
  DestinationSyncMode,
  SyncMode,
  SyncSchemaStream,
} from "core/domain/catalog";

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

  pkRequired?: boolean;
  cursorRequired?: boolean;

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
  cursorRequired,
  isRowExpanded,
  hasFields,
  onExpand,
}) => {
  const { primaryKey, syncMode, destinationSyncMode } = stream.config;
  const pkKeyItems = primaryKey.map((k) => k.join("."));
  const syncSchema = useMemo(
    () => ({
      syncMode: syncMode,
      destinationSyncMode: destinationSyncMode,
    }),
    [syncMode, destinationSyncMode]
  );

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
          <ExpandFieldCell
            onExpand={onExpand}
            isItemOpen={isRowExpanded}
            tooltipItems={pkKeyItems}
          >
            <FormattedMessage
              id="form.pkSelected"
              values={{ count: pkKeyItems.length, items: pkKeyItems }}
            />
          </ExpandFieldCell>
        )}
      </Cell>
      <Cell>
        {cursorRequired && (
          <ExpandFieldCell onExpand={onExpand} isItemOpen={isRowExpanded}>
            {stream.config.cursorField.join(".")}
          </ExpandFieldCell>
        )}
      </Cell>
    </>
  );
};
