# Connector Health

Airbyte runs regular testing of all integrations to ensure we are able to properly interact with APIs/DBs/etc. Our goal is to quickly identify breaking changes.

This page shows the status of integration tests running for each connector on `master`.

**Red status badges** mean the last test failed.  
**Yellow status badges** mean the last test passed, but at least one of the last ten tests failed.  
**Green status badges** mean the last ten tests were all successful.

The test status badges are cached and can take 5 minutes to update.

Clicking on a status will take you to a summary of past tests that link to the Github workflows executed for the test.

**Airbyte Certified:** We mark a connector as "Airbyte Certified" after verifying that the connector adheres to our recommended [best practices](../contributing-to-airbyte/building-new-connector/best-practices.md).

## Sources

| Source | Build Status | Airbyte Certified | Notes |
| :--- | :--- | :---: | :--- |
| Braintree | [![source-braintree-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-braintree-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-braintree-singer) |  |  |
| Drift | [![source-drift](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-drift%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-drift) |  |  |
| Exchange Rates API | [![source-exchangeratesapi-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-exchangeratesapi-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-exchangeratesapi-singer) |  |  |
| Facebook Marketing | [![source-facebook-marketing](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-facebook-marketing%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-facebook-marketing) | ✅ |  |
| Files | [![source-file](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-file%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-file) | ✅ |  |
| Freshdesk | [![source-freshdesk](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-freshdesk%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-freshdesk) |  |  |
| GitHub | [![source-github-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-github-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-github-singer) | ✅ |  |
| GitLab | [![source-gitlab-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-gitlab-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-gitlab-singer) | ✅ |  |
| Google Adwords | [![source-google-adwords-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-google-adwords-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-google-adwords-singer) | ✅ | **March 22nd, 2021:** Airbyte's API token used for testing is getting throttled. We currently have an application with Google to increase our rate limit. |
| Google Analytics | [![source-googleanalytics-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-googleanalytics-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-googleanalytics-singer) | ✅ | |
| Google Sheets | [![source-google-sheets](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-google-sheets%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-google-sheets) | ✅ |  |
| Google Directory API | [![source-google-directory](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-google-directory%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-google-directory) | ✅ |  |
| Greenhouse | [![source-greenhouse](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-greenhouse%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-greenhouse) |  |  |
| HTTP Request | [![source-http-request](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-http-request%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-http-request) |  |  |
| Hubspot | [![source-hubspot-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-hubspot%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-hubspot) | ✅ |  |
| Instagram | [![source-instagram](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-instagram%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-instagram) | ✅ |  |
| Intercom | [![source-intercom-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-intercom-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-intercom-singer) |  |  |
| Jira | [![source-jira](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-jira%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-jira) |  |  |
| Looker | [![source-looker](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-looker%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-looker) |  | \*\*\*\* |
| Mailchimp | [![source-mailchimp](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-mailchimp%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-mailchimp) |  |  |
| Marketo | [![source-marketo-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-marketo-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-marketo-singer) | ✅ |  |
| Microsoft SQL Server \(MSSQL\) | [![source-mssql](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-mssql%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-mssql) | ⏱Certification in progress |  |
| Microsoft Teams | [![source-microsoft-teams](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-microsoft-teams%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-microsoft-teams) |  |  |
| Mixpanel | [![source-mixpanel-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-mixpanel-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-mixpanel-singer) |  |  |
| Mongo DB | [![source-mongodb](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-mongodb%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-mongodb) |  |  |
| MySQL | [![source-mysql](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-mysql%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-mysql) | ⏱Certification in progress |  |
| Plaid | [![source-plaid](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-plaid%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-plaid) |  |  |
| Postgres | [![source-postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-postgres%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-postgres) | ⏱Certification in progress |  |
| Recurly | [![source-recurly](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-recurly%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-recurly) |  |  |
| Redshift | [![source-redshift](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-redshift%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-redshift) | ⏱Certification in progress |  |
| Salesforce | [![source-salesforce-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-salesforce-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-salesforce-singer) | ✅ |  |
| Sendgrid | [![source-sendgrid](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-sendgrid%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-sendgrid) |  |  |
| Shopify | [![source-shopify-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-shopify-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-shopify-singer) | ✅ |  |
| Slack | [![source-slack-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-slack-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-slack-singer) |  | **January 25, 2021:** The underlying Slack instance \(Airbyte's public slack\) receives enough traffic that data almost always changes mid-test, causing a discrepancy in expected and actual results. The fix will be to pull data between two specific dates in the past to avoid data changing in real time. |
| Stripe | [![source-stripe-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-stripe-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-stripe-singer) | ✅ |  |
| Twilio | [![source-twilio-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-twilio-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-tempo) |  |  |
| Tempo | [![source-tempo](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-tempo%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-tempo) |  |  |
| Zendesk Support | [![source-zendesk-support-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-zendesk-support-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-zendesk-support-singer) |  | \*\*\*\* |
| Zoom | [![source-zoom-singer](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-zoom-singer%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/source-zoom-singer) |  |  |

## Destinations

| Destination | Status | Airbyte Certified |
| :--- | :--- | :---: |
| BigQuery | [![destination-bigquery](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-bigquery%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-bigquery) | ✅ |
| Local CSV | [![destination-csv](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-csv%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-csv) | ✅ |
| Local JSON | [![destination-local-json](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-local-json%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-local-json) | ✅ |
| Postgres | [![destination-postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-postgres%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-postgres) | ✅ |
| Redshift | [![destination-redshift](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-redshift%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-redshift) | ✅ |
| Snowflake | [![destination-snowflake](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-snowflake%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-snowflake) | ✅ |

