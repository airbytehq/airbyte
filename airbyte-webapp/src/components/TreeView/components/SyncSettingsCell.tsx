import React, { useMemo } from "react";
import styled from "styled-components";

import { Cell } from "../../SimpleTableComponents";
import DropDown from "../../DropDown";
import { IDataItem } from "../../DropDown/components/ListItem";
import { SyncMode, SyncSchemaStream } from "../../../core/resources/Schema";
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

  const fullData = useMemo(() => {
    const syncData: {
      value: string;
      text: string;
      secondary?: boolean;
      groupValue?: string;
      groupValueText?: string;
    }[] = item.supportedSyncModes
      .filter(mode => mode !== SyncMode.Incremental)
      .map(mode => ({
        value: mode,
        text: formatMessage({
          id: `sources.${mode}`,
          defaultMessage: mode
        })
      }));

    const isIncrementalSupported = item.supportedSyncModes.includes(
      SyncMode.Incremental
    );

    // If INCREMENTAL is included in the supported sync modes...
    if (isIncrementalSupported) {
      if (item.sourceDefinedCursor) {
        // If sourceDefinedCursor is true, In the dropdown we should just have one row for incremental
        syncData.push({
          text: formatMessage({
            id: "sources.incrementalSourceCursor"
          }),
          value: SyncMode.Incremental
        });
      } else {
        // If sourceDefinedCursor is false...

        // If defaultCursorField is set, then the field specified in there should be at the top of the list
        // and have the word "(default)" next to it
        if (item.defaultCursorField?.length) {
          syncData.push({
            text: formatMessage(
              {
                id: "sources.incrementalDefault"
              },
              { value: item.defaultCursorField[0] }
            ),
            value: item.defaultCursorField[0],
            secondary: true,
            groupValue: SyncMode.Incremental,
            groupValueText: formatMessage({
              id: "sources.incremental"
            })
          });
        }

        // Any column in the stream can be used as the cursor
        item.fields.forEach(field => {
          if (
            !syncData.find(dataItem => dataItem.value === field.cleanedName)
          ) {
            syncData.push({
              text: field.cleanedName,
              value: field.cleanedName,
              secondary: true,
              groupValue: SyncMode.Incremental,
              groupValueText: formatMessage({
                id: "sources.incremental"
              })
            });
          }
        });
      }
    }

    return syncData;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [item.supportedSyncModes, item.fields]);

  const currentValue = item.cursorField?.length
    ? item.sourceDefinedCursor
      ? SyncMode.Incremental
      : item.cursorField[0]
    : item.syncMode || "";

  return (
    <Cell>
      <DropDownContainer>
        <StyledDropDown
          fullText
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
