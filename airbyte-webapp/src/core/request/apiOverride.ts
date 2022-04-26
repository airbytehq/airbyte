import { Config } from "../../config";
import { RequestMiddleware } from "./RequestMiddleware";

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
  options?: { config: Pick<Config, "apiUrl">; middlewares: RequestMiddleware[]; signal?: RequestInit["signal"] }
): Promise<typeof responseType extends "blob" ? Blob : T> => {
  if (!options) {
    throw new Error("Please provide middlewares and config!");
  }
  const { apiUrl } = options.config;
  // Unsure how worth it is to try to fix this replace
  const requestUrl = `${apiUrl}${url.replace("/v1/", "")}`;

  for (const middleware of options.middlewares) {
    headers = (await middleware({ headers })).headers;
  }

  const response = await fetch(`${requestUrl}${new URLSearchParams(params)}`, {
    method,
    ...(data ? { body: JSON.stringify(data) } : {}),
    headers,
    signal: options.signal,
  });

  return responseType === "blob" ? response.blob() : response.json();
};
