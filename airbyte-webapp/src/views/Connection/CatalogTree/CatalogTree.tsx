import { Field, FieldProps, setIn } from "formik";
import React, { useCallback } from "react";

import { AirbyteStreamConfiguration, DestinationSyncMode, SyncSchemaStream } from "core/domain/catalog";
import { FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

import { ConnectionFormMode } from "../ConnectionForm/ConnectionForm";
import { CatalogSection } from "./CatalogSection";

interface CatalogTreeProps {
  streams: SyncSchemaStream[];
  destinationSupportedSyncModes: DestinationSyncMode[];
  onChangeStream: (stream: SyncSchemaStream) => void;
  mode?: ConnectionFormMode;
}

const CatalogTree: React.FC<CatalogTreeProps> = ({ streams, destinationSupportedSyncModes, onChangeStream, mode }) => {
  const onUpdateStream = useCallback(
    (id: string, newConfig: Partial<AirbyteStreamConfiguration>) => {
      const streamNode = streams.find((streamNode) => streamNode.id === id);

      if (streamNode) {
        const newStreamNode = setIn(streamNode, "config", Object.assign({}, streamNode.config, newConfig));

        onChangeStream(newStreamNode);
      }
    },
    [streams, onChangeStream]
  );

  return (
    <>
      {streams.map((streamNode) => (
        <Field key={`schema.streams[${streamNode.id}].config`} name={`schema.streams[${streamNode.id}].config`}>
          {({ form }: FieldProps<FormikConnectionFormValues>) => (
            <CatalogSection
              key={`schema.streams[${streamNode.id}].config`}
              errors={form.errors}
              namespaceDefinition={form.values.namespaceDefinition}
              namespaceFormat={form.values.namespaceFormat}
              prefix={form.values.prefix}
              streamNode={streamNode}
              destinationSupportedSyncModes={destinationSupportedSyncModes}
              updateStream={onUpdateStream}
              mode={mode}
            />
          )}
        </Field>
      ))}
    </>
  );
};

export default CatalogTree;
