import React, { useMemo } from "react";
import styled from "styled-components";
import { useIntl } from "react-intl";

import { Cell } from "../../SimpleTableComponents";
import DropDown, { DropDownRow } from "../../DropDown";
import { IDataItem } from "../../DropDown/components/ListItem";
import {
  SyncMode,
  SyncSchemaField,
  SyncSchemaStream
} from "../../../core/domain/catalog";

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
  streamNode: SyncSchemaStream;
  fields: SyncSchemaField[];
  onSelect: (data: IDataItem) => void;
};

function traverse(
  fields: SyncSchemaField[],
  cb: (field: SyncSchemaField) => any
) {
  fields.forEach(field => {
    cb(field);
    if (field.fields) {
      traverse(field.fields, cb);
    }
  });
}

const SyncSettingsCell: React.FC<IProps> = ({
  streamNode,
  fields,
  onSelect
}) => {
  const { stream, config } = streamNode;
  const formatMessage = useIntl().formatMessage;

  const fullData = useMemo(() => {
    const syncData: DropDownRow.IDataItem[] = stream.supportedSyncModes
      .filter(mode => mode !== SyncMode.Incremental)
      .map(mode => ({
        value: mode,
        text: formatMessage({
          id: `sources.${mode}`,
          defaultMessage: mode
        })
      }));

    const isIncrementalSupported = stream.supportedSyncModes.includes(
      SyncMode.Incremental
    );

    // If INCREMENTAL is included in the supported sync modes...
    if (isIncrementalSupported) {
      // If sourceDefinedCursor is true, In the dropdown we should just have one row for incremental
      if (stream.sourceDefinedCursor) {
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
        if (stream.defaultCursorField?.length) {
          syncData.push({
            text: formatMessage(
              {
                id: "sources.incrementalDefault"
              },
              { value: stream.defaultCursorField[0] }
            ),
            value: stream.defaultCursorField[0],
            secondary: true,
            groupValue: SyncMode.Incremental,
            groupValueText: formatMessage({
              id: "sources.incremental"
            })
          });
        }

        // Any column of primitive type in the stream can be used as the cursor
        traverse(fields, field => {
          if (
            field.type !== "object" &&
            !syncData.some(dataItem => dataItem.value === field.cleanedName)
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
  }, [fields, stream, formatMessage]);

  const currentValue = config.cursorField?.length
    ? stream.sourceDefinedCursor
      ? SyncMode.Incremental
      : config.cursorField[0]
    : config.syncMode || "";

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
