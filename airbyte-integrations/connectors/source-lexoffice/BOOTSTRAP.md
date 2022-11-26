# LexOffice

LexOffice is a ERP system designed for small to mid-size companies to organize and manage all ERP processes, e.g. invoicing.
This connector adds ability to fetch all vouchers/invoices.
Connector is implemented with [Airbyte CDK](https://docs.airbyte.io/connector-development/cdk-python).
The LexOffice API is describe [here](https://developers.lexoffice.io/docs/#lexoffice-api-documentation).

All records are taken from the vouchers endpoint that returns a list of vouchers.
Each voucher record can be uniquely identified by an `id` key.
Vouchers include several types, including salesinvoice (e.g. for sales orders), salescreditnote (e.g. for refunds or returned sales orders), purchaseinvoice and purchasecreditnote.

LexOffice API by default returns a list of all vouchers. To allow for incremental streaming, the page size is cut down to 1 by using paging parameters.
Requests that hit any of LexOffice rate limits will receive a `429 Too Many Requests` response, which contains the standard Retry-After header indicating how many seconds the client should wait before retrying the request.

[Here](https://developers.lexoffice.io/docs/#paging-of-resources) is a link with info on how pagination is implemented.
