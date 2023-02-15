import cloneDeep from "lodash/cloneDeep";
import isEqual from "lodash/isEqual";

import { AirbyteJSONSchema } from "core/jsonSchema/types";
import { ResolveManifest } from "core/request/ConnectorBuilderClient";
import {
  ConnectorManifest,
  DatetimeBasedCursor,
  DeclarativeStream,
  DeclarativeStreamIncrementalSync,
  DeclarativeStreamSchemaLoader,
  DpathExtractor,
  HttpRequester,
  HttpRequesterAuthenticator,
  SimpleRetriever,
  SimpleRetrieverPaginator,
  SimpleRetrieverPartitionRouter,
  SimpleRetrieverPartitionRouterAnyOfItem,
  Spec,
} from "core/request/ConnectorManifest";
import { useResolveManifest } from "services/connectorBuilder/ConnectorBuilderApiService";

import {
  authTypeToKeyToInferredInput,
  BuilderFormAuthenticator,
  BuilderFormValues,
  BuilderPaginator,
  BuilderStream,
  CDK_VERSION,
  DEFAULT_BUILDER_FORM_VALUES,
  DEFAULT_BUILDER_STREAM_VALUES,
  isInterpolatedConfigKey,
  OLDEST_SUPPORTED_CDK_VERSION,
  RequestOptionOrPathInject,
  versionSupported,
} from "./types";
import { formatJson } from "./utils";

export const useManifestToBuilderForm = () => {
  const { resolve } = useResolveManifest();
  return { convertToBuilderFormValues: convertToBuilderFormValues.bind(this, resolve) };
};

export const convertToBuilderFormValues = async (
  resolve: (manifest: ConnectorManifest) => Promise<ResolveManifest>,
  manifest: ConnectorManifest,
  currentBuilderFormValues: BuilderFormValues
) => {
  let resolveResult: ResolveManifest;
  try {
    resolveResult = await resolve(manifest);
  } catch (e) {
    let errorMessage = e.message;
    if (errorMessage[0] === '"') {
      errorMessage = errorMessage.substring(1, errorMessage.length);
    }
    if (errorMessage.slice(-1) === '"') {
      errorMessage = errorMessage.substring(0, errorMessage.length - 1);
    }
    throw new ManifestCompatibilityError(undefined, errorMessage.trim());
  }
  const resolvedManifest = resolveResult.manifest as ConnectorManifest;

  if (!versionSupported(resolvedManifest.version)) {
    throw new ManifestCompatibilityError(
      undefined,
      `Connector builder UI only supports manifests version >= ${OLDEST_SUPPORTED_CDK_VERSION} and <= ${CDK_VERSION}, encountered ${resolvedManifest.version}`
    );
  }

  const builderFormValues = cloneDeep(DEFAULT_BUILDER_FORM_VALUES);
  builderFormValues.global.connectorName = currentBuilderFormValues.global.connectorName;
  builderFormValues.checkStreams = resolvedManifest.check.stream_names;

  const streams = resolvedManifest.streams;
  if (streams === undefined || streams.length === 0) {
    const { inputs, inferredInputOverrides } = manifestSpecAndAuthToBuilder(resolvedManifest.spec, undefined);
    builderFormValues.inputs = inputs;
    builderFormValues.inferredInputOverrides = inferredInputOverrides;

    return builderFormValues;
  }

  assertType<SimpleRetriever>(streams[0].retriever, "SimpleRetriever", streams[0].name);
  assertType<HttpRequester>(streams[0].retriever.requester, "HttpRequester", streams[0].name);
  builderFormValues.global.urlBase = streams[0].retriever.requester.url_base;

  const { inputs, inferredInputOverrides, auth } = manifestSpecAndAuthToBuilder(
    resolvedManifest.spec,
    streams[0].retriever.requester.authenticator
  );
  builderFormValues.inputs = inputs;
  builderFormValues.inferredInputOverrides = inferredInputOverrides;
  builderFormValues.global.authenticator = auth;

  const serializedStreamToIndex = Object.fromEntries(streams.map((stream, index) => [JSON.stringify(stream), index]));
  builderFormValues.streams = streams.map((stream, index) =>
    manifestStreamToBuilder(
      stream,
      index,
      serializedStreamToIndex,
      streams[0].retriever.requester.url_base,
      streams[0].retriever.requester.authenticator
    )
  );

  return builderFormValues;
};

const manifestStreamToBuilder = (
  stream: DeclarativeStream,
  index: number,
  serializedStreamToIndex: Record<string, number>,
  firstStreamUrlBase: string,
  firstStreamAuthenticator?: HttpRequesterAuthenticator
): BuilderStream => {
  assertType<SimpleRetriever>(stream.retriever, "SimpleRetriever", stream.name);
  const retriever = stream.retriever;

  assertType<HttpRequester>(retriever.requester, "HttpRequester", stream.name);
  const requester = retriever.requester;

  if (
    !firstStreamAuthenticator || firstStreamAuthenticator.type === "NoAuth"
      ? requester.authenticator && requester.authenticator.type !== "NoAuth"
      : !isEqual(retriever.requester.authenticator, firstStreamAuthenticator)
  ) {
    throw new ManifestCompatibilityError(stream.name, "authenticator does not match the first stream's");
  }

  if (retriever.requester.url_base !== firstStreamUrlBase) {
    throw new ManifestCompatibilityError(stream.name, "url_base does not match the first stream's");
  }

  if (![undefined, "GET", "POST"].includes(requester.http_method)) {
    throw new ManifestCompatibilityError(stream.name, "http_method is not GET or POST");
  }

  assertType<DpathExtractor>(retriever.record_selector.extractor, "DpathExtractor", stream.name);

  return {
    ...DEFAULT_BUILDER_STREAM_VALUES,
    id: index.toString(),
    name: stream.name ?? "",
    urlPath: requester.path,
    httpMethod: (requester.http_method as "GET" | "POST" | undefined) ?? "GET",
    fieldPointer: retriever.record_selector.extractor.field_path as string[],
    requestOptions: {
      requestParameters: Object.entries(requester.request_parameters ?? {}),
      requestHeaders: Object.entries(requester.request_headers ?? {}),
      // try getting this from request_body_data first, and if not set then pull from request_body_json
      requestBody: Object.entries(requester.request_body_data ?? requester.request_body_json ?? {}),
    },
    primaryKey: manifestPrimaryKeyToBuilder(stream),
    paginator: manifestPaginatorToBuilder(retriever.paginator, stream.name),
    incrementalSync: manifestIncrementalSyncToBuilder(stream.incremental_sync, stream.name),
    partitionRouter: manifestPartitionRouterToBuilder(retriever.partition_router, serializedStreamToIndex, stream.name),
    schema: manifestSchemaLoaderToBuilderSchema(stream.schema_loader),
    unsupportedFields: {
      transformations: stream.transformations,
      retriever: {
        requester: {
          error_handler: stream.retriever.requester.error_handler,
        },
        record_selector: {
          record_filter: stream.retriever.record_selector.record_filter,
        },
      },
    },
  };
};

function manifestPartitionRouterToBuilder(
  partitionRouter: SimpleRetrieverPartitionRouter | SimpleRetrieverPartitionRouterAnyOfItem | undefined,
  serializedStreamToIndex: Record<string, number>,
  streamName?: string
): BuilderStream["partitionRouter"] {
  if (partitionRouter === undefined) {
    return undefined;
  }

  if (Array.isArray(partitionRouter)) {
    return partitionRouter.flatMap(
      (subRouter) => manifestPartitionRouterToBuilder(subRouter, serializedStreamToIndex, streamName) || []
    );
  }

  if (partitionRouter.type === undefined) {
    throw new ManifestCompatibilityError(streamName, "partition_router has no type");
  }

  if (partitionRouter.type === "CustomPartitionRouter") {
    throw new ManifestCompatibilityError(streamName, "partition_router contains a CustomPartitionRouter");
  }

  if (partitionRouter.type === "ListPartitionRouter") {
    return [partitionRouter];
  }

  if (partitionRouter.type === "SubstreamPartitionRouter") {
    const manifestSubstreamPartitionRouter = partitionRouter;

    if (manifestSubstreamPartitionRouter.parent_stream_configs.length > 1) {
      throw new ManifestCompatibilityError(streamName, "SubstreamPartitionRouter has more than one parent stream");
    }
    const parentStreamConfig = manifestSubstreamPartitionRouter.parent_stream_configs[0];

    const matchingStreamIndex = serializedStreamToIndex[JSON.stringify(parentStreamConfig.stream)];
    if (matchingStreamIndex === undefined) {
      throw new ManifestCompatibilityError(
        streamName,
        "SubstreamPartitionRouter's parent stream doesn't match any other stream"
      );
    }

    return [
      {
        type: "SubstreamPartitionRouter",
        parent_key: parentStreamConfig.parent_key,
        partition_field: parentStreamConfig.partition_field,
        parentStreamReference: matchingStreamIndex.toString(),
      },
    ];
  }

  throw new ManifestCompatibilityError(streamName, "partition_router type is unsupported");
}

function manifestPrimaryKeyToBuilder(manifestStream: DeclarativeStream): BuilderStream["primaryKey"] {
  if (!isEqual(manifestStream.primary_key, manifestStream.primary_key)) {
    throw new ManifestCompatibilityError(
      manifestStream.name,
      "primary_key is not consistent across stream and retriever levels"
    );
  }
  if (manifestStream.primary_key === undefined) {
    return [];
  } else if (Array.isArray(manifestStream.primary_key)) {
    if (manifestStream.primary_key.length > 0 && Array.isArray(manifestStream.primary_key[0])) {
      throw new ManifestCompatibilityError(manifestStream.name, "primary_key contains nested arrays");
    } else {
      return manifestStream.primary_key as string[];
    }
  } else {
    return [manifestStream.primary_key];
  }
}

function manifestIncrementalSyncToBuilder(
  manifestIncrementalSync: DeclarativeStreamIncrementalSync | undefined,
  streamName?: string
): DatetimeBasedCursor | undefined {
  if (!manifestIncrementalSync) {
    return undefined;
  }
  if (manifestIncrementalSync.type === "CustomIncrementalSync") {
    throw new ManifestCompatibilityError(streamName, "incremental sync uses a custom implementation");
  }
  if (
    typeof manifestIncrementalSync.start_datetime !== "string" ||
    typeof manifestIncrementalSync.end_datetime !== "string"
  ) {
    throw new ManifestCompatibilityError(streamName, "start_datetime or end_datetime are not set to a string value");
  }

  return manifestIncrementalSync;
}

function manifestPaginatorToBuilder(
  manifestPaginator: SimpleRetrieverPaginator | undefined,
  streamName: string | undefined
): BuilderPaginator | undefined {
  if (manifestPaginator === undefined || manifestPaginator.type === "NoPagination") {
    return undefined;
  }

  if (manifestPaginator.page_token_option === undefined) {
    throw new ManifestCompatibilityError(streamName, "paginator does not define a page_token_option");
  }

  if (manifestPaginator.pagination_strategy.type === "CustomPaginationStrategy") {
    throw new ManifestCompatibilityError(streamName, "paginator.pagination_strategy uses a CustomPaginationStrategy");
  }

  let pageTokenOption: RequestOptionOrPathInject | undefined = undefined;

  if (manifestPaginator.page_token_option.type === "RequestPath") {
    pageTokenOption = { inject_into: "path" };
  } else {
    pageTokenOption = {
      inject_into: manifestPaginator.page_token_option.inject_into,
      field_name: manifestPaginator.page_token_option.field_name,
    };
  }

  return {
    strategy: manifestPaginator.pagination_strategy,
    pageTokenOption,
    pageSizeOption: manifestPaginator.page_size_option,
  };
}

function manifestSchemaLoaderToBuilderSchema(
  manifestSchemaLoader: DeclarativeStreamSchemaLoader | undefined
): BuilderStream["schema"] {
  if (manifestSchemaLoader === undefined) {
    return undefined;
  }

  if (manifestSchemaLoader.type === "InlineSchemaLoader") {
    const inlineSchemaLoader = manifestSchemaLoader;
    return inlineSchemaLoader.schema ? formatJson(inlineSchemaLoader.schema) : undefined;
  }

  // Return undefined if schema loader is not inline.
  // In this case, users can copy-paste the schema into the Builder, or they can re-infer it
  return undefined;
}

function manifestAuthenticatorToBuilder(
  manifestAuthenticator: HttpRequesterAuthenticator | undefined,
  streamName?: string
): BuilderFormAuthenticator {
  let builderAuthenticator: BuilderFormAuthenticator;
  if (manifestAuthenticator === undefined) {
    builderAuthenticator = {
      type: "NoAuth",
    };
  } else if (manifestAuthenticator.type === undefined) {
    throw new ManifestCompatibilityError(streamName, "authenticator has no type");
  } else if (manifestAuthenticator.type === "CustomAuthenticator") {
    throw new ManifestCompatibilityError(streamName, "uses a CustomAuthenticator");
  } else if (manifestAuthenticator.type === "OAuthAuthenticator") {
    if (
      Object.values(manifestAuthenticator.refresh_request_body ?? {}).filter((value) => typeof value !== "string")
        .length > 0
    ) {
      throw new ManifestCompatibilityError(
        streamName,
        "OAuthAuthenticator contains a refresh_request_body with non-string values"
      );
    }

    builderAuthenticator = {
      ...manifestAuthenticator,
      refresh_request_body: Object.entries(manifestAuthenticator.refresh_request_body ?? {}),
    };
  } else {
    builderAuthenticator = manifestAuthenticator;
  }

  // verify that all auth keys which require a user input have a {{config[]}} value

  const userInputAuthKeys = Object.keys(authTypeToKeyToInferredInput[builderAuthenticator.type]);

  for (const userInputAuthKey of userInputAuthKeys) {
    if (!isInterpolatedConfigKey(Reflect.get(builderAuthenticator, userInputAuthKey))) {
      throw new ManifestCompatibilityError(
        undefined,
        `Authenticator's ${userInputAuthKey} value must be of the form {{ config['key'] }}`
      );
    }
  }

  return builderAuthenticator;
}

function manifestSpecAndAuthToBuilder(
  manifestSpec: Spec | undefined,
  manifestAuthenticator: HttpRequesterAuthenticator | undefined
) {
  const result: {
    inputs: BuilderFormValues["inputs"];
    inferredInputOverrides: BuilderFormValues["inferredInputOverrides"];
    auth: BuilderFormAuthenticator;
  } = {
    inputs: [],
    inferredInputOverrides: {},
    auth: manifestAuthenticatorToBuilder(manifestAuthenticator),
  };

  if (manifestSpec === undefined) {
    return result;
  }

  const required = manifestSpec.connection_specification.required as string[];

  Object.entries(manifestSpec.connection_specification.properties as Record<string, AirbyteJSONSchema>).forEach(
    ([specKey, specDefinition]) => {
      const matchingInferredInput = Object.values(authTypeToKeyToInferredInput[result.auth.type]).find(
        (input) => input.key === specKey
      );
      if (matchingInferredInput) {
        result.inferredInputOverrides[matchingInferredInput.key] = specDefinition;
      } else {
        result.inputs.push({
          key: specKey,
          definition: specDefinition,
          required: required.includes(specKey),
        });
      }
    }
  );

  return result;
}

function assertType<T extends { type: string }>(
  object: { type: string },
  typeString: string,
  streamName: string | undefined
): asserts object is T {
  if (object.type !== typeString) {
    throw new ManifestCompatibilityError(streamName, `doesn't use a ${typeString}`);
  }
}

export class ManifestCompatibilityError extends Error {
  __type = "connectorBuilder.manifestCompatibility";

  constructor(public streamName: string | undefined, public message: string) {
    const errorMessage = `${streamName ? `Stream ${streamName}: ` : ""}${message}`;
    super(errorMessage);
    this.message = errorMessage;
  }
}

export function isManifestCompatibilityError(error: { __type?: string }): error is ManifestCompatibilityError {
  return error.__type === "connectorBuilder.manifestCompatibility";
}
