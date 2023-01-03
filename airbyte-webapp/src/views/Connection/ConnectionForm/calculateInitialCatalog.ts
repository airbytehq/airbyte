import isEqual from "lodash/isEqual";

import { SyncSchema, SyncSchemaStream } from "core/domain/catalog";
import {
  DestinationSyncMode,
  SyncMode,
  AirbyteStreamConfiguration,
  StreamDescriptor,
  StreamTransform,
} from "core/request/AirbyteClient";

const getDefaultCursorField = (streamNode: SyncSchemaStream): string[] => {
  if (streamNode.stream?.defaultCursorField?.length) {
    return streamNode.stream.defaultCursorField;
  }
  return streamNode.config?.cursorField || [];
};

const clearBreakingFieldChanges = (nodeStream: SyncSchemaStream, breakingChangesByStream: StreamTransform[]) => {
  if (!breakingChangesByStream.length || !nodeStream.config) {
    return nodeStream;
  }

  let clearPrimaryKey = false;
  let clearCursorField = false;

  for (const streamTransformation of breakingChangesByStream) {
    // get all of the removed field paths for this transformation
    const removedFieldPaths = streamTransformation.updateStream?.map((update) => update.fieldName);

    if (!removedFieldPaths?.length) {
      continue;
    }

    // if there is a primary key in the config, and any of its field paths were removed, we'll be clearing it
    if (
      !!nodeStream.config?.primaryKey?.length &&
      nodeStream.config?.primaryKey?.some((key) => removedFieldPaths.some((removedPath) => isEqual(key, removedPath)))
    ) {
      clearPrimaryKey = true;
    }

    // if there is a cursor field, and any of its field path was removed, we'll be clearing it
    if (
      !!nodeStream.config?.cursorField?.length &&
      removedFieldPaths.some((removedPath) => isEqual(removedPath, nodeStream?.config?.cursorField))
    ) {
      clearCursorField = true;
    }
  }

  return {
    ...nodeStream,
    config: {
      ...nodeStream.config,
      primaryKey: clearPrimaryKey ? [] : nodeStream.config.primaryKey,
      cursorField: clearCursorField ? [] : nodeStream.config.cursorField,
    },
  };
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
    stream: { supportedSyncModes, sourceDefinedCursor, sourceDefinedPrimaryKey },
  } = streamNode;

  if (
    supportedSyncModes.includes(SyncMode.incremental) &&
    supportedDestinationSyncModes.includes(DestinationSyncMode.append_dedup) &&
    sourceDefinedCursor &&
    sourceDefinedPrimaryKey?.length
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
  streamsWithBreakingFieldChanges?: StreamTransform[],
  isNotCreateMode?: boolean,
  newStreamDescriptors?: StreamDescriptor[]
): SyncSchema => {
  return {
    streams: schema.streams.map<SyncSchemaStream>((apiNode, id) => {
      const nodeWithId: SyncSchemaStream = { ...apiNode, id: id.toString() };
      const nodeStream = verifySourceDefinedProperties(verifySupportedSyncModes(nodeWithId), isNotCreateMode || false);

      // if the stream is new since a refresh, verify cursor and get optimal sync modes
      const isStreamNew = newStreamDescriptors?.some(
        (streamIdFromDiff) =>
          streamIdFromDiff.name === nodeStream.stream?.name &&
          streamIdFromDiff.namespace === nodeStream.stream?.namespace
      );

      // narrow down the breaking field changes from this connection to only those relevant to this stream
      const breakingChangesByStream =
        streamsWithBreakingFieldChanges && streamsWithBreakingFieldChanges.length > 0
          ? streamsWithBreakingFieldChanges.filter((streamTransformFromDiff) => {
              return (
                streamTransformFromDiff.streamDescriptor.name === nodeStream.stream?.name &&
                streamTransformFromDiff.streamDescriptor.namespace === nodeStream.stream?.namespace
              );
            })
          : [];

      // if we're in edit or readonly mode and the stream is not new, check for breaking changes then return
      if (isNotCreateMode && !isStreamNew) {
        return clearBreakingFieldChanges(nodeStream, breakingChangesByStream);
      }

      return getOptimalSyncMode(verifyConfigCursorField(nodeStream), supportedDestinationSyncModes);
    }),
  };
};

export default calculateInitialCatalog;
