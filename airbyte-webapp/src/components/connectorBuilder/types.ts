import { JSONSchema7 } from "json-schema";
import merge from "lodash/merge";
import semver from "semver";
import * as yup from "yup";

import { AirbyteJSONSchema } from "core/jsonSchema/types";
import {
  ConnectorManifest,
  Spec,
  ApiKeyAuthenticator,
  BasicHttpAuthenticator,
  BearerAuthenticator,
  DeclarativeStream,
  NoAuth,
  SessionTokenAuthenticator,
  RequestOption,
  OAuthAuthenticator,
  HttpRequesterAuthenticator,
  DeclarativeStreamSchemaLoader,
  PageIncrement,
  OffsetIncrement,
  CursorPagination,
  SimpleRetrieverPaginator,
  DefaultPaginatorPageTokenOption,
  DatetimeBasedCursor,
  ListPartitionRouter,
  SubstreamPartitionRouterType,
  SubstreamPartitionRouter,
  ListPartitionRouterType,
  ApiKeyAuthenticatorType,
  SessionTokenAuthenticatorType,
  OAuthAuthenticatorType,
  CursorPaginationType,
  OffsetIncrementType,
  PageIncrementType,
  BearerAuthenticatorType,
  BasicHttpAuthenticatorType,
} from "core/request/ConnectorManifest";

export type EditorView = "ui" | "yaml";

export interface BuilderFormInput {
  key: string;
  required: boolean;
  definition: AirbyteJSONSchema;
}

export type BuilderFormAuthenticator = (
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
  checkStreams: string[];
  version: string;
}

export type RequestOptionOrPathInject = Omit<RequestOption, "type"> | { inject_into: "path" };

export interface BuilderPaginator {
  strategy: PageIncrement | OffsetIncrement | CursorPagination;
  pageTokenOption: RequestOptionOrPathInject;
  pageSizeOption?: RequestOption;
}

export interface BuilderSubstreamPartitionRouter {
  type: SubstreamPartitionRouterType;
  parent_key: string;
  partition_field: string;
  parentStreamReference: string;
  request_option?: RequestOption;
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
  incrementalSync?: DatetimeBasedCursor;
  partitionRouter?: Array<ListPartitionRouter | BuilderSubstreamPartitionRouter>;
  schema?: string;
  unsupportedFields?: Record<string, unknown>;
}

// 0.28.0 is the version where breaking changes got introduced - older states can't be supported
export const OLDEST_SUPPORTED_CDK_VERSION = "0.28.0";

// TODO pull in centralized CDK version configuration to ensure it's consistent across all components
export const CDK_VERSION = "0.28.0";

export function versionSupported(version: string) {
  return semver.satisfies(version, `>= ${OLDEST_SUPPORTED_CDK_VERSION} <=${CDK_VERSION}`);
}

export const DEFAULT_BUILDER_FORM_VALUES: BuilderFormValues = {
  global: {
    connectorName: "Untitled",
    urlBase: "",
    authenticator: { type: "NoAuth" },
  },
  inputs: [],
  inferredInputOverrides: {},
  streams: [],
  checkStreams: [],
  version: CDK_VERSION,
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

export const LIST_PARTITION_ROUTER: ListPartitionRouterType = "ListPartitionRouter";
export const SUBSTREAM_PARTITION_ROUTER: SubstreamPartitionRouterType = "SubstreamPartitionRouter";

export const API_KEY_AUTHENTICATOR: ApiKeyAuthenticatorType = "ApiKeyAuthenticator";
export const BEARER_AUTHENTICATOR: BearerAuthenticatorType = "BearerAuthenticator";
export const BASIC_AUTHENTICATOR: BasicHttpAuthenticatorType = "BasicHttpAuthenticator";
export const SESSION_TOKEN_AUTHENTICATOR: SessionTokenAuthenticatorType = "SessionTokenAuthenticator";
export const OAUTH_AUTHENTICATOR: OAuthAuthenticatorType = "OAuthAuthenticator";

export const CURSOR_PAGINATION: CursorPaginationType = "CursorPagination";
export const OFFSET_INCREMENT: OffsetIncrementType = "OffsetIncrement";
export const PAGE_INCREMENT: PageIncrementType = "PageIncrement";

export const authTypeToKeyToInferredInput: Record<string, Record<string, BuilderFormInput>> = {
  NoAuth: {},
  ApiKeyAuthenticator: {
    api_token: {
      key: "api_key",
      required: true,
      definition: {
        type: "string",
        title: "API Key",
        airbyte_secret: true,
      },
    },
  },
  BearerAuthenticator: {
    api_token: {
      key: "api_key",
      required: true,
      definition: {
        type: "string",
        title: "API Key",
        airbyte_secret: true,
      },
    },
  },
  BasicHttpAuthenticator: {
    username: {
      key: "username",
      required: true,
      definition: {
        type: "string",
        title: "Username",
      },
    },
    password: {
      key: "password",
      required: true,
      definition: {
        type: "string",
        title: "Password",
        airbyte_secret: true,
      },
    },
  },
  OAuthAuthenticator: {
    client_id: {
      key: "client_id",
      required: true,
      definition: {
        type: "string",
        title: "Client ID",
        airbyte_secret: true,
      },
    },
    client_secret: {
      key: "client_secret",
      required: true,
      definition: {
        type: "string",
        title: "Client secret",
        airbyte_secret: true,
      },
    },
    refresh_token: {
      key: "client_refresh_token",
      required: true,
      definition: {
        type: "string",
        title: "Refresh token",
        airbyte_secret: true,
      },
    },
  },
  SessionTokenAuthenticator: {
    username: {
      key: "username",
      required: false,
      definition: {
        type: "string",
        title: "Username",
      },
    },
    password: {
      key: "password",
      required: false,
      definition: {
        type: "string",
        title: "Password",
        airbyte_secret: true,
      },
    },
    session_token: {
      key: "session_token",
      required: false,
      definition: {
        type: "string",
        title: "Session token",
        description: "Session token generated by user (if provided username and password are not required)",
        airbyte_secret: true,
      },
    },
  },
};

export const inferredAuthValues = (type: BuilderFormAuthenticator["type"]): Record<string, string> => {
  return Object.fromEntries(
    Object.entries(authTypeToKeyToInferredInput[type]).map(([authKey, inferredInput]) => {
      return [authKey, interpolateConfigKey(inferredInput.key)];
    })
  );
};

function getInferredInputList(global: BuilderFormValues["global"]): BuilderFormInput[] {
  const authKeyToInferredInput = authTypeToKeyToInferredInput[global.authenticator.type];
  const authKeys = Object.keys(authKeyToInferredInput);
  return authKeys.flatMap((authKey) => {
    if (
      extractInterpolatedConfigKey(Reflect.get(global.authenticator, authKey)) === authKeyToInferredInput[authKey].key
    ) {
      return [authKeyToInferredInput[authKey]];
    }
    return [];
  });
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

const interpolateConfigKey = (key: string): string => {
  return `{{ config['${key}'] }}`;
};

const interpolatedConfigValueRegex = /^{{config\[('|"+)(.+)('|"+)\]}}$/;

export function isInterpolatedConfigKey(str: string | undefined): boolean {
  if (str === undefined) {
    return false;
  }
  const noWhitespaceString = str.replace(/\s/g, "");
  return interpolatedConfigValueRegex.test(noWhitespaceString);
}

function extractInterpolatedConfigKey(str: string | undefined): string | undefined {
  if (str === undefined) {
    return undefined;
  }
  const noWhitespaceString = str.replace(/\s/g, "");
  const regexResult = interpolatedConfigValueRegex.exec(noWhitespaceString);
  if (regexResult === null) {
    return undefined;
  }
  return regexResult[2];
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

export const builderFormValidationSchema = yup.object().shape({
  global: yup.object().shape({
    connectorName: yup.string().required("form.empty.error"),
    urlBase: yup.string().required("form.empty.error"),
    authenticator: yup.object({
      header: yup.mixed().when("type", {
        is: (type: string) => type === API_KEY_AUTHENTICATOR || type === SESSION_TOKEN_AUTHENTICATOR,
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      token_refresh_endpoint: yup.mixed().when("type", {
        is: OAUTH_AUTHENTICATOR,
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      session_token_response_key: yup.mixed().when("type", {
        is: SESSION_TOKEN_AUTHENTICATOR,
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      login_url: yup.mixed().when("type", {
        is: SESSION_TOKEN_AUTHENTICATOR,
        then: yup.string().required("form.empty.error"),
        otherwise: (schema) => schema.strip(),
      }),
      validate_session_url: yup.mixed().when("type", {
        is: SESSION_TOKEN_AUTHENTICATOR,
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
                is: (val: string) => ([OFFSET_INCREMENT, PAGE_INCREMENT] as string[]).includes(val),
                then: yup.number().required("form.empty.error"),
                otherwise: yup.number(),
              }),
              cursor_value: yup.mixed().when("type", {
                is: CURSOR_PAGINATION,
                then: yup.string().required("form.empty.error"),
                otherwise: (schema) => schema.strip(),
              }),
              stop_condition: yup.mixed().when("type", {
                is: CURSOR_PAGINATION,
                then: yup.string(),
                otherwise: (schema) => schema.strip(),
              }),
              start_from_page: yup.mixed().when("type", {
                is: PAGE_INCREMENT,
                then: yup.string(),
                otherwise: (schema) => schema.strip(),
              }),
            })
            .notRequired()
            .default(undefined),
        })
        .notRequired()
        .default(undefined),
      partitionRouter: yup
        .array(
          yup.object().shape({
            cursor_field: yup.mixed().when("type", {
              is: (val: string) => val === LIST_PARTITION_ROUTER,
              then: yup.string().required("form.empty.error"),
              otherwise: (schema) => schema.strip(),
            }),
            values: yup.mixed().when("type", {
              is: LIST_PARTITION_ROUTER,
              then: yup.array().of(yup.string()),
              otherwise: (schema) => schema.strip(),
            }),
            request_option: nonPathRequestOptionSchema,
            parent_key: yup.mixed().when("type", {
              is: SUBSTREAM_PARTITION_ROUTER,
              then: yup.string().required("form.empty.error"),
              otherwise: (schema) => schema.strip(),
            }),
            parentStreamReference: yup.mixed().when("type", {
              is: SUBSTREAM_PARTITION_ROUTER,
              then: yup.string().required("form.empty.error"),
              otherwise: (schema) => schema.strip(),
            }),
            partition_field: yup.mixed().when("type", {
              is: SUBSTREAM_PARTITION_ROUTER,
              then: yup.string().required("form.empty.error"),
              otherwise: (schema) => schema.strip(),
            }),
          })
        )
        .notRequired()
        .default(undefined),
      incrementalSync: yup
        .object()
        .shape({
          request_option: nonPathRequestOptionSchema,
          start_datetime: yup.string().required("form.empty.error"),
          end_datetime: yup.string().required("form.empty.error"),
          step: yup.string().required("form.empty.error"),
          datetime_format: yup.string().required("form.empty.error"),
          start_time_option: nonPathRequestOptionSchema,
          end_time_option: nonPathRequestOptionSchema,
          stream_state_field_start: yup.string(),
          stream_state_field_end: yup.string(),
          lookback_window: yup.string(),
        })
        .notRequired()
        .default(undefined),
    })
  ),
});

function builderAuthenticatorToManifest(globalSettings: BuilderFormValues["global"]): HttpRequesterAuthenticator {
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

function builderPaginatorToManifest(paginator: BuilderStream["paginator"]): SimpleRetrieverPaginator {
  if (!paginator) {
    return { type: "NoPagination" };
  }

  let pageTokenOption: DefaultPaginatorPageTokenOption;
  if (paginator?.pageTokenOption.inject_into === "path") {
    pageTokenOption = { type: "RequestPath" };
  } else {
    pageTokenOption = {
      type: "RequestOption",
      inject_into: paginator.pageTokenOption.inject_into,
      field_name: paginator.pageTokenOption.field_name,
    };
  }
  return {
    type: "DefaultPaginator",
    page_token_option: pageTokenOption,
    page_size_option: paginator.pageSizeOption,
    pagination_strategy: paginator.strategy,
  };
}

function builderStreamPartitionRouterToManifest(
  values: BuilderFormValues,
  partitionRouter: BuilderStream["partitionRouter"],
  visitedStreams: string[]
): Array<ListPartitionRouter | SubstreamPartitionRouter> | undefined {
  if (!partitionRouter) {
    return undefined;
  }
  if (partitionRouter.length === 0) {
    return undefined;
  }
  return partitionRouter.map((subRouter) => {
    if (subRouter.type === "ListPartitionRouter") {
      return subRouter;
    }
    const parentStream = values.streams.find(({ id }) => id === subRouter.parentStreamReference);
    if (!parentStream) {
      return {
        type: "SubstreamPartitionRouter",
        parent_stream_configs: [],
      };
    }
    if (visitedStreams.includes(parentStream.id)) {
      // circular dependency
      return {
        type: "SubstreamPartitionRouter",
        parent_stream_configs: [],
      };
    }
    return {
      type: "SubstreamPartitionRouter",
      parent_stream_configs: [
        {
          type: "ParentStreamConfig",
          parent_key: subRouter.parent_key,
          request_option: subRouter.request_option,
          partition_field: subRouter.partition_field,
          stream: builderStreamToDeclarativeSteam(values, parentStream, visitedStreams),
        },
      ],
    };
  });
}

const EMPTY_SCHEMA = { type: "InlineSchemaLoader", schema: {} } as const;

function parseSchemaString(schema?: string): DeclarativeStreamSchemaLoader {
  if (!schema) {
    return EMPTY_SCHEMA;
  }
  try {
    return { type: "InlineSchemaLoader", schema: JSON.parse(schema) };
  } catch {
    return EMPTY_SCHEMA;
  }
}

function builderStreamToDeclarativeSteam(
  values: BuilderFormValues,
  stream: BuilderStream,
  visitedStreams: string[]
): DeclarativeStream {
  const declarativeStream: DeclarativeStream = {
    type: "DeclarativeStream",
    name: stream.name,
    primary_key: stream.primaryKey,
    schema_loader: parseSchemaString(stream.schema),
    retriever: {
      type: "SimpleRetriever",
      requester: {
        type: "HttpRequester",
        url_base: values.global?.urlBase,
        path: stream.urlPath,
        http_method: stream.httpMethod,
        request_parameters: Object.fromEntries(stream.requestOptions.requestParameters),
        request_headers: Object.fromEntries(stream.requestOptions.requestHeaders),
        request_body_json: Object.fromEntries(stream.requestOptions.requestBody),
        authenticator: builderAuthenticatorToManifest(values.global),
      },
      record_selector: {
        type: "RecordSelector",
        extractor: {
          type: "DpathExtractor",
          field_path: stream.fieldPointer,
        },
      },
      paginator: builderPaginatorToManifest(stream.paginator),
      partition_router: builderStreamPartitionRouterToManifest(values, stream.partitionRouter, [
        ...visitedStreams,
        stream.id,
      ]),
    },
    incremental_sync: stream.incrementalSync,
  };

  return merge({}, declarativeStream, stream.unsupportedFields);
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
    documentation_url: "https://example.org",
    type: "Spec",
  };

  const streamNames = values.streams.map((s) => s.name);
  const validCheckStreamNames = (values.checkStreams ?? []).filter((checkStream) => streamNames.includes(checkStream));
  const correctedCheckStreams =
    validCheckStreamNames.length > 0 ? validCheckStreamNames : streamNames.length > 0 ? [streamNames[0]] : [];

  return merge({
    version: CDK_VERSION,
    type: "DeclarativeSource",
    check: {
      type: "CheckStream",
      stream_names: correctedCheckStreams,
    },
    streams: manifestStreams,
    spec,
  });
};

export const DEFAULT_JSON_MANIFEST_VALUES: ConnectorManifest = convertToManifest(DEFAULT_BUILDER_FORM_VALUES);
