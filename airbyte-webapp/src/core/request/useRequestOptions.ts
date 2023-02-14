import { config } from "config";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

import { ApiOverrideRequestOptions } from "./apiOverride";

const ROOT_APIS = {
  oss: config.apiUrl,
  cloud: config.cloudApiUrl,
} as const;

export const useRequestOptions = (api: "oss" | "cloud" = "oss"): ApiOverrideRequestOptions => {
  const middlewares = useDefaultRequestMiddlewares();
  const rootUrl = ROOT_APIS[api];

  if (!rootUrl) {
    throw new Error(`Could not find root URL path for ${api} endpoints.`);
  }

  return {
    config: { apiUrl: rootUrl },
    middlewares,
  };
};
