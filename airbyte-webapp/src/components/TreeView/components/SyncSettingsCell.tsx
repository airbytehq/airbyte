import React, { useMemo, useState } from "react";
import styled from "styled-components";

import { Cell } from "../../SimpleTableComponents";
import DropDown from "../../DropDown";
import { IDataItem } from "../../DropDown/components/ListItem";
import { SyncSchemaStream } from "../../../core/resources/Schema";
import { useIntl } from "react-intl";

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
  const formatMessage = useIntl().formatMessage;
  const [supportIncremental, setSupportIncremental] = useState(false);

  const data: IDataItem[] = useMemo(
    () =>
      item.supportedSyncModes
        .filter(mode => {
          if (mode === "incremental") {
            setSupportIncremental(true);
            return false;
          }
          return true;
        })
        .map(mode => ({
          value: mode,
          text: formatMessage({
            id: `sources.${mode}`,
            defaultMessage: mode
          })
        })),
    [formatMessage, item.supportedSyncModes]
  );

  const fullData = useMemo(() => {
    // If INCREMENTAL is included in the supported sync modes...
    if (supportIncremental) {
      if (item.sourceDefinedCursor) {
        // If sourceDefinedCursor is true, In the dropdown we should just have one row for incremental
        data.push({
          text: formatMessage({
            id: "sources.incrementalSourceCursor"
          }),
          value: "incremental"
        });
      } else {
        // If sourceDefinedCursor is false...

        // If defaultCursorField is set, then the field specified in there should be at the top of the list
        // and have the word "(default)" next to it
        item.defaultCursorField.forEach(field =>
          data.push({
            text: formatMessage(
              {
                id: "sources.incrementalDefault"
              },
              { value: field }
            ),
            value: field,
            secondary: true,
            groupValue: "incremental",
            groupValueText: formatMessage({
              id: "sources.incremental"
            })
          })
        );

        // Any column in the stream can be used as the cursor
        item.fields.forEach(field => {
          if (!data.find(dataItem => dataItem.value === field.cleanedName)) {
            data.push({
              text: field.cleanedName,
              value: field.cleanedName,
              secondary: true,
              groupValue: "incremental",
              groupValueText: formatMessage({
                id: "sources.incremental"
              })
            });
          }
        });
      }
    }
    return data;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [item.fields, supportIncremental]);

  const currentValue =
    item.cursorField && item.cursorField.length
      ? item.cursorField[0]
      : item.syncMode || "";

  return (
    <Cell>
      <DropDownContainer>
        <StyledDropDown
          hasFilter
          withBorder
          value={currentValue}
          data={fullData}
          onSelect={onSelect}
          groupBy="groupValueText"
          filterPlaceholder={formatMessage({
            id: "sources.searchIncremental"
          })}
        />
      </DropDownContainer>
    </Cell>
  );
};

export default SyncSettingsCell;
