# Xero

The Xero source connector interacts with [Xero Accounting API](https://developer.xero.com/documentation/api/accounting/overview), which provides all accounting data such as invoices, contacts, bank transactions etc.

Unfortunately, it requires [Xero Custom Connections](https://developer.xero.com/documentation/guides/oauth2/custom-connections/) subscription to work as default Xero OAuth2 Authentication supports only short-lived access_tokens with frequently updated refresh_tokens.

For testing and development purposes you can use [Xero demo company](https://developer.xero.com/documentation/development-accounts/#accessing-the-xero-demo-company) with Xero Custom Connections free of charge.
