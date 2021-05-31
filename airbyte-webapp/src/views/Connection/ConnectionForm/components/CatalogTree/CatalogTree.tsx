import React, { useCallback, useMemo } from "react";
import { setIn } from "formik";

import { CatalogSection } from "./CatalogSection";
import {
  AirbyteStream,
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SyncSchemaStream,
} from "core/domain/catalog";
import { naturalComparatorBy } from "utils/objects";

type IProps = {
  filter?: string;
  streams: SyncSchemaStream[];
  destinationSupportedSyncModes: DestinationSyncMode[];
  onChangeSchema: (schema: SyncSchemaStream[]) => void;
};

const CatalogTree: React.FC<IProps> = ({
  streams,
  destinationSupportedSyncModes,
  onChangeSchema,
  filter,
}) => {
  const onUpdateStream = useCallback(
    (stream: AirbyteStream, newStream: Partial<AirbyteStreamConfiguration>) => {
      const newSchema = streams.map((streamNode) => {
        return streamNode.stream === stream
          ? setIn(
              streamNode,
              "config",
              Object.assign({}, streamNode.config, newStream)
            )
          : streamNode;
      });

      onChangeSchema(newSchema);
    },
    [streams, onChangeSchema]
  );

  const sortedSchema = useMemo(
    () =>
      streams.sort(naturalComparatorBy((syncStream) => syncStream.stream.name)),
    [streams]
  );

  const filteringSchema = useMemo(() => {
    return filter
      ? sortedSchema.filter((stream) =>
          stream.stream.name.toLowerCase().includes(filter.toLowerCase())
        )
      : sortedSchema;
  }, [filter, sortedSchema]);

  return (
    <>
      {filteringSchema.map((streamNode) => (
        <CatalogSection
          key={`${
            streamNode.stream.namespace ? `${streamNode.stream.namespace}/` : ""
          }${streamNode.stream.name}`}
          streamNode={streamNode}
          destinationSupportedSyncModes={destinationSupportedSyncModes}
          updateStream={onUpdateStream}
        />
      ))}
    </>
  );
};

export default CatalogTree;
