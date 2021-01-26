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

<table>
  <thead>
    <tr>
      <th style="text-align:left">Source</th>
      <th style="text-align:left">Status</th>
      <th style="text-align:center">Airbyte Certified</th>
      <th style="text-align:left">Notes</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:left">Braintree</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-braintree-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-braintree-singer%2Fbadge.json" alt="source-braintree-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Drift</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-drift"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-drift%2Fbadge.json" alt="source-drift"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Exchange Rates API</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-exchangeratesapi-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-exchangeratesapi-singer%2Fbadge.json" alt="source-exchangeratesapi-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Facebook Marketing</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-facebook-marketing"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-facebook-marketing%2Fbadge.json" alt="source-facebook-marketing"/></a>
      </td>
      <td style="text-align:center">&#x2705;</td>
      <td style="text-align:left">
        <p><b>Jan 25</b>: Replaced the Singer-based connector which had finicky integration
          tests with an Airbyte native one.</p>
        <p>&lt;b&gt;&lt;/b&gt;</p>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">Files</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-file"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-file%2Fbadge.json" alt="source-file"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Freshdesk</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-freshdesk"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-freshdesk%2Fbadge.json" alt="source-freshdesk"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">GitHub</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-github-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-github-singer%2Fbadge.json" alt="source-github-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Google Adwords</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-google-adwords-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-google-adwords-singer%2Fbadge.json" alt="source-google-adwords-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Google Analytics</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-googleanalytics-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-googleanalytics-singer%2Fbadge.json" alt="source-googleanalytics-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Google Sheets</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-google-sheets"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-google-sheets%2Fbadge.json" alt="source-google-sheets"/></a>
      </td>
      <td style="text-align:center">&#x2705;</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Greenhouse</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-greenhouse"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-greenhouse%2Fbadge.json" alt="source-greenhouse"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">HTTP Request</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-http-request"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-http-request%2Fbadge.json" alt="source-http-request"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Hubspot</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-hubspot-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-hubspot-singer%2Fbadge.json" alt="source-hubspot-singer"/></a>
      </td>
      <td style="text-align:center">&#x2705;</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Intercom</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-intercom-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-intercom-singer%2Fbadge.json" alt="source-intercom-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Jira</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-jira"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-jira%2Fbadge.json" alt="source-jira"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Looker</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-looker"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-looker%2Fbadge.json" alt="source-looker"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Mailchimp</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-mailchimp"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-mailchimp%2Fbadge.json" alt="source-mailchimp"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Marketo</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-marketo-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-marketo-singer%2Fbadge.json" alt="source-marketo-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Microsoft SQL Server (MSSQL)</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-mssql"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-mssql%2Fbadge.json" alt="source-mssql"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Microsoft Teams</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-microsoft-teams"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-microsoft-teams%2Fbadge.json" alt="source-microsoft-teams"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Mixpanel</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-mixpanel-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-mixpanel-singer%2Fbadge.json" alt="source-mixpanel-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">MySQL</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-mysql"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-mysql%2Fbadge.json" alt="source-mysql"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Plaid</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-plaid"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-plaid%2Fbadge.json" alt="source-plaid"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Postgres</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-postgres"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-postgres%2Fbadge.json" alt="source-postgres"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Recurly</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-recurly"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-recurly%2Fbadge.json" alt="source-recurly"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Redshift</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-redshift"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-redshift%2Fbadge.json" alt="source-redshift"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Salesforce</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-salesforce-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-salesforce-singer%2Fbadge.json" alt="source-salesforce-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Sendgrid</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-sendgrid"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-sendgrid%2Fbadge.json" alt="source-sendgrid"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Shopify</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-shopify-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-shopify-singer%2Fbadge.json" alt="source-shopify-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Slack</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-slack-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-slack-singer%2Fbadge.json" alt="source-slack-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Stripe</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-stripe-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-stripe-singer%2Fbadge.json" alt="source-stripe-singer"/></a>
      </td>
      <td style="text-align:center">&#x2705;</td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Twilio</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-twilio-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-twilio-singer%2Fbadge.json" alt="source-twilio-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Zendesk Support</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-zendesk-support-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-zendesk-support-singer%2Fbadge.json" alt="source-zendesk-support-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
    <tr>
      <td style="text-align:left">Zoom</td>
      <td style="text-align:left"><a href="https://status-api.airbyte.io/tests/summary/source-zoom-singer"><img src="https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fsource-zoom-singer%2Fbadge.json" alt="source-zoom-singer"/></a>
      </td>
      <td style="text-align:center"></td>
      <td style="text-align:left"></td>
    </tr>
  </tbody>
</table>

## Destinations

| Destination | Status | Airbyte Certified |
| :--- | :--- | :---: |
| BigQuery | [![destination-bigquery](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-bigquery%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-bigquery) |  |
| Local CSV | [![destination-csv](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-csv%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-csv) |  |
| Local JSON | [![destination-local-json](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-local-json%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-local-json) |  |
| Postgres | [![destination-postgres](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-postgres%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-postgres) |  |
| Redshift | [![destination-redshift](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-redshift%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-redshift) |  |
| Snowflake | [![destination-snowflake](https://img.shields.io/endpoint?url=https%3A%2F%2Fstatus-api.airbyte.io%2Ftests%2Fsummary%2Fdestination-snowflake%2Fbadge.json)](https://status-api.airbyte.io/tests/summary/destination-snowflake) |  |

