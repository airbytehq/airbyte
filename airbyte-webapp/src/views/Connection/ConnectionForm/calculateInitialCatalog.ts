import { SyncSchema, SyncSchemaStream } from "core/domain/catalog";
import { DestinationSyncMode, SyncMode, AirbyteStreamConfiguration } from "core/request/AirbyteClient";

const getDefaultCursorField = (streamNode: SyncSchemaStream): string[] => {
  if (streamNode.stream?.defaultCursorField?.length) {
    return streamNode.stream.defaultCursorField;
  }
  return streamNode.config?.cursorField || [];
};

const verifySourceDefinedProperties = (streamNode: SyncSchemaStream, isEditMode: boolean) => {
  if (!streamNode.stream || !streamNode.config || !isEditMode) {
    return streamNode;
  }

  const {
    stream: { sourceDefinedPrimaryKey, sourceDefinedCursor },
  } = streamNode;

  // if there's a source-defined cursor and the mode is correct, set the config to the default
  if (sourceDefinedCursor) {
    streamNode.config.cursorField = streamNode.stream.defaultCursorField;
  }

  // if the primary key doesn't need to be calculated from the source, just return the node
  if (!sourceDefinedPrimaryKey || sourceDefinedPrimaryKey.length === 0) {
    return streamNode;
  }

  // override the primary key with what the source said
  streamNode.config.primaryKey = sourceDefinedPrimaryKey;

  return streamNode;
};

const verifySupportedSyncModes = (streamNode: SyncSchemaStream): SyncSchemaStream => {
  if (!streamNode.stream) {
    return streamNode;
  }
  const {
    stream: { supportedSyncModes },
  } = streamNode;

  if (supportedSyncModes?.length) {
    return streamNode;
  }
  return { ...streamNode, stream: { ...streamNode.stream, supportedSyncModes: [SyncMode.full_refresh] } };
};

const verifyConfigCursorField = (streamNode: SyncSchemaStream): SyncSchemaStream => {
  if (!streamNode.config) {
    return streamNode;
  }
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
  if (!streamNode.stream?.supportedSyncModes) {
    return streamNode;
  }
  const {
    stream: { supportedSyncModes, sourceDefinedCursor },
  } = streamNode;

  if (
    supportedSyncModes.includes(SyncMode.incremental) &&
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
    supportedSyncModes.includes(SyncMode.incremental) &&
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

const calculateInitialCatalog = (
  schema: SyncSchema,
  supportedDestinationSyncModes: DestinationSyncMode[],
  isEditMode?: boolean
): SyncSchema => ({
  streams: schema.streams.map<SyncSchemaStream>((apiNode, id) => {
    const nodeWithId: SyncSchemaStream = { ...apiNode, id: id.toString() };
    const nodeStream = verifySourceDefinedProperties(verifySupportedSyncModes(nodeWithId), isEditMode || false);

    if (isEditMode) {
      return nodeStream;
    }

    return getOptimalSyncMode(verifyConfigCursorField(nodeStream), supportedDestinationSyncModes);
  }),
});

export default calculateInitialCatalog;
