import { Config } from "../../config";
import { RequestMiddleware } from "./RequestMiddleware";

export interface ApiOverrideRequestOptions {
  config: Pick<Config, "apiUrl">;
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
  }: {
    url: string;
    method: "get" | "post" | "put" | "delete" | "patch";
    params?: URLSearchParams;
    data?: U;
    headers?: HeadersInit;
    responseType?: "blob";
  },
  options?: ApiOverrideRequestOptions
): Promise<typeof responseType extends "blob" ? Blob : T> => {
  if (!options) {
    throw new Error("Please provide middlewares and config!");
  }
  const { apiUrl } = options.config;
  const requestUrl = `${apiUrl}${url}`;

  for (const middleware of options.middlewares) {
    headers = (await middleware({ headers })).headers;
  }

  const response = await fetch(`${requestUrl}${new URLSearchParams(params)}`, {
    method,
    ...(data ? { body: getRequestBody(data) } : {}),
    headers,
    signal: options.signal,
  });

  // TODO: For some reason some responses that return blobs do not have `responseType: "blob"` generated
  return responseType === "blob" || response.headers.get("Content-Type") === "application/x-gzip"
    ? response.blob()
    : response.json();
};
