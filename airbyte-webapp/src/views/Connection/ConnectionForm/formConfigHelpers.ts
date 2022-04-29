import {
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SyncMode,
  SyncSchemaStream,
} from "../../../core/domain/catalog";

const getDefaultCursorField = (streamNode: SyncSchemaStream): string[] => {
  if (streamNode.stream.defaultCursorField.length) {
    return streamNode.stream.defaultCursorField;
  }
  return streamNode.config.cursorField;
};

export const verifySupportedSyncModes = (streamNode: SyncSchemaStream): SyncSchemaStream => {
  const {
    stream: { supportedSyncModes },
  } = streamNode;

  if (supportedSyncModes?.length) return streamNode;
  return { ...streamNode, stream: { ...streamNode.stream, supportedSyncModes: [SyncMode.FullRefresh] } };
};

export const verifyConfigCursorField = (streamNode: SyncSchemaStream): SyncSchemaStream => {
  const { config } = streamNode;

  return {
    ...streamNode,
    config: {
      ...config,
      cursorField: config.cursorField?.length ? config.cursorField : getDefaultCursorField(streamNode),
    },
  };
};

export const getOptimalSyncMode = (
  streamNode: SyncSchemaStream,
  supportedDestinationSyncModes: DestinationSyncMode[]
): SyncSchemaStream => {
  const updateStreamConfig = (
    config: Pick<AirbyteStreamConfiguration, "syncMode" | "destinationSyncMode">
  ): SyncSchemaStream => ({
    ...streamNode,
    config: { ...streamNode.config, ...config },
  });

  const {
    stream: { supportedSyncModes, sourceDefinedCursor },
  } = streamNode;

  if (
    supportedSyncModes.includes(SyncMode.Incremental) &&
    supportedDestinationSyncModes.includes(DestinationSyncMode.Dedupted) &&
    sourceDefinedCursor
  ) {
    return updateStreamConfig({
      syncMode: SyncMode.Incremental,
      destinationSyncMode: DestinationSyncMode.Dedupted,
    });
  }

  if (supportedDestinationSyncModes.includes(DestinationSyncMode.Overwrite)) {
    return updateStreamConfig({
      syncMode: SyncMode.FullRefresh,
      destinationSyncMode: DestinationSyncMode.Overwrite,
    });
  }

  if (
    supportedSyncModes.includes(SyncMode.Incremental) &&
    supportedDestinationSyncModes.includes(DestinationSyncMode.Append)
  ) {
    return updateStreamConfig({
      syncMode: SyncMode.Incremental,
      destinationSyncMode: DestinationSyncMode.Append,
    });
  }

  if (supportedDestinationSyncModes.includes(DestinationSyncMode.Append)) {
    return updateStreamConfig({
      syncMode: SyncMode.FullRefresh,
      destinationSyncMode: DestinationSyncMode.Append,
    });
  }
  return streamNode;
};
