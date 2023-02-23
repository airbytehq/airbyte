import { useMemo } from "react";
import { useMutation } from "react-query";

import { useConfig, MissingConfigError } from "config";
import { StripeCheckoutSessionCreate, StripeService } from "packages/cloud/lib/domain/stripe";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";

export function useStripeService(): StripeService {
  const requestAuthMiddleware = useDefaultRequestMiddlewares();
  const { cloudApiUrl } = useConfig();

  if (!cloudApiUrl) {
    throw new MissingConfigError("Missing required configuration cloudApiUrl");
  }

  return useMemo(() => new StripeService(cloudApiUrl, requestAuthMiddleware), [cloudApiUrl, requestAuthMiddleware]);
}

export function useStripeCheckout() {
  const service = useStripeService();
  return useMutation((params: StripeCheckoutSessionCreate) => service.createCheckoutSession(params));
}
