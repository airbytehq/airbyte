## Prerequisite

* A verified property in Google Search Console
* Credentials to a Google Service Account (or Google Service Account with delegated Domain Wide Authority) or Google User Account
* Enable  Google Search Console API
​
## Setup guide
1. Enter the site URL.
2. Enter a **Start Date** in the format YYYY-MM-DD. Data after this date will be replicated.
2. Click **Authenticate your account** by selecting Oauth (recommended).
   * If you prefer Service Account Key Authentication, follow the instructions in our [full documentation](https://docs.airbyte.com/integrations/sources/google-search-console/).
3. (Optional) Set an **End Date** if you do not want data after a specific date.
4. (Optional) Airbyte generates default reports. To add more reports, you need to add **Custom Reports** as a JSON array describing the custom reports you want to sync from Google Search Console. 

Custom Reports can be added in the format: `{"name": "<report-name>", "dimensions": ["<dimension-name>", ...]}`

For detailed information on supported sync modes, supported streams, performance considerations, refer to the full documentation for [Google Search Console](https://docs.airbyte.com/integrations/sources/google-search-console/).