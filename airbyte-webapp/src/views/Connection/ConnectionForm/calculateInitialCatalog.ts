import {
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SyncMode,
  SyncSchema,
  SyncSchemaStream,
} from "core/domain/catalog";

const getDefaultCursorField = (streamNode: SyncSchemaStream): string[] => {
  if (streamNode.stream.defaultCursorField.length) {
    return streamNode.stream.defaultCursorField;
  }
  return streamNode.config.cursorField;
};

const verifySupportedSyncModes = (streamNode: SyncSchemaStream): SyncSchemaStream => {
  const {
    stream: { supportedSyncModes },
  } = streamNode;

  if (supportedSyncModes?.length) {
    return streamNode;
  }
  return { ...streamNode, stream: { ...streamNode.stream, supportedSyncModes: [SyncMode.FullRefresh] } };
};

const verifyConfigCursorField = (streamNode: SyncSchemaStream): SyncSchemaStream => {
  const { config } = streamNode;

  return {
    ...streamNode,
    config: {
      ...config,
      cursorField: config.cursorField?.length ? config.cursorField : getDefaultCursorField(streamNode),
    },
  };
};

const getOptimalSyncMode = (
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

const calculateInitialCatalog = (
  schema: SyncSchema,
  supportedDestinationSyncModes: DestinationSyncMode[],
  isEditMode?: boolean
): SyncSchema => ({
  streams: schema.streams.map<SyncSchemaStream>((apiNode, id) => {
    const nodeWithId: SyncSchemaStream = { ...apiNode, id: id.toString() };
    const nodeStream = verifySupportedSyncModes(nodeWithId);

    if (isEditMode) {
      return nodeStream;
    }

    return getOptimalSyncMode(verifyConfigCursorField(nodeStream), supportedDestinationSyncModes);
  }),
});

export default calculateInitialCatalog;
