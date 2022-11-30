import { Form, Formik, useFormikContext } from "formik";
import { useEffect } from "react";

import { Button } from "components/ui/Button";

import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useConnectorBuilderState } from "services/connectorBuilder/ConnectorBuilderStateService";
import { usePatchFormik } from "views/Connector/ConnectorForm/useBuildForm";

import styles from "./Builder.module.scss";
import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderOneOf } from "./BuilderOneOf";

const FormikPatch: React.FC = () => {
  usePatchFormik();
  return null;
};

const FormObserver: React.FC = () => {
  const { values } = useFormikContext<ConnectorManifest>();
  const { setJsonManifest } = useConnectorBuilderState();

  useEffect(() => {
    // console.log("FormObserver::values", values);
    setJsonManifest(values);
  }, [values, setJsonManifest]);

  return null;
};

// Note: we are explicitly NOT using intl for the BuilderField strings, in order to keep this easier to maintain
export const Builder: React.FC = () => {
  return (
    <Formik
      initialValues={{
        version: "1.0.0",
        checker: {
          stream_names: [],
        },
        check: {
          stream_names: [],
        },
        streams: [],
      }}
      onSubmit={(values: ConnectorManifest) => {
        console.log(values);
      }}
    >
      <>
        <FormikPatch />
        <Form>
          <FormObserver />
          <div className={styles.container}>
            <BuilderCard>
              <BuilderField
                type="text"
                path="streams[0].$options.url_base"
                label="API Url"
                tooltip="Base URL of the API"
              />
              <BuilderField
                type="text"
                path="streams[0].$options.name"
                label="Stream Name"
                tooltip="Name of the stream"
              />
              <BuilderField
                type="text"
                path="streams[0].retriever.requester.path"
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
            <Button className={styles.submitButton} size="sm" type="submit">
              Submit
            </Button>
          </div>
        </Form>
      </>
    </Formik>
  );
};
