import React from "react";
import styled from "styled-components";

import { Cell } from "../../SimpleTableComponents";
import DropDown from "../../DropDown";
import { IDataItem } from "../../DropDown/components/ListItem";
import { SyncSchemaStream } from "../../../core/resources/Schema";

const DropDownContainer = styled.div`
  padding-right: 10px;
`;

const StyledDropDown = styled(DropDown)`
  & ~ .rw-popup-container {
    min-width: 260px;
    left: auto;
  }
`;

type IProps = {
  item: SyncSchemaStream;
  onSelect: (data: IDataItem) => void;
};

const SyncSettingsCell: React.FC<IProps> = ({ item, onSelect }) => {
  const supportIncremental = !!item.supportedSyncModes.find(
    mode => mode === "incremental"
  );

  const currentSyncMode = item.defaultCursorField.length
    ? item.defaultCursorField[0]
    : item.syncMode || "full_refresh";

  const data: IDataItem[] = [{ text: "Full refresh", value: "full_refresh" }];

  if (supportIncremental && item.cursorField.length) {
    item.cursorField.forEach(fieldData =>
      data.push({
        text: fieldData,
        value: fieldData,
        secondary: true,
        groupValue: "incremental",
        groupValueText: "Incremental - based on..."
      })
    );
  }

  const onSelectMode = (data: IDataItem) => {
    onSelect(data);
  };

  return (
    <Cell>
      <DropDownContainer>
        <StyledDropDown
          hasFilter
          withBorder
          value={currentSyncMode}
          data={data}
          onSelect={onSelectMode}
          groupBy={supportIncremental ? "groupValueText" : undefined}
        />
      </DropDownContainer>
    </Cell>
  );
};

export default SyncSettingsCell;
