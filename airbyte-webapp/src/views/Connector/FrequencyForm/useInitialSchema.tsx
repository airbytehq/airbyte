import { useMemo } from "react";
import { useIntl } from "react-intl";

import {
  AirbyteStreamConfiguration,
  SyncMode,
  SyncSchema,
  SyncSchemaStream,
} from "core/domain/catalog";
import FrequencyConfig from "data/FrequencyConfig.json";
import { DropDownRow } from "components/DropDown";

// get cursorField if it is empty and syncMode is INCREMENTAL
function getDefaultCursorField(streamNode: SyncSchemaStream): string[] {
  if (streamNode.stream.defaultCursorField.length) {
    return streamNode.stream.defaultCursorField;
  }
  return streamNode.config.cursorField;
}

// If the value in supportedSyncModes is empty assume the only supported sync mode is FULL_REFRESH.
// Otherwise it supports whatever sync modes are present.
const useInitialSchema = (schema: SyncSchema): SyncSchema => {
  const initialSchema = useMemo<SyncSchema>(
    () => ({
      streams: schema.streams.map<SyncSchemaStream>((streamNode) => {
        const node = !streamNode.stream.supportedSyncModes?.length
          ? {
              ...streamNode,
              stream: {
                ...streamNode.stream,
                supportedSyncModes: [SyncMode.FullRefresh],
              },
            }
          : streamNode;

        // If syncMode isn't null - don't change item
        if (node.config.syncMode) {
          return node;
        }

        const updateStream = (
          config: Partial<AirbyteStreamConfiguration>
        ): SyncSchemaStream => ({
          ...node,
          config: { ...node.config, ...config },
        });

        const supportedSyncModes = node.stream.supportedSyncModes;

        // If syncMode is null, FULL_REFRESH should be selected by default (if it support FULL_REFRESH).
        if (supportedSyncModes.includes(SyncMode.FullRefresh)) {
          return updateStream({
            syncMode: SyncMode.FullRefresh,
          });
        }

        // If source support INCREMENTAL and not FULL_REFRESH. Set INCREMENTAL
        if (supportedSyncModes.includes(SyncMode.Incremental)) {
          return updateStream({
            cursorField: streamNode.config.cursorField.length
              ? streamNode.config.cursorField
              : getDefaultCursorField(streamNode),
            syncMode: SyncMode.Incremental,
          });
        }

        // If source don't support INCREMENTAL and FULL_REFRESH - set first value from supportedSyncModes list
        return updateStream({
          syncMode: streamNode.stream.supportedSyncModes[0],
        });
      }),
    }),
    [schema.streams]
  );

  return initialSchema;
};

const useFrequencyDropdownData = (): DropDownRow.IDataItem[] => {
  const formatMessage = useIntl().formatMessage;

  const dropdownData = useMemo(
    () =>
      FrequencyConfig.map((item) => ({
        ...item,
        text:
          item.value === "manual"
            ? item.text
            : formatMessage(
                {
                  id: "form.every",
                },
                {
                  value: item.simpleText || item.text,
                }
              ),
      })),
    [formatMessage]
  );

  return dropdownData;
};

export { useInitialSchema, useFrequencyDropdownData };
