import { Form, Formik, useFormikContext } from "formik";
import { useEffect } from "react";

import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { usePatchFormik } from "views/Connector/ConnectorForm/useBuildForm";

import styles from "./Builder.module.scss";
import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderSidebar } from "./BuilderSidebar";

const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

const FormObserver: React.FC = () => {
  const { values } = useFormikContext<ConnectorManifest>();
  const { setJsonManifest } = useConnectorBuilderState();

  useEffect(() => {
    setJsonManifest(values);
  }, [values, setJsonManifest]);

  return null;
};

interface BuilderProps {
  toggleYamlEditor: () => void;
}

export const Builder: React.FC<BuilderProps> = ({ toggleYamlEditor }) => {
  const { jsonManifest } = useConnectorBuilderState();

  return (
    <Formik
      initialValues={jsonManifest}
      onSubmit={(values: ConnectorManifest) => {
        console.log(values);
      }}
    >
      <>
        <FormikPatch />
        <div className={styles.container}>
          <BuilderSidebar className={styles.sidebar} toggleYamlEditor={toggleYamlEditor} />
          <Form className={styles.form}>
            <FormObserver />
            <BuilderCard>
              {/* Note: we are explicitly NOT using intl for the BuilderField strings, in order to keep this easier to maintain */}
              <BuilderField
                type="text"
                path="streams[0].retriever.requester.url_base"
                label="API Url"
                tooltip="Base URL of the API"
              />
            </BuilderCard>
            <BuilderCard>
              <BuilderField
                type="text"
                path="streams[0].$options.name"
                label="Stream Name"
                tooltip="Name of the stream"
              />
              <BuilderField
                type="text"
                path="streams[0].$options.path"
                label="Path URL"
                tooltip="Path of the endpoint that this stream represents."
              />
              <BuilderField
                type="array"
                path="streams[0].retriever.record_selector.extractor.field_pointer"
                label="Field Pointer"
                tooltip="Pointer into the response that should be extracted as the final record"
              />
              <BuilderField
                type="enum"
                path="streams[0].retriever.requester.http_method"
                options={["GET", "POST"]}
                label="HTTP Method"
                tooltip="HTTP method to use for requests sent to the API"
              />
            </BuilderCard>
          </Form>
        </div>
      </>
    </Formik>
  );
};
