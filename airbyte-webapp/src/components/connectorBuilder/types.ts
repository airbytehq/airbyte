import { JSONSchema7 } from "json-schema";

import { SourceDefinitionSpecificationDraft } from "core/domain/connector";
import { PatchedConnectorManifest } from "core/domain/connectorBuilder/PatchedConnectorManifest";
import { DeclarativeStream } from "core/request/ConnectorManifest";

export interface BuilderFormValues {
  global: {
    connectorName: string;
    urlBase: string;
  };
  inputs: Array<{
    key: string;
    required: boolean;
    definition: JSONSchema7;
  }>;
  streams: BuilderStream[];
}

export interface BuilderStream {
  name: string;
  urlPath: string;
  fieldPointer: string[];
  httpMethod: "GET" | "POST";
}

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
