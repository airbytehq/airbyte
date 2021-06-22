import React, { useCallback } from "react";
import { Field, setIn, FastFieldProps } from "formik";

import {
  AirbyteStream,
  AirbyteStreamConfiguration,
  DestinationSyncMode,
  SyncSchemaStream,
} from "core/domain/catalog";
import { CatalogSection } from "./CatalogSection";

type IProps = {
  streams: SyncSchemaStream[];
  destinationSupportedSyncModes: DestinationSyncMode[];
  onChangeSchema: (schema: SyncSchemaStream[]) => void;
};

const CatalogTree: React.FC<IProps> = ({
  streams,
  destinationSupportedSyncModes,
  onChangeSchema,
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

  return (
    <>
      {streams.map((streamNode) => (
        <Field
          key={`schema.streams[${streamNode.id}].config`}
          name={`schema.streams[${streamNode.id}].config`}
        >
          {({ form }: FastFieldProps) => (
            <CatalogSection
              key={`schema.streams[${streamNode.id}].config`}
              errors={form.errors}
              streamNode={streamNode}
              destinationSupportedSyncModes={destinationSupportedSyncModes}
              updateStream={onUpdateStream}
            />
          )}
        </Field>
      ))}
    </>
  );
};

export default CatalogTree;
