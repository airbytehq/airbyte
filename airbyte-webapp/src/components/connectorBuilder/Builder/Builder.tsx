import { Form, Formik, useFormikContext } from "formik";
import { useEffect } from "react";

import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { usePatchFormik } from "views/Connector/ConnectorForm/useBuildForm";

import styles from "./Builder.module.scss";
import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderOneOf } from "./BuilderOneOf";
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
              <BuilderOneOf
                path="streams[0].retriever.requester.authenticator"
                label="Authenticator"
                tooltip="Authentication method to use for requests send to the API"
                options={[
                  { label: "No Auth", typeValue: "NoAuth" },
                  {
                    label: "API Key",
                    typeValue: "ApiKeyAuthenticator",
                    children: (
                      <>
                        <BuilderField
                          type="text"
                          path="streams[0].retriever.requester.authenticator.header"
                          label="Header"
                          tooltip="HTTP header which should be set to the API Key"
                        />
                        <BuilderField
                          type="text"
                          path="streams[0].retriever.requester.authenticator.api_token"
                          label="API Token"
                          tooltip="Value to set on the API Key header"
                        />
                      </>
                    ),
                  },
                  {
                    label: "Basic HTTP",
                    typeValue: "BasicHttpAuthenticator",
                    children: (
                      <>
                        <BuilderField
                          type="text"
                          path="streams[0].retriever.requester.authenticator.username"
                          label="Username"
                          tooltip="Value to use for username"
                        />
                        <BuilderField
                          type="text"
                          path="streams[0].retriever.requester.authenticator.password"
                          label="Password"
                          tooltip="Value to use for password"
                        />
                      </>
                    ),
                  },
                ]}
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
