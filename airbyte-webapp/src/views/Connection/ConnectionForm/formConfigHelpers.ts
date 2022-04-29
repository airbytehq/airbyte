import { AirbyteStreamConfiguration, DestinationSyncMode, SyncMode } from "core/request/AirbyteClient";

import { SyncSchemaStream } from "../../../core/domain/catalog";

const getDefaultCursorField = (streamNode: SyncSchemaStream) => {
  if (streamNode?.stream?.defaultCursorField?.length) {
    return streamNode.stream.defaultCursorField;
  }
  return streamNode?.config?.cursorField;
};

export const verifySupportedSyncModes = (streamNode: SyncSchemaStream) => {
  if (!streamNode?.stream) {
    return;
  }
  const { supportedSyncModes } = streamNode.stream;

  if (supportedSyncModes?.length) {
    return streamNode;
  }
  return { ...streamNode, stream: { ...streamNode.stream, supportedSyncModes: [SyncMode.full_refresh] } };
};

export const verifyConfigCursorField = (streamNode: SyncSchemaStream | undefined): SyncSchemaStream | undefined => {
  if (!streamNode?.config) {
    return;
  }

  const { config } = streamNode;

  return {
    ...streamNode,
    config: {
      ...config,
      cursorField: config?.cursorField?.length ? config.cursorField : getDefaultCursorField(streamNode),
    },
  };
};

export const getOptimalSyncMode = (
  streamNode: SyncSchemaStream | undefined,
  supportedDestinationSyncModes: DestinationSyncMode[] | undefined
) => {
  if (!streamNode?.stream || !supportedDestinationSyncModes) {
    return;
  }

  const updateStreamConfig = (
    config: Pick<AirbyteStreamConfiguration, "syncMode" | "destinationSyncMode">
  ): SyncSchemaStream => ({
    ...streamNode,
    config: { ...streamNode.config, ...config },
  });

  const { supportedSyncModes, sourceDefinedCursor } = streamNode.stream;

  if (
    supportedSyncModes?.includes(SyncMode.incremental) &&
    supportedDestinationSyncModes.includes(DestinationSyncMode.append_dedup) &&
    sourceDefinedCursor
  ) {
    return updateStreamConfig({
      syncMode: SyncMode.incremental,
      destinationSyncMode: DestinationSyncMode.append_dedup,
    });
  }

  if (supportedDestinationSyncModes.includes(DestinationSyncMode.overwrite)) {
    return updateStreamConfig({
      syncMode: SyncMode.full_refresh,
      destinationSyncMode: DestinationSyncMode.overwrite,
    });
  }

  if (
    supportedSyncModes?.includes(SyncMode.incremental) &&
    supportedDestinationSyncModes.includes(DestinationSyncMode.append)
  ) {
    return updateStreamConfig({
      syncMode: SyncMode.incremental,
      destinationSyncMode: DestinationSyncMode.append,
    });
  }

  if (supportedDestinationSyncModes.includes(DestinationSyncMode.append)) {
    return updateStreamConfig({
      syncMode: SyncMode.full_refresh,
      destinationSyncMode: DestinationSyncMode.append,
    });
  }
  return streamNode;
};
