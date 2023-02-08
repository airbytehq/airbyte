import {
  AirbyteStream,
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SelectedFieldInfo,
  SyncMode,
} from "core/request/AirbyteClient";

import { mergeFieldPathArrays } from "./streamConfigHelpers";

export function updateStreamSyncMode(
  stream: AirbyteStream,
  config: AirbyteStreamConfiguration,
  syncModes: { syncMode: SyncMode; destinationSyncMode: DestinationSyncMode }
): AirbyteStreamConfiguration {
  const { syncMode, destinationSyncMode } = syncModes;

  // If field selection was enabled, we need to ensure that any source-defined primary key or cursor is selected automatically
  if (config?.fieldSelectionEnabled) {
    const previouslySelectedFields = config?.selectedFields || [];
    const requiredSelectedFields: SelectedFieldInfo[] = [];

    // If the sync mode is incremental, we need to ensure the cursor is selected
    if (syncMode === "incremental") {
      if (stream.sourceDefinedCursor && stream.defaultCursorField?.length) {
        requiredSelectedFields.push({ fieldPath: stream.defaultCursorField });
      }
      if (config.cursorField?.length) {
        requiredSelectedFields.push({ fieldPath: config.cursorField });
      }
    }

    // If the destination sync mode is append_dedup, we need to ensure that each piece of the composite primary key is selected
    if (destinationSyncMode === "append_dedup" && stream.sourceDefinedPrimaryKey) {
      if (stream.sourceDefinedPrimaryKey?.length) {
        requiredSelectedFields.push(
          ...stream.sourceDefinedPrimaryKey.map((path) => ({
            fieldPath: path,
          }))
        );
      }
      if (config.primaryKey) {
        requiredSelectedFields.push(
          ...config.primaryKey.map((path) => ({
            fieldPath: path,
          }))
        );
      }
    }

    // Deduplicate the selected fields array, since the same field could have been added twice (e.g. as cursor and pk)
    const selectedFields = mergeFieldPathArrays(previouslySelectedFields, requiredSelectedFields);

    return {
      ...config,
      selectedFields,
      ...syncModes,
    };
  }

  return {
    ...config,
    ...syncModes,
  };
}
