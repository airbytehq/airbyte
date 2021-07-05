import React from "react";
import { FormattedMessage } from "react-intl";

import styled from "styled-components";

import { MainInfoCell } from "./components/MainInfoCell";
import { Cell } from "components/SimpleTableComponents";
import { ExpandFieldCell } from "./components/ExpandFieldCell";
import { SyncSettingsCell } from "./components/SyncSettingsCell";
import { SyncSchemaStream } from "core/domain/catalog";

const EmptyField = styled.span`
  color: ${({ theme }) => theme.greyColor40};
`;

interface StreamHeaderProps {
  stream: SyncSchemaStream;
  destName: string;
  destNamespace: string;
  availableSyncModes: any;
  syncMode: string;
  onSelectSyncMode: any;
  onSelectStream: any;

  pkRequired?: boolean;
  cursorRequired?: boolean;

  isRowExpanded: boolean;
  hasFields: boolean;
  onExpand: any;
}

export const StreamHeader: React.FC<StreamHeaderProps> = ({
  stream,
  onSelectSyncMode,
  onSelectStream,
  availableSyncModes,
  pkRequired,
  cursorRequired,
  isRowExpanded,
  hasFields,
  onExpand,
}) => {
  const pkKeyItems = stream.config.primaryKey.map((k) => k.join("."));

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
      <Cell>
        {stream.stream.namespace || (
          <EmptyField>
            <FormattedMessage id="form.noNamespace" />
          </EmptyField>
        )}
      </Cell>
      <SyncSettingsCell
        value={`${stream.config.syncMode}.${stream.config.destinationSyncMode}`}
        data={availableSyncModes}
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
