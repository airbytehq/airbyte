import { SyncSchema, SyncSchemaStream } from "core/domain/catalog";
import { DestinationSyncMode, SyncMode, AirbyteStreamConfiguration } from "core/request/AirbyteClient";

const getDefaultCursorField = (streamNode: SyncSchemaStream): string[] => {
  if (streamNode.stream?.defaultCursorField?.length) {
    return streamNode.stream.defaultCursorField;
  }
  return streamNode.config?.cursorField || [];
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
    const nodeStream = verifySupportedSyncModes(nodeWithId);

    if (isEditMode) {
      return nodeStream;
    }

    return getOptimalSyncMode(verifyConfigCursorField(nodeStream), supportedDestinationSyncModes);
  }),
});

export default calculateInitialCatalog;
