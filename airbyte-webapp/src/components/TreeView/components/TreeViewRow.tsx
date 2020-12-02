import React, { useMemo, useState } from "react";
import styled from "styled-components";

import { Row, Cell } from "../../SimpleTableComponents";
import { INode } from "../types";
import MainInfoCell from "./MainInfoCell";

type IProps = {
  isChild?: boolean;
  item: INode;
  checked: string[];
  onCheck: (data: string[]) => void;
};

const ItemRow = styled(Row)`
  height: 100%;
  white-space: nowrap;
`;

const TreeItem = styled.div<{ isChild?: boolean }>`
  height: 40px;
  border-bottom: 1px solid ${({ theme }) => theme.greyColor20};
  margin-left: ${({ isChild }) => (isChild ? 64 : 0)}px;
`;

const TreeViewRow: React.FC<IProps> = ({ item, checked, onCheck, isChild }) => {
  const [expanded, setExpanded] = useState<Array<string>>([]);

  const isItemOpen = useMemo(
    () => !!expanded.find(expandedItem => expandedItem === item.value),
    [expanded, item.value]
  );

  const isItemHasChildren = useMemo(
    () => !!(item.children && item.children.length),
    [item.children]
  );

  // TODO: fix it
  const isItemChecked = useMemo(
    () => !!checked?.find(checkedItem => checkedItem === item.value),
    [checked, item.value]
  );

  const onExpand = () => {
    if (isItemOpen) {
      const newState = expanded.filter(stateItem => stateItem !== item.value);
      setExpanded(newState);
    } else {
      setExpanded([...expanded, item.value]);
    }
  };

  // TODO: fix it
  const onCheckBoxClick = () => {
    if (isItemChecked) {
      const newState = checked.filter(stateItem => stateItem !== item.value);
      onCheck(newState);
    } else {
      onCheck([...checked, item.value]);
    }
  };

  return (
    <>
      <TreeItem isChild={isChild}>
        <ItemRow>
          <MainInfoCell
            hideCheckbox={item.hideCheckbox}
            label={item.label}
            onCheckBoxClick={onCheckBoxClick}
            onExpand={onExpand}
            isItemChecked={isItemChecked}
            isItemHasChildren={isItemHasChildren}
            isItemOpen={isItemOpen}
          />
          <Cell />
          <Cell />
          <Cell />
        </ItemRow>
      </TreeItem>
      {isItemOpen &&
        isItemHasChildren &&
        item.children?.map(item => (
          <TreeViewRow
            item={item}
            checked={checked}
            onCheck={onCheck}
            isChild
          />
        ))}
    </>
  );
};

export default TreeViewRow;
