import { CommonRequestError } from "./CommonRequestError";
import { RequestMiddleware } from "./RequestMiddleware";
import { VersionError } from "./VersionError";
import { AirbyteWebappConfig } from "../../config";

export interface ApiOverrideRequestOptions {
  config: Pick<AirbyteWebappConfig, "apiUrl">;
  middlewares: RequestMiddleware[];
  signal?: RequestInit["signal"];
}

function getRequestBody<U>(data: U) {
  const stringifiedData = JSON.stringify(data);
  const nonJsonObject = stringifiedData === "{}";
  if (nonJsonObject) {
    // The app tries to stringify blobs which results in broken functionality.
    // There may be some edge cases where we pass in an empty object.
    // @ts-expect-error There may be a better way to do this, but for now it solves the problem.
    return data as BodyInit;
  }
  return stringifiedData;
}

export const apiOverride = async <T, U = unknown>(
  {
    url,
    method,
    params,
    data,
    headers,
    responseType,
    signal,
  }: {
    url: string;
    method: "get" | "post" | "put" | "delete" | "patch";
    params?: URLSearchParams;
    data?: U;
    headers?: HeadersInit;
    responseType?: "blob";
    signal?: AbortSignal;
  },
  options?: ApiOverrideRequestOptions
): Promise<typeof responseType extends "blob" ? Blob : T> => {
  if (!options) {
    throw new Error("Please provide middlewares and config!");
  }

  const { apiUrl } = options.config;
  // Remove the `v1/` in the end of the apiUrl for now, during the transition period
  // to get rid of it from all environment variables.
  const requestUrl = `${apiUrl.replace(/\/v1\/?$/, "")}${url.startsWith("/") ? "" : "/"}${url}`;

  for (const middleware of options.middlewares) {
    ({ headers } = await middleware({ headers }));
  }

  const response = await fetch(`${requestUrl}${new URLSearchParams(params)}`, {
    method,
    ...(data ? { body: getRequestBody(data) } : {}),
    headers,
    signal: signal ?? options.signal,
  });

  /*
   * Orval only generates `responseType: "blob"` if the schema for an endpoint
   * is `type: string`, and `format: binary`.
   * If it references a type that is `type: string`, and `format: binary` it does not interpret
   * it correctly. So I am making an assumption that if it's not explicitly JSON, it's a binary file.
   */
  return parseResponse(response, responseType);
};

/** Parses errors from server */
async function parseResponse<T>(response: Response, responseType?: "blob"): Promise<T> {
  if (response.status === 204) {
    return {} as T;
  }
  if (response.status >= 200 && response.status < 300) {
    /*
     * Orval only generates `responseType: "blob"` if the schema for an endpoint
     * is `type: string, and format: binary`.
     * If it references a type that is `type: string, and format: binary` it does not interpret
     * it correct. So I am making an assumption that if it's not explicitly JSON, it's a binary file.
     */
    return responseType === "blob" || response.headers.get("Content-Type") !== "application/json"
      ? response.blob()
      : response.json();
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  let resultJsonResponse: any;

  // If some error returned in json, lets try to parse it
  try {
    resultJsonResponse = await response.json();
  } catch (e) {
    // non json result
    console.log("// non json result");
    throw new CommonRequestError(response, "non-json response");
  }

  if (resultJsonResponse?.error) {
    if (resultJsonResponse.error.startsWith("Version mismatch between")) {
      throw new VersionError(resultJsonResponse.error);
    }
  }

  throw new CommonRequestError(response, resultJsonResponse?.message ?? JSON.stringify(resultJsonResponse?.detail));
}
