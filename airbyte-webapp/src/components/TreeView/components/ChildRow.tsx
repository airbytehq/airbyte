import React from "react";
import styled from "styled-components";

import { Cell } from "components/SimpleTableComponents";
import { SyncSchemaField } from "core/domain/catalog";

import MainInfoCell from "./MainInfoCell";
import ItemRow from "./ItemRow";
import TreeItem from "./TreeItem";

type IProps = {
  depth?: number;
  item: SyncSchemaField;
};

const StyledCell = styled(Cell)`
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: default;
`;

const ChildRow: React.FC<IProps> = ({ item, depth = 0 }) => {
  // TODO hack for v0.2.0: don't allow checking any of the children aka fields in a stream.
  // hideCheckbox={true} should be removed once it's possible to select these again.
  // https://airbytehq.slack.com/archives/C01CWUQT7UJ/p1603173180066800
  return (
    <>
      <TreeItem depth={0}>
        <ItemRow>
          <MainInfoCell
            hideCheckbox={true}
            label={item.name}
            isItemChecked={true}
            depth={depth}
          />
          <StyledCell>{item.type}</StyledCell>
          <StyledCell title={item.cleanedName}>{item.cleanedName}</StyledCell>
          <Cell />
        </ItemRow>
      </TreeItem>
      {item.fields?.map(field => (
        <ChildRow item={field} depth={depth} />
      ))}
    </>
  );
};

export default ChildRow;
