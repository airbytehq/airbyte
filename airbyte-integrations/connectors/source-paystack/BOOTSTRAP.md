# Paystack

paystack.com is a Payment Gateway and its REST API is similar to Stripe's. This Paystack API connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).

The Paystack API has resources including (not exhaustive)
- Customers
- Transactions - Payments and payment attempts
- Subscriptions - Recurring payments
- Invoices - Requests for payment
- Settlements - Transfers from the Paystack Gateway account to the merchant (account instance owner) bank account
- Refunds - Reversed payments

The Paystack API can be used to charge customers, and to perform CRUD operations on any of the above resources. For Airbyte only the "R" - read operations are needed, however Paystack currently supports a single secret key which can do all CRUD operations.

## Notes & Quirks
- Pagination uses the query parameters "page" (starting at 1) and "perPage".
- The standard cursor field is "createdAt" on all responses, except the "Invoices" stream which uses "created_at". It's likely the interface for this resource is either outdated or failed to be backward compatible (some other resources have both fields and some have only "createdAt").

## Useful links below
- [Paystack connector documentation](https://docs.airbyte.io/integrations/sources/paystack) - Information about specific streams and some nuances about the connector
- [Paystack dashboard](https://dashboard.paystack.com/#/settings/developer) - To grab your API token