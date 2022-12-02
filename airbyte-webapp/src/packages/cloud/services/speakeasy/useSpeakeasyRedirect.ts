import { getSpeakeasyCallbackUrl } from "packages/cloud/lib/domain/speakeasy";
import { useSuspenseQuery } from "services/connector/useSuspenseQuery";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

const SPEAKEASY_QUERY_KEY = "speakeasy-redirect";

export const useSpeakeasyRedirect = () => {
  const config = { apiUrl: "/cloud_api" };
  const middlewares = useDefaultRequestMiddlewares();
  const requestOptions = { config, middlewares };

  return useSuspenseQuery([SPEAKEASY_QUERY_KEY], () => getSpeakeasyCallbackUrl(requestOptions));
};
