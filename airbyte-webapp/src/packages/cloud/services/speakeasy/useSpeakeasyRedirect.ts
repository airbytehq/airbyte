import { getSpeakeasyCallbackUrl } from "packages/cloud/lib/domain/speakeasy";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

import { useConfig } from "../config";

const SPEAKEASY_QUERY_KEY = "speakeasy-redirect";

export const useSpeakeasyRedirect = () => {
  const { cloudPublicApiUrl } = useConfig();
  const config = { apiUrl: cloudPublicApiUrl };
  const middlewares = useDefaultRequestMiddlewares();
  const requestOptions = { config, middlewares };

  return useSuspenseQuery([SPEAKEASY_QUERY_KEY], () => getSpeakeasyCallbackUrl(requestOptions));
};
