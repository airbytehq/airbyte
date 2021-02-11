import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

import { Cell } from "../../SimpleTableComponents";
import MainInfoCell from "./MainInfoCell";
import SyncSettingsCell from "./SyncSettingsCell";
import ChildRow from "./ChildRow";

import {
  AirbyteStreamConfiguration,
  SyncSchemaStream
} from "../../../core/domain/catalog";
import ItemRow from "./ItemRow";
import TreeItem from "./TreeItem";
import { IDataItem } from "../../DropDown/components/ListItem";
import { traverseSchemaToField } from "../../../core/domain/catalog/fieldUtil";

const StyledCell = styled(Cell)`
  overflow: hidden;
  text-overflow: ellipsis;
`;

type IProps = {
  isChild?: boolean;
  streamNode: SyncSchemaStream;
  updateItem: (
    streamId: string,
    a: Partial<AirbyteStreamConfiguration>
  ) => void;
};

const TreeViewRow: React.FC<IProps> = ({ streamNode, updateItem }) => {
  const { stream, config } = streamNode;
  const streamId = stream.name;
  const [expanded, setExpanded] = useState<Array<string>>([]);
  const isItemOpen = useMemo<boolean>(
    () => expanded.some(expandedItem => expandedItem === streamId),
    [expanded, streamId]
  );
  const fields = useMemo(
    () => traverseSchemaToField(stream.jsonSchema, streamId),
    [stream]
  );

  const onExpand = useCallback(() => {
    const newState = isItemOpen
      ? expanded.filter(stateItem => stateItem !== streamId)
      : [...expanded, streamId];

    setExpanded(newState);
  }, [expanded, isItemOpen, streamId]);

  const onSelectSyncMode = useCallback(
    (data: IDataItem) => {
      if (data.groupValue) {
        updateItem(streamId, {
          syncMode: data.groupValue,
          cursorField: [data.value]
        });
      } else {
        updateItem(streamId, {
          syncMode: data.value,
          cursorField: []
        });
      }
    },
    [streamId, updateItem]
  );

  const onCheckBoxClick = useCallback(
    () =>
      updateItem(streamId, {
        selected: !config.selected
      }),
    [streamId, updateItem]
  );

  const hasChildren = fields && fields.length > 0;

  return (
    <>
      <TreeItem>
        <ItemRow>
          <MainInfoCell
            label={stream.name}
            onCheckBoxClick={onCheckBoxClick}
            onExpand={onExpand}
            isItemChecked={config.selected}
            isItemHasChildren={hasChildren}
            isItemOpen={isItemOpen}
          />
          <Cell />
          <StyledCell>{config.aliasName}</StyledCell>
          <SyncSettingsCell
            streamNode={streamNode}
            fields={fields}
            onSelect={onSelectSyncMode}
          />
        </ItemRow>
      </TreeItem>
      {isItemOpen &&
        hasChildren &&
        fields?.map(field => <ChildRow item={field} depth={1} />)}
    </>
  );
};

export default TreeViewRow;
