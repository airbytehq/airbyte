import React from "react";
import styled from "styled-components";

import { Cell } from "../../SimpleTableComponents";
import MainInfoCell from "./MainInfoCell";

import { SyncSchemaField } from "../../../core/domain/catalog";
import ItemRow from "./ItemRow";
import TreeItem from "./TreeItem";

type IProps = {
  depth?: number;
  item: SyncSchemaField;
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

const ChildRow: React.FC<IProps> = ({ item, depth = 0 }) => {
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
            isItemChecked={true}
            depth={depth}
          />
          <StyledCell>{item.type}</StyledCell>
          <StyledCell>{item.cleanedName}</StyledCell>
          <Cell />
        </ChildItemRow>
      </ChildTreeItem>
      {item.fields?.map(field => (
        <ChildRow item={field} depth={depth} />
      ))}
    </>
  );
};

export default ChildRow;
