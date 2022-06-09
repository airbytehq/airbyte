export interface StripeCheckoutSessionCreate {
  workspaceId: string;
  successUrl: string;
  cancelUrl: string;
  quantity?: number;
}

export interface StripeCheckoutSessionRead {
  stripeUrl: string;
}
