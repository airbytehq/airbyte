import React, { useCallback, useMemo } from "react";

import { TreeViewSection } from "./components/TreeViewSection";
import {
  SyncSchema,
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  AirbyteStream,
} from "core/domain/catalog";
import { naturalComparatorBy } from "utils/objects";

type IProps = {
  filter?: string;
  schema: SyncSchema;
  destinationSupportedSyncModes: DestinationSyncMode[];
  onChangeSchema: (schema: SyncSchema) => void;
};

const TreeView: React.FC<IProps> = ({
  schema,
  destinationSupportedSyncModes,
  onChangeSchema,
  filter,
}) => {
  const onUpdateStream = useCallback(
    (stream: AirbyteStream, newStream: Partial<AirbyteStreamConfiguration>) => {
      const newSchema = schema.streams.map((streamNode) => {
        return streamNode.stream === stream
          ? {
              ...streamNode,
              config: { ...streamNode.config, ...newStream },
            }
          : streamNode;
      });

      onChangeSchema({ streams: newSchema });
    },
    [schema, onChangeSchema]
  );

  const filteringSchema = useMemo(() => {
    return filter
      ? {
          streams: schema.streams.filter((stream) =>
            stream.stream.name.toLowerCase().includes(filter.toLowerCase())
          ),
        }
      : schema;
  }, [filter, schema]);

  // TODO: there is no need to sort schema everytime. We need to do it only once as streams[].stream is const
  const sortedSchema = useMemo(
    () => ({
      streams: filteringSchema.streams.sort(
        naturalComparatorBy((syncStream) => syncStream.stream.name)
      ),
    }),
    [filteringSchema.streams]
  );

  return (
    <>
      {sortedSchema.streams.map((streamNode) => (
        <TreeViewSection
          key={`${
            streamNode.stream.namespace ? streamNode.stream.namespace + "/" : ""
          }${streamNode.stream.name}`}
          streamNode={streamNode}
          destinationSupportedSyncModes={destinationSupportedSyncModes}
          updateStream={onUpdateStream}
        />
      ))}
    </>
  );
};

export default TreeView;
