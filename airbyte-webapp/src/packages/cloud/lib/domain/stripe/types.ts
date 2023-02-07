export interface StripeCheckoutSessionCreate {
  workspaceId: string;
  successUrl: string;
  cancelUrl: string;
  quantity?: number;
  stripeMode: "payment" | "setup";
}

export interface StripeCheckoutSessionRead {
  stripeUrl: string;
}
