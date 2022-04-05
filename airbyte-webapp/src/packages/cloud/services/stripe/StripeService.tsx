import { useMemo } from "react";
import { useMutation } from "react-query";

import { StripeCheckoutSessionCreate, StripeService } from "packages/cloud/lib/domain/stripe";
import { useDefaultRequestMiddlewares } from "services/useDefaultRequestMiddlewares";
import { useConfig } from "packages/cloud/services/config";

export function useStripeService(): StripeService {
  const requestAuthMiddleware = useDefaultRequestMiddlewares();
  const { cloudApiUrl } = useConfig();

  return useMemo(() => new StripeService(cloudApiUrl, requestAuthMiddleware), [cloudApiUrl, requestAuthMiddleware]);
}

export function useStripeCheckout() {
  const service = useStripeService();
  return useMutation((params: StripeCheckoutSessionCreate) => service.createCheckoutSession(params));
}
