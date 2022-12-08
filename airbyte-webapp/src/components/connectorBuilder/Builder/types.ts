import * as yup from "yup";

import {
  ConnectorManifest,
  DeclarativeStream,
  HttpRequesterAllOfAuthenticator,
} from "core/request/ConnectorBuilderClient";

export interface BuilderFormValues {
  global: {
    connectorName: string;
    urlBase: string;
    // TODO: make required when authenticator is fully added
    authenticator?: HttpRequesterAllOfAuthenticator;
  };
  streams: BuilderStream[];
}

export interface BuilderStream {
  name: string;
  urlPath: string;
  fieldPointer: string[];
  httpMethod: "GET" | "POST";
}

export const builderFormValidationSchema = yup.object().shape({
  global: yup.object().shape({
    connectorName: yup.string().required("form.empty.error"),
    urlBase: yup.string().required("form.empty.error"),
    authenticator: yup.object(),
  }),
  streams: yup.array().of(
    yup.object().shape({
      name: yup.string().required("form.empty.error"),
      urlPath: yup.string().required("form.empty.error"),
      fieldPointer: yup.array().of(yup.string()),
      httpMethod: yup.mixed().oneOf(["GET", "POST"]),
    })
  ),
});

export const convertToManifest = (values: BuilderFormValues): ConnectorManifest => {
  const manifestStreams: DeclarativeStream[] = values.streams.map((stream) => {
    return {
      name: stream.name,
      retriever: {
        name: stream.name,
        requester: {
          name: stream.name,
          url_base: values.global?.urlBase,
          path: stream.urlPath,
          authenticator: values.global?.authenticator,
          // TODO: remove these empty "config" values once they are no longer required in the connector manifest JSON schema
          config: {},
        },
        record_selector: {
          extractor: {
            field_pointer: stream.fieldPointer,
            config: {},
          },
        },
        config: {},
      },
      config: {},
    };
  });

  return {
    version: "0.1.0",
    check: {
      stream_names: [],
    },
    streams: manifestStreams,
  };
};
