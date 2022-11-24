import { Form, Formik } from "formik";

import { Button } from "components/ui/Button";

import { ConnectorManifest } from "core/request/ConnectorManifest";
import { usePatchFormik } from "views/Connector/ConnectorForm/useBuildForm";

import styles from "./Builder.module.scss";
import { BuilderCard } from "./BuilderCard";
import { BuilderField } from "./BuilderField";
import { BuilderOneOf } from "./BuilderOneOf";

const FormikPatch: React.FC = () => {
  usePatchFormik();
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
        streams: [],
      }}
      onSubmit={(values: ConnectorManifest) => {
        console.log(values);
      }}
    >
      <>
        <FormikPatch />
        <Form>
          <div className={styles.container}>
            <BuilderCard>
              <BuilderField
                type="text"
                path="streams[0].retriever.requester.path"
                label="Path URL"
                tooltip="Path of the endpoint that this stream represents."
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
