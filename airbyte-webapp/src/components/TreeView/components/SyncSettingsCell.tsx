import React from "react";
import styled from "styled-components";

import { Cell } from "../../SimpleTableComponents";
import DropDown from "../../DropDown";
import { IDataItem } from "../../DropDown/components/ListItem";
import { SyncSchemaStream } from "../../../core/resources/Schema";

const DropDownContainer = styled.div`
  padding-right: 10px;
`;

type IProps = {
  item: SyncSchemaStream;
  onSelect: (value: string) => void;
};

const SyncSettingsCell: React.FC<IProps> = ({ item, onSelect }) => {
  const data = [
    { text: "Full refresh", value: "full_refresh" },
    { text: "Incremental - based on...", value: "incremental" }
  ];

  const onSelectMode = (data: IDataItem) => onSelect(data.value);

  return (
    <Cell>
      <DropDownContainer>
        <DropDown
          withBorder
          value={item.syncMode || "full_refresh"}
          data={data}
          onSelect={onSelectMode}
        />
      </DropDownContainer>
    </Cell>
  );
};

export default SyncSettingsCell;
