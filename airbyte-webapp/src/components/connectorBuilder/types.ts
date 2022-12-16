import { JSONSchema7 } from "json-schema";
import * as yup from "yup";

import { SourceDefinitionSpecificationDraft } from "core/domain/connector";
import { PatchedConnectorManifest } from "core/domain/connectorBuilder/PatchedConnectorManifest";
import { DeclarativeStream } from "core/request/ConnectorManifest";

export interface BuilderFormInput {
  key: string;
  required: boolean;
  definition: JSONSchema7;
}

export interface BuilderFormValues {
  global: {
    connectorName: string;
    urlBase: string;
  };
  inputs: BuilderFormInput[];
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

export const convertToManifest = (values: BuilderFormValues): PatchedConnectorManifest => {
  const manifestStreams: DeclarativeStream[] = values.streams.map((stream) => {
    return {
      name: stream.name,
      retriever: {
        name: stream.name,
        requester: {
          name: stream.name,
          url_base: values.global?.urlBase,
          path: stream.urlPath,
          request_options_provider: {
            request_parameters: Object.fromEntries(stream.requestOptions.requestParameters),
            request_headers: Object.fromEntries(stream.requestOptions.requestHeaders),
            request_body_data: Object.fromEntries(stream.requestOptions.requestBody),
          },
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

  const specSchema: JSONSchema7 = {
    $schema: "http://json-schema.org/draft-07/schema#",
    type: "object",
    required: values.inputs.filter((input) => input.required).map((input) => input.key),
    properties: Object.fromEntries(values.inputs.map((input) => [input.key, input.definition])),
    additionalProperties: true,
  };

  const spec: SourceDefinitionSpecificationDraft = {
    connectionSpecification: specSchema,
  };

  return {
    version: "0.1.0",
    check: {
      stream_names: [],
    },
    streams: manifestStreams,
    spec,
  };
};
