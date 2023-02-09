import { MissingConfigError, useConfig } from "config";
import { getSpeakeasyCallbackUrl } from "packages/cloud/lib/domain/speakeasy";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

const SPEAKEASY_QUERY_KEY = "speakeasy-redirect";

export const useSpeakeasyRedirect = () => {
  const { cloudPublicApiUrl } = useConfig();

  if (!cloudPublicApiUrl) {
    throw new MissingConfigError("Missing required configuration cloudPublicApiUrl");
  }

  const config = { apiUrl: cloudPublicApiUrl };
  const middlewares = useDefaultRequestMiddlewares();
  const requestOptions = { config, middlewares };

  return useSuspenseQuery([SPEAKEASY_QUERY_KEY], () => getSpeakeasyCallbackUrl(requestOptions));
};
