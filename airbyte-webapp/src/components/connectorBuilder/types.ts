import * as yup from "yup";

import {
  ConnectorManifest,
  DeclarativeStream,
  InterpolatedRequestOptionsProvider,
} from "core/request/ConnectorManifest";

export interface BuilderFormValues {
  global: {
    connectorName: string;
    urlBase: string;
  };
  streams: BuilderStream[];
}

export interface BuilderStream {
  name: string;
  urlPath: string;
  fieldPointer: string[];
  httpMethod: "GET" | "POST";
  requestOptions: {
    requestParameters: Array<[string, string]>;
    requestHeaders: Array<[string, string]>;
    requestBody: Array<[string, string]>;
  };
}

export const builderFormValidationSchema = yup.object().shape({
  global: yup.object().shape({
    connectorName: yup.string().required("form.empty.error"),
    urlBase: yup.string().required("form.empty.error"),
  }),
  streams: yup.array().of(
    yup.object().shape({
      name: yup.string().required("form.empty.error"),
      urlPath: yup.string().required("form.empty.error"),
      fieldPointer: yup.array().of(yup.string()),
      httpMethod: yup.mixed().oneOf(["GET", "POST"]),
      requestOptions: yup.object().shape({
        requestParameters: yup.array().of(yup.array().of(yup.string())),
        requestHeaders: yup.array().of(yup.array().of(yup.string())),
        requestBody: yup.array().of(yup.array().of(yup.string())),
      }),
    })
  ),
});

export const convertToManifest = (values: BuilderFormValues): ConnectorManifest => {
  const manifestStreams: DeclarativeStream[] = values.streams.map((stream) => {
    return {
      type: "DeclarativeStream",
      name: stream.name,
      retriever: {
        type: "SimpleRetriever",
        name: stream.name,
        requester: {
          type: "HttpRequester",
          name: stream.name,
          url_base: values.global?.urlBase,
          path: stream.urlPath,
          request_options_provider: {
            // TODO can't declar type here because the server will error out, but the types dictate it is needed. Fix here once server is fixed.
            // type: "InterpolatedRequestOptionsProvider",
            request_parameters: Object.fromEntries(stream.requestOptions.requestParameters),
            request_headers: Object.fromEntries(stream.requestOptions.requestHeaders),
            request_body_data: Object.fromEntries(stream.requestOptions.requestBody),
          } as InterpolatedRequestOptionsProvider,
        },
        record_selector: {
          type: "RecordSelector",
          extractor: {
            type: "DpathExtractor",
            field_pointer: stream.fieldPointer,
          },
        },
      },
    };
  });

  return {
    version: "0.1.0",
    type: "DeclarativeSource",
    check: {
      type: "CheckStream",
      stream_names: [],
    },
    streams: manifestStreams,
  };
};
