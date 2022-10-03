export interface OrbCreditLedgerEntry {
  entry_type: "increment" | "decrement" | "expiration_change";
  amount: number;
  expiry_date?: string;
  description: string;
  per_unit_cost_basis: string;
}

export interface AddTrialCreditsResponse {
  amount: number;
  created_at: string;
  credit_block: {
    expiry_date: string;
    id: string;
    per_unit_cost_basis: string | null;
  };
  customer: {
    external_customer_id: string;
    id: string;
  };
  description: string;
  ending_balance: number;
  entry_type: "increment" | "decrement" | "expiration_change";
  id: string;
  starting_balance: number;
  entry_status: "commited" | "pending";
  ledger_sequence_number: number;
}

export interface OrbCustomer {
  balance: string;
  billing_address: string | null;
  created_at: string;
  currency: string;
  email: string;
  external_customer_id: string;
  id: string;
  name: string;
  payment_provider: string | null;
  payment_provider_id: string | null;
  shipping_address: string | null;
  timezone: string;
}
