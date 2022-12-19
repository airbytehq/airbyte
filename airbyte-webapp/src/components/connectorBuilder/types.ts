import { JSONSchema7 } from "json-schema";
import * as yup from "yup";

import { SourceDefinitionSpecificationDraft } from "core/domain/connector";
import { PatchedConnectorManifest } from "core/domain/connectorBuilder/PatchedConnectorManifest";
import { AirbyteJSONSchema } from "core/jsonSchema/types";
import { DeclarativeStream, HttpRequesterAllOfAuthenticator } from "core/request/ConnectorManifest";

export interface BuilderFormInput {
  key: string;
  required: boolean;
  definition: AirbyteJSONSchema;
}

export interface BuilderFormValues {
  global: {
    connectorName: string;
    urlBase: string;
    authenticator: HttpRequesterAllOfAuthenticator;
  };
  inputs: BuilderFormInput[];
  inferredInputOverrides: Record<string, Partial<AirbyteJSONSchema>>;
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
function getInferredInputList(values: BuilderFormValues): BuilderFormInput[] {
  if (values.global.authenticator.type === "ApiKeyAuthenticator") {
    return [
      {
        key: "api_key",
        required: true,
        definition: {
          type: "string",
          title: "API Key",
          airbyte_secret: true,
        },
      },
    ];
  }
  if (values.global.authenticator.type === "BearerAuthenticator") {
    return [
      {
        key: "api_key",
        required: true,
        definition: {
          type: "string",
          title: "API Key",
          airbyte_secret: true,
        },
      },
    ];
  }
  if (values.global.authenticator.type === "BasicHttpAuthenticator") {
    return [
      {
        key: "username",
        required: true,
        definition: {
          type: "string",
          title: "Username",
        },
      },
      {
        key: "password",
        required: true,
        definition: {
          type: "string",
          title: "Password",
          airbyte_secret: true,
        },
      },
    ];
  }
  return [];
}

export function getInferredInputs(values: BuilderFormValues): BuilderFormInput[] {
  const inferredInputs = getInferredInputList(values);
  return inferredInputs.map((input) =>
    values.inferredInputOverrides[input.key]
      ? {
          ...input,
          definition: { ...input.definition, ...values.inferredInputOverrides[input.key] },
        }
      : input
  );
}

export const builderFormValidationSchema = yup.object().shape({
  global: yup.object().shape({
    connectorName: yup.string().required("form.empty.error"),
    urlBase: yup.string().required("form.empty.error"),
    authenticator: yup.object({
      header: yup.mixed().when("type", {
        is: "ApiKeyAuthenticator",
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      api_token: yup.mixed().when("type", {
        is: "ApiKeyAuthenticator",
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      username: yup.mixed().when("type", {
        is: "BasicHttpAuthenticator",
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      password: yup.mixed().when("type", {
        is: "BasicHttpAuthenticator",
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
    }),
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
          authenticator: values.global.authenticator,
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

  const allInputs = [...values.inputs, ...getInferredInputs(values)];

  const specSchema: JSONSchema7 = {
    $schema: "http://json-schema.org/draft-07/schema#",
    type: "object",
    required: allInputs.filter((input) => input.required).map((input) => input.key),
    properties: Object.fromEntries(allInputs.map((input) => [input.key, input.definition])),
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
