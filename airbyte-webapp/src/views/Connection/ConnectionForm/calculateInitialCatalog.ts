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

const cleanBreakingFieldChanges = (streamNode: SyncSchemaStream, breakingChangesByStream: StreamTransform[]) => {
  breakingChangesByStream.forEach((streamTransformation) => {
    // get all of the removed field paths
    const removedFieldPaths = streamTransformation.updateStream?.map((update) => update.fieldName);

    if (streamNode.config?.primaryKey && removedFieldPaths?.length) {
      // if any of the field paths in the primary key match any of the field paths that were removed, clear the entire primaryKey property
      if (
        streamNode.config.primaryKey.some((key) => removedFieldPaths.some((removedPath) => isEqual(key, removedPath)))
      ) {
        streamNode.config.primaryKey = [];
      }
    }

    if (streamNode.config?.cursorField && removedFieldPaths) {
      // if the cursor field path is one of the removed field paths, clear the entire cursorField property
      if (removedFieldPaths.some((key) => isEqual(key, streamNode?.config?.cursorField))) {
        streamNode.config.cursorField = [];
      }
    }
  });
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
  breakingFieldChanges?: StreamTransform[],
  isNotCreateMode?: boolean,
  newStreamDescriptors?: StreamDescriptor[]
): SyncSchema => {
  return {
    streams: schema.streams.map<SyncSchemaStream>((apiNode, id) => {
      const nodeWithId: SyncSchemaStream = { ...apiNode, id: id.toString() };
      const nodeStream = verifySourceDefinedProperties(verifySupportedSyncModes(nodeWithId), isNotCreateMode || false);

      // narrow down the breaking field changes from this connection to only those relevant to this stream
      const breakingChangesByStream =
        breakingFieldChanges && breakingFieldChanges.length > 0
          ? breakingFieldChanges.filter((streamTransformFromDiff) => {
              return (
                streamTransformFromDiff.streamDescriptor.name === nodeStream?.stream?.name &&
                streamTransformFromDiff.streamDescriptor.namespace === nodeStream.stream?.namespace
              );
            })
          : [];

      // if there are breaking field changes in this stream, clear the relevant primary key(s)/cursor(s)
      if (breakingChangesByStream.length) {
        cleanBreakingFieldChanges(nodeStream, breakingChangesByStream);
      }

      // if the stream is new since a refresh, verify cursor and get optimal sync modes
      const isStreamNew = newStreamDescriptors?.some(
        (streamIdFromDiff) =>
          streamIdFromDiff.name === nodeStream?.stream?.name &&
          streamIdFromDiff.namespace === nodeStream.stream?.namespace
      );
      if (isNotCreateMode && !isStreamNew) {
        return nodeStream;
      }
      return getOptimalSyncMode(verifyConfigCursorField(nodeStream), supportedDestinationSyncModes);
    }),
  };
};

export default calculateInitialCatalog;
