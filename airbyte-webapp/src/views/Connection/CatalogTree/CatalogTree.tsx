import { Field, FieldProps, setIn, useFormikContext } from "formik";
import React, { useCallback } from "react";

import { SyncSchemaStream } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/Connection/ConnectionFormService";
import { ConnectionFormValues, FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

import { CatalogSection } from "./CatalogSection";

interface CatalogTreeProps {
  streams: SyncSchemaStream[];
  onChangeStream: (stream: SyncSchemaStream) => void;
}

const CatalogTree: React.FC<CatalogTreeProps> = ({ streams, onChangeStream }) => {
  const { mode } = useConnectionFormService();
  const onUpdateStream = useCallback(
    (id: string | undefined, newConfig: Partial<AirbyteStreamConfiguration>) => {
      const streamNode = streams.find((streamNode) => streamNode.id === id);

      if (streamNode) {
        const newStreamNode = setIn(streamNode, "config", { ...streamNode.config, ...newConfig });

        onChangeStream(newStreamNode);
      }
    },
    [streams, onChangeStream]
  );

  const { initialValues } = useFormikContext<ConnectionFormValues>();

  const changedStreams = streams.filter((stream, idx) => {
    return stream.config?.selected !== initialValues.syncCatalog.streams[idx].config?.selected;
  });

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
              updateStream={onUpdateStream}
              changedSelected={changedStreams.includes(streamNode) && mode === "edit"}
            />
          )}
        </Field>
      ))}
    </>
  );
};

export default CatalogTree;
