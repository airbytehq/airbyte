import { useConfig } from "../../config/ConfigServiceProvider";
import { useDefaultRequestMiddlewares } from "../../services/useDefaultRequestMiddlewares";

export const useApiOverride = async <T, U = unknown>({
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
}): Promise<typeof responseType extends "blob" ? Blob : T> => {
  const { apiUrl } = useConfig();
  // Unsure how worth it is to try to fix this replace
  const requestUrl = `${apiUrl}${url.replace("/v1/", "")}`;

  const middlewares = useDefaultRequestMiddlewares();
  for (const middleware of middlewares) {
    headers = (await middleware({ headers })).headers;
  }

  const response = await fetch(`${requestUrl}` + new URLSearchParams(params), {
    method,
    ...(data ? { body: JSON.stringify(data) } : {}),
    headers,
  });

  return responseType === "blob" ? response.blob() : response.json();
};

export { useApiOverride as apiOverride };
