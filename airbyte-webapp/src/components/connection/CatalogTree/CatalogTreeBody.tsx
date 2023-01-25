import { Field, FieldProps, setIn } from "formik";
import React, { useCallback } from "react";

import { FormikConnectionFormValues } from "components/connection/ConnectionForm/formConfig";

import { SyncSchemaStream } from "core/domain/catalog";
import { AirbyteStreamConfiguration } from "core/request/AirbyteClient";
import { useNewTableDesignExperiment } from "hooks/connection/useNewTableDesignExperiment";
import { useConnectionFormService } from "hooks/services/ConnectionForm/ConnectionFormService";

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

export const CatalogTreeBody: React.FC<CatalogTreeBodyProps> = ({ streams, changedStreams, onStreamChanged }) => {
  const { mode } = useConnectionFormService();
  const isNewTableDesignEnabled = useNewTableDesignExperiment();

  const onUpdateStream = useCallback(
    (id: string | undefined, newConfig: Partial<AirbyteStreamConfiguration>) => {
      const streamNode = streams.find((streamNode) => streamNode.id === id);

      if (streamNode) {
        const newStreamNode = setIn(streamNode, "config", { ...streamNode.config, ...newConfig });

        // config.selectedFields must be removed if fieldSelection is disabled
        if (!newStreamNode.config.fieldSelectionEnabled) {
          delete newStreamNode.config.selectedFields;
        }

        onStreamChanged(newStreamNode);
      }
    },
    [streams, onStreamChanged]
  );

  return (
    <div className={styles.container}>
      {isNewTableDesignEnabled ? (
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
