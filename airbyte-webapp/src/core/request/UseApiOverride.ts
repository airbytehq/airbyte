import { useConfig } from "../../config/ConfigServiceProvider";
import { useSuspenseQuery } from "../../services/connector/useSuspenseQuery";

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
}): Promise<T> => {
  const { apiUrl } = useConfig();

  return useSuspenseQuery(url, async () => {
    // Unsure how worth it is to try to fix this replace
    const response = await fetch(`${apiUrl}${url.replace("/v1/", "")}` + new URLSearchParams(params), {
      method,
      ...(data ? { body: JSON.stringify(data) } : {}),
      headers,
    });

    return responseType === "blob" ? response.blob() : response.json();
  });
};

export { useApiOverride as req };

// In some case with react-query and swr you want to be able to override the return error type so you can also do it here like this

export type ErrorType<Error> = Error;

// In case you want to wrap the body type (optional)

// (if the custom instance is processing data before sending it, like changing the case for example)

export type BodyType<BodyData> = BodyData;
