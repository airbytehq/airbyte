// get cursorField if it is empty and syncMode is INCREMENTAL
import {
  SyncMode,
  SyncSchema,
  SyncSchemaStream
} from "../../core/resources/Schema";
import React from "react";
import FrequencyConfig from "../../data/FrequencyConfig.json";
import { useIntl } from "react-intl";

const getDefaultCursorField = (stream: SyncSchemaStream) => {
  if (stream.defaultCursorField.length) {
    return stream.defaultCursorField;
  }
  if (stream.fields?.length) {
    return [stream.fields[0].cleanedName];
  }

  return stream.cursorField;
};

const useInitialSchema = (schema: SyncSchema) => {
  const initialSchema = React.useMemo(
    () => ({
      streams: schema.streams.map(item => {
        // If the value in supportedSyncModes is empty assume the only supported sync mode is FULL_REFRESH.
        // Otherwise it supports whatever sync modes are present.
        const itemWithSupportedSyncModes =
          !item.supportedSyncModes || !item.supportedSyncModes.length
            ? { ...item, supportedSyncModes: [SyncMode.FullRefresh] }
            : item;

        // If syncMode isn't null - don't change item
        if (!!itemWithSupportedSyncModes.syncMode) {
          return itemWithSupportedSyncModes;
        }

        const hasFullRefreshOption = itemWithSupportedSyncModes.supportedSyncModes.includes(
          SyncMode.FullRefresh
        );

        const hasIncrementalOption = itemWithSupportedSyncModes.supportedSyncModes.includes(
          SyncMode.Incremental
        );

        // If syncMode is null, FULL_REFRESH should be selected by default (if it support FULL_REFRESH).
        return hasFullRefreshOption
          ? {
              ...itemWithSupportedSyncModes,
              syncMode: SyncMode.FullRefresh
            }
          : hasIncrementalOption // If source support INCREMENTAL and not FULL_REFRESH. Set INCREMENTAL
          ? {
              ...itemWithSupportedSyncModes,
              cursorField: itemWithSupportedSyncModes.cursorField.length
                ? itemWithSupportedSyncModes.cursorField
                : getDefaultCursorField(itemWithSupportedSyncModes),
              syncMode: SyncMode.Incremental
            }
          : // If source don't support INCREMENTAL and FULL_REFRESH - set first value from supportedSyncModes list
            {
              ...itemWithSupportedSyncModes,
              syncMode: itemWithSupportedSyncModes.supportedSyncModes[0]
            };
      })
    }),
    [schema.streams]
  );

  return initialSchema;
};

const useFrequencyDropdownData = () => {
  const formatMessage = useIntl().formatMessage;

  const dropdownData = React.useMemo(
    () =>
      FrequencyConfig.map(item => ({
        ...item,
        text:
          item.value === "manual"
            ? item.text
            : formatMessage(
                {
                  id: "form.every"
                },
                {
                  value: item.text
                }
              )
      })),
    [formatMessage]
  );

  return dropdownData;
};

export { useInitialSchema, useFrequencyDropdownData };
