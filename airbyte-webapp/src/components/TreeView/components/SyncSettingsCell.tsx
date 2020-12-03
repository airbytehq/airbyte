import React from "react";
import styled from "styled-components";

import { Cell } from "../../SimpleTableComponents";
import { INode } from "../types";
import DropDown from "../../DropDown";
import { IDataItem } from "../../DropDown/components/ListItem";

const SyncCell = styled(Cell)`
  padding-right: 10px;
`;

type IProps = {
  item: INode;
  onSelect: (data: IDataItem) => void;
};

const SyncSettingsCell: React.FC<IProps> = ({ item, onSelect }) => {
  const data = [
    { text: "Full refresh", value: "full_refresh" },
    { text: "Incremental - based on...", value: "incremental" }
  ];

  return (
    <SyncCell>
      <DropDown
        withBorder
        value={item.syncMode}
        data={data}
        onSelect={onSelect}
      />
    </SyncCell>
  );
};

export default SyncSettingsCell;
