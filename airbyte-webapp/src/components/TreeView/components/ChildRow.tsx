import React, { useCallback } from "react";
import styled from "styled-components";

import { Cell } from "../../SimpleTableComponents";
import MainInfoCell from "./MainInfoCell";

import { SyncSchemaField } from "../../../core/resources/Schema";
import ItemRow from "./ItemRow";
import TreeItem from "./TreeItem";

type IProps = {
  isChild?: boolean;
  item: SyncSchemaField;
  updateItem: (a: any) => void;
};

const ChildItemRow = styled(ItemRow)`
  margin-left: -64px;
`;

const ChildTreeItem = styled(TreeItem)`
  margin-left: 64px;
`;

const StyledCell = styled(Cell)`
  overflow: hidden;
  text-overflow: ellipsis;
`;

const ChildRow: React.FC<IProps> = ({ item, updateItem }) => {
  const onCheckBoxClick = useCallback(
    () => updateItem({ ...item, selected: !item.selected }),
    [item, updateItem]
  );

  // TODO hack for v0.2.0: don't allow checking any of the children aka fields in a stream.
  // hideCheckbox={true} should be removed once it's possible to select these again.
  // https://airbytehq.slack.com/archives/C01CWUQT7UJ/p1603173180066800
  return (
    <>
      <ChildTreeItem>
        <ChildItemRow>
          <MainInfoCell
            hideCheckbox={true}
            label={item.name}
            onCheckBoxClick={onCheckBoxClick}
            isItemChecked={item.selected}
            isItemHasChildren={false}
            isChild
          />
          <StyledCell>{item.dataType}</StyledCell>
          <StyledCell>{item.cleanedName}</StyledCell>
          <Cell />
        </ChildItemRow>
      </ChildTreeItem>
    </>
  );
};

export default ChildRow;
