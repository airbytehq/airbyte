import { AirbyteRequestService } from "core/request/AirbyteRequestService";

import { StripeCheckoutSessionRead, StripeCheckoutSessionCreate } from "./types";

export class StripeService extends AirbyteRequestService {
  get url(): string {
    return "v1/stripe";
  }

  public async createCheckoutSession(params: StripeCheckoutSessionCreate): Promise<StripeCheckoutSessionRead> {
    return this.fetch<StripeCheckoutSessionRead>(`${this.url}/create_checkout_session`, params);
  }
}
