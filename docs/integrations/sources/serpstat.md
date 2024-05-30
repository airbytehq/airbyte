# Serpstat

This page contains the setup guide and reference information for the Serpstat source connector.

## Setup guide

### Step 1: Get Serpstat API key

#### For new Serpstat users

1. Create a new [Serpstat account](https://serpstat.com/signup/?utm_source=).
2. Go to [My account](https://serpstat.com/users/profile/) page and click **Get API key**.
3. Follow the instructions to get the API key.
4. Click **Copy** to copy the API key.

#### For existing Serpstat users

Go to [My account](https://serpstat.com/users/profile/) page and click **Copy** to copy the API key.

### Step 2: Set up the Serpstat connector in Airbyte

1. [Log into your Airbyte Cloud](https://cloud.airbyte.io/workspaces) or Airbyte Open Source account.
2. Click **Sources** and then click **+ New source**.
3. On the **Set up the source** page, select **Serpstat** from the **Source type** dropdown.
4. Enter a name for your connector.
5. Enter the API key.
6. Expand **Optional fields** and fill them in. Each API response consumes API credits available to your Serpstat subscription plan. To limit the number of consumed API rows, decrease **Page size** and **Pages to fetch** options.
7. Click **Set up source**.

## Supported sync modes

The Serpstat source connector supports the following [sync modes](https://docs.airbyte.com/cloud/core-concepts#connection-sync-modes):

- Full refresh

## Supported Streams

- [Domains summary](https://serpstat.com/api/412-summarnij-otchet-po-domenu-v4-serpstatdomainproceduregetdomainsinfo/)
- [Domain history](https://serpstat.com/api/420-istoriya-po-domenu-v4-serpstatdomainproceduregetdomainshistory/)
- [Domain keywords](https://serpstat.com/api/584-top-search-engine-keywords-by-v4-domain-serpstatdomainproceduregetdomainkeywords/)
- [Domain keywords by region](https://serpstat.com/api/sorting-the-domain-by-keywords/)
- [Domain competitors](https://serpstat.com/api/590-domain-competitors-in-v4-search-result-serpstatdomainproceduregetcompetitors/)
- [Domain top pages](https://serpstat.com/api/588-domain-top-urls-v4-serpstatdomainproceduregettopurls/)

## Performance considerations

The maximum sync speed is limited by the number of requests per second per API key. See this limit in your [Serpstat account](https://serpstat.com/users/profile/).

## Changelog

| Version | Date       | Pull Request                                             | Subject                    |
| :------ | :--------- | :------------------------------------------------------- | :------------------------- |
| 0.1.0   | 2023-08-21 | [28147](https://github.com/airbytehq/airbyte/pull/28147) | Release Serpstat Connector |
