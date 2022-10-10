# Zuora

SOAP API docs (more info on queries with ZOQL) are [here](https://knowledgecenter.zuora.com/Central_Platform/API/G_SOAP_API).

REST API docs are [here](https://www.zuora.com/developer/api-reference/).

The Zuora API exposes a SQL-like interface ([ZOQL](https://knowledgecenter.zuora.com/Central_Platform/Query/ZOQL)) for customers to pull their data on subscriptions, users, transactions etc. An example of a query may be:
select * from account where updateddate >= TIMESTAMP 

Zuora has [various base endpoints](https://www.zuora.com/developer/api-reference/#section/Introduction/Access-to-the-API), differentiating for production/sandbox, US/EU etc.

It operates on a POST-check-GET mechanism where the ZOQL query is first sent in the initial request, the id of that request can then be polled to check status and eventually consumed with another request when completed.

The information about all streams can be pulled dynamically using ZOQL queries SHOW TABLES and DESCRIBE {table}.

Auth = OAuth2 with a header of “grant_type” set to “client_credentials” and no refresh token


See [this](https://docs.airbyte.io/integrations/sources/zuora) link for the nuances about the connector.
