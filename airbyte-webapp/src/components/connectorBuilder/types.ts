import { ConnectorManifest, DeclarativeStream } from "core/request/ConnectorManifest";

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
}

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
