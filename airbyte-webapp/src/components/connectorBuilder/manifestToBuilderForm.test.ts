import { load } from "js-yaml";
import merge from "lodash/merge";

import { ConnectorManifest, DeclarativeStream } from "core/request/ConnectorManifest";

import { convertToBuilderFormValues } from "./manifestToBuilderForm";
import { DEFAULT_BUILDER_FORM_VALUES } from "./types";

const baseManifest: ConnectorManifest = {
  type: "DeclarativeSource",
  version: "0.1.0",
  check: {
    type: "CheckStream",
    stream_names: [],
  },
  streams: [],
};

const stream1: DeclarativeStream = {
  type: "DeclarativeStream",
  name: "stream1",
  retriever: {
    type: "SimpleRetriever",
    name: "stream1",
    record_selector: {
      type: "RecordSelector",
      extractor: {
        type: "DpathExtractor",
        field_pointer: [],
      },
    },
    requester: {
      type: "HttpRequester",
      name: "stream1",
      url_base: "https://url.com",
      path: "/stream-1-path",
    },
  },
};

const stream2: DeclarativeStream = merge({}, stream1, {
  name: "stream2",
  retriever: {
    name: "stream2",
    requester: {
      name: "stream2",
      path: "/stream-2-path",
    },
  },
});

describe("Conversion throws error when", () => {
  it("streamListErrorMessage is present", () => {
    const streamListErrorMessage = "Some error message";
    const convert = () => {
      convertToBuilderFormValues({} as ConnectorManifest, DEFAULT_BUILDER_FORM_VALUES, streamListErrorMessage);
    };
    expect(convert).toThrow(streamListErrorMessage);
  });

  it("manifest contains refs", () => {
    const convert = () => {
      // have to use a string manifest here, because refs aren't in the schema
      const manifest = `
        version: "0.1.0"
        definitions:
          retriever:
            name: "pokemon"
            primary_key: "id"
            requester:
              name: "pokemon"
              path: "/pokemon/{{config['pokemon_name']}}"
              url_base: "https://pokeapi.co/api/v2"
              http_method: "GET"
            record_selector:
              extractor:
                type: DpathExtractor
                field_pointer: []
        streams:
          - type: DeclarativeStream
            name: "pokemon"
            primary_key: "id"
            schema_loader:
              type: InlineSchemaLoader
              schema: {}
            retriever:
              $ref: "*ref(definitions.retriever)"
        check:
          stream_names:
            - "pokemon"`;
      convertToBuilderFormValues(load(manifest) as ConnectorManifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("contains refs");
  });

  it("manifest contains options", () => {
    // have to use a string manifest here, because using $options results in an invalid schema
    const convert = () => {
      const manifest = `
        version: "0.1.0"
        streams:
          - type: DeclarativeStream
            $options:
              name: "pokemon"
              primary_key: "id"
              path: "/pokemon/{{config['pokemon_name']}}"
            retriever:
              requester:
                url_base: "https://pokeapi.co/api/v2"
                http_method: "GET"
              record_selector:
                extractor:
                  type: DpathExtractor
                  field_pointer: []
        check:
          stream_names:
            - "pokemon"`;
      convertToBuilderFormValues(load(manifest) as ConnectorManifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("contains refs");
  });

  it("manifests has incorrect retriever type", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          {
            type: "DeclarativeStream",
            name: "firstStream",
            retriever: {
              type: "CustomRetriever",
              class_name: "some_python_class",
            },
          },
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("doesn't use a SimpleRetriever");
  });

  it("manifest has incorrect requester type", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              requester: {
                type: "CustomRequester",
                class_name: "some_python_class",
              },
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("doesn't use a HttpRequester");
  });

  it("manifest has inconsistent stream names", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              name: "other name",
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("name is not consistent");
  });

  it("manifest has inconsistent authenticators", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              requester: {
                authenticator: {
                  type: "BearerAuthenticator",
                  api_token: "{{ config['api_key'] }}",
                },
              },
            },
          }),
          merge({}, stream2, {
            retriever: {
              requester: {
                authenticator: {
                  type: "ApiKeyAuthenticator",
                  api_token: "{{ config['api_key'] }}",
                  header: "API_KEY",
                },
              },
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("authenticator does not match");
  });

  it("manifest has inconsistent url_bases", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          stream1,
          merge({}, stream2, {
            retriever: {
              requester: {
                url_base: "https://differenturl.com",
              },
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("url_base does not match");
  });

  it("manifest has invalid http_method", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              requester: {
                http_method: "PATCH",
              },
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("http_method is not GET or POST");
  });

  it("manifest has incorrect extractor type", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              record_selector: {
                extractor: {
                  type: "CustomExtractor",
                },
              },
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("doesn't use a DpathExtractor");
  });

  it("manifest has incorrect request_options_provider type", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              requester: {
                request_options_provider: {
                  type: "CustomRequestOptionsProvider",
                },
              },
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("doesn't use a InterpolatedRequestOptionsProvider");
  });

  it("manifest has invalid stream_slicer type", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              stream_slicer: {
                type: "CustomStreamSlicer",
              },
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("contains a CustomStreamSlicer");
  });

  it("manifest has invalid start_datetime", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              stream_slicer: {
                type: "DatetimeStreamSlicer",
                start_datetime: {
                  type: "MinMaxDatetime",
                },
              },
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow(/start_datetime.*not set to a string value/);
  });

  it("manifest has inconsistent primary_keys", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            primary_key: ["id"],
            retriever: {
              primary_key: ["name"],
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("primary_key is not consistent");
  });

  it("manifest has nested primary_keys", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            primary_key: [["id", "name"]],
            retriever: {
              primary_key: [["id", "name"]],
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("primary_key contains nested arrays");
  });

  it("manifest doesn't define page_token_option", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              paginator: {},
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("paginator does not define a page_token_option");
  });

  it("manifest has inconsistent paginator url_base", () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              paginator: {
                page_token_option: {
                  type: "RequestOption",
                  inject_into: "request_parameter",
                },
                url_base: "https://otherurl.com",
              },
            },
          }),
        ],
      };
      convertToBuilderFormValues(manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    expect(convert).toThrow("paginator.url_base does not match");
  });
});

describe("Conversion successfully results in", () => {
  it("default values if manifest is empty", () => {
    const manifest = `
      version: "0.1.0"
      check:
        stream_names: []
      streams: []`;
    const formValues = convertToBuilderFormValues(load(manifest) as ConnectorManifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues).toEqual(DEFAULT_BUILDER_FORM_VALUES);
  });

  it("spec properties converted to inputs if no streams present", () => {
    const manifest = `
      version: "0.1.0"
      check:
        stream_names: []
      streams: []
      spec:
        connection_specification:
          $schema: http://json-schema.org/draft-07/schema#
          type: object
          required:
            - api_key
          properties:
            api_key:
              type: string
              title: API Key
              airbyte_secret: true`;
    const formValues = convertToBuilderFormValues(load(manifest) as ConnectorManifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.inferredInputOverrides).toEqual({});
    expect(formValues.inputs).toEqual([
      {
        key: "api_key",
        required: true,
        definition: {
          type: "string",
          title: "API Key",
          airbyte_secret: true,
        },
      },
    ]);
  });

  it("spec properties converted to input overrides on matching auth keys", () => {
    const manifest = `
      version: "0.1.0"
      check:
        stream_names: []
      streams:
        - name: firstStream
          retriever:
            type: SimpleRetriever
            name: firstStream
            record_selector:
              type: RecordSelector
              extractor:
                type: DpathExtractor
                field_pointer: []
            requester:
              type: HttpRequester
              name: firstStream
              authenticator:
                type: ApiKeyAuthenticator
                api_token: '{{ config[''api_key''] }}'
                header: ''
      spec:
        connection_specification:
          $schema: http://json-schema.org/draft-07/schema#
          type: object
          required:
            - api_key
          properties:
            api_key:
              type: string
              title: API Key
              airbyte_secret: true
            other_key:
              type: string
              title: Other key`;
    const formValues = convertToBuilderFormValues(load(manifest) as ConnectorManifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.inputs).toEqual([
      {
        key: "other_key",
        required: false,
        definition: {
          type: "string",
          title: "Other key",
        },
      },
    ]);
    expect(formValues.inferredInputOverrides).toEqual({
      api_key: {
        type: "string",
        title: "API Key",
        airbyte_secret: true,
      },
    });
  });
});
