import merge from "lodash/merge";

import { ConnectorManifest, DeclarativeStream } from "core/request/ConnectorManifest";

import { DEFAULT_BUILDER_FORM_VALUES } from "./types";
import { convertToBuilderFormValues } from "./useManifestToBuilderForm";

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

const noOpResolve = (manifest: ConnectorManifest) => {
  return Promise.resolve({ manifest });
};

describe("Conversion throws error when", () => {
  it("resolve throws error", async () => {
    const errorMessage = "Some resolve error message";
    const resolve = (_manifest: ConnectorManifest) => {
      throw new Error(errorMessage);
    };
    const convert = async () => {
      return convertToBuilderFormValues(resolve, {} as ConnectorManifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    await expect(convert).rejects.toThrow(errorMessage);
  });

  it("manifests has incorrect retriever type", async () => {
    const convert = async () => {
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
      return convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    await expect(convert).rejects.toThrow("doesn't use a SimpleRetriever");
  });

  it("manifest has incorrect requester type", async () => {
    const convert = async () => {
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
      return convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    await expect(convert).rejects.toThrow("doesn't use a HttpRequester");
  });

  it("manifest has an authenticator with a non-interpolated secret key", async () => {
    const convert = async () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              requester: {
                authenticator: {
                  type: "ApiKeyAuthenticator",
                  api_token: "abcd1234",
                  header: "API_KEY",
                },
              },
            },
          }),
        ],
      };
      return convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    await expect(convert).rejects.toThrow("api_token value must be of the form {{ config[");
  });

  it("manifest has an OAuthAuthenticator with a refresh_request_body containing non-string values", async () => {
    const convert = () => {
      const manifest: ConnectorManifest = {
        ...baseManifest,
        streams: [
          merge({}, stream1, {
            retriever: {
              requester: {
                authenticator: {
                  type: "OAuthAuthenticator",
                  client_id: "{{ config['client_id'] }}",
                  client_secret: "{{ config['client_secret'] }}",
                  refresh_token: "{{ config['client_refresh_token'] }}",
                  refresh_request_body: {
                    key1: "val1",
                    key2: {
                      a: 1,
                      b: 2,
                    },
                  },
                  token_refresh_endpoint: "https://api.com/refresh_token",
                  grant_type: "client_credentials",
                },
              },
            },
          }),
        ],
      };
      return convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    };
    await expect(convert).rejects.toThrow("OAuthAuthenticator contains a refresh_request_body with non-string values");
  });
});

describe("Conversion successfully results in", () => {
  it("default values if manifest is empty", async () => {
    const formValues = await convertToBuilderFormValues(noOpResolve, baseManifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues).toEqual(DEFAULT_BUILDER_FORM_VALUES);
  });

  it("spec properties converted to inputs if no streams present", async () => {
    const manifest: ConnectorManifest = {
      ...baseManifest,
      spec: {
        type: "Spec",
        connection_specification: {
          $schema: "http://json-schema.org/draft-07/schema#",
          type: "object",
          required: ["api_key"],
          properties: {
            api_key: {
              type: "string",
              title: "API Key",
              airbyte_secret: true,
            },
          },
        },
      },
    };
    const formValues = await convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.inferredInputOverrides).toEqual({});
    expect(formValues.inputs).toEqual([
      {
        key: "api_key",
        required: true,
        definition: manifest.spec?.connection_specification.properties.api_key,
      },
    ]);
  });

  it("spec properties converted to input overrides on matching auth keys", async () => {
    const manifest: ConnectorManifest = {
      ...baseManifest,
      streams: [
        merge({}, stream1, {
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
      spec: {
        type: "Spec",
        connection_specification: {
          $schema: "http://json-schema.org/draft-07/schema#",
          type: "object",
          required: ["api_key"],
          properties: {
            api_key: {
              type: "string",
              title: "API Key",
              airbyte_secret: true,
            },
            numeric_key: {
              type: "number",
              title: "Numeric key",
            },
          },
        },
      },
    };
    const formValues = await convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.inputs).toEqual([
      {
        key: "numeric_key",
        required: false,
        definition: manifest.spec?.connection_specification.properties.numeric_key,
      },
    ]);
    expect(formValues.inferredInputOverrides).toEqual({
      api_key: manifest.spec?.connection_specification.properties.api_key,
    });
  });

  it("request options converted to key-value list", async () => {
    const manifest: ConnectorManifest = {
      ...baseManifest,
      streams: [
        merge({}, stream1, {
          retriever: {
            requester: {
              request_options_provider: {
                type: "InterpolatedRequestOptionsProvider",
                request_parameters: {
                  k1: "v1",
                  k2: "v2",
                },
              },
            },
          },
        }),
      ],
    };
    const formValues = await convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.streams[0].requestOptions.requestParameters).toEqual([
      ["k1", "v1"],
      ["k2", "v2"],
    ]);
  });

  it("primary key string converted to array", async () => {
    const manifest: ConnectorManifest = {
      ...baseManifest,
      streams: [
        merge({}, stream1, {
          primary_key: "id",
          retriever: {
            primary_key: "id",
          },
        }),
      ],
    };
    const formValues = await convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.streams[0].primaryKey).toEqual(["id"]);
  });

  it("cartesian product stream slicer converted to builder cartesian product slicer", async () => {
    const manifest: ConnectorManifest = {
      ...baseManifest,
      streams: [
        merge({}, stream1, {
          retriever: {
            stream_slicer: {
              type: "CartesianProductStreamSlicer",
              stream_slicers: [
                {
                  type: "ListStreamSlicer",
                  cursor_field: "id",
                  slice_values: ["slice1", "slice2"],
                },
                {
                  type: "DatetimeStreamSlicer",
                  cursor_field: "id",
                  datetime_format: "%Y-%m-%d",
                  cursor_granularity: "P1D",
                  end_datetime: "2017-01-25",
                  start_datetime: "2017-01-30",
                  step: "P1D",
                },
              ],
            },
          },
        }),
      ],
    };
    const formValues = await convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.streams[0].streamSlicer).toEqual(manifest.streams[0].retriever.stream_slicer);
  });

  it("substream stream slicer converted to builder substream slicer", async () => {
    const manifest: ConnectorManifest = {
      ...baseManifest,
      streams: [
        stream1,
        merge({}, stream2, {
          retriever: {
            stream_slicer: {
              type: "SubstreamSlicer",
              parent_stream_configs: [
                {
                  type: "ParentStreamConfig",
                  parent_key: "key",
                  stream: stream1,
                  stream_slice_field: "field",
                },
              ],
            },
          },
        }),
      ],
    };
    const formValues = await convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.streams[1].streamSlicer).toEqual({
      type: "SubstreamSlicer",
      parent_key: "key",
      stream_slice_field: "field",
      parentStreamReference: "0",
    });
  });

  it("schema loader converted to schema", async () => {
    const manifest: ConnectorManifest = {
      ...baseManifest,
      streams: [
        merge({}, stream1, {
          schema_loader: {
            type: "InlineSchemaLoader",
            schema: {
              key: "value",
            },
          },
        }),
      ],
    };
    const formValues = await convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.streams[0].schema).toEqual(
      `{
  "key": "value"
}`
    );
  });

  it("stores unsupported fields", async () => {
    const manifest: ConnectorManifest = {
      ...baseManifest,
      streams: [
        merge({}, stream1, {
          transformations: [
            {
              type: "AddFields",
              fields: ["id"],
            },
          ],
          checkpoint_interval: 123,
          retriever: {
            requester: {
              error_handler: {
                type: "DefaultErrorHandler",
                max_retries: 3,
              },
            },
            record_selector: {
              record_filter: {
                type: "RecordFilter",
                condition: "true",
              },
            },
          },
        }),
      ],
    };
    const formValues = await convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.streams[0].unsupportedFields).toEqual({
      transformations: manifest.streams[0].transformations,
      checkpoint_interval: manifest.streams[0].checkpoint_interval,
      retriever: {
        requester: {
          error_handler: manifest.streams[0].retriever.requester.error_handler,
        },
        record_selector: {
          record_filter: manifest.streams[0].retriever.record_selector.record_filter,
        },
      },
    });
  });

  it("OAuth authenticator refresh_request_body converted to array", async () => {
    const manifest: ConnectorManifest = {
      ...baseManifest,
      streams: [
        merge({}, stream1, {
          retriever: {
            requester: {
              authenticator: {
                type: "OAuthAuthenticator",
                client_id: "{{ config['client_id'] }}",
                client_secret: "{{ config['client_secret'] }}",
                refresh_token: "{{ config['client_refresh_token'] }}",
                refresh_request_body: {
                  key1: "val1",
                  key2: "val2",
                },
                token_refresh_endpoint: "https://api.com/refresh_token",
                grant_type: "client_credentials",
              },
            },
          },
        }),
      ],
    };
    const formValues = await convertToBuilderFormValues(noOpResolve, manifest, DEFAULT_BUILDER_FORM_VALUES);
    expect(formValues.global.authenticator).toEqual({
      type: "OAuthAuthenticator",
      client_id: "{{ config['client_id'] }}",
      client_secret: "{{ config['client_secret'] }}",
      refresh_token: "{{ config['client_refresh_token'] }}",
      refresh_request_body: [
        ["key1", "val1"],
        ["key2", "val2"],
      ],
      token_refresh_endpoint: "https://api.com/refresh_token",
      grant_type: "client_credentials",
    });
  });
});
