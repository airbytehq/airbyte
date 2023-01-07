import { JSONSchema7 } from "json-schema";
import * as yup from "yup";

import { AirbyteJSONSchema } from "core/jsonSchema/types";
import {
  ConnectorManifest,
  InterpolatedRequestOptionsProvider,
  Spec,
  ApiKeyAuthenticator,
  BasicHttpAuthenticator,
  BearerAuthenticator,
  DeclarativeStream,
  NoAuth,
  SessionTokenAuthenticator,
  RequestOption,
  OAuthAuthenticator,
  DefaultPaginatorPaginationStrategy,
  SimpleRetrieverStreamSlicer,
  HttpRequesterAuthenticator,
  SubstreamSlicer,
  SubstreamSlicerType,
  CartesianProductStreamSlicer,
} from "core/request/ConnectorManifest";

export interface BuilderFormInput {
  key: string;
  required: boolean;
  definition: AirbyteJSONSchema;
}

type BuilderFormAuthenticator = (
  | NoAuth
  | (Omit<OAuthAuthenticator, "refresh_request_body"> & {
      refresh_request_body: Array<[string, string]>;
    })
  | ApiKeyAuthenticator
  | BearerAuthenticator
  | BasicHttpAuthenticator
  | SessionTokenAuthenticator
) & { type: string };

export interface BuilderFormValues {
  global: {
    connectorName: string;
    urlBase: string;
    authenticator: BuilderFormAuthenticator;
  };
  inputs: BuilderFormInput[];
  inferredInputOverrides: Record<string, Partial<AirbyteJSONSchema>>;
  streams: BuilderStream[];
}

export interface BuilderPaginator {
  strategy: DefaultPaginatorPaginationStrategy;
  pageTokenOption: RequestOption;
  pageSizeOption?: RequestOption;
}

export interface BuilderSubstreamSlicer {
  type: SubstreamSlicerType;
  parent_key: string;
  stream_slice_field: string;
  parentStreamReference: string;
  request_option?: RequestOption;
}

export interface BuilderCartesianProductSlicer {
  type: "CartesianProductStreamSlicer";
  stream_slicers: Array<
    Exclude<SimpleRetrieverStreamSlicer, SubstreamSlicer | CartesianProductStreamSlicer> | BuilderSubstreamSlicer
  >;
}

export interface BuilderStream {
  id: string;
  name: string;
  urlPath: string;
  fieldPointer: string[];
  primaryKey: string[];
  httpMethod: "GET" | "POST";
  requestOptions: {
    requestParameters: Array<[string, string]>;
    requestHeaders: Array<[string, string]>;
    requestBody: Array<[string, string]>;
  };
  paginator?: BuilderPaginator;
  streamSlicer?:
    | Exclude<SimpleRetrieverStreamSlicer, SubstreamSlicer | CartesianProductStreamSlicer>
    | BuilderSubstreamSlicer
    | BuilderCartesianProductSlicer;
  schema?: string;
}

export const DEFAULT_BUILDER_FORM_VALUES: BuilderFormValues = {
  global: {
    connectorName: "",
    urlBase: "",
    authenticator: { type: "NoAuth" },
  },
  inputs: [],
  inferredInputOverrides: {},
  streams: [],
};

export const DEFAULT_BUILDER_STREAM_VALUES: Omit<BuilderStream, "id"> = {
  name: "",
  urlPath: "",
  fieldPointer: [],
  primaryKey: [],
  httpMethod: "GET",
  requestOptions: {
    requestParameters: [],
    requestHeaders: [],
    requestBody: [],
  },
};

function getInferredInputList(global: BuilderFormValues["global"]): BuilderFormInput[] {
  if (global.authenticator.type === "ApiKeyAuthenticator") {
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
  if (global.authenticator.type === "BearerAuthenticator") {
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
  if (global.authenticator.type === "BasicHttpAuthenticator") {
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
  if (global.authenticator.type === "OAuthAuthenticator") {
    return [
      {
        key: "client_id",
        required: true,
        definition: {
          type: "string",
          title: "Client ID",
          airbyte_secret: true,
        },
      },
      {
        key: "client_secret",
        required: true,
        definition: {
          type: "string",
          title: "Client secret",
          airbyte_secret: true,
        },
      },
      {
        key: "refresh_token",
        required: true,
        definition: {
          type: "string",
          title: "Refresh token",
          airbyte_secret: true,
        },
      },
    ];
  }
  if (global.authenticator.type === "SessionTokenAuthenticator") {
    return [
      {
        key: "username",
        required: false,
        definition: {
          type: "string",
          title: "Username",
        },
      },
      {
        key: "password",
        required: false,
        definition: {
          type: "string",
          title: "Password",
          airbyte_secret: true,
        },
      },
      {
        key: "session_token",
        required: false,
        definition: {
          type: "string",
          title: "Session token",
          description: "Session token generated by user (if provided username and password are not required)",
          airbyte_secret: true,
        },
      },
    ];
  }
  return [];
}

export function getInferredInputs(
  global: BuilderFormValues["global"],
  inferredInputOverrides: BuilderFormValues["inferredInputOverrides"]
): BuilderFormInput[] {
  const inferredInputs = getInferredInputList(global);
  return inferredInputs.map((input) =>
    inferredInputOverrides[input.key]
      ? {
          ...input,
          definition: { ...input.definition, ...inferredInputOverrides[input.key] },
        }
      : input
  );
}

export const injectIntoValues = ["request_parameter", "header", "path", "body_data", "body_json"];
const nonPathRequestOptionSchema = yup
  .object()
  .shape({
    inject_into: yup.mixed().oneOf(injectIntoValues.filter((val) => val !== "path")),
    field_name: yup.string().required("form.empty.error"),
  })
  .notRequired()
  .default(undefined);

// eslint-disable-next-line no-useless-escape
export const timeDeltaRegex = /^(([\.\d]+?)y)?(([\.\d]+?)m)?(([\.\d]+?)w)?(([\.\d]+?)d)?$/;

const regularSlicerShape = {
  cursor_field: yup.mixed().when("type", {
    is: (val: string) => val !== "SubstreamSlicer" && val !== "CartesianProductStreamSlicer",
    then: yup.string().required("form.empty.error"),
    otherwise: (schema) => schema.strip(),
  }),
  slice_values: yup.mixed().when("type", {
    is: "ListStreamSlicer",
    then: yup.array().of(yup.string()),
    otherwise: (schema) => schema.strip(),
  }),
  request_option: nonPathRequestOptionSchema,
  start_datetime: yup.mixed().when("type", {
    is: "DatetimeStreamSlicer",
    then: yup.string().required("form.empty.error"),
    otherwise: (schema) => schema.strip(),
  }),
  end_datetime: yup.mixed().when("type", {
    is: "DatetimeStreamSlicer",
    then: yup.string().required("form.empty.error"),
    otherwise: (schema) => schema.strip(),
  }),
  step: yup.mixed().when("type", {
    is: "DatetimeStreamSlicer",
    then: yup.string().matches(timeDeltaRegex, "form.pattern.error").required("form.empty.error"),
    otherwise: (schema) => schema.strip(),
  }),
  datetime_format: yup.mixed().when("type", {
    is: "DatetimeStreamSlicer",
    then: yup.string().required("form.empty.error"),
    otherwise: (schema) => schema.strip(),
  }),
  start_time_option: yup.mixed().when("type", {
    is: "DatetimeStreamSlicer",
    then: nonPathRequestOptionSchema,
    otherwise: (schema) => schema.strip(),
  }),
  end_time_option: yup.mixed().when("type", {
    is: "DatetimeStreamSlicer",
    then: nonPathRequestOptionSchema,
    otherwise: (schema) => schema.strip(),
  }),
  stream_state_field_start: yup.mixed().when("type", {
    is: "DatetimeStreamSlicer",
    then: yup.string(),
    otherwise: (schema) => schema.strip(),
  }),
  stream_state_field_end: yup.mixed().when("type", {
    is: "DatetimeStreamSlicer",
    then: yup.string(),
    otherwise: (schema) => schema.strip(),
  }),
  lookback_window: yup.mixed().when("type", {
    is: "DatetimeStreamSlicer",
    then: yup.string(),
    otherwise: (schema) => schema.strip(),
  }),
  parent_key: yup.mixed().when("type", {
    is: "SubstreamSlicer",
    then: yup.string().required("form.empty.error"),
    otherwise: (schema) => schema.strip(),
  }),
  parentStreamReference: yup.mixed().when("type", {
    is: "SubstreamSlicer",
    then: yup.string().required("form.empty.error"),
    otherwise: (schema) => schema.strip(),
  }),
  stream_slice_field: yup.mixed().when("type", {
    is: "SubstreamSlicer",
    then: yup.string().required("form.empty.error"),
    otherwise: (schema) => schema.strip(),
  }),
};

export const builderFormValidationSchema = yup.object().shape({
  global: yup.object().shape({
    connectorName: yup.string().required("form.empty.error"),
    urlBase: yup.string().required("form.empty.error"),
    authenticator: yup.object({
      header: yup.mixed().when("type", {
        is: (type: string) => type === "ApiKeyAuthenticator" || type === "SessionTokenAuthenticator",
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      token_refresh_endpoint: yup.mixed().when("type", {
        is: "OAuthAuthenticator",
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      session_token_response_key: yup.mixed().when("type", {
        is: "SessionTokenAuthenticator",
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      login_url: yup.mixed().when("type", {
        is: "SessionTokenAuthenticator",
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      validate_session_url: yup.mixed().when("type", {
        is: "SessionTokenAuthenticator",
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
      primaryKey: yup.array().of(yup.string()),
      httpMethod: yup.mixed().oneOf(["GET", "POST"]),
      requestOptions: yup.object().shape({
        requestParameters: yup.array().of(yup.array().of(yup.string())),
        requestHeaders: yup.array().of(yup.array().of(yup.string())),
        requestBody: yup.array().of(yup.array().of(yup.string())),
      }),
      schema: yup.string().test({
        test: (val: string | undefined) => {
          if (!val) {
            return true;
          }
          try {
            JSON.parse(val);
            return true;
          } catch {
            return false;
          }
        },
        message: "connectorBuilder.invalidSchema",
      }),
      paginator: yup
        .object()
        .shape({
          pageSizeOption: nonPathRequestOptionSchema,
          pageTokenOption: yup.object().shape({
            inject_into: yup.mixed().oneOf(injectIntoValues),
            field_name: yup.mixed().when("inject_into", {
              is: "path",
              then: (schema) => schema.strip(),
              otherwise: yup.string().required("form.empty.error"),
            }),
          }),
          strategy: yup
            .object({
              page_size: yup.mixed().when("type", {
                is: (val: string) => ["OffsetIncrement", "PageIncrement"].includes(val),
                then: yup.number().required("form.empty.error"),
                otherwise: yup.number(),
              }),
              cursor_value: yup.mixed().when("type", {
                is: "CursorPagination",
                then: yup.string().required("form.empty.error"),
                otherwise: (schema) => schema.strip(),
              }),
              stop_condition: yup.mixed().when("type", {
                is: "CursorPagination",
                then: yup.string(),
                otherwise: (schema) => schema.strip(),
              }),
              start_from_page: yup.mixed().when("type", {
                is: "PageIncrement",
                then: yup.string(),
                otherwise: (schema) => schema.strip(),
              }),
            })
            .notRequired()
            .default(undefined),
        })
        .notRequired()
        .default(undefined),
      streamSlicer: yup
        .object()
        .shape({
          ...regularSlicerShape,
          stream_slicers: yup.mixed().when("type", {
            is: "CartesianProductStreamSlicer",
            then: yup.array().of(yup.object().shape(regularSlicerShape)),
            otherwise: (schema) => schema.strip(),
          }),
        })
        .notRequired()
        .default(undefined),
    })
  ),
});

function builderFormAuthenticatorToAuthenticator(
  globalSettings: BuilderFormValues["global"]
): HttpRequesterAuthenticator {
  if (globalSettings.authenticator.type === "OAuthAuthenticator") {
    return {
      ...globalSettings.authenticator,
      refresh_request_body: Object.fromEntries(globalSettings.authenticator.refresh_request_body),
    };
  }
  if (globalSettings.authenticator.type === "SessionTokenAuthenticator") {
    return {
      ...globalSettings.authenticator,
      api_url: globalSettings.urlBase,
    };
  }
  return globalSettings.authenticator as HttpRequesterAuthenticator;
}

function builderFormStreamSlicerToStreamSlicer(
  values: BuilderFormValues,
  slicer: BuilderStream["streamSlicer"],
  visitedStreams: string[]
): SimpleRetrieverStreamSlicer | undefined {
  if (!slicer) {
    return undefined;
  }
  if (slicer.type !== "SubstreamSlicer" && slicer.type !== "CartesianProductStreamSlicer") {
    return slicer;
  }
  if (slicer.type === "CartesianProductStreamSlicer") {
    return {
      type: "CartesianProductStreamSlicer",
      stream_slicers: slicer.stream_slicers.map((subSlicer) => {
        return builderFormStreamSlicerToStreamSlicer(values, subSlicer, visitedStreams);
      }),
    } as unknown as CartesianProductStreamSlicer;
  }
  const parentStream = values.streams.find(({ id }) => id === slicer.parentStreamReference);
  if (!parentStream) {
    return {
      type: "SubstreamSlicer",
      parent_stream_configs: [],
    };
  }
  if (visitedStreams.includes(parentStream.id)) {
    // circular dependency
    return {
      type: "SubstreamSlicer",
      parent_stream_configs: [],
    };
  }
  return {
    type: "SubstreamSlicer",
    parent_stream_configs: [
      {
        type: "ParentStreamConfig",
        parent_key: slicer.parent_key,
        request_option: slicer.request_option,
        stream_slice_field: slicer.stream_slice_field,
        stream: builderStreamToDeclarativeSteam(values, parentStream, visitedStreams),
      },
    ],
  };
}

function parseSchemaString(schema?: string) {
  if (!schema) {
    return undefined;
  }
  try {
    return { type: "InlineSchemaLoader", schema: JSON.parse(schema) };
  } catch {
    return undefined;
  }
}

function builderStreamToDeclarativeSteam(
  values: BuilderFormValues,
  stream: BuilderStream,
  visitedStreams: string[]
): DeclarativeStream {
  return {
    type: "DeclarativeStream",
    name: stream.name,
    primary_key: stream.primaryKey,
    schema_loader: parseSchemaString(stream.schema),
    retriever: {
      type: "SimpleRetriever",
      name: stream.name,
      primary_key: stream.primaryKey,
      requester: {
        type: "HttpRequester",
        name: stream.name,
        url_base: values.global?.urlBase,
        path: stream.urlPath,
        request_options_provider: {
          // TODO can't declare type here because the server will error out, but the types dictate it is needed. Fix here once server is fixed.
          // type: "InterpolatedRequestOptionsProvider",
          request_parameters: Object.fromEntries(stream.requestOptions.requestParameters),
          request_headers: Object.fromEntries(stream.requestOptions.requestHeaders),
          request_body_json: Object.fromEntries(stream.requestOptions.requestBody),
        } as InterpolatedRequestOptionsProvider,
        authenticator: builderFormAuthenticatorToAuthenticator(values.global),
      },
      record_selector: {
        type: "RecordSelector",
        extractor: {
          type: "DpathExtractor",
          field_pointer: stream.fieldPointer,
        },
      },
      paginator: stream.paginator
        ? {
            type: "DefaultPaginator",
            page_token_option: {
              ...stream.paginator.pageTokenOption,
              // ensures that empty field_name is not set, as connector builder server cannot accept a field_name if inject_into is set to 'path'
              field_name: stream.paginator.pageTokenOption?.field_name
                ? stream.paginator.pageTokenOption?.field_name
                : undefined,
            },
            page_size_option: stream.paginator.pageSizeOption,
            pagination_strategy: stream.paginator.strategy,
            url_base: values.global?.urlBase,
          }
        : { type: "NoPagination" },
      stream_slicer: builderFormStreamSlicerToStreamSlicer(values, stream.streamSlicer, [...visitedStreams, stream.id]),
    },
  };
}

export const convertToManifest = (values: BuilderFormValues): ConnectorManifest => {
  const manifestStreams: DeclarativeStream[] = values.streams.map((stream) =>
    builderStreamToDeclarativeSteam(values, stream, [])
  );

  const allInputs = [...values.inputs, ...getInferredInputs(values.global, values.inferredInputOverrides)];

  const specSchema: JSONSchema7 = {
    $schema: "http://json-schema.org/draft-07/schema#",
    type: "object",
    required: allInputs.filter((input) => input.required).map((input) => input.key),
    properties: Object.fromEntries(allInputs.map((input) => [input.key, input.definition])),
    additionalProperties: true,
  };

  const spec: Spec = {
    connection_specification: specSchema,
    documentation_url: "",
    type: "Spec",
  };

  return {
    version: "0.1.0",
    type: "DeclarativeSource",
    check: {
      type: "CheckStream",
      stream_names: [],
    },
    streams: manifestStreams,
    spec,
  };
};
