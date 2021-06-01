import React, { useCallback, useMemo } from "react";
import { FastField, setIn } from "formik";

import {
  AirbyteStream,
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SyncSchemaStream,
} from "core/domain/catalog";
import { naturalComparatorBy } from "utils/objects";
import { FastFieldProps } from "formik/dist/FastField";
import { CatalogSection } from "./CatalogSection";

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
        <FastField name={`schema.streams[${streamNode.id}].config`}>
          {({ form }: FastFieldProps) => (
            <CatalogSection
              key={`schema.streams[${streamNode.id}].config`}
              errors={form.errors}
              streamNode={streamNode}
              destinationSupportedSyncModes={destinationSupportedSyncModes}
              updateStream={onUpdateStream}
            />
          )}
        </FastField>
      ))}
    </>
  );
};

export default CatalogTree;
