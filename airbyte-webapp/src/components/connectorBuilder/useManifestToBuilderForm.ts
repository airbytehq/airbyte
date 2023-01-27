import isEqual from "lodash/isEqual";

import { AirbyteJSONSchema } from "core/jsonSchema/types";
import { ResolveManifest } from "core/request/ConnectorBuilderClient";
import {
  CartesianProductStreamSlicer,
  ConnectorManifest,
  DatetimeStreamSlicer,
  DeclarativeStream,
  DeclarativeStreamSchemaLoader,
  DpathExtractor,
  HttpRequester,
  HttpRequesterAuthenticator,
  InlineSchemaLoader,
  InterpolatedRequestOptionsProvider,
  ListStreamSlicer,
  SimpleRetriever,
  SimpleRetrieverPaginator,
  SimpleRetrieverStreamSlicer,
  Spec,
  SubstreamSlicer,
} from "core/request/ConnectorManifest";
import { useResolveManifest } from "services/connectorBuilder/ConnectorBuilderApiService";

import {
  authTypeToKeyToInferredInput,
  BuilderFormAuthenticator,
  BuilderFormValues,
  BuilderPaginator,
  BuilderStream,
  BuilderSubstreamSlicer,
  DEFAULT_BUILDER_FORM_VALUES,
  DEFAULT_BUILDER_STREAM_VALUES,
  isInterpolatedConfigKey,
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

  const builderFormValues = DEFAULT_BUILDER_FORM_VALUES;
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

  if (retriever.name !== stream.name || requester.name !== stream.name) {
    throw new ManifestCompatibilityError(
      stream.name,
      "name is not consistent across stream, retriever, and requester levels"
    );
  }

  if (![undefined, "GET", "POST"].includes(requester.http_method)) {
    throw new ManifestCompatibilityError(stream.name, "http_method is not GET or POST");
  }

  assertType<DpathExtractor>(retriever.record_selector.extractor, "DpathExtractor", stream.name);

  if (requester.request_options_provider) {
    assertType<InterpolatedRequestOptionsProvider>(
      requester.request_options_provider,
      "InterpolatedRequestOptionsProvider",
      stream.name
    );
  }

  return {
    ...DEFAULT_BUILDER_STREAM_VALUES,
    id: index.toString(),
    name: stream.name ?? "",
    urlPath: requester.path,
    httpMethod: (requester.http_method as "GET" | "POST" | undefined) ?? "GET",
    fieldPointer: retriever.record_selector.extractor.field_pointer as string[],
    requestOptions: {
      requestParameters: Object.entries(requester.request_options_provider?.request_parameters ?? {}),
      requestHeaders: Object.entries(requester.request_options_provider?.request_headers ?? {}),
      // try getting this from request_body_data first, and if not set then pull from request_body_json
      requestBody: Object.entries(
        requester.request_options_provider?.request_body_data ??
          requester.request_options_provider?.request_body_json ??
          {}
      ),
    },
    primaryKey: manifestPrimaryKeyToBuilder(stream),
    paginator: manifestPaginatorToBuilder(retriever.paginator, stream.name, firstStreamUrlBase),
    streamSlicer: manifestStreamSlicerToBuilder(retriever.stream_slicer, serializedStreamToIndex, stream.name),
    schema: manifestSchemaLoaderToBuilderSchema(stream.schema_loader),
    unsupportedFields: {
      transformations: stream.transformations,
      checkpoint_interval: stream.checkpoint_interval,
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

function manifestStreamSlicerToBuilder(
  manifestStreamSlicer: SimpleRetrieverStreamSlicer | undefined,
  serializedStreamToIndex: Record<string, number>,
  streamName?: string
): BuilderStream["streamSlicer"] {
  if (manifestStreamSlicer === undefined) {
    return undefined;
  }

  if (manifestStreamSlicer.type === undefined) {
    throw new ManifestCompatibilityError(streamName, "stream_slicer has no type");
  }

  if (manifestStreamSlicer.type === "CustomStreamSlicer") {
    throw new ManifestCompatibilityError(streamName, "stream_slicer contains a CustomStreamSlicer");
  }

  if (manifestStreamSlicer.type === "SingleSlice") {
    throw new ManifestCompatibilityError(streamName, "stream_slicer contains a SingleSlice");
  }

  if (manifestStreamSlicer.type === "DatetimeStreamSlicer") {
    const datetimeStreamSlicer = manifestStreamSlicer as DatetimeStreamSlicer;
    if (
      typeof datetimeStreamSlicer.start_datetime !== "string" ||
      typeof datetimeStreamSlicer.end_datetime !== "string"
    ) {
      throw new ManifestCompatibilityError(streamName, "start_datetime or end_datetime are not set to a string value");
    }
    return manifestStreamSlicer as DatetimeStreamSlicer;
  }

  if (manifestStreamSlicer.type === "ListStreamSlicer") {
    return manifestStreamSlicer as ListStreamSlicer;
  }

  if (manifestStreamSlicer.type === "CartesianProductStreamSlicer") {
    return {
      type: "CartesianProductStreamSlicer",
      stream_slicers: manifestStreamSlicer.stream_slicers.map((subSlicer) => {
        return manifestStreamSlicerToBuilder(subSlicer, serializedStreamToIndex, streamName) as
          | Exclude<SimpleRetrieverStreamSlicer, SubstreamSlicer | CartesianProductStreamSlicer>
          | BuilderSubstreamSlicer;
      }),
    };
  }

  if (manifestStreamSlicer.type === "SubstreamSlicer") {
    const manifestSubstreamSlicer = manifestStreamSlicer as SubstreamSlicer;

    if (manifestSubstreamSlicer.parent_stream_configs.length > 1) {
      throw new ManifestCompatibilityError(streamName, "SubstreamSlicer has more than one parent stream");
    }
    const parentStreamConfig = manifestSubstreamSlicer.parent_stream_configs[0];

    const matchingStreamIndex = serializedStreamToIndex[JSON.stringify(parentStreamConfig.stream)];
    if (matchingStreamIndex === undefined) {
      throw new ManifestCompatibilityError(
        streamName,
        "SubstreamSlicer's parent stream doesn't match any other stream"
      );
    }

    return {
      type: "SubstreamSlicer",
      parent_key: parentStreamConfig.parent_key,
      stream_slice_field: parentStreamConfig.stream_slice_field,
      parentStreamReference: matchingStreamIndex.toString(),
    };
  }

  throw new ManifestCompatibilityError(streamName, "stream_slicer type is unsupported");
}

function manifestPrimaryKeyToBuilder(manifestStream: DeclarativeStream): BuilderStream["primaryKey"] {
  if (!isEqual(manifestStream.primary_key, manifestStream.retriever.primary_key)) {
    throw new ManifestCompatibilityError(
      manifestStream.name,
      "primary_key is not consistent across stream and retriever levels"
    );
  }
  if (manifestStream.primary_key === undefined) {
    return [];
  } else if (Array.isArray(manifestStream.retriever.primary_key)) {
    if (manifestStream.retriever.primary_key.length > 0 && Array.isArray(manifestStream.retriever.primary_key[0])) {
      throw new ManifestCompatibilityError(manifestStream.name, "primary_key contains nested arrays");
    } else {
      return manifestStream.retriever.primary_key as string[];
    }
  } else {
    return [manifestStream.retriever.primary_key];
  }
}

function manifestPaginatorToBuilder(
  manifestPaginator: SimpleRetrieverPaginator | undefined,
  streamName: string | undefined,
  globalUrlBase: string
): BuilderPaginator | undefined {
  if (manifestPaginator === undefined || manifestPaginator.type === "NoPagination") {
    return undefined;
  }

  if (manifestPaginator.page_token_option === undefined) {
    throw new ManifestCompatibilityError(streamName, "paginator does not define a page_token_option");
  }

  if (manifestPaginator.url_base !== globalUrlBase) {
    throw new ManifestCompatibilityError(streamName, "paginator.url_base does not match the first stream's url_base");
  }

  if (manifestPaginator.pagination_strategy.type === "CustomPaginationStrategy") {
    throw new ManifestCompatibilityError(streamName, "paginator.pagination_strategy uses a CustomPaginationStrategy");
  }

  return {
    strategy: manifestPaginator.pagination_strategy,
    pageTokenOption: manifestPaginator.page_token_option,
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
    const inlineSchemaLoader = manifestSchemaLoader as InlineSchemaLoader;
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
