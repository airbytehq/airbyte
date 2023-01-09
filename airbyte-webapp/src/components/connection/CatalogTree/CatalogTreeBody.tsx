import { Field, FieldProps, setIn } from "formik";
import React, { useCallback } from "react";

import { SyncSchemaStream } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";
import { FormikConnectionFormValues } from "views/Connection/ConnectionForm/formConfig";

import { BulkHeader } from "./BulkHeader";
import { CatalogSection } from "./CatalogSection";
import styles from "./CatalogTreeBody.module.scss";
import { CatalogTreeHeader } from "./CatalogTreeHeader";
import { CatalogTreeSubheader } from "./CatalogTreeSubheader";
import { CatalogTreeTableHeader } from "./next/CatalogTreeTableHeader";
import { StreamConnectionHeader } from "./next/StreamConnectionHeader";

interface CatalogTreeBodyProps {
  streams: SyncSchemaStream[];
  changedStreams: SyncSchemaStream[];
  onStreamChanged: (stream: SyncSchemaStream) => void;
}

const isNewStreamsTableEnabled = process.env.REACT_APP_NEW_STREAMS_TABLE ?? false;

export const CatalogTreeBody: React.FC<CatalogTreeBodyProps> = ({ streams, changedStreams, onStreamChanged }) => {
  const { mode } = useConnectionFormService();

  const onUpdateStream = useCallback(
    (id: string | undefined, newConfig: Partial<AirbyteStreamConfiguration>) => {
      const streamNode = streams.find((streamNode) => streamNode.id === id);

      if (streamNode) {
        const newStreamNode = setIn(streamNode, "config", { ...streamNode.config, ...newConfig });

        onStreamChanged(newStreamNode);
      }
    },
    [streams, onStreamChanged]
  );

  return (
    <div className={styles.container}>
      {isNewStreamsTableEnabled ? (
        <>
          <StreamConnectionHeader />
          <CatalogTreeTableHeader />
        </>
      ) : (
        <>
          <CatalogTreeHeader />
          <CatalogTreeSubheader />
          <BulkHeader />
        </>
      )}
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
    </div>
  );
};
