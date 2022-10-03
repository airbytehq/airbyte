import { AddTrialCreditsResponse, OrbCreditLedgerEntry, OrbCustomer } from "./types";

export type AddTrialCreditsRequest = Pick<OrbCreditLedgerEntry, "amount" | "expiry_date"> & { customerId: string };

// TODO: this can be improved to have one different IDEMPOTENCY_KEY per experiment
const EXP_ADD_TRIAL_CREDITS_IDEMPOTENCY_KEY = "exp-speedy-connection-";

export class OrbService {
  get baseUrl(): string {
    return "https://api.billwithorb.com/v1";
  }

  async addTrialCredits({ customerId, amount, expiry_date }: AddTrialCreditsRequest): Promise<AddTrialCreditsResponse> {
    const path = `${this.baseUrl}/customers/${customerId}/credits/ledger_entry`;

    const requestOptions: RequestInit = {
      method: "POST",
      body: JSON.stringify({
        entry_type: "increment",
        amount,
        expiry_date,
        per_unit_cost_basis: "0",
        description: `Added ${amount} free trial credits`,
      }),
      headers: {
        Authorization: `Bearer ${process.env.REACT_APP_ORB_KEY}`,
        "Content-Type": "application/json",
        "Idempotency-Key": EXP_ADD_TRIAL_CREDITS_IDEMPOTENCY_KEY + customerId,
      },
    };
    const response = await fetch(path, requestOptions);
    return await response.json();
  }

  async getCustomerIdByExternalId(external_customer_id: string): Promise<OrbCustomer> {
    const path = `${this.baseUrl}/customers/external_customer_id/${external_customer_id}`;
    const requestOptions: RequestInit = {
      method: "GET",
      headers: {
        Authorization: `Bearer ${process.env.REACT_APP_ORB_KEY}`,
        "Content-Type": "application/json",
      },
    };
    const response = await fetch(path, requestOptions);
    return await response.json();
  }
}
