import { Form, Formik } from "formik";
import { isArray } from "lodash";

import { ConnectorManifest } from "core/request/ConnectorManifest";
import { useConnectorManifestSchema } from "services/connectorBuilder/ConnectorBuilderApiService";

import { BuilderCard } from "./BuilderCard";
import { OneOfField } from "./OneOfField";

export const Builder: React.FC = () => {
  const connectorManifestSchema = useConnectorManifestSchema();
  console.log("connectorManifestSchema", connectorManifestSchema);
  // getPathSchema(connectorManifestSchema);

  // const path = "streams[0].retriever.requester.path";
  // const pathSplit = path
  //   .split(/\[|\]\.|\./)
  //   .filter((split) => split.trim().length > 0)
  //   .map((splitString) => {
  //     const splitNumber = Number(splitString);
  //     return Number.isNaN(splitNumber) ? splitString : splitNumber;
  //   });

  // const formBlock = jsonSchemaToUiWidget(connectorManifestSchema.definitions as JSONSchema7);

  // const validationSchema = useConstructValidationSchema(connectorManifestSchema);
  // console.log(validationSchema);

  const path = "streams[0].retriever.requester.authenticator";
  const streams = connectorManifestSchema?.properties?.streams;
  if (streams === undefined || typeof streams === "boolean") {
    return <>"Error"</>;
  }
  const items = streams.items;
  if (items === undefined || isArray(items) || typeof items === "boolean") {
    return <>"Error"</>;
  }
  const retriever = items.properties?.retriever;
  if (retriever === undefined || typeof retriever === "boolean") {
    return <>"Error"</>;
  }
  const requester = retriever.properties?.requester;
  if (requester === undefined || typeof requester === "boolean") {
    return <>"Error"</>;
  }
  const authenticator = requester.properties?.authenticator;
  if (authenticator === undefined || typeof authenticator === "boolean") {
    return <>"Error"</>;
  }
  const oneOfOptions = authenticator.oneOf;
  if (oneOfOptions === undefined) {
    return <>"Error"</>;
  }
  const options = oneOfOptions.map((oneOfOption) => {
    if (typeof oneOfOption === "boolean" || oneOfOption.title === undefined) {
      throw new Error();
    }
    return {
      label: oneOfOption.title,
      value: oneOfOption.title,
    };
  });
  console.log(options);

  return (
    <Formik
      initialValues={{
        version: "1.0.0",
        checker: {
          stream_names: [],
        },
        streams: [],
      }}
      // validationSchema={validationSchema}
      onSubmit={(values: ConnectorManifest) => {
        console.log(values);
      }}
    >
      <Form>
        <BuilderCard>
          {/* <BuilderField
            label="Path URL"
            tooltip="Path of the endpoint that this stream represents."
            type="text"
            path="streams[0].retriever.requester.path"
          /> */}
          <OneOfField options={options} path={path} />
        </BuilderCard>
        <button type="submit">Submit</button>
      </Form>
    </Formik>
  );
};
