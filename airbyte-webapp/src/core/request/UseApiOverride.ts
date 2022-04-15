import { useConfig } from "../../config/ConfigServiceProvider";
import { useSuspenseQuery } from "../../services/connector/useSuspenseQuery";

export const useApiOverride = <T, U = unknown>({
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
}) => {
  const { apiUrl } = useConfig();
  // Unsure how worth it is to try to fix this replace
  const requestUrl = `${apiUrl}${url.replace("/v1/", "")}`;
  const key = `${requestUrl}${method}`;

  return useSuspenseQuery<T>(key, async () => {
    const response = await fetch(`${requestUrl}` + new URLSearchParams(params), {
      method,
      ...(data ? { body: JSON.stringify(data) } : {}),
      headers,
    });

    return responseType === "blob" ? response.blob() : response.json();
  });
};
